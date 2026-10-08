# v0.9 — actual held-out frog acoustic pilot result and stop decision

**Actual source execution:** [GitHub Actions run 37740126489](https://github.com/zuizui0223/frogcs/actions/runs/37740126489) completed successfully. Original output preserved as `receipts/real_frog_heldout/frog_strong_calling_heldout_v09.json` and the run artifact 11533821398. Data source is original SHA256-pinned USGS NAAMP Runs/Stops/Counts plus the pre-existing completed Daymet sample artifact. This independent study is separate from locked RC6.

## Frozen test and factual readout

- Full source-only climate attachment: 213 survey runs, 12 chosen routes, 92 actually surveyed route-years; 1981–2015 Daymet route-level history, 1981–2000 baseline.
- Pre-outcome threshold: each route must have >=3 training runs (2001–2010) and >=2 testing runs (2011–2015); remaining 9 routes, 113 train and 57 untouched test runs. The 57 visits represent 26 held-out route-years, not 57 independent climate changes.
- Binary observation at each of the route's ten surveyed stops: any CI>=2 call, summed as 0–10 for each run. A negative is acoustic nondetection, not biological absence; this is *not* offspring production or adult abundance.
- H0: route intercepts, survey round, season, observed air temperature and rain recency.
- H1: identical plus preceding five complete years' Daymet temperature anomaly and precipitation ratio. Ridge penalty fixed to 1.0; training-only normalization; no post-outcome parameter or threshold tuning.
- Mean test Bernoulli log loss/stop: **H0=0.5614683748; H1=0.5637255838**. Improvement H0−H1 = **−0.0022572089** (negative = worse with climate).
- Equal-route-weighted gain H0−H1 = **−0.0072757646**. Five route gains >0 and four <0. The group pattern is mixed; see machine-readable receipt, not an overall positive predictive finding.
- Total strong-acoustic stop counts in the fixed sample: 739 / 1130 training sampled stops and 412 / 570 testing sampled stops (clustered within routes and survey dates).

**Classification: NO INCREMENTAL OUT-OF-TIME PREDICTIVE SUPPORT for this specific past-five-year climate-history pair at the fixed, small route sample.** Do **not** say climate is irrelevant to frog reproduction; this is one nonrepresentative acoustic-magnitude forecast and is not a causal test.

## Interpretation and boundaries

The climate data already show important difference between retrospective full-period climate slopes and conditions leading into actual frog surveys. However, adding only previous-five-year annual temperature/precipitation did **not** improve heldout forecast beyond nearer meteorology, season and route. This does not resolve whether warming alters reproductive phenology, species-specific activity, water persistence, or within-route acoustic **site allocation**.

Nine held-out routes are too few for generalizable climate-change or route-heterogeneity inference. Most predictors are observed at route/year grain while individual calls are measured at stop/run grain; do not count 570 stop opportunities as independent climate replications. No uncertainty interval/p-value was predeclared or estimated for the prediction gain; do not interpret route sign counts as significance.

## Explicit stop rule

Do **not** respond to the negative result by searching new rain/climate lag windows, species subsets, penalties, outcome thresholds, alternative calendar splits, or only positive routes to rescue a climate prediction. This pilot is frozen as a feasibility/negative predictive check.

## Next independent and biologically distinct investigation

Actual physical-site corroboration, verified Annual NLCD class-change map (same pixel, pre-survey), and a design with repeated visits **before and after** mapped terrestrial change are still necessary for the main ecological question: environmental tracking of calling locations versus acoustic site legacy. Earlier monthly surface-water predictors were already negative for the within-taxon concentration explanation; do not retune them. No 30m same-site satellite change, verified breeding success or anthropogenic climate causal effect is established here.