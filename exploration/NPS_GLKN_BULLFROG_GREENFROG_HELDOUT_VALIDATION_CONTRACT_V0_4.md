# Independent NPS acoustic partner portability test — frozen outcome contract v0.4

Author timestamp: 2026-10-22, **before inspecting any expert-annotated frog calling response values** from the verified NPS 2016–2023 source CSV.

## Rationale and population

The NAAMP result (2011? no — original NAAMP monitoring 2001–2015) was that the location of American bullfrog `Lithobates catesbeianus` adds geographic-route-heldout predictive information on where green frog `Lithobates clamitans` is heard, beyond static NWI wetland/PEM, strictly earlier species×physical-SiteID calling history and generic other-calling richness. Both retrospectively negative partners `Anaxyrus fowleri` and `Hyla versicolor` were **not** independently predictive after adding bullfrog; no direct species interaction or competition was proven.

New independent NPS GLKN acoustic monitoring resource (NOT NAAMP):
- Official NPS DataStore reference **2320505**, 2016–2023; source-only verified file ID **763377**.
- Original acoustic annotation CSV **68,581,307 bytes**, SHA256 **b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2**.
- Original authoritative metadata XML **131,226 bytes**, SHA256 **a37af87cd333168f52503f823041c4ab578b6968333c7d5f315604222ae4eb8f**.
- **147,913** taxon-by-recording rows, **16,561** unique recording files at **66** park×station sites across 7 parks; **13** distinct `ScientificName` label categories.
- Within the source, **12,499** recording files across **50** stations / 5 parks have EXPLICIT rows for both `L. clamitans` and `L. catesbeianus`; this is sampling availability, not co-calling.
- **4,121** explicit joint-row events also include `Anaxyrus fowleri` (2 parks); **12,376** include `Dryophytes versicolor` (5 parks; taxonomic name corresponding to NAAMP *Hyla versicolor*). Negative partner tests **secondary only**.
- Most NPS recordings include 7–11 surveyed taxa rather than the global 13; complete per-park target species sets occur in **5,550** recordings, among those **4,950** have the bullfrog+greenfrog explicit rows. Never impute missing taxon rows as nondetection.
- Recorded `Hydroperiod` in `Permanent`, `Semi-permanent`, `Ephemeral` regimes, with no per-file cross-taxon disagreement. `AvgTemperature_C` exists in the frog file but ~11.5% of recordings lack it. Do NOT ingest 282MB hourly temperature file to retune availability.
- The public NPS metadata defines `ManualCIV` (call index 0–3) as expert-assigned; `SurveyorDetectedStatus` YES/NO is independent confirmation label. `FileName` identifies one recording window, not a frog individual or breeding outcome.
- The same station-date typically has ONE recording, and none of the 12,499 bullfrog+greenfrog opportunities is part of a station-date group of ≥3. Hence **not** an NAAMP ten-stop or within-night network reallocation replication; use point-recording-level predictive association only.

