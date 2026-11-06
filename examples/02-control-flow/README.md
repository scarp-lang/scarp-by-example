# 02 · Control flow

Conditions are booleans; a branch body has its own scope. Loops also support `break` and `continue`.

| Lesson | Learn | Expected behavior |
| --- | --- | --- |
| [01 · Decisions](01-decisions.srp) | `if`, `elif`, `else` and short-circuit guards | Chooses a grade and prints a branch message |
| [02 · While loops](02-while-loops.srp) | Counting, conditional skipping and early exit | Prints the accumulated sum |
| [03 · Repeat](03-repeat.srp) | `repeat N as index` with a fixed count | Prints `8` then `0` |
| [04 · Nested repeat](04-nested-repeat.srp) | Nested repeat loops, inner `continue`, and counters | Prints `9 3 24` |

Run `scarp exec examples/02-control-flow/01-decisions.srp` (change the file name for other lessons) from the repository root. Run `scarp verify PATH` for silent static validation. Compare the output byte-for-byte to the matching `.stdout` file.

**Try it:** before running the while example, predict which indices contribute to the sum. Then locate the `continue` and `break` statements. For the nested repeat, count all 12 row/column pairs, then remove the three equal-coordinate pairs before computing the remaining sum.
