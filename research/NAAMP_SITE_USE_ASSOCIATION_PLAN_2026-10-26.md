# Existing-data site-use characterization

User steering replaces incremental predictive improvement as the immediate
question: characterize repeatedly used locations and examine correlations.
No new external data are required for this phase. The overall research goal
remains active; fine-scale hydroperiod and vegetation are not silently filled.

- [x] Aggregate all eligible completed surveys by physical site. Primary cohort:
  at least 6 visits over at least 3 years. Save all sites and coverage; sensitivity
  cohorts use >=3 visits/2 years and >=10 visits/5 years.
- [x] Primary response: strong-call visits / completed visits. Secondary response:
  years with any strong-call visit / observed years. Also retain any-call rate,
  yearly mean strong-call rate and equally weighted survey-season strong rate.
  Seasonal sensitivity requires all 3 standard seasons. Calling is a breeding-
  activity proxy; sites are acoustic locations, not verified pond polygons.
- [x] Join saved species suitability, group potential richness, climate and
  EarthEnv flooded vegetation/open water. Primary environmental comparisons:
  3-group richness + pond-breeding Caudata richness, under both backgrounds;
  mean species suitability per group; flooded vegetation/open water. Climate,
  latitude/longitude and effort are context, not proof of biological effects.
- [x] Report whole-cohort Spearman correlations AND route-adjusted rank
  correlations (rank both variables, subtract each route's rank mean, correlate
  residuals). These are different scales, not incremental prediction scores.
  Report sample size and routes with within-route predictor variation.
- [x] Bootstrap entire routes 1,000 times for primary group/environment
  correlations, recomputing ranks in each replicate. Save all results; do not
  choose favorable background or response. Species-level and sensitivity
  correlations are exploratory summaries without confidence intervals.
- [x] Characterize high-use (>=75% strong-call visits) versus low-use (<=25%)
  sites by medians/distributions, with denominators and geographic/effort
  context. This descriptive comparison is not a causal preference estimate.
- [x] Validate aggregation, missingness, join uniqueness and rank adjustment;
  create a correlation figure, inspect it, save a Japanese report and update
  the existing research PR. Keep predictive analyses as a distinct earlier
  question, never interpret their lack of improvement as lack of correlation.

Files: research/scripts/naamp_site_use_associations.py; a focused regression
test; research/results/naamp_site_use_associations_20261026/; report/figure in
the task outputs. Use numpy/pandas/scipy and the frozen saved input tables.
No p-value significance selection or inference of competition from residuals.

Ruling before examining associations: ten physical sites share two route labels.
Join route labels connected by a shared site into one resampling component;
save the full mapping. Same site/date/season rows occur 848 times. They are not
assumed to be erroneous duplicates: keep completed visits in the primary
denominator, and add an equal-calendar-day strong-call-rate sensitivity.

Verification: four regression tests passed; exact replay of eight CSV tables
and metadata from all 1,000 bootstrap draws. Figure visually inspected.
PR #141 description updated to the pattern-first scope.
