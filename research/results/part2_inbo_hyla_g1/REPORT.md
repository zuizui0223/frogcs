# INBO cross-stage empirical G1 — site-only improvement, failed temporal transport

**Date:** 2026-10-26. `frogcs` research branch, candidate future integrated manuscript Part II. **EXPLORATORY independent source**; no update to RC6. [Result JSON](observed_results.json) | [locked before effects](../../INBO_HYLA_ACOUSTIC_TO_LARVA_G1_FROZEN_2026-10-26.md) | [reproducible code](../../scripts/inbo_hyla_acoustic_to_larva_g1.py) | [GitHub Actions success](https://github.com/zuizui0223/frogcs/actions/runs/40211162054).

## 1. What was genuinely joined

Two CC0 INBO Meetnetten.be sampling-event archives, [adult chorus DOI 10.15468/d4bu8j](https://doi.org/10.15468/d4bu8j) and [larvae/metamorphs DOI 10.15468/swgure](https://doi.org/10.15468/swgure), downloaded as actual original ZIPs and source-SHA256-verified. Publisher event-level `locationID`, year/date and independently matching `locality` labels were used. No blurred coordinates were used for proximity joins, and no confidential original location identifiers were written to Git.

- General cross-protocol G0: **96** identical source `locationID`; **247** same-location-year pairs with adult chorus sampled before larval census.
- Response-blind G0.1 species eligibility: `Hyla arborea` **245** qualifying site-years at **93** locations, `Pelobates fuscus` only **2** site-years at **2** locations — the latter fixed non-estimable **before opening outcomes**.
- Valid `Hyla` pairs include **212** recorded prior adult call-present vs **33** explicitly surveyed non-calling site-years; later first available explicit-larva census had **149 present** and **96 absent** outcomes. Years 2016–2025.
- These are **published monitoring site identifiers**, not field re-surveys or confirmed within-pond movement paths. Any physical-waterbody ambiguity and incomplete independent stage-detection effort remain potential bias.

## 2. Frozen G1 forecast comparison

Predictor was **any recorded adult `Hyla arborea` chorus before the first explicitly surveyed larval census** in the same source-location/year. Outcome was **source-recorded larval occurrence `present` versus `absent`** at that census. True unsurveyed cells were **never** turned into zero.

The baseline model M0 had year, first larval census day, gap since last adult survey and number of previous adult-calling surveys. It did **not** have measured hydroperiod, prey/predator abundance, pond surface or numerical larval sampling effort in the final complete cases (see measurement QC below). The source-code internal label `M0_time_hydrology_recording` is **not a claim hydrology was fitted**; its `model_config.use_permanent=false` and `permanent_water_coverage=0` are authoritative. M1 added one binary strictly prior adult chorus signal. Both models used the exact same 245 rows and five-group held-out-site logistic CV, no tunable species or detection threshold.

| Primary out-of-site comparison (93 site groups) | M0 observed timing/recording | M1 + prior adult chorus |
|---|---:|---:|
| Brier loss (lower is better) | **0.25823** | **0.24271** |
| Log loss | **0.71875** | **0.69377** |

- Brier improvement: **+0.01552**, station-balanced bootstrap 95% interval (conditional fixed out-of-fold predictions) **+0.00112 to +0.04465**; the uncertainty scheme is not a refitted or truly prospective sample replication.
- Log loss improvement: **+0.02498**, 95% site bootstrap interval **−0.00794 to +0.09625**. Thus even the main source-held-out gain is metric- and uncertainty-dependent.

**Crucial counterweight, frozen time holdout 2024–2025 (35 rows, 34 sites):**

| Future-year holdout | M0 | M1 + prior chorus |
|---|---:|---:|
| Brier | **0.27839** | **0.34786** |
| Log loss | **0.75061** | **1.00915** |

**M1 was worse** by **0.06947 Brier** and **0.25855 log loss** in the later years. This defeats a claim of **stable temporally transferable added acoustic-to-larva predictive information** under this frozen linear-year learner. The observed contradiction is retained, not tuned away with alternative years, predictors or thresholds.

## 3. Water/effort and ecological identification limitations

Direct event-level measurement audit found that **all 245 eligible first explicit-larva site-year rows lack a coded `permanent water column` covariate at that exact survey event**. The broader INBO larval data dictionary contains that measurement type, but *having a field somewhere in the dataset is not having its value for these matched observations*. The model baseline is **NOT hydroperiod-adjusted**.

Categorical larval `sampling effort type` appeared in **165/245** records (67.3%), with 80 unknown. The G1 baseline as specified included number of prior adult surveys, date and year, but did **not** add the larval effort category or quantitative scoop counts. Remaining detection differences cannot be ruled out. This additional reporting audit was done after seeing the first source-heldout result and did **not** change fitted predictions.

No independent measures of frog egg or tadpole **survival**, larval predator **size/cohort density**, fish presence at these exact focal events, **summer dry-out and reflood** or predation attacks were used. A positively recorded adult chorus leading larval detection is stage-reporting linkage, not successful reproduction attributable to a particular adult, and not the cause of RC6's excess multi-stop configuration.

## 4. Biological conclusion and publication decision

- **Supported descriptively:** exact publisher-site repeated adult `Hyla` calling and later larval observations are jointly queryable in a real independent dataset, with a modest out-of-location predictive increment above recorded timing and adult survey opportunity.
- **Not robustly supported:** improvement beyond measured local hydrology (not observed on the focal sample), independent future-year transfer (actually worsened), predator-driven selection, age/size-stage mismatch, larval survival and drought-induced release.
- **Implication for the one combined frogcs manuscript:** G0 (source + site/time/taxon mapping) **passes provisionally** for stage reporting, G1 has a **limited mixed-predictability result**, but G2 mechanistic predation/hydrology **has not passed**. This cannot yet be folded into RC6 as an explanatory mechanism.

## 5. Next genuinely discriminating evidence

Prioritize original pond-year census including measured fish, *large overwintered tadpole* size/density and prey egg/tadpole survival with real summer dry-out dates. The public ESGR and St Marks Dryad original workbooks returned HTTP401 through GitHub runners, Mohonk original EDI CSV entities HTTP403; they are not refitted. A Mohonk GBIF IPT occurrence mirror was read (13,862 records) but **lacks source pond `locationID` and the EDI native chorus/egg/tadpole and water-quality fields**, so it cannot replace the paired EDI original for this target.

**No stand-alone RC6 publication is automatically activated.** That is now a conditional editorial backup option, with the research's one integrated manuscript route and an explicit checkpoint documented in [the dated decision](../../INTEGRATED_PAPER_DECISION_2026-10-26.md).
