# Ecology Letters first-shot — science freeze and submission handoff

**Frozen on 2026-11-08 (JST). Submission preparation only; not submitted to the journal.**

## Authority and version

- **Scientific source branch/commit:** `research/g18-usgs-independent-acoustic-larval-source-20261108` at `e6f6b941ff75e008658bdff0910868eb03e44673` (stacked through G12–G18; do not mistake the default `main` frog chorus RC6 for this separate food-web Letter).
- **Main scientific manuscript:** [R1–R4/G8–G18 integrated Letter](../../editorial/MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md), Git blob `571bd270b1e0100c5d5ef3995c9b479f8e54dc57`.
- **Supplementary information:** [S1–S20](../../editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md), Git blob `f5aa85c99a016432c7bdf9648cd4024f46d53012`.
- **Original cover-letter draft:** [author-side source](../../editorial/ECOLOGY_LETTERS_COVER_LETTER_DRAFT_2026-11-06.md), Git blob `c1da1aa2ec8eaa4bb4fbd0b1580023640e275c73`. The long draft contains private editorial notes and MUST NOT be uploaded to the journal verbatim.
- **Main figure masters (unchanged):** [four original PNGs and audited hashes](../../editorial/FOUR_FIGURE_SOURCE_ASSEMBLY_RECORD_2026-11-06.md).
- **Research evidence authority:** G12 [prior sensitivity](../../research/G12_ABC_POM_PRIOR_IDENTIFIABILITY_VERIFIED_RESULT_2026-11-07.md); G13 [conditional structural null](../../research/G13_ABC_POM_CONDITIONAL_STRUCTURE_NULL_VERIFIED_RESULT_2026-11-07.md); G14/G15 [field background sensitivity](../../research/G15_ABC_ACOUSTIC_SELECTION_SPECIFICITY_VERIFIED_RESULT_2026-11-07.md); G17 [failed numerical replay](../../research/G17_FAILED_ORIGINAL_DIAGONAL_NUMERICAL_REPLAY_2026-11-08.md) and G17b [post-hoc rank decomposition](../../research/G17B_EXACT_G15_ANCHORED_CROSSSWAP_VERIFIED_RESULT_2026-11-08.md); G18 [USGS independent stage observation](../../research/G18_USGS_INDEPENDENT_CALL_LARVA_OBSERVATION_VERIFIED_RESULT_2026-11-08.md).

## Frozen claims — editorial changes must preserve these signs and limitations

1. **Main ecological result:** in each of two disjoint 256-structure experiments crossed with all 27 synthetic rates, the vegetation-function manipulation increased the *model's four-sign compatibility* (+2.71/+2.75 percentage points) while decreasing mean *simulated* frog log-cohort abundance (−0.040/−0.041); these are not wild demographic effects. The relative excess-loss comparison after rate×context standardization was not supported (G10).
2. **Conditional positive outcome:** with independently manipulated salamander arrival and aquatic duration, the combined vegetation effect on frog cohorts changed from −0.186 (late/short) to +0.116 (early/long). Do not generalize this to all rates, habitats, or observed ponds.
3. **G13 structural selectivity:** 794/20,000 original synthetic proposals fulfilled four idealized signs; they represented 647 distinct food webs versus 711.93 under a rate/developmental-context-conditioned acceptance-label permutation null (p≈0.0002). This rejects structure-exchangeability *within the synthetic screen*, not uncertainty over the actual natural food web. G12 reweighting varied acceptance from 1.09% to 6.85%; the acceptance fraction is NOT a probability of a mechanism in nature.
4. **Field-prediction limits G14–G17b:** ABC source-template point improvement against a flexible environmental baseline is confined to uniform SDM background, not robust in target-group; the pre-fixed dual-background gates failed. G16 attributed 95.61% of cross-SDM discrepancy to mapped V0 sites; G17b points to the odonate/caudate source SDM ranks. The G17 numerical-replay gate **failed** and is not repaired retroactively by G17b.
5. **G18 independent observational bridge:** exact original USGS adult-call and tadpole-detection data: 1,054 survey samples at 64 sites, 13 species; larval detection 45/860 (5.23%) with within-plot adult calls versus 125/12,842 (0.973%) without (crude ratio 5.376). Earlier calls did not reliably improve unseen-site later-larval predictions and worsened fixed later-year forecasts. Co-recording is not cohort calibration, recruitment, causal predation, or individual survival.

