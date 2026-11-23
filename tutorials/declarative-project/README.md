# Your first declarative Scarp project

**Requires the actively pinned [Scarp compiler release](../../docs/compiler-target.json).**
This is a complete, **original** runnable project with lowercase **`scarp.project`**
(manifest v2), source imports, a pure helper, two tests and a stdin fixture. It
uses the interpreter; it does not compile to a native executable.

## Project structure

```text
declarative-project/
├── scarp.project
├── src/
│   ├── main.srp
│   └── totals.srp
├── tests/
│   ├── 01-multiplication.srp
│   ├── 02-input.srp
│   └── 02-input.stdin
└── expected.stdout
```

## Run from the learning repository root

```sh
scarp verify tutorials/declarative-project
scarp run tutorials/declarative-project
scarp project info --json tutorials/declarative-project
scarp test --list --json tutorials/declarative-project
scarp test --require-tests --json tutorials/declarative-project
```

Expected application stdout (byte-exact):

```text
Total: 42
```

To try **no-argument** `exec` (introduced in published alpha.18),
change into `tutorials/declarative-project` and run `scarp exec`. The
current directory has a validated manifest, so this runs `src/main.srp`.
`scarp verify` from the same directory statically checks the project.

The manifest is declarative **Scarp-specific text, not TOML or JSON**:
`project`, its name, version, entrypoint, application type and optional
empty `dependencies {}` block. Real dependency resolution is not available.
`scarp init NEW_DIRECTORY` scaffolds this lowercase format; it rejects
any destination that already exists. The older `scarp create` generates
a historical `Scarp.project` manifest and is retained for compatibility.

The test runner executes direct `tests/*.srp` files; tests are ordinary
Scarp programs using `assert`. Test `01-multiplication.srp` checks
pure multiplication. Test `02-input.srp` consumes **only** its
`02-input.stdin` UTF-8 fixture (`6` LF `7` LF); the shell's
stdin is not used. The test runner's JSON listing never executes source.
The `--require-tests` flag prevents a silently empty test suite from
passing CI. Use `--filter input` to select the second test.

## Practice / अभ्यास

Change the application call to `totals.multiply(7, 8)` in a
**copy** of this project. Predict the output before running `verify`
then `exec`. Add another `tests/*.srp` file asserting that
`multiply(7, 8) == 56`. Do not change the checked-in reference fixtures.

**हिन्दी:** `scarp.project` नए प्रकार का मैनिफ़ेस्ट है। पहले `verify` से
कोड की स्थिर जाँच करें, फिर `run` या प्रोजेक्ट फ़ोल्डर के अंदर से
`exec` चलाएँ। `test --require-tests --json` दोनों असली टेस्ट चलाता
है। दूसरे टेस्ट का इनपुट केवल उसकी `.stdin` फ़ाइल से आता है।

## Limits

The project reader is bounded, validates the declared entrypoint, rejects
unknown/duplicate manifest fields, unsafe entry paths and malformed input.
A malformed manifest cannot be bypassed by silently executing a nearby
`main.srp`. No package registry, dependency resolution, lockfile,
project workspaces, browser execution or general native compilation is implied.

[Full English guide](../../docs/declarative-projects.md) ·
[हिन्दी मार्गदर्शिका](../../docs/hi/declarative-projects.md) ·
[Historical v1 project guide](../../docs/project-workflow.md)
