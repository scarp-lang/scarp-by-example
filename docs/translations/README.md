# Localization / स्थानीयकरण

English is the canonical teaching text during initial development. Hindi explanations are planned.

Rules for translations:
- Keep section and lesson IDs aligned across locales.
- Translate headings and explanations, but do not change source syntax or exact output fixtures.
- Preserve links to the same runnable `.srp` files and tested compiler revision.
- Ask a language reviewer to check technical terms and beginner clarity.
- Mark untranslated content transparently; do not invent compiler features.

The source lesson and its stdout fixture are locale-neutral. Translation changes must never bypass the compiler validation workflow.

## Published Hindi guides

[Hindi learning index](../hi/README.md) now covers every lesson of chapters 01 and 02 using original `.srp` and `.stdout` links. Keep these guides in sync whenever a new lesson is introduced in those chapters.
