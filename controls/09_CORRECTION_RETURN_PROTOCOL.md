# Required return and correction protocol

Every production session returns the following package. Evidence is cumulative and source-linked; no item may be silently omitted because it is blank, extrinsic, illegible, repetitive, or difficult.

## Artifacts

1. One standalone monolingual source-language Layer-1 TeX/PDF for each source witness role actually owned. Latin recensions remain Latin; Arabic witnesses remain Arabic; editor-authored German or modern material stays separately credited.
2. One independent standalone monolingual Layer-2 TeX/PDF per requested target language. Never return a bilingual, facing-page, or mixed-language reader.
3. One separately labelled Layer-3 critical apparatus with restrained numbered notes.
4. Raw figure/table crops and separate conservative presentation derivatives when editable reconstruction cannot preserve every visible relation.

## Ledgers

- `physical_unit_disposition.tsv`: every physical source unit, including blanks, covers, cards, stamps, and excluded matter.
- `source_alignment.tsv`: stable source anchor to output line/page/section mapping.
- `evidence_ledger.tsv`: claim, source coordinates, witnessed reading, reasoning, confidence, and artifact impact.
- `unresolved_readings.tsv`: bounded alternatives, source coordinates, image references, and confidence.
- `witness_variants.tsv`: witness/recension identity and non-silent variants; never collapse recensions.
- `critical_findings.tsv`: stable apparatus ID, issue class, diplomatic reading, faithful translation, proposed critical reading, required hypotheses, proof/counterexample/witness evidence, confidence, propagation impact, prior-notice result, and citations.
- `formula_table_ledger.tsv`: every formula/table anchor, cell/row/column coverage, verification state, and machine-readable companion path.
- `figure_provenance.tsv`: source unit, crop rectangle, raw/derivative dimensions, operations and parameters, SHA-256 hashes, insertion status, and render comparison.
- `proposed_corrections.tsv`: canonical anchor, current reading, proposal, exact evidence, confidence, affected languages/artifacts, and accept/reject state. A translation never edits canon silently.
- `language_synchronization.tsv`: target language, canonical source checkpoint/hash, source replay state, proposed-correction IDs, latest accepted canonical checkpoint, and propagation state.

## Checkpoint

Return these exact fields even when their value is `NONE`:

```text
canonical_source_checkpoint_sha256=
last_fully_transcribed_source_unit=
last_fully_verified_source_unit=
first_untouched_source_unit=
owned_units_total=
owned_units_disposed=
unresolved_count=
figure_count=
formula_or_table_count=
```

A session is complete only when `owned_units_disposed` equals `owned_units_total`, with no gap or overlap. Preserve superseded checkpoints with reasons and hashes.

## Build, render, and audit

Build deterministically twice from a clean output root and compare hashes. Render and visually inspect the first/last page, every seam, every figure, every flagged formula/table, every blank/colophon/trailing leaf, and representative dense/damaged pages. Return the build environment, command, exit state, warnings, page count, and render-sample ledger.

Run an independent cold audit from a new absent replay root. It replays source hashes, exact coverage, archive members, builds, renders, and all mandatory ledgers without patching the candidate. A failure freezes that candidate; repairs create a successor and rerun the entire audit. There is no human review gate.

## Multilingual QA loop

Each translation starts from a version-pinned canonical checkpoint and independently rechecks its owned source pixels. It routes possible canon errors through `proposed_corrections.tsv`. Accepted corrections create a new canonical checkpoint and propagate to every affected language edition while preserving release history. Later language passes are additional source checks, not substitutes for initial replay or independent audit.
