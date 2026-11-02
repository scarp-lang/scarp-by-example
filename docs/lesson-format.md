# Lesson-writing standard

Each runnable lesson needs:
- A short descriptive `.srp` filename with a numbered prefix.
- A matching `.stdout` file with the exact printed output (UTF-8, LF; include trailing newline where emitted).
- A section README entry that explains the concept and links to the files.
- A known upstream compiler reference and a successful compiler run before merge.

Avoid environment-dependent output, interactive prompts and speculative runtime features. Use the documented `scarp run PATH` command, not old prerelease commands such as `println` on current `main`.

The verifier treats every `.srp` outside an `_support` directory as a lesson, requires one fixture per lesson, and fails on unmatched fixtures. All tested examples are compared byte-for-byte; `check` and `run` must both succeed.
