# FROGCS mechanism test — equal current water, different antecedent soil trajectory

**Date:** 2026-10-19; user-requested exploratory research, separated from JAE frozen `main`.
**Pre-result contract:** This file is committed **before** inspecting any newly retrieved ERA5 historical soil-water values or their relationship to NAAMP calls. The already observed cross-sectional association between water content and strong calling is NOT a new discovery, and no causal mechanism can be identified by this retrospective reanalysis.

## One new mechanistic hypothesis

**Hydrologic trajectory hypothesis (conditional hysteresis):** At similar current reanalysis soil-water levels, rain recency, surface water and other meteorological/seasonal conditions, *rising* soil water during the week before a survey may be associated with greater current reproductive acoustic activation than a *stably wet or drying* week. A temporal trend is biologically distinct from a static wetness state or fixed habitat quality. This still does not measure water in actual breeding pools, adults entering ponds, eggs, or recruitment.

An amphibian natural-history precedent finds the **timing and consistency of preceding rainfall** can matter independently of current water; see Güell and Warkentin 2023 `https://doi.org/10.1093/beheco/arad072` and Schalk et al. 2019 `https://pmc.ncbi.nlm.nih.gov/articles/PMC6639928/`. The *novel test here* is the joint seven-day historical **soil-water trajectory** versus the fixed-current soil state on the continental NAAMP repeated-route sample, not a claim to discover that frogs respond to rain.

## Measured data and estimands

- Population: original SHA-pinned NAAMP Runs, Stops, Counts, 2001–2015, fixed same-route and same-RunNumber cross-year wetter-rain-recency vs drier-rain-recency matched survey pairs.
- Eligible *exactly the already archived* 4,108 pair × matched RunID rows / 7,559 ERA5 survey-midpoint runs, plus pre-existing stable ten-SiteID 4,045-pair subset for original models. Exclude records missing any of 7-day lagged values, report all exclusions; never substitute zeros, alter station inclusion or source pins.
- Existing meteorology: original 0.25° Earthmover icechunk ERA5 `single/temporal`, `swvl1` (0–7cm) and `swvl2` (7–28cm); ground air/VPD/72h rain from existing checksum-locked 2026-10-19 environment cache (ZIP SHA256 `e182e0e30a7a5f1a7f1b8683d0024155b06f44b03205faa5df4beb02895d97a0`).
- **New data read:** soil layers 1 and 2 at **t−24 hours and t−168 hours** for every archived survey RunID, at same nearest pixel and UTC floored survey-midpoint hour. No future observations, no outcome-guided time/window or spatial pixels.
- Mean common soil level at event: `S_t = (swvl1_t+swvl2_t)/2`. Net 7-day historical water rise at that event: `H_7=S_t−(swvl1_(t−168h)+swvl2_(t−168h))/2`. Fixed sensitivity `H_1=S_t−(swvl1_(t−24h)+swvl2_(t−24h))/2`.
- Paired difference `ΔH7=H_7(wet-rain-recency side)-H_7(dry-rain-recency side)`, **not a chronological wet-to-dry change**. Paired difference of current common water `ΔS_t`, independent layer imbalance `Δswvl1−Δswvl2`. **Equally matched present state** is a *regression adjustment*, NOT exact matching of the true wetland substrate at ten listening stops.
- Primary acoustic outcome: original `strong_new_count`: taxon × stop cells silent in the drier-rain-recency survey but CI≥2 in the wetter-rain-recency survey, within the archived paired contrasts. No direct breeding, eggs or population readout.

## Frozen comparisons, not post-outcome searches

**Primary single hypothesis**: OLS fixed effects for individual `State:Route`, original `rain_contrast`, `log(1+rain72h_w)−log(1+rain72h_d)`, `temp_difference`, `doy_difference`, `year_gap`, RunNumber, VPD relief/average, mean air temperature and water state, `ΔS_t`, soil-layer imbalance, and **one added `ΔH7` term**. Cluster uncertainty by route, CR1 with all absorbed route degrees of freedom. Report β for *+0.01m³/m³ greater ΔH7*, 95% cluster CI and uncorrected two-sided P. Use outcome and all covariates exactly identical in nested models, no sample drift. Keep observed soil β and its change.

**Secondary pre-named test:** independently replace 7-day trajectory with **24h ΔH1** while keeping same covariates; test whether an immediate wetting trajectory is more informative on the same support. Apply Holm to the two trajectory P values for interpretation; no alternative lag selection.

**Falsification/robustness:**
1. source-locked contemporaneous S1/S2 at t must agree with prior numeric environment cache; test original 4108→4045 count and original route-FE coefficient 0.0990725077 per 0.01m³/m³ on the unchanged model.
2. same-observer paired subset, same route+RunNumber absorbed effects and year-fixed contrasts, all reported regardless of sign.
3. missing survey-midpoint or historical ERA5 treated as explicit missingness; if retained pairs fall below 3,000 or routes below 450, **STOP no effect**.
4. temporal transfer: fit fixed 2008 cutoff (both survey years ≤2008) vs ≥2009 on same covariate support and original known-state/RunNumber policy. Report route-equal MSE improvement of 7-day-history over current soil alone and separate **seen-route / unseen-route** results; no retuning/future-label correction. If no incremental heldout improvement, do not claim transferable causal signal.
5. environmental source/pixel geocoding 0.25°, survey times and soil volumes are reanalysis estimates not groundwater measurements or soil sensors.
6. **No global time-series causal direction** is inferred: survey pairs span different years and labels are by rain recency, hence one cannot infer sequential chorus events or spawning after rain.
7. No test of original JAE within-taxon multi-stop concentration C or any life-history/oviposition trait.

**Interpretation decision:** strong within-route association + heldout incremental gain + consistent same observer would make the *hydric historical trajectory* a stronger explanatory candidate but **still** not prove rainfall causation, adult behavioral readiness or eggs. If current-level-only model wins out of time, hydrologic hysteresis is unsupported by this panel. Negative results must be retained; no tuning endpoints/lag hours.

Separate analytic script and scientific cache, on `research/state-history-hydric-synthesis-v1` only.
