# Learning roadmap and feature gates

This page separates course design from compiler implementation. A planned lesson is **not** an executable feature.

| Learning area | Course position | Publication gate |
| --- | --- | --- |
| Output, bindings, arithmetic, booleans | Basics | Working compiler fixtures and passing CI |
| `if`/`elif`/`else`, while, repeat | Control flow | Working compiler fixtures and passing CI |
| Typed functions and recursion | Functions | Working compiler fixtures and passing CI |
| Numeric vectors, windows, matrices | Collections / AI foundations | Working compiler fixtures and passing CI |
| Source modules and imports | Modules | Working compiler fixtures and passing CI |
| Generic lists, maps, sets, records | Future | Compiler implements and tests the complete construct |
| Structured errors and propagation | Future | Compiler ships a tested public syntax and runtime semantics |
| Async, concurrency, networking | Future | Tested runtime APIs and deterministic, safe demonstrations |
| Agents, inference tooling and model training | Future | Explicitly implemented APIs, repeatable local tests and honest limitations |

## Website

An interactive learning site is a future enhancement. Source lessons and CI are authoritative. A site must derive published examples from verified files, preserve locale parity, and avoid exposing planned syntax as executable.

See [feature matrix](https://github.com/scarp-lang/scarp/blob/main/docs/development/feature-matrix.md) for upstream implementation status.
