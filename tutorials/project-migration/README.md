# Migrate a Scarp project: legacy v1 → declarative v2

This workshop includes two runnable projects checked against the published
compiler in [`docs/compiler-target.json`](../../docs/compiler-target.json).
It is a guide to **manual migration**, not an automatic rewriting tool.

## Files you can compare

```text
project-migration/
├── legacy/
│   ├── Scarp.project
│   ├── src/main.srp
│   ├── src/lib/math.srp
│   ├── tests/01-arithmetic.srp
│   ├── tests/02-input.srp
│   ├── tests/02-input.stdin
│   └── expected.stdout
└── modern/
    ├── scarp.project
    ├── src/main.srp
    ├── src/lib/math.srp
    ├── tests/01-arithmetic.srp
    ├── tests/02-input.srp
    ├── tests/02-input.stdin
    └── expected.stdout
```

**Only the manifest differs.** Every `.srp` file, import, test
program, input fixture and output fixture has identical bytes between
these two directories. Their Python verifier rejects accidental divergence.

Before — `legacy/Scarp.project` (format v1):

```text
scarp-project: 1
name: project-migration
entry: src/main.srp
```

After — `modern/scarp.project` (format v2):

```text
project "project-migration" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
```

The new format is **not TOML**, JSON, or executable Scarp source.
`dependencies {}` does not install or resolve packages. A lowercase
filename containing the three-line legacy body is **not** a v2 migration.

## Reproduce the exact program and test results

From the learning repository root:

```sh
scarp verify tutorials/project-migration/legacy
scarp verify tutorials/project-migration/modern

scarp run tutorials/project-migration/legacy
scarp run tutorials/project-migration/modern

scarp project info --json tutorials/project-migration/legacy
scarp project info --json tutorials/project-migration/modern

scarp test --list --json tutorials/project-migration/legacy
scarp test --list --json tutorials/project-migration/modern
scarp test --require-tests --json tutorials/project-migration/legacy
scarp test --require-tests --json tutorials/project-migration/modern
```

Both `run` commands must print exactly:

```text
Migrated: 42
```

Both suites discover **two** tests; both should report
`discovered: 2`, `passed: 2` and `failed: 0`.
The input test reads `19` and `23` from its own
`02-input.stdin`, never shell stdin. Its imported function still
computes 42.

`project info --json` exposes the real distinction: the legacy
manifest reports `format: legacy-v1` and a null version; the modern
manifest reports `format: v2` and `version: 0.1.0`.

From inside either project folder, `scarp exec` without arguments
uses that directory's manifest (supported by published alpha.18+).

## Safe manual migration procedure

1. Make a copy of your existing project or use version control.
2. Preserve the `src/`, `tests/` and import graph initially.
3. **Replace** the old three-line `Scarp.project` with a new
   lowercase `scarp.project` that has the v2 declarative body.
4. Confirm `scarp project info --json` reports `"format": "v2"`.
5. Run `scarp verify`, `scarp run` and
   `scarp test --require-tests --json`; compare output
   with the legacy project before making other changes.

Do not ship both manifest spellings in the same directory; they cannot
coexist reliably on case-insensitive filesystems.

## CI regression coverage

```sh
python scripts/verify_project_migration.py --compiler /absolute/path/to/scarp
```

The real-compiler verifier checks exact source parity, project metadata,
static verification, execution, implicit project discovery, read-only
module inspection, direct test listing, test execution, input test
selection and byte-exact stdout. Temporary copies prove that a
rename-only attempt cannot masquerade as v2 and an intentionally
failing `scarp test --json=v2` still reports its runtime failure.

**हिन्दी:** सिर्फ़ फ़ाइल का नाम बदलने से नया प्रारूप नहीं बनता।
`scarp.project` में सही `project`, `version`, `entry` और `type`
घोषित करें। पुराने और नए प्रोजेक्ट का आउटपुट और दोनों टेस्ट
मिलाने के बाद ही पुराने मैनिफ़ेस्ट को हटाएँ।

[English guide](../../docs/project-migration.md) ·
[हिन्दी मार्गदर्शिका](../../docs/hi/project-migration.md) ·
[Modern projects](../../docs/declarative-projects.md)
