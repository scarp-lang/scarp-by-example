# Migrating Scarp projects: `Scarp.project` → `scarp.project`

The published Scarp compiler understands **two distinct project manifest
formats**. For new projects, use declarative **v2** via
`scarp init NEW_DIRECTORY`. The three-line v1 format created by
`scarp create` remains supported for older projects.

The [side-by-side runnable workshop](../tutorials/project-migration/README.md)
contains the same executable program, imported module, two Scarp test
programs, stdin fixture and stdout fixture under both formats. This is
a reproducible *migration parity test*, not a package installer or
automatic converter.

[हिन्दी में पढ़ें](hi/project-migration.md) ·
[Modern project introduction](declarative-projects.md) ·
[Historical v1 guide](project-workflow.md)

## Only change the manifest at first

| | Legacy v1 | Declarative v2 |
| --- | --- | --- |
| Filename | `Scarp.project` | `scarp.project` |
| Format discriminator | `scarp-project: 1` | `project "name" { ... }` |
| Name | `name: project-migration` | `project "project-migration"` |
| Version | not declared (JSON `null`) | `version: "0.1.0"` |
| Entry | `entry: src/main.srp` | `entry: "src/main.srp"` |
| Type | implicit application | `type: "application"` |
| Dependencies | none | optional empty `dependencies {}` |
| Metadata `format` | `legacy-v1` | `v2` |

**Not TOML:** the v2 manifest is a small Scarp-specific declarative
grammar. Real dependency management is not implemented. The old
three-line body is still v1 even when renamed to lowercase.

## Check before and after

Use the compiler version from
[the active course pin](compiler-target.json). Run from the course root:

```sh
scarp verify tutorials/project-migration/legacy
scarp verify tutorials/project-migration/modern
scarp run tutorials/project-migration/legacy
scarp run tutorials/project-migration/modern
```

Both executions print **`Migrated: 42`** followed by one LF.
The source imports a public pure `add` function from `src/lib/math.srp`.
Successful `verify` is silent and does not execute runtime statements.

Read metadata without running code:

```sh
scarp project info --json tutorials/project-migration/legacy
scarp project info --json tutorials/project-migration/modern
```

The schema is version 1 for the JSON report, irrespective of the
manifest's **own** format number. The first report has
`"format": "legacy-v1"` and `"version": null`; the second
has `"format": "v2"` and `"version": "0.1.0"`. Both preserve
the project name and entrypoint.

Check that tests and input fixtures migrate with the code:

```sh
scarp test --list --json tutorials/project-migration/legacy
scarp test --require-tests --json tutorials/project-migration/legacy
scarp test --list --json tutorials/project-migration/modern
scarp test --require-tests --json tutorials/project-migration/modern
```

Listing is read-only. Running the suite executes two ordinary
`tests/*.srp` programs. The second test reads only its matching
`02-input.stdin` file, so the two project copies check the
same input and assertions.

## Step-by-step safe migration

1. **Keep a backup.** Work in a new directory or tracked branch.
2. Copy `src/`, `tests/`, relevant fixtures and module imports
   unchanged.
3. Replace the v1 manifest with the new lowercase v2 manifest;
   set the version, entry and `application` type explicitly.
4. Remove the old manifest rather than keeping two spellings
   side by side.
5. Confirm the reported metadata's `format` is exactly `v2`.
6. Verify, execute and run the same tests; compare program stdout
   byte-for-byte with your legacy project.
7. Only then start using new language features or project settings.

On case-insensitive disks, `Scarp.project` and `scarp.project`
may be the *same file path*. Do not rely on both names existing;
replace the content using version control or write a temporary
new filename before renaming.

## Debugging failed migration tests

The workshop's
[real compiler verifier](../scripts/verify_project_migration.py)
creates temporary test copies: it proves a lowercase legacy body
is **not** identified as declarative v2, then adds one intentionally
failing assertion and checks `scarp test --json=v2` returns a
structured runtime failure with nonzero status. The committed
project fixtures themselves remain green and untouched.

The released project workflow does not generate native executables,
install packages, resolve dependencies, search parent directories or
provide a browser interpreter. Unsupported capabilities are not
implied by copying these examples.
