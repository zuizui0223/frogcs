# Independent study: developmental trophic reversal × acoustic timing (2026-10-25)

**STATUS: FIRST ORIGINAL ANAX XLSX SOURCE AUDIT VERIFIED (298 DATED SURVEYS, 233 EMERGENCE COUNTS); NO NEW ACOUSTIC × STAGE EFFECT OR ALARM SIGNAL TEST PASSED.** This branch must not be merged into, or used to reopen, frozen JAE RC6 scientific results. The frogcs RC6 mainline and 2001–2015 NAAMP conclusions remain unchanged.

## Ecological question

Can adult frog breeding calls serve as temporal cues to the period in which the same frog–consumer pair changes its predator/prey role across metamorphosis, and is receiver antipredator behaviour actually responsive to the signal?

Separate hypotheses:
1. **Documented stage-dependent trophic reversal** — directions must be directly documented for a named predator/prey pair. Spatial or seasonal co-observation alone is insufficient.
2. **Acoustic lead / lag** — compare matched site × breeding-season × week caller composition with egg/tadpole, nymph and emergence stages. Define signs as calling at t versus stage exposure at t + 1/2/4/8 weeks, with negative-time placebo and effort-conditioned seasonal/weather baselines.
3. **Acoustic receiver response** — only acute co-recorded receiver actions, cessation cascades or playback interventions can support warning / use-by-receiver claims. Calling as an ordinary reproductive cue is NOT evidence of an evolved alarm signal.

## Verified anchor and source timeline

**Litoria aurea × Anax papuensis.** Beranek et al. 2023 Ecology (DOI 10.1002/ecy.4108) documents tadpoles eaten by larval dragonflies from antecedent original work and juvenile/adult frogs consuming dragonflies during larval/emergence stages. The 2023 paper describes nine monitored wetlands across 2016–2020. The uploaded original XLSX provides verifiable numerical site/date emergence counts for 2018-09–2019-04 only (see source audit), plus a month-only predation summary. Original field data are published at DOI 10.17632/9swstxknpz.1. This paper supports stage-specific reversal, not measured frog-call warnings or population-scale reversal rates.

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

## Confirmed external comparison frame (reviewed 2026-10-25)

Do not pool heterogeneous study outcomes as a single meta-analytic effect.

| System | Exactly what is observed | Reversal clock | Relation to calls |
| --- | --- | --- | --- |
| *Litoria aurea* × *Anax papuensis* | Trophic directions supported across Beranek (2023) and antecedent tadpole-predation work. Frogs consumed emerging and larval dragonflies. | Seasonal development / emergence; September–November window in one 9-wetland programme | FrogID calling could be prospective, but no original site-season-week linkage has been certified |
| *Leuciscus aspius* × *Alburnus alburnus* | Adult bleak eat drifting asp eggs: 64/147 sampled bleak stomachs contained eggs; 21.2 ± 2.2% mortality over the 40-cm camera field; original paper also establishes adult bleak as asp prey | **Tens of seconds**, between egg release and adhesion | Independent non-acoustic time-resolution control; not 1/2/4-week lag data |
| *Esox lucius* × *Gasterosteus aculeatus* | Sticklebacks consumed 97% of pike under 35 mm in a feeding trial vs 5% above 35 mm. Juvenile pike can potentially consume small adult sticklebacks from a modelled 78-mm threshold; all sticklebacks potentially at ~175 mm | **Body-size/gape transition**, not a directly observed predation-switch date | Independent non-acoustic size-axis control; reverse branch modelled rather than an observed feeding experiment |
| *Hynobius retardatus* × frog tadpoles | Salamander cannibalism promotes giant larvae that take frog tadpoles more readily; does NOT demonstrate prey becoming predator of that salamander | Size-structured intensity change, **non-reciprocal control** | No warning/acoustic result |

Sources: https://doi.org/10.1002/ecy.4108 ; https://doi.org/10.1038/s41598-017-07339-w ; https://doi.org/10.1111/1365-2656.12981 ; https://doi.org/10.1002/ece3.8894 .

