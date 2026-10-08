# Terrestrial environmental history: outcome-blind feasibility v0.1 — 2026-10-08

## Scientific question

This is **not** a new surface-water test and does **not** modify the already-frozen RC6/JAE concentration analysis or final E3 Landsat NDMI contract.

The new biological hypothesis is a **terrestrial environmental-history filter**:

> The spatial expression of a common rain pulse may depend on the trajectory of surrounding non-water vegetation moisture *before* the survey, not just wetland surface-water extent or a single contemporaneous terrestrial snapshot.

An adult frog's accessibility/availability to breed may reflect environmental exposure and terrestrial refuge condition accumulated over prior weeks. This is a hypothesis, not a claim established by the NAAMP CallingIndex data.

## The nontrivial test: terrestrial environmental hysteresis

The substantive prediction is not merely that greener/wetter sites have more callers.

**At comparable current land NDMI and comparable rain recency, reproductive acoustic activation may differ depending on whether the surrounding land recently re-wetted or has been wet/stable for weeks.** Thus the same current state could produce different spatial calling configurations because the preceding terrestrial environmental path differs.

This is a conditional, history-dependent prediction. It must not be interpreted as demonstrated migration, individual memory, or reproductive fitness.

Competing ecological expectations must be retained:
- an **accessibility/re-wetting** process predicts stronger activation after recent recovery from a dry terrestrial state;
- a **cumulative-readiness** process predicts stronger activation after sustained antecedent wetness, even without a large recent upward trajectory;
- a null environmental-history mechanism predicts that adding the antecedent trajectory supplies no predictive or concentration-allocation improvement beyond current state and rain.

## Two distinct timescales

1. **Antecedent land-moisture trajectory (priority):** change in land-pixel NDMI between an earlier 33–96-day antecedent period and a recent 0–32-day antecedent period. Both entirely precede the survey. Condition on current NDMI, site history, rain, temperature and seasonality; subtract expected within-season phenological change where a training-only baseline is available.
2. **Long-term structural habitat history (descriptive, separate):** annual changes in forest/land cover from USGS LCMAP (1985–2021 version-of-record), used to contextualize land change rather than replace the moisture trajectory or to find a favorable new predictor.

The short-term NDMI signal is *spectral vegetation moisture*, not a measurement of frog hydration, water depth, or reproductive success. Annual LCMAP is structural change and is not evidence of same-night behavioral activation.

## Priority terrestrial support

For feasibility, inherit the **500-m radius and QA rules of the final E3 contract**, with open-water QA pixels excluded. The scientific object is the valid non-water surface within this support. Some wetland vegetation may remain, so it must not be described as exclusively upland habitat.

Do not select a new radius or alternative index according to frog results.

## Outcome-blind phase 0 (implemented now)

Using the already-produced final E3 metadata receipt:
- total fixed focal RunIDs;
- number of eligible full-route same-product Landsat scenes within the preceding 32 days;
- number of **distinct acquisition dates**, not merely product IDs;
- proportion of runs with >=2 distinct dates separated by >=16 days;
- distribution by acquisition era and route;
- distribution of candidate counts.

The metadata receipt is itself generated from frozen focal RunID identities and dates. This script reads **no CallingIndex values, no NDMI pixels and no concentration endpoints**.

This is only an **availability upper bound** for estimating a time trajectory. It does not imply any scene is cloud-free, provides sufficient valid non-water pixels, or meets the eventual pair-level coverage gate.

## Later phase 1 (not authorized by metadata alone)

If pursued as a separate study, independently assess:
- all-ten-stop 500-m QA-valid land-pixel coverage for a recent window 0–32 days;
- at least one independent QA-valid scene for earlier 33–96 days;
- full sensor harmonization for TM/ETM+/OLI;
- quality-consistent observations and seasonal/land-cover stratification.

No future-of-survey imagery may enter a predictor. Use the same-site near-minus-earlier NDMI difference and remove route-wide shared variation. Separate this from seasonality and long-term site history.

Pre-specify full pair/route/state coverage thresholds **before pixel values or frog outcomes are joined**. A metadata-rich result cannot waive insufficient actual QA coverage.

## Existing stop rule and inference boundary

The final E3 concentration test retains its frozen single-acquisition, 500-m, 32-day and >=70%-valid-pixel design.

Do **not** replace a failed E3 with this temporal formulation and portray it as the originally preregistered confirmatory test. A different terrestrial history estimand requires a separate research question and a new outcome-blind feasibility step; testing another predictor on the same NAAMP endpoint after many negative analyses is exploratory and requires independent temporal/geographic/programme validation before claiming a transferable ecological mechanism.

Avoid promoting multiple terrestrial indices, radii, windows or species subsets according to results. The present deliverable is feasibility only.
