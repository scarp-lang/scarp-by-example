# 02 · Control flow

Conditions are booleans; a branch body has its own scope. Loops also support `break` and `continue`.

| Lesson | Learn | Expected behavior |
| --- | --- | --- |
| [01 · Decisions](01-decisions.srp) | `if`, `elif`, `else` and short-circuit guards | Chooses a grade and prints a branch message |
| [02 · While loops](02-while-loops.srp) | Counting, conditional skipping and early exit | Prints the accumulated sum |
| [03 · Repeat](03-repeat.srp) | `repeat N as index` with a fixed count | Prints `8` then `0` |

Run `scarp run examples/02-control-flow/01-decisions.srp` (change the file name for other lessons) from the repository root. Run `scarp check PATH` for a compiler check. Compare the output byte-for-byte to the matching `.stdout` file.

**Try it:** before running the while example, predict which indices contribute to the sum. Then locate the `continue` and `break` statements.
