# Exact decimals and deliberate rounding — Scarp alpha.11

This **optional, independently pinned** workshop is for the published [Scarp v0.0.6-alpha.11 prerelease](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.11) at immutable source commit `79b57395957f47e1270ee542a856c844b82386de`. The two upstream example programs and their exact `.stdin` / `.stdout` fixtures are byte-identical copies of the compiler repository. The additional rounding program follows the published regression tests. This is not a migration of the numbered course: its **52 lessons remain on alpha.4**. The examples run in the local interpreter, **not** in the learning website or native C11/ELF compilers.

## Run and compare

Use the **alpha.11** Scarp executable, not alpha.10 or the current compiler `main`:

```sh
scarp version
scarp verify tutorials/exact-decimal/decimal_exact.srp
scarp exec tutorials/exact-decimal/decimal_exact.srp
scarp exec tutorials/exact-decimal/rounding_and_conversion.srp
scarp verify tutorials/exact-decimal/interactive/exact_decimal.srp
```

For the typed-input example, run locally with interactive permission:

```sh
scarp exec --interactive tutorials/exact-decimal/interactive/exact_decimal.srp
```

Enter `2.675`, then press Enter. The exact prompt and output appear in `interactive/exact_decimal.stdout`. To replay a fixture rather than type it, the workshop CI passes the original UTF-8 `interactive/exact_decimal.stdin` bytes to the process. `scarp verify` checks syntax/types without running code. `scarp exec` actually executes it. Interactive `input_decimal` is intentionally rejected without `--interactive` (E0054).

| Example | Lesson |
| --- | --- |
| [Exact arithmetic](decimal_exact.srp) | Typed decimal function, tax calculation, array elements, and explicit rounded division: `235.99`, `0.3`, `0.33` |
| [Explicit rounding](rounding_and_conversion.srp) | Half-even vs half-up tie rules, presentation scale, and explicit integer conversion |
| [Interactive exact input](interactive/exact_decimal.srp) | Hindi prompt `राशि> `, UTF-8 input, decimal parsing and half-even formatting |

## Important semantics

- `decimal("0.1") + decimal("0.2")` is exactly `0.3`; the separate `float` type uses binary64. There are **no implicit conversions** between numeric types. Convert to/from integer with `decimal_from_integer` / `decimal_to_integer`.
- `decimal_round(value, places, mode)` changes a numeric value. `decimal_format(value, places, mode)` returns **text** with exactly that many displayed places; for instance, `decimal_format(decimal("1.2"), 2, "half_even")` yields `1.20`.
- `decimal("1") / decimal("3")` cannot be represented exactly and reports **E0070**. Explicitly choose a scale and rounding mode with `decimal_div_rounded`.
- Valid rounding modes are `half_even`, `half_up`, `toward_zero` and `away_from_zero`. Decimal text or a mode that is invalid reports **E0068**; limit failures use **E0069**.
- Limits: at most **28 canonical coefficient digits**, **18 fractional places**, and **96 UTF-8 bytes** of constructor input. Text exponents, thousands separators, NaN and Infinity are not supported. Native C11/ELF decimal execution is unavailable (E0049).
- Module constant initializers do not allow constructor calls; bindings/functions/tuples/fixed arrays and imported signatures can carry the decimal type.

For more details, read the [compiler's version-pinned Decimal reference](https://github.com/scarp-lang/scarp/blob/79b57395957f47e1270ee542a856c844b82386de/docs/decimal.md).

## Reproducible release verification

```sh
python -m unittest discover -s scripts -p 'test_alpha11_decimal.py'
python scripts/verify_alpha11_decimal.py --compiler /path/to/scarp --compiler-source /path/to/alpha11-checkout
```

The verifier rejects wrong compiler checkout and binary versions, checks all five upstream source/input/output files byte-for-byte, statically verifies and runs all three examples, compares stdout **as bytes**, checks the E0054 interactive gate and tests negative Decimal diagnostics. The separate GitHub Actions matrix runs it on Linux, Windows and macOS.

## हिन्दी में अभ्यास

यह कार्यशाला प्रकाशित **Scarp alpha.11** के लिए है। मुख्य 52 पाठ alpha.4 पर ही रहेंगे। यह वेबसाइट पर कोड चलाने का दावा नहीं करती; उदाहरण अपने कंप्यूटर पर Scarp interpreter से चलाएँ।

1. `decimal_exact.srp` में देखें कि `0.1 + 0.2` का परिणाम सटीक `0.3` है। `float` और `decimal` अलग प्रकार हैं।
2. `rounding_and_conversion.srp` में `half_even` और `half_up` से `1.225` को दो दशमलव स्थान तक गोल करें। फिर `decimal_round` (संख्या) और `decimal_format` (टेक्स्ट) की तुलना करें।
3. `interactive/exact_decimal.srp` में `राशि> ` के बाद `2.675` दें। आउटपुट `राशि> 2.68` है। इस प्रोग्राम के लिए `--interactive` ज़रूरी है।
4. किसी अलग अस्थायी फ़ाइल में `decimal("1") / decimal("3")` चलाकर E0070 देखें; फिर स्पष्ट राउंडिंग के साथ `decimal_div_rounded` इस्तेमाल करें।

बदलाव के बाद मूल सत्यापित उदाहरण वापस रखें ताकि उनकी `.stdout` फ़ाइलों से परिणाम मेल खाते रहें।
