# Source-verified real NWI PEM × GBIF species-stage point intersection — feasibility audit

Date: 2026-10-25. **Exploratory source-data readiness**, sample design fixed BEFORE looking at any selected GBIF stage point's NWI class. Not a complete global/US stage habitat test, not a refit of frogcs locked JAE RC6, and not an inference of realized predator–prey interactions.

## Intended transition

From USFWS Cowardin **PEM** (Palustrine Emergent Wetland) actual polygons to precisely georeferenced GBIF frog, salamander and dragonfly stage observation points. This is direct evidence about the feasibility of a **source-backed GBIF×NWI geographical data join**; it is not an actual NPS past-chorus station join because NPS publicly downloaded audio data have only `SiteLocation` codes and no station coordinates. Never assign an NPS/NAAMP station to a wetland simply from a park centroid or an unverified original longitude.

## Source fixed before spatial outcomes

**Source GBIF** `https://api.gbif.org/v1/occurrence/search`; `year=2010,2025`, `country=US`, `hasCoordinate=true`, `hasGeospatialIssue=false`, `occurrenceStatus=PRESENT`. Five species strictly EXACT matched to GBIF, chosen by GloBI wetland research relevance BEFORE any spatial PEM outcomes:

- Odonata `Anax junius`, GBIF 5051741 — stage `Nymph` vs `Adult`;
- Caudata `Taricha torosa`, 2431913 — `Larva` vs `Adult`;
- Caudata `Ambystoma maculatum`, 2431951 — `Larva` vs `Adult`;
- Anura `Anaxyrus boreas`, 2422924 — `Larva` vs `Adult`;
- Anura `Pseudacris regilla`, 2428132 — `Larva` vs `Adult`.

Only aquatic-stage-vs-adult **georeferenced GBIF reporting**; do not call these same-pond juvenile and adult cohorts, or assume all five belong to a confirmed one-pond three-species network.

**Sampling**: for each species×stage, obtain count before outcomes. Fetch up to 300 records per page from *three fixed offsets*: 0, approximately half of searchable records (rounded down to 300), and terminal 300 (or zero if fewer). Note that GBIF occurrence `search` has a 100,000 paginated maximum; clamp offsets accordingly and label incomplete `API_ORDER_BIASED_HEAD_MIDDLE_TAIL`. From each fetched page select up to five **first** distinct occurrence-key records with nonmissing year+month, continental US lat 24–50 and lon −125 to −66, WGS84 coordinates and explicitly reported uncertainty ≤100m. This creates a max **15 points/species×stage ×10=150 primary GBIF points**. Record the number skipped for missing/large coordinate uncertainty, plus retrieved/source totals; no biological absence inference if quota unmet.

**Source USFWS NWI** `https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer`, feature layer `0`: polygon `ATTRIBUTE` Cowardin classification, `WETLAND_TYPE`, `ACRES`. Lookup a strict point `geometry=lon,lat`, inSR=4326, polygon intersects, no buffer or nearest wetland, returnGeometry=false. Polygon key existence is verified independently by layer metadata and official code table layer 1. Source codes `PEM1A`, `PEM1C`, `PEM1F`, `PEM2F` are known official; other PEM modifiers and other Cowardin classes must remain in outputs, no forcible interpolation.

Control API traffic at most **150 NWI requests**, no parallel requests beyond two workers, max 2 retries with backoff, keep request errors as `unknown` rather than `outside NWI`. If polygon overlaps multiple features, preserve count and attributes; primary `on_any_PEM` true if any polygon code begins `PEM`, `on_any_mapped_wetland` if any NWI polygon returned. A **point not inside NWI polygon** is `not matched at point`, NOT `dry habitat` or true absence of wetland. NWI map features can be omitted/unmapped or from another year.

## Predeclared outputs

- Source QA table (10 species×stage source count, sampled, known-precision, accepted, REST failures).
- Species/stage with recorded point-in-mapped-NWI polygons, and specifically PEM1 vs PEM2 vs PEM0 classification, named other Cowardin types.
- Descriptive simple rates **only within selected GBIF source-point sample**. No global/US species-stage percentages, confidence intervals or P-values; sampling is sorted nonrandom and self/third-party site recording effort biases stage ratios. Apparent larva-adult differences may simply reflect observation microhabitat or marked observer GPS uncertainty.
- NWI REST source code provenance + GBIF observation IDs, coords and uncertainty stay in read-only GitHub Action artifact, not entire public repo; commit only small summary and report.
- At most one read-only workflow; stable partial output if a minority of requests fail, but mark any class effect `NONESTIMABLE` if >20% NWI response failures or fewer than five accepted points per stage group.

### Boundary with frogcs and the network

Actual amphibian NAAMP RC6 + NPS annual audio data show historical strong-site use, but **the NPS station coordinates are not in its current public species-audio file**, and NAAMP original coordinates have transcription errors. This analysis is the first real stage×**exact NWI polygon** feasibility audit, not a third validation of chorus reuse or evidence that PEM1A/C/F favors predator-avoidance synchrony. A three-guild causal test still requires **co-surveyed same pond×time** D/S/F stages and predator attack/survival.
