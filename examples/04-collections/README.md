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
| [09 · Vector norm](09-vector-norm.srp) | `norm` length and immutable `normalize` for a 3-4 vector | `5.0`, then `[0.6, 0.8]` |
| [10 · Float refinement](10-float-refinement.srp) | Newton-style square-root refinement, bounded steps, typed contracts | `sqrt2 checked true`, then `sqrt9 3.0` |
| [11 · Vector allocation](11-vector-allocation.srp) | `fill`, `len` and `sum` on a three-element numerical vector | `3.0 3` |
| [12 · Root mean square](12-root-mean-square.srp) | Stable `rms` on signals and visible vector windows | `balanced 2.0`, `window 2.5`, `finite true`, `zero 0.0` |
| [13 · Sampled calculus](13-sampled-calculus.srp) | Bounded trapezoidal area and interval secant slopes | `9.0`, `[2.0, 2.0]` |
| [14 · Pearson correlation](14-pearson-correlation.srp) | Centered linear association of paired numerical data | `1.0`, `-1.0`, `0.0` |

Run `scarp run examples/04-collections/01-vectors.srp` from this repository root or pass an absolute lesson path. Compare the exact `.stdout` beside each file.

**Exercise:** compare immutable `bind` with mutable `var` in the vector lesson. The original vector does not change when a new scaled value is assigned to another binding.

## Learn from the new lessons

**05 · Floating-point smoothing:** `blend` combines the current estimate and a new sample with a `weight` between 0 and 1. Four repeated updates bring 20.0 closer to 28.0; at equal weight, blending 10.0 and 14.0 produces 12.0. This is a simple arithmetic filter, **not** a sensor framework.

**06 · Tile windows:** A window excludes the sentinel values 99.0 and 88.0 before building a 2×2 matrix. `turn(matrix)` rearranges rows and columns, `lane(..., 0)` selects the first transposed row (original first column), `unroll` flattens the matrix, and `matvec` computes `[3.0, 7.0]`. Inspect the complete fixture to see the printed tile format.

**07 · Numerical kernels:** `variance` measures spread, while `stddev` returns 0.0 for identical inputs. `relu`, `sigmoid` and `tanh` transform each numerical input. The extreme values here demonstrate stable bounded output on this compiler, not a learned neural network.

**08 · Vector probabilities:** Normalizing [2, 3, 5] produces weights summing to approximately 1; `softmax` converts scores into a probability-like vector. **Floating-point output is not always a short decimal**: the exact second element is printed as `0.30000000000000004`. The examples test a tolerance rather than assuming exact sum equality. Extreme positive/negative scores test numerical stability.

**Try it:** before opening the fixtures, predict why the smoothing estimate rises toward 28.0; why the tile window excludes sentinel values; and why the softmax result for four identical scores is 0.25 at each index.

## Norms, refinement and allocation

**09 · Vector norm:** `norm([3.0, 4.0])` returns the Euclidean length 5.0. `normalize` produces the new unit-length vector `[0.6, 0.8]` without mutating the original binding. Check by computing `3 / 5` and `4 / 5` on paper.

**10 · Float refinement:** `pure funcra root` estimates a positive number's square root using a fixed number of Newton updates and typed parameters. The `needs` preconditions require a positive input and nonnegative step count; `ensures` requires a positive result. The lesson **checks** a tolerance for √2 rather than asserting an exact irrational number, and obtains 3.0 for √9. This is a numerical demonstration, not a general floating-point math library.

**11 · Vector creation:** `fill(1.0, 3)` generates three floating-point values. `sum` gives 3.0 and `len` gives 3. An upstream source comment discusses its payload-byte representation, but that detail is not asserted as a cross-platform memory API by this course.

**Practice:** Which input to `normalize` has length five? How many Newton update steps are used by default? Why should `len(numbers)` be 3?

## Root mean square (published compiler alpha.6)

**12 · Stable RMS:** `rms(samples)` computes the root mean square of a nonempty finite vector. Four samples `[2.0, -2.0, 2.0, -2.0]` give RMS 2.0. Selecting `[3.0, 4.0, 0.0, 0.0]` through `window` gives RMS 2.5. The compiler uses scaling so the tested large finite values remain finite without squaring them directly. An empty vector is a runtime error. This requires Scarp v0.0.6-alpha.1; the operation neither modifies the input nor trains a model.

**Practice:** Square the four window values, add, divide by four, and take the square root. Why is the result different from `norm`?

## Published alpha.4 sampled calculus

**13 · Sampled calculus:** `sample_area(time, velocity)` applies the composite trapezoidal rule to irregular samples, giving `9.0`; `sample_slopes` reports a finite secant slope per interval, `[2.0, 2.0]`. The coordinate vector must be strictly increasing, and these functions do not implement symbolic integration or differentiation. Published in `v0.0.6-alpha.4`; the `.srp` and `.stdout` were copied unchanged from the tagged compiler fixtures.

**Practice:** Compute the area of the intervals `[0, 1]` and `[1, 3]` separately, then add them. Why do both secant slopes equal `2.0` even though their time intervals differ?

## Published alpha.5: Pearson correlation

**14 · Pearson correlation:** `pearson_correlation(left, right)` measures centered linear association. Increasing values correlate at `1.0`, reversing a series produces `-1.0`, and the balanced nonlinear fixture produces `0.0`. Both vectors must have the same length (at least two), finite values and nonzero variance. Correlation neither demonstrates causation nor statistical significance.

**Practice:** Center each sample around its mean. Why does reversing the second series make the correlation negative?
