# WFTS prospective weather and analysis specification v0.5

**Status:** frozen before receipt or inspection of any WFTS species × station × survey outcome matrix. Supersedes v0.3 before outcome access.

This document operationalizes the already-frozen external-replication endpoint for the first candidate network, WFTS.

## 1. Scope

Use only the **traditional Wisconsin Frog and Toad Survey** route design.

Exclude:
- phenology surveys;
- mink frog surveys;
- ad hoc records;
- route-runs that do not contain the complete permanent-site design required below.

No frog-response value may be inspected to alter these rules.

## 2. Spatial unit

Primary repeated unit:

`traditional RouteID × SurveyPeriod × Year`

Each eligible route-run must contain exactly 10 permanent listening stations.

For the primary confirmation, retain only matched comparisons for which all 10 physical stations can be verified as the same stations in both surveys.

If documented station replacement occurred between the two surveys, exclude that pair from the primary analysis.

Station coordinates may come from:
1. versioned WFTS station coordinates supplied with the response data; otherwise
2. archived official route maps/descriptions, provided historical station identity can be established without response values.

## 3. Weather product

Primary external weather product:

**Daymet daily surface weather, Version 4 R1**  
ORNL DAAC DOI: **10.3334/ORNLDAAC/2129**

Variables:
- daily precipitation (`prcp`, mm/day);
- daily minimum temperature (`tmin`, °C);
- daily maximum temperature (`tmax`, °C).

Rationale fixed before outcome readback:
- daily temporal resolution;
- approximately 1-km grid;
- continental North American coverage from 1980 onward;
- covers the full WFTS standardized period beginning in 1984.

Do not switch to PRISM, ERA5, station weather or another precipitation product after frog outcomes are inspected.

A different product may be used only if Daymet acquisition fails technically **before** WFTS outcome readback; that failure and replacement must be committed first.

### Daymet calendar handling

Use the official Daymet calendar semantics.

Daymet retains **February 29** in leap years and drops **December 31** so every Daymet year has 365 entries. Map WFTS Gregorian survey dates directly to the corresponding Daymet calendar date; do not apply a post-February leap-year offset.

Traditional WFTS surveys occur in April–July, so the omitted December 31 is outside the eligible survey window.

If a future external dataset contains a December 31 survey, that date is ineligible under this frozen Daymet implementation rather than being silently remapped.

## 4. Antecedent-rain metric

For every station and survey date:

1. Ignore precipitation on the survey calendar date.
2. Starting with the complete local calendar day immediately preceding the survey, count consecutive days with Daymet precipitation **< 1.0 mm/day**.
3. Stop at the most recent day with precipitation **≥ 1.0 mm/day**.
4. Cap the count at **30 days**.

Call this station-level value:

`dry_days_i`

The cap and 1-mm threshold are fixed before outcome data are opened.

### Route-run rainfall exposure

For each complete 10-station route-run define:

`rain_recency = mean_i[ log(1 + dry_days_i) ]`

across the 10 permanent stations.

Lower values are closer to recent rain.

Do not choose mean versus median after inspecting frog outcomes.

## 5. Temperature covariate

For each station/date:

`tmean_i = (tmin_i + tmax_i) / 2`

Route-run temperature:

`tmean_run = mean_i(tmean_i)`

Use Daymet temperature for all route-runs in the primary analysis, rather than mixing recorded and gridded temperature according to missingness.

Recorded WFTS temperature may be retained for descriptive/sensitivity analysis only.

## 6. Matched comparisons

Within every:

`RouteID × SurveyPeriod`

sort eligible complete route-runs by year.

Pair adjacent **observed eligible years**, matching the NAAMP discovery logic.

For each pair:
- the member with lower `rain_recency` is the wetter/closer-to-rain survey;
- the other is the drier survey;
- exclude exact ties in `rain_recency`;
- `rain_contrast = rain_recency_dry - rain_recency_wet`, positive by construction;
- `temperature_difference = tmean_wet - tmean_dry`;
- `day_of_year_difference = DOY_wet - DOY_dry`;
- `year_gap = year_wet - year_dry` in absolute elapsed years, with sign not used.

Do not select pairs based on frog richness, species identity, call index or concentration.

## 7. Prior-history requirement

The principal comparator requires strictly-prior history.

For a focal pair, use only eligible runs in the same traditional route and survey period with dates **before the earlier focal year** to estimate taxon × physical-station propensity.

Pairs with no strictly-prior eligible run are excluded from the principal confirmatory analysis.

A prior run contributes to the historical propensity only when at least **8 of the 10 focal physical SiteIDs** are represented, matching the frozen NAAMP prior-site implementation.

No future run may contribute to the historical propensity.

## 8. Frog matrix

For every eligible route-run construct:

`taxon × 10-station call-index matrix`

with:
- 0 = no recorded call;
- 1–3 = WFTS call index.

Primary concentration uses binary active status `CI > 0`.

Species nomenclature must be harmonized by a mapping frozen before endpoint calculation. Historical taxonomic-name changes are resolved by synonym mapping, not by dropping records based on response direction.

