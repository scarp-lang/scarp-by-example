# 02 · Control flow

Conditions are booleans; a branch body has its own scope. Loops also support `break` and `continue`.

| Lesson | Learn | Expected behavior |
| --- | --- | --- |
| [01 · Decisions](01-decisions.srp) | `if`, `elif`, `else` and short-circuit guards | Chooses a grade and prints a branch message |
| [02 · While loops](02-while-loops.srp) | Counting, conditional skipping and early exit | Prints the accumulated sum |
| [03 · Repeat](03-repeat.srp) | `repeat N as index` with a fixed count | Prints `8` then `0` |
| [04 · Nested repeat](04-nested-repeat.srp) | Nested repeat loops, inner `continue`, and counters | Prints `9 3 24` |
| [05 · While sum](05-while-sum.srp) | Inclusive `<=` boundary, accumulate 1 through 10, advance the counter | Prints `55`, then final counter `11` |
| [06 · While countdown](06-while-countdown.srp) | A descending counter with `>=` and `-=` | Prints 5 through 0, one per line |
| [07 · While product](07-while-product.srp) | Multiplication accumulator initialized to 1 | Prints `120`, then final factor `6` |

Run `scarp exec examples/02-control-flow/01-decisions.srp` (change the file name for other lessons) from the repository root. Run `scarp verify PATH` for silent static validation. Compare the output byte-for-byte to the matching `.stdout` file.

**Try it:** first trace lessons 05–07 by hand: write down the counter and accumulator after each iteration. For `<=` with an increasing counter, 10 is included and the counter exits at 11. For `>=` with a decreasing counter, 1 is included and the counter exits at 0. Then revisit lesson 02 to predict which indices contribute to its sum and locate `continue` and `break`. For the nested repeat, count all 12 row/column pairs, then remove the three equal-coordinate pairs before computing the remaining sum.
