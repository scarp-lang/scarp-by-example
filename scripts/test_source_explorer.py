"""Regression tests for authored links, byte locations and compiler contract."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from source_explorer import (
    INDEX, PROJECT, ROOT, byte_span, load_reference_map,
    render_reference_explorer, verify_reference_map,
)


class ReferenceExplorerTests(unittest.TestCase):
    def test_every_link_is_source_backed(self):
        mapping = load_reference_map()
        self.assertEqual(len(mapping["files"]), 2)
        self.assertEqual(len(mapping["symbols"]), 11)
        self.assertEqual(sum(len(s["references"]) for s in mapping["symbols"]), 20)
        self.assertEqual({s["id"] for s in mapping["symbols"] if s["name"] == "base"},
                         {"base-outer", "base-inner"})

    def test_utf8_byte_span_is_not_character_offset(self):
        source = "é x\n".encode("utf-8")
        self.assertEqual(byte_span(source, 1, 3, "x"), (3, 4))
        with self.assertRaisesRegex(ValueError, "does not contain"):
            byte_span(source, 1, 2, "x")
        with self.assertRaisesRegex(ValueError, "positive"):
            byte_span(source, 1, True, "x")
        with self.assertRaisesRegex(ValueError, "outside"):
            byte_span(source, 2, 1, "x")

    def test_render_links_to_source_and_fallback_descriptions(self):
        html = render_reference_explorer()
        self.assertEqual(html.count('class="ref-token"'), 31)
        self.assertEqual(html.count('class="ref-card"'), 11)
        self.assertIn('href="#ref-card-base-outer"', html)
        self.assertIn('href="#ref-card-base-inner"', html)
        self.assertIn('data-ref-kind="argument_label"', html)
        self.assertIn('src/main.srp', html)
        self.assertIn('src/lib/navigation_values.srp', html)
        self.assertIn('lang="en"', html)
        self.assertIn('lang="hi"', html)
        self.assertNotIn('onclick=', html)
        self.assertNotIn('fetch(', html)

    def test_map_rejects_stale_pin_and_wrong_token(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / PROJECT, root / PROJECT)
            (root / "docs").mkdir()
            shutil.copyfile(ROOT / "docs/compiler-target.json",
                            root / "docs/compiler-target.json")
            path = root / INDEX
            data = json.loads(path.read_text(encoding="utf-8"))
            data["compiler_commit"] = "wrong pin"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "compiler pin"):
                load_reference_map(root)

            data["compiler_commit"] = load_reference_map()["compiler_commit"]
            data["symbols"][0]["definition"][1] += 1
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not contain"):
                load_reference_map(root)

    def test_exact_compiler_reference_targets_are_required(self):
        """Construct a minimal synthetic inventory; CI tests the real compiler."""
        mapping = load_reference_map()
        ids = {name: i for i, name in enumerate(mapping["files"])}
        sources = {f: (ROOT / PROJECT / f).read_bytes() for f in ids}
        symbols = []
        references = []
        for symbol_id, authored in enumerate(mapping["symbols"]):
            file = authored["file"]
            symbols.append({
                "id": symbol_id,
                "name": authored["name"],
                "kind": authored["kind"],
                "public": authored["public"],
                "location": {
                    "source": ids[file],
                    "span": list(byte_span(sources[file], *authored["definition"], authored["name"])),
                },
            })
            for file, line, col, kind in authored["references"]:
                references.append({
                    "target": symbol_id,
                    "kind": kind,
                    "location": {
                        "source": ids[file],
                        "span": list(byte_span(sources[file], line, col, authored["name"])),
                    },
                })
        inventory = {
            "kind": "scarp.references",
            "files": [{"id": id_, "path": name} for name, id_ in ids.items()],
            "symbols": symbols,
            "references": references,
        }
        verify_reference_map(inventory)
        references[0]["target"] = len(symbols) + 1
        with self.assertRaisesRegex(ValueError, "compiler reference missing"):
            verify_reference_map(inventory)
        references[0]["target"] = 0
        symbols[0]["location"]["span"][0] += 1
        with self.assertRaisesRegex(ValueError, "compiler declaration missing"):
            verify_reference_map(inventory)


if __name__ == "__main__":
    unittest.main()
