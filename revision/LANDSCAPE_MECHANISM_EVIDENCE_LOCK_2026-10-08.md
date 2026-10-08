# Landscape-mechanism evidence lock — 2026-10-08

**Status:** The predefined JRC, MODIS DSWEmod, NWI water-regime, NWI wetland-type, and NWI wetland-amount mechanism comparisons have completed without support for reconstructing the original within-taxon concentration excess. The night-LST route was coverage-inconclusive. The final E3 Landsat NDMI route is allowed only under its frozen public-source and coverage gates.

## Biological question retained throughout

Can observable local wetland/landscape state explain the higher-order allocation of frog reproductive acoustic activity to multiple stops occupied by the same taxon, beyond the established principal comparator?

The principal comparator already represents cross-fitted species rainfall responses, strictly-prior species × physical SiteID propensity, dry-state persistence (a=0.75), and the observed aggregate incidence of wet-survey activation.

The **within-taxon concentration endpoint is unchanged**. It is not reproductive success and does not establish individual site fidelity or animal movement.

## Frozen evidence ledger

**DO NOT compare raw residual magnitudes across rows:** each remote dataset yields its own prespecified complete-case subset. Compare M0 and the augmented generator **within the same row**.

| Measurement / hypothesis | Same-sample pairs / routes / states | M0 residual | Augmented residual | Fraction removed | Decision |
|---|---|---:|---:|---:|---|
| JRC 250-m monthly visible water (M1) | 1,881 / 366 / 20 | 0.174490 | 0.182250 | -4.45% | non-support |
| DSWEmod 500-m current, 3-month persistence and 12-month variability (M3) | 1,649 / 324 / 19 | 0.502156 | 0.530218 | -5.59% | non-support |
| NWI official water regime × rainfall (M_REGIME) | 2,028 / 300 / 20 | 0.383006 | 0.383679 | -0.18% | non-support |
| NWI WETLAND_TYPE × rainfall (secondary, same NWI sample) | 2,028 / 300 / 20 | 0.383006 | 0.388262 | -1.37% | non-support |
| NWI 500-m union wetland-area fraction × rainfall (M_AREA) | 2,409 / 364 / 20 | 0.367787 | 0.372321 | -1.23% | non-support |

For all five augmented comparisons, the concentration residual remained outside its simulation-based upper 95% bound; the upper-tail Monte Carlo P remained 0.000999 (1,000 replicates).

### NWI wetland-amount retrieval and gate provenance

The scientific contract `revision/NAAMP_NWI_WETLAND_AMOUNT_RAIN_MECHANISM_CONTRACT_V0_1.md` was frozen before focal wetland-area readback.

Eight original/recovered source shards were frozen, and one code issue in the response-blind coverage denominator was identified before the frog endpoint was calculated:
- initial aggregation incorrectly counted SiteIDs on routes already excluded by the strict coordinate gate;
- fixed denominator: 3,968 distinct strict-coordinate focal SiteIDs;
- 3,831 successfully assigned SiteIDs = 96.55% (>=90% gate);
- 2,409 complete focal pairs / 364 routes / 20 states (all thresholds passed);
- no metric, radius, threshold, source shard, simulation rule, or biological endpoint changed.

The corrected frozen GitHub Actions run was **37705731375**. It classified the result `wetland_amount_filter_not_supported`.

### Descriptive coefficient-stability QA (not a frozen hypothesis test)

The final M_AREA artifact reports full-rank designs in both deterministic folds (28/28 columns each) and estimable wetland-area × rain coefficients for 42 taxa in fold A and 39 in fold B. Of the 39 taxa estimable in both, 24 had the same coefficient sign; the cross-fold Pearson correlation was -0.236. The actual magnitude of the added area-specific logit shift was modest (mean absolute 0.0413; 95th percentile 0.1552).

This is a **post-readback descriptive audit**, not an inferential endpoint or evidence of a universally negative ecological effect. It is consistent with the frozen conclusion that a nationally portable wetland-area rain filter has not been demonstrated.

### Other tests and their different inference targets

- DSWEmod classes 1–4 and 250-m named spatial sensitivities did not rescue the concentration mechanism.
- JRC 250-m strong-chorus spatial-alignment permutation: P=0.360, non-support.
- DSWEmod 500-m strong-chorus spatial-alignment permutation: 1,211 informative pair × taxon clusters, P=0.646, non-support.
- Temporal validation of the separate three-month hydrological-readiness prediction: early period 2003 and 2005–2009 training, 2010–2015 validation; equal-species mean held-out log-loss **gain = -0.003588**, route bootstrap 95% CI **[-0.005858, -0.002186]**; classification `recent_wetness_temporal_transfer_not_supported`. This rejects promotion of that predictive clue to a transferable environmental-history principle.
- MOD11A1 local nighttime surface temperature: frozen common-night coverage gate failed (same-date A: 83 pairs / 62 routes; within two days B: 427 pairs / 184 routes). This is **coverage-inconclusive**, **not a negative thermal effect result**.

## What is empirically narrowed

The excess within-taxon multi-site chorus allocation is **not reconstructed by the tested forms** of:
1. monthly visible surface-water extent;
2. monthly partial/potential wetland fraction;
3. persistence and variability of those surface-water fractions;
4. static mapped water-regime/type filtering of rainfall response;
5. total 500-m mapped wetland area filtering rainfall response.

This is a defensible ecological boundary, not a demonstration that water or landscape conditions are irrelevant.

## Remaining unresolved mechanisms

The tested remote sources do not directly measure:
- nocturnal water temperature at an actual calling site;
- water depth, chemistry, or substratum moisture at spawning microhabitats;
- small temporary pools beneath canopy/emergent vegetation or below pixel support;
- sub-monthly inundation pulses;
- local breeding population size and physiological readiness;
- taxon-specific/socially coupled reproductive acoustic state.

The current NAAMP archival calling-index data cannot by themselves identify which of these causes the residual.

## Final remaining public abiotic route: E3 (strictly bounded)

The archived priority ledger authorizes a **single** final remote-abiotic candidate: Landsat Collection 2 Level-2 NDMI under the prospectively frozen 500-m / 32-day / 70%-valid-pixel / same-acquisition route rules.

First USGS LandsatLook preflight classified image access inconclusive. A separate **outcome-blind alternate-distribution preflight** (branch `remotesensing/e3-pc-access-v1`) tests whether the same USGS C2 L2 product can be accessed through Microsoft Planetary Computer. It does **not** change the index or any inferential rule.

Proceed to E3 NAAMP site coverage only if source and pixel-QA checks pass at unrelated historical test locations; proceed to frog endpoint only if 1,500 pairs / 300 routes / 15 states pass the fixed gate. Otherwise record E3 as source- or coverage-inconclusive.

**Stop after E3**. No additional arbitrary satellite index, radius, time window, or response-selected taxon group should replace a failed result.

## Manuscript boundary

Keep the existing RC6/JAE principal discovery unchanged. Do not claim the causal mechanism has been identified. The remote-sensing work may support a concise Limitations/SI qualification:

> Satellite measures of visible surface water, partial inundation, mapped wetland hydroperiod, wetland type and local wetland amount did not account for the higher-order concentration under the tested frozen generators; finer hydrology and biological/behavioral states remain unresolved.

Do not turn a negative abiotic audit into a new headline or reopen the core submission.
