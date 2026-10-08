# Route-scale climate vs frog acoustic-activity magnitude: prospective execution contract v0.1

Status: **separate exploratory analysis, not JAE RC6, not causal, not preregistered before all previous frog outcomes in the repository were inspected**.

## Primary purpose

Determine whether past-only (preceding 5 complete years) temperature and precipitation anomalies add out-of-time predictive information about the **number of 10 sampled NAAMP stops registering any CI >= 2 strong calling**, above recorded recent-rain recency, survey air temperature, phenology, route, and run round. An improved predictor is neither a climatic cause nor a reproductive-success mechanism. It is not a test of site allocation; the latter requires separately verified physical sites.

## Locked sampling and source authority

- 12 routes fixed without reading frog calls in the already-completed 1981–2015 official Daymet source receipt. Their locations are approximate median of geometry-only screened stations. This is ~1km regional climate, **not 30m wetland location**.
- Official NAAMP 2001–2015 Runs/Stops/Counts CSV validated by SHA256; eligible exactly-10 surveyed stop records. Positive Count table encodes CI 1/2/3 only, and CI>=2 at a surveyed stop denotes strong acoustic activity. Absence of a positive row at an *eligible surveyed stop* gives acoustic nondetection, not frog absence.
- Daymet exposure is previous five complete years relative to 1981–2000, **not** full-period slope as a historical predictor.

## Comparison frozen before this execution

H0: Ridge binomial logit of 10-stop strong activity fraction: route fixed effects, RunNumber, annual sine/cosine seasonality, survey air temperature and log(1+DaysSinceRain). H1: same plus prior5 mean-temperature anomaly and log of prior5 precipitation ratio. Exact ridge strength=1; training-only z-scaling. Group routes with >=3 training runs and >=2 held-out runs. Train years <=2010, untouched test 2011–2015; fail closed for <5 routes, <30 train runs, or <20 test runs. Score held-out per-stop Bernoulli log-loss with equal-run and equal-route summaries, no selection of the sign of gain. No additional lag windows, thresholds or subgroup searching after response readout. No P-value or causal claim from this single small nonrepresentative pilot.

## Robustness and stop rules

- No fine-scale satellite/hydroperiod interpretation from these climate exposures.
- Prior RC6 strong chorus analyses are *already known to investigators*; do not imply prospective registration before all frog data access.
- If model lacks sufficient temporal holdout, code returns INSUFFICIENT_TEMPORAL_HOLDOUT_COVERAGE without modifying inclusion after outcomes.
- For positive out-of-time gain, describe only predictive association at 12-screen-route level; separate independent geographically blocked confirmation would be necessary.
- For zero/negative gain, explicitly report no added climate-history prediction rather than tuning terms.
