# Broad-area species distribution pilot

The 1,061 strict-quality records were a neighborhood-limited pilot, not the
available training set. Matching observation dates or proximity to NAAMP is NOT
an eligibility condition for this SDM. Fit species separately, not three orders
as if each were a species. This contract precedes model results.

First executable pilot: retain the original strict-pilot species as candidates;
inventory all their GBIF counts over contiguous US (24–50 N, 125–66 W),
1980–2015, reported coordinate uncertainty 0–1,000 m. Select the five largest
candidate species per order by this count, independently of NAAMP outcomes.
Save the complete candidate inventory, including species not selected. This is
a data-rich feasibility pilot, not a representative sample of each order.
Unknown life stage does not exclude a record. Remove fossil/living specimens
and records from datasets explicitly identified as NAAMP. Keep source IDs,
dataset, stage, date and coordinates. Complete pagination is required; no first
page or capped query may be treated as a full sample. The temporal range is a
retrospective training window, not a strict pre-visit forecast.

Predictors fixed in advance: WorldClim 2.1 10-minute BIO1, BIO4, BIO12, BIO15
(1970–2000 climate normals) and EarthEnv full classes 8 and 12 (1-km consensus
flooded vegetation and open water). Sample actual occurrence coordinates.
These support climate/landscape suitability, not pond microhabitat or actual
hydroperiod. No NAAMP calling outcome enters SDM training or selection.

One presence per species per 10-minute cell; deterministic lowest GBIF ID.
Presence–background regularized logistic model with standardized linear and
squared predictor terms. Common uniform land background, plus same-order
other-pilot-species background sensitivity. The latter only partly addresses
recording bias and is not a complete order-level survey-effort surface.
Five deterministic spatial folds made from 2-degree blocks; a second 4-degree
blocking sensitivity. Hold out whole blocks, fit transformations only on
training folds. Report all fold discrimination and support, including failures;
do not select species by resulting AUC. AUC assesses presence/background
discrimination, not occurrence-probability calibration. No tuning on test folds.

Project species scores to NAAMP coordinates, report percentile against the
fixed common land background and environmental-range extrapolation flags.
Do not call raw logistic outputs calibrated occupancy probabilities, sum them
as expected richness, or label all Caudata aquatic larval predators/all Odonata
records nymph habitat. Species habitat and GloBI links are the next filtering
layer. Compare matched NAAMP sites only after species validation; broad climate
scores may distinguish regions while having little resolution within routes.

Primary references and source endpoints are recorded in
SDM_SOURCE_METHOD_FEASIBILITY_2026-10-26.md. Water persistence and the joint
history/vegetation/mechanism comparison remain distinct downstream analyses.
