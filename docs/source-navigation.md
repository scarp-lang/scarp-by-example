# Navigate Scarp names and references (v0.0.6-alpha.1)

Scarp alpha.6 introduces **static**, opt-in source intelligence. You can ask which identifiers are declared or used in an imported module without running the program. This is a compiler feature, **not** an LSP server, editor integration, automatic rename or an incremental cache.

This tutorial reuses the [two-module project](../tutorials/module-inspection/Scarp.project) that already has an exact interpreter output fixture. The public `answer` binding is declared in `src/lib/math.srp`, then accessed via the `math` import alias in `src/main.srp`.

## Run the commands

First install or build the exact [pinned prerelease](compatibility.md). From the course root:

```sh
scarp verify tutorials/module-inspection
scarp inspect modules --json tutorials/module-inspection
scarp inspect symbols --json tutorials/module-inspection
scarp inspect references --json tutorials/module-inspection
scarp launch tutorials/module-inspection
```

The two new `inspect` commands produce **metadata on stdout**. `launch` is the only command here that runs the ordinary statements and prints `42` followed by a newline, matching the project's [fixture](../tutorials/module-inspection/expected.stdout). There is no corresponding `.stdout` lesson for a JSON index.

Both `inspect` commands also accept `tutorials/module-inspection/src/main.srp` instead of the directory. They resolve the import and type-check the full source graph. File display labels may differ between paths and operating systems; avoid comparing raw JSON byte-for-byte across machines.

## How to read the JSON

Both views use `schema_version: 1`, `span_encoding: "utf-8-bytes"`, `column_encoding: "unicode-scalar"` and one-based line/column positions. The `kind` is `"scarp.symbols"` or `"scarp.references"`. Expect:

- `files`: discovered source-file IDs and display paths.
- `symbols`: definitions and other named identities, such as the `math` alias and public `answer`. Some builtins have no source `location`.
- `references` (reference view only): each use site's `target` symbol ID, use `kind` and source location.

A `location.span` is a half-open **UTF-8 byte range**, not a Unicode character count. Symbol IDs are **only valid inside that one result**. After editing a file or running inspection again, rebuild the index instead of caching IDs. The compiler checks imports, privacy and names; errors return nonzero with no partial JSON.

## Why read-only matters

Try a disposable file with `print(1 / 0);`. `inspect symbols --json FILE` and `inspect references --json FILE` can succeed because they **do not evaluate runtime arithmetic**. `exec FILE` fails at runtime. Conversely, an unknown identifier fails inspection because static name resolution still applies. The [CLI regression test](../scripts/verify_cli.py) checks these boundaries and the project/file consistency against the released compiler.

**Exercise:** inspect the two-module project, locate the `answer` declaration and the reference in the entrypoint, then compare the file and directory views while ignoring platform-specific display paths.

See the [compiler's versioned index contract](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.1/docs/symbol-index.md) and [Hindi companion guide](hi/source-navigation.md). No general editor integration or browser-side Scarp execution is implied.
