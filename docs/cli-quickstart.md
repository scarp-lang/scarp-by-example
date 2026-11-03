# Scarp CLI quickstart (v0.0.5-alpha.3)

Use this guide with the **published Scarp v0.0.5-alpha.3 source at commit `7715c28df09c7703b39e14fddb963275b25df476`**. Scarp is a prerelease language. The commands below were checked against that source, not guessed from future roadmap proposals.

This is a **tooling guide**, not a new runnable `.srp` lesson. Command outputs such as tokens or an AST are development-oriented and deliberately do not have `.stdout` fixtures.

## 1. Get the matching compiler

Follow the [compatibility instructions](compatibility.md) to check out and build the pinned Scarp source. Check the executable itself:

```sh
scarp version
scarp guide
scarp diagnose
```

`scarp version` prints the running compiler's version. `scarp guide` shows supported commands. `scarp diagnose` reports local compiler and host capabilities without accessing a network. If `scarp` is not on your PATH, replace it in every example with the full path to `target/debug/scarp` (Windows: `target\debug\scarp.exe`). Run the examples from the **scarp-by-example repository root**; source paths below are relative to that directory.

## 2. Verify, then execute

```sh
scarp verify examples/01-basics/01-hello.srp
scarp exec examples/01-basics/01-hello.srp
```

- `verify` loads the source and imports and performs available syntax, name and type checks **without evaluating runtime statements**. A successful check is silent and returns exit code 0.
- `exec` executes the program with the current Scarp interpreter. The hello lesson prints `Hello from Scarp!` followed by a newline; compare the exact bytes with [its fixture](../examples/01-basics/01-hello.stdout).
- `exec` is **not** a native compilation or a project build. It accepts one source file; it does not forward program arguments.

For a module-backed example, keep the local `_support` files in place:

```sh
scarp verify examples/05-modules/01-modular-inference.srp
scarp exec examples/05-modules/01-modular-inference.srp
```

## 3. Inspect source (read-only)

```sh
scarp guide inspect tokens
scarp inspect tokens examples/01-basics/01-hello.srp
scarp inspect ast examples/01-basics/01-hello.srp
scarp inspect modules examples/05-modules/01-modular-inference.srp
scarp inspect modules --json examples/05-modules/01-modular-inference.srp
```

| Command | What it actually checks | Output |
| --- | --- | --- |
| `inspect tokens` | Lexes the entry file only; does not parse names or types | Tokens and source locations |
| `inspect ast` | Parses the entry file; does not resolve imports or type-check | Human-readable **unstable** debug syntax tree |
| `inspect modules` | Loads and statically checks the module graph, including supported compile-time constants | Module inventory; `--json` is available here only, with schema version 1 |

The inspect commands do not execute the lesson's runtime statements. Successful AST output is **not** a stable JSON API; `--json` does **not** apply to `inspect ast` or `inspect tokens`. Inspection output is not the lesson's expected program stdout.

## 4. Why `verify` and `check` are different

The older `run` command still behaves like `exec` for this compiler. But **`check` is not a synonym for `verify`**: `check` executes selected runtime paths while suppressing their output.

For an optional local experiment, save this temporary program outside the numbered lesson catalog:

```scarp
print(1 / 0);
```

`scarp verify FILE.srp` succeeds because the program is syntactically and statically valid; `scarp check FILE.srp` fails when it evaluates division by zero. `scarp exec FILE.srp` also fails. This example tests the command distinction, not a recommended way to write programs. The [CLI regression test](../scripts/verify_cli.py) creates and removes its own temporary file to check this behavior without adding an unsupported lesson.

## Command reference

| Command | Purpose |
| --- | --- |
| `scarp version` / `scarp guide` | Version and built-in usage |
| `scarp diagnose` / `scarp diagnose --json` | Local host/compiler capability report |
| `scarp verify FILE` | Static validation only |
| `scarp exec FILE` | Execute one source program |
| `scarp inspect tokens FILE` | Inspect lexer output |
| `scarp inspect ast FILE` | Inspect parser's development tree |
| `scarp inspect modules [--json] FILE` | Inspect the statically checked module graph |
| `scarp run FILE` / `scarp check FILE` | Older compatibility commands; check evaluates code |

Success typically returns exit code `0`; source or execution failures return `1`, invalid CLI usage returns `2`. Runtime diagnostics may be printed to stderr, while `exec` program output goes to stdout. When debugging a file, `scarp guide exec` or `scarp guide verify` shows focused help.

**Not supported by this pinned CLI:** `scarp compile`, `scarp create`, `scarp launch`, package publishing, LSP, native code emission, and general automatic differentiation. The exact compiler SHA and prerelease status matter more than guessing from newer upstream documentation.

[Back to the course](../README.md) · [हिन्दी CLI गाइड](hi/cli-quickstart.md) · [Compiler compatibility](compatibility.md)
