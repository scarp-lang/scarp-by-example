# Declarative Scarp projects (`scarp.project`)

This is the recommended **current project format** for the active, published
[Scarp compiler](compiler-target.json). Since alpha.8, `scarp init`
creates lowercase `scarp.project` files. Since alpha.18,
`scarp exec` with no source argument can select a valid
project in the **current directory**. The older `Scarp.project`
manifest and `scarp create` are supported for compatibility
but are not the recommended starting point.

[Open the runnable project](../tutorials/declarative-project/README.md) ·
[Read this tutorial in Hindi](hi/declarative-projects.md) ·
[See the legacy v1 guide](project-workflow.md)

## 1. Create a new project

```sh
scarp init learning-project
scarp verify learning-project
scarp run learning-project
```

`init` only accepts a path that does **not** exist;
never run it on the checked-in sample. The command creates
`scarp.project`, `src/main.srp` and
other empty folders in a scaffold. The checked-in tutorial project is an
independently authored sample with two tests and an import.

```text
tutorials/declarative-project/
├── scarp.project
├── src/main.srp
├── src/totals.srp
├── tests/01-multiplication.srp
├── tests/02-input.srp
├── tests/02-input.stdin
└── expected.stdout
```

The manifest declares the project's name, version, entry and type:

```text
project "learning-project" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
```

**Not TOML/JSON:** the Scarp compiler parses this dedicated text grammar.
The `dependencies {}` block reserves syntax but
does **not** install or resolve packages.

## 2. Static verification versus execution

From the learning repository root:

```sh
scarp verify tutorials/declarative-project
scarp run tutorials/declarative-project
```

Successful `verify` writes no output and does not execute
ordinary statements. `run` executes the imported
`totals.multiply(6, 7)` function. The exact stdout is:

```text
Total: 42
```

In the project folder, no-argument commands work:

```sh
cd tutorials/declarative-project
scarp verify
scarp exec
```

These commands use the **current working directory**, not an ancestor
directory search. `exec` without a file has a fallback
for directories that do not contain a project manifest, but **must
reject a malformed existing manifest**, not silently run another file.

## 3. Read validated project metadata

```sh
scarp project info --json tutorials/declarative-project
```

This does not execute source or load imports. The expected schema-v1
metadata includes `name: learning-project`,
`version: 0.1.0`, `manifest: scarp.project`,
`format: v2`, `type: application` and
`entry: src/main.srp`. A malformed manifest reports
an error rather than returning partial metadata.

## 4. Discover and execute real tests

```sh
scarp test --list --json tutorials/declarative-project
scarp test --require-tests --json tutorials/declarative-project
scarp test --json --filter input tutorials/declarative-project
```

`--list` checks test paths without executing the
tests. The `--require-tests` flag prevents a vacuous
success when no tests are present. The two files are run in lexicographic
order, producing a JSON report with `discovered: 2`,
`passed: 2` and `failed: 0`.

`01-multiplication.srp` imports and asserts the
multiplication function. `02-input.srp` reads two
numbers from its **sibling `02-input.stdin` fixture**:
6 and 7. The test runner does not consume the terminal's stdin;
an unrelated test receives no such input.

The CI verifier
[`verify_declarative_project.py`](../scripts/verify_declarative_project.py)
checks all of this on the exact compiler source pin and on Linux,
Windows and macOS. It also creates a **temporary** invalid manifest
with a traversal entry, verifying that static verification, metadata
inspection and implicit execution reject it. The checked-in tutorial
is never mutated by the verifier.

## Format limitations and migration

The manifest is bounded to 4096 UTF-8 bytes; fields are strict and
a declared entrypoint must stay inside the project. The only current
project type is `application`. Paths with traversal,
invalid components, unsafe symlinks and unknown/duplicate fields are
rejected. Do not distribute both `scarp.project` and
`Scarp.project` in the same project: case-sensitive and
case-insensitive filesystems handle such pairs differently.

To migrate a legacy sample, create a new lowercase manifest with
the same intended entry, run `scarp verify` and
`scarp run`, then remove the older manifest after
validation. Do not merely lowercase the filename while retaining the
three-line `scarp-project: 1` body and assume the
format is upgraded.

There is **no** dependency registry, lockfile, remote package install,
native executable compiler, workspace discovery or browser interpreter
in this project workflow. See the [official compiler project format](https://github.com/scarp-lang/scarp/blob/e534e73a81c9500e3aef9f3d51cafa0bc7bbcf75/docs/project-v2.md).