Independent earlier *Litoria aurea* calling-versus-tadpole monitoring (https://doi.org/10.1002/ece3.980) did not support calling-male counts as a reliable proxy for the number of breeding ponds. This is an important falsifier: calling cannot silently stand in for tadpole production.

## Executable v0.2 — current branch

- `protocol_v0_2.json`: a frozen source, estimand and comparison contract.
- `registry/source_screen_v0_2.csv`: source-confirmed direct edges, model-inferred edges and nonreciprocal controls.
- `src/stage_acoustic_screen.py`: fail-closed original-row gate, source-week opportunity accounting, stage-specific call lead/negative-lag scan; no pseudo-dated trophic switches.
- `tests/test_stage_acoustic_screen.py` and `tests/test_anax_original_xlsx.py`: source gate / denominator / stage ontology / month reconciliation / lag regression tests (**18 tests passing in GitHub Actions**).
- `.github/workflows/stage_reversal_acoustic_qa.yml`: branch + PR test automation.

Run:

```bash
python -m unittest discover -s studies/stage_reversal_acoustic/tests -v
python studies/stage_reversal_acoustic/src/stage_acoustic_screen.py --out /tmp/stage_acoustic_readiness.json
# Without verified original rows and a completed source gate, output MUST say NOT_ESTIMABLE.
```

Real model execution requires three true event-derived matrices (original frog recordings by site-week, annotated stage survey opportunities by the SAME geography/season, and direct predation observations by pair and stage). Mere DOI availability and a passing parser test are not a real outcome.

### Original Anax spreadsheet: source audit complete, cross-source joining still blocked

- The user supplied the **actual** Mendeley `Anax_emergence.xlsx` file, verified under SHA256 `25fabdd0df0d8b679ff23033abbb9fc175067c835f1bd1ef41a5fc4890360c74`. It is deliberately **not uploaded to GitHub**.
- We verified 298 physical code × date numerical visits (2018-09-04–2019-04-09), 233 emerging dragonflies and 48 positive visits. The exact eight-month emergence aggregate was recomputed from raw counted rows and matches the workbook's author-provided K:M table. The author-provided `Predation` column sums to 14 but is monthly only with unknown individual date/site provenance.
- Central emergence period: 25th percentile **2018-10-16**, median **2018-11-01**, 75th percentile **2018-11-14**; highest weekly count **62** in the week beginning 2018-10-29.
- Article prose cites four study seasons and nine wetlands, while the original XLSX has one numeric counted season, eleven recurring labels (plus sixteen incidental codes) and differences in seasonal descriptive wording. Do not silently harmonize.
- A same-study-site peer-reviewed paper (https://doi.org/10.1007/s10531-022-02387-9) explicitly names nine constructed wetlands: permanent `1B, 3A`; ephemeral `1A,2A,2B,2C,4A,4B,4C`. These **nine named codes** account for **189 emergence counts in 230 dated survey rows**, while the additional recurring code `14B` alone holds **44**. This is a strong source-ontology sensitivity, **not** verified identity equivalence for 14A/B.
- See [frozen original audit receipt](results/ANAX_ORIGINAL_SOURCE_AUDIT_20261025.json), [full Japanese evidence report](results/ANAX_ORIGINAL_REANALYSIS_JA_20261025.md), [nine-wetland cross-paper ledger](registry/ANAX_NINE_WETLAND_SOURCE_MAP_V0_1.json), and reproducible local script `src/audit_anax_original_xlsx.py`.

- FrogID v7 has public occurrence information, but its original **recording-opportunity** denominator and date/coordinate join to dragonfly emergence remain to be audited.
- There is no documented same-recorder, same-event receiver behaviour or playback intervention in these linked sources.

The source-gate result is **NOT_ESTIMABLE**, not negative evidence. Do not execute exploratory effect-hunting against available-but-noncommensurate rows.

## Execution accounting

Created 2026-10-25 on `study/stage-reversal-acoustic-macro-20261025`. The v0.2 QA is green (18/18 tests), and the original user-provided Anax spreadsheet has been analyzed and recorded under a pinned SHA, including one-season phenology and nine-wetland sensitivity. **The stage × frog-call joint analysis remains NOT_ESTIMABLE**, because the workbook contains no frogs calling, dated matched prey/predator attacks, or receiver responses. No frozen JAE RC6 manuscript / SI / results have been changed.
