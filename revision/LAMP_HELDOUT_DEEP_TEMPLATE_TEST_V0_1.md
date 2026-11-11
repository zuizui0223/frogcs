# LAMP held-out deep-template test v0.1 — 2026-10-06

## Status

**Frozen after header-only inspection and before any LAMP species/call-index outcome value was parsed.**

This is a separate geographic holdout test of the prospective structural prediction already frozen in frogcs:
> broad/deep multi-site activity need not erase spatial selectivity; deep activity may remain more strongly coupled to recurrent high-use sites than shallow activity.

It is **not** a replication of the rainfall-conditioned NAAMP primary endpoint because the public LAMP CSV does not contain a comparable rainfall-recency field.

## Dataset and independence boundary

Louisiana Amphibian Monitoring Program (LAMP), Carter (2021), USGS ScienceBase DOI 10.5066/P9VNBWM2.

Header-only preflight established:
- RouteRegion, RouteNumb, RouteName, Run, Stop, Year, Month, Day;
- 26 species columns;
- ten-stop NAAMP-style route structure;
- no rainfall/precipitation field in the public CSV.

The frogcs discovery analysis contains no Louisiana state observations. LAMP is therefore a **held-out geographic dataset outside the 21-state discovery sample**, but it remains within the NAAMP protocol family and must not be called independent-programme replication.

## Fixed temporal split

Training/template period: **1997–2008 inclusive**.
Validation/holdout period: **2009–2017 inclusive**.

The split may not be moved after outcome readback.

## Call-state coding

Species columns are interpreted using the documented LAMP Calling Index:
- blank/0 = no recorded calling;
- 1–3 = calling positive;
- CI >= 2 = strong calling.

If the public file contains any additional nonnumeric response code not explicitly documented in the metadata, stop and classify schema-incompatible before calculating the endpoint.

## Training-only site template

For each RouteNumb × Run × species × Stop in 1997–2008:

- n_obs = number of observed route-run-year opportunities at that stop;
- n_active = number with CI > 0;
- q_s = (n_active + 0.5) / (n_obs + 1.0);
- prior_strong_s = 1 if CI >= 2 occurred at least once in training, else 0.

Template eligibility:
- all ten stops have >= 3 training opportunities;
- at least one prior_strong and at least one non-prior_strong stop;
- the species has >= 5 calling-positive training route-run-years.

No validation outcome may alter these rules.

## Validation clusters

Unit: RouteNumb × Run × Year × species in 2009–2017.

Require:
- all ten stops observed in that route-run-year;
- species CI values valid at all ten stops;
- K = number of CI>0 stops is between 1 and 9 inclusive;
- an eligible training template exists.

Define:
- shallow = K 1–3;
- deep = K >= 4.

K=10 is excluded because exact-K placement has no spatial-choice variance.

## Exact-K q-conditioned historical-template alignment

For each eligible validation cluster:
- observed_overlap = number of active validation stops with prior_strong_s=1.

Enumerate all choose(10,K) stop subsets.
For subset S assign weight proportional to:

product over s in S of q_s/(1-q_s).

Normalize weights across all size-K subsets.

Expected_overlap = weighted mean number of prior_strong stops under this exact-K conditional null.

Alignment residual:
R = observed_overlap - expected_overlap.

R>0 means the validation-year activity is more aligned with the historical strong-site template than expected from training-period site activity propensities and the exact observed spatial depth K.

## Frozen primary test

Primary endpoint:
Delta = mean(R | deep) - mean(R | shallow).

Inference:
- route-block bootstrap;
- resample RouteNumb with replacement and retain all Run × Year × species clusters within selected routes;
- 10,000 replicates;
- seed 2840242;
- percentile 95% interval.

Primary support rule:
1. informativeness gate passes;
2. Delta > 0;
3. 95% bootstrap interval for Delta lies wholly above 0.

## Frozen secondary test

Deep-only alignment:
D = mean(R | deep).

Support requires D > 0 and its route-block bootstrap 95% interval lies wholly above 0.

Secondary cannot rescue a failed primary test.

## Informativeness gate

Required before interpretation:
- >= 50 deep K>=4 clusters;
- >= 100 shallow K=1–3 clusters;
- >= 5 species represented among deep clusters;
- >= 20 routes represented among deep clusters.

Failure classification: **inconclusive_holdout_template_test**.

## One-shot interpretation

- **heldout_template_support**: gate passes and both primary and secondary support rules pass.
- **heldout_template_non_support**: gate passes but one or both support rules fail.
- **inconclusive_holdout_template_test**: gate fails.

The result must be retained regardless of direction. No alternate K threshold, time split, CI threshold, smoothing constant, site-template definition or subset may replace it after readback.

## Biological interpretation boundary

Support would mean:
> In held-out Louisiana NAAMP-protocol routes, unusually deep multi-site frog calling remains more strongly associated with recurrent strong-calling locations than shallow calling, even after exact spatial depth and training-period site propensity are represented.

It would strengthen the ecological interpretation of **expansion without homogenization**.

It would not establish:
- rainfall causality or a rain-specific response;
- individual fidelity or memory;
- movement among stops;
- hydrological or social mechanism;
- independent-programme replication;
- universality.

## Relation to RC6

This test does not reopen RC6 automatically. Any manuscript use requires a separate explicit decision after this one-shot holdout result is fully disclosed.
