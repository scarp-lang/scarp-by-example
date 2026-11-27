# Generic functions and text — Scarp v0.0.7-alpha.3

This independent workshop targets the [published Alpha.3 release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.7-alpha.3), source commit `44a3bb0a91e67570e46ce058a3f6211f8e5db0f5`. It does not change the numbered course's compiler target or its historical fixtures. Run these lessons with the Alpha.3 interpreter, not a native backend.

## Run locally

Install the matching published compiler, or check out the exact source commit and build with `cargo build --locked --offline`. From the examples repository root:

```sh
scarp version
scarp verify tutorials/alpha7-generics-text/generic_values.srp
scarp exec tutorials/alpha7-generics-text/generic_values.srp
```

The output must match the adjacent `.stdout` file, including spaces and newlines. Repeat for the other programs below. On Windows, use `scarp.exe` if needed. Keep the source files in UTF-8 with LF line endings.

| Program | Learn | Try next |
| --- | --- | --- |
| [generic_values](generic_values.srp) | Infer types from values, explicit arguments, tuple and fixed-array parameters | Pass a boolean to identity, then try a two-element string array. |
| [generic_constraints](generic_constraints.srp) | Numeric vs Comparable; preserve integer, Decimal, float and BigInt precision | Compare two tuples with equal first elements. Why does the second element matter? |
| [contextual_inference](contextual_inference.srp) | Binding annotations, explicit type arguments, record fields and defaults | Add a list of integers using an annotated binding. |
| [generic_option](generic_option.srp) | Some, None, matching and typed fallbacks | Compare a present zero with an absent integer. |
| [generic_result](generic_result.srp) | Propagation with `?`, preserving the error type | Try a different error message; follow the Err branch. |
| [string_operators](string_operators.srp) | Concatenation, repeat, raw and multiline text | Compare an escaped newline with a raw backslash followed by n. |
| [text_snapshots](text_snapshots.srp) | Compound updates, UTF-8 and zero repetition | Change the repeat count and confirm the previous snapshot is unchanged. |

## Avoid common mistakes

- A generic parameter is one exact type for a particular call. An unconstrained parameter cannot be multiplied; use `Numeric` where appropriate. Numeric supports integer, float, decimal and bigint, not string.
- `Comparable` permits ordering, not multiplication; compatible numeric tuples can be compared lexicographically.
- If no argument or surrounding result type fixes a parameter, write `empty::<integer>()` instead of `print(empty())`.
- The same type parameter cannot infer integer and float simultaneously. Use explicit conversions when semantically appropriate.
- An Option match must cover Some and None. Result propagation requires the same error type.
- Use `name + "\n" + language` for two lines. A raw literal `r"a\nb"` preserves the backslash. Triple-quoted strings preserve actual line breaks and indentation.
- String repetition has the string on the left and a nonnegative integer on the right. No implicit number-to-string conversion or string interpolation is introduced.

## हिन्दी मार्गदर्शिका

यह अभ्यास प्रकाशित Alpha.3 के लिए है। पुराना मुख्य पाठ्यक्रम अपने अलग कंपाइलर संस्करण पर बना रहता है।

- **Generic:** एक ही फ़ंक्शन अलग-अलग निश्चित प्रकारों के लिए उपयोग किया जा सकता है। `identity(100)` में T का प्रकार integer है, जबकि `identity("Scarp")` में string है।
- **Constraint:** Numeric गणितीय क्रियाओं की अनुमति देता है। Comparable तुलना की अनुमति देता है। अलग-अलग संख्यात्मक प्रकार अपने नियम बनाए रखते हैं।
- **Inference:** जब फ़ंक्शन का प्रकार केवल परिणाम से पता चलता है, तो binding में प्रकार लिखें या `::<integer>` दें।
- **Option:** Some में मान है, None में नहीं। शून्य मान और अनुपस्थित मान अलग हैं।
- **Result:** Ok सफलता और Err त्रुटि दर्शाता है। `?` त्रुटि को आगे भेज सकता है; त्रुटि का प्रकार वही होना चाहिए।
- **String:** `+` से टेक्स्ट जोड़ें और `*` से दोहराएँ। सामान्य string में newline escape काम करता है; raw string में वह ज्यों का त्यों रहता है।
- हर प्रोग्राम चलाकर उसकी `.stdout` फ़ाइल से परिणाम मिलाएँ। पहले मान को सुरक्षित रखकर string बदलने पर पुराना मान नहीं बदलता।

## Verification and scope

The independent workflow builds the exact published source on Linux, Windows and macOS, checks the compiler version and upstream string-example Git blob hashes, verifies the inventory, and compares executable stdout byte-for-byte. It also checks selected invalid generic and string expressions for the published diagnostic codes.

The string-operators pair is an unchanged upstream fixture from the compiler; the other six pairs are course-authored examples grounded in the released compiler's tests. The compiler's [generic-function guide](https://github.com/scarp-lang/scarp/blob/44a3bb0a91e67570e46ce058a3f6211f8e5db0f5/docs/generic-functions.md) explains specialization and its limits. The [string operator implementation tests](https://github.com/scarp-lang/scarp/blob/44a3bb0a91e67570e46ce058a3f6211f8e5db0f5/tests/string_operators.rs) cover additional cases.

Generic records, variants, user-defined constraints, closures and native string execution are outside this workshop. The experimental ELF64 backend is not the same execution mode as `scarp exec`.
