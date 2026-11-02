# Lesson-writing standard

Each runnable lesson needs:
- A short descriptive `.srp` filename with a two-digit numbered prefix (e.g. `01-example.srp`). Lesson numbers in each chapter must start at `01`, be unique, and contain no gaps.
- A matching `.stdout` file with byte-exact printed output (UTF-8 and LF line endings; include trailing newline only if emitted). Intentional interior carriage-return bytes are allowed, but CRLF line endings are not.
- A section README entry that explains the concept and links to the files.
- A known upstream compiler reference and a successful compiler run before merge.

Avoid environment-dependent output, interactive prompts and speculative runtime features. Use the documented `scarp run PATH` command and syntax supported by the pinned compiler commit. Both `print` and `println` appear in compiler-verified examples, but older prereleases may differ.

The verifier treats every `.srp` outside an `_support` directory as a lesson, requires one fixture per lesson, and fails on unmatched fixtures. All tested examples are compared byte-for-byte; `check` and `run` must both succeed.
