# Automated lesson validation

Run these commands from the `scarp-by-example` repository root:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp
python3 scripts/verify_cli.py --compiler /absolute/path/to/scarp
```

The Python 3 verifier uses only the standard library. It discovers all numbered `.srp` lessons (excluding `_support` source modules), rejects missing/orphaned `.stdout` files, invokes static `scarp verify` then `scarp exec`, and compares the raw output bytes. The independent CLI smoke test verifies legacy `run` equivalence on selected lessons and demonstrates that `check` can execute runtime expressions, unlike `verify`.

The `test_lesson_notes.py` tests enforce 50 exact Hindi/source/fixture matches and HTML-safe rendering. The website generator embeds the notes and rejects missing explanations, so no page can silently show an unrelated translation.

CI builds and runs the exact Scarp source commit identified in `.github/workflows/examples.yml`, on Linux, Windows and macOS. A passing upstream compiler test is an **input** to this project, not a substitute for passing this repository's own checks.

To upgrade compiler compatibility, update both workflow refs and `docs/compiler-target.json` in one PR, run the full CI matrix and CLI smoke test, and review every output change. See the [CLI guide](../docs/cli-quickstart.md).
