# NPS strictly prior interspecific acoustic cross-lag: frozen exploratory comparison

Date: 2026-10-26. **Post-NAAMP, post-NPS-own-history exploratory**, not an untouched confirmatory replication. The outcome-bearing test here was specified after an **outcome-blind taxon/effort roster** in [roster run](https://github.com/zuizui0223/frogcs/actions/runs/40207593602). RC6 JAE paper is immutable. This analysis measures **calling histories**, not aquatic egg predation, biomass or demography.

## One primary pair (chosen from independent natural history, not outcomes)

- Exposure **green frog** `Lithobates clamitans`: annual strong call (ManualCIV>=2) at the *same NPS physical station* in calendar year `t-1`.
- Response **wood frog** `Lithobates sylvaticus`: annual strong call (ManualCIV>=2) in year `t`. Previous-year wood-frog strong call at the same station enters as a separate covariate.
- Sign proposed for **adult acoustic site-use only**: negative association of past green-frog calling with current wood-frog calling (`beta<0`). This is **not** evidence that current wood frog eggs were eaten before its own spring calling. Direct green-frog tadpole -> wood-frog egg predation is a separate published natural-history mechanism, not measured by NPS.
- **Reverse** directional falsifier (mandatory): year `t-1` wood-frog strong call -> year `t` green-frog strong call, controlling own past green-frog call. A difference is suggestive of asymmetric acoustic site histories but *does not eliminate dynamic habitat confounding*.

## Frozen secondary comparisons

1. Green frog `t-1` -> **spring peeper** `Pseudacris crucifer` `t`; no assumed demonstrated egg predation by this exact pair.
2. Green frog `t-1` -> **American toad** `Anaxyrus americanus` `t`; check phenology/habitat separation.
3. Green frog `t-1` -> **gray treefrog** `Dryophytes versicolor` `t` as ecologically imperfect comparator (later breeding may lessen immediate early-spring stage exposure); not a guaranteed null.
4. Bullfrog `Lithobates catesbeianus` `t-1` -> wood frog `t`, **secondary** because larval food relationships and overwintering probability are population-specific.
5. Blanchard's cricket frog and ambiguous `Pseudacris maculata/triseriata` remain excluded from the primary pair, not automatically negative controls.

The 13 names and scored annual coverage were frozen from the original pinned NPS source (2016–2023, 66 stations, 7 parks, 13 taxa) before cross-taxon coefficients. No new taxon re-selection if signs disappoint.

## Common data construction

- **Original** NPS version: DOI 10.57830/2320505, downloaded and SHA256-verified by existing `nps_glkn_strict_history.py`: `b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2`.
- Unit = `ParkCode × SiteLocation × ScientificName × EventYear`, outcome the **annual maximum** manually scored chorus index (CI 0–3). Every species-station-year must have scored recording evidence; missing rows are unknown, **not zero**.
- Same station `t-1` must be a *calendar* prior year, not "last observed" if two years apart. Require scored prior exposure species and scored prior target (controls); exclude insufficient pairs **before reading response**. The main contrasts may have different eligible samples; don't directly subtract raw slopes as a statistical test of sign asymmetry.
- Fix `park × current year` (within species) and stable physical station fixed effects, plus target `t-1` CI2plus, prior generic other-taxon CI2plus fraction *excluding focal and exposure species*, log focal current/year-previous acoustic effort and log exposure previous-year effort. Site FE absorbs constant hydroperiod category, not unmeasured time-varying water levels.
- Fit risk-difference style within-fixed-effect linear probability model; report rank, effective stations, parks, park-years, score distribution, cluster-by-station SE (with limitations), leave-one-park-out coefficients and exposure within-site transitions. If predictor is collinear, or insufficient independent variation (<3 parks, <20 sites, <10 exposure transitions), explicitly return `not_estimable`. No sign-searching fallback.
- Also fit a baseline without the other-species lag on **exactly the same eligible rows** to audit incremental conditional in-sample `R2`; this is **not** held-out prediction.
- Lead-exposure in year `t+1` is a **diagnostic only**, never a predictor or a valid causal negative control by itself (site persistence links temporal leads and lags). Direction is not identified from year-lag asymmetry alone.

## Limits

- Scored listening station ≠ identified pond; acoustic presence `t-1` ≠ directly observed overwintering tadpole `t`; strong calls ≠ abundance; prey current adult chorus `t` is **not** affected by its subsequent egg predation in the same season.
- Species and recording site must have overlapping measurement opportunities and calling phenology. Previous and current annual maxima are sensitive to effort, seasonal recording window, ambient noise, and species-specific habitat selection.
- This analysis is **distinct** from the earlier NPS own-history coefficient +0.464 and the locked NAAMP +0.2969 spatial concentration residual. No cross-system pooling.
- A negative effect is **not** unique evidence for predation. A zero effect does not refute larval-stage predation; a positive effect could reflect co-selection of wetlands. No H3 drought reset test from categorical Hydroperiod.
- If external pond-stage measurements become available, use the integrated G0–G4 gates first; no claim of verified aquatic predator proxy solely from acoustic results.

## Outcome decision

- Primary sign non-negative or unstable: H1A acoustic suppression **not supported**; retain as null/adverse. Main biological H1B (egg predation) remains untested.
- Primary negative, stable and reverse absent: **consistent with directional acoustic site-use filtering**, but habitat alternatives remain. The next necessary gate is actually measured pond×overwintered-stage counts and phenology.
