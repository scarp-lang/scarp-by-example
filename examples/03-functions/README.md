# 03 · Functions

Learn the current compiler's typed function declaration syntax: `funcra`. Function parameters and return types are explicit. A `pure funcra` cannot perform effects such as output.

| Lesson | Demonstrates | Expected output |
| --- | --- | --- |
| [01 · Typed functions](01-typed-functions.srp) | Function calls, typed arguments/returns, forward calls, unit returns, pure functions | `35`, `Hello Scarp`, `6` on separate lines |
| [02 · Recursion](02-recursion.srp) | Recursive Fibonacci and mutually recursive even/odd tests | `55`, then `true false` |

Use `scarp run examples/03-functions/01-typed-functions.srp` from the repository root; use `scarp check PATH` to validate a lesson. Exact fixtures appear in matching `.stdout` files.

**Things to notice:** `funcra` is Scarp's implemented keyword, not an alias for Python/Rust `fn`. The recursion example includes a `needs` contract on non-negative inputs. Recursion is subject to compiler runtime limits.
