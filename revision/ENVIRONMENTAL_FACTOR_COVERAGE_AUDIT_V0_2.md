# Environmental-factor coverage audit v0.2

## Status

This audit supersedes `revision/ENVIRONMENTAL_FACTOR_COVERAGE_AUDIT_V0_1.md`.

It is a **coverage and mechanism-shape audit**, not a reopened outcome analysis. It does not add a new endpoint, weather window, hydrological reconstruction, threshold or claim escalation.

## Question

Have the major environmental drivers of frog calling been examined strongly enough that the remaining within-taxon spatial configuration can be treated as more than an obvious omitted-weather artefact?

## Bottom line

No observational study can claim that **all environmental causes have been excluded**.

The current NAAMP chain has directly or indirectly addressed most major **route-night atmospheric, seasonal and observation-process** explanations known from the frog-calling literature.

The strongest unresolved environmental family is not another route-wide weather variable. It is:

> **dynamic local wetland state × taxon-specific breeding requirements**

especially survey-event variation in hydroperiod, inundation/water level, local soil wetness/runoff, and water temperature.

The key reason is structural. Any omitted driver capable of reproducing the focal residual must be:

1. variable among survey events;
2. non-uniform among stops within the same route;
3. taxon-specific in effect; and
4. able to preserve or reinforce recurrent taxon-specific site selectivity.

A broad route-wide atmospheric cue alone does not have that shape.

## Literature-derived environmental axes

The following are established or repeatedly investigated environmental drivers of anuran calling:

- **air and water temperature, rainfall, barometric pressure, relative humidity and wind velocity** — Oseen & Wassersug (2002), *Oecologia* 133:616–625, DOI 10.1007/s00442-002-1067-5;
- **temperature, rainfall, moon illumination/visibility, humidity and barometric pressure**, together with persistent site-to-site and day-to-day local variation — Brooke, Alford & Schwarzkopf (2000), *Behavioral Ecology and Sociobiology* 49:79–87, DOI 10.1007/s002650000256;
- **day of year/season, daily and lagged temperature, humidity, rainfall at several lag windows and moon phase** across 100 species — Thompson et al. (2022), *Diversity and Distributions* 28:2375–2387, DOI 10.1111/ddi.13634;
- **hydropattern, vegetation and weekly precipitation** for boreal chorus frog calling — Buckley et al. (2021), *Ecological Indicators* 121:107171, DOI 10.1016/j.ecolind.2020.107171;
- **wetland inundation / river-flow arrival** causing species- and site-specific chorus changes — Sarker et al. (2022), *Ecological Indicators* 145:109640, DOI 10.1016/j.ecolind.2022.109640;
- **temperature, relative humidity, preceding rainfall and moonlight** in a recent causal-model PAM study — Chirino et al. (2025), *Philosophical Transactions B* 380:20240050, DOI 10.1098/rstb.2024.0050;
- **photoperiod and temperature**, with no atmospheric-pressure or rainfall effect in one subtropical annual PAM study — Pouso et al. (2026), *Bioacoustics* 35:75–89, DOI 10.1080/09524622.2025.2597859.

These studies support two conclusions relevant to NAAMP:

1. environmental drivers are strongly **species-specific** and scale-dependent;
2. local hydrology/habitat state can matter independently of broad weather.

## Coverage matrix

