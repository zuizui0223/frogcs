# Climate × frog strong-calling, v0.9 pre-outcome cohort gate

**Date 2026-10-08. Source-only and environmental data only at this status; no frog Counts.csv has yet been analyzed in the new route-scale comparison.**

## Completed empirical provenance

- The official USGS NAAMP source metadata screen successfully reconstructed 7,848 ten-stop standardized surveys; the 12-route independent climate screen is **not** a representative regional sample.
- Original 1981–2015 Daymet at 12 metadata-selected route median coordinates produced 12 complete 35-year series and prior-only climate-history values for 2001–2015.
- The Daymet-to-NAAMP join succeeded in Actions run [37737903061](https://github.com/zuizui0223/frogcs/actions/runs/37737903061): 213 eligible unique survey runs; 12 routes and states; 92 actually sampled route-years. No frog outcomes used.
- A separate source-only comparison of 2001 versus 2015 prior-5-year climate states reconstructed 180 possible route-years. The previous-5y precipitation ratio increased in 8 of 12, whereas 1981–2015 annual Theil–Sen precipitation slopes were positive in 10 of 12; four routes' signs disagreed. This is exposure description, not the frog response.

## Frozen before new frog-response evaluation

Route-level exploratory acoustic model is specified in `ROUTE_ACOUSTIC_EXPLORATORY_CONTRACT_V0_1.md` and `scripts/route_climate_strong_calling_pilot.py`. Endpoint: among exactly ten sampled stops, count how many have at least one CallingIndex>=2 record on the route visit. Model H0 conditions on route, survey round, seasonal harmonics, run temperature, rain recency; H1 adds two strictly-prior climate-history predictors. Fixed ridge binomial fitting; <=2010 training only, 2011–2015 heldout scoring. The study is *not* a retrospective reanalysis of the RC6 endpoint and does not alter any submitted manuscript.

## Actual response-blind test cohort check

- Across 12 screened routes: **146** survey runs dated <=2010, **67** dated 2011–2015.
- Minimum >=3 training, >=2 testing per route gives **9** eligible routes, **113** train runs, **57** test runs, and **26** unique held-out route-years.
- Three routes fail the frozen minimum: Indiana (2 training), Maryland (1 test), Pennsylvania (0 test).
- The sampling units for generalization are only nine held-out routes, and the 57 survey events are correlated observations. Do **not** label 57 as independent climate-change replications.

## Current execution

- GitHub Actions: [route acoustic held-out pilot](https://github.com/zuizui0223/frogcs/actions/runs/37740185066), status **queued** at time of writing.
- Official Counts.csv has not yet been read by this pilot. Any later success/failure must be reported without revising outcome thresholds or year cutoff.
- The existing landscape/RС6 locked conclusions remain frozen.
- No 30m site-level habitat-change or actual breeding success claim is authorized; **zero field-verified historical physical sites** have entered this study's terrestrial satellite inference.

## Interpretation branches

- Positive heldout H1–H0 gain: limited *incremental predictive association* of antecedent five-year route climate on strong calling magnitude in the prespecified tiny pilot. No climate-change cause, no site-allocation or wetland mediation.
- Null/negative gain: under this sample, past five-year climate does not improve prediction beyond nearer-weather and survey controls. Do not tune rain windows, thresholds, taxon subsets or model families after reading outcomes.
- Insufficient coverage or source error: report the exact failure, no replacement routes selected post hoc.

## Stronger future inference

Independent fixed-site coordinate corroboration and same-pixel Annual NLCD land transitions are prerequisites for testing within-route redistribution of acoustic activity. Since prior JRC/DSWEmod surface-water mechanisms were unsupported, do not reopen those tests to rescue the result.
