# v4.8 — Ocock 2024 original model grain, cohort coverage, and Gwydir source identity

**Audit 2026-10-09 JST.** Original-paper extraction, not a new biological analysis or confirmation of source-level availability. Independent study, **do not modify locked JAE RC6 `main`**. No frog response records, sensitive coordinates, new hydrology or signed data requests were obtained.

## 1. Original paper has THREE DISTINCT denominators

The published source [Ocock et al. (2024), *Managing flows for frogs*](https://doi.org/10.1071/MF23181), Results and Table 3, gives:

| Exact scientific grain | Source count | This is *not*... |
| --- | ---: | --- |
| All completed amphibian **site surveys** | **343** across **95 survey nights**, 29 physical wetland sites | A complete set of nightly ten-stop chorus matrices |
| Complete-case **calling / breeding-attempt** random-forest samples | **303** | All 343 original five-minute observations or species-specific CI values |
| Complete-case **metamorph / breeding-success** random-forest samples | **325** | The same 303 sites/dates as in the calling model |
| Sites / site-surveys with recently metamorphosed frogs among the five dominant flow-dependent species | **28 sites / 81 site-surveys** | A denominator of 81 total survey opportunities, evidence of individual breeding success or known event parentage |
| Survey samples by catchment (not guaranteed to be the model-complete subsets) | **195 Gwydir / 148 Macquarie** | 195 and 148 independent environmental pulses |

The **303** and **325** model sample sizes are separate complete-case outcome panels (with potentially different explanatory-variable sets). In the 343-visit frame, **40 visits are not in the full calling model and 18 are not in the full metamorph model**, but the *overlap and exclusions by year/site/treatment* have **not been reported as an authenticated record-level join**.

If and only if both complete-case sets are subsets of the exact same original **343 source visit IDs**, the simple set intersection is between **285** and **303** visit IDs. This mathematical bound is *not* their actual identified overlap, says nothing about **strictly prior chorus history**, and cannot link an earlier acoustic event to a later larval outcome.

The original results for the abundant flow-dependent group also state **recent metamorphs at 28 sites on 81 site surveys**; this reports positive observed follow-up stages, not an estimate of detection-adjusted breeding success or number of reproductive events.

**Research stop:** a frogcs follow-on requires a verified joined source view with species-level prior call category, a valid earlier survey opportunity/zero, true habitat/hydroperiod and later stage survey/date/effort. Group sums and published stage counts do not contain that sequence.

## 2. The published machine-learning split is NOT external site/year validation

Ocock et al.'s original Analyses specifies:
- **80% calibration / 20% validation** chosen by **conditional Latin hypercube sampling (cLHC)** to span the multivariate predictor range;
- Boruta predictor selection; **10-fold CV** for hyperparameter tuning and the authors also report **leave-one-out cross-validation (LOOCV)** model validation;
- published Table 3: calling model **303 complete cases**, LCC=**0.692**, R²=**0.48**; metamorph model **325 cases**, LCC=**0.686**, R²=**0.47**.

Nothing in the publicly described cLHC or LOOCV framework establishes that **whole physical wetlands, whole catchments, whole hydrological events, or entire calendar years** were withheld from training while predicting a truly untouched block. This is a **different prediction target**, not proof that the published model was fitted incorrectly or that its variable rankings are invalid.

A prospective frogcs transfer test therefore must evaluate:
- complete **held-out physical wetland** or **future year/hydrological event** blocks, not individual randomly chosen site×visit rows;
- source-authoritative **same-site same-night opportunity** and staged follow-up join;
- fixed original response encoding and environmental covariates before looking at test-year results;
- separation of predictability of a *guild calling sum* from the *conditional species×wetland spatial configuration*, and of metamorph presence/count from proven larval survival attributable to an earlier call.

Do **not** claim “the published R² is overoptimistic” without executing a source-authenticated independent blocked comparison. The methodological observation is strictly that *the reported design alone does not demonstrate block transfer*.

## 3. Critical same-region source mismatch: **15 ≠ 16 Gwydir sites**

Published [Ocock et al. (2024)](https://doi.org/10.1071/MF23181) used **15 Gwydir wetlands** (plus 14 Macquarie). The independently published [Sarker et al. (2022), *The effect of inundation on frog communities and chorusing behaviour*](https://doi.org/10.1016/j.ecolind.2022.109640) describes **16 five-year Gwydir frog monitoring sites**, plus **six dedicated flow-event acoustic recorder sites**. The [Commonwealth Gwydir 2021–22 report, Appendix I: Frogs](https://www.dcceew.gov.au/sites/default/files/documents/gwydir-river-selected-area-2021-22-annual-summary-report-appendix-i.pdf) likewise describes 16 Gwydir five-year frog survey sites for 2015–2019.

**These 15/16 are not a trivial typo to “fix” by silently merging:**
- There may be original frame/inclusion or site eligibility differences (unknown without source manifest);
- The six flow-response recorder locations are not necessarily the same as the original fifteen all-year frog census locations;
- The two projects' populations, periods, sampling intensity and the order/method of auditory vs visual protocols should not be assumed identical;
- Without the source original physical-site crosswalk, neither programme can reconstruct Ocock's per-site prior strong-chorus history or add independent test sites from Sarker;
- Overlapping government frog monitoring programmes are **not independent scientific replications** simply because they were analysed in different articles.

A minimal source request should **first ask for the source-authoritative inclusion/exclusion relationship between the 15 Ocock and 16 Sarker Gwydir sampling sites**, without requesting sensitive coordinates. A simple non-reversible match/unknown/excluded table or a yes/no count plus reason is sufficient for the *source feasibility* stage.

## 3B. Source-published taxon-specific spatial breadth is already heterogeneous — but it is *ever heard*, not strong history

The original Ocock Table 2 reports `Number of sites calling recorded` across **the entire 2015–2020 observation period**. Among its six flow-dependent focal taxa:

| Published flow-dependent taxon | Any calling recorded at how many of 29 wetlands (pooled years) |
| --- | ---: |
| `Crinia parinsignifera` | 27 |
| `Limnodynastes fletcheri` | 27 |
| `Limnodynastes salmini` | 14 |
| `Limnodynastes tasmaniensis` | 29 |
| `Litoria latopalmata` | 18 |
| `Litoria peronii` | 26 |

**This is real published taxon-level descriptive evidence.** It shows substantial heterogeneity in **cumulative reported calling-site breadth**, even among flow-dependent taxa. However, for the widely heard taxa a binary **ever-called-at-site** history is close to saturated; for `L. tasmaniensis` it is **29/29**, so it cannot distinguish historical `ever-called` sites from never-called sites in the same 29-site source frame.

frogcs's relevant modifier is **strictly prior, species-specific STRONG chorusing** at actual physical sites, not species being heard at any point from 2015 through 2020. The published Table 2 does **not** show the year-specific onset of those sites, relative historic strong chorus category, nights with simultaneous cross-site calls, or the presence of animals at silent sites. Therefore this table cannot replace the source visit×species original audio categories.

This matters biologically: a putative 'history' effect based merely on whether a taxon was *ever heard by 2020* would leak later detections into earlier events and, in several species, provide almost no within-assemblage site contrast. Treat Table 2 as **a preliminary choice of taxon breadth**, not an inferential temporal template.

## 4. A small, safe source-only decision package — no response rows required

Once an original custodian provides it, these **aggregate** items decide the right research question before species observations are inspected:

1. **Per catchment × source-defined night**: number of distinct physical wetlands with a completed five-minute auditory census; count of nights with ≥4 physical wetland opportunities inside one catchment rather than pooled across catchments. Existing [v4.7 catchment-night checker](scripts/audit_ocock_catchment_night_aggregate_v47.py) accepts such anonymized count metadata.
2. **Model-sample mapping, by original visit ID only, returned as aggregate counts**: number of eligible site-visits with original acoustic 5-minute data, with complete **calling-model** predictors, with complete **metamorph-model** predictors, and in **both panels**. Reconcile to published **343 / 303 / 325** while preserving reasons for missingness.
3. **Prior-coverage potential**: for each catchment-night without disclosing site ID or calling value, count distinct *currently surveyed* wetlands with at least one verified comparable **strictly earlier** five-minute frog census; report this jointly with ≥4 current sites. This is a *ceiling on evaluable prior-site history*; **not** evidence those earlier censuses had strong calls.
4. **Actual stage follow-up feasibility**: count site visits with true metamorph surveillance effort, and independently describe the authors' **81 positive observed** dominant-species metamorph site-surveys versus the full opportunity denominator; require plausible larval developmental lag and physical site crosswalk.
5. **Programme crosswalk**: verify whether the **15 Gwydir** wetlands in Ocock and the **16** in Sarker have consistent original names/aliases over 2015–2020 (without releasing protected fauna coordinates).

**Stop or downgrade the study** if this metadata shows that no catchment-night has enough source-observed same-species locations with prior opportunities, or if the only biological endpoints available are the published guild sum and sporadic later metamorph counts. It would still be possible to study narrower **within-site hydroperiod and guild abundance prediction**, but this is not replication of JAE RC6's route-spanning k≥4 taxon-specific historical chorus-site phenomenon.

### Status and provenance

- **Confirmed**: paper-reported totals and modelling design; separate published 15 vs 16 Gwydir site frames; 81 site-surveys with positive observed metamorphs in common flow-dependent taxa.
- **Not confirmed**: actual night-by-wetland array; historical prior-site coverage; calling/metamorph model visit-ID intersection; direct water and sound measurements; the Ocock–Sarker physical site crosswalk; access to complete registered BioNet systematic survey events.
- **No new ecological coefficient or field response** computed. No external email, paid request, special login or use of personal/sensitive location data. Submission-locked RC6 unchanged.
