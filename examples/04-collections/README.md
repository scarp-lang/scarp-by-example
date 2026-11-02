# 04 · Numeric collections and types

**Scope:** the current compiler offers specialised numeric vectors, integer collections and matrix/tile operations, **not** a general-purpose list/map/set library.

| Lesson | Learn | Expected behavior |
| --- | --- | --- |
| [01 · Vectors](01-vectors.srp) | Numeric vector literals, `len`, indexing and numeric operations | Printed vector values and computed aggregates |
| [02 · Vector windows](02-vector-windows.srp) | Selecting and combining numeric windows | `[20.0, 30.0]`, `[20.0, 30.0, 50.0]`, `[]` |
| [03 · Integer collections](03-integer-collections.srp) | Explicit `integers` values and integer window helpers | Printed windows, replacements and totals |
| [04 · Typed declarations](04-typed-declarations.srp) | Type annotations for vector/float/tile/boolean/string | `typed true 6.5` |

Run `scarp run examples/04-collections/01-vectors.srp` from this repository root or pass an absolute lesson path. Compare the exact `.stdout` beside each file.

**Exercise:** compare immutable `bind` with mutable `var` in the vector lesson. The original vector does not change when a new scaled value is assigned to another binding.
