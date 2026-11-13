# Exact signed integers — Scarp alpha.9 workshop

This optional hands-on workshop uses **published Scarp v0.0.6-alpha.9**, source commit `0814997dc43982eb707a9a1aee72aab3a7ac8b41`. Its source and output files are **byte-for-byte copies of the published compiler examples**, not hypothetical syntax. [Published alpha.9 release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.9).

**Compatibility boundary:** This workshop needs alpha.9. The numbered course on `main` remains pinned to alpha.4; alpha.5–alpha.8 additions live in separate review branches. Do not copy these examples into the earlier course without upgrading its compiler tests. This is interpreter execution; alpha.9 does not add a native executable build command.

## Run the three examples

Use the exact published alpha.9 Scarp compiler. From the repository root:

```sh
scarp version
scarp verify tutorials/exact-bigint/bigint_arithmetic.srp
scarp exec tutorials/exact-bigint/bigint_arithmetic.srp
scarp exec tutorials/exact-bigint/bigint_sequences.srp
scarp exec tutorials/exact-bigint/bigint_module.srp
```

Compare each program's output with the adjacent `.stdout` file. Successful static `verify` checks types without running the program; `exec` actually evaluates it. Keep the companion `modules/bigint_math.srp` file beside the module example.

| Program | What it teaches |
| --- | --- |
| [Arithmetic](bigint_arithmetic.srp) | Decimal construction, explicit integer conversions, signed quotient/remainder, equality and ordering |
| [Sequences](bigint_sequences.srp) | Calculating the 100th Fibonacci number and 50! with an exact `bigint` return type |
| [Modules](bigint_module.srp) | Calling an exported pure function from an imported module |

Try the arithmetic example with the known signed rule: integer division truncates toward zero; for negative operands, a nonzero remainder has the dividend's sign. Unlike `integer`, which is signed 64-bit, `bigint` retains exact decimal integer results beyond that range. BigInt does **not** automatically convert to or from `integer` or `float`.

### Bounds and limitations

BigInt is bounded by runtime budgets, not infinite: the default digit budget is 10,000 decimal digits and the cumulative limb budget is 8 MiB. An explicitly configured higher digit limit can be up to 1,000,000, subject to the other limits. Large operations may hit work quotas earlier. BigInt interpreter support does not imply support for native C11/ELF code generation, decimal fractions, or an arbitrary-precision floating type. See the [published compiler documentation](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.9/docs/bigint.md).

To prove this workshop really matches the published compiler, build the pinned compiler source and run:

```sh
python scripts/verify_alpha9_bigint.py --compiler /path/to/scarp --compiler-source /path/to/pinned/compiler
```

The verifier checks the checkout commit, binary version, upstream source/output fidelity, static verification and exact output bytes. Its Linux/Windows/macOS jobs are independent of the numbered course.

## हिन्दी अभ्यास

यह कार्यशाला प्रकाशित **Scarp v0.0.6-alpha.9** के लिए है। मुख्य 52 पाठ अभी alpha.4 पर ही सत्यापित हैं।

1. `bigint_arithmetic.srp` में बड़ी धनात्मक संख्या में 1 जोड़ें और देखें कि परिणाम `integer` की 64-bit सीमा से बड़ा होकर भी सटीक रहता है।
2. ऋणात्मक संख्या का भाग तथा शेषफल देखें। भागफल शून्य की ओर घटता है और गैर-शून्य शेषफल का चिह्न भाज्य के समान रहता है।
3. `bigint_sequences.srp` में Fibonacci की 100वीं संख्या और 50! पढ़ें। केवल परीक्षण के लिए `repeat 100` बदलकर `repeat 10` करें; फिर मूल फ़ाइल वापस रखें।
4. `bigint_module.srp` में `exact.twice` देखें और समझें कि `pub pure funcra` किसी दूसरे मॉड्यूल में कैसे उपयोग होता है।

`verify` केवल कोड की जाँच करता है, जबकि `exec` प्रोग्राम चलाता है। `bigint` के लिए संसाधन सीमा है; इसे असीमित मेमोरी या native compilation न समझें। बदलावों के बाद मूल `.srp` फ़ाइलें वापस रखें ताकि सत्यापित उदाहरण और आउटपुट मेल खाते रहें।
