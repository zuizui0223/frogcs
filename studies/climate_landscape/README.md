# Independent climate × terrestrial landscape × frog calling study (v0.1)

**Date: 2026-10-08. Status: response-blind design, not a completed satellite overlay or climate-effect result.**

This is **not** an RC6/JAE manuscript change. The scientific claims and endpoints in `release/jae-multisite-rc6` remain frozen. The prior post-RC6 landscape exploration was closed; this is a separate study proposed by the user. WFTS was not pursued, and is not treated as evidence.

## Core ecological question

Do multi-year hydroclimatic shifts and terrestrial land-cover changes change **where** frog species express breeding-season calling, beyond short-term rainfall-associated acoustic pulses?

Most importantly: do warming/early spring cues become decoupled from seasonally persistent water, and can terrestrial/forest/wetland buffers preserve recurrent calling locations? Calling detections are **not** reproductive success, true breeding, permanent occupancy, abundance, individual memory, or climate-change attribution.

## Data design

- Frog: NAAMP fixed stops surveyed in 2001–2015. Build the longitudinal panel from **all eligible survey opportunities** (7,848 ten-stop standardized runs), *not only* the RC6 4,236 wetter–drier matched comparisons; retain RunNumber, route, year, observation date, observer and skipped/missing status. Raw positive CallingIndex records are sparse: zero only at a genuinely surveyed eligible stop.
- Climate: Daymet V4 (1980–; daily North American interpolated weather) as primary daily time series; PRISM 1981– daily CONUS independent check; GRIDMET/DROUGHT for multi-window SPEI/SPI/EDDI. Use a fixed 1981–2000 baseline and separate 7/30/90-day **strictly prior** weather exposures from prior five-complete-year climate-state anomalies.
- Long-term trend diagnostics: describe 1981–2015 annual meteorological trend independently from frog outcomes. **Never** use a 1981–2015 full-period trend as a look-ahead predictor for an outcome in 2001–2014. Retrospective climate changes are not automatically anthropogenic causal attribution.
- Terrestrial: USGS Annual NLCD Collection 1.2, 1985–2025, 30 m, forests/agriculture/wetlands/imperviousness; Landsat C2 verified cloud-masked acquisition-time reflectance and NDVI/NDWI. Calculate predeclared 250-m local and 1-km landscape buffer fractions around verified physical sites.
- Surface water: JRC monthly water history 1984–2021, 30 m; water/nonwater/**no data** are distinct. It can miss small/canopy ponds and intra-monthly hydroperiod; the most recent fully *pre-survey* observation is a proxy, not water depth or larval survival. Do not use a full-month image including post-survey observations as a presurvey predictor.
- Climate water deficit: TerraClimate is secondary only; its catalog explicitly warns that parent datasets determine trends, so do not use it for independent trend attribution.

## Hard data-quality gate

NAAMP's pinned USGS site-coordinate source contains gross transcription errors, including +83.302° longitude in Route 270107, SiteID 4507 and multiple routes with implausible within-route separations. No site-level 30-m overlay or exact-distance ecology is allowed until a **response-blind, independently verified station coordinate/identity ledger** has been frozen. Do not repair coordinates after viewing species outcomes or relabel station moves as habitat changes. Track site-year identity, coordinate uncertainty, valid pixels, and acquisition dates.

## Three competing generators (to be compared out of block)

1. **Fast cue:** recent rain and seasonal conditions, species-specific response, past acoustic site history.
2. **Local environmental filter:** fast cue plus remotely visible seasonal water, preceding-year land cover, forest and impermeable cover, with hydroclimate state.
3. **Decoupling and buffering:** slower warming/drought × local wetland persistence/terrestrial buffer interactions change the spatial selection of calling sites.

Test both marginal species × site call intensity and **configuration of calling across stops conditional on total activity**. Distinguish acoustic shifts, sites not surveyed, and station relocation. Fit train-era (e.g. 2001–2010) to temporal holdout (2011–2015) and independently held-out geographical blocks; report route-clustered uncertainty. Freeze endpoint, scales, inclusion criteria and model family before outcome reading.

## Result interpretation

There is no new positive frog–climate association to report yet. Climate-driven hydroperiod changes, frog breeding-site drying and call-phenology changes already have a substantial literature; the targeted gap is the multispecies **joint spatial reorganization of acoustic site use** under discordant short-term cues, persistent wetland availability, and terrestrial land-cover change. Detectable calling–water mismatch is not proof of failed reproduction.

This branch is an independent planning lane. It does not re-open earlier failed dispersion/compactness tests and must not modify locked RC6 figures or claim receipts.

## Data and literature entry points

- NAAMP data: https://doi.org/10.5066/F7G44NG0
- USGS Annual NLCD Collection 1.2: https://www.usgs.gov/centers/eros/science/about-annual-nlcd
- Daymet V4: https://developers.google.com/earth-engine/datasets/catalog/NASA_ORNL_DAYMET_V4
- GRIDMET drought: https://developers.google.com/earth-engine/datasets/catalog/GRIDMET_DROUGHT
- JRC monthly surface water: https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory
- USGS multi-year satellite-and-ground sensors caveat: https://www.usgs.gov/publications/multi-year-data-satellite-and-ground-based-sensors-show-details-and-scale-matter
- USGS 2026 hydroperiod/breeding habitat forecast: https://www.usgs.gov/publications/climate-driven-changes-wetland-hydroperiods-predict-losses-habitat-suitability

**Next gate:** verify stations without looking at calling responses; separately export dated climate and remotely sensed covariate tables and their source/QC metadata; only then join the NAAMP responses.
