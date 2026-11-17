# Modern collections and checked results — Scarp alpha.13

**Release-pinned:** These examples are taken from published [Scarp v0.0.6-alpha.13](https://github.com/scarp-lang/scarp/releases/tag/v0.0.6-alpha.13) at annotated-tag commit `e755fda37cdaeed29434e848cb5dd41f2f2e7eb2`. All eight `.srp` programs and their `.stdout` files are **byte-for-byte copies from the official compiler examples** at that commit. They are not hypothetical APIs or hand-edited outputs.

The language features taught here arrived in **alpha.12**. Alpha.13 principally improves Rust-host cache/editor APIs, propagation payload handling and aggregate resource checks; it does **not** create a new list/map syntax. Host-only APIs are not presented as callable Scarp functions.

## Run on the published compiler

From the Scarp by Example repository root, using an **exact alpha.13 binary**:

~~~sh
scarp version
scarp verify tutorials/modern-collections/typed_dynamic_lists.srp
scarp exec tutorials/modern-collections/typed_dynamic_lists.srp
python scripts/verify_alpha13_compat.py --compiler /path/to/scarp --compiler-source /path/to/alpha13/compiler-checkout
~~~

On Windows use `scarp.exe`. For the final command, `--compiler-source` must be the **pinned Git checkout**, not just the path to a downloaded executable. The verifier checks the exact checkout SHA, binary version, upstream fidelity, static `verify` and byte-exact `exec` output for all eight programs.

| Official example | Learning goal |
| --- | --- |
| [Typed lists](typed_dynamic_lists.srp) | Homogeneous `list<T>`, records, nested lists |
| [Persistent list updates](persistent_list_updates.srp) | `list_push`, `list_set` and `list_remove` |
| [Typed maps](typed_maps.srp) | `map<K,V>`, canonical key order and equality |
| [Persistent map updates](persistent_maps.srp) | `map_set`, `map_remove`, `map_get_or` |
| [Ordered projections](map_projections.srp) | `map_keys` and `map_values` produce typed lists |
| [Option/Result matching](typed_submission.srp) | Exhaustive `match on` for success and failure |
| [Explicit propagation](typed_propagation.srp) | `?` on immutable binding initializers in named functions |
| [Aggregate boundaries](aggregate_resource_boundaries.srp) | Snapshot independence and boolean key ordering |

Read each source beside its neighboring expected-output file. Predict the exact stdout before executing. Map keys are printed in canonical ascending order regardless of their source order. `list_set` and `map_set` produce fresh snapshots; old bindings remain unchanged.

## Key limits

- `list<T>` is immutable and at most 4096 entries. Updates return new values and consume bounded work and allocation.
- `map<K,V>` accepts `integer`, `boolean` or `string` keys and at most 1024 distinct entries. Ordered projection follows canonical key order. `map_get_or` evaluates its fallback eagerly.
- `option<T>` and `result<T,E>` are checked concrete variants; constructors need explicit type arguments. `?` is allowed on an immutable `bind` initializer inside a named `funcra` with compatible enclosing Option/Result return type, not on arbitrary expressions.
- These source programs use interpreter execution; they do not imply a native executable compiler, GPU support, an unrestricted runtime or browser execution.

Upstream references: [lists](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.13/docs/typed-dynamic-lists.md), [maps](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.13/docs/typed-maps.md), [Option/Result](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.13/docs/option-result.md), and [propagation](https://github.com/scarp-lang/scarp/blob/v0.0.6-alpha.13/docs/option-result-propagation.md).

## हिन्दी अभ्यास

यह कार्यशाला प्रकाशित **alpha.13 compiler** के असली उदाहरणों पर आधारित है। Typed list, map और Option/Result जैसी सुविधाएँ पहले **alpha.12** में आई थीं।

1. `persistent_list_updates.srp` में देखें कि पुरानी list नहीं बदलती, नया snapshot बनता है।
2. `typed_maps.srp` में keys का लिखा हुआ क्रम और output का क्रम तुलना करें।
3. `map_projections.srp` में `map_keys` और `map_values` से एक ही canonical key-order मिलता है।
4. `typed_propagation.srp` में समझें कि `Err` या `None` पर `?` function से जल्दी return करता है, लेकिन यह हर expression पर नहीं लग सकता।

`scarp verify` static जाँच करता है; `scarp exec` code चलाता है। Website पर कोड दिखाई देता है, लेकिन वहाँ Scarp interpreter नहीं चलता।
