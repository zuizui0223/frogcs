# Environmental-factor coverage audit v0.1

## Question

Has the current NAAMP analysis directly or indirectly addressed the major environmental factors known to influence frog calling, and what environmental explanations remain viable for the residual within-taxon spatial configuration?

This is a **coverage audit**, not a reopened outcome analysis. It does not introduce a new endpoint, weather window, hydrological mechanism family, threshold or claim escalation.

## Bottom line

No study can claim to have measured **all** environmental causes, and the current manuscript should not do so.

The present NAAMP chain has directly or indirectly addressed most broad route-night atmospheric, seasonal and observation-process explanations. The strongest remaining environmental gap is **dynamic local wetland state**: hydroperiod, water level, soil moisture, fine-scale inundation and related site-level hydrology were not directly measured for the focal surveys.

The existing evidence nevertheless narrows what an omitted environmental explanation would have to look like. It cannot be only a broad route-wide weather shift or a static site-quality difference. To reproduce the observed residual, a remaining environmental driver would need to vary on the survey-event timescale, differ among sites within a route, have taxon-specific effects, and preserve or reinforce recurrent taxon-specific site selectivity.

## Coverage matrix

| Environmental / observation axis | Current treatment | Coverage | Residual concern |
|---|---|---|---|
| Rainfall recency | `DaysSinceRain`; linear principal models and nonlinear `log(1 + DaysSinceRain)` in flexible common-environment model | **Direct, strong** | Rainfall is observational; recency can proxy other wet-state changes |
| Antecedent rainfall amount | 72-h ERA5 precipitation, species-specific cross-fitted response | **Direct, strong** | Gridded precipitation is not local pond hydrology |
| Future rainfall placebo | non-overlapping +1 to +72 h ERA5 window | **Direct negative control** | Similar fit to antecedent amount limits temporal-mechanism interpretation |
| Current/light rain | earlier branch-preserved negative control | **Examined, secondary provenance** | Not a canonical principal comparator |
| Air temperature | route-run mean air temperature; linear and nonlinear terms; rain-recency × temperature interaction | **Direct, strong** | Does not equal local water temperature |
| Season / phenology | day-of-year terms, first and second annual harmonics, RunNumber, State | **Direct/indirect, strong** | Explicit astronomical photoperiod not separately parameterized |
| Photoperiod / daylength | largely deterministic from date and latitude; represented indirectly through seasonal terms | **Indirect** | Species-specific photoperiod effects not isolated as a separate covariate |
| Relative humidity | earlier branch-preserved individual and joint humidity-pressure diagnostics | **Examined, secondary provenance** | No canonical site-level humidity series; microclimate can differ among stops |
| Surface pressure / pressure fall | earlier branch-preserved diagnostics after rain recency and 72-h amount | **Examined, secondary provenance** | Local pressure is largely route-wide and is not a strong candidate for selective site placement by itself |
| Wind | start/end Beaufort codes in detection-augmented common-environment model | **Direct, strong for detection/common-cause sensitivity** | Fine-scale gusts/masking not captured |
| Ambient noise / major interruptions | Noise / MassNoiseIndex / TimeOut sensitivities | **Direct, strong for observation process** | Unrecorded masking remains possible |
| Observer identity / hearing | same-observer restriction and hearing-impairment fields | **Direct, strong for observation process** | Within-observer perceptual error remains possible |
| Time of night / route progression | not a separate species-specific time-of-night term; leave-one-taxon-out stop-night hotness can absorb common route-order/time progression | **Indirect / partial** | Taxon-specific diel response could remain |
| Moonlight / lunar phase | not directly modelled | **Not direct** | A route-wide lunar effect alone would resemble a broad taxon-night shift; local canopy × moonlight interactions could remain |
| Hydroperiod | no survey-night local hydroperiod measurement | **Not direct — major gap** | **High-priority residual environmental candidate** |
| Water level / inundation | no survey-night local water-level measurement | **Not direct — major gap** | **High-priority residual environmental candidate** |
| Soil moisture / local wetness | no site-level survey-night measure | **Not direct — major gap** | **High-priority residual environmental candidate** |
| Fine-scale rainfall heterogeneity | ERA5 is route-scale gridded precipitation, not stop-scale rainfall | **Not direct** | Could contribute through local wetting differences |
| Water temperature | air temperature is represented; local water temperature is not | **Not direct** | Potentially important for species with aquatic calling/breeding microhabitats |
| Salinity / pH / conductivity / water chemistry | not directly measured | **Not direct** | Likely site- and system-specific; stable components can be partly absorbed by prior site history |
| Wetland type / canopy / vegetation / elevation / static habitat | not all entered as explicit covariates in the focal comparator | **Indirectly represented** | Strictly-prior species × physical-SiteID propensity absorbs persistent site suitability, but not temporal habitat change |
| Dynamic vegetation / ephemeral habitat state | not directly measured | **Not direct** | Could interact with local hydrology and taxon-specific habitat requirements |
| Generic contemporaneous stop condition shared across taxa | leave-one-taxon-out stop-night hotness estimated from other taxa | **Strong indirect falsification** | Does not capture environmental effects that are strongly taxon-specific |
| Uniform species × route-night environmental state | cross-fitted scalar-state generator | **Strong structural falsification** | Sufficient for concentration but predicts too much near/far dependence; a uniform all-stop shift is too coherent |

