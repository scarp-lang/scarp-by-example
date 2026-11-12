# Scarp alpha.8: real projects and tests

**Compiler:** published [v0.0.6-alpha.8](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.8), exact source `37253e7805c0ca594560700dd1deb3928458e60d`.

This workshop is deliberately **separate from the numbered course**, whose independently verified compiler pin must not be silently changed. Run all commands with the **alpha.8 executable**. This directory is a real interpreter-backed Scarp project, not a screenshot, JavaScript emulator, package install or native compilation tutorial.

```text
alpha8-project-testing/
  scarp.project
  src/main.srp
  src/offset.srp
  tests/addition.srp
  tests/input.srp
  tests/input.stdin
  expected.stdout
```

Run these commands from the root of the `scarp-by-example` checkout:

```sh
scarp version
scarp verify tutorials/alpha8-project-testing
scarp run tutorials/alpha8-project-testing
scarp project info --json tutorials/alpha8-project-testing
scarp test --list tutorials/alpha8-project-testing
scarp test --require-tests tutorials/alpha8-project-testing
scarp test --json tutorials/alpha8-project-testing
scarp test --json --filter input tutorials/alpha8-project-testing
```

`scarp run` prints exactly `42` followed by one LF byte; the checked-in `expected.stdout` is authoritative. The test runner executes two ordinary `.srp` files. `addition.srp` uses `assert(...)`; `input.srp` receives the exact two-line contents of its sibling `input.stdin` (17 and 25). The assertions produce no program output. The JSON report describes test status rather than replaying the programs' output.

**Experiment safely on a local copy:** change `25` to `24` in `tests/input.stdin` and rerun `scarp test --json --filter input`. The input assertion should fail with diagnostic **E0065** and exit status 1. Keep the Git-tracked original fixture unchanged. `scarp test --list` performs read-only test discovery, not execution. `--require-tests` makes an empty suite fail in CI, whereas an empty suite succeeds by default.

`scarp.project` is Scarp's declarative v2 manifest format, **not TOML or JSON**. Its `dependencies {}` is deliberately empty; there is no dependency installer, registry, native `scarp compile` command, or stable package system here. Legacy `Scarp.project` projects continue to work with their own compatibility rules.

See the step-by-step [English guide](../../docs/alpha8-project-testing.md) and [हिन्दी गाइड](../../docs/hi/alpha8-project-testing.md). The [cross-platform workflow](../../.github/workflows/alpha8-project-testing.yml) builds only the exact published compiler source commit, then runs the [independent project verifier](../../scripts/verify_alpha8_project_testing.py), checking positive and negative test cases on Linux, Windows and macOS. It does not change the main course's compiler pin or release any software.

This miniature project is original course teaching material (MIT). The workflow behavior is checked against the official compiler's alpha.8 documentation and bundled calculator project.
