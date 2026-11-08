# G18b — Frozen original-USGS adult-call versus tadpole/larval observation analysis, pending codebook eligibility

**2026-11-08 JST. Fixed after examining source IDs, years and field names only, before inspecting any species-specific call/tadpole response values.** Source: USGS Glorioso & Waddle (2025), DOI **10.5066/P9T71JCO**, CC0, original ScienceBase item **5eb5880c82ce25b5135ae784**. G18 original 7 CSV files were successfully acquired via GitHub Actions #42440852240 and byte SHA256s are recorded. This is **a separate USGS survey from the original NAAMP frogcs study**. The original G17b predictor-background analysis is completed and must not be retroactively changed.

## Source-only support known before response opening
- Exactly **2,221** dated Sample_Data rows with unique \`Sample ID\`, 70 physical sites and 2008–2016 coverage.
- Exactly **2,222** vocalization rows (one Sample ID not in the sample metadata); **1,055** tadpole/larval rows (one Sample ID not in the sample metadata).
- Exact adult vocalization↔larval table Sample ID overlap is **1,054** identifiable sampling events, across **64 physical sites**, **230 distinct physical site×year units**, restricted to **2012–2016**. Earlier 2008–2011 acoustic records must not be called paired larval surveys.
- **13 exactly named overlapping frog species** across both response table *headers*, with \`_In\`/\`_Out\` vocalization subcolumns. Unresolved pooled/species-group larvae and \`Ambystoma opacum\` without corresponding call species **must never be assigned to a named frog**.
- Sample ID anomalies outside the Sample_Data master are checked and reported; never date/site-join orphan response samples by nearest location.

## Codebook gate for genuine negative/detection opportunities

Only after checking the official **ATCH_Metadata.xml** source dictionary: for each source Species_In/Species_Out and tadpole column, determine whether 0 denotes survey-completed non-detection, \`NA\` denotes missing or not assessed, and positive numeric or categorical codes denote detection. **Do not equate structural blanks, absent sample IDs, unmatched species or no effort with absence**. If official methods do not establish the non-detection convention, mark \`NEGATIVE_OPPORTUNITY_UNVERIFIED\`, do not fit binary acoustic→larval occurrence models, and report descriptive co-reporting among positive records only. If the two modalities are not at the same site/date/sample, the matching gate fails; no nearest coordinate join.

If explicit 0/1/count coding is supported by the source, the *only primary field endpoints* are:
- \`acoustic_present_in\`: documented positive call index/count for the exact named species's \`_In\` column at that original Sample ID, with explicit 0 as a completed non-detection. \`_Out\` is **secondary sensitivity**; its spatial scope differs and is not combined with \`_In\` without an explicit source justification.
- \`larva_detected\`: documented positive original tadpole/larva record for the exact named species at the **same original Sample ID** (for contemporaneous detection test), or a strictly subsequent Sample ID with date later in the same original site×calendar year (for temporal test).
- \`acoustic_present_in_or_out\`: secondary survey-radius sensitivity only after the \`_Out\` codebook is clear.

## Frozen primary contemporaneous same-event test (not a survival or lag model)

Universe = complete source-known 1,054 paired events × 13 exactly named taxa, but include each event×taxon only if **both** original coded modality observations are explicitly comparable and either 0 or positive with documented sampling opportunity. Record all excluded/missing counts by reason; do not deduce zeros from records not in the tadpole table.

Report full 2×2 counts (acoustic 0/1 vs larval 0/1), exact both-positive, acoustic-only, larva-only, both-explicit-negative, separate per-taxon and 64 site-level support, and site-block resampled risk difference \(P(\mathrm{larvae\ detected}|\mathrm{call\ detected})-P(\mathrm{larvae\ detected}|\mathrm{explicit\ call\ nondetected})\) with 10,000 source-site-cluster bootstrap draws (seed 20261108). If either call class has fewer than **20 independent source site×species units** or fewer than **10 positives and 10 negatives in the actual larval endpoint**, report \`NOT_ESTIMABLE\`, not a favorable estimate.

No ecological attribution from same-event adult calls to prior egg survival is allowed.

## Frozen secondary strictly earlier adult call → later larval recorded-presence predictive test

The sampling unit is **site×species×calendar-year** (not individual repeated site nights). From **all** original larval survey samples in each site/year/taxon with a complete non-detection opportunity, choose *the chronologically earliest larval sample with at least one earlier completed acoustic survey at the same physical site and year*, strictly \`date(acoustic)<date(later larva)\`, independent of larval outcome. Outcome is detection at that first qualifying larval sample. Exposure is **any positive** \`_In\` call among the strictly earlier completed acoustic surveys, and separately count the number of prior acoustic opportunities. Source visits on the *same day* are not considered prior. Keep all undetected larval outcomes and species with original qualified opportunities, with counts/denominators reported by species/year/site before fitting.

Compare two fixed ridge-logistic (\`C=1.0\`) models at **five deterministic leave-original-site-group-out folds** (stable SHA256 alphabetical source-site rank mod five):
1. \`M0\`: species categorical fixed-effect indicators, year categorical indicators, first eligible larva sample day-of-year (scaled using training folds only), \`log1p(previous completed adult-acoustic samples)\`.
2. \`M1\`: \`M0\` plus exactly one \`any prior adult call\` binary feature.

Both models get **identical heldout rows and folds**, with *no* site-ID categorical predictor that leaks unseen sites, no test-outcome missingness selection and original source species/year retained. Primary numerical evaluation: site-equal-weight Brier gain \(\mathrm{Brier}(M0)-\mathrm{Brier}(M1)\), plus heldout log-loss difference; report actual original sites/years/calls/larvae. Bootstrap 10,000 physical sites (seed 20261108) resampling original paired out-of-fold site summaries; clearly this is a conditional-on-fit source-site bootstrap, **not** a prospective independent test. Require ≥25 physical sites, ≥50 site×taxon×year opportunities and at least 10 later-larva positive and 10 explicit negative outcomes across eligible test rows; otherwise classify predictive stage bridge **INELIGIBLE** with original denominator table. Original 2012–2016 support permits temporal 2015–2016 holdout only if both classes ≥10 with ≥10 physically independent sites and prior years include both response classes; report it regardless of direction, no time-window optimizing.

## Inference and publication stop

A positive same-event association is *method/detection co-reporting*. A positive lagged predictor indicates a statistical link from **recorded adult calling** to **later stage detection**, not individual frog survival or causal recruitment. No recorded Odonata larvae abundance, actual salamander predation, pond submerged refuge manipulation or model 4-sign quantitative calibration follows. The two original modalities can both be controlled by unmeasured site/season/effort. An odds ratio cannot transform model log larval cohort abundance into natural call intensity without an independent likelihood or demographic link.

Keep G8/G11 model-family positive replication, G13 synthetic ABC selection, R1 NAAMP associations, and G5/G7/G14/G15 non-support. Do not change the *Ecology Letters* manuscript's Results from a newly found external data source unless both source-outcome eligibility and fixed biological analysis evidence actually pass. No original USGS response values, sensitive coordinates or personnel names should be committed to the public repository by default.
