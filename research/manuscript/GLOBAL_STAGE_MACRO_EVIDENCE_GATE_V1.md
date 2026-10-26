# Global stage-geography macro module — evidence gate for a single frogcs flagship

**Date:** 2026-10-26. **Observed data, exploratory, not a new stage-specific trophic mechanism.** This is a source-preserving interpretation of existing executed full-scan [GloBI × GBIF audits](../results/FULL_GLOBAL_GLOBI_GBIF_STAGE_TESTS_2026-10-25.md). All core numbers must be drawn from the pinned result JSON files rather than estimated from prose. It belongs in the combined paper as **independent macroecological observation and specificity countertest**, not as a replication of the NAAMP acoustic result or INBO larval result.

## M0 — full source food-web stage labels (topology of reported relations)

- Fixed GloBI v0.11 dated 2026-09-10; source DOI [10.5281/zenodo.22691479](https://doi.org/10.5281/zenodo.22691479) and MD5 `8212776b7ba0c4fa8de26a00b5ce8595`.
- **24,453,954** indexed source rows scanned, **77,720** amphibian/odonate/aquatic beetle focal food-web rows.
- After explicit non-self species and canonical-stage QA, **1,240** source rows with both certain life stages; **881** distinct directed species-stage patterns from **768** directed species pairs. Stage-source DOI coverage is only three source dataset DOIs.
- **29** opposite-direction species pairs are unverified literature/database candidates. Not 29 independent observed aquatic trophic reversals, nor a worldwide reversal frequency.

## M1 — source-stage reporting phase, not interaction

The initial 61-species source-selected experimental 2026-08 GBIF Anura/Odonata parquet scan produced **4,026,251** quality-filtered occurrences, with **1,253,335** stage-labelled rows and 18 GloBI source links having both taxa/stages in the subset. The stage-specific 1° grid×year×month comparison used the actual reported stage labels, not model-imputed larval biomass.

- **17/18** had at least one exact grid-year-month joint report.
- **16/18** exceeded the mean of their own 11 cyclic month-shift comparators at ≥1 observation per stage-month; pooled observed joint cells **16,605**, summed shifted average **6,804.818**. At ≥5 stage reports, **12/14** pairs with shared grid-years exceeded their shift average.
- This is a **12-phase descriptive diagnostic**, with minimal phase-rank resolution 1/12, not a robust randomization p-value. Original source/predation links and GBIF same-grid co-reporting come from heterogeneous sighting effort. **Seasonality shared by unrelated taxa** may explain much of the result.

## M2 — ecological partner-specificity countertest (critical negative control)

The expanded 2026-08 GBIF Anura/Odonata stage partition contains **78** eligible GloBI directed stage patterns; 77 have both-stage GBIF reporting. Of these, **56** have ≥2 comparator prey species from the same guild/stage and matched reporting volume and geographic coverage; 35 distinct source predator species.

- At ≥1 report/stage/gridmonth, focal known-database-link phase ratio exceeded median alternative prey for **31/56**. Median focal-minus-alternative ratio **+0.090459**.
- At ≥5 reports/stage/gridmonth, this fell to **26/56**, with median focal-minus-alternative **−0.018509**.
- Alternatives are **undocumented in the fixed complete-stage GloBI subset**, not proven non-prey, and comparisons are post-readback/exploratory.
- The near-even 31/56 and below-half 26/56 diagnostics **do not establish robust stage-dependent prey-specific phenological matching**; do not select the exploratory positive mean while ignoring the negative strict median and source/effort bias.

## M3 — environmental context alternative, not verified wetland mechanism

In an EarthEnv 2014 static regularly flooded-vegetation-background comparison, **32** source stage edges had both source-validated near-zero versus high flooded-background contrasts at the ≥1 threshold; median high-minus-nearzero **−0.028117** for focal minus matched prey reporting phase ratio (20 predator taxa). The 1° and static background cannot measure live emergent-stem biomass, pond hydroperiod, or actual attacks. No robust biotic-specific flooded vegetation interaction was identified.

The source-pinned WorldClim historical 2010–2024 1° monthly rain match also documented **10/15** eligible pairs with positive within-grid-year co-report-minus-single report precipitation means (median **+3.376 mm/month**). This monthly co-report association is not the 72-hour NAAMP rain pulse, a field water-depth measurement or a predation effect.

## Manuscript claim boundary and placement

**Supported:** world-scale biodiversity database observations are strongly structured by season and life-stage labels, including overrepresented exact-calendar co-reports relative to simple cyclical phase shifts.  
**Not supported:** an excess unique to documented predator–prey pairs after stage/guild/coverage comparison; a measured pond-stage trophic flux or spatial timing mechanism; a global relationship between NAAMP rainfall-induced chorus and any larval predator population.

In the integrated frogcs manuscript, put these as **Results `3.4** and Discuss as a *constraint against inferring trophic specificity from generic seasonal co-occurrence*. This is a separate geographic/generalization lens and strengthens inferential discipline. **It is not a third empirical confirmation of a predator-suppression mechanism.**

## Source paths and audit priority

- [Full-source Pinned GloBI × GBIF stages](../results/full_globi_2026_stage_gbif_grid/observed_results.json).
- [Source-wide month-shift descriptive null](../results/month_shift_globi_gbif/observed_results.json).
- [Matched alternative-prey specificity test](../results/expanded_stage_specificity/observed_results.json).
- [EarthEnv matched wetland-background contrast](../results/earthenv_gbif_matched_stage/observed_results.json).
- [WorldClim within-grid-year month comparison](../results/globi_gbif_rain_contrast/observed_results.json).

**Evidence licensing:** if species-stage source selection, GBIF interpretation, DOI-pinned GBIF data, sampling effort, or partner identity validity are not externally audited, all patterns retain the status **post-readback exploratory stage-reporting associations**. Never use this module to upgrade the unmeasured G2 mechanism gate.
