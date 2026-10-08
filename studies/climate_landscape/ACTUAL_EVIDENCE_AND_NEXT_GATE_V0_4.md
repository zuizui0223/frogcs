# Climate × terrestrial landscape × frog site use: empirical evidence boundary (v0.4)

**2026-10-08. Independent study. RC6 frozen and unchanged.**

## Empirical archive findings already available in other frogcs branches

The preceding remotesensing branches were investigated before creating any new climatic response claim.

- **Static/seasonal water DOES NOT explain the established RC6 concentration mechanism** under the frozen JRC and DSWEmod tests. JRC 250-m analysis (1,881 pairs) changed the concentration residual from 0.17449 to 0.18225, -4.45% removed. DSWEmod 500-m M3-complete 1,649-pair analysis changed residual from 0.50216 (M0) to 0.53022 (M3), -5.59% removed. These tests are **closed, not candidates for retuning**.
- A separate **held-out CI>=2 strong-chorus prediction** showed a positive *incremental* 3-month wetness gain in equal-species mean log loss: +0.010569, route bootstrap 95% [+0.002535,+0.025074]. However, B0->B3 full hydrology gain +0.005690 has interval [-0.005152,+0.021601]; **overall hydrology sequence NOT supported**, and only 15/53 taxa had positive gain (16 negative, 22 non-estimable/zero). The isolated three-month finding must not be promoted into hydrological causal explanation.
- **Coordinate geometry-only quality** from frozen audit: 1,106/1,183 NAAMP coordinate routes eligible, 77 excluded, known gross errors excluded. This does **not** mean independently verified physical stations; 250-m spatial inference needs additional identity/location evidence.
- **Landsat pre-survey 32-day scene metadata** on a *prior RC6 focal subset*: 3,811 unique RunIDs, 395 routes, 3,793 RunIDs have ≥2 scene dates ≥16 days apart. These are short-window scene candidates, not 2001–2015 image-to-image temporal change and not QA-confirmed pixel estimates. The subset is not a response-blind, representative set of all 7,848 eligible NAAMP surveys.

## New study's separate, falsifiable biological question

**Over repeated breeding seasons, do frog taxa abandon or continue re-expressing strong calling at historically used sites when terrestrial habitat and antecedent hydroclimate change?**

Competing outcomes (all acoustic, not breeding success):

1. **Environmental tracking:** loss of surrounding forest / gain in developed cover and multi-year warm/dry anomalies predict transitions away from historically strong-calling species × physical sites, beyond same-season short-term weather and prior taxon/site propensity.
2. **Persistence/inertia:** prior site use retains predictive power under habitat deterioration, indicating a lag in acoustic site-use adjustment; a signal would not by itself prove an ecological trap or reproductive failure.
3. **No added long-term environmental information:** site-history and season/weather explain transitions just as well on held-out blocks; a predictive gain from fast/slow interactions is unsupported.

Existing JRC/DSWEmod current-water and 3-month variability tests are **prior evidence**, not comparisons re-optimized in this new study. A future outcome analysis must distinguish changes in CI>=2 probability from within-taxon spatial configuration conditional on aggregate response.

## Strict implementation/selection boundaries

- Construct opportunities from public **Runs + Stops** for all standardized 2001–2015 surveys. Do not choose sites because they appeared in the earlier 2,916 matched rain-history pairs or the 3,811 Landsat-metadata runs. Do not read `Counts.csv` before fixing site/date inclusion, environment extraction and outcome models.
- Establish a **response-blind** location ledger: source hash, route and SiteID uniqueness, state-collision check, geometry outlier and relocation diagnostics. Exploratory coarse (1-km) site-surroundings in audited coordinates must be labelled *provisional*, not field-verified wetland positions. Confirmatory 30-m/250-m site interpretation stays blocked until independent position evidence exists.
- Use Annual NLCD C1.2 **year y−1** cover and 5-year change, and satellite image dates *entirely before survey* (no satellite post-survey information as predictor). Note Annual NLCD retrospective maps may use future image information during model generation: they are past-year labels, **not a time-available operational forecast**.
- Use Daymet 1981–2000 fixed reference, prior 7/30/90-day actual weather and 5 previous *complete* years. The v0.4 calendar gate accommodates the Daymet V4 leap-year omitted December 31, with explicit n observed source days and no fabricated daily values; PRISM uses Gregorian calendar and must not inherit this exception.
- Repeat **same route × physical site × survey round × adjacent years**, survey calendar day within 21 days. Record observer continuity; same-observer sensitivity is secondary, not an outcome-dependent inclusion decision. Prevent missing/no-data -> absence conversions.
- Predefine training years, geographic blocks, minimum repeated-year support and outcomes **before** joining sparse positive Counts; use train 2001–2010 and held-out 2011–2015 where support permits. Compare (M0) season/recent weather/prior acoustic site use, (M1) + past land cover and hydroclimate, (M2) + prespecified forest/development × antecedent drought/warmth interaction.
- Treat climate trend as exposure association. 2001–2015 NAAMP observations cannot uniquely identify anthropogenic climate-change causality; 1981–2015 meteorological trends are descriptive, not a look-ahead predictor.

## Provenance, currently unresolved

The official USGS NAAMP source hashes are pinned and a GitHub Actions source-feasibility job is installed on the independent study branch. **No real new climate × frog results are established by this study as of this note**; new local tests use synthetic data. Receipt from the public source job must be checked before any real run/site counts are claimed. The older JRC/DSWEmod results above are independent prior analyses and already real.

References inside the repository:
- `remotesensing/REMOTE_SENSING_HYDROLOGY_MECHANISM_CLOSURE_2026-10-07.md`
- `remotesensing/DSWEMOD_REPRODUCTIVE_ACTIVITY_PREDICTION_RESULT_2026-10-07.md`
- `remotesensing/NAAMP_RS_COORDINATE_ELIGIBILITY_RECEIPT_V0_1.json`
- GitHub Actions run 37716006893 `terrestrial-time-history-metadata-feasibility-v01` (metadata only)