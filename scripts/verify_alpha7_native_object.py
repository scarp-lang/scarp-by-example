#!/usr/bin/env python3
"""Verify the independently pinned alpha.2 native object workshop."""

from __future__ import annotations

import argparse
import json
import platform
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / "tutorials" / "alpha7-native-object"
PIN = "638dc4c227f34f1c660be66834bcc0cbdb22dec8"
VERSION = "0.0.7-alpha.2"
CASES = {
    "checked": (["checked"], "scarp_checked_integer_function", 2, None),
    "wide": (["checked"], "scarp_checked_integer_function", 8, None),
    "bounded": (["bounded", "1000"], "scarp_bounded_integer_function", 1, 1000),
    "entry": (["bounded-entry", "compute", "1000", "4096"],
              "scarp_bounded_integer_entry", 2, 1000),
}


def require(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError(label)


def run(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, cwd=ROOT, input=b"", capture_output=True,
                          timeout=30, check=False)


def success(result: subprocess.CompletedProcess[bytes], label: str) -> bytes:
    require(result.returncode == 0 and not result.stderr,
            f"{label}: {result.returncode}, {result.stderr!r}")
    return result.stdout


def rejected(result: subprocess.CompletedProcess[bytes], status: int, label: str) -> None:
    require(result.returncode == status and not result.stdout and bool(result.stderr),
            f"{label}: expected error {status}, got {result!r}")


def check_elf(data: bytes) -> None:
    require(len(data) >= 64, "truncated ELF header")
    require(data[:7] == b"\x7fELF\x02\x01\x01", "not little-endian ELF64 v1")
    kind, machine, version = struct.unpack_from("<HHI", data, 16)
    require((kind, machine, version) == (1, 62, 1), "not x86-64 relocatable ELF")
    section_offset = struct.unpack_from("<Q", data, 40)[0]
    header_size, _, _, section_size, sections, names = struct.unpack_from("<6H", data, 52)
    require(header_size == 64 and section_size == 64 and sections > 0,
            "invalid ELF header/section sizes")
    require(section_offset >= 64 and section_offset + sections * section_size <= len(data)
            and 0 < names < sections, "section table outside object")


def check_metadata(raw: bytes, name: str, source: bytes) -> dict:
    report = json.loads(raw.decode("utf-8"))
    require(isinstance(report, dict), "metadata is not a JSON object")
    args, symbol, arity, work = CASES[name]
    for key, expected in {
        "schema_version": 1, "target": "x86_64-none",
        "symbol": symbol, "integer_arguments": arity,
        "max_work": work, "call_stack_alignment": 16,
        "span_encoding": "utf-8-bytes",
    }.items():
        require(key in report and type(report[key]) is type(expected)
                and report[key] == expected, f"{name}: invalid {key}")
    require(report.get("mode") == args[0], "incorrect native mode")
    for field in ("callee_frame_bytes", "callee_stack_bytes", "stack_argument_bytes"):
        require(type(report.get(field)) is int and report[field] >= 0,
                f"{name}: invalid {field}")
    require(report["callee_stack_bytes"] == report["callee_frame_bytes"] + 8,
            "callee stack does not include return address")
    require(report["stack_argument_bytes"] == max(0, arity - 6) * 8,
            "incorrect external stack argument bytes")
    spans = report.get("failure_spans")
    require(isinstance(spans, list) and bool(spans), "missing failure spans")
    for span in spans:
        require(isinstance(span, list) and len(span) == 2
                and all(type(v) is int for v in span)
                and 0 <= span[0] < span[1] <= len(source), "invalid failure span")
        source[:span[0]].decode("utf-8")
        source[:span[1]].decode("utf-8")
    if name == "entry":
        require(report.get("max_stack_bytes") == int(args[-1]), "incorrect stack budget")
        peak = report.get("peak_stack_bytes")
        require(type(peak) is int and 0 < peak <= 4096, "invalid peak stack")
        require(report.get("max_active_frames") == 3, "expected three active frames")
    return report


def check_host(output: bytes, reports: dict) -> None:
    expected = {
        "checked": (7, 0, "checked"), "overflow": (0, 1, "checked"),
        "empty": (0, 0, "bounded"), "triangle": (15, 0, "bounded"),
        "negative": (0, 5, "bounded"), "exhausted": (0, 4, "bounded"),
        "entry": (22, 0, "entry"), "divide": (0, 2, "entry"),
        "again": (22, 0, "entry"),
    }
    expected.update({
        "wide-forward": (204, 0, "wide"), "wide-reverse": (120, 0, "wide"),
        "wide-overflow": (0, 1, "wide"),
    })
    seen = set()
    for line in output.decode("ascii").splitlines():
        label, value, status, span = line.split()
        require(label in expected and label not in seen, f"unexpected row: {label}")
        wanted_value, wanted_status, case = expected[label]
        require((int(value), int(status)) == (wanted_value, wanted_status),
                f"{label}: incorrect value/status")
        if wanted_status:
            require(0 <= int(span) < len(reports[case]["failure_spans"]),
                    f"{label}: span index outside metadata")
            if label in ("divide", "overflow", "wide-overflow"):
                start, end = reports[case]["failure_spans"][int(span)]
                source = (WORKSHOP / (case + ".srp")).read_bytes()
                operator = {"divide": b"/", "overflow": b"+", "wide-overflow": b"*"}[label]
                # A slash in a leading comment is not the division expression.
                # All three fixtures put the failing operator in a return body;
                # select the final occurrence for wide's eighth-argument multiply.
                body = source.index(b"return ")
                expected_start = (source.rindex(operator, body) if label == "wide-overflow"
                                  else source.index(operator, body))
                require((start, end) == (expected_start, expected_start + len(operator)),
                        f"{label}: incorrect operator byte span")
        else:
            require(int(span) == 0, f"{label}: success span is not zero")
        seen.add(label)
    require(seen == set(expected), "missing native host rows")


def check_interpreter(binary: str, folder: Path) -> None:
    """Run independent interpreter calls using the identical function declarations."""
    cases = {
        "checked": ("print(offset(12, -5));", b"7\n"),
        "bounded": ("print(triangular(0));\nprint(triangular(5));", b"0\n15\n"),
        "entry": ("print(compute(21, 2));", b"22\n"),
        "wide": ("print(weighted(1, 2, 3, 4, 5, 6, 7, 8));\n"
                 "print(weighted(8, 7, 6, 5, 4, 3, 2, 1));", b"204\n120\n"),
    }
    for name, (calls, output) in cases.items():
        program = folder / (name + "-interpreted.srp")
        program.write_bytes((WORKSHOP / (name + ".srp")).read_bytes()
                            + b"\n" + calls.encode("utf-8") + b"\n")
        require(success(run(binary, "exec", str(program)), name + " interpreter") == output,
                f"{name}: interpreter result differs from expected native value")


def check_boundaries(binary: str, folder: Path, reports: dict) -> None:
    """The measured static stack bound is both sufficient and necessary."""
    peak = reports["entry"]["peak_stack_bytes"]
    program = str(WORKSHOP / "entry.srp")
    exact = folder / "exact-stack.o"
    args = (binary, "native-object", "--json", "x86_64-none",
            "bounded-entry", "compute", "1000")
    raw = success(run(*args, str(peak), program, "-o", str(exact)), "exact stack")
    metadata = json.loads(raw)
    expected = dict(reports["entry"], max_stack_bytes=peak)
    require(metadata == expected, "exact stack metadata differs")
    require(exact.read_bytes() == (folder / "entry.o").read_bytes(),
            "exact stack budget changed object bytes")
    too_small = folder / "one-byte-short.o"
    rejected(run(*args, str(peak - 1), program, "-o", str(too_small)),
             1, "one byte below required stack")
    require(not too_small.exists(), "one-byte-short budget published an object")

    zero = folder / "zero-work.o"
    raw = success(run(binary, "native-object", "--json", "x86_64-none",
                      "bounded", "0", str(WORKSHOP / "bounded.srp"), "-o", str(zero)),
                  "zero work emission")
    require(json.loads(raw).get("max_work") == 0, "zero work budget lost")
    check_elf(zero.read_bytes())

    # Compilation must not run top-level effects, and unsupported recursion
    # and invalid UTF-8 must never leave a partial output.
    for name, source, mode in (
        ("effect", b"print(42);", ("checked",)),
        ("recursive", b"pure funcra loop(n: integer) -> integer { return loop(n); }",
         ("bounded-entry", "loop", "1000", "4096")),
        ("invalid-utf8", b"\xff", ("checked",)),
    ):
        src = folder / (name + ".srp")
        src.write_bytes(source)
        obj = folder / (name + ".o")
        rejected(run(binary, "native-object", "--json", "x86_64-none",
                     *mode, str(src), "-o", str(obj)), 1, name)
        require(not obj.exists(), f"{name}: rejected source produced an object")


def verify(compiler: Path, source: Path, link_host: bool) -> None:
    manifest = json.loads((WORKSHOP / "compiler-target.json").read_text(encoding="utf-8"))
    require(manifest == {
        "version": VERSION, "release_tag": "v" + VERSION,
        "source_commit": PIN, "status": "prerelease",
        "release_url": "https://github.com/scarp-lang/scarp/releases/tag/v" + VERSION,
    }, "workshop pin mismatch")
    head = success(run("git", "-C", str(source), "rev-parse", "HEAD"), "source revision")
    require(head.decode("ascii").strip() == PIN, "compiler source mismatch")
    binary = str(compiler)
    require(success(run(binary, "version"), "compiler version").decode().strip()
            == "scarp " + VERSION, "compiler version mismatch")
    if link_host:
        require(platform.system() == "Linux" and platform.machine().lower() in ("x86_64", "amd64"),
                "--link-host requires Linux x86-64")
    reports = {}
    with tempfile.TemporaryDirectory(prefix="scarp-native-workshop-") as tmp:
        folder = Path(tmp)
        objects = []
        for name, (args, _, _, _) in CASES.items():
            program = WORKSHOP / (name + ".srp")
            raw_source = program.read_bytes()
            raw_source.decode("utf-8")
            obj = folder / (name + ".o")
            copy = folder / (name + "-repeat.o")
            base = (binary, "native-object", "x86_64-none", *args, str(program), "-o")
            raw = success(run(binary, "native-object", "--json", "x86_64-none",
                              *args, str(program), "-o", str(obj)), name)
            reports[name] = check_metadata(raw, name, raw_source)
            data = obj.read_bytes()
            check_elf(data)
            require(success(run(*base, str(copy)), name + " repeat") == b"",
                    "non-JSON emission produced stdout")
            require(copy.read_bytes() == data, "nondeterministic object bytes")
            rejected(run(*base, str(obj)), 1, name + " overwrite")
            require(obj.read_bytes() == data, "existing object changed")
            if name != "wide":
                objects.append(str(obj))
        absent = folder / "rejected.o"
        rejected(run(binary, "native-object", "unknown-target", "checked",
                     str(WORKSHOP / "checked.srp"), "-o", str(absent)), 2, "target")
        require(not absent.exists(), "invalid target wrote a file")
        rejected(run(binary, "native-object", "--json", "x86_64-none", "bounded-entry",
                     "compute", "1000", "1", str(WORKSHOP / "entry.srp"), "-o",
                     str(absent)), 1, "stack budget")
        require(not absent.exists(), "insufficient stack wrote a file")
        check_boundaries(binary, folder, reports)
        check_interpreter(binary, folder)
        if link_host:
            host = folder / "host"
            success(run("cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        str(WORKSHOP / "host.c"), *objects, "-o", str(host)), "host link")
            wide_host = folder / "wide-host"
            success(run("cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        str(WORKSHOP / "wide_host.c"), str(folder / "wide.o"),
                        "-o", str(wide_host)), "wide host link")
            output = success(run(str(host)), "native host")
            output += success(run(str(wide_host)), "wide native host")
            check_host(output, reports)
    print("PASS: four native objects, exact stack boundary, metadata, determinism,"
          " rejection cases and six interpreter results"
          + (", plus twelve linked native results." if link_host else "."))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--compiler-source", required=True, type=Path)
    parser.add_argument("--link-host", action="store_true")
    args = parser.parse_args()
    try:
        verify(args.compiler.resolve(), args.compiler_source.resolve(), args.link_host)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
