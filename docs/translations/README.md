# Localization / स्थानीयकरण

English is the canonical teaching text; Hindi companion guides are available for all six currently published chapters.

Rules for translations:
- Keep section and lesson IDs aligned across locales.
- Translate headings and explanations, but do not change source syntax or exact output fixtures.
- Preserve links to the same runnable `.srp` files and tested compiler revision.
- Ask a language reviewer to check technical terms and beginner clarity.
- Mark untranslated content transparently; do not invent compiler features.

The source lesson and its stdout fixture are locale-neutral. Translation changes must never bypass the compiler validation workflow. The website now embeds each Hindi lesson's explanation directly into its dedicated page using the matching numbered heading from the corresponding `docs/hi/NN-*.md` chapter guide. Every numbered Hindi section must contain one matching source link, one matching output link, and an `**अभ्यास:**` exercise. `scripts/test_lesson_notes.py` enforces this one-to-one mapping.

## Published Hindi guides

[Hindi learning index](../hi/README.md) covers all published lessons across chapters 01–06, linking to the same original `.srp` and `.stdout` files. The translation parity unit test verifies that every current lesson is linked exactly once by source and stdout. When adding a new lesson or chapter, add its Hindi companion coverage in the same PR, or explicitly propose a policy change with clear untranslated status instead of silently omitting content.
