# Lesson-writing standard

Each runnable lesson needs:
- A short descriptive `.srp` filename with a two-digit numbered prefix (e.g. `01-example.srp`). Lesson numbers in each chapter must start at `01`, be unique, and contain no gaps.
- A matching `.stdout` file with byte-exact printed output (UTF-8 and LF line endings; include trailing newline only if emitted). Intentional interior carriage-return bytes are allowed, but CRLF line endings are not.
- A section README table entry that explains the concept, includes the documented expected result, and links to the file.
- A matching numbered Hindi teaching section in `docs/hi/NN-topic.md` with the same original source and stdout links and a practical `**अभ्यास:**` question. The site publishes these notes directly on the standalone lesson page.
- A known upstream compiler reference and a successful compiler run before merge.

Avoid environment-dependent output, interactive prompts and speculative runtime features. Use the documented `scarp exec PATH` command and syntax supported by the pinned compiler commit. Both `print` and `println` appear in compiler-verified examples, but older prereleases may differ.

The verifier treats every `.srp` outside an `_support` directory as a lesson, requires one fixture per lesson, and fails on unmatched fixtures. All tested examples pass silent static `verify` and byte-for-byte `exec` output checks; legacy `check` semantics are tested separately. Read the [CLI guide](cli-quickstart.md) for command distinctions.
