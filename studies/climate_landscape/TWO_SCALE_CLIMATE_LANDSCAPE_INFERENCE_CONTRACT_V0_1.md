# Two-scale ecological inference contract: climate forcing vs terrestrial-site reorganization

**Status: independent study design, 2026-10-08. No frog-response outcome opened in this new analysis. Not an RC6 amendment.**

## Central biological question

When long-term warming/drying and terrestrial landscape conversion accumulate, does reproductive-season acoustic activity simply rise/fall within a set of historically recurrent frog calling sites, or is strong calling **reallocated among physical sites**? Can forest/wetland terrestrial buffers decouple the two responses?

The word 'breeding' is reserved for verified breeding activity; NAAMP CallingIndex is an **acoustic reproductive behaviour proxy**, not egg deposition, population size, adult return or larval success.

## Why two separately identified scales are essential

### Model A — route × species × survey event *magnitude*

For species `s` on 10-stop route `r` in survey event `t`, define
`K(s,r,t)=count(stop i with CallingIndex>=2)`. A model of K considers:
- historical 1981–2000 climate baseline and *strictly antecedent* annual climatic state (previous 5 full years), plus rain/temperature in the previous 7/30/90 days;
- taxon-specific seasonality, observer and detection;
- route/site sampling continuity; time/geography blocks;
- route summaries of verified terrestrial conversion.

Hypotheses A1 (weather-only) vs A2 (weather + antecedent climate state + land change) ask whether **the amount of strong calling** is better predicted on genuinely held-out regions/years. They do not establish causal climate-change attribution.

### Model B — route × species × survey event *configuration conditional on K*

Let `z_i` indicate CI>=2 at each of the ten physical stops; only compare events with an informative `0<K<10`. Conditional on total K, use a constrained (fixed-K) allocation model:

`P(z | sum_i z_i=K, eta) = exp(sum_i z_i*eta_i) / sum_{A subset {1..10}, |A|=K} exp(sum_{i in A} eta_i)`

with an `eta_i` containing strictly-prior (time-causal) taxon×site use, *local* change in verified forest->developed/forest->agriculture, fixed physical habitat, and prespecified `antecedent warming/drought × terrestrial buffering` interactions. The exact 10-stop denominator can be evaluated by enumerating at most 1024 binary configurations per event.

**Identifiability warning:** any route-wide weather or climate main effect that adds an identical constant `c(s,r,t)` to all `eta_i` *cancels exactly* from this fixed-K likelihood. Therefore Model B cannot detect a uniform regional climate main effect; it measures the **relative allocation among stops** only. Route-wide climate main effects belong to Model A. Climate × spatially heterogeneous local land cover *can* affect Model B.

## Competing ecological predictions (not chosen after seeing new responses)

1. **Environmental tracking**: conditional on overall K, strong chorus migrates preferentially away from sites with confirmed forest-to-developed conversions toward relatively buffered sites (a statistical change in site allocation, not literal individual frog movement).
2. **Acoustic site legacy**: formerly recurrent strong-calling sites remain strongly used after mapped terrestrial conversion, with any decline delayed to later repeated observations. A lag requires at least one pre-event and *two or more* post-event surveys at the SAME externally corroborated physical station; a simple old/new image pair **cannot** establish delayed effects.
3. **Magnitude/configuration separation**: prior warm/dry climate shifts influence total active acoustic opportunities (Model A) but not Model B unless they interact with spatially heterogeneous site buffers.
4. **Null / confounding**: land and climate inputs add no transferable held-out prediction beyond strict prior site history, short-term weather, season, and observer/detection conditions.

All are empirically defeasible and can have null results. Do not change historic JRC/DSWEmod negative mechanism tests.

## Landscape predictor and timing contract

- Source: official USGS Annual NLCD Collection 1.2 (1985–2025), not legacy 2001/2006/2011 epoch mosaics.
- Primary independently validated local buffers: 250 m and 1 km, both fixed before frog-response join. Mapped terrestrial exposure is *pairwise valid-pixel* forest-to-developed conversion, not difference in independently masked forest totals. Missing or conflicting pixels are not “no change.” Require >=80% pairwise coverage in both years.
- Antecedent change windows: `survey_year - 6` to `survey_year - 1` (past five-year interval). Do NOT use classified land cover in the same calendar year as the frog survey to infer conditions prior to that year's survey. When available, also verify the official Land Cover Confidence and Land Cover Change products, rather than treating all class transitions as equally certain.
- Climate: Daymet/PRISM 1981–2000 fixed climatology, with previous complete five-year climate state and prior 7/30/90 day weather (Daymet leap year Dec 31 structural missingness preserved, never imputed).
- Long-term warming/drying vs land conversion are partially correlated; no coefficient should be called causal without an external disturbance instrument/natural experiment or suitable design.

## Sample and temporal leakage control

- The new independent universe is the **full USGS standardized Runs+Stops cohort**: 7,848 ten-stop surveys on 807 routes in 21 states, verified by successful download-and-QC run [37728326242](https://github.com/zuizui0223/frogcs/actions/runs/37728326242); 8,223 unique route×SiteID keys, 29,986 adjacent-year matched-season potential stop comparisons. The latter are **dependent stop comparisons**, not 29,986 independent climate replicates.
- The older E3 Landsat metadata universe (3,811 runs, 395 routes) was previously selected in a frog-informed analytical pipeline. Its route-year Landsat comparability readouts are useful engineering pilots, **not an outcome-independent main population**.
- A site must pass geometry/relocation verification before 30-m spatial inference. Distinguish geometry-only pass from external station identity verification; at latest cohort audit the latter remains zero.
- Site historic strong-calling propensity uses only calendar years BEFORE each focal outcome and must be cross-fitted within route/region; don't compute future site propensity or pair contrast from future occurrences.
- Choose among Model A/B variants via only past training periods; evaluate 2011–2015 as a held-out future period **and** geography-blocked folds. Report imbalance in states, taxa, seasons, observer continuity and site survey histories. If validation sample sizes fail, classify infeasible rather than relaxing rules after reading outcomes.

## Core falsification/control requirements

- Compare conditional configuration predictions at exact held-out K and route-level K prediction separately. A marginal calling log-loss gain does **not** imply a solved spatial allocation mechanism.
- Control survey month/day, survey round, route position/stop order and observer; don't call a non-detection an occupancy extinction. Analyse repeated fixed sites only after stable physical identity verified.
- Independent same-season fixed-site comparisons distinguish annual landscape turnover from survey phenology drift.
- A prospective *future-land-change association check* may be reported only as a diagnostic, not as a guaranteed negative causal control, because habitat trends and prior suitability can induce associations in either time direction.
- Report spatial scene validity, sensor SLC-off gaps, Annual NLCD category confidence, and pixel-pair missingness with all effects.

## Current status / action boundary

Actual source-only repeat-stop counts are established, and official Annual NLCD per-pixel transition extraction code and synthetic tests exist. **No actual site-level NLCD change, Daymet climate-shift estimates, species calling change, reproduction or climate causality has yet been calculated** in the independent study. Subsequent outcome-stage code must wait for documented physical-site and imaging-QC provenance.
