# 05 · Modules and explicit imports

Modules let a lesson separate a public API from implementation details.

| Lesson | Demonstrates | Expected output |
| --- | --- | --- |
| [01 · Modular inference](01-modular-inference.srp) | `import "...srp" as name`, exported bindings, public pure function | `Modular inference`, `[4.0, 1.0]`, `0 [1.0, 0.0]` |
| [02 · Constant expressions](02-constant-expressions.srp) | Exported constants, chained imports and a function's default argument | `constant expressions 42 84 true 0.75 42` |
| [03 · Integer series](03-integer-series.srp) | Import a typed `integers` API, supply a named argument and call a numerical helper | `[integer: -1, 0] 0.5 3` |
| [04 · Public and private API](04-public-private-api.srp) | Exported function calls an internal helper without exporting it | `module tools 42` |
| [05 · Exported signatures](05-exported-signatures.srp) | Typed public constants, a pure function and its default argument | `42` |

The first lesson imports [linear.srp](_support/linear.srp), which itself imports [settings.srp](_support/settings.srp). Both are **support modules**, not separate runnable lessons. The source comes from the upstream compiler's `module_demo.srp`; its import path was changed from `modules/` to `_support/` for the course. Lesson 02 similarly uses `_support/constants.srp` and `_support/constant_base.srp`.

From the repository root: `scarp verify examples/05-modules/01-modular-inference.srp` followed by `scarp exec examples/05-modules/01-modular-inference.srp`. The first command validates the source without executing its runtime statements; the second prints output.

**Notice:** `pub` exposes declarations; `pure funcra` defines a pure function. Keep the `_support/` directory next to the entry point; imports are resolved relative to their importing files.

**New lesson:** [02 · Constant expressions](02-constant-expressions.srp) imports `_support/constants.srp`, which imports `_support/constant_base.srp`. The modules demonstrate source-relative paths and public constants; constants are not runtime-mutable shared globals. Keep both helpers in `_support` when copying the lesson.


## Try imported numeric APIs and inspection

**03 · Typed integer series:** The imported [`integer_series.srp`](_support/integer_series.srp) exports a `sequence` function returning an `integers` collection. The named argument `start: -1` overrides its default; `count = 2` therefore yields the two values -1 and 0. `spread` converts the collection to a numerical vector before calculating standard deviation, producing 0.5. `low_bits & 0x3` yields 3. This is a specialised numeric collection, **not** general-purpose lists or maps.

**04 · Public/private boundaries:** The imported [`inspection.srp`](_support/inspection.srp) exposes `label` and `adjusted`. Internally, `adjusted(39)` adds a private helper's offset (1) and the default `step` (2), producing 42. The private `helper` and `offset` are implementation details: the importing source cannot use them directly. A public function is allowed to use private declarations from its own module.

**05 · Inspectable signatures:** `pub bind base: integer` and `pub bind answer: integer` expose typed constants; `echo(value: integer = answer)` returns the default value 42. This source is also a safe target for the **static** module inspector:

```sh
scarp inspect modules examples/05-modules/05-exported-signatures.srp
scarp inspect modules --json examples/05-modules/05-exported-signatures.srp
```

The JSON reports a schema-versioned module inventory, **not** program output and not a general JSON API for Scarp. To execute the same lesson:

```sh
scarp exec examples/05-modules/05-exported-signatures.srp
```

It prints `42`. For more on what each command really does, read the [CLI quickstart](../../docs/cli-quickstart.md).

**Exercises:** Explain why `sequence(2, start: -1)` has exactly two values; trace where `adjusted(39)` obtains its 1 and 2; find the function's default argument in `inspect modules --json` metadata. Do not edit the byte-exact fixtures while experimenting.
