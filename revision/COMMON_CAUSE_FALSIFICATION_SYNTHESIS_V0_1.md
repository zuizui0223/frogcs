# Common-cause falsification synthesis v0.1

Date: 2026-10-03

## Provenance boundary

The original same-data mechanism sequence ended under its prespecified stopping rule. That rule was explicitly reopened on 2026-10-03. Everything in this note that was run after reopening is **post-hoc exploratory falsification**, not independent confirmation and not part of the original prespecified evidence sequence.

## Question

Could the NAAMP within-taxon multi-site concentration be a trivial consequence of a species-wide environmental switch acting across all ten route stops on a given night?

## Stage 1 — flexible measured route-night environment

Fixed contract: `exploration/NAAMP_FLEXIBLE_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json`

Population: 2,916 strictly-prior-history pairs, 439 routes, 20 states.

The cross-fitted species model allowed nonlinear `log(1 + DaysSinceRain)`, nonlinear temperature, first and second annual harmonics, a rain-recency × temperature interaction, State and RunNumber effects, strictly-prior species × physical-SiteID history, dry-state persistence and matched total wet incidence.

Result:
- observed concentration β = **1.6503**
- existing principal-null prediction = **1.3535**
- flexible-environment prediction = **1.3872**
- residual: **0.2969 → 0.2631**
- fraction of existing residual removed = **11.4%**
- flexible-null residual 95% interval = **−0.1307 to 0.1276**
- upper-tail **P = 0.000999**

Nonlinear rain recency, temperature, season and their tested interaction explain only a small fraction of the concentration residual.

## Stage 2 — actual antecedent rainfall amount

A separate earlier NAAMP analysis had already established that antecedent rainfall amount is biologically informative for strong activation: the 72-h ERA5 rainfall-amount effect on the strong-new-chorus score was β = **0.741** (95% CI **0.386 to 1.097**) while DaysSinceRain remained positive.

Fixed concentration contract: `exploration/NAAMP_RAIN_AMOUNT_COMMON_ENVIRONMENT_NULL_CONTRACT_V0_1.json`

Weather/prior-history intersection: **2,835** pairs, **428** routes, **20** states.

Same-sample comparison:
- observed concentration β = **1.7136**
- linear species-response null prediction = **1.3960**
- linear conditional residual = **0.3176**
- 72-h rainfall common-environment prediction = **1.4166**
- rainfall conditional residual = **0.2970**
- fraction of same-sample residual removed = **6.5%**
- rainfall-null residual 95% interval = **−0.1305 to 0.1378**
- upper-tail **P = 0.000999**

Actual antecedent rainfall amount clearly helps explain whether strong activation occurs, but it explains very little of the residual allocation of that activity across multiple stops within the same taxon.

## Other measured atmospheric cues already examined

Earlier branch-preserved analyses provide useful negative controls:

- **Current light rain:** no supported independent effect on strong activation.
- **Surface pressure / pressure fall:** no supported independent effect once rain recency and 72-h rainfall amount are represented.
- **Humidity:** no supported individual effect; a joint humidity+pressure test contained some information, but rain recency remained positive.
- **AnuraSet external threshold exercise:** did not provide a robust general replication of a threshold-dominant recent-rain response.

These analyses do not exhaust environmental common causes. Local hydroperiod, water level, soil moisture, small-scale rainfall heterogeneity and other unmeasured route-night variables remain possible.

## Stage 3 — repaired direct conditional-independence diagnostic

The original fixed diagnostic strongly rejected independent Bernoulli stop outcomes under the strongest measured-environment + historical-site comparator (**D = 0.4159**, P = **0.000999**), but a later audit showed that D is an unbounded standardized dependence score rather than a correlation coefficient. It is retained for provenance and breadth-of-departure auditing, but not as the primary effect-size metric and not for design-effect conversion.

A bounded repair was therefore fixed before its value was read:

- all **18,769** species × route-night clusters: **rho_b = 0.1721**, null 95% interval **−0.00267 to 0.00285**, P = **0.000999**;
- **dry-route-silent** taxa: **rho_b = 0.2849**, null 95% interval **−0.00541 to 0.00565**, P = **0.000999**;
- **dry-route-active** taxa: **rho_b = 0.1273**, null 95% interval **−0.00314 to 0.00350**, P = **0.000999**.

