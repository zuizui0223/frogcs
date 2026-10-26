# GloBI globally geolocated interaction records — six-region source audit v0.1

2026-10-25, exploratory prespecified **after** reading country-level selected GloBI×GBIF pilot: `research/results/global_globi_gbif/observed_results.json`.

### Why
The country-level 63-edge live API sample was highly European and country-scale co-reporting cannot identify local interactions. GloBI also provides `latitude` and `longitude` of source interaction records. Query six non-mutually-exclusive **bounding boxes**, record source/target life stages and bibliographic citation. This provides an **independent, georeferenced data provenance audit**, not proof of attack frequency or a representative random world sample.

### Retrieval
Bounding boxes in lonmin,latmin,lonmax,latmax (not precise continents):
- North America: -170,5,-50,83
- South America: -83,-56,-35,5
- Europe/Mediterranean: -25,31,45,72
- Africa: -20,-36,52,31
- Asia: 45,-5,180,80
- Oceania: 110,-50,180,-5

Any geometrical overlap yields duplicates; deduplicate by source occurrence IDs when provided, else source citation + taxon names/stages + rounded coordinates. BBoxes **do not define perfect continents** and no counts are normalized by wetland area, GBIF effort or country reporting. `bbox` API is documented at https://github.com/globalbioticinteractions/globalbioticinteractions/wiki/api .

For each box, query 8 direction filters: Anura→Odonata, Odonata→Anura, Anura→Caudata, Caudata→Anura, Anura→Dytiscidae, Dytiscidae→Anura, Anura→all prey and all predators→Anura. `includeObservations=true`, `interactionType=eats`, 0..199 max per query (bounded live API, nonrandom). Some queries may return `preysOn`; retain it but exclude parasite links.

### Fields + validation
- `source_taxon_name,source_taxon_path,source_specimen_life_stage,interaction_type,target_taxon_name,target_taxon_path,target_specimen_life_stage,latitude,longitude,study_citation,source_specimen_occurrence_id,target_specimen_occurrence_id`.
- Coordinates numeric, geographic bounds valid, not near null island (0,0); both names exact binomial, role taxonomy checked from pipe-separated paths.
- Citation required. A record with an iNaturalist observation link has an image/photo-like record, but not independently audited confirmation of the attack.
- Actor stage and prey stage classes kept as given; unknowns and -999 are missing.
- Source study/observation/event duplicates not independent; compile source counts, strict both-stage counts, global latitude-band observed *link examples*, candidate reciprocal species pairs.
- No global prevalence/rate/predation flux is estimated; geographic reporting is strongly biased.

### Main deliverable
`research/results/global_globi_geo/geolocated_interaction_records.csv` plus summary and sources, reproducible GitHub Actions. Compare distribution of **documented spatially anchored records** with previous GBIF **possible country-level ranges** without turning potential overlap into verified local attack. Do not infer rainfall, emergent-plant structure or frog chorus from the GloBI point.
