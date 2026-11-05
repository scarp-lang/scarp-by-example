"""Pure schema checks for the published static source-navigation inventory."""

import json
import unittest

from verify_cli import CliSmokeError, validate_navigation_inventory


def fixture(kind="symbols"):
    data = {
        "schema_version": 1, "kind": "scarp." + kind,
        "span_encoding": "utf-8-bytes", "column_encoding": "unicode-scalar",
        "position_base": 1, "files": [{"id": 0, "path": "main.srp"}],
        "symbols": [{"id": 0, "name": "value", "kind": "binding"}],
    }
    if kind == "references":
        data["references"] = [{
            "target": 0, "kind": "read", "location": {
                "source": 0, "span": [0, 5],
                "start": {"line": 1, "column": 1},
                "end": {"line": 1, "column": 6},
            }
        }]
    return data


class NavigationSchemaTests(unittest.TestCase):
    def test_valid_symbol_and_reference_inventories(self):
        for kind in ("symbols", "references"):
            with self.subTest(kind=kind):
                data = fixture(kind)
                self.assertEqual(validate_navigation_inventory(json.dumps(data).encode(), kind), data)

    def test_rejects_wrong_kind_version_or_encoding(self):
        for field, value in (("kind", "scarp.modules"), ("schema_version", 2),
                             ("span_encoding", "utf-16"), ("column_encoding", "bytes"),
                             ("position_base", 0)):
            with self.subTest(field=field):
                data = fixture()
                data[field] = value
                with self.assertRaises(CliSmokeError):
                    validate_navigation_inventory(json.dumps(data).encode(), "symbols")

    def test_rejects_dangling_reference_and_duplicate_ids(self):
        data = fixture("references")
        data["references"][0]["target"] = 42
        with self.assertRaisesRegex(CliSmokeError, "dangling"):
            validate_navigation_inventory(json.dumps(data).encode(), "references")
        data = fixture()
        data["symbols"].append(data["symbols"][0].copy())
        with self.assertRaisesRegex(CliSmokeError, "duplicate"):
            validate_navigation_inventory(json.dumps(data).encode(), "symbols")

    def test_rejects_invalid_json_and_malformed_files(self):
        with self.assertRaises(CliSmokeError):
            validate_navigation_inventory(b"{", "symbols")
        data = fixture()
        data["files"] = [{"id": True, "path": "main.srp"}]
        with self.assertRaises(CliSmokeError):
            validate_navigation_inventory(json.dumps(data).encode(), "symbols")


if __name__ == "__main__":
    unittest.main()
