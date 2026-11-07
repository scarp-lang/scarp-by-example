# Guided Scarp coding labs / चरण-दर-चरण Scarp अभ्यास

These six exercises are **separate from the 52 runnable reference lessons**. Each lab
has a compiler-verified starter program, a compiler-verified reference solution,
and a byte-exact `solution.stdout` fixture. Every starter must compile successfully
but produce **different** output from its solution. No browser Scarp interpreter
or automated judging service is provided. The control-flow and AI-foundations labs each offer an optional stretch challenge with separate source-backed starter, exact fixture and tested solution; the number of core labs remains six.

For a guided order of study, start from the [Basics chapter learning path](https://scarp-lang.github.io/scarp-by-example/chapters/01-basics/#chapter-path): first read source-backed lessons, then practice three English/Hindi self-checks, and finally open the chapter's coding lab. All six chapter pages offer this sequence. Your optional saved lesson completion count is separate from quiz results and any attempts you run in the compiler.

## Start a lab

1. Open the [online lab index](https://scarp-lang.github.io/scarp-by-example/labs/) and select a chapter.
2. Read the challenge in English or हिन्दी and inspect `labs/NN-topic/starter.srp`.
3. In your local checkout, copy `starter.srp` to **`attempt.srp` in that same lab folder**.
4. Change `attempt.srp` to achieve the output shown in `solution.stdout`.
5. Verify and execute with the published **Scarp v0.0.6-alpha.3** CLI:

```text
scarp verify labs/01-basics/attempt.srp
scarp exec labs/01-basics/attempt.srp
```

Replace `01-basics` with the lab chapter. The compiler executable must be on
your PATH, or invoke it by its actual absolute executable path.
Use the exact pinned compiler source commit
`ceff07d9014f466974e0c9e02fc5d23573f55777` when building from source;
see the [CLI quickstart](cli-quickstart.md).

**Important for module imports:** the `05-modules` starter imports
`_support/values.srp`. Keep your `attempt.srp` in the **same lab folder** and
keep the support directory intact. Avoid moving just the source file.

## What the verifier checks

The CI command

```text
python scripts/verify_guided_labs.py --compiler /path/to/scarp
```

requires all of the following before a lab can be published:

- Exactly one bilingual lab per existing chapter, with all starter and solution files.
- Valid UTF-8 starter and solution source and a byte-exact UTF-8, LF-only output fixture.
- The real compiler's **silent static `verify`** passes for both starter and solution.
- The real compiler **executes the starter successfully**, but its stdout does
  **not** already equal the target output.
- The real compiler executes each solution with stdout exactly matching `solution.stdout`.
- Every advertised optional stretch has separate UTF-8 `stretch-starter.srp`, `stretch-solution.srp` and byte-exact `stretch-solution.stdout` files; it must independently pass the same verify/exec checks and never arrive already solved.
- Linux, macOS and Windows workflows pass against the same pinned published compiler.

Checkpoints and labs serve different purposes: multiple-choice checkpoints
help learners reason about the provided code, while labs require editing
real `.srp` source and comparing actual CLI output.

## Current exercises

| Chapter | Goal | Expected output |
| --- | --- | --- |
| 01 · Basics | Rectangle area | `42` |
| 02 · Control flow | Sum repeat indices | `10` |
| 03 · Functions | Repair square(6) | `36` |
| 04 · Collections | Compute vector mean | `2.5` |
| 05 · Modules | Double imported public value | `42` |
| 06 · AI foundations | One-hot highest score | `[0.0, 1.0, 0.0]` |

## Optional stretch challenge · अतिरिक्त अभ्यास

The [control-flow lab](https://scarp-lang.github.io/scarp-by-example/labs/02-control-flow/#stretch-challenge) includes a second, independent task: scan `[integer: 5, 8, 13, 8, 21]` and stop at the first number **strictly greater than 10**. Print the zero-based index and how many values you inspected. The compiler-verified output is `2 3` followed by a newline. The starter incorrectly checks for values greater than 20, so it inspects too many items before stopping. Practice by copying `labs/02-control-flow/stretch-starter.srp` to `labs/02-control-flow/stretch-attempt.srp` and running:

```text
scarp verify labs/02-control-flow/stretch-attempt.srp
scarp exec labs/02-control-flow/stretch-attempt.srp
```

The stretch variant has its own hint, bilingual explanation and reference solution, but is not counted as a seventh chapter or core lab. As with core tasks, the website does not execute, collect or grade attempts.

The [AI-foundations optional stretch](https://scarp-lang.github.io/scarp-by-example/labs/06-ai-foundations/#stretch-challenge) demonstrates the **alpha.3** `softmax_temp`, `logsoftmax_temp` and `topk` built-ins. The starter prints only equal-score probabilities. Extend it to display the single-score log probability and the highest three original indices from logits `[1.0, 4.0, 4.0, 2.0]` at temperature 0.5. The exact expected output is:

```text
[0.5, 0.5]
[0.0]
[integer: 1, 2, 3]
```

Copy `labs/06-ai-foundations/stretch-starter.srp` to `stretch-attempt.srp` in the same directory, then run `scarp verify` and `scarp exec` as above. The reference source and fixture match the compiler's published `examples/temperature_softmax.*` and must pass independent course CI verification. This is deterministic score ranking, not random sampling.

The goal is to **learn the published compiler's behavior**, not to claim that
unreleased AI, general concurrency, networking or framework features exist.
Never modify output fixtures to hide a compiler mismatch. Contributors should
include a real source-backed task, both translations, tested starter/solution
and a valid fixture. Keep unfinished ideas in the roadmap rather than on live pages.