## What the literature says matters

The environmental axes above are not hypothetical conveniences.

- Oseen & Wassersug (2002) explicitly considered air and water temperature, rainfall, barometric pressure, relative humidity and wind velocity.
- Brooke, Alford & Schwarzkopf (2000) considered temperature, rainfall, moon illumination/visibility, humidity and barometric pressure and found both shared day-level and persistent local variation.
- Recent passive-acoustic work has identified temperature, relative humidity, antecedent rainfall and moonlight as relevant in some species.
- Hydropattern/inundation studies show that water availability and wetland inundation can strongly structure frog calling and assemblage activity.

Thus hydroperiod/water state is a biologically serious omitted axis rather than an arbitrary post-hoc candidate.

## Why broad unmeasured weather is no longer the main alternative

Several results jointly constrain the form of any omitted common-environment explanation:

1. Flexible nonlinear rain recency, temperature, season and their interaction removed only a small part of the focal residual.
2. Actual antecedent 72-h rainfall amount also left the focal residual.
3. Earlier humidity/pressure/current-rain diagnostics did not yield a dominant alternative trigger.
4. Hearing/noise/wind adjustment left the dependence essentially unchanged.
5. A leave-one-taxon-out stop-night term estimated from **other taxa** substantially improved prediction of shared stop conditions but did not remove target-taxon concentration/dependence.
6. A transferable **uniform species-night scalar state** was too spatially coherent across the ten stops.
7. Deep activation preferentially aligns with recurrent taxon-specific strong-chorus locations beyond fixed current site propensity.

Therefore a remaining environmental explanation cannot be merely “another route-wide weather variable”. It must be **event-varying, spatially non-uniform and taxon-specific in effect**.

## Most plausible remaining environmental family

The strongest unresolved family is:

> **dynamic local hydrology × taxon-specific breeding requirements**

Examples include:
- survey-night water level;
- recent inundation of individual wetlands;
- hydroperiod state;
- local soil moisture / shallow-water availability;
- small-scale rainfall/runoff differences;
- site-specific water temperature or chemistry where biologically relevant.

This family has exactly the structure still allowed by the data: a broad favourable period can occur at route scale while only a recurrent subset of sites enters the local state suitable for a particular taxon.

This is compatible with the working description:

> **broad activation + local filtering**

It is **not identified** by the current data.

## Why this should not be reopened casually in NAAMP

A retrospective site-level hydrology overlay is not automatically trustworthy.

The pinned NAAMP coordinate table contains known gross transcription errors, including impossible within-route distances. The exact-distance analysis was therefore explicitly withdrawn from biological interpretation. Any site-level remote-sensing or raster hydrology reconstruction would first require an externally validated coordinate-repair table fixed without reference to frog outcomes.

The existing science lock also prohibits adding new same-data hydrological mechanism families in response to the residual.

Accordingly, the present manuscript should **not** be delayed for another environmental fishing exercise.

## Future test that would actually discriminate mechanisms

The clean next study is not “add more weather covariates”. It is a fixed-site dataset with verified coordinates and direct or independently reconstructed local wetland state.

A strong design would measure, before looking at the configuration endpoint:

- local water level / inundation state;
- hydroperiod or recent wet/dry transition;
- soil moisture / runoff proxy;
- air and water temperature;
- humidity and pressure;
- time of night;
- moon illumination;
- stable habitat/site descriptors;
- the same repeated taxon × physical-site calling matrix.

Then test whether local hydrology removes the configuration residual after response magnitude and prior site history are conditioned on.

## Authorized conclusion after this audit

Do **not** say:
> all environmental factors have been excluded.

Do say:
> **The strongest measured atmospheric, seasonal and observation-process explanations are insufficient. The leading unresolved environmental alternative is a temporally dynamic, spatially heterogeneous local wetland state—especially hydroperiod/water-level variation—with taxon-specific effects.**

That distinction preserves the current paper's contribution while identifying the most informative next mechanistic test.
