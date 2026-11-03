# Your first real Scarp project (v0.0.5-alpha.4)

This guide teaches the **published** Scarp v0.0.5-alpha.4 project commands. It is based on the exact tagged source commit `79141329176f5dce51457e90a6652902f6432135`, not unmerged compiler PRs. [Compiler compatibility](compatibility.md) · [हिन्दी गाइड](hi/project-workflow.md)

A project is a directory containing a manifest `Scarp.project` and a selected `.srp` entrypoint. Alpha.4's project workflow uses the real **interpreter**, not native executable generation or package distribution.

## 1. Start from a new directory

In a working folder where `hello-world` does **not** already exist, run:

```sh
scarp create hello-world
```

The compiler creates:

```text
hello-world/
├── Scarp.project
└── src/
    └── main.srp
```

The generated manifest is exactly:

```text
scarp-project: 1
name: hello-world
entry: src/main.srp
```

The generated entry file is:

```scarp
print("Hello from Scarp!");
```

`create` never overwrites or adopts a destination that already exists, even an empty directory. Its parent directory must already exist. This command does **not** download packages or access any registry.

## 2. Validate the project without executing it

```sh
scarp verify hello-world
```

Here `hello-world` is the explicit **project directory**, not a file. The compiler checks the bounded manifest, resolves the entrypoint inside that directory, and statically validates Scarp source/imports without evaluating runtime statements. Success is silent. If you instead run `scarp verify hello-world/src/main.srp`, the compiler checks that single source file without reading the project manifest.

## 3. Launch the real interpreter

```sh
scarp launch hello-world
```

Expected program stdout:

```text
Hello from Scarp!
```

`launch` uses the real interpreter and the same runtime budget/diagnostic behavior as `scarp exec FILE.srp`. It does not generate a native executable. It takes an explicit project directory; there is no automatic search for an ancestor `Scarp.project`.

## 4. Verify the checked-in sample from this course

The [sample manifest](../tutorials/first-project/Scarp.project), [Scarp source](../tutorials/first-project/src/main.srp), and [byte-exact stdout](../tutorials/first-project/expected.stdout) are stored in this repository. From the **scarp-by-example repository root**, run:

```sh
scarp verify tutorials/first-project
scarp launch tutorials/first-project
```

The [CLI smoke test](../scripts/verify_cli.py) checks this project with the actual pinned compiler on Linux, Windows and macOS. This tutorial is separate from the **50 numbered lessons**, whose existing `.srp` and `.stdout` fixtures remain unchanged.

## 5. Practice by editing a copy

Create your own new project, then replace its `src/main.srp` contents with:

```scarp
print(6 * 7);
```

Run `scarp verify YOUR_PROJECT_DIRECTORY`, then `scarp launch YOUR_PROJECT_DIRECTORY`. The supported integer multiplication prints `42`. Check the result yourself before looking at the source. Do not modify the course's checked-in sample when practicing.

A second useful experiment is to use a syntactically valid runtime error, such as `print(1 / 0);`, in your own temporary project: `verify` passes the static check while `launch` returns a runtime error. This is the difference between static validation and program execution; the automated project smoke test checks the same distinction in an isolated temporary directory.

## Manifest constraints and security boundaries

| Rule | Published alpha.4 behavior |
| --- | --- |
| Format | UTF-8 with exactly three ordered lines: version, name, entry |
| Version | `scarp-project: 1` |
| Maximum manifest | 4,096 bytes |
| Project name | 1–96 UTF-8 bytes, no path separators, colon or controls |
| Entrypoint | Contained relative `.srp` file, e.g. `src/main.srp` |
| Missing/unknown fields | Rejected rather than ignored |
| Traversal or unsafe symlinks | Rejected to keep entrypoint inside the project |
| `verify DIRECTORY` | Static checks, no program output, no runtime-budget flags |
| `launch DIRECTORY` | Interpreter execution with runtime budgets |
| Invalid manifest | Exit code 1; optional schema-v1 JSON diagnostics |

To see structured error details use `scarp verify --diagnostic-format=json YOUR_PROJECT_DIRECTORY`. The JSON diagnostic schema is versioned, but `Scarp.project` is still an experimental development format.

## Not implemented

`create`/`launch` do **not** provide a registry, dependency resolution, a lockfile, general workspace discovery, multiple project entrypoints, a source-to-native executable compiler or package publishing. Future language features must not be inferred from these commands.

[Course homepage](../README.md) · [CLI quickstart](cli-quickstart.md) · [Published compiler release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.5-alpha.4)