| Environmental / observation axis | Current NAAMP treatment | Coverage | Can it plausibly reproduce the remaining configuration by itself? |
|---|---|---|---|
| Rainfall recency | `DaysSinceRain`; linear principal response + nonlinear spline in flexible common-environment model | **Direct, strong** | **No evidence**; residual remains |
| Antecedent rainfall amount | 72-h ERA5 precipitation; species-specific cross-fitted response | **Direct, strong** | **No evidence**; residual remains |
| Future rainfall amount | non-overlapping +1 to +72 h ERA5 placebo | **Direct negative control** | No; similar amount-model fit but focal residual remains |
| Current/light rain | earlier branch-preserved diagnostic | **Examined, secondary provenance** | Low support |
| Air temperature | mean route-run air temperature; linear + nonlinear terms; rain-recency × temperature interaction | **Direct, strong** | No; flexible model leaves most residual |
| Season / day of year | RunNumber, State, day-of-year, first and second annual harmonics | **Direct/indirect, strong** | Unlikely as sole explanation |
| Photoperiod / daylength | represented indirectly by date/seasonal harmonics; not isolated | **Indirect** | Route-wide photoperiod alone is structurally too broad |
| Relative humidity | earlier individual and joint humidity-pressure diagnostics | **Examined, secondary provenance** | Broad humidity alone has little support; stop-scale microhumidity remains possible |
| Surface/barometric pressure | earlier pressure / pressure-fall diagnostics after rainfall controls | **Examined, secondary provenance** | Low as sole explanation; largely route-wide |
| Wind | mean Beaufort code in detection-augmented comparator | **Direct** | Does not remove residual |
| Recorded noise / interruptions | Noise, MassNoiseIndex / TimeOut sensitivities | **Direct** | Does not remove residual |
| Observer / hearing | same-observer restrictions + hearing-impairment fields | **Direct** | Observer replacement not required |
| Generic contemporaneous stop condition | leave-one-taxon-out stop-night hotness inferred from other taxa | **Strong indirect falsification** | Shared stop condition improves prediction but leaves target-taxon residual |
| Uniform species × route-night state | cross-fitted scalar latent-state generator | **Strong structural falsification** | Too coherent spatially; predicts excessive near/far dependence |
| Time of night / route progression | not entered as a taxon-specific diel function; partly absorbed by stop-night hotness / route position | **Partial** | **Medium-priority residual candidate** if taxon-specific |
| Moon phase / moonlight | not directly parameterized | **Not direct** | **Low–medium** alone; mostly route-wide, but canopy × moonlight could become local |
| Fine-scale rainfall heterogeneity | ERA5 is route-scale gridded precipitation | **Not direct** | **Medium–high** if it drives stop-specific hydrology |
| Hydroperiod | no survey-event local measurement | **Not direct** | **High-priority** |
| Water level / inundation | no survey-event local measurement | **Not direct** | **High-priority** |
| Soil moisture / local wetness / runoff | no stop-level survey-event measure | **Not direct** | **High-priority** |
| Water temperature | air temperature represented; water temperature absent | **Not direct** | **Medium–high**, taxon/site dependent |
| Dynamic vegetation / emergent cover | no survey-event local measure | **Not direct** | **Medium**, especially through hydrology/calling-site availability |
| Static wetland type / canopy / elevation / habitat | not exhaustively explicit in focal comparator; persistent site quality represented by strictly-prior taxon × SiteID propensity | **Indirect** | **Low as sole explanation**; temporal habitat change remains possible |
| Water chemistry (pH, conductivity, salinity) | not directly measured | **Not direct** | **Low–medium**, probably system/taxon specific and often temporally slower |

## Why "another weather variable" is no longer a sufficient objection

The current evidence already imposes a strong shape constraint on any omitted environmental explanation.

### 1. Flexible measured weather leaves most of the focal residual

Nonlinear rainfall recency, nonlinear temperature, season and the tested rain × temperature interaction moved the principal residual only from 0.2969 to 0.2631: **11.4% removed**.

### 2. Actual rainfall amount is insufficient

On the weather-eligible sample, adding antecedent 72-h ERA5 rainfall amount still left a large positive conditional residual.

### 3. Antecedent specificity is weak

The non-overlapping future-rain model predicts nearly the same concentration as the antecedent amount model, while both fail to reproduce the observed concentration. Therefore a small improvement from rainfall amount is not evidence for a uniquely antecedent rainfall-amount mechanism.

### 4. Humidity / pressure / current-rain alternatives were examined

Earlier branch-preserved diagnostics did not identify current light rain, pressure/pressure fall or humidity as a dominant explanation after the principal rainfall information was represented.

### 5. Measured observation conditions are insufficient

Adding hearing impairment, major-noise timeout and wind removed only **4.8%** of the same-sample concentration residual and left dry-route-silent residual dependence essentially unchanged.

### 6. A deliberately strong generic stop-night environmental proxy is insufficient

The leave-one-taxon-out stop-night term, learned from all other taxa, substantially improved prediction of stop richness but did not remove target-taxon concentration/dependence. Thus a generic contemporaneous site condition shared across taxa is not enough.

