# Prospective external replication specification v0.2

**Status:** frozen before selecting or inspecting any external outcome data for this integrated claim.

## Purpose

Prospectively test whether the NAAMP finding of **within-taxon multi-site concentration** generalizes to a frog monitoring dataset external to the 21-state discovery sample.

The external study is confirmation only if its outcome data were not used to develop the NAAMP concentration endpoint or choose the comparator. Any physical route/site reused from the discovery dataset must be identified from metadata before outcome loading and excluded from the confirmatory sample; if no discovery geography is shared, record that fact explicitly.

## Dataset eligibility

A candidate external monitoring network must provide, before any response analysis:

1. repeated surveys at identifiable physical sites;
2. taxon-level calling/detection records at each site;
3. at least three sites per repeated spatial unit so third-and-later participation is definable;
4. survey-level rainfall recency or an externally linkable rainfall exposure;
5. repeated history sufficient to estimate prior taxon × physical-site use without using the focal comparison;
6. enough independent spatial units to split them deterministically into training and test folds.

If these structural requirements fail, the dataset is classified **ineligible**, not negative.

## Frozen biological endpoint

For each taxon absent from the reference survey and present in the target survey:

- (k_i) = number of target sites occupied;
- (e_i = max(k_i-1,0));
- concentration score (C = Σ_i choose(e_i,2)).

The primary question is whether the survey closer to rain shows more within-taxon concentration than expected under a comparator that preserves transferable taxon response and prior site use.

## Frozen principal comparator

Where the external design permits, fit only:

- taxon-specific rainfall response using the opposite spatial fold;
- strictly-prior taxon × physical-site propensity;
- focal reference-state persistence;
- one common magnitude-matching shift within each comparison.

Do not add taxon × site-specific rain coefficients or new trait terms after outcome readback.

## Primary decision and informativeness

Support requires the observed concentration effect to exceed the upper 95% comparator distribution in the predeclared direction.

A failed support gate is not automatically an informative biological non-replication. Before opening candidate outcomes, freeze an effect-size benchmark derived only from the discovery estimate and a sampling-uncertainty procedure appropriate to the external spatial unit. Classify a failed gate as:

- **informative non-replication/attenuation** only if the uncertainty interval excludes the frozen benchmark;
- **inconclusive** otherwise.

For WFTS the frozen benchmark is 50% of the NAAMP conditional residual, with a 1,000-replicate route-cluster bootstrap. Report effect size and uncertainty under every outcome.

## Secondary endpoints

Secondary only:
- direct silence→strong/full chorus if an ordinal calling index exists;
- third-and-later site participation;
- historical strong-site targeting;
- an exact N,K exchangeable diagnostic.

The N,K diagnostic cannot substitute for the principal comparator.

## One-shot rule

The first eligible external dataset tested under this specification is the confirmatory test.

If it fails, do not search additional external networks and report only successful ones as confirmation. Further datasets may be analysed as explicit replications, with all outcomes disclosed.

## Interpretation

A positive external result would support transferability of the multi-site concentration pattern.

An informative negative result would delimit its generality; an inconclusive result would leave generality unresolved.

Neither outcome identifies the lower-level biological generator.


## Candidate-network selection audit

**Selection frozen before inspecting any candidate-network outcome matrix.**

### Primary candidate: Wisconsin Frog and Toad Survey (WFTS)

WFTS is the first external network selected for eligibility assessment because public programme documentation establishes, without opening response-level outcome data, that it has:

- annual statewide monitoring since 1984;
- approximately 100 permanent roadside routes;
- exactly 10 listening stations per traditional route;
- repeated surveys three times each year;
- 5-minute listening periods;
- the same qualitative call-index scale (1 = separated individual calls, 2 = overlapping calls with distinguishable individuals, 3 = continuous/full chorus);
- permanent station descriptions intended to allow repeated surveying from the same locations.

These properties match the structural requirements of the frozen external-replication design unusually well.

The WFTS response data are external to the 21-state NAAMP discovery sample used in this repository; Wisconsin is not one of those discovery states. However, WFTS is historically coordinated in cooperation with USGS/NAAMP, so protocol similarity must not be described as methodological independence. It is an external dataset with unusually close estimand alignment.

**Outcome data have not been inspected for this selection decision. Public design documentation has been inspected; row-level response-data access remains unresolved. WFTS is therefore classified `DESIGN_ELIGIBLE / DATA_ACCESS_PENDING`, not yet `CONFIRMATORY_DATASET_READY`.**

### Secondary candidate: Iowa Frog and Toad Call Survey

The Iowa programme is retained only as a predeclared fallback if WFTS cannot supply an analysable repeated site-level dataset. Public documentation establishes:

- monitoring since 1991;
- repeated annual routes;
- 5–10 wetland sites per route;
- three surveys per year;
- site-level calling records.

It is less clean for the frozen primary endpoint because route site number varies and the programme later absorbed former NAAMP routes.

### One-shot candidate rule

1. Attempt WFTS eligibility first.
2. If WFTS lacks the necessary repeated site-level records or rainfall-linkable dates, classify it **structurally ineligible** before looking at the concentration endpoint.
3. Only then may Iowa be evaluated for structural eligibility.
4. If WFTS is structurally eligible, it is the confirmatory dataset regardless of the eventual result.

### Data-access boundary

Public programme descriptions and blank/sample forms may be inspected to establish design eligibility.

Do **not** inspect species × station × year outcome matrices, calculate concentration summaries, or choose subsets based on apparent effect direction before the eligibility decision and analysis implementation are frozen.

### Public design sources used for candidate selection

- Wisconsin DNR / WFTS programme overview and survey manual.
- Iowa DNR Frog and Toad Call Survey programme description and 2025 methods report.

The repository should record the exact downloaded/source metadata and checksums if response-level WFTS data are later obtained.


## Frozen implementation documents for WFTS

Before WFTS response-data access, the following are frozen:

- `revision/WFTS_EXTERNAL_REPLICATION_ELIGIBILITY_V0_1.md` — design/data-access eligibility;
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md` — Daymet exposure, pairing, endpoint, comparator and coverage gate;
- `revision/WFTS_CANONICAL_SCHEMA_V0_2.json` — canonical run/matrix schema;
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py` — sole confirmatory analysis authority;
- `scripts/wfts/generate_synthetic_wfts_fixture.py` — artificial data only for code QA;
- `revision/WFTS_DATA_REQUEST_TEMPLATE_V0_1.md` — request designed not to solicit outcome summaries.

Real WFTS response data must not be passed to the confirmatory analysis until schema/provenance and the pre-response coverage gate have been recorded.


## Confirmatory code authority

Before any WFTS response outcome is inspected, the authorized execution sequence is:

1. `scripts/wfts/preflight_wfts_structure.py`
2. verify structural gate and SHA256 receipt
3. `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

The confirmatory script requires:
- the exact preflight receipt;
- identical runs/matrix SHA256 hashes;
- identical canonical-schema SHA256;
- a passed pre-response coverage gate.

Scripts v0.1–v0.3 are development history only.


## Frozen WFTS weather authority

Before WFTS response outcomes are opened, the rainfall exposure is implemented by:

- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- `scripts/wfts/build_daymet_covariates.py`

The adapter uses Daymet daily `prcp/tmin/tmax`, a 1.0-mm wet-day threshold, a 30-day dry-spell cap, excludes survey-day precipitation, and averages `log(1+dry_days)` over the ten stations.

The adapter is response-free and its synthetic QA must pass before real response analysis.
