# Environmental explanation of recurring frog chorus locations — pre-outcome design note v0.1
Date: 2026-10-24
Status: **DRAFT / OUTCOME-BLIND**. Not a preregistered hypothesis test, not executed, and not an alteration of the frozen RC6 manuscript.

## Current established environmental resources
- The 2001–2015 USGS Annual NLCD Collection 1.2 site × surveyed-year panel covers 64,779 keys, 129,558 buffers at 100 and 500 m, passing pixel QC.
- 500-m annual habitat is relatively stable at most repeated sites. Same-year annual land-cover categories are retrospectively mapped and may contain observations made after the frog survey; they are **habitat context, not proven preceding-date land state**.
- The 100-m roadside-dominated developed cover exceeds 500-m developed cover substantially; do not label this as frog preference.
- The directly timed Landsat C2 L3 DSWE INWAM scene metadata are findable, but the pixel files were blocked by authentication in current anonymous access. Do not impute water fractions from metadata.
- A strictly preceding-calendar-month, anonymous EC JRC/Google Global Surface Water MonthlyHistory VER5-0 fallback is being tested on real NAAMP stations. Original image band: 0=no observation, 1=nonwater, 2=water. Previous calendar month is chosen so no image within the survey calendar month is used. It is **not a prior 30-day average** or an event-day hydroperiod measurement. Use only with explicit provenance and missingness, and never claim that remote-water absence proves dry breeding habitat.

## Biological contrast (once measured; no frog observations examined now)
Do favourable rainfall conditions reveal reproductive acoustic activity preferentially at historically recurrent species-specific sites because of stable land-cover structure, event-variable inundation, or residual dependence after these environmental factors are represented?

### Endpoint families proposed for a later frozen plan
1. *Recurrent strong-chorus location*, within species × route-season, conditional on prior record eligibility. Habitat composition can predict recurrence but cannot identify individual return or spawning success.
2. *Within-taxon multi-site configuration* on a wetter route survey, conditional on the total magnitude of acoustic activation and strictly prior species × physical-SiteID propensity. Reproduce the **same definition**, not redefine after looking at new environmental coefficients.
3. *Event-water interaction* only where prior-month or scene-level water has sufficient observed pixels, paired with appropriate observation/availability controls. Distinguish stable habitat from temporally varying water, and water from detectability.

### Candidate covariates: no signs assumed
- Primary habitat: 500-m woody+emergent wetland fraction, forest fraction, developed fraction and agriculture fraction. Compositional dependence requires preselected contrasts or regularisation; do not interpret each class as independent.
- Observation-context sensitivity: 100-m developed fraction, plus noise/wind/observer and visit-time covariates where available.
- Temporal water: prior-month 500-m water fraction **among clear observed pixels**, with valid-observation fraction and site-level repeated water-history variability; compare against a same-site multi-year baseline, never 0-as-dry.
- Species/taxon: allow partially pooled heterogeneous responses, avoiding one sign assumed for all species.

### Minimal data gates before opening frog outcome tables
1. Verify full 15-year NLCD source identities, CRS, 30-m categorical values and site-year joins (complete).
2. For each water product, pin the exact version, 0/1/2 meaning, previous-month extraction calendar, 500-m circle definition, missingness thresholds and source checksums (JRC pilot still in progress).
3. Show by-state, by-year, by-habitat and by-month water coverage. Demand sufficient within-site and within-route overlap of both water and non-water pixels; a no-observation pixel is never dry.
4. Define the outcome subset, hypotheses, model specification, null conditioning, negative controls and train/test geography/time blocks **before any new outcome computation**.
5. Label all NAAMP outcome fits exploratory even when cross-fit or held-out by state, because previous RC6 analyses have inspected this same monitoring program. Independent confirmation requires new external response data.

### Suggested technical model sequence — no execution authorised by this draft
M0: species-specific rain sensitivity + prior physical-site activity propensity + dry persistence + activation magnitude control.
M1: M0 + 500-m land-cover context (species-varying slopes).
M2: M1 + strictly previous-month water proxy × species, with valid pixel fraction and month/season controls.
M3: M2 + additional taxon×route-night dependence, only after environmental factors fail.
Evaluate configuration calibration, not just marginal calling accuracy. Failure of M2 with low water coverage is **not evidence against hydrological filtering**.

## Inferential limits
Static vegetation can be a cause, a correlated proxy, or affect sound propagation/detection. Satellite water at 30 m misses small/vegetated ponds; retrospective products can embed scene-processing context. NAAMP route stops were visited sequentially, so no true simultaneity, frog colonisation, movement, or reproductive success may be inferred.

## Source documentation
- [JRC Monthly History v1.4](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory)
- [JRC original download repository](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GSWE/MonthlyHistory/)
- [USGS Annual NLCD 1.2](https://www.usgs.gov/centers/eros/science/usgs-eros-archive-land-cover-annual-nlcd-collection-1-land-cover)
- [USGS DSWE](https://www.usgs.gov/landsat-missions/landsat-collection-2-level-3-dynamic-surface-water-extent-science-product)
