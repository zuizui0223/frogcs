# Frogs, emergent aquatic vegetation and survey-month wetness — 2026-10-21

## Status

**Completed user-directed new post-hoc exploration.** Positive NWI plant-location associations in several taxa **do not** extend to an identifiable NWI emergent-cover × MODIS three-month-wetness mechanism for spatial calling allocation or checkerboard segregation in the tested joint environmental model.

This is a **new ecological question**, not a continuation or reanalysis of the frozen JAE RC6 primary endpoint. All data and source gates are archived; the manuscript, SI and submission bundle are unmodified.

## A. The exact question

Does a taxon's allocation of strong calls to mapped emergent wetland habitats depend on the route's recent satellite-estimated wetness state, and can that dependence generate the observed nonrandom overlap/segregation among taxa?

This is not simply whether frogs call more after rain. It controls the taxon-by-night number of strong-call stops *exactly*, then asks **which stops** receive those calls and how different taxa share them.

## B. Outcome-blind external data intersection

- USGS NAAMP: **2,626 fully covered standardized ten-stop survey runs**, **336 routes**, **18 states** (26,260 site-visits).
- Early period (2003, 2005–2009): **829 runs**; late period (2010–2015): **1,797 runs**.
- **1,484** matched source-only survey runs had among-stop mapped PEM variation and at least some satellite three-month wetness.
- Station geometry and NWI PEM mapped within **250m**: frozen full USFWS NWI crosswalk from run 39450277196.
- Current monthly partially inundated wetland (DSWEmod classes 1–3) and survey-month + preceding two months: MODIS **500m** from original frozen extraction run 37615425574.
- Prior independent analysis already failed transfer of the three-month-wetness strong-calling predictive gain to later years (−0.003588, 95% interval −0.005858 to −0.002186). This was established **before** the new interaction test and is not overturned by any result below.

