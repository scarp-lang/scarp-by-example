# Scarp alpha.8 project testing: from zero to a verified test suite

**Prerequisite:** the published Scarp `v0.0.6-alpha.8` executable, source `37253e7805c0ca594560700dd1deb3928458e60d`. Earlier prereleases do not provide this complete project testing workflow. [हिन्दी में पढ़ें](hi/alpha8-project-testing.md).

## 1. Project structure and declarative manifest

Open [the complete runnable workshop](../tutorials/alpha8-project-testing/README.md). The `scarp.project` file tells the compiler where the application starts:

```text
project "alpha8-test-workshop" {
    version: "0.1.0"
    entry: "src/main.srp"
    type: "application"
    dependencies {}
}
```

The format is Scarp's own restricted declarative syntax; `dependencies {}` is a reserved empty block, **not** an active package manager. For a fresh project, `scarp init new-project` creates a new directory; it will refuse to overwrite one that already exists.

## 2. Keep the application and test code separate

The reusable [`src/offset.srp`](../tutorials/alpha8-project-testing/src/offset.srp) module defines one exported pure function. [`src/main.srp`](../tutorials/alpha8-project-testing/src/main.srp) imports it and prints 42. Run:

```sh
scarp verify tutorials/alpha8-project-testing
scarp run tutorials/alpha8-project-testing
```

`verify` checks syntax, imports and types without executing application statements. `run` executes the interpreter-backed entrypoint. Compare its output byte-for-byte with [`expected.stdout`](../tutorials/alpha8-project-testing/expected.stdout), including the final newline.

## 3. Write executable assertions

[`tests/addition.srp`](../tutorials/alpha8-project-testing/tests/addition.srp) imports the same module and checks both a positive and a negative input. The syntax `assert(condition, "optional message");` checks a Boolean **at runtime**, and a false condition causes diagnostic **E0065**. `assert` is a statement rather than an `assert_eq` library function, and it does not print a passing message.

```sh
scarp test --list tutorials/alpha8-project-testing
scarp test --require-tests tutorials/alpha8-project-testing
scarp test --json tutorials/alpha8-project-testing
```

The runner sorts only immediate `tests/*.srp` files, executes them individually and captures their output. Listing does **not** execute test code. Structured `--json` reports use schema version 1. `--require-tests` rejects accidentally empty suites, including on CI.

## 4. Give each test its own input

[`tests/input.srp`](../tutorials/alpha8-project-testing/tests/input.srp) calls `read_line()` twice, converts the text with `text_to_integer`, and asserts a sum of 42. Its sibling [`tests/input.stdin`](../tutorials/alpha8-project-testing/tests/input.stdin) contains exactly two LF-terminated lines: `17` and `25`.

```sh
scarp test --json --filter input tutorials/alpha8-project-testing
```

The `--filter` value is a literal, case-sensitive filename substring, not a regular expression. The runner does not inherit your terminal's stdin. Change the fixture in a local copy to `17` and `24` to see E0065; do not alter the canonical checked-in test inputs. `--list` does not read the fixture bytes.

## 5. Validate the actual compiler, not only a web preview

After building the pinned source or installing the matching verified binary, run:

```sh
python scripts/verify_alpha8_project_testing.py --compiler /absolute/path/to/scarp
```

Use the absolute path to `scarp.exe` on Windows. The verifier checks exact entrypoint output, project metadata, JSON test counts/order, filtering, and several negative tests in disposable temporary directories. CI also verifies that the compiler checkout's **HEAD equals the published source SHA**.

**Boundaries:** This is an interpreter and project-testing tutorial. It does not demonstrate native executable compilation, dependencies, a formatter, a package registry, concurrent test execution or AI training. The existing main course is intentionally pinned to a different compiler release.