## Three editorial inclusions are already present in the source

- **G13:** R2 Results and Discussion; SI S15. Structural selectivity, with identification limitations.
- **G18:** Discussion and SI S20. Positive same-survey observation and negative forward prediction, without bridging to modelled abundance.
- **G12 and G14–G17:** SI S14 and S16–S19 plus a brief background-dependence limitation in the main Discussion. Preserve the original G17 FAIL.

**Decision:** no additional G-series explorations, no revised priors, no new field-model calibration attempts, no post hoc search for more positive findings. Only formatting, reference hygiene, publisher-required metadata, archive/rights clearance, and coauthor review may modify the editorial packaging. Any later science analysis must be explicitly requested by reviewers and recorded as post-freeze.

## Journal and current upload gate

- **Journal/type:** *Ecology Letters*, original research **Letter**. Official [Author Guidelines](https://onlinelibrary.wiley.com/page/journal/14610248/homepage/ForAuthors.html): main text ≤5,000 words, abstract ≤150 words, at most six main figures/tables/boxes; double-spaced text and separate figures are accepted for first submission.
- **Current audited counts reported by candidate:** main scientific body 4,984 words (including headings); abstract 148; four main figures. Keep original numerical results and original figure PNG bytes unchanged.
- **Clean initial-submission files:** generate text-only Word copies plus four original figure PNG files and a full SI Word copy using the separate editorial-packaging workflow. This workflow **does not run a scientific simulation or retrain any model**.
- **MANDATORY EXTERNAL GATES BEFORE ACTUAL JOURNAL SUBMISSION:**
  1. Obtain verified corresponding-author name/affiliation/email and complete title-page metadata; secure affirmative approval of **all coauthors** and verify contribution, conflict of interest and exclusivity declarations. Never fabricate these.
  2. Assign a project-owned materials/code licence, and package third-party files under actual source-specific redistribution rights. Do not redistribute restricted raster/checklist/source files by default.
  3. Deposit the reproducibility material and metadata with a **permanent public archival DOI** accessible to editors/reviewers, as required by the journal, and insert the real DOI in the manuscript's data availability statement. The existing GitHub repository and source USGS DOIs alone are not the project archive DOI.
  4. Have authors inspect the publication-size four main figures and S1–S4 supplementary figures, verify reference list and rendering, then populate editorial/reviewer suggestions and upload via the journal's Research Exchange.
- **Actual journal submission status:** NOT SUBMITTED. The freeze does **not** certify author approvals, archiving, or journal receipt.

## Primary fixed QA evidence

- G18 original-source plus cross-method field/temporal analysis CI: [SUCCESS #42442037230](https://github.com/zuizui0223/frogcs/actions/runs/42442037230).
- G18 integrated 44-claim and SI structure QA: [SUCCESS #42442576563](https://github.com/zuizui0223/frogcs/actions/runs/42442576563).
- Four assembled source-backed figures and audit: [SUCCESS #42169682447](https://github.com/zuizui0223/frogcs/actions/runs/42169682447).
- [Source provenance and currently unresolved data/code rights](../../editorial/DATA_CODE_AND_REFERENCE_PROVENANCE_2026-11-06.md).

**Frozen manuscript conclusion (unchanged):** food webs that generate the idealized frog–predator signature do not necessarily benefit frogs; under early and long salamander aquatic exposure, vegetation can instead benefit frog cohorts. Acoustic patterns motivate the model but have NOT identified a wild trophic mechanism.
