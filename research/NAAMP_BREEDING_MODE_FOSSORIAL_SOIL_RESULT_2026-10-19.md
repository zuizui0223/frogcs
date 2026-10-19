# NAAMP soil-water effect is NOT explained by the measured terrestrial-egg or named adult-burrower taxa

2026-10-19. Exploratory NAAMP study **separate from the frozen JAE manuscript**. Nothing here establishes egg-laying, offspring survival, demographic recruitment or cognitive memory; recorded calling index remains acoustic behavior.

## Biological question

**Does the observed broad association of ERA5 subsurface soil moisture with strong calling mainly reflect frogs laying eggs underground, or the subset of frogs living in burrows?**

Three ecologically different stages must not be conflated:

1. **Adult terrestrial/burrowing survival and emergence.** Burrowing spadefoots such as *Scaphiopus holbrookii* emerge after rain and lay eggs in temporary **surface-water** pools. *Pseudacris streckeri* also burrows underground but deposits eggs in shallow surface water.
2. **Terrestrial oviposition.** *Eleutherodactylus planirostris* lays terrestrial eggs in moist sheltered soil/litter and has direct development without free-swimming tadpoles; this species is actually present in the NAAMP taxon list, but its quiet call is easy to miss.
3. **Hydroperiod, terrestrial hydration and reproductive readiness.** These are plausible alternative explanations for pooled soil-water/calling links in mostly wetland-associated taxa. None is isolated by 0.25° ERA5 or monthly MODIS land cover; no eggs or physiological hydration are observed.

Sources:
- [USGS NAAMP survey and site construction](https://www.usgs.gov/centers/eesc/science/north-american-amphibian-monitoring-program)
- [North Carolina Wildlife: Eastern spadefoot emerges from soil, breeds in temporary pools](https://www.ncwildlife.gov/species/eastern-spadefoot)
- [Missouri/Illinois field guide: Pseudacris streckeri burrows but lays eggs under water](https://www.ideals.illinois.edu/items/120614/bitstreams/395779/data.pdf)
- [UF/IFAS: Greenhouse frog moist terrestrial egg deposits and direct development](https://ask.ifas.ufl.edu/publication/UW527)
- [Pseudacris life-history synthesis: genus breeds in aquatic environments](https://pmc.ncbi.nlm.nih.gov/articles/PMC8394169/)
- [Rainfall and hydroperiod can predict actual spawning differently from larval survival](https://pmc.ncbi.nlm.nih.gov/articles/PMC8956532/)

## Step 1. SHA-pinned original taxon availability gate (executed)

All 7,848 NAAMP eligible surveys, source Runs/Stops/Counts each verified against original SHA256. Genus-level adult-burrower group was fixed before these results: Scaphiopus and Spea (4 operational taxa in eligible survey records).

- Strong CI≥2 source records for the four named spadefoot taxa: **83** across **32 routes**, 13 years.
- All strong-call source rows across any taxa: **67,219**; spadefoot share **0.1235%**. Precommitted sufficiency minimum 200 source records in ≥30 routes: **failed the record count**; no spadefoot-specific soil interaction fitted.
- [Execution and ten unit tests](https://github.com/zuizui0223/frogcs/actions/runs/39201606641).

A subsequent **post hoc, species-list-informed** source extension examined *Eleutherodactylus planirostris* (terrestrial direct developing eggs) and *Pseudacris streckeri* (adult burrower, aquatic eggs):
- **Greenhouse frog**: six records with CI≥1, **zero** CI≥2 strong-chorus records in eligible surveys.
- **Strecker's chorus frog**: one CI≥2 record.
- All five documented adult-burrowing, aquatic-egg taxa combined: **84** strong-chorus source records across all eligible runs.
- [Subsequent source-only test with seven unit tests](https://github.com/zuizui0223/frogcs/actions/runs/39201940702).
- No attempt to classify all remaining taxa as nonfossorial; other species may use terrestrial retreats/burrows.

## Step 2. Same 4,045 pairs, same ERA5 regression, direct leaveout (executed)

The original full **4,108 NAAMP paired** strong-new-taxon×stop incidence counts were reconstructed exactly from the source-verified original Calls/Stops records, using the existing rain-recency assignment. Only *after* this exact agreement was confirmed were six **named** taxa left out.

The primary model retains the **same 4,045 physical-station-stable survey pairs, 563 routes**, and prior original within-route demeaned CR1 OLS design: 0–7 cm / 7–28 cm common change, depth-contrast control, rain recency/amount, season/year lag, temperature, VPD, and RunNumber. Same equal sample and geographic distribution, no re-extraction or soil model tuning.

| CI≥2 new taxon × listening-stop count response | ERA5 common soil delta +0.01 m³/m³ coefficient | 95% route-cluster CI |
|---|---:|---:|
| ALL operational taxa | **+0.0990725** | [0.0653954,0.1327496] |
| Remove five named burrowing aquatic breeders + greenhouse frog | **+0.0971567** | [0.0637124,0.1306010] |
| Only six named taxa (difference, post hoc diagnostic) | +0.0019158 | [-0.0008157,+0.0046472] |

In the stable SiteID sample, **76 of 13,347 new strong-chorus taxon×stop counts = 0.5694%** were from the six named taxa; those 76 events appeared in 34 pairs across 21 routes. The direct-developing terrestrial egg species contributed **zero**.

**Interpretation:** These specifically verified reproductive-mode taxa are not generating the pooled positive soil-water association. The 1.9% change in the coefficient after exclusion is not a mechanistic attributable fraction; it is a same-data leaveout sensitivity. No biology of unclassified taxa was assumed.

[Actual full-range NAAMP leaveout CI: SUCCESS, six tests](https://github.com/zuizui0223/frogcs/actions/runs/39202528021). [Archived aggregate artifact](https://github.com/zuizui0223/frogcs/actions/runs/39202528021/artifacts/12164187167).

## Strongest biological interpretation remaining

Observed: route-scale ERA5 soil moisture differences associate positively with **male reproductive calling**, including after same-route and locally visible MODIS water control. The most defensible ecological hypothesis is a **breeding-opportunity filter**: the surrounding terrestrial/moist substrate state and longer-lived suitability of nearby reproductive habitats might contribute to the probability of many species entering chorusing. This remains a hypothesis, not a demonstrated pathway.

What would discriminate mechanisms:

- **Direct mating/oviposition**: count egg masses or record amplexus, clutch deposition, juvenile cohorts and independent detection effort, at exactly matched wetland visits. Acoustic CI is insufficient.
- **Adult burrowing/emergence or hydration**: use independent pitfall/individual tracking, locally measured soil profiles/soil temperature, weather and water loss/hydration data; compare named fossorial vs aquatic/arboreal breeding modes after adequate route-level support.
- **Hydroperiod vs adult cue**: measure pond depth/water permanence and post-oviposition drying alongside time-resolved acoustic activity, separately modelling adult calling vs egg/larval survival.
- **Terrestrial eggs**: study terrestrial direct-developing amphibians independently; NAAMP predominantly samples near-wetland listening positions and greenhouse frog call detection is poor.

**No intervention, actual mating, egg or tadpole observation is in the analyzed dataset. There is no demonstration of offspring success or of spadefoot-specific soil effect.** Original JAE main remains unchanged.
