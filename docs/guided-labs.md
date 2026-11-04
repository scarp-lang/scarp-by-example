# Guided Scarp coding labs / चरण-दर-चरण Scarp अभ्यास

These six exercises are **separate from the 50 runnable reference lessons**. Each lab
has a compiler-verified starter program, a compiler-verified reference solution,
and a byte-exact `solution.stdout` fixture. Every starter must compile successfully
but produce **different** output from its solution. No browser Scarp interpreter
or automated judging service is provided.

## Start a lab

1. Open the [online lab index](https://scarp-lang.github.io/scarp-by-example/labs/) and select a chapter.
2. Read the challenge in English or हिन्दी and inspect `labs/NN-topic/starter.srp`.
3. In your local checkout, copy `starter.srp` to **`attempt.srp` in that same lab folder**.
4. Change `attempt.srp` to achieve the output shown in `solution.stdout`.
5. Verify and execute with the published **Scarp v0.0.5-alpha.4** CLI:

```text
scarp verify labs/01-basics/attempt.srp
scarp exec labs/01-basics/attempt.srp
```

Replace `01-basics` with the lab chapter. The compiler executable must be on
your PATH, or invoke it by its actual absolute executable path.
Use the exact pinned compiler source commit
`79141329176f5dce51457e90a6652902f6432135` when building from source;
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

The goal is to **learn the published compiler's behavior**, not to claim that
unreleased AI, general concurrency, networking or framework features exist.
Never modify output fixtures to hide a compiler mismatch. Contributors should
include a real source-backed task, both translations, tested starter/solution
and a valid fixture. Keep unfinished ideas in the roadmap rather than on live pages.
