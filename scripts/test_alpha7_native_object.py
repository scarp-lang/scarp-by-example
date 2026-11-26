"""Offline regression tests for the native workshop verifier."""
import copy
import json
import struct
import unittest

from verify_alpha7_native_object import check_elf, check_metadata, check_host, WORKSHOP


def elf():
    data = bytearray(64 + 2 * 64)
    data[:7] = b"\x7fELF\x02\x01\x01"
    struct.pack_into("<HHI", data, 16, 1, 62, 1)
    struct.pack_into("<Q", data, 40, 64)
    struct.pack_into("<6H", data, 52, 64, 0, 0, 64, 2, 1)
    return bytes(data)


def report(mode="checked", arity=2, work=None):
    return {
        "schema_version": 1, "target": "x86_64-none",
        "mode": mode, "symbol": "scarp_checked_integer_function",
        "integer_arguments": arity, "max_work": work, "call_stack_alignment": 16,
        "span_encoding": "utf-8-bytes", "callee_frame_bytes": 8,
        "callee_stack_bytes": 16, "stack_argument_bytes": max(0, arity - 6) * 8,
        "failure_spans": [[2, 3]],
    }


def encode(value):
    return json.dumps(value).encode("utf-8")


class ElfTests(unittest.TestCase):
    def test_valid_header(self):
        check_elf(elf())

    def test_truncated(self):
        with self.assertRaises(ValueError):
            check_elf(elf()[:63])

    def test_wrong_architecture(self):
        data = bytearray(elf())
        struct.pack_into("<H", data, 18, 183)
        with self.assertRaises(ValueError):
            check_elf(data)

    def test_wrong_object_kind(self):
        data = bytearray(elf())
        struct.pack_into("<H", data, 16, 2)
        with self.assertRaises(ValueError):
            check_elf(data)

    def test_section_overrun(self):
        data = bytearray(elf())
        struct.pack_into("<Q", data, 40, 128)
        with self.assertRaises(ValueError):
            check_elf(data)

    def test_invalid_names_index(self):
        data = bytearray(elf())
        struct.pack_into("<H", data, 62, 2)
        with self.assertRaises(ValueError):
            check_elf(data)


class MetadataTests(unittest.TestCase):
    source = "é+".encode()

    def test_correct_utf8_span(self):
        check_metadata(encode(report()), "checked", self.source)

    def test_eight_arguments(self):
        check_metadata(encode(report(arity=8)), "wide", self.source)

    def test_schema_bool_is_not_integer(self):
        bad = report()
        bad["schema_version"] = True
        with self.assertRaises(ValueError):
            check_metadata(encode(bad), "checked", self.source)

    def test_wrong_mode(self):
        bad = report("bounded")
        with self.assertRaises(ValueError):
            check_metadata(encode(bad), "checked", self.source)

    def test_wrong_stack_slots(self):
        bad = report(arity=8)
        bad["stack_argument_bytes"] = 0
        with self.assertRaises(ValueError):
            check_metadata(encode(bad), "wide", self.source)

    def test_wrong_return_address(self):
        bad = report()
        bad["callee_stack_bytes"] = 8
        with self.assertRaises(ValueError):
            check_metadata(encode(bad), "checked", self.source)

    def test_span_splits_unicode_scalar(self):
        bad = report()
        bad["failure_spans"] = [[1, 3]]
        with self.assertRaises(ValueError):
            check_metadata(encode(bad), "checked", self.source)

    def test_span_out_of_bounds(self):
        bad = report()
        bad["failure_spans"] = [[2, 4]]
        with self.assertRaises(ValueError):
            check_metadata(encode(bad), "checked", self.source)

    def test_entry_stack_depth_and_limit(self):
        good = report("bounded-entry", work=1000)
        good.update(symbol="scarp_bounded_integer_entry", max_stack_bytes=4096,
                    peak_stack_bytes=128, max_active_frames=3)
        check_metadata(encode(good), "entry", self.source)
        for field, value in (("peak_stack_bytes", 4097), ("max_active_frames", 2)):
            with self.subTest(field=field):
                bad = dict(good, **{field: value})
                with self.assertRaises(ValueError):
                    check_metadata(encode(bad), "entry", self.source)


class HostTests(unittest.TestCase):
    def setUp(self):
        self.reports = {}
        for name, op in (("checked", b"+"), ("wide", b"*"), ("entry", b"/"),
                         ("bounded", b"+")):
            source = (WORKSHOP / (name + ".srp")).read_bytes()
            # Find the operator in the function rather than in a comment.
            start = (source.rindex(op) if name == "wide"
                     else source.index(op, source.index(b"pure funcra")))
            self.reports[name] = {"failure_spans": [[start, start + 1]]}
        self.output = (
            b"checked 7 0 0\noverflow 0 1 0\nempty 0 0 0\n"
            b"triangle 15 0 0\nnegative 0 5 0\nexhausted 0 4 0\n"
            b"entry 22 0 0\ndivide 0 2 0\nagain 22 0 0\n"
            b"wide-forward 204 0 0\nwide-reverse 120 0 0\nwide-overflow 0 1 0\n"
        )

    def test_all_rows(self):
        check_host(self.output, self.reports)

    def test_wrong_result(self):
        with self.assertRaises(ValueError):
            check_host(self.output.replace(b"204", b"205"), self.reports)

    def test_duplicate_row(self):
        with self.assertRaises(ValueError):
            check_host(self.output + b"checked 7 0 0\n", self.reports)

    def test_missing_row(self):
        with self.assertRaises(ValueError):
            check_host(self.output.replace(b"again 22 0 0\n", b""), self.reports)

    def test_wrong_failure_span(self):
        bad = copy.deepcopy(self.reports)
        bad["entry"]["failure_spans"] = [[0, 1]]
        with self.assertRaises(ValueError):
            check_host(self.output, bad)

    def test_wrong_multiply_in_same_function(self):
        bad = copy.deepcopy(self.reports)
        source = (WORKSHOP / "wide.srp").read_bytes()
        start = source.index(b"*")
        bad["wide"]["failure_spans"] = [[start, start + 1]]
        with self.assertRaises(ValueError):
            check_host(self.output, bad)

    def test_out_of_range_failure_id(self):
        with self.assertRaises(ValueError):
            check_host(self.output.replace(b"divide 0 2 0", b"divide 0 2 1"), self.reports)
