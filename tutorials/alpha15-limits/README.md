# Alpha.15: bounded inspection and UTF-8 string comparisons

**Release:** [Scarp v0.0.6-alpha.15](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.15)
([source `a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281`](https://github.com/scarp-lang/scarp/commit/a21b7b6d942bd1ca9abbbbb522f92f9c8e21e281), 19 November 2026).
This is an **optional local tutorial**, not another numbered lesson or a browser interpreter.

## Run a real comparison

The [Scarp source](string-comparisons.srp) compares Hindi UTF-8 strings and
prints the two exact lines in its [output fixture](string-comparisons.stdout).
From the learning repository root, run the published alpha.15 compiler:

```sh
scarp verify tutorials/alpha15-limits/string-comparisons.srp
scarp exec tutorials/alpha15-limits/string-comparisons.srp
```

Expected stdout:

```text
true
true
```

Equal-byte-length string equality and inequality now charge **one work step
per started 64 UTF-8 bytes**, in addition to expression overhead. A character
can occupy several UTF-8 bytes, so character count is not the work meter unit.
The 129-byte comparison witness in the verifier has a program-specific boundary:
`--max-steps 12` produces E0017 and `--max-steps 13` succeeds.
**13 steps is not a universal allowance for all comparisons.**

## Inspect the source size boundary

`scarp inspect tokens FILE` lexes one file, `scarp inspect ast FILE`
parses it, and legacy `scarp tokens FILE` remains available.
These commands inspect source and do not execute runtime statements.

Published alpha.15 accepts a source file of **exactly 1,048,576 bytes (1 MiB)**
for these operations, but rejects a file with **1,048,577 bytes** before
tokenization. This is a byte limit, not a line or character limit.

Run the regression with the real binary and exact compiler checkout:

```sh
python scripts/verify_alpha15_limits.py --compiler /path/to/scarp --compiler-source /path/to/alpha15-checkout
```

The verifier checks Git HEAD, binary version, static verification, exact
stdout, both file-size boundaries, JSON errors, and string work quotas.
It creates temporary files and uses only Python's standard library.
The website does **not** execute Scarp; experimental semantic-cache revision
checks and checked ELF64 integer shifts are Rust embedding APIs, not
language keywords or a general `scarp compile` command.

[हिन्दी मार्गदर्शिका](../../docs/hi/alpha15-limits.md) ·
[Compiler compatibility](../../docs/compatibility.md) ·
[Main course](../../README.md)
