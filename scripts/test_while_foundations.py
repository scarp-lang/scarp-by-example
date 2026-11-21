"""Regress the beginner while lessons and exact predicted output fixtures.

The examples workflow also verifies and executes every .srp against the real,
release-pinned Scarp compiler on Linux, macOS and Windows.
"""

from __future__ import annotations

import unittest

from verify_examples import EXAMPLES, discover_examples, read_expected_stdout


class WhileFoundationsTests(unittest.TestCase):
    def check_lesson(self, filename: str, snippets: tuple[str, ...], output: bytes) -> None:
        source = EXAMPLES / "02-control-flow" / filename
        fixture = source.with_suffix(".stdout")
        text = source.read_text(encoding="utf-8")
        for snippet in snippets:
            with self.subTest(lesson=filename, snippet=snippet):
                self.assertIn(snippet, text)
        self.assertEqual(read_expected_stdout(fixture), output)
        self.assertIn((source, fixture), discover_examples(EXAMPLES))

    def test_inclusive_sum_and_final_counter(self):
        self.check_lesson(
            "05-while-sum.srp",
            ("var i = 1;", "var total = 0;", "while i <= 10 {",
             "total += i;", "i += 1;", "print(total);", "print(i);"),
            (str(sum(range(1, 11))) + "\n11\n").encode("utf-8"),
        )

    def test_countdown_uses_greater_equal_and_decrement(self):
        self.check_lesson(
            "06-while-countdown.srp",
            ("var remaining = 5;", "while remaining >= 1 {",
             "print(remaining);", "remaining -= 1;"),
            ("".join(f"{number}\n" for number in range(5, -1, -1))).encode("utf-8"),
        )

    def test_product_initializes_to_one_not_zero(self):
        result = 1
        for factor in range(1, 6):
            result *= factor
        self.check_lesson(
            "07-while-product.srp",
            ("var factor = 1;", "var product = 1;", "while factor <= 5 {",
             "product *= factor;", "factor += 1;"),
            (f"{result}\n6\n").encode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
