# ONTO-TIME — independent original-data Australian frog × odonate seasonal macro screen

**Not an extension to the 2023 Beranek paper's sample and not part of frozen JAE RC6.** Branch `study/stage-reversal-acoustic-macro-20261025`, independent macro lane.

## Core biological hierarchy
1. Trophic role reversal (needs direct two-way, named pair/stage predation evidence; paper examples do not automatically generalize).
2. Seasonal opportunity (same broad region/time occurrence of callers and adult dragonflies, using original FrogID and GBIF).
3. Risk-cue use (only directly observed receiver behavioral changes from real paired experiments; neither GBIF nor FrogID proves this).
4. Mechanism (development/gape size, hydroperiod or shifts in cue identity; cannot be inferred from the occurrence archive alone).

## Frozen exploration grid
Australia; six equal 6-degree latitude bands: [-44,-38],[-38,-32],[-32,-26],[-26,-20],[-20,-14],[-14,-10]. Years 2018, 2019, 2020, 2021, 2022, 2023. Months Jan–Dec. Within each lat×year, retrieve **12 month counts** from three original GBIF streams (FrogID call-positive species records, all odonate records, and explicitly `lifeStage=Adult` odonates). Use `taxonKey=789` for the GBIF order to avoid silently ignored `order=Odonata` query parameters. FrogID source is always constrained by its exact datasetKey.

The primary simple metric is monthly **overlap coefficient** `sum(min(p_frog_m,p_odonataAdult_m))`; both distributions normalized *within their stream / latitude / year* (no equality of detection efforts presumed). The 12-month rotational null gives a **descriptive reference only**. Circular mean phase / concentration R and highest count month are secondaries. Eligible panels: 100+ frog species-positive rows; 30+ explicit adult odonate records; 100+ any-stage odonate records; at least 4 nonzero months in both streams. Excluded records are NOT forced to zeros and never rescued by shifting eligibility after seeing effects.

## Key novelty restriction
**Stage-specific reciprocal predator–prey reversals and sound-warning functions are not demonstrated by seasonal group co-occurrence.** The macro ecological question is narrower: whether the *observed seasonal opportunity* for sound-bearing frogs and adult odonates is repeatably concentrated and latitude-dependent. Original GloBI networks and other risk-cue experiments are separate evidence layers / future mechanism links, not interchangeable endpoints or independent populations.

## Original source feasibility already observed
- 2018–24 GBIF Australia `taxonKey=789`: 147,911 Odonata occurrences; 19,999 explicitly Adult; 105 Nymph; 3 Larva; 29 Egg. Most records have no interpretable stage. 
- 2018–24 Australia `taxonKey=952`: 1,378,754 Anura occurrences, only 88 explicitly `Larva` and 20 `Egg`. This is **stage completeness not sufficient** for direct national reversal timing.
- 2019 south / 2020 north pilot showed monthly data obtainable at independent lat–year grain. All remaining panels are treated as new exploratory outcomes, never confirmation.
- Two independent behavioural signal counter-examples: Thapa et al. 2024 report life-stage odor recognition generalizing across beetles but not salamanders, https://doi.org/10.1093/beheco/arae014; Urushihara & Takatsu 2026 report residual nonconsumptive predation cue effects after prey outgrow the size-risk window, https://doi.org/10.5061/dryad.31zcrjdzw. **No primary data downloaded or reanalysed for either**; these are prospective mechanism modules.

## Execution
Self-contained scripts and aggregate metadata will be in `macro/` under the independent study; do not edit original JAE frozen results. Source snapshots must retain query parameters, capture date and the full 12-month count vector. `lifeStage` absence is never adult. All effect statements must be conditional on sample effort and not elevated to predator attack or alarm behavior.