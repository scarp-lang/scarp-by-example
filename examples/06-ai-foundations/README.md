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
| [12 · Temperature softmax](12-temperature-softmax.srp) | Positive-temperature probability scaling and deterministic `topk` | `[0.5, 0.5]`, `[0.0]`, `[integer: 1, 2, 3]` |
| [13 · Cosine similarity](13-cosine-similarity.srp) | Compare finite vector directions independently of magnitude | `1.0`, `0.0`, `-1.0` |
| [14 · Cumulative sampled area](14-sample-cumulative-area.srp) | Calculate trapezoidal prefix areas from sampled velocity | `[0.0, 1.0, 9.0, 16.0]`, `16.0` |
| [15 · Top-K ranking](15-topk-ranking.srp) | Deterministic sorted original indices and scores, including ties and empty results | `[integer: 1, 2, 4]`, `[5.0, 5.0, 3.0]`, `[integer: 1, 2]`, `[integer:]` |
| [16 · Deterministic nucleus selection](16-nucleus-selection.srp) | Choose the smallest ranked probability prefix reaching a mass threshold | `[integer: 0, 1]`, `[0.5, 0.25]`, `[integer: 0, 1, 2]`, `[integer: 1, 2]` |

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

## Release-pinned numerical lessons

**12 · Temperature softmax:** `softmax_temp` and `logsoftmax_temp` transform finite scores with a positive temperature; `topk` selects deterministic original indices, not random samples. Available since published `v0.0.6-alpha.3`.

**13 · Cosine similarity:** `cosine_similarity` reports `1.0` for parallel vectors, `0.0` for perpendicular vectors, and `-1.0` for opposite directions. Published in `v0.0.6-alpha.4`.

**14 · Cumulative sampled area:** `sample_cumulative_area` evaluates trapezoidal prefix areas from measurements; the final prefix matches `sample_area` for this fixture. Published in `v0.0.6-alpha.4`. This is not symbolic integration.

All three `.srp` / `.stdout` pairs are copied unchanged from the compiler's immutable [v0.0.6-alpha.4 example fixtures](https://github.com/scarp-lang/scarp/tree/v0.0.6-alpha.4/examples). The compiler retains its regression copies. Read the [official scientific-kernels guide](https://scarp-lang.github.io/scarp-docs/language/scientific-kernels-alpha4.html) for the API contracts.

**15 · Deterministic Top-K:** `topk(scores, 3)` preserves original zero-based indices sorted by descending scores with lower indices winning equal-score ties. `topk_values` supplies their unchanged values. Ranking `softmax` probabilities retains the same tie order; `topk([], 0)` is a valid empty result. These are not stochastic sampling or text generation algorithms. Published in `v0.0.6-alpha.3` and unchanged in alpha.4.

## Published alpha.5 candidate ranking

**16 · Deterministic nucleus selection (Top-P):** `top_p(probabilities, 0.75)` returns the earliest descending-probability prefix reaching a specified positive mass, preserving original indices and deterministic tie order; `top_p_values` returns the selected probabilities. A threshold of exactly `1.0` retains all entries. The final example combines `softmax_temp` with `top_p`, but **never samples randomly** or produces text. The input must be normalized and the mass must be in `(0, 1]`. Introduced in published `v0.0.6-alpha.5`; source and stdout are copied byte-for-byte from that release.

**Practice:** Why does mass 0.75 select indices `[0, 1]` but mass 1.0 includes the last 0.25? Which tied index is selected first after temperature-controlled softmax?
