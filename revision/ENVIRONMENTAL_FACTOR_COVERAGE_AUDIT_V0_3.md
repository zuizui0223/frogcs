# Environmental-factor coverage audit v0.3

## Status

This audit supersedes `revision/ENVIRONMENTAL_FACTOR_COVERAGE_AUDIT_V0_2.md`.

It is a **coverage and mechanism-shape audit**, not a reopened outcome analysis. It does not add a new endpoint, weather window, hydrological reconstruction, threshold, model selection exercise or claim escalation.

Literature coverage was rechecked through 2026 against primary frog-calling studies spanning meteorology, hydrology, diel/lunar effects and local habitat state.

## Question

Have the major environmental drivers of frog calling been examined strongly enough that the remaining within-taxon spatial configuration can be treated as more than an obvious omitted-weather artefact?

## Bottom line

No observational study can claim that **all environmental causes have been excluded**.

The current NAAMP chain has directly or indirectly addressed most major **broad route-night atmospheric, seasonal and observation-process** explanations known from the frog-calling literature.

The strongest unresolved environmental family is:

> **dynamic local wetland state × taxon-specific breeding requirements**

especially survey-event variation in:
- hydroperiod / recent wet-dry transition;
- water level / inundation / shallow-water extent;
- local soil wetness / runoff / fine-scale rainfall;
- water temperature;
- temporally changing calling substrate or emergent vegetation.

The structural reason matters more than the length of the covariate list. Any omitted driver capable of reproducing the focal residual must be:

1. variable among survey events;
2. non-uniform among stops within the same route;
3. taxon-specific in effect; and
4. able to preserve or reinforce recurrent taxon-specific site selectivity.

A route-wide atmospheric cue by itself does not have that geometry.

## Literature-verified environmental axes

### Broad meteorology

Oseen & Wassersug (2002), *Oecologia* 133:616–625, DOI 10.1007/s00442-002-1067-5, jointly examined:
- air temperature;
- water temperature;
- rainfall;
- barometric pressure;
- relative humidity;
- wind velocity;
- time of day.

They found species-specific combinations of drivers, with water temperature especially important in summer breeders and time of day important in spring breeders.

Brooke, Alford & Schwarzkopf (2000), *Behavioral Ecology and Sociobiology* 49:79–87, DOI 10.1007/s002650000256, examined:
- temperature;
- rainfall;
- moon illumination / visibility;
- humidity;
- barometric pressure;
- local and day-level variation.

Their design is especially relevant because shared day-level conditions coexisted with persistent site-to-site heterogeneity.

Chirino et al. (2025), *Philosophical Transactions B* 380:20240050, DOI 10.1098/rstb.2024.0050, used a causal-model PAM framework and found direct effects of:
- temperature;
- relative humidity;
- prior 24-h rainfall;
- moonlight;
while current rainfall was not a strong direct driver.

These studies reinforce that weather effects are species-specific and can operate at multiple temporal scales.

### Local hydrology and water state

Brinley Buckley et al. (2021), *Ecological Indicators* 121:107171, DOI 10.1016/j.ecolind.2020.107171, paired acoustic monitoring with time-lapse habitat imagery and found **hydropattern**, vegetation and weekly precipitation to be important predictors of boreal chorus frog calling.

Wheeler et al. (2018), *Journal of Herpetology* 52:289–298, DOI 10.1670/17-103, found **water depth and water temperature** influenced calling phenology of a lotic-breeding frog, with timing differing among sites and years.

Guzy et al. (2012), *Journal of Applied Ecology* 49:941–952, DOI 10.1111/j.1365-2664.2012.02172.x, recorded wetland water depth and reconstructed hydroperiod while monitoring frog choruses across repeated wetlands.

Sarker et al. (2022), *Ecological Indicators* 145:109640, DOI 10.1016/j.ecolind.2022.109640, showed that hydrological inundation can reorganize frog richness and chorusing across sites.

Together these studies make **survey-event local water state** a biologically serious omitted axis, not a generic residual placeholder.

### Diel, lunar and local-light effects

Time of day is important for some taxa (Oseen & Wassersug 2002), and moonlight can alter calling in species-specific ways. Chirino et al. (2025) found reduced calling with greater moonlight in *Agalychnis lemur*.