### Route × survey-period candidate taxon support

For each `RouteID × SurveyPeriod`, define the candidate taxon pool as the **union of taxa with CI > 0 in any eligible run of that same route and survey period across the complete eligible WFTS time series**.

This mirrors the NAAMP stratum-support rule.

The all-year union is used **only to define candidate support**. It does not provide historical probability weights.

All taxon × physical-station probability weights in the principal comparator remain strictly prior to the focal pair.

Do not use the statewide list of all Wisconsin taxa as the simulation pool at every route, because doing so would permit activation of taxa never observed in that route-period stratum and could artificially diffuse the comparator.

Do not replace this rule with a prior-only pool after outcome readback; a prior-only pool would mechanically exclude genuinely route-new taxa from the target survey.

## 9. Frozen concentration endpoint

For every taxon absent from all 10 stations in the drier/reference survey and present at one or more stations in the wetter/target survey:

- `k_i` = number of wetter stations with CI > 0;
- `e_i = max(k_i - 1, 0)`;
- `C_pair = sum_i choose(e_i, 2)`.

This score is zero through the second occupied station and increases as extra participation accumulates within the same recruited taxon at third-and-later stations.

Do not substitute a different concentration index after result readback.

## 10. Matched regression

Observed concentration coefficient:

`C_pair ~ rain_contrast + temperature_difference + day_of_year_difference + year_gap + SurveyPeriod`

Inference:
- OLS;
- cluster-robust covariance by `RouteID`.

SurveyPeriod is categorical.

No county, habitat, trait or species-pool covariate may be added after outcome readback.

## 11. Deterministic route folds

Reuse the **same deterministic route-fold logic** as the NAAMP cross-fit comparator.

If the implementation requires canonical route strings, use the WFTS RouteID rendered as a zero-padded/stable string and apply the existing repository fold function unchanged.

All stations from one route must remain in the same fold.

Do not rebalance folds based on frog outcomes.

## 12. Principal comparator

The confirmatory comparator must contain exactly:

1. taxon-specific rainfall response estimated only from the opposite route fold;
2. strictly-prior taxon × physical-station propensity;
3. focal drier/reference-state persistence with the same **a = 0.75** anchor used in the NAAMP principal joint comparator;
4. one common pair-level log-odds shift chosen so expected wetter total incidence matches the observed wetter incidence total.

No taxon × station-specific rainfall interaction is permitted.

No trait term is permitted.

No model family may be selected after outcome readback.

## 13. Simulation and conditional statistic

Generate **1,000 simulations** under the principal comparator.

For every simulation calculate:
- route-new-taxon rainfall coefficient;
- total extra-stop rainfall coefficient;
- within-taxon concentration rainfall coefficient.

Across null simulations fit the same conditional regression used in the NAAMP principal comparator:

`concentration_beta ~ route_new_taxon_beta + extra_stop_beta`

Primary test statistic:

`observed concentration beta - null-predicted concentration beta at the observed first-order coefficients`

Primary support gate:

> observed conditional residual exceeds the upper 95% null-residual bound.

Report plus-one upper-tail Monte Carlo P.

Failure to pass the support gate is **not by itself sufficient to call an informative non-replication**. Outcome interpretation follows the frozen informativeness rule below; no result can trigger endpoint/comparator retuning.

## 14. Minimum coverage gate

### Stage 1: response-blind structural gate

Before loading `taxon_key` or `call_index`, read only:
- RouteID;
- SurveyPeriod;
- SurveyYear;
- survey date;
- station order;
- physical-site identity;
- precomputed Daymet `rain_recency` and `tmean_run`.

Using only those fields, report:
- eligible complete route-runs;
- routes;
- matched pairs;
- pairs with strictly-prior structural history;
- deterministic route-fold sizes.

The confirmatory analysis proceeds to response loading only if:
- **≥ 30 traditional routes** contribute to the principal history subset; and
- **≥ 300 matched pairs** have strictly-prior history; and
- both deterministic route folds contain **≥ 10 routes**.

If any gate fails, classify the dataset **underpowered/ineligible for the frozen confirmatory test** and stop **without loading taxon identity or call-index values**.

### Stage 2: response load after gate PASS

Only after the structural gate passes may the analysis load the canonical `taxon_key` and `call_index` columns.

At that stage report:
- taxa represented in the RouteID × SurveyPeriod support pools;
- species-slope estimability by fold;
- strictly-prior history exposure.

Then calculate the frozen endpoint and principal comparator exactly once.

These gates and the two-stage loading order were fixed before WFTS response-data access.

## 15. Frozen informativeness rule for a non-PASS result

The discovery reference is the NAAMP principal-comparator conditional residual:

- NAAMP conditional residual = **0.2968537316513371**.

Before WFTS outcomes are opened, define the minimum effect size whose exclusion would count as an informative attenuation/non-replication as **50% of the discovery residual**:

- frozen threshold = **0.14842686582566855**.

