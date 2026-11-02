# Compiler compatibility policy

This project is **not** a promise that all Scarp prereleases accept the same syntax.

- The compiler's latest publicly inspected `main` revision when this foundation was prepared was `e4db8e191cd7ea623123cae7348450ca6c95b170` (2026-11-02).
- The compiler `main` Cargo package identifies as `0.0.5-alpha.2`, which does **not** mean that prerelease has been published.
- The published release checked during preparation was `v0.0.5-alpha.1`.
- The [GitHub Actions workflow](../.github/workflows/examples.yml) pins a compiler commit instead of silently upgrading to a new interpreter on every run.
- Initial lessons are selected from the official compiler's own `examples/` fixtures, which are exercised by its `scripts/check.sh`. This provides an upstream CI baseline. The new repository's independent CI status must be checked separately.

If a lesson requires a newer compiler than you have installed, rebuild the tested commit; do not substitute obsolete syntax without noting the version. Run `scarp --version` and record your checkout SHA with `git rev-parse HEAD`.

The development interpreter currently supports primitive bindings, comparisons, control flow, typed functions, numeric vectors, matrices and explicit source imports. Do not advertise general-purpose maps/sets, structured error handling, async/await, scheduling, sockets, HTTP, agent systems or autograd as implemented merely because the project has plans for them.

### Compiler upgrade process

1. Open a PR changing the pinned commit in `.github/workflows/examples.yml`.
2. Run the entire example suite and investigate differences; update expected output only when the language behavior intentionally changed.
3. Update this document with the new commit and any new incompatibilities.
4. Merge only when workflow checks succeed.