These factors are therefore real, but their geometry matters:
- a route-wide time or lunar cue alone is too broad to explain recurrent taxon-specific site selectivity;
- it becomes more plausible through local modifiers such as canopy, edge structure or microclimate.

### Habitat and water chemistry

Static wetland type, vegetation, canopy, morphology and water chemistry can influence habitat suitability.

However, in the focal NAAMP comparator, persistent taxon-specific site suitability is already partly represented by strictly-prior species × physical-SiteID propensity.

Therefore the environmentally relevant omitted component is primarily **event-specific change or interaction**, not static site class alone.

## Coverage matrix

| Environmental / observation axis | Current NAAMP treatment | Coverage | Residual priority |
|---|---|---|---|
| Rainfall recency | DaysSinceRain; linear principal response + nonlinear flexible model | **Direct, strong** | Low as sole explanation |
| Antecedent rainfall amount | 72-h ERA5 precipitation; species-specific cross-fit | **Direct, strong** | Low as sole explanation |
| Future rainfall amount | non-overlapping +1 to +72 h placebo | **Direct negative control** | Weakens antecedent-specific mechanism |
| Current/light rain | earlier branch-preserved diagnostic | **Examined, secondary** | Low |
| Air temperature | linear + nonlinear; rain-recency × temperature | **Direct, strong** | Low as sole explanation |
| Season / day of year | RunNumber, State, annual harmonics | **Direct/indirect, strong** | Low as sole explanation |
| Photoperiod / daylength | absorbed largely by seasonal/date terms | **Indirect** | Low as sole explanation |
| Relative humidity | earlier individual + joint humidity-pressure diagnostics | **Examined, secondary** | Low–medium if local microhumidity |
| Barometric pressure / pressure fall | earlier diagnostics after rainfall controls | **Examined, secondary** | Low as sole explanation |
| Wind | Beaufort code in detection-augmented comparator | **Direct** | Low; residual remains |
| Recorded noise / interruptions | Noise / MassNoiseIndex / TimeOut sensitivities | **Direct** | Low; residual remains |
| Observer / hearing | same-observer + hearing fields | **Direct** | Low |
| Generic stop-night condition | leave-one-taxon-out stop hotness from other taxa | **Strong indirect falsification** | Low for generic shared condition |
| Uniform taxon × route-night state | cross-fitted scalar-state generator | **Strong structural falsification** | Too spatially coherent |
| Exact stop time / taxon-specific diel response | no direct species-specific stop-time function | **Partial** | **Medium** |
| Moon phase / moonlight | not direct | **Not direct** | **Low–medium**, mainly with local modifiers |
| Fine-scale rainfall heterogeneity | ERA5 is gridded route-scale weather | **Not direct** | **Medium–high** via local hydrology |
| Hydroperiod / wet-dry transition | no survey-event local measure | **Not direct** | **Highest** |
| Water level / inundation | no survey-event local measure | **Not direct** | **Highest** |
| Soil moisture / runoff / local wetness | no stop-level event measure | **Not direct** | **High** |
| Water temperature | air temperature only | **Not direct** | **High / taxon-dependent** |
| Dynamic vegetation / calling substrate | no event-level local measure | **Not direct** | **Medium** |
| Static wetland type / canopy / elevation | prior SiteID propensity absorbs persistent suitability partly | **Indirect** | Low alone |
| pH / conductivity / salinity | not direct | **Not direct** | Low–medium; likely system/taxon specific |
| Artificial/local light | not direct | **Not direct** | Low alone; mostly persistent/site-specific |
| Snowmelt / ice-out | not direct | **Indirect through season**, locally relevant in northern taxa | Medium in restricted systems |

## What has actually been falsified

### Flexible broad environment

Nonlinear rain recency, nonlinear temperature, annual seasonality and the tested rain × temperature interaction removed only **11.4%** of the principal concentration residual.

### Actual rainfall amount

Antecedent 72-h ERA5 rainfall amount still left a large positive residual.

### Temporal specificity of rainfall amount

A non-overlapping future-rain model predicted nearly the same concentration as the antecedent rainfall-amount model while both failed to reproduce the observed configuration.

Therefore the small increment from rainfall amount cannot be interpreted as evidence for a uniquely antecedent 72-h rainfall mechanism.

### Measured detection conditions

Hearing impairment, major-noise timeout and wind removed only **4.8%** of the same-sample concentration residual and did not reduce dry-route-silent residual dependence.

