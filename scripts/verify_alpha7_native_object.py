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
        require(key in report and report[key] == expected, f"{name}: invalid {key}")
    require(isinstance(report.get("mode"), str) and bool(report["mode"]),
            "missing mode")
    for field in ("callee_frame_bytes", "callee_stack_bytes", "stack_argument_bytes"):
        require(type(report.get(field)) is int and report[field] >= 0,
                f"{name}: invalid {field}")
    require(report["callee_stack_bytes"] == report["callee_frame_bytes"] + 8,
            "callee stack does not include return address")
    require(report["stack_argument_bytes"] == 0, "unexpected external stack arguments")
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
            if label == "divide":
                start, end = reports[case]["failure_spans"][int(span)]
                source = (WORKSHOP / "entry.srp").read_bytes()
                require(b"/" in source[start:end], "division failure lost its callee span")
        else:
            require(int(span) == 0, f"{label}: success span is not zero")
        seen.add(label)
    require(seen == set(expected), "missing native host rows")


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
            objects.append(str(obj))
        absent = folder / "rejected.o"
        rejected(run(binary, "native-object", "unknown-target", "checked",
                     str(WORKSHOP / "checked.srp"), "-o", str(absent)), 2, "target")
        require(not absent.exists(), "invalid target wrote a file")
        rejected(run(binary, "native-object", "--json", "x86_64-none", "bounded-entry",
                     "compute", "1000", "1", str(WORKSHOP / "entry.srp"), "-o",
                     str(absent)), 1, "stack budget")
        require(not absent.exists(), "insufficient stack wrote a file")
        if link_host:
            host = folder / "host"
            success(run("cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        str(WORKSHOP / "host.c"), *objects, "-o", str(host)), "host link")
            check_host(success(run(str(host)), "native host"), reports)
    print("PASS: three native object modes, metadata, determinism and rejection cases"
          + (", plus nine linked native results." if link_host else "."))


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