Source-only receipts from [Actions 39722310835](https://github.com/zuizui0223/frogcs/actions/runs/39722310835), [39722811424](https://github.com/zuizui0223/frogcs/actions/runs/39722811424). The named pair and outcome rules are frozen below before readback.

## Outcome and source QA before fitting

- For **each FileName×ParkCode×SiteLocation×StartTime**, require one unique row for green frog and one for bullfrog, no duplicated taxon key and valid year 2016–2023.
- Primary **manually scored acoustic presence** `ManualCIV>=1` versus `ManualCIV=0` for both taxa. Accept **only literal numeric 0,1,2,3**; null/unparsable is *missing*, NEVER zero. In the same complete-case recording, both species must have valid manual scores.
- Expert `SurveyorDetectedStatus` may be `YES`, `NO`, or unknown; compute the observed discordance between valid manual `ManualCIV>=1` and manual status YES. **Gate:** at least 90% of otherwise eligible pair rows must have valid manual values; of those with a binary status present, discordance must be ≤1%; if not, label `measurement_QA_inconclusive` and do not promote any scientific result. No alternate outcome swap after seeing status.
- Recording-level valid mean ambient temperature `AvgTemperature_C` between **−20°C and +45°C** required. Other temperatures dropped as unmeasured.
- At least **1,000 complete paired recording outcomes**, **150 green-frog positive recordings**, **100 bullfrog positive recordings**, at least **20 independent sites**, **2 park units**, **100 positive bullfrog recordings across at least 10 distinct sites**. Otherwise `insufficient_outcome_information`, no claim that bullfrog has no effect.
- The detector vs expert difference is described but detector status is *never* substituted for missing manual labels.
- Exclude only if these frozen rules fail. Report denominator waterfall and site/park/year-specific outcome availability. No row selected by co-calling effect direction.

## Fixed independent-site predictive comparison

Unit: a **recording event** with valid manually annotated both-frog scores. Response Y=green frog ManualCIV≥1, predictor X=bullfrog ManualCIV≥1. This is a test of *same-recording acoustic association*, not prospective forecast of bullfrog location or causal detection of other frogs.

- Deterministic **site-disjoint A/B split within each ParkCode**, defined from SHA256 sort of ParkCode:SiteLocation identifiers; alternating 5 site locations per fold within the five source eligible parks. Every recording from the same park×site stays in one fold, including all years.
- M0 predictors frozen:
  - intercept;
  - ParkCode dummy variables with lexicographically first park baseline (site-disjoint folds contain all eligible parks if possible);
  - Hydroperiod one-hot with `Ephemeral` baseline (`Permanent`, `Semi-permanent`);
  - year `(EventYear−2019)/5`;
  - annual season `sin(2π×DOY/365.25)`, `cos(2π×DOY/365.25)`;
  - clock time `sin(2π×hour/24)`, `cos(2π×hour/24)`;
  - `AvgTemperature_C/10` (unit 10°C).
- M1: all M0 predictors **plus** observed bullfrog ManualCIV≥1 in the same recording.
- Both models use `sklearn.linear_model.LogisticRegression` with identical fixed L2 penalty `C=1.0`, `solver="lbfgs"`, `max_iter=500`, `class_weight=None`. No hyperparameter search or model rescue.
- Train separately on fold A → score fold B, and on B → score A. Require ≥50 green positives, ≥30 bull positives in **each training fold**, and at least 100 valid recording events in each heldout fold (otherwise `insufficient_training_fold`).
- Outcome: mean heldout **Bernoulli log-loss improvement M0−M1** (positive means partner improves prediction) in nats/recording; route/site-block bootstrap **2,000 replicates**, seed **2840337**, resampling entire ParkCode×SiteLocation blocks with replacement, report 95% CI and observed fold-wise scores. Report Brier score improvement as a separately fixed companion.
- A **transferable positive association** candidate requires mean gain>0, site-bootstrap 95% CI lower>0, *both* heldout fold mean gains>0, and positive fitted bullfrog coefficient in **both training folds**. Explicitly report observational and post-discovery independent source, not direct species–species attraction.
- **Site-level confounding sensitivity:** On the exact same complete-case data, fit a logistic regression of green presence on bull presence + site fixed effects + year, annual and clock season and temperature, with cluster-robust covariance at ParkCode×SiteLocation, if model is identifiable and ≥15 sites have both bullfrog positive/negative recordings. Test only the bullfrog coefficient sign/CI; no causal claim, no replacement of primary heldout decision.
- **Complete park-panel sensitivity:** repeat M0/M1 exactly on those full-panel recordings identified solely by the source taxon-row metadata (a response-blind selection); compute heldout gain and CI. Do not swap it for primary when primary fails.
- **Strong calls secondary:** ManualCIV≥2 response/predictor in same complete cases, but require ≥100 positives of each and ≥20 sites, otherwise underpowered. Never replace primary.
- **Negative partners secondary:** fixed `Anaxyrus fowleri` and `Dryophytes versicolor` only where a valid expert ManualCIV row exists, as separate candidate predictors on top of bullfrog: no new species replacement or direction search. If one lacks ≥60 manually positive source recordings over ≥10 sites, do not attempt its incremental test. Report BH over at most these two predefined comparisons, but never make these primary if positive pair fails.

## Interpretation and critical missing links

A positive same-recording bullfrog indicator may capture a shared temporal calling window, unresolved local weather, the same microphone sensitivity, acoustic masking and predator/wetland context; **the two species need not be actively interacting**. NPS `Hydroperiod` is a broadly assessed water-regime category **not aquatic macrophyte cover**. Predator fish/invertebrates and plant species identities are not in this release, so no trophic mediation can be identified.

Original NAAMP coefficients and nulls are not transferred. A positive NPS result would be an independent observational replication of **conditional acoustic partner information**, not an independent proof of NAAMP's specific spatial checkerboard mechanism. A negative or inconclusive result does not invalidate the NAAMP descriptive pair network because protocols and temporal grains differ.

## Immutability

The NPS exact file SHA and program version are fixed. Never commit raw NPS CSV, raw recording file identifiers or personally identifying field data to the repository; output only aggregate model/QA receipts. No RC6/main/author-submission modifications.