### Generic local common cause

A leave-one-taxon-out stop-night term derived from other taxa improved prediction of shared stop conditions but did not remove the target taxon's configuration/dependence residual.

### Uniform taxon-night state

A transferable scalar taxon × route-night state could reproduce concentration but predicted too much near/far dependence. A simple all-stop switch is therefore structurally too coherent.

## Ranked unresolved environmental alternatives

### Rank 1 — dynamic local hydrology × taxon-specific breeding requirement

**Priority: highest.**

Includes:
- hydroperiod state;
- recent inundation;
- water level / shallow-water extent;
- soil moisture / runoff;
- fine-scale local rainfall;
- water temperature;
- event-specific aquatic microhabitat availability.

Why it fits:
- changes among nights/years;
- differs among nearby sites;
- affects taxa differently;
- can repeatedly favour the same taxon-specific locations;
- is independently known to influence calling and breeding phenology.

This is the only major environmental family that naturally matches all four structural constraints without requiring multiple additional assumptions.

### Rank 2 — taxon-specific diel timing × route progression

**Priority: medium.**

Because NAAMP stops were sampled sequentially, taxon-specific diel timing can create route-position gradients.

Why it is secondary:
- generic route-order/time effects are partly absorbed by stop-night hotness;
- far-lag dependence remains strong;
- exact recurrent SiteID alignment is not naturally predicted by time alone.

A future fixed-site design should record exact stop timestamps.

### Rank 3 — local microclimate / moonlight × canopy or topography

**Priority: low–medium.**

Humidity and moonlight genuinely affect calling in some species.

But:
- route-wide lunar phase is common to all stops;
- broad humidity cues were already examined;
- this family becomes spatially plausible mainly when modified locally by canopy, vegetation or edge microclimate.

### Rank 4 — dynamic habitat structure / calling substrate

**Priority: medium.**

Event- or year-specific vegetation, emergent cover, shallow margins or temporary calling substrate can change site suitability.

This could be partly coupled to hydrology and should be measured jointly rather than treated as an independent broad-weather variable.

### Rank 5 — static habitat / water chemistry alone

**Priority: lower as sole explanation.**

Static site differences are partly absorbed by prior species × SiteID history.

Water chemistry can matter biologically, but to explain the focal residual it would need substantial event-level variation or interaction with current hydrology.

## Environmental mechanism-shape conclusion

The focal residual does **not** show that environment is unimportant.

It shows:

> **The strongest measured broad atmospheric, seasonal and observation-process variables do not determine the realised taxon-by-place configuration once response magnitude and prior site use are represented.**

The leading environmental explanation is itself a configuration-generating process:

> **a broad favourable taxon-night state filtered through dynamic local wetland conditions that differ among sites and taxa.**

This is the most concrete environmental interpretation of:

> **broad activation + local filtering**

## Decisive future test

Do **not** add more route-wide weather variables to the current NAAMP archive.

Use a future repeated fixed-site system with verified physical coordinates and collect before reading the configuration endpoint:

- local water level / inundation;
- hydroperiod / recent wet-dry transition;
- soil moisture / runoff;
- local precipitation;
- air and water temperature;
- relative humidity and pressure;
- exact observation time;
- moon illumination;
- canopy / vegetation / shallow-water extent;
- stable wetland descriptors;
- observer / detection conditions;
- repeated taxon × site CallingIndex.

Then compare three predeclared generators:

1. **broad weather only**;
2. **local wetland state only**;
3. **broad taxon-night activation × local wetland filter**.

### If local hydrology removes the residual

The current latent configuration resolves largely into environmental filtering.

### If broad-state × local-filter wins

The paper's current working interpretation becomes a directly supported mechanism.

### If substantial residual remains after direct local hydrology

Social facilitation, demographic availability or other taxon-level latent-state processes become much more plausible.

## Authorized conclusion

Do **not** say:

> all environmental factors were tested or excluded.

Do say:

> **Most major broad atmospheric, seasonal and observation-process explanations were directly or indirectly examined and were insufficient. The leading unresolved environmental alternative is dynamic, spatially heterogeneous local wetland state—especially hydroperiod, water level/inundation, local wetness/runoff and water temperature—with taxon-specific effects.**

This is the strongest defensible environmental-coverage statement for the current manuscript.