After the primary WFTS endpoint is calculated once, estimate sampling uncertainty in the **observed conditional residual** by a deterministic **1,000-replicate route-cluster bootstrap** (seed 2840224). Each bootstrap resamples whole traditional routes with replacement, recomputes the three observed rainfall coefficients, and evaluates the residual using the null-regression coefficients from the frozen principal comparator.

Three outcome classes are allowed:

1. **replication_support** — the observed conditional residual exceeds the upper 95% principal-comparator null bound;
2. **informative_nonreplication_of_half_discovery_effect** — the support gate fails **and** the upper 95% route-bootstrap bound for the observed conditional residual is below 0.14842686582566855;
3. **inconclusive_nonpass** — the support gate fails but the bootstrap interval still includes residuals at least half as large as the NAAMP discovery residual.

The second class means that WFTS does not support a residual dependence effect of even half the NAAMP magnitude under the aligned endpoint. It does **not** prove a true zero effect. The third class must not be described as a biological non-replication.

An exact classical power calculation cannot be made from route/pair counts alone without opening the WFTS taxon × station incidence structure, because the variance of the concentration statistic depends on that unopened structure. The frozen three-way rule therefore separates **absence of support** from **enough precision to delimit a discovery-scale effect** without using a post hoc power calculation.

## 16. Secondary endpoints

Only after the primary endpoint is calculated:

1. direct 0→CI3 rainfall coefficient;
2. third-and-later participation;
3. within-pair/taxon historical strong-site targeting;
4. exact N,K exchangeable diagnostic;
5. same-observer sensitivity if stable observer identifiers are available.

None can rescue a failed primary replication.

## 17. Data provenance

On receipt of WFTS data, before endpoint calculation record:
- exact file names;
- byte sizes;
- SHA256 hashes;
- acquisition date;
- provider/source;
- schema;
- row counts;
- year range;
- route/station coverage;
- missingness of required fields.

Schema/missingness may determine structural eligibility but must not be used to select ecologically favorable subsets.

## 18. Outcome-blind exclusions

Allowed exclusions:
- nontraditional survey types;
- incomplete route-runs;
- unverifiable/replaced physical stations for the primary analysis;
- missing survey date;
- missing route/station/taxon identity;
- invalid call-index values;
- weather extraction failure defined before outcome analysis.

Not allowed:
- dropping taxa because their effect is negative;
- dropping routes because concentration is low;
- tuning rainfall thresholds;
- changing the prior-history window;
- redefining route-new taxa after inspection.

## 19. Interpretation

A **replication_support** result supports transferability of within-taxon multi-site concentration to an external Wisconsin dataset with closely aligned protocol.

An **informative_nonreplication_of_half_discovery_effect** delimits transferability of a discovery-scale dependence effect.

An **inconclusive_nonpass** leaves external generality unresolved.

Because WFTS is historically linked to USGS/NAAMP protocol development, either outcome should be described as an **external-dataset replication**, not a replication under an unrelated monitoring methodology.

No outcome identifies the lower-level biological generator.


## 20. Frozen implementation and preflight authority

Real WFTS confirmation under this v0.5 specification must use exactly:

1. `scripts/wfts/preflight_wfts_structure.py`
2. `scripts/wfts/run_wfts_confirmatory_analysis_v0_5.py`

with canonical schema:

`revision/WFTS_CANONICAL_SCHEMA_V0_2.json`

The preflight:
- parses only route/station/date/weather structural fields;
- does not parse `taxon_key` or `call_index`;
- records SHA256 for the full runs and matrix files;
- records the canonical-schema SHA256;
- must pass the frozen route/pair/fold coverage gate.

The confirmatory script:
- requires the exact preflight receipt;
- recomputes runs/matrix SHA256 and requires byte identity;
- recomputes the canonical-schema SHA256 and requires identity;
- repeats the response-blind structural gate internally;
- loads response columns only after both preflight and internal structural gates pass.

v0.1–v0.3 scripts and specs are retained only as pre-data development history.

No change from v0.3 affects the ecological endpoint, candidate support rule, principal comparator, coverage thresholds, simulation count, seed or decision rule. v0.5 adds fail-closed provenance and response-access safeguards only.


## 20. Frozen Daymet weather implementation

The primary weather exposure defined in Sections 3–5 must be built with:

- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- `scripts/wfts/build_daymet_covariates.py`

Synthetic weather-code QA:

`.github/workflows/wfts_daymet_code_qa.yml`

The weather adapter accepts only route/station/date/coordinate structural fields and fails closed if frog-response-like columns are present.

The adapter records:
- structural-input SHA256;
- raw Daymet response SHA256 for every physical SiteID;
- output SHA256 for canonical run weather and station weather tables;
- exact Daymet request URLs.

Real WFTS frog outcomes must not be supplied to the weather adapter.

The canonical `runs.csv` passed to the structural preflight and confirmatory analysis must use the weather output generated under this frozen adapter or a byte-identical verified derivative.

No precipitation product, wet-day threshold, dry-day cap, route aggregation, or survey-day precipitation rule may change after WFTS frog outcomes are opened.
