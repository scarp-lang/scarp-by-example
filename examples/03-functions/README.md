# 03 · Functions

Learn the current compiler's typed function declaration syntax: `funcra`. Function parameters and return types are explicit. A `pure funcra` cannot perform effects such as output.

| Lesson | Demonstrates | Expected output |
| --- | --- | --- |
| [01 · Typed functions](01-typed-functions.srp) | Function calls, typed arguments/returns, forward calls, unit returns, pure functions | `35`, `Hello Scarp`, `6` on separate lines |
| [02 · Recursion](02-recursion.srp) | Recursive Fibonacci and mutually recursive even/odd tests | `55`, then `true false` |
| [03 · Function contracts](03-function-contracts.srp) | Default and named arguments, `needs` and `ensures` contracts | `10`, `3`, `12 12` |
| [04 · Terminal recursion](04-terminal-recursion.srp) | A direct self-return with an accumulator, default argument, and `needs` contract | `128` |

Use `scarp run examples/03-functions/01-typed-functions.srp` from the repository root; use `scarp check PATH` to validate a lesson. Exact fixtures appear in matching `.stdout` files.

**Things to notice:** `funcra` is Scarp's implemented keyword, not an alias for Python/Rust `fn`. The recursion example includes a `needs` contract on non-negative inputs. Recursion is subject to compiler runtime limits.

**New lesson:** [03 · Function contracts](03-function-contracts.srp) demonstrates caller-defined defaults and named arguments. The `needs` condition checks a precondition; `ensures` states a result property. Explore the example with its deliberately valid calls before writing an invalid call in a separate local file.

**04 · Terminal recursion:** `count(n, total)` returns a direct call to itself until `n` reaches zero; `total` accumulates the count. The compiler's upstream example notes that this form **can** reuse an execution frame, but this lesson makes no claim that every recursive call is optimized or that arbitrary recursion is unbounded. Predict why `count(128)` prints `128`.