The drier-state split uses only the drier survey, so the stronger dependence among dry-route-silent taxa is not created by selecting on their wetter outcome. It directly links the shared-state diagnostic to the pre-wet stratum from which acoustically route-new taxa can emerge.

### Spatial scale along the route

A fixed lag-profile diagnostic asked whether the residual dependence was confined to adjacent route positions. Among dry-route-silent taxa:

- pooled stop-number lags 1–3: **0.2964**, P = **0.000999**;
- pooled stop-number lags 7–9: **0.2718**, P = **0.000999**.

Every individual lag from 1 to 9 was positive and outside its independent-null envelope. In all fixed-support clusters, near and far coefficients were **0.1829** and **0.1577**, respectively.

Stop-number lag is route topology, not exact geographic distance. Nevertheless, persistence at lags 7–9 shows that the residual dependence is not merely an adjacent-stop phenomenon.

### Observer sensitivity

Observer turnover was not required. Among **2,191** weather-linked prior-history pairs in which the same observer conducted both focal surveys:

- all clusters: **rho_b = 0.1627**, P = **0.000999**;
- dry-route-silent clusters: **rho_b = 0.2758**, P = **0.000999**.

This does not exclude within-observer perceptual error, but it rules out observer replacement as a necessary explanation.

### Taxonomic breadth

A breadth audit fixed before the bounded repair used the historical D score. All **40/40** information-eligible taxa had positive departures; the largest positive numerator contributor accounted for **11.7%** of positive mass, and every leave-one-species-out pooled D remained positive. Because D is unbounded, its specieswise numerical values are not treated as comparable effect sizes. The audit supports breadth of the positive departure, not a common effect magnitude or mechanism.

## Biological interpretation now supported

> **A frog species' acoustic state on a given route-night behaves as a shared landscape-scale state: after measured rainfall amount, nonlinear rain recency, temperature, season, historical physical-site use, dry-state persistence and total activity are represented, calling outcomes remain positively dependent within the same species and night, including among taxa previously silent across the route and at widely separated route positions.**

This establishes the **scale of dependence**, not its unique lower-level cause.

Still unresolved:
- unmeasured shared hydrology or microclimate;
- synchronized breeding state;
- demographic/availability state shared across a route;
- social facilitation;
- other latent route-night processes.

Not established:
- individual movement among stops;
- literal simultaneity among sequential NAAMP stops;
- rainfall causality;
- social transmission;
- a universal anuran mechanism.

## Monitoring implication

The direct ecological result implies that stop number is not automatically equal to independent information. The historical NAAMP occupancy literature itself treated route stops as spatial replicates and noted that nesting within routes could induce dependence affecting trend precision.

Two fixed post-hoc uncertainty diagnostics compare model-based IID covariance with clustered covariance for the same representative stop-level activation regression.

Pooled analysis:
- species × route-night clustering: SE **1.81×** IID;
- route-pair clustering: SE **2.24×** IID;
- route clustering across years: SE **2.69×** IID.

Specieswise audit:
- 39 taxa met fixed information thresholds;
- pair-clustered SE exceeded IID in **38/39**, median ratio **1.61** (IQR **1.30–1.74**);
- route-clustered SE exceeded IID in **36/39**, median ratio **1.48** (IQR **1.24–1.72**).

Thus uncertainty inflation is not only a pooled multispecies phenomenon. These diagnostics do **not** re-estimate a published NAAMP occupancy-trend model and do not establish a universal correction factor.

## Current decision

The common-cause test does **not** support pivoting the paper to “species-specific rainfall thresholds explain the pattern.”

The stronger direction is:

1. retain the ecological discovery as **species-by-route-night landscape-scale dependence**;
2. show that the strongest measured common environmental triggers explain little of the allocation residual;
3. describe the remaining object as a **species-by-route-night shared landscape state**, especially pronounced among taxa silent on the drier route and persisting to far route-position lags;
4. note that same-observer restriction leaves the dependence essentially intact, so observer turnover is not required;
5. elevate the monitoring-design implication cautiously: clustered uncertainty is broadly larger across species, but no published occupancy-trend estimator has yet been re-fit;
6. keep WFTS as the prospective confirmation, with the already frozen secondary common-environment diagnostic in `revision/WFTS_PROSPECTIVE_COMMON_ENVIRONMENT_DIAGNOSTIC_V0_1.json`.
