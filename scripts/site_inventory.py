"""Expected site inventory derived from real version-pinned course sources.

This module deliberately does not hardcode the lesson count or total pages:
adding a new verified `.srp` lesson should expand both automatically, while
a missing or unexpected route still fails the route-inventory test.
"""

from __future__ import annotations

from build_site import chapter_url, read_course
from guided_labs import read_labs

STATIC_PAGE_PATHS = frozenset({
    "index.html",
    "labs/index.html",
    "projects/index.html",
    "projects/module-inspection/index.html",
    "projects/source-navigation/index.html",
})


def expected_lesson_count() -> int:
    """Count actual validated, release-pinned runnable course lessons."""
    lessons, _, _ = read_course()
    return len(lessons)


def expected_page_paths() -> set[str]:
    """List exact generated HTML routes, not only an assumed total."""
    lessons, chapters, _ = read_course()
    return (
        set(STATIC_PAGE_PATHS)
        | {lesson.url for lesson in lessons}
        | {chapter_url(section) for section in chapters}
        | {lab.url for lab in read_labs()}
    )
