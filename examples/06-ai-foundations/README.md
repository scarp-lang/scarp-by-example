# 06 · Foundations for AI-oriented programs

Scarp has early numerical primitives useful for AI-related calculations. **These exercises do not claim full AI frameworks, autodiff, GPU acceleration, model training systems or agent tooling.**

| Lesson | Demonstrates | Expected output |
| --- | --- | --- |
| [01 · Matrix inference](01-matrix-inference.srp) | Matrix/tile construction and matrix-vector multiplication | `[4.0, 1.0]` |
| [02 · Classification gradient](02-classification-gradient.srp) | One-hot target and **explicit** categorical-loss gradient | `[0.0, 1.0, 0.0]`, `[0.5, -0.5]`, `0.0` |
| [03 · Classification loss](03-classification-loss.srp) | Scalar categorical loss and selecting maximum score index | `0.0`, `-0.0`, `1` |
| [04 · Score selection](04-score-selection.srp) | Deterministic `argmax`/`argmin` and extremum values | `1 3.0`, then `0 1.0` |
| [05 · Matrix targets](05-matrix-targets.srp) | `tile`, matrix-vector scores, `argmax` and `onehot` | `[1.0, 0.0, 0.0]` |
| [06 · Matrix forward pass](06-matrix-forward.srp) | Typed `tile` input, `tileadd`, `tilescale`, `matvec`, bias, `softmax` and contracts | `[0.5, 0.5]` |
| [07 · Log-space scores](07-log-space.srp) | `logsumexp` and `logsoftmax` without exponential overflow | `0.0`, then `[0.0, -1000.0]` |
| [08 · Explicit coefficient fitting](08-coefficient-fit.srp) | User-written squared-error loss and gradient steps on small vectors | `true`, `true` for coefficient and loss tolerance tests |
| [09 · Linear transforms](09-linear-transform.srp) | `matmul` composition of a 2×3 and a 3×2 tile | `tile(2x2)[[58.0, 64.0], [139.0, 154.0]]` |
| [10 · Class score ties](10-class-score-ties.srp) | `matvec`, `argmax` first-match behavior and `maxval` | `[2.0, 2.0, -1.0] 0 2.0` |
| [11 · Matrix probabilities](11-matrix-probabilities.srp) | Equal-score `softmax` and categorical-loss tolerance check | `[0.5, 0.5]`, then `true` |

Use `scarp run examples/06-ai-foundations/01-matrix-inference.srp` from the repository root. `scarp check PATH` validates source, and the adjacent `.stdout` defines the exact output.

**Important:** computed gradients are explicit compiler functions; these examples do **not** imply an automatic differentiation engine or a production-grade model deployment stack. Avoid drawing conclusions about real-world model quality from toy numeric inputs.

**New lesson:** [04 · Score selection](04-score-selection.srp) compares scores where the maximum appears twice. The example demonstrates the first-match tie behavior of the current `argmax` implementation; it does **not** train or load a model.

## More numerical AI foundations

**05 · Matrix targets:** Multiply a 3×2 `tile` by a two-element vector, choose the greatest score with `argmax`, then form the corresponding `onehot` vector. The output `[1.0, 0.0, 0.0]` represents an index, not a prediction from a trained model.

**06 · A small forward pass:** A `pure funcra forward` adds a numeric bias vector to `matvec` scores and normalizes them with `softmax`. `tileadd` and `tilescale` construct its simple weights. The `needs` and `ensures` clauses check dimensions, while equal scores produce `[0.5, 0.5]`. No gradients or learned weights are implied.

**07 · Log space:** `logsumexp` and `logsoftmax` operate directly on log scores. Their printed output for `[0.0, -1000.0]` illustrates numerical stability when naive exponential calculations could underflow. It does not implement a general ML training framework.

**08 · Explicit coefficient fitting:** The program models `y = coefficient * x` with three toy samples and repeats 40 hand-written gradient steps to reduce the mean-squared error. It tests that the fitted coefficient is close to 2.0 and the error is tiny; the two printed `true` lines indicate those threshold conditions, **not** a universal optimizer, automatic differentiation system, or production training API.

**Try it:** compute the `matvec` scores in lesson 05 on paper; explain why equal class scores yield 0.5 in lesson 06; compare `logsoftmax` with `softmax` conceptually; and identify the lines in lesson 08 where the gradient is **manually computed**.

## Composition, ties and probability checks

**09 · Rectangular matrix composition:** `matmul` composes a 2×3 numeric `tile` and a 3×2 tile into a 2×2 result. The printed first row is `[58.0, 64.0]`; calculate 1×7 + 2×9 + 3×11 to verify 58.0. This shows a matrix primitive, not a general linear-algebra framework.

**10 · Equal class scores:** `matvec` produces `[2.0, 2.0, -1.0]`. `argmax(scores)` returns **index 0**, because equal maximum values select the first occurrence in the pinned compiler; `maxval(scores)` returns 2.0. An index is not a probability or a model confidence score.

**11 · Numerical probabilities:** Applying the identity `tile` to `[0.0, 0.0]` produces equal class scores; `softmax` outputs `[0.5, 0.5]`. `crossentropy(scores, 1)` is checked against 0.6931–0.6932, so the printed `true` demonstrates a numerical tolerance comparison rather than exact floating-point equality. No model training or autograd is involved.

**Practice:** Why does the rectangular product have shape 2×2? Which index wins a tie for first place? Why does the two-class loss test use a range?
