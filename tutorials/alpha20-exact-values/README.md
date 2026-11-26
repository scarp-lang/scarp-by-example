# Exact values and tuple snapshots — Scarp alpha.20

[हिन्दी में पढ़ें](../../docs/hi/alpha20-exact-values.md) · [Published compiler](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.20)

This optional workshop is independently pinned to `b1a9347f93540fdf95b0ddecba4adc55a3b4bb98`. The numbered course proposes v0.0.7-alpha.1; this workshop retains its independent alpha.20 pin and is never silently retargeted. The upstream tuple examples retain their original development-era comments; the feature is now described in the published alpha.20 release notes. No newer compiler main behavior is assumed.

## Run and predict

Use the alpha.20 executable from the published release, or build the exact commit using Cargo. From this repository root:

~~~sh
scarp version
scarp verify tutorials/alpha20-exact-values/decimal_literals.srp
scarp exec tutorials/alpha20-exact-values/decimal_literals.srp
scarp exec tutorials/alpha20-exact-values/tuple_snapshots.srp
~~~

Compare the output with the adjacent `.stdout` files. A successful static verify is not proof of a correct runtime result.

| Program | Concept | Prediction exercise |
| --- | --- | --- |
| [decimal_literals](decimal_literals.srp) | Opt-in `d` suffix, exact arithmetic, ordinary float contrast | Why does adding 0.1d three times yield 0.3? |
| [decimal_exact](decimal_exact.srp) | Explicit constructor, typed arrays, rounding | Why does rounded one-third print 0.33? |
| [tuple_index_updates](tuple_index_updates.srp) | Constant-index replacement of a mutable binding | Which tuple retains the old coordinates? |
| [tuple_ordering](tuple_ordering.srp) | Numeric lexicographic comparisons, including nested tuples | Which differing member decides the result? |
| [tuple_snapshots](tuple_snapshots.srp) | Mixed member types, saved values and numeric comparison | Why is (1, 90) less than (2, 0)? |

## Decimal is not float

Use decimal literals for exact base-ten quantities. The suffix changes the type; it is not display formatting. The compiler rejects implicit decimal/float and decimal/integer addition. Use `decimal_format` for a requested number of displayed fractional digits, and `decimal_div_rounded` when explicitly rounded division is needed. Decimal precision and range are bounded; exact does not mean unlimited.

## Tuple changes are persistent

`var` permits rebinding after a replacement; `bind` does not. The index must be an in-range integer literal (parentheses are allowed), and the new member must preserve the original member type. Existing snapshots keep their original value. This is not an in-place array mutation API. Compatible numeric tuples compare lexicographically, not by summing their members. This workshop makes no promise about ordering arbitrary strings, records, or mismatched tuple shapes.

## Try failures

Use a separate scratch file for each case: decimal mixed with float, decimal mixed with integer, assignment to a tuple held by bind, a computed tuple index, an out-of-range index, or replacing an integer member with a string. The verifier expects E0015, E0013 or E0059 as appropriate, with no output.

## Validate the workshop

~~~sh
python scripts/verify_alpha20_exact_values.py --compiler /path/to/scarp --compiler-source /path/to/pinned/scarp
~~~

The dedicated three-platform workflow checks the exact Git commit, compiler version, upstream file identities, all five stdout fixtures, silent static verification, and rejected invalid programs. The [static online workshop](https://scarp-lang.github.io/scarp-by-example/workshops/alpha20-exact-values/) includes an overview and five dedicated lesson pages. Code runs locally, not in the browser.

The experimental Rust ELF64 emitter is not a source-language native compilation command. All programs here run with the interpreter. See [compatibility](../../docs/compatibility.md).
