# 05 · Modules and explicit imports

Modules let a lesson separate a public API from implementation details.

| Lesson | Demonstrates | Expected output |
| --- | --- | --- |
| [01 · Modular inference](01-modular-inference.srp) | `import "...srp" as name`, exported bindings, public pure function | `Modular inference`, `[4.0, 1.0]`, `0 [1.0, 0.0]` |
| [02 · Constant expressions](02-constant-expressions.srp) | Exported constants, chained imports and a function's default argument | `constant expressions 42 84 true 0.75 42` |

The lesson imports [linear.srp](_support/linear.srp), which itself imports [settings.srp](_support/settings.srp). These two files are **support modules**, not separate runnable lessons. The source is taken from the upstream compiler's `module_demo.srp`; only its import path was changed from `modules/` to `_support/` to match this course layout.

From the repository root: `scarp run examples/05-modules/01-modular-inference.srp`.

**Notice:** `pub` exposes declarations; `pure funcra` defines a pure function. Keep the `_support/` directory next to the entry point; imports are resolved relative to their importing files.

**New lesson:** [02 · Constant expressions](02-constant-expressions.srp) imports `_support/constants.srp`, which imports `_support/constant_base.srp`. The modules demonstrate source-relative paths and public constants; constants are not runtime-mutable shared globals. Keep both helpers in `_support` when copying the lesson.
