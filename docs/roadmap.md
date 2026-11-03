# Learning roadmap and feature gates

This page separates course design from compiler implementation. A planned lesson is **not** an executable feature.

| Learning area | Course position | Publication gate |
| --- | --- | --- |
| Output, bindings, arithmetic, booleans | Basics | Working compiler fixtures and passing CI |
| `if`/`elif`/`else`, while, repeat | Control flow | Working compiler fixtures and passing CI |
| Typed functions and recursion | Functions | Working compiler fixtures and passing CI |
| Numeric vectors, windows, matrices | Collections / AI foundations | Working compiler fixtures and passing CI |
| Source modules and imports | Modules | Working compiler fixtures and passing CI |
| Unicode text construction, slicing and repetition | Basics | Published alpha.3 implementation and passing exact-output CI |
| Generic lists, maps, sets, records | Future | Compiler implements and tests the complete construct |
| Structured errors and propagation | Future | Compiler ships a tested public syntax and runtime semantics |
| Async, concurrency, networking | Future | Tested runtime APIs and deterministic, safe demonstrations |
| Agents, inference tooling and model training | Future | Explicitly implemented APIs, repeatable local tests and honest limitations |

## Developer CLI

The pinned prerelease CLI is taught in separate [English](cli-quickstart.md) and [Hindi](hi/cli-quickstart.md) guides, backed by real-command smoke tests. Inspection metadata is **not** treated as a runnable `.srp` lesson; native compilation, an LSP and package tools remain outside the current verified feature set.

## Website

The [static, searchable learning catalog](https://scarp-lang.github.io/scarp-by-example/) is deployed using GitHub Actions after validating all runnable examples with the pinned compiler. Source lessons and CI remain authoritative. Browser-based Scarp execution and richer interactivity are future enhancements; English/Hindi companion guides already cover every published lesson, and the catalog must not present unimplemented syntax as runnable.

See [feature matrix](https://github.com/scarp-lang/scarp/blob/main/docs/development/feature-matrix.md) for upstream implementation status.