### 7. A broad taxon-night switch is too simple

A uniform species × route-night scalar state can reproduce row-count concentration but predicts substantially more spatial coherence than observed. Any remaining common state must therefore be **spatially filtered**.

## Ranked unresolved environmental alternatives

### Rank 1 — dynamic local hydrology × taxon-specific breeding requirement

**Priority: highest.**

Candidate variables:
- local water level;
- recent inundation / wet-dry transition;
- hydroperiod state;
- shallow-water extent;
- soil moisture / runoff;
- fine-scale rain accumulation;
- water temperature.

Why it fits the required geometry:
- varies through time;
- differs among nearby wetlands;
- can affect taxa differently;
- can repeatedly make the same taxon-specific sites favourable.

This family is directly supported as biologically important by hydropattern/inundation studies.

### Rank 2 — taxon-specific diel timing × route progression

**Priority: medium.**

NAAMP stops are sampled sequentially. A species-specific diel response could create non-uniform stop patterns if survey time systematically interacts with stop order.

Why it is not currently the leading explanation:
- generic stop-night hotness can absorb common route-order/time effects;
- residual dependence remains substantial at far stop-number lags;
- the observed recurrent SiteID alignment is not naturally predicted by time of night alone.

A direct stop-time model would nevertheless be valuable in a future dataset with reliable per-stop timestamps.

### Rank 3 — local microclimate / moonlight × canopy

**Priority: low–medium.**

Humidity and moonlight can affect calling in some species, including recent PAM studies. But a route-wide moon or humidity signal alone resembles the already-rejected broad state. It becomes structurally plausible only through local modifiers such as canopy, topography or water-edge microclimate.

### Rank 4 — temporally changing habitat structure

**Priority: medium but secondary to hydrology.**

Vegetation, emergent cover or temporary calling substrate may change among years and sites. Static habitat quality is partly absorbed by prior species × SiteID propensity, so the relevant omitted component is **change**, not fixed habitat class.

### Rank 5 — static site descriptors / water chemistry

**Priority: lower as sole explanation.**

Persistent site differences can contribute to recurrent site use, but the focal comparator already incorporates strictly-prior taxon × physical-site propensity. Static variables would need to interact with event-specific conditions to explain the residual.

## Structural conclusion

The residual does **not** show that environmental factors are irrelevant.

It shows something narrower:

> **The strongest measured broad environmental and observation-process variables do not determine the realised spatial configuration once response magnitude and prior site use are represented.**

The leading environmental alternative is itself a **configuration-generating process**:

> **a broad favourable taxon-night state expressed only where dynamic local wetland conditions cross taxon-specific suitability thresholds.**

This is exactly the form expected under the working description:

> **broad activation + local filtering**

## What would turn this into a new mechanistic discovery

The decisive next test is not another route-wide weather covariate.

A future fixed-site study should measure, before reading the configuration endpoint:

- verified stop coordinates;
- survey-event water level / inundation;
- hydroperiod or recent wet-dry transition;
- local soil moisture / runoff;
- air and water temperature;
- relative humidity and pressure;
- exact stop time;
- moon illumination;
- canopy / vegetation;
- stable wetland descriptors;
- repeated taxon × physical-site CallingIndex.

Then compare three generators:

1. **broad weather only**;
2. **local wetland state only**;
3. **broad taxon-night activation × local wetland filter**.

The third model is the mechanistic prediction generated by the current paper.

If direct local hydrology removes the conditional configuration residual, the current "latent spatial organization" would resolve into an environmental filtering mechanism.

If substantial residual dependence and recurrent-site alignment remain even after direct local hydrology, then social, demographic or other taxon-level latent-state mechanisms become much more plausible.

## Authorized conclusion

Do **not** say:

> all environmental factors were tested or excluded.

Do say:

> **Most major broad atmospheric, seasonal and observation-process explanations were directly or indirectly examined and were insufficient. The leading unresolved environmental alternative is dynamic, spatially heterogeneous local wetland state—especially hydroperiod, water level/inundation and related local wetness—with taxon-specific effects.**

This is the strongest defensible environmental-coverage statement for the current manuscript.
