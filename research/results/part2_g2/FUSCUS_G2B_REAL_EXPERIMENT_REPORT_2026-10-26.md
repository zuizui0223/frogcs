# Experimental G2B observed — water drawdown and temperature predict metamorph development; predator cues do not improve held-out forecasts

**Observed/source-authenticated** 2026-10-26, **exploratory secondary analysis of a published experiment**, not an untouched independent hypothesis test, and not proof of aquatic predation. Source: Delgadillo-Méndez et al. (2025) *Freshwater Biology* **70:e70124**, [DOI 10.1111/fwb.70124](https://doi.org/10.1111/fwb.70124), [original CSIC CC BY 4.0 source](https://digital.csic.es/handle/10261/411885) (59,841-byte original XLSX, SHA256 `eb76b0ec8162278c14860fddcfe30a487ff9e8fc4b8fe40311f88dabe0fd9b25`).

[Response-blind original file receipt](fuscus_workbook_schema_g0.json) | [treatment-assignment/replicate audit](fuscus_assignment_g0.json) | [frozen analysis plan before inspecting workbook outcome columns](../../FUSCUS_EXPERIMENT_G2B_FROZEN_ANALYSIS_2026-10-26.md) | [full observed JSON](fuscus_factorial_observed_results.json) | [analysis script](../../scripts/fuscus_factorial_experiment_g2b.py) | [GitHub Actions successful real-data run](https://github.com/zuizui0223/frogcs/actions/runs/40258386081).

## 1. Direct experiment vs unresolved field question

The original factorial treatment assigned *Leptodactylus fuscus* tadpoles to **30/35 °C**, **HW** (stable high water) vs **DD** (experimentally lowered water level), and **P/NP** (chemical cues of a predator present/absent). Three source foam nests contributed larvae; 10 planned replicate containers per factorial treatment arm, each initially three tadpoles. The independent developmental exposure unit is the **small container**; temperature is assigned by an **8-bath thermostatic pool structure** (4 each). **P is an experimental cue exposure, not a live predator attack. DD is controlled laboratory drawdown, not observed natural pond dry-down.**

The publicly archived spreadsheet has **226 individual source rows, 79 small containers, 8 common water-bath pools, three original clutches**. Treatment balance was checked **without reading outcomes**: seven of eight arms contain the 10 intended small containers; the `35|P|DD` arm has **9**. Ten observed containers include fewer than three original individual records, contributing to **14 unlisted individuals** relative to the intended 240. Original scientific interpretation must not silently assume whether these omissions represent death, recording loss or another event.

## 2. Survival denominator audit, not imputed mortality

Among the **226 recorded individuals**, the source `survival_G46` field records **213 survived**, **13 not survived**, **0 unknown source-coded statuses**. An additional **14 planned individuals are not represented by any source rows**. Under the *explicit unverified sensitivity assumption* that unlisted individuals all died, overall survival equals 213/240 = **88.75%**, numerically matching the original published total. If they all survived, the upper bound is (213+14)/240 = **94.58%**. A match to the publication does **not by itself independently verify** every absent row's fate.

The eight arm-level survival bounds and missing denominators are in the original JSON. Particularly important is the **35 °C / P / DD** arm with **24** recorded individuals versus **30** planned; it has a source-coded 24/24 recorded survival, but 6 unlisted individuals. Its true full-assignment survival cannot be treated as 100% from observed records alone (sensitivity 80–100%). This arm missingness could materially affect water×predator×temperature contrasts. **No unique fully observed 240-animal survival logistic estimate is claimed.**

## 3. Experimental development: cross-thermal-bath held-out test

Observed outcomes from **213 recorded metamorphs** gave `mass_46` at Gosner stage 46 and `time_to_46` days to that stage. For each endpoint, the original repeated tadpole IDs were collapsed to the **mean of surviving metamorphs within each of 79 small containers**. Outcome is therefore conditioned on metamorph survival and may be selection biased. All models use **identical 79 containers**.

M0 = temperature + water treatment + source clutch. M1 adds experimental predator cues. M2 adds predator cue × drydown. The source pool/thermal bath is completely excluded in turn (`LeaveOneGroupOut` across **eight baths**), ridge α=10, with z-scoring learned on the training baths only. The metric is mean squared error on `log(mean observed container metamorph trait)`, averaged **equally over baths** rather than treating 213 animals as 213 independent temperature replicates.

| Bath-blocked held-out error (lower better) | M0 environment/clutch | M1 + predator chemical cue | M2 + cue×drawdown |
|---|---:|---:|---:|
| **G46 metamorph mass, log-MSE** | **0.020890** | 0.021249 | 0.021316 |
| **Days to G46, log-MSE** | **0.015731** | 0.016492 | 0.016485 |

- For **metamorph mass**, M1−M0 bath-balanced prediction gain = **−0.000359** (2,000 bath-bootstrap fixed-OOF interval **−0.001400 to +0.000220**). Adding interaction M2−M1 = **−0.000067** (interval −0.000156 to +0.000007).
- For **days until metamorphosis**, M1−M0 gain **−0.000761** (interval **−0.001734 to +0.000073**); adding M2−M1 ~**+0.000008** (interval **−0.000218 to +0.000201**). These intervals describe resampling **eight observed bath contributions conditional on fitted held-out predictions**, not a new eight-wetland trial.
- Adding cues or a cue×drydown product to this **particular predictive learner and finite sample** did **not improve cross-bath predictive accuracy** over temperature/water/clutch. This does not logically show **all** risk-cue effects are zero; other study endpoints (e.g. locomotor responses) may differ, and the source publication should be cited for the original factorial inferential analysis.

### Drydown-related mass response, descriptive survivor means

| Temperature | High water: no cue / cue (g) | Drydown: no cue / cue (g) |
|---|---:|---:|
| 30 °C | 0.20463 / 0.20703 | **0.18833 / 0.18920** |
| 35 °C | 0.24665 / 0.23972 | **0.21267 / 0.22815** |

At **both tested temperatures**, metamorphs from the experimentally reduced-water cells were generally lighter than counterparts from stable-water cells. This is a **descriptive mean among metamorphs**, not a statement about every originally allocated animal, a pooled unbiased mortality-weighted fitness effect, or a cross-bath causal population conclusion.

The water×cue difference-in-differences for recorded survivor mass was **−0.00153 g at 30 °C** and **+0.02241 g at 35 °C**. Their sign changes across temperature and the M2 out-of-bath non-improvement preclude a generalized synergistic predator×drying result.

## 4. Broader ecological interpretation for frogcs's ONE proposed manuscript

1. **Independent controlled stage ecology is now genuinely observed inside frogcs.** External randomized/assigned predator-cue exposure, independently manipulated artificial drying, and tadpole metamorph mass/time show one way to discriminate abiotic conditions from a biotic-risk signal in a controlled developmental stage. This is stronger mechanistic observability than a GloBI edge or a GBIF same-grid stage report.
2. **For these reported final phenotypes, added predator cues do not outperform a water/temperature baseline when thermal water baths are held out.** The source experiment is an empirical counterexample to treating any predator proxy as universally overriding abiotic filters, rather than a general proof that predators do not matter.
3. **Field-G2 is still not complete.** No original aquatic pool here was a naturally monitored NAAMP or INBO pond; no overwintered predator-stage size/density, direct tadpole predation rates, independently monitored 72-hour rainfall, same-pond dry/reset records, or within-site adult chorus were joined. Hence RC6's residual **+0.2969** remains a separately observed acoustic phenomenon, not an estimated predation-attributable component.
4. Missing 14 planned tadpole rows, eight bath pools, only three independent source clutches and metamorph-survivor conditioning limit strong treatment-independent or stage-survival inference. A published experimental association is not an original new frogcs intervention.

**Decision for the integrated draft:** add G2B as **external independent experimental developmental-stage evidence** and use the negative predator-cue heldout result to guard against an overly simple biotic mechanism. Still do not label a field G2 predator-stage×hydroperiod×egg-survival test as passed. The one-paper strategy remains an aspiration conditional on honest cross-source ecological logic.
