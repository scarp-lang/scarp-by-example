#!/usr/bin/env python3
"""Audit a generated GitHub Pages site without using the network.

Verify local links/assets, URL fragments, unique element IDs, one correct
canonical URL per HTML page, and exact HTML-route sitemap coverage.
Requires only Python's standard library, not a browser or Scarp compiler.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

PUBLIC_SITE = "https://scarp-lang.github.io/scarp-by-example/"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
ALLOWED_EXTERNAL_SCHEMES = frozenset({"http", "https", "mailto", "tel"})


@dataclass
class SiteAudit:
    pages: int = 0
    links: int = 0
    fragments: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


class ParsedPage(HTMLParser):
    """Track navigational references and anchor IDs without regex on HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicates: list[str] = []
        self.refs: list[tuple[str, str]] = []
        self.canonicals: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        id_value = attributes.get("id")
        if id_value is not None:
            if not id_value or id_value in self.ids:
                self.duplicates.append(id_value)
            self.ids.add(id_value)

        href = attributes.get("href")
        if tag == "link" and "canonical" in (attributes.get("rel") or "").split():
            self.canonicals.append(href or "")
        elif tag in ("a", "link") and href is not None:
            self.refs.append((f"{tag}[href]", href))

        if tag in ("script", "img", "source") and attributes.get("src") is not None:
            self.refs.append((f"{tag}[src]", attributes["src"] or ""))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def expected_canonical(root: Path, page: Path, base_url: str) -> str:
    relative = page.relative_to(root).as_posix()
    return base_url + relative.removesuffix("index.html")


def _resolve_reference(
    root: Path, page: Path, value: str, base_url: str
) -> tuple[Path, str] | None:
    """Return (destination file, decoded fragment), or None for external URLs."""
    if not value.strip():
        raise ValueError("empty URL")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("URL contains control characters")
    if "\\" in value:
        raise ValueError("backslashes are not valid local URL separators")
    url = urlsplit(value)
    if url.scheme and url.scheme.lower() not in ALLOWED_EXTERNAL_SCHEMES:
        raise ValueError(f"unsafe/unsupported URL scheme: {url.scheme}")
    if url.scheme in ("mailto", "tel"):
        return None

    base = urlsplit(base_url)
    if url.netloc:
        if url.scheme not in ("http", "https"):
            raise ValueError("protocol-relative or malformed remote URL")
        if url.scheme != base.scheme or url.netloc != base.netloc:
            return None
        # An absolute same-origin URL is local only in this published site.
        prefix = base.path
        if not url.path.startswith(prefix):
            raise ValueError("same-origin URL escapes the course base path")
        raw_path = url.path[len(prefix):]
        destination = root / unquote(raw_path)
    elif value.startswith("/"):
        raise ValueError("root-absolute links must be scoped to the course URL")
    else:
        destination = page.parent / unquote(url.path)

    destination = destination.resolve()
    if not destination.is_relative_to(root):
        raise ValueError("link resolves outside the published site")
    if destination.is_dir():
        destination /= "index.html"
    return destination, unquote(url.fragment)


def audit_site(
    directory: Path, *, base_url: str = PUBLIC_SITE
) -> SiteAudit:
    """Check every generated HTML page and all its local URL references."""
    root = directory.resolve()
    if not base_url.endswith("/"):
        raise ValueError("public base URL must end with /")
    parts = urlsplit(base_url)
    if parts.scheme != "https" or not parts.netloc or parts.query or parts.fragment:
        raise ValueError("public base URL must be an HTTPS directory URL")

    report = SiteAudit()
    if not root.is_dir():
        report.errors.append(f"missing output directory: {root}")
        return report

    pages = sorted(root.rglob("*.html"))
    report.pages = len(pages)
    if not pages:
        report.errors.append("site contains no HTML pages")
        return report

    parsed: dict[Path, ParsedPage] = {}
    for page in pages:
        parser = ParsedPage()
        try:
            parser.feed(page.read_text(encoding="utf-8"))
            parser.close()
        except (OSError, UnicodeError, ValueError) as error:
            report.errors.append(f"{page.relative_to(root)}: unreadable HTML: {error}")
            continue
        parsed[page] = parser
        name = page.relative_to(root).as_posix()
        for duplicate in parser.duplicates:
            report.errors.append(f"{name}: repeated or empty id={duplicate!r}")
        expected = expected_canonical(root, page, base_url)
        if parser.canonicals != [expected]:
            report.errors.append(
                f"{name}: canonical URL must be {expected!r}, got {parser.canonicals!r}"
            )

    for page, source in parsed.items():
        source_name = page.relative_to(root).as_posix()
        for attribute, value in source.refs:
            report.links += 1
            try:
                result = _resolve_reference(root, page, value, base_url)
            except ValueError as error:
                report.errors.append(f"{source_name}: {attribute}={value!r}: {error}")
                continue
            if result is None:
                continue
            target, fragment = result
            if not target.is_file():
                report.errors.append(
                    f"{source_name}: {attribute}={value!r}: missing {target.relative_to(root)}"
                )
                continue
            if fragment:
                report.fragments += 1
                target_page = parsed.get(target)
                if target_page is None:
                    report.errors.append(
                        f"{source_name}: {attribute}={value!r}: fragment on a non-HTML target"
                    )
                elif fragment not in target_page.ids:
                    report.errors.append(
                        f"{source_name}: {attribute}={value!r}: "
                        f"missing id={fragment!r} in {target.relative_to(root)}"
                    )

    sitemap_path = root / "sitemap.xml"
    try:
        tree = ET.parse(sitemap_path)
        sitemap = tree.getroot()
        if sitemap.tag != SITEMAP_NS + "urlset":
            report.errors.append("sitemap.xml: expected standard sitemap urlset")
        seen_urls = [
            (item.text or "").strip()
            for item in sitemap.findall(f"{SITEMAP_NS}url/{SITEMAP_NS}loc")
        ]
        duplicates = sorted({url for url in seen_urls if seen_urls.count(url) > 1})
        if duplicates:
            report.errors.append(f"sitemap.xml: duplicate locations {duplicates!r}")
        expected_urls = {expected_canonical(root, p, base_url) for p in pages}
        missing = sorted(expected_urls - set(seen_urls))
        extra = sorted(set(seen_urls) - expected_urls)
        if missing:
            report.errors.append(f"sitemap.xml: missing HTML routes {missing!r}")
        if extra:
            report.errors.append(f"sitemap.xml: unexpected routes {extra!r}")
    except (OSError, ET.ParseError) as error:
        report.errors.append(f"sitemap.xml: missing or invalid XML: {error}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("dist"))
    parser.add_argument("--public-url", default=PUBLIC_SITE)
    args = parser.parse_args(argv)
    report = audit_site(args.site, base_url=args.public_url)
    if not report.valid:
        for error in report.errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(report.errors)} site integrity violations across {report.pages} pages")
        return 1
    print(
        f"PASS: {report.pages} HTML pages, {report.links} URLs, "
        f"{report.fragments} anchors and exact sitemap/canonical coverage"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
