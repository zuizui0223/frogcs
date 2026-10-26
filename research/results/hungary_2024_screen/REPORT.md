# Hungary 2024 wetland × anuran acoustic detection: first genuine external vegetation screen

**Status:** REAL observed-source calculation, verified with GitHub Actions (not simulated); explicitly exploratory, not a preregistered or independent replication of frogcs RC6's conditional spatial-allocation statistic.

- Authors / CC BY 4.0 attribution: Mizsei & Wenner (2025), *Effectiveness of wetland restoration on amphibians in a drying grassland habitat losing its breeding sites*, https://doi.org/10.5281/zenodo.15044115.
- Verifiable inputs: [site](../../external/zenodo_15044115/wetland_amp_site_data.csv) / [survey](../../external/zenodo_15044115/wetland_amp_surv_data.csv), original MD5 confirmed.
- Executable: [Python](../../scripts/hungary_vegetation_chorus.py), [reported result JSON](observed_results.json), [CI run](https://github.com/zuizui0223/frogcs/actions/runs/40179776959).

## Raw data integrity and sample

29 wetlands (13 intervention, 9 artificial ditches / waterbodies, 7 controls), 381 method-specific rows, 2024, 26 distinct survey days, 9 detected amphibian taxa (7 frogs/toads and 2 newts). Emergent macrophyte cover ranges **1–60%**. **Only two** sites have fish present. Four survey methods:

| Method | Visits | Any of seven frogs/toads detected | Nonzero fraction |
|---|---:|---:|---:|
| Acoustic | 129 | 40 | 31.0% |
| Visual | 129 | 100 | 77.5% |
| Dipnet | 59 | 51 | 86.4% |
| Bottletrap | 64 | 31 | 48.4% |

These are observation-method positive fractions, *not* standardized detection probabilities, population sizes or evidence that choruses are rare. Counts are from the actual source CSV and the scripted check.

## Method

Five-fold **site-blocked** held-out logistic predictions of any frog/toad detected at an acoustic visit; one site appears only in training or test in each fold. Weather/day-of-year/temperature/humidity/precipitation as baseline; adding site depth and intervention/artificial/control class, or static site-level emergent/submerged plant percent cover. Standardized continuous covariates + regularized logistic regression; all models use the **same folds and samples**.

Brier scores are mean held-out squared prediction errors, site-balanced so a frequently sampled wetland does not dominate. The resampled difference intervals below are 2000 **site-level bootstraps conditional on predictions**, **not** fully refitted uncertainty bounds and **not** causal/confirmatory hypothesis tests.

## Observed acoustic-prediction results

| Predictor tier | Site-balanced CV Brier (smaller better) |
|---|---:|
| W0 broad weather + season | **0.2080** |
| W1a + water depth only | **0.2037** |
| W1b + wetland management/class only | **0.1822** |
| W1 + water depth AND wetland class | **0.1742** |
| W2 + emergent cover on W1 | **0.1753** |
| W2alt + submerged cover on W1 | **0.1862** |
| W3 + emerged + submerged + plant taxa richness on W1 | **0.2025** |

- The W1 combined **Brier gain over W0 = +0.03384**, conditional cluster-bootstrap interval **+0.00920 to +0.05727**. Do not assign this to water depth alone.
- Depth alone improves **+0.00434** (interval **−0.00817 to +0.01692**); site management/class alone **+0.02585** (interval **−0.00012 to +0.04868**). The combined gain is greater, but the class component is the main observed improvement in this dataset.
- **Emergent cover added to W1 does not improve held-out prediction**: Brier gain **−0.00115** (interval **−0.00641 to +0.00391**). Submerged cover also does not improve it (**−0.01197**, interval **−0.03737 to +0.00297**). Fitting a more complex plant panel is worse (**−0.02829**, interval **−0.05445 to −0.00781**).
- This is an important **negative constraint** on naïve “more emergent cover → stronger choruses”. These results do **not** refute habitat architecture as a mediator; cover (%) is not stem density, plant taxon, inundated stem area, or predation refuge.
- The sensitivity endpoint **visual** differs substantially: W0 **0.2084**, W1 **0.2272**, W2/emergent **0.2298**; adding wetland class/depth worsens predictions. Sound-producing adults vs directly observed frogs/other stages are *not interchangeable detections*.

## History audit (single spring only)

All 29 sites had ≥2 acoustic visits. First visit positive in **7/29** sites; among 100 later visits, acoustic-positive fractions were **0.3929** at sites first positive versus **0.3056** at sites first negative. This is descriptive detection persistence in one season, **not** strong chorus recurrence across years, individual philopatry, or evidence for a stable frogcs spatial template.

## Crucial non-estimabilities

- Only **2/29** sites were fish positive, so `fish × emergent-cover` predator refuge moderation is **not estimable reliably**. Do not report a coefficient.
- There is no oviposition-success/larval-survival data, no true ordinal CallingIndex, no dragonfly/salamander larval predator census, no within-site interannual vegetation change, and no ten-stop route configuration. Hence no new frogcs `C = Σ choose(k_i−1, 2)` value.
- The source covariates are static site values and study class; the observed improvement could be other stable habitat attributes, sampling context or restoration history. Causal vegetation inference needs repeated plant/hydrology measurements or randomized interventions.
- One study, one season, site-blocked rather than study-/year-blocked CV; these are exploratory results. There are 7 model tiers including post-readback diagnostic comparisons and no independent correction for multiplicity.

## Cross-system implication for the proposed macroecology

The RC6 fixed prior-site acoustic concentration remains unexplained by its assessed broad-weather comparator; this 2024 external pilot independently confirms that **site identity/class can improve acoustic prediction beyond weather**, but does not identify plants or predators as the mechanism. Hamer et al. (2021; DOI 10.1002/eap.2293) independently reports a positive fish×emergent interaction for *occupancy*; that is a different estimand and cannot be pooled with the Hungarian acoustic-detection Brier difference.

The next available high-priority independent target is the new NPS Great Lakes 2016–2023 fixed-site acoustic package (DOI 10.57830/2320505; 14 taxa, 7 parks), for an actual multi-year prior-site strong-call test if record schema/source audit succeeds. For plant causality, prioritize year-to-year emergent structural change, fish/odonate stage guilds and within-pond intervention designs; do not replace missing predator data by GloBI links.
