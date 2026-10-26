# GLOBAL GloBI × GBIF — stage-structured food-web macroecology: empirical v0.1

Date: **2026-10-25**. **New primary science direction** of `frogcs` research branch; original RC6 journal manuscript/main and WFTS decision unchanged. Three actual public-API investigations were completed; none of the derived counts is a global trophic-reversal prevalence or direct vegetation mechanism estimate.

## 1. Science question

> **Where do life-stage-specific trophic roles create possible predator–prey encounters across the world, and how should wetland hydrology, emergent plant architecture and frog chorus history determine which opportunities become realized interactions?**

Avoid a tautology: joining GloBI diet links and GBIF country presence gives **plausibility of geographic overlap**, not actual attack events. The frogcs result on historical species×acoustic-site use is a **separate temporal phenomenon** and must not be assumed to arise from GloBI interactions without data.

## 2. What we actually obtained and computed (2026-10-25)

### A. GloBI directed stage-evidence × GBIF world geographic reporting

[Full receipt](global_globi_gbif/observed_results.json) | [Real-data CI](https://github.com/zuizui0223/frogcs/actions/runs/40186528522) | [Script](../scripts/global_globi_gbif_pilot.py).

- Live public GloBI `includeObservations=true` and 18 aquatic guild directional queries: **1,294 original returned association rows**, **613** records meeting initial two species-binomial, source/target taxon-path, feeding-type and citation eligibility; **391** distinct directed species pairs.
- Pre-geography study/direction-balanced 63 candidate edges, 66 candidate trophic species, 28 primary citation groups; 58 trophic edges survived exact GBIF taxonomic name matching (64 of 66 trophic species were accepted), plus seven aquatic/emergent plant proxy species accepted in GBIF.
- **57/58** surviving links had both partner species georeferenced anywhere in the same *country* with at least five GBIF reports of each, and **56/58** at >=20. These are **co-reported potential distribution overlaps**, not pond observations. 58 countries had at least one potential edge, and 100 countries had at least one of seven emergent-plant proxy taxa recorded.
- Strong apparent European concentration (e.g. France 30 and Germany/Netherlands 28 co-reported opportunity links) is a **source/sampling artifact candidate** from the selected, nonrandom GloBI API head pages and GBIF differential effort, not proof Europe has the richest interaction networks.
- Only **8** of the 58 selected GloBI edges had at least one joint predator/prey life-stage pattern. The first-page source selected some food-web sources multiple times; neither stages nor geographically selected pairs are a representative sample of aquatic interactions worldwide.

### B. Actual **georeferenced GloBI association records** in six broad world boxes

[Corrected empirical receipt](global_globi_geo/observed_results_v2.json) | [Real-data CI](https://github.com/zuizui0223/frogcs/actions/runs/40187148921) | [Geospatial parser and source QA](../scripts/global_georeferenced_globi.py).

- 48 directional source API queries across six macroscale lat/lon boxes, **1,783 retrieved rows**; 878 eligible *source association records* with species-level names, locations and citations before deduplication.
- **729 distinct georeferenced association records**, **346 distinct directed species pairs**, **338 taxon names**, **610 distinct study citation strings**. These counts combine direct-looking iNaturalist-linked observations and literature/metaweb associations that still require source checking.
- Predator and prey developmental stages are both recorded for only **77/729** cases (**10.6%**); at least one side is stage-annotated for **359/729** (**49.2%**). Missing stage records cannot be interpreted as ecological absence.
- After fixing an incorrect counting rule, **18 taxa have candidate conspecific feeding records** (one species eating itself, potentially cannibalism); a **single different-species reciprocal pair** is present in these nonrandom sampled records, *Bostrychia hagedash* ↔ *Xenopus laevis*, whose opposing directions need **source-level biological audit** before claiming actual reverse predation. Thus **no globally representative or source-verified ontogenetic dominance-reversal rate** is authorized.
- The records are highly guild-imbalanced: frogs are often prey of **reptiles and birds**, but georeferenced larval odonate–frog associations are especially sparse under this subset. A lack of georeferenced aquatic predator examples is a **data gap**, not their ecological absence.
- These boxes do not partition world habitats equally. Their sample counts (NA 155, SA 102, Europe/Mediterranean 108, Africa 104, Asia 118, Oceania 142) **are not actual event frequencies** or comparable rates across bioregions.

### C. GBIF life-stage *observations*, tied to the GloBI joint-stage patterns

[Actual GBIF stage result](global_globi_gbif/stage_bridge/observed_results.json) | [Script](../scripts/gbif_global_lifestage_bridge.py) | [Real-data global CI](https://github.com/zuizui0223/frogcs/actions/runs/40187649746).

- Among **64** matched trophic species, GBIF reports **4,508,513** georeferenced 2010–2026 occurrence records with no flagged geospatial issue; **1,277,068** records (**28.3%**) have a mapped raw `lifeStage` label among Adult, Larva/Nymph/Tadpole, Juvenile or Egg categories.
- **61/64** species have at least one such stage annotation, and **51/64** have >=5 reported Adult and >=5 aquatic immature labels. The stage-frequency percentages are not stage biomass or cohort demographic shares because reporting is method- and taxon-biased.
- Of the GloBI-selected edges, the **8 stage-annotated directed species pairs** contain **10 observed joint predator/prey stage configurations**. GBIF country facets for those explicit paired stages yielded a country-level overlap for **all 10/10** configurations at minimum 5 occurrences per partner stage, using 15 unique species × developmental-stage facet queries. **This is a *feasibility* of mapping stage-specific potential ranges, not 10 confirmed attacks or global prevalence**. Important sources still include Preston et al. (2012) California food-web database with inferred links.
- Example: `Anax junius` *larva* → `Anaxyrus boreas` *larva* documented as a database edge, with both stages recorded by GBIF in CA/MX/US (≥1; CA/US ≥5). These are same-country reports from unrelated GBIF sightings, not verified in the same pond or same year.
- Example: reciprocal stage evidence for the `Taricha torosa`–`Anax junius` pair exists in source database, but both directions in a California Quick Pond metaweb require per-edge observation-quality review before biological role-switch claims.

## 3. Plant and environmental layer: what is and is not globally represented

GBIF stage-accepted plant proxies (all 7 matched):
- *Phragmites australis*
- *Typha latifolia* and *T. angustifolia*
- *Schoenoplectus lacustris* and *S. tabernaemontani*
- *Bolboschoenus maritimus*
- *Eleocharis palustris*.

The seven species have GBIF presence reports in **100 countries in total** in this first source-defined sample. **Presence of emergent-plant species at country scale ≠ vegetation density, structural architecture, seasonal inundation or refuge effectiveness at a pond.** No global plant×predator causal coefficient, nor rainfall-by-chorus effect, has been estimated.

Natural/global wetland raster covariates must be added separately (wetland footprint, open water permanence, vegetation structure, hydrological seasonality, aquifer and rainfall). At actual grid scale include source geolocation/detection effort and native/non-native status, ecoregion and year/month; no mixing broad country distributions with fine-scale aquatic encounters.

## 4. Transition to genuinely scalable GLOBAL inference — verified GBIF SQL cube

[Generator](../scripts/build_gbif_global_cube_sql.py) | [Official validated manifest](global_globi_gbif/gbif_bulk_cube/manifest.json) | [1° GBIF SQL payload](global_globi_gbif/gbif_bulk_cube/global_1deg.payload.json) | [0.5° GBIF SQL payload](global_globi_gbif/gbif_bulk_cube/global_0p5deg.payload.json).

- **71 taxon keys** match accepted predator/prey and plant taxa from this pilot.
- Two global grid-and-month/year species occurrence **SQL download queries**, 1° (GBIF_DMSGCode(3600,..)) and 0.5° (1800,..), were produced with `hascoordinate=true`, `hasgeospatialissues=false`, `occurrencestatus='PRESENT'`, `year=2010–2026`, and reported coordinates with uncertainty <=10 km or missing uncertainty handled separately. 
- **Both queries were accepted by GBIF's public validation API (HTTP 201)** on 2026-10-25, verified by [GitHub Actions logs](https://github.com/zuizui0223/frogcs/actions/runs/40187531308). **Neither bulk download was submitted and no bulk download DOI has been produced** because the actual GBIF service requires authenticated request. The source collection remains nonrandom GloBI live API and does not yet meet publication-standard GloBI pinned-full-release requirements.
- **Production transition:** use fully version-pinned GloBI (DOI 10.5281/zenodo.3950589) streamed into DuckDB; submit the validated GBIF aggregate cube with a GBIF account; attach download DOI/citation, then join gridded taxon×stage×year/month opportunity with independent global wetland + hydroperiod + vegetation *structure*, and test alternative network/hydrology generative models with held-out ecoregions and studies.
- For final inference, use multiple ecological grain resolutions (0.5° and 1° exploratory; coarser/finer after power and data quality assessment) and carefully distinguish **observed trophic interactions** from source-documented **potential** edges.

## 5. Integration with frozen frogcs results (separate data hierarchy)

| Scale | Existing supported finding | Global model prediction (NOT yet tested) |
|---|---|---|
| Hour/night | NAAMP 4,236 wetter–drier pairs, rain-associated strong-call activation, conditional within-taxon 10-stop concentration residual +0.2969 | regional rain/hydroperiod shifts possible interactions after stage-specific co-presence |
| Years/same place | independent NPS 2016–2023: prior own-species strong chorus predicts future same-species strong activity after generic other-taxon station and broad hydroperiod/effort | persistent vegetated wetland architecture and predators may act as taxon-specific historical site filters |
| Ontogeny | GloBI has stage-resolved predator→prey candidates; GBIF 51/64 taxa have enough adult and immature observations in this pilot | compare true larval vs postmetamorphic predator roles and opposite-edge opportunity within spatial wetland cells |
| Vegetation | Hamer et al. 55 wetland occupancy: fish × emergent positive in some taxa, Hungary 29 wetland call detection: crude percent emergent gives no marginal out-of-site gain | vegetation **structure × predator guild × stage × water level**, not a universal positive emergent-cover coefficient |

**Main scientific hypothesis:** *Rain-triggered reproductive chorus states are selectively expressed through persistent wetland architecture and history. Those same habitats structure larval and adult trophic encounters, sometimes shifting predator/prey roles across ontogeny.* This is biologically compelling but its **joint causal test remains prospective** until stage-coincident pond measurements and verified plant structure are available.

## 6. Current project status (explicit)

Completed:
1. Real GloBI global source and stage audit; 729 mapped geolocated records in six boxes.
2. Global GBIF exact species match and country reporting; 58 documented edible edges under the selected subset.
3. GBIF **stage-specific** global feasibility audit, actual millions of occurrence records summarized.
4. Two officially validated global 1°/0.5° SQL *query preparations*; no credentials, private data or account access required.
5. Machine-readable JSON receipts, reusable Python analyses and successful GitHub Actions on independent `research/stage-structured-interactions-2026-10-25` branch.

Unresolved:
- GloBI pinned full-dataset ingestion and per-edge independent evidence vetting.
- GBIF bulk spatial cube request (authenticated), its DOI, spatial QA, introduced species, wetland mask and grid-sensitivity.
- Local aquatic vegetation architecture, co-occurring predators and frog egg/larva/chorus temporal linkage; none can be imputed from GloBI/GBIF presence alone.
