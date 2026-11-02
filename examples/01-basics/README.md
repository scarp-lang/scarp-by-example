# 01 · Scarp basics

Start with the basics before tackling functions and modules.

All examples are copied from the [Scarp compiler example suite](https://github.com/scarp-lang/scarp/tree/main/examples), whose `scripts/check.sh` exercises these programs. See [upstream attribution](../../THIRD_PARTY_NOTICES.md).

| Lesson | Learn | Expected result |
| --- | --- | --- |
| [01 · Hello](01-hello.srp) | `print` displays a string | `Hello from Scarp!` |
| [02 · Bindings](02-bindings.srp) | `bind` defines immutable values and expressions | Area followed by `42` |
| [03 · Mutable values](03-mutable.srp) | `var`, assignments and compound arithmetic | Sequence shown in [stdout](03-mutable.stdout) |
| [04 · Arithmetic](04-arithmetic.srp) | Integer operators and precedence | Sequence shown in [stdout](04-arithmetic.stdout) |
| [05 · Booleans](05-booleans.srp) | Comparisons, boolean logic and short-circuiting | `true`, `false`, `true`, `false` |

**Run any lesson:** `scarp run examples/01-basics/01-hello.srp` from this repository root, with the compiler executable on `PATH`. Or use its absolute path.

**Check it:** `scarp check examples/01-basics/01-hello.srp` (silent when successful).

**Exact output:** each lesson has a `.stdout` file next to the `.srp` file. These fixtures include line breaks and are checked automatically. Read the source, predict the output, run it, then compare the fixture.

**Note:** `bind` is not a mutable variable. `var` allows reassignment. `print` is the current compiler syntax; earlier prereleases used `println`.
