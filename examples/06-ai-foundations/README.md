# 06 · Foundations for AI-oriented programs

Scarp has early numerical primitives useful for AI-related calculations. **These exercises do not claim full AI frameworks, autodiff, GPU acceleration, model training systems or agent tooling.**

| Lesson | Demonstrates | Expected output |
| --- | --- | --- |
| [01 · Matrix inference](01-matrix-inference.srp) | Matrix/tile construction and matrix-vector multiplication | `[4.0, 1.0]` |
| [02 · Classification gradient](02-classification-gradient.srp) | One-hot target and **explicit** categorical-loss gradient | `[0.0, 1.0, 0.0]`, `[0.5, -0.5]`, `0.0` |
| [03 · Classification loss](03-classification-loss.srp) | Scalar categorical loss and selecting maximum score index | `0.0`, `-0.0`, `1` |

Use `scarp run examples/06-ai-foundations/01-matrix-inference.srp` from the repository root. `scarp check PATH` validates source, and the adjacent `.stdout` defines the exact output.

**Important:** computed gradients are explicit compiler functions; these examples do **not** imply an automatic differentiation engine or a production-grade model deployment stack. Avoid drawing conclusions about real-world model quality from toy numeric inputs.
