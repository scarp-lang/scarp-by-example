# Automated lesson validation

Run these commands from the `scarp-by-example` repository root:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/verify_examples.py --compiler /absolute/path/to/scarp
```

The Python 3 verifier uses only the standard library. It discovers all numbered `.srp` lessons (excluding `_support` source modules), rejects missing/orphaned `.stdout` files, invokes `scarp check` then `scarp run`, and compares the raw output bytes.

CI builds and runs the exact Scarp source commit identified in `.github/workflows/examples.yml`, on Linux, Windows and macOS. A passing upstream compiler test is an **input** to this project, not a substitute for passing this repository's own checks.

To upgrade compiler compatibility, update the workflow ref and `docs/compatibility.md` in one PR, run the full CI matrix, and review every output change.
