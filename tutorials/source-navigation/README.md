# Source navigation workshop · Scarp alpha.6

This is an **executable two-module project**, separate from the 51 numbered lessons. The source is adapted from Scarp's published `v0.0.6-alpha.1` example `examples/symbol_navigation.srp`: the import path is relocated into this project's `src/lib/` directory. The helper and exact expected output are from the same tagged upstream source; see [third-party notices](../../THIRD_PARTY_NOTICES.md). No sample JSON is fabricated.

From the **Scarp by Example repository root**, using the [pinned compiler](../../docs/compatibility.md):

```sh
scarp verify tutorials/source-navigation
scarp inspect modules --json tutorials/source-navigation
scarp inspect symbols --json tutorials/source-navigation
scarp inspect references --json tutorials/source-navigation
scarp launch tutorials/source-navigation
```

The read-only inspection commands never execute ordinary program statements. `launch` runs the actual interpreter and prints `30` followed by LF, matching [expected.stdout](expected.stdout). You can replace the directory argument with `tutorials/source-navigation/src/main.srp` for the two symbol/reference commands.

## What to look for

1. Find the public `offset` and `adjust` declarations in the imported module, and the private `private_seed`. The `library` alias is defined in `main.srp`.
2. Locate the two **different** `base` declarations: the outer one is used to initialize the inner one; the inner one is used by the accumulator.
3. Find the named argument sites `value:` and `n:` and identify the parameter declarations to which their references resolve.
4. Look for the `step` loop index and the call to `twice`.
5. Compare file- and directory-based inspection. Display paths may differ, and `symbol.id` is local to one snapshot. Do not compare IDs across invocations.

The browser website displays the original source, expected output and instructions, but it **does not run Scarp**. Read the [English teaching guide](../../docs/source-navigation.md), [Hindi guide](../../docs/hi/source-navigation.md) or [workshop page](https://scarp-lang.github.io/scarp-by-example/projects/source-navigation/).
