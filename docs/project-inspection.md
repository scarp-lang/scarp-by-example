# Inspect a Scarp project without executing it

**Published target:** [Scarp v0.0.5-alpha.5](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.5), source commit `2eeed0aa52ccb59523307841ad8ffbd83f8911a8` (**prerelease**, not stable).

New in the published alpha.5 CLI: `scarp inspect modules --json PROJECT_DIRECTORY`. This resolves an explicit `Scarp.project`, statically checks its entrypoint and relative imports, then emits **schema-version-1 module metadata**. It does **not** run `print` or any ordinary program statement.

[Open the illustrated course page](https://scarp-lang.github.io/scarp-by-example/projects/module-inspection/) · [हिन्दी में पढ़ें](hi/project-inspection.md)

## 1. Explore the checked-in two-module project

```text
tutorials/module-inspection/
├── Scarp.project
├── src/
│   ├── main.srp
│   └── lib/
│       └── math.srp
└── expected.stdout
```

The actual manifest is:

```text
scarp-project: 1
name: module-inspection
entry: src/main.srp
```

The entrypoint `src/main.srp` reads:

```scarp
import "lib/math.srp" as math;
print(math.answer);
```

The helper `src/lib/math.srp` exports a public compile-time scalar binding:

```scarp
// Public compile-time scalar binding imported by main.srp.
pub bind answer = 21 * 2;
```

The checked-in output fixture is one line, `42`. The project is **separate** from the 50 numbered runnable course lessons.

## 2. Inspect first, then launch

Run from the **scarp-by-example** repository root, using the exact alpha.5 CLI:

```sh
scarp verify tutorials/module-inspection
scarp inspect modules --json tutorials/module-inspection
scarp inspect modules --json tutorials/module-inspection/src/main.srp
scarp launch tutorials/module-inspection
```

- `verify DIRECTORY` validates the versioned manifest, entrypoint and imported source **statically**, with successful output on neither stream.
- Both `inspect modules --json` commands expose schema-v1 module metadata. The project-directory form resolves to the same canonical entrypoint as the source-file form. Their module graph and symbol metadata should agree; schema-v1 `module.path` is a loader-provided **display label**, so its presentation can differ by operating system or invocation. They do not print the program result.
- `launch DIRECTORY` executes through the actual interpreter and prints `42` followed by LF. Compare its stdout byte-for-byte with [expected.stdout](../tutorials/module-inspection/expected.stdout).

You can also run `scarp modules --json tutorials/module-inspection` for legacy compatibility, but prefer the Scarp-first `inspect modules` spelling in new tooling. Use `scarp guide inspect modules` for current help.

The course's `scripts/verify_cli.py` tests directory/file semantic inventory parity on the pinned compiler, ignoring only platform-dependent module display labels. It also asserts inspection does not run a runtime-failing statement, and that an invalid manifest is rejected without partial JSON output.

## 3. Try a small experiment

Create a **new copy** of the project directory. Change the public binding in `src/lib/math.srp` to `pub bind answer = 30 + 12;`. Before running anything, inspect the project again. Then verify and launch it. Both expressions yield the same final scalar result, so the expected output remains `42`. Restore the original file before submitting changes to this repository.

Keep import paths portable, relative to the importing source, and confined to the checked project root. The compiler enforces bounded source reads and manifest checks; do not treat that as a security sandbox for untrusted concurrent filesystem changes.

## 4. What alpha.5 does *not* provide

The interpreter still cannot build a native Scarp executable from `.srp` using a `scarp compile` command. Alpha.5's **experimental scalar C11 emitter is a Rust embedding API** (`scarp::c_backend::emit_c` / `emit_program`) that supports only a restricted subset; it requires a separate C11 compiler provided by the embedding host. The course does not claim general-purpose native compilation, a stable C ABI, a package manager, a GPU backend, async/networking or autograd.

For compiler compatibility and reproducible source verification, see [the pinned source policy](compatibility.md), [CLI quickstart](cli-quickstart.md) and [project creation tutorial](project-workflow.md).