Outcome-blind preflight **passed all gates** without opening Counts.csv; [preflight run 39518202016](https://github.com/zuizui0223/frogcs/actions/runs/39518202016), receipt `exploration/NAAMP_PLANT_WETNESS_SOURCE_PREFLIGHT_RECEIPT_V0_1.json`.

## C. Cross-fitted placement of strong choruses

Primary endpoint: CallingIndex≥2 at each physical stop, **conditional on that species calling strongly at 1–9 of the ten route stops that night**.

- H0 environmental model: NWI total wetland + NWI PEM + current MODIS partial-water extent + three-month MODIS wetness.
- H1 model: H0 + **PEM fraction × route-mean survey-month-inclusive three-month wetness**.
- Models fit in the opposite deterministic route fold using exact fixed-k likelihood and fixed ridge/coefficients; no selection of the five previously BH-positive plant-associated taxa.
- H0 versus H1 is evaluated on exactly the same held-out strong-call placements.

| Out-of-sample test | H1−H0 increase in location log-likelihood (nats per taxon×run) | Route bootstrap 95% interval |
|---|---:|---|
| Opposite-route validation | **−0.000810** | −0.003351 to +0.001744 |
| Early-years fit → 2010–2015 test | **−0.000841** | −0.004379 to +0.002123 |

Route split: **6,282** informative taxon×run clusters across **335 routes** and 44 taxon units. Early→late: **4,564** informative taxon×run clusters across **299 routes**. Both interaction increments are **unsupported**: no confidence interval excludes zero in the positive direction, and point estimates are slightly negative. The early→late split is a genuine year holdout on the recorded species-level outcome, but the MODIS recent3 includes the survey calendar month; it is **not a leakage-free prospective hydrological forecast**.

Fitted H1 interaction signs among eligible taxa were heterogeneous: route-fold A training **8 positive/16 negative**, route-fold B **5 positive/14 negative**; early-only training **3 positive/10 negative**. This is descriptive, not a signed causal mechanism.

## D. Can PEM × satellite wetness generate acoustic checkerboarding?

Secondary between-taxon C-score generator was restricted to **840 originally qualifying strong-call survey matrices across 242 routes**. The exact same observed number of taxa per stop and number of detected stops per taxon are conserved. Weighted Curveball Metropolis–Hastings simulations use 199 draws/matrix, explicit fixed margin identity checks and route-out training. The synthetic stationary-distribution QA passed.

| Statistic | Mean C-score |
|---|---:|
| Observed taxon-by-stop checkerboard | **2.396502** |
| Original exchangeable fixed-fixed prediction | 2.335512 |
| H0: static plants + current/recent MODIS water | 2.336088 |
| H1: plus PEM × recent-wetness interaction | **2.334529** |

Increment in the **predicted C-score** attributable specifically to the interaction:

- **−0.001560**; 95% route-clustered CI **−0.003089 to −0.000031**, nominal P=0.0456.
- The small negative difference does not support the preregistered prediction that a vegetation × wetness preference filter *increases* checkerboarding. Its borderline nominal P is not grounds for an alternative headline claim, especially within post-hoc analyses.

Residual C-score after H1:

- **+0.061974**, 95% route-clustered CI **+0.039616 to +0.084332**;
- simulated weighted-null upper-tail plus-one **P=0.005**, the minimum possible given 199 draws;
- H0 residual **+0.060414** on the same sample.
- Spatial folds separately: H1-adjusted residual +0.06493 (fold A), +0.05886 (fold B), both positive.
- Weighted Curveball mixing audit: **0 of 622** originally informative matrices lost C-score exploration; accepted feasible proposals about **65%** in each generator.

**Classification:** `plant_x_wetness_interaction_prediction_not_supported`; `plant_x_wetness_checkerboard_explanation_not_supported`; `residual_between_taxon_checkerboard_persists`.

## E. What is newly learned — and not learned

1. A subset of species has cross-sectional associations with mapped emergent wetland polygons. Those associations are real exploratory statistical findings for acoustic locations but **do not imply direct habitat selection behaviour** or prove plant effects on reproduction.
2. Previously tested satellite water state, static plant cover and their current/3-month interaction **cannot explain the excess species segregation** in the tested model, even while conserving the observed taxon and stop activity margins.
3. The test makes a sharper *negative* conclusion than simply naming "unmeasured habitat": a combination of measured plant distribution and month-scale satellite hydrology is not sufficient to produce the observed **joint multi-taxon spatial configuration**.

Do **not** infer that all environmental mechanisms were excluded. NWI does not reconstruct 2001–2015 macrophyte cover, and DSWEmod cannot resolve plant-covered shallow water, precise hydroperiods, water temperature or microhabitat. The survey-month-inclusive recent3 may include satellite readings taken after the corresponding acoustic survey. A social mechanism, competition, demographic abundance, or conspecific recruitment remains a hypothesis rather than an identified causal generator.

## Decision for continuing research

**Stop retuning satellite products/plant buffers to rescue the checkerboard mechanism.** The next mechanistically discriminating experiment would use repeated, precisely located acoustic monitoring with survey-event plant cover **and** independently measured hydrology (water depth/level, time since wetting, substrate moisture and water temperature), plus contemporaneous conspecific calling state. Ideally manipulate vegetation or water state at replicated sites to separate environmental filtering from species/social effects. This is a **new field or monitoring study**, not unfinished work in the current NAAMP dataset.

## Reproducibility
- Frozen hypothesis/design: `exploration/NAAMP_PLANT_WETNESS_INTERACTION_CONTRACT_2026_10_21.md`.
- Source-only coverage: `exploration/NAAMP_PLANT_WETNESS_SOURCE_PREFLIGHT_RECEIPT_V0_1.json`.
- Complete computed results: `exploration/NAAMP_PLANT_WETNESS_INTERACTION_RESULT_V0_1.json`.
- Executed workflow: [GitHub Actions 39519040536](https://github.com/zuizui0223/frogcs/actions/runs/39519040536) (SUCCESS; exact artifact 12310221822).
- Previous weighted checkerboard generator: [run 39516056663](https://github.com/zuizui0223/frogcs/actions/runs/39516056663).
- Ancient remote hydrology closure: `remotesensing/naamp-dynamic-hydrology-v1`, `remotesensing/REMOTE_SENSING_HYDROLOGY_MECHANISM_CLOSURE_2026-10-07.md`.
