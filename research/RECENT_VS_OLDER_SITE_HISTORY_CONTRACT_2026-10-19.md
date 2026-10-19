# Frozen exploratory forecast: recent versus older calling-site history

Date: 2026-10-19. Separate research branch; JAE main and all submitted estimands unchanged. This is a new POST-HOC analysis of an already studied NAAMP data source, NOT independent confirmation or preregistration of unseen data.

## Question and comparator

Does the preceding year's strong-calling location add more information about current strong-calling placement than an equally sized, two-years-old observation, beyond earlier site-specific calling propensity? Historical presence is recorded acoustic activity, not organismal occupancy, natal origin or individual memory.

Use the original SHA256-pinned NAAMP Runs/Stops/Counts loader and existing complete-ten-stop survey eligibility (2001–2015). Stratify by State × RouteNumber × RunNumber. Exclude ambiguous multiple eligible surveys in a stratum-year. Require ten distinct physical SiteIDs, a current survey at year t, surveys at exactly t−1 and t−2 with the identical physical-site set, and at least THREE earlier surveys at t−3 or earlier with that same set. Sort by physical SiteID for consistent vector alignment. A taxon is eligible only if a CI1–3 record occurs in that earlier background (never chosen using future taxon records).

Response: recorded CI≥2 at each of ten stops. Condition on the observed number k of CI≥2 stops in the current taxon × route × run survey. Only k=1..9 informs placement. This is a retrospective conditional placement forecast with current k supplied, NOT a prospective unconditional calling forecast, an activity-amount model or the JAE concentration C test.

Background probability q_j=(number of earlier CI≥2 records + 0.5)/(number of earlier surveyed runs + 1). Earlier means ≤t−3; neither lag1 nor lag2 nor the current outcome enters q. Baseline z_j=logit(q_j).

Three conditional logistic allocation models use the same frames and exact combinatorial likelihood over all choose(10,k) placements:
- M0: eta_j=a*z_j.
- MR: eta_j=a*z_j+b*recorded_strong(t−1,j).
- MO: eta_j=a*z_j+b*recorded_strong(t−2,j).

MR and MO have the same parameter count and add one completed survey each. Comparing MR only with M0 would not separate recency from the benefit of another noisy measurement of constant habitat suitability. MR versus MO is therefore the PRIMARY comparison. Estimated background propensity is NOT equivalent to perfect removal of all stable habitat differences.

## Time split and fixed reporting

Fit coefficients using target years ≤2008. Freeze coefficients and evaluate target years 2009–2015. Each prediction may use earlier completed surveys, including an earlier test-period survey, but no coefficients are refitted and no future observation enters a predictor. This is rolling-origin conditional placement evaluation on reused historical data, not pristine prospective external validation. Report this distinction.

Learn parameters with deterministic bounded optimization (each coefficient in [−6,+6]) and a numerical ridge of 1e−6 times squared coefficient norm added to average negative conditional log likelihood. Stop on convergence failure or coefficient-boundary hit rather than choosing new bounds. Require at least 200 informative training frames and 200 test frames, each with at least 50 routes; these are feasibility thresholds, not power guarantees. Do not change thresholds/windows/outcome after execution.

Primary effect: route-equal mean held-out log-score(MR) minus log-score(MO), nats per taxon-survey. Secondary: MR−M0 and MO−M0. Use 2,000 bootstrap resamples of whole route clusters, seed 20261019, to summarize test-route uncertainty. These intervals condition on the trained model and do not cover refitting/training uncertainty. Report all three models, route/state/taxon coverage, test-year breakdown, directional route fraction, and same-observer-across-t,t−1,t−2 sensitivity without refitting. No selective species/state/window search.

## Interpretation and next decision

MR>MO in held-out conditional score indicates a recency-sensitive predictive pattern at these sampled positions; it does NOT distinguish changing hydrology, stable-propensity estimation error, demographic persistence, detection, same-individual learning or inherited memory. MR≈MO with both above M0 is consistent with the extra observation mainly measuring persistent site propensity. Neither adds predictive value: do not advance a recency claim. An interval spanning zero is inconclusive, not equivalence.

Local water-depth/history, physical individual abundance, individual identities and generation labels are absent here. Hence 'environment held exactly equal', 'learning', 'biological memory independent of environment', and 'generation-spanning memory' are not admissible conclusions under ANY outcome. Regionally correlated sampling, route changes, selection on earlier detections, uneven observation effort, and within-programme reuse remain limitations.

No new raster acquisition, remote-sensing protocol change, dataset hunt, custodial email, or animal experiment is authorized by this forecast. Successful execution adds one bounded empirical diagnostic and an explicit decision; no additional synthetic ecological worlds will be used to rescue a result.
