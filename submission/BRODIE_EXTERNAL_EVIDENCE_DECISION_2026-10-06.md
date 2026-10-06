# Brodie external-evidence submission decision — 2026-10-06

## Decision

Do **not** merge the Brodie external reanalysis into the RC6 initial submission.

Keep it as a fully reproducible external-evidence branch that can be used if editors/reviewers challenge transferability or ask whether the multi-site spatial pattern appears outside NAAMP.

## Why not merge now

1. The primary held-out-season alignment result is positive and useful, but the source article was already known to report cross-site consistency for some species. The analysis is row-outcome-blind, not literature-blind.
2. The three-site design cannot reproduce the NAAMP ten-stop concentration endpoint or its fourth-through-tenth-stop heavy tail.
3. The stronger secondary prediction was not supported: high-activity nights did not consistently increase historical-best-site share.
4. Same-night rainfall did not strengthen or weaken template alignment.
5. Adding this analysis would lengthen and complicate a manuscript whose main contribution is already narrow and conditional, without materially increasing conceptual novelty.
6. The current RC6 manuscript already includes FrogID as a limited cross-dataset consistency check and explicitly states that full external transferability remains untested. That boundary remains scientifically cleaner for initial submission.

## What the branch is good for

If a reviewer says:
- “this is a NAAMP-specific artifact,”
- “the site-history pattern may not transfer,” or
- “broad activation should homogenize site use,”

the branch provides a direct response:

> In an independent Australian fixed-site acoustic dataset, species-specific site allocation learned only from the first wet season remained positively aligned with multi-site chorus allocation in the held-out second season (median A = 0.0277; species-block bootstrap 95% CI 0.0053–0.1652), and increasing total chorus activity did not measurably reduce that alignment.

Use the result as **external corroboration**, not independent preregistered confirmation.

## Current authority

Initial submission remains the existing RC6 main branch and scientific lock.

External evidence is isolated on:
- branch: `external/brodie-chorus-validation-v1`
- contract: `external/BRODIE_2025_EXPANSION_WITHOUT_HOMOGENIZATION_CONTRACT_V0_1.md`
- script: `external/run_brodie_2025_expansion_without_homogenization_v0_1.py`
- receipt: `external/BRODIE_2025_EXPANSION_WITHOUT_HOMOGENIZATION_RECEIPT_V0_1.json`
- novelty reassessment: `external/NOVELTY_REASSESSMENT_AFTER_BRODIE_2026-10-06.md`

## Bottom line

The external result increases confidence in the biological direction, not the paper's conceptual novelty. The best submission strategy is therefore to preserve it as reviewer-facing reserve evidence rather than reopen the initial manuscript.
