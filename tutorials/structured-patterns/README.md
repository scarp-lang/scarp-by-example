# Structured patterns and deterministic map snapshots — Scarp alpha.14

**Compiler provenance:** Published [Scarp v0.0.6-alpha.14](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.14), exact compiler commit `43627b74af5fccccc5e233e98207413983ebafc1` (18 November 2026). The two `.srp` programs and two `.stdout` fixtures in this directory are **byte-identical to the corresponding committed compiler examples** at that pin. These are interpreter-backed programs, not sample pseudocode.

This optional workshop deliberately does **not** replace the separately validated alpha.13 baseline for the 52 numbered lessons. Its dedicated three-OS CI will also rerun those existing lessons and labs against alpha.14 to detect compatibility regressions before changing the default pin.

## Website learning pages

The static learning portal provides [a workshop overview](https://scarp-lang.github.io/scarp-by-example/workshops/structured-patterns/) and a **separate page for each original program**:

- [Nested record and tuple patterns](https://scarp-lang.github.io/scarp-by-example/workshops/structured-patterns/nested-record-tuples/)
- [Persistent map projections](https://scarp-lang.github.io/scarp-by-example/workshops/structured-patterns/persistent-map-projections/)

These are source-backed documentation pages, not live interpreter playgrounds. The links become public on GitHub Pages only after the reviewed change is merged and deployed.

## Run the original source


From this learning repository, with the **exact published alpha.14** `scarp` executable:

~~~sh
scarp version
scarp verify tutorials/structured-patterns/structured_pattern_coverage.srp
scarp exec tutorials/structured-patterns/structured_pattern_coverage.srp
scarp verify tutorials/structured-patterns/map_string_projection_snapshots.srp
scarp exec tutorials/structured-patterns/map_string_projection_snapshots.srp
python scripts/verify_alpha14_patterns.py --compiler /absolute/path/to/scarp --compiler-source /path/to/scarp-alpha14-git-checkout
~~~

Windows users should use `scarp.exe` for the executable; the verifier requires the actual Git checkout at the commit above, not an arbitrary source directory. It checks the compiler version and **committed Git objects**, then invokes static verification and compares exact UTF-8 stdout bytes.

## 1. Nested record and tuple patterns

**[Source](structured_pattern_coverage.srp) · [Exact output](structured_pattern_coverage.stdout)**

The program creates an `Event::Move` carrying a named `Point` record. A `match on` arm destructures the record fields into `horizontal` and `vertical`. A separate `bind (first, second)` destructures a two-element tuple. Predict the three printed lines and check the fixture: `12`, `30`, then `13`.

The **alpha.14 improvement** is clearer parser diagnostics for missing/duplicate commas and closing delimiters in nested tuple, array and record patterns. The overall destructuring feature predates this prerelease. Nested refutable patterns and pattern guards are not implied by the example.

**Try:** Locally change the tuple values, predict the new third line and run `scarp verify` followed by `scarp exec`. Do not overwrite the checked-in official fixture with your experiment.

## 2. Deterministic maps after persistent updates

**[Source](map_string_projection_snapshots.srp) · [Exact output](map_string_projection_snapshots.stdout)**

Start with `"z"`, `"a"` and `"m"` keys, then insert `"b"`, replace `"m"` and remove `"z"`. On each snapshot, `map_keys` and `map_values` traverse the same **canonical key ordering**. The original snapshot remains unchanged. Pair each values-list entry with the key at the same index: this makes the deterministic order easy to inspect.

**Try:** Before opening the fixture, write the ten expected output lines in order. Explain why the final two match the first two despite later changes. You can experiment with additional keys in a separate copy.

## हिन्दी मार्गदर्शिका

यह कार्यशाला प्रकाशित **alpha.14 compiler** के वास्तविक उदाहरणों पर आधारित है।

1. **Nested patterns:** `Move` में मौजूद `Point` record से `horizontal` और `vertical` निकालकर प्रिंट किया जाता है। फिर `(first, second)` tuple से दो मान लेकर उनका योग निकालते हैं।
2. **Maps:** `map_set` और `map_remove` पुराना map बदलते नहीं; वे नया snapshot देते हैं। `map_keys` और `map_values` में क्रम एक जैसा रहता है, इसलिए संबंधित key और value एक ही index पर मिलते हैं।
3. **अभ्यास:** पहले बिना चलाए output लिखें, फिर `scarp verify` और `scarp exec` से जाँचें। मूल `.stdout` fixture को प्रयोग के समय न बदलें।

## Supported boundary

The source-language examples use the **local Scarp interpreter**. Alpha.14's checked ELF64 integer object emitter and editor cache limits are **Rust embedding APIs**, not ordinary Scarp functions or a general `scarp compile` command. The static learning site shows code and fixtures; it does not execute Scarp in a browser.

The upstream example files retain the [compiler's Apache-2.0 licensing terms](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.14/LICENSE-APACHE-2.0); this learning repository also carries the relevant notice.
