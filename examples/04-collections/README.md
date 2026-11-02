# 04 · Numeric collections and types

**Scope:** the current compiler offers specialised numeric vectors, integer collections and matrix/tile operations, **not** a general-purpose list/map/set library.

| Lesson | Learn | Expected behavior |
| --- | --- | --- |
| [01 · Vectors](01-vectors.srp) | Numeric vector literals, `len`, indexing and numeric operations | Printed vector values and computed aggregates |
| [02 · Vector windows](02-vector-windows.srp) | Selecting and combining numeric windows | `[20.0, 30.0]`, `[20.0, 30.0, 50.0]`, `[]` |
| [03 · Integer collections](03-integer-collections.srp) | Explicit `integers` values and integer window helpers | Printed windows, replacements and totals |
| [04 · Typed declarations](04-typed-declarations.srp) | Type annotations for vector/float/tile/boolean/string | `typed true 6.5` |
| [05 · Float smoothing](05-float-smoothing.srp) | Float-only weighted blending, default arguments and `needs` contracts | `smoothed 25.46875`, `balanced 12.0` |
| [06 · Tile windows](06-tile-windows.srp) | Windowed vector into a 2×2 `tile`, transpose/column, flatten and `matvec` | Matrix, `[1.0, 3.0]`, then a six-value vector |
| [07 · Numerical kernels](07-numerical-kernels.srp) | `variance`, `stddev`, `relu`, `sigmoid` and `tanh` on numeric data | `2.0 0.0` and three vectors |
| [08 · Vector probabilities](08-vector-probabilities.srp) | Explicit weight normalization, `softmax`, and probability checks | Two probability vectors, stable extreme-score results and `true` tests |

Run `scarp run examples/04-collections/01-vectors.srp` from this repository root or pass an absolute lesson path. Compare the exact `.stdout` beside each file.

**Exercise:** compare immutable `bind` with mutable `var` in the vector lesson. The original vector does not change when a new scaled value is assigned to another binding.

## Learn from the new lessons

**05 · Floating-point smoothing:** `blend` combines the current estimate and a new sample with a `weight` between 0 and 1. Four repeated updates bring 20.0 closer to 28.0; at equal weight, blending 10.0 and 14.0 produces 12.0. This is a simple arithmetic filter, **not** a sensor framework.

**06 · Tile windows:** A window excludes the sentinel values 99.0 and 88.0 before building a 2×2 matrix. `turn(matrix)` rearranges rows and columns, `lane(..., 0)` selects the first transposed row (original first column), `unroll` flattens the matrix, and `matvec` computes `[3.0, 7.0]`. Inspect the complete fixture to see the printed tile format.

**07 · Numerical kernels:** `variance` measures spread, while `stddev` returns 0.0 for identical inputs. `relu`, `sigmoid` and `tanh` transform each numerical input. The extreme values here demonstrate stable bounded output on this compiler, not a learned neural network.

**08 · Vector probabilities:** Normalizing [2, 3, 5] produces weights summing to approximately 1; `softmax` converts scores into a probability-like vector. **Floating-point output is not always a short decimal**: the exact second element is printed as `0.30000000000000004`. The examples test a tolerance rather than assuming exact sum equality. Extreme positive/negative scores test numerical stability.

**Try it:** before opening the fixtures, predict why the smoothing estimate rises toward 28.0; why the tile window excludes sentinel values; and why the softmax result for four identical scores is 0.25 at each index.
