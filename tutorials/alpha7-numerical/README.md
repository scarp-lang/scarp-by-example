# Scarp v0.0.7-alpha.1 — numerical programming workshop

This independently pinned workshop teaches three source-language additions from the [published compiler release](https://github.com/scarp-lang/scarp/releases/tag/v0.0.7-alpha.1), commit `996bd5b83c8cb26e98637563729f67bdacc61cd4`. The numbered course and historical workshops keep their own compatibility targets. These are original course programs, informed by the official release and its examples, not verbatim upstream imports.

## Learning path

| Program | Concept | Predict before running |
| --- | --- | --- |
| [Array concatenation](array_concat.srp) | Matching element types, compile-time result length, immutable snapshots | What is the length of two arrays of length two? |
| [Integer reductions](integer_reductions.srp) | GCD/HCF alias, LCM across three integers, signed values and zero | When do periods 3, 5 and 8 first coincide? |
| [Stable softplus](stable_softplus.srp) | Element-wise floating-point activation, extreme scores, tolerance checks | What happens near zero and at very large positive or negative inputs? |

## 1. Fixed-size array concatenation

The pure function combines two integer arrays of length two into a new integer array of length four. The result type includes its length. Both original arrays retain their values. Concatenating a typed empty array leaves the values unchanged. The operation is not an in-place append; its element types must match. Fixed arrays and vector values are distinct types.

**Exercise:** Change the first input to two different integers. Predict all five output lines. Then change the declared return length to three and observe static rejection.

## 2. Integer reductions

GCD (greatest common divisor) and HCF (highest common factor) are equivalent here. The greatest positive integer dividing 18, 30 and 42 is 6. The signed input example also yields 6; zero does not erase the nonzero common factor. The least common multiple of 3, 5 and 8 is 120; an LCM containing zero returns zero. The release accepts 2–1024 integer operands. This is fixed-width integer arithmetic, not arbitrary-precision BigInt arithmetic; overflow must not be treated as a valid wrapped result.

**Exercise:** Predict the common divisor and the first shared period of 6, 10 and 15.

## 3. Stable softplus

Softplus is the smooth activation log(1 + exp(x)). A direct exponential can overflow for a large positive score, even if the mathematically correct activation is finite. The published compiler provides a stable vector implementation. The example uses two extreme finite values and checks the central value with a tolerance instead of relying on a particular printed approximation to log(2). The original score vector is unchanged. This is a mathematical primitive, not a trained model or automatic differentiation.

**Exercise:** Predict which of the two scores has the larger activation and why both central-value comparisons are true.

## Run locally

From the course root, use the published alpha.1 binary or build its exact source. For example:

~~~sh
scarp version
scarp verify tutorials/alpha7-numerical/array_concat.srp
scarp exec tutorials/alpha7-numerical/array_concat.srp
~~~

Repeat for the other two programs and compare the adjacent stdout files. To run the complete verification including rejected calls, use:

~~~sh
python scripts/verify_alpha7_numerical.py --compiler /absolute/path/to/scarp --compiler-source /absolute/path/to/pinned/scarp
~~~

The verifier requires the exact Git checkout and CLI version, silent static checks, empty stderr and byte-exact stdout for successful programs, plus rejected malformed calls. It is run on Linux, Windows and macOS by the dedicated CI workflow. The Pages workflow also runs it before generating the catalog.

The native ELF64 emitter, host token cache controls and frame reuse are implementation or Rust-host features; this workshop does not claim a native compilation CLI, unrestricted native calls, or source-level memory management controls. All workshop material is original MIT-licensed course content.

[हिन्दी मार्गदर्शिका](../../docs/hi/alpha7-numerical.md)
