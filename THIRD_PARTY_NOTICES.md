# Third-party example provenance

The initial Scarp programs and matching stdout fixtures were copied from the [official Scarp compiler repository](https://github.com/scarp-lang/scarp/tree/main/examples), inspected at commit `e4db8e191cd7ea623123cae7348450ca6c95b170`. They are derived from source distributed under **Apache License 2.0**, reproduced here in [LICENSE-APACHE-2.0](LICENSE-APACHE-2.0).

The learning repository's own original editorial material and tooling are MIT-licensed under [LICENSE](LICENSE), while upstream-derived example sources and output fixtures retain their upstream Apache-2.0 licensing and attribution. The origin of each initial lesson can be identified from the same stem under `scarp/examples/`.

The 2026-11-02 course expansion imported the following additional compiler fixtures from the same upstream source tree (unchanged between pinned compiler commit `e4db8e1` and inspected `9e50075`): `scopes`, `string_bindings`, `output`, `unicode`, `unicode_text`, `scalar_conversions`, `escapes`, `function_contracts`, `constant_expressions`, and `score_selection`. The `constant_expressions.srp` import prefix changed to `_support/` to match this repository's layout. Its upstream helpers `modules/constants.srp` and `modules/constant_base.srp` are retained under `05-modules/_support/`.

Do not remove existing copyright notices. Review additional third-party material and its license before merging it.
