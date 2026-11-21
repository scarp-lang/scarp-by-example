# Published Scarp alpha.10 — input, arrays and exact arithmetic

This independent workshop uses the **published** [Scarp v0.0.6-alpha.10](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.10), pinned to source commit `44fcd0f77ccb92648cdb1fc7632495c506c87cb3`. Every runnable `.srp`, `.stdin` and `.stdout` file here is an **exact copy** of the official compiler's corresponding published fixture. The programs are implemented, not proposed. Original compiler examples are Apache-2.0 licensed.

**Course boundary:** the main 52 numbered lessons still target alpha.4. The separate [alpha.9 BigInt workshop](../exact-bigint/README.md) remains pinned to alpha.9. This workshop does not change either compiler target, lesson count, site search index or production Pages routes. Static website examples do not execute in a browser.

## Six runnable examples

| Files | Concept | Execution mode |
| --- | --- | --- |
| [Fixed arrays](fixed_arrays.srp) · [output](fixed_arrays.stdout) | Immutable `array<T, N>`, nested arrays, indexing, structural equality, typed empty arrays | ordinary |
| [Advanced BigInt](bigint_exact.srp) · [output](bigint_exact.stdout) | Exact `bigint_divmod`, powers, bit lengths, radix conversion, integer roots and GCD | ordinary |
| [Unicode line inventory](line_inventory.srp) · [input](line_inventory.stdin) · [output](line_inventory.stdout) | `try_read_line()`, blank lines versus EOF, CRLF and final non-terminated line | redirected stdin |
| [Prompt and fallback](interactive/greeting.srp) · [input](interactive/greeting.stdin) · [output](interactive/greeting.stdout) | `ask_or` prompt, UTF-8 text, EOF fallback | `--interactive` |
| [Typed calculator](interactive/typed_calculator.srp) · [input](interactive/typed_calculator.stdin) · [output](interactive/typed_calculator.stdout) | `input_float`, `input`, `flush_stdout`, conditional arithmetic | `--interactive` |
| [Big integer prompt](interactive/exact_integer.srp) · [input](interactive/exact_integer.stdin) · [output](interactive/exact_integer.stdout) | `input_bigint`, exact signed arithmetic beyond 64-bit | `--interactive` |

## Run locally

Install the alpha.10 compiler (or build it from the exact source commit). Confirm `scarp version` reports `scarp 0.0.6-alpha.10`. From the **learning repository root**:

```sh
scarp verify tutorials/alpha10-foundations/fixed_arrays.srp
scarp exec tutorials/alpha10-foundations/fixed_arrays.srp
scarp exec tutorials/alpha10-foundations/bigint_exact.srp
scarp exec tutorials/alpha10-foundations/line_inventory.srp < tutorials/alpha10-foundations/line_inventory.stdin
scarp exec --interactive tutorials/alpha10-foundations/interactive/greeting.srp < tutorials/alpha10-foundations/interactive/greeting.stdin
scarp exec --interactive tutorials/alpha10-foundations/interactive/typed_calculator.srp < tutorials/alpha10-foundations/interactive/typed_calculator.stdin
scarp exec --interactive tutorials/alpha10-foundations/interactive/exact_integer.srp < tutorials/alpha10-foundations/interactive/exact_integer.stdin
```

Use these shell redirections in Bash. On Windows PowerShell, use the compiler's explicit `--input-file` option with the corresponding `.stdin` file instead of shell input redirection, which can alter bytes in some shells. Pass `--interactive` for prompt-driven examples. Without it, prompt calls fail with E0054 rather than quietly reading terminal input.

**Prompt output is not atomic:** prompt text is intentionally flushed before a read; the user can see it even if a later operation fails. Ordinary non-interactive output is replayed after successful execution. For repeatable output comparisons, use the checked-in `.stdin` fixtures; they include exact UTF-8 bytes, and the inventory sample intentionally includes both CRLF and a final line without a newline. Do not strip or normalize them.

## Try the concepts

1. **Arrays:** In `fixed_arrays.srp`, locate `array<string, 2>`, nested array indexing and `[array: <array<integer, 2>>]`. Unlike numerical vectors, fixed arrays can contain strings or nested structural values. Arrays have immutable elements; a `var` may replace the whole array with the same exact type. Out-of-bounds indices raise a runtime diagnostic.
2. **BigInt:** Examine `bigint_divmod`. The quotient truncates toward zero, and remainder follows the dividend's sign. The bit-length of `2^128` is 129; integer square root is `2^64`. These operations consume bounded computation and storage.
3. **Line input:** `try_read_line()` returns `(true, line)` even for an empty input line, versus `(false, "")` at EOF. The Unicode inventory uses this distinction to count **three** lines correctly.
4. **Prompts:** `input_float` returns a finite float; `input_bigint` returns exact arbitrary-precision (bounded) integer values. A plain `input` returns text. Invalid typed input fails rather than falling back to an implicit conversion.
5. **Streams:** `flush_stdout()` makes ordinary output visible immediately. For separate stderr examples and test fixtures, see the published compiler's stream-output documentation; this course does not pretend that stdout and stderr are interchangeable.

These are **interpreter** examples, not compiled native executables. Scarp alpha.10 does not provide general file read/write/append functions. Advanced BigInt modular exponentiation uses variable-time arithmetic; do not assume constant-time cryptographic protection.

## Provenance and verification

Run `python scripts/verify_alpha10_foundations.py --compiler /absolute/path/to/scarp --compiler-source /absolute/path/to/pinned/compiler` using an exact checkout of the compiler source. It validates the immutable source commit, compiler version, byte-identical upstream fixtures, silent static checking, exact runtime stdout, empty stderr on success, and E0054 capability gating. GitHub Actions builds the published compiler source and repeats the checks on Linux, Windows and macOS; no latest-main compiler behavior is silently substituted.

## हिन्दी में सीखें

यह स्वतंत्र कार्यशाला प्रकाशित **Scarp v0.0.6-alpha.10** के लिए है। मुख्य 52 पाठ alpha.4 पर ही सत्यापित हैं; उन्हें बिना जाँच बदला नहीं गया है।

- **Fixed arrays:** `array<integer, 2>` में ठीक दो समान प्रकार के मान होते हैं। `[array: 1, 2]` एक array है, सामान्य numeric vector नहीं। `[array: <integer>]` खाली लेकिन स्पष्ट प्रकार वाला array है।
- **बड़े पूर्णांक:** `bigint` सामान्य `integer` (signed 64-bit) से अलग है। `bigint_divmod`, `bigint_pow`, `bigint_gcd` और radix conversion के परिणाम सटीक हैं, लेकिन संसाधन सीमाएँ लागू होती हैं।
- **Input:** `try_read_line()` में `(true, "")` का अर्थ खाली लाइन है; `(false, "")` का अर्थ EOF है। इसलिए खाली लाइन को पढ़ना बंद करने का संकेत न मानें।
- **Interactive:** `input`, `input_float`, `input_bigint` और `ask_or` के लिए `--interactive` दें। Prompt तुरंत दिखता है। `.stdin` फाइल में जो UTF-8 डेटा है, उसका क्रम वही रखें।
- **अभ्यास:** पहले हर `.srp` चलाकर साथ की `.stdout` से तुलना करें। फिर अपनी कॉपी में दो float का गुणन बदलकर जोड़ करें और नया परिणाम जाँचें; आधिकारिक fixtures को न बदलें।

सभी उदाहरण वास्तविक कंपाइलर के प्रकाशित source से लिए गए हैं। वेबसाइट स्वयं Scarp को ब्राउज़र में नहीं चलाती।
