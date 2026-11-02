# 01 · Scarp basics

Start with the basics before tackling functions and modules.

All examples are copied from the [Scarp compiler example suite](https://github.com/scarp-lang/scarp/tree/main/examples), whose `scripts/check.sh` exercises these programs. See [upstream attribution](../../THIRD_PARTY_NOTICES.md).

| Lesson | Learn | Expected result |
| --- | --- | --- |
| [01 · Hello](01-hello.srp) | `print` displays a string | `Hello from Scarp!` |
| [02 · Bindings](02-bindings.srp) | `bind` defines immutable values and expressions | Area followed by `42` |
| [03 · Mutable values](03-mutable.srp) | `var`, assignments and compound arithmetic | Sequence shown in [stdout](03-mutable.stdout) |
| [04 · Arithmetic](04-arithmetic.srp) | Integer operators and precedence | Sequence shown in [stdout](04-arithmetic.stdout) |
| [05 · Booleans](05-booleans.srp) | Comparisons, boolean logic and short-circuiting | `true`, `false`, `true`, `false` |
| [06 · Scopes](06-scopes.srp) | Nested blocks and shadowed names | `11`, `23`, `11`, `3` |
| [07 · String bindings](07-string-bindings.srp) | Reassigning a string and local shadowing | English and Hindi text, plus integer `42` |
| [08 · Output](08-output.srp) | `write` versus `print` | Mixed output; final `done` has no newline |
| [09 · Unicode](09-unicode.srp) | UTF-8 literals | `नमस्ते 🌍` and `café — Scarp` |
| [10 · Unicode text](10-unicode-text.srp) | Text length, byte count, code points and searches | `6 10 127757`, `5 true`, `true true` |
| [11 · Scalar conversions](11-scalar-conversions.srp) | Explicit numeric conversion | `10.5 12 0` |
| [12 · Escapes](12-escapes.srp) | Newline, quotation mark, and backslash escapes | Four visible output lines |
| [13 · Comments](13-comments.srp) | `//` line comments, strings containing comment markers and whitespace between tokens | `// inside a string is text`, blank line, then `done` |
| [14 · Bitwise fields](14-bitwise-fields.srp) | Hex/binary integer literals, `|=`, `&`, `>>>`, `<<` and `~` | `3`, `10`, signed 64-bit minimum, `-1` |
| [15 · Control escapes](15-control-escapes.srp) | Tab, literal carriage return and escaped backslashes | Three output lines with exact tab and inline CR bytes |

**Run any lesson:** `scarp run examples/01-basics/01-hello.srp` from this repository root, with the compiler executable on `PATH`. Or use its absolute path.

**Check it:** `scarp check examples/01-basics/01-hello.srp` (silent when successful).

**Exact output:** each lesson has a `.stdout` file next to the `.srp` file. Fixtures preserve the exact bytes, including any final newline **or its absence**, and are checked automatically. Read the source, predict the output, run it, then compare the fixture.

## More to notice

- **06:** Each new block may introduce a new binding with the same name. The outer value remains available after the inner scope finishes.
- **07:** A `var` can be assigned another string, while `bind` remains immutable; a block can shadow a name with another type.
- **08:** `write` does not append a newline; `print` does. The expected-output file intentionally has **no final newline**.
- **09–10:** Unicode characters and UTF-8 bytes are different counting units. Compare `text_len` and `text_bytes` before assuming indexing is byte-based.
- **11:** Conversions require explicit calls (`to_float` and `to_integer`), not a silent change of numeric type.
- **12:** An escape sequence in a quoted string can represent a newline or literal backslash.
- **13:** `//` starts a comment **outside** a quoted string. The compiler also accepts `println` in this pinned revision; the statement name can be separated from its parentheses by a comment and whitespace.
- **14:** `0xA0 | 0b0011` is `0xA3` (163 decimal). Applying `& 0x0F` isolates the lowest four bits and produces 3; `>>> 4` gives 10. `1 << 63` prints `-9223372036854775808` in this signed 64-bit example and `~0` gives -1. Bitwise operators on integer representations are **not** the same as `and`/`or` on boolean values.
- **15:** `\\t` embeds a tab and `\\r` embeds an actual carriage-return byte. Text editors and terminals may display a carriage return differently. The byte-exact fixture is authoritative; the website deliberately displays it as a visible `\\r` sequence without rewriting the file.

**Practice:** predict the stdout before opening a fixture, then run `scarp check` and `scarp run` on the lesson.

**Note:** `bind` is not a mutable variable. `var` allows reassignment. The pinned compiler accepts both `print` and `println` in these examples; older releases may differ.
