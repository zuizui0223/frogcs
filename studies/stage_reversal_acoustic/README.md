# Independent study: developmental trophic reversal × acoustic timing (2026-10-25)

**STATUS: NEW PROSPECTIVE DEVELOPMENT LANE, NO NEW EMPIRICAL TEST PASSED.** This branch must not be merged into, or used to reopen, frozen JAE RC6 scientific results. The frogcs RC6 mainline and 2001–2015 NAAMP conclusions remain unchanged.

## Ecological question

Can adult frog breeding calls serve as temporal cues to the period in which the same frog–consumer pair changes its predator/prey role across metamorphosis, and is receiver antipredator behaviour actually responsive to the signal?

Separate hypotheses:
1. **Documented stage-dependent trophic reversal** — directions must be directly documented for a named predator/prey pair. Spatial or seasonal co-observation alone is insufficient.
2. **Acoustic lead / lag** — compare matched site × breeding-season × week caller composition with egg/tadpole, nymph and emergence stages. Define signs as calling at t versus stage exposure at t + 1/2/4/8 weeks, with negative-time placebo and effort-conditioned seasonal/weather baselines.
3. **Acoustic receiver response** — only acute co-recorded receiver actions, cessation cascades or playback interventions can support warning / use-by-receiver claims. Calling as an ordinary reproductive cue is NOT evidence of an evolved alarm signal.

## Verified anchor and source timeline

**Litoria aurea × Anax papuensis.** Beranek et al. 2023 Ecology (DOI 10.1002/ecy.4108) documents tadpoles eaten by larval dragonflies from antecedent original work and juvenile/adult frogs consuming dragonflies during larval/emergence stages. Nine wetlands were surveyed over 2016–2020; most documented emergence predation was in austral October–November. Original field data are published at DOI 10.17632/9swstxknpz.1. This paper supports stage-specific reversal, not measured frog-call warnings or population-scale reversal rates.

**FrogID v7** — Australian Museum version released 2026-09-09, >1 million expert-validated frog *occurrence records* from 2017-11-10 to 2024-11-09 (228 species). Recorded call timestamps give potential seasonal cues, but occurrence exports generally do not identify exact oviposition or natural frog absences.

**iNaturalist stage annotations** — Life Stage exists, but valid eggs/larvae/emergence observations, annotation consistency, event ID denominators, coordinates and date coverage must be verified before modelling; an unannotated observation is not an adult or a zero.

**Existing North American screening** — earlier exploration compared 15 latitude bands, finding five North American bands where reported frog tadpoles overlap salamander larvae more than salamander eggs, with a same-iNaturalist-source sensitivity. This is exploratory co-reporting only, NOT direct predation reversal or an audio-joined finding. Original rows need to be recovered before fitting new models.

**NAAMP** — USGS frogcs acoustic data cover 2001–2015. This historical period is NOT time-matched to FrogID v7 and cannot silently be paired with 2017–2024 life-stage records; it is not being reanalysed as part of RC6.

## Required flat original-data grain

All datasets are source/observation/event audited, source versions and hashes frozen before reading the target outcomes, and shared region/year/season support verified (including southern breeding seasons spanning calendar years).

- `calls.csv` — `cell_id,season_id,week_start,species,positive_recordings,total_recordings`. Count distinct source *recordings* in numerator and within-programme denominator, not occurrence taxon rows. For presence-conditioned FrogID this is a share of eligible recordings, NOT unconditional calling probability.
- `stages.csv` — `cell_id,season_id,week_start,species,stage,count,total_annotated`. Accepted stage dictionary initially egg/larva/metamorph/emerging/juvenile/adult; all input stages need a source-verified mapping. Unknown/missing are neither zeros nor assumed adults.
- `documented_stage_edges.csv` — `edge_id,pair_id,predator_species,predator_stage,prey_species,prey_stage,evidence_status,source_doi`; allow only documented named stage-specific directional edges.
- Geography: ~50-km cells only after confirming geolocation precision; buffer/edge sensitivity and independent cell-season-year sample-size gates are mandatory.

## Estimands, claim gates and STOP condition

An initial **source-conditioned descriptive** estimator can tabulate same-week co-observation opportunities for a documented stage pair and conditional call-fraction lead/lags. A sign change in relative co-stage opportunity is *not* a measured reversal in attack direction. Observed predation direction remains externally documented.

The result-bearing test would compare an out-of-block season/weather/recording-effort baseline against the exact baseline plus preregistered trophic-stage timing and calling terms. Nulls include an unmatched consumer pair, negative call lags, source- and season-matched controls, and predeclared spatial/time holdouts. A receiver *warning* conclusion is gated on genuinely high-frequency co-recorded behavioural responses/playbacks.

**DO NOT declare a trophic-switch date, warning signal, alarm effect, density or reproductive success from NAAMP or FrogID incidence alone.** If no independent source-matched stage × acoustic opportunities can be reconstructed, report NOT ESTIMABLE.

## Source references

- Beranek et al. 2023, DOI https://doi.org/10.1002/ecy.4108
- 2023 original supplementary dataset https://data.mendeley.com/datasets/9swstxknpz/1
- FrogID 7.0 official https://australian.museum/blog/amri-news/frogid-dataset-7/
- iNaturalist ontology https://www.inaturalist.org/pages/annotations
- NAAMP DOI https://doi.org/10.5066/F7G44NG0

## Execution accounting

Created 2026-10-25 as separate exploratory study. A standalone stdlib-Python v0.1 descriptive implementation and eight local unit tests were generated separately, with all eight passing. They have **not yet been uploaded to this branch or run on original rows**; this GitHub branch contains the frozen source/claim contract and evidence registry only. No new biological result is claimed.
