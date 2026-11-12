"""Mobile navigation HTML is keyboard-friendly and consistent on nested routes."""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import PurePosixPath

from build_site import page_shell


class NavigationReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active: str | None = None
        self.links: dict[str, list[tuple[str, str]]] = {"top-nav": [], "mobile-menu-links": []}
        self.details = 0
        self.summaries = 0
        self.current_href: str | None = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "details" and attributes.get("class") == "mobile-nav":
            self.details += 1
            if "data-mobile-nav" not in attributes:
                raise AssertionError("mobile navigation missing interaction marker")
        if tag == "summary":
            self.summaries += 1
        if tag == "nav" and attributes.get("class") in self.links:
            self.active = attributes["class"]
        if tag == "a" and self.active:
            self.current_href = attributes.get("href")

    def handle_data(self, data):
        if self.active and self.current_href and data.strip():
            self.links[self.active].append((self.current_href, data.strip()))
            self.current_href = None

    def handle_endtag(self, tag):
        if tag == "nav":
            self.active = None
        if tag == "a":
            self.current_href = None


class MobileNavigationTests(unittest.TestCase):
    def test_native_mobile_menu_duplicates_primary_destinations_on_every_level(self):
        routes = (
            "index.html",
            "chapters/01-basics/index.html",
            "lessons/01-basics/01-hello/index.html",
            "labs/01-basics/index.html",
            "projects/index.html",
            "projects/source-navigation/index.html",
            "projects/project-testing/index.html",
            "workshops/conditionals-and-unicode/01-grading/index.html",
            "workshops/input-and-tuples/index.html",
        )
        for route in routes:
            with self.subTest(route=route):
                markup = page_shell(route, "A title", "Description", '<main id="main-content"></main>')
                parser = NavigationReader()
                parser.feed(markup)
                self.assertEqual(parser.details, 1)
                self.assertEqual(parser.summaries, 1)
                desktop = parser.links["top-nav"]
                mobile = parser.links["mobile-menu-links"]
                self.assertEqual(len(desktop), 7)
                self.assertEqual(desktop, mobile)
                labels = [label for _, label in mobile]
                self.assertEqual(
                    labels, ["Chapters", "Search", "Projects", "Workshops", "Coding labs", "Compiler", "GitHub"]
                )
                if route.startswith("lessons/"):
                    self.assertIn(("../../../index.html#chapters", "Chapters"), mobile)
                    self.assertIn(("../../../labs/index.html", "Coding labs"), mobile)
                self.assertIn('<summary>Menu</summary>', markup)
                self.assertIn('aria-label="Mobile navigation"', markup)
                self.assertIn('href="#main-content">Skip to content', markup)

    def test_disclosure_is_in_static_markup_without_javascript(self):
        html = page_shell("index.html", "Home", "Static", '<main id="main-content"></main>')
        self.assertLess(html.index('<summary>Menu</summary>'), html.index('class="mobile-menu-links"'))
        self.assertNotIn('aria-hidden="true" class="mobile-nav"', html)


if __name__ == "__main__":
    unittest.main()
