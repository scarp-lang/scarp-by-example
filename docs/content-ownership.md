# Scarp content ownership and safe migration

| Repository | Primary responsibility |
| --- | --- |
| [scarp](https://github.com/scarp-lang/scarp) | Compiler implementation, regression `.srp` / `.stdout` fixtures, technical designs and release evidence |
| [scarp-docs](https://github.com/scarp-lang/scarp-docs) | Public language reference, installation, CLI, and official English/Hindi guides |
| [scarp-by-example](https://github.com/scarp-lang/scarp-by-example) | Runnable numbered lessons, byte-exact stdout fixtures, projects, labs, exercises and bilingual explanations |

## Migration checklist

1. Read the immutable, **published** compiler tag and exact release source commit recorded in [compiler-target.json](compiler-target.json). Retain historical provenance under [compiler-target-alpha4.json](compiler-target-alpha4.json) for older migrated fixtures. Unreleased compiler-main features must not be advertised here as shipped.
2. Copy each complete `.srp` / `.stdout` pair from that tag into a numbered lesson. Keep the compiler's original fixture: it remains necessary for regression testing.
3. Add an entry to the chapter's `README.md` table and one matching `### NN · ...` entry to `docs/hi/<chapter>.md`, with exactly one source link, one stdout link and an `**अभ्यास:**` exercise.
4. Link the public official reference in `scarp-docs` to the runnable example and back. Do not silently change historical compiler documentation, tags or release evidence.
5. Run the repository's real-compiler `verify` and `exec` checks with byte-exact stdout, the static Pages build, Hindi-coverage checks and CI before merging. The [alpha.4 manifest](migration-provenance.json), [alpha.5 manifest](migration-provenance-alpha5.json) and [source-provenance verifier](../scripts/verify_migration_provenance.py) independently require every copied `.srp` and `.stdout` to match its **original** published compiler checkout byte-for-byte.
6. Preserve old GitHub links and published URLs until all inbound references are audited; do not bulk-delete source fixtures or specs.

## Published alpha.4 migration cohorts

The initial examples [temperature softmax](../examples/06-ai-foundations/12-temperature-softmax.srp), [cosine similarity](../examples/06-ai-foundations/13-cosine-similarity.srp), and [sampled cumulative area](../examples/06-ai-foundations/14-sample-cumulative-area.srp) were copied with their expected outputs from compiler tag [v0.0.6-alpha.4](https://github.com/scarp-lang/scarp/tree/v0.0.6-alpha.4/examples), exact release commit `f04be0758cbce405ddcdb229699b0ff83c09d207`.

### Additional source-preserving examples

- [Sampled calculus](../examples/04-collections/13-sampled-calculus.srp) and its `.stdout`: originally `examples/sampled_calculus.srp` in published tag `v0.0.6-alpha.4`, which prints `9.0` and `[2.0, 2.0]`.
- [Top-K ranking](../examples/06-ai-foundations/15-topk-ranking.srp) and its `.stdout`: originally `examples/topk_scores.srp` in the same tag, which prints deterministic original indices, corresponding values, probability-ranked indices, and an empty `integers` result.

The original five alpha.4 migrated fixtures are checked against the historic alpha.4 checkout and **also executed** under the new pinned alpha.5 compiler. Two additional alpha.5 fixtures—[Pearson correlation](../examples/04-collections/14-pearson-correlation.srp) and [Top-P selection](../examples/06-ai-foundations/16-nucleus-selection.srp)—are checked against alpha.5 using the [new manifest](migration-provenance-alpha5.json). All seven pairs keep their original compiler-side regression sources and exact output fixtures; no older tag is rewritten.
