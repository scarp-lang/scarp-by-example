# Contributing to Scarp by Example

Thank you for helping people learn Scarp.

## Before adding a lesson

1. Consult the [Scarp compiler](https://github.com/scarp-lang/scarp), [syntax documentation](https://github.com/scarp-lang/scarp/tree/main/docs), [CLI quickstart](docs/cli-quickstart.md) and [compatibility policy](docs/compatibility.md).
2. Verify the proposed syntax exists in the compiler source checkout used by CI. Do not infer implementation from roadmaps or discussion alone.
3. Add an explicitly numbered `.srp` lesson and an adjacent `.stdout` with its **exact UTF-8 stdout**. Avoid unstable time, randomness, network requests, host-specific paths and inputs.
4. Explain what learners should notice in the section README; keep examples small and focused. Make explanations understandable to newcomers.
5. Run `python3 scripts/verify_examples.py --compiler /path/to/scarp`, and include the compiler commit tested in the PR.
6. Open a focused pull request. Avoid version bumps, tags or publishing a stable release.

If the feature is unavailable, propose an issue or update [the roadmap](docs/roadmap.md). **Do not publish a hypothetical `.srp` file as runnable.**

## File structure

- `examples/NN-topic/NN-name.srp`: self-contained runnable lesson
- `examples/NN-topic/NN-name.stdout`: exact expected stdout, including trailing newline
- `examples/NN-topic/README.md`: lesson explanations, run instructions, expected behavior
- `examples/NN-topic/_support/`: imported source modules; not standalone lessons
- `docs/translations/`: translation policy and, later, locale-specific explanations

Use UTF-8 and LF line endings for text fixtures. Paths should be lowercase and hyphenated. Never modify stdout fixtures just to hide runtime regressions: investigate the compiler behavior and document intentional changes.

## Code reviews and scope

Keep one concept per lesson and avoid external dependencies. Include the origin of copied code and license information in your PR. For compiler bugs, report findings in the [compiler repository](https://github.com/scarp-lang/scarp/issues). Be respectful and constructive; see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
