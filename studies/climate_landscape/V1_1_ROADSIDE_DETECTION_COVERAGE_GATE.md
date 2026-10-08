# NAAMP land-cover change × frog acoustic calling: roadside observation-process gate

**2026-10-08. Response-blind metadata audit only; no new frog effects.**

## Ecological confounding that must be handled

Cosentino et al. (2014, *Biological Conservation*, DOI 10.1016/j.biocon.2014.09.027) already studied 1,617 NAAMP stops and found strong associations of frog distributions/richness with road density and vehicle traffic, while effects of developed land around wetlands were small or even positive conditional on road disturbance. This means there is no sound basis to preregister a universal forest→developed negative acoustic endpoint. Roadside traffic can affect anuran survival or habitat use **and** the ability of surveyors to hear calls; acoustic records cannot by themselves separate these processes.

NAAMP's original `Stops.csv` includes `CarCount`, `MassNoiseIndex`, `Noise`, and `TimeOut`. A future same-site Annual NLCD time-change design needs to establish whether those fields are comparable within repeated sites and survey rounds, rather than assuming roadside acoustic nondetections are habitat abandonment.

## New purely source-based audit

`scripts/audit_naamp_roadside_detection_history.py` reads only original checksum-pinned `Runs.csv` and `Stops.csv` and the previously defined response-blind standardized surveyed-site panel. It separately counts:

- source completeness of traffic counts, hearing-impairment proxy and time-outs;
- same-physical-SiteID, consecutive-year, same survey round, ±21-day season contrasts with paired traffic/noise measurement;
- same-observer contrasts where `ObserverTrackingID` is available;
- traffic changes among comparable pairs without fitting a frog response.

Preexisting definitions from `scripts/naamp/run_naamp_detection_quality_robustness.py` are preserved: impairment is `MassNoiseIndex >= 2` for valid codes 0–4, falling back to `Noise` coded 0/1 when MassNoiseIndex is missing; `TimeOut` is a separate 0/1 variable. Invalid or missing values remain missing. `CarCount` is a nonnegative observed tally; it is not a continuous estimate of road density or commuting traffic.

**No Counts.csv is read. No effect is fitted. No site is classified as field-verified.** This remains orthogonal to locked v0.9 negative held-out climate forecast and avoids re-exploring climate lags, outcomes or species after seeing the result.

## Interpretation gate for subsequent land-cover ecology

Even with paired terrestrial pixels and verified site identity:

1. Compare terrestrial land-cover changes only under explicitly measured or uncertainty-bounded traffic/noise conditions; report measured-sample attrition.
2. Analyze species-specific *acoustic site use*, never claim extinction, movement, individual site fidelity or breeding success without complementary evidence.
3. Pre-register whether roadside disturbance is a confounder, an ecological pathway, or a detection mechanism in the estimand; controlling for traffic mechanically can suppress a real causal pathway from development to frog habitat use.
4. The main test remains lagged same-site calling after objectively mapped land-cover conversion versus sites without conversion, with temporal and geographic blocking. Changes to the baseline strong-calling pilot after its negative result are prohibited.

## Source documents

- USGS NAAMP protocol: https://www.usgs.gov/centers/eesc/science/north-american-amphibian-monitoring-program
- Cosentino et al. 2014: https://doi.org/10.1016/j.biocon.2014.09.027
- USGS Annual NLCD Collection 1.2: https://www.usgs.gov/centers/eros/science/annual-national-land-cover-database
