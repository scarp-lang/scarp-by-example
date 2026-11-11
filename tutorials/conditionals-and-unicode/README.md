# Conditional expressions and Unicode escapes — Scarp alpha.7

This optional, independent workshop uses **published Scarp v0.0.6-alpha.7**,
source commit `b1c1fd232b418267d95520c69ee563ac99ecae30`.
It does not change the numbered course's older compiler target or the separately
pinned alpha.6 input-and-tuples workshop in draft PR #62.

[Official alpha.7 prerelease](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.7)
· [Compiler compatibility information](../../docs/compatibility.md)

## Three source-verified programs

| Source | What you learn | Expected output |
| --- | --- | --- |
| [01-grading.srp](01-grading.srp) | `if`/`elif`/`else` as a string value, and returning a conditional value from a typed pure function | [fixture](01-grading.stdout) |
| [02-lazy-branches.srp](02-lazy-branches.srp) | Only selected branches execute: no stdin read and no division by zero | [fixture](02-lazy-branches.stdout) |
| [03-unicode-scalars.srp](03-unicode-scalars.srp) | `\u{HEX}` characters, scalar/UTF-8 byte counts, and composed vs. decomposed text | [fixture](03-unicode-scalars.stdout) |

From this repository root, use the **alpha.7** Scarp executable:

```sh
scarp verify tutorials/conditionals-and-unicode/01-grading.srp
scarp exec tutorials/conditionals-and-unicode/01-grading.srp
scarp exec tutorials/conditionals-and-unicode/02-lazy-branches.srp
scarp exec tutorials/conditionals-and-unicode/03-unicode-scalars.srp
```

`verify` statically checks types and syntax; `exec` runs the interpreter.
No input is required for these programs. Each adjacent `.stdout` file is checked
byte-for-byte in the three-OS Actions matrix. You can reproduce all checks with:

```sh
python scripts/verify_alpha7_workshop.py --compiler /path/to/scarp --compiler-source /path/to/scarp-checkout
```

## Important boundaries

- An expression has the shape `if condition { value } elif condition { value } else { value }`.
- The final `else` is mandatory, every result block has one expression, and all results must have **the same exact type**.
- A branch that is not selected still needs to be syntactically and type-correct; it is not evaluated at runtime.
- Conditional **expressions** work in the interpreter, not in module constant definitions or the experimental native C11/ELF64 emission paths.
- `\u{HEX}` represents a valid Unicode scalar value. Surrogate values, codepoints above U+10FFFF and invalid hex escapes are diagnosed.
- Unicode scalar count and UTF-8 byte count differ. `e` plus a combining accent has two scalars and three bytes; it is not byte-equal to the single precomposed character.

## हिन्दी में समझें

यह कार्यशाला प्रकाशित **Scarp alpha.7** पर आधारित है। पहले तीन `.srp` फ़ाइलों को पढ़ें,
फिर ऊपर दिए `verify` और `exec` कमांड चलाएँ। परिणामों की तुलना संबंधित `.stdout` फ़ाइल से करें।

**पहला पाठ:** `if` को सिर्फ़ कोई statement नहीं, बल्कि मान लौटाने वाली expression के रूप में
भी लिख सकते हैं। `score` बदलकर देखें कि `elif` या `else` में से कौन-सी branch चुनी जाती है।
हर branch को एक ही प्रकार का मान लौटाना चाहिए और अंतिम `else` आवश्यक है।

**दूसरा पाठ:** केवल चुनी हुई branch चलाई जाती है। इसीलिए उदाहरण में अनचाहा
`read_line()` और `1 / 0` कभी execute नहीं होते। लेकिन compiler उन branches की
syntax और types फिर भी जाँचता है।

**तीसरा पाठ:** `\u{HEX}` से Unicode character लिखा जाता है। `नमस्ते 👋` बनता है।
`text_len` Unicode scalar गिनता है; `text_bytes` UTF-8 bytes गिनता है।
एक-जैसे दिखने वाले अलग Unicode sequences हमेशा सीधे बराबर नहीं होते।

अभ्यास: पहले पाठ के `score` को 95 और फिर -2 करें; दूसरे पाठ में `true` और
`false` की जगह बदलने पर runtime पर क्या असर पड़ेगा, इसे **सोचकर बताएँ**।
मूल fixtures को PR में बदलने से पहले वापस रखें ताकि CI में सत्यापन बना रहे।
