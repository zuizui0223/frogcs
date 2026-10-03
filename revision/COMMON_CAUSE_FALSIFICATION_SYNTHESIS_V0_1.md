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

## Stage 2b — measured acoustic-observation conditions

We next asked whether the remaining pattern could be a route-night detectability artefact rather than an ecological state. The fixed complete-case analysis retained **2,718 pairs on 421 routes** and added recorded hearing-impairment fraction, major-noise timeout fraction and mean Beaufort wind to the same cross-fitted 72-h-rainfall common-environment model. The baseline and augmented models used the **same focal pairs and training-run universe**.

Results:
- same-sample 72-h-rainfall residual = **0.2851**;
- detection-augmented residual = **0.2713**;
- fraction removed = **4.8%**;
- augmented residual null 95% interval = **−0.1408 to 0.1378**;
- augmented upper-tail **P = 0.000999**.

The route-night dependence result was even less affected:
- dry-route-silent baseline **rho_b = 0.2856**;
- detection-augmented **rho_b = 0.2860**;
- augmented null 95% interval = **−0.00555 to 0.00509**;
- **P = 0.000999**.

Thus measured route-run hearing impairment, major-noise interruption and wind do not account for the residual allocation or the dry-route-silent dependence. This does **not** eliminate unrecorded masking, within-observer perceptual error or species-specific detectability.

## Stage 3 — repaired direct conditional-independence diagnostic

The original fixed diagnostic strongly rejected independent Bernoulli stop outcomes under the strongest measured-environment + historical-site comparator (**D = 0.4159**, P = **0.000999**), but a later audit showed that D is an unbounded standardized dependence score rather than a correlation coefficient. It is retained for provenance and breadth-of-departure auditing, but not as the primary effect-size metric and not for design-effect conversion.

A bounded repair was therefore fixed before its value was read:

- all **18,769** species × route-night clusters: **rho_b = 0.1721**, null 95% interval **−0.00267 to 0.00285**, P = **0.000999**;
- **dry-route-silent** taxa: **rho_b = 0.2849**, null 95% interval **−0.00541 to 0.00565**, P = **0.000999**;
- **dry-route-active** taxa: **rho_b = 0.1273**, null 95% interval **−0.00314 to 0.00350**, P = **0.000999**.

The drier-state split uses only the drier survey, so the stronger dependence among dry-route-silent taxa is not created by selecting on their wetter outcome. It directly links the shared-state diagnostic to the pre-wet stratum from which acoustically route-new taxa can emerge. The q construction also includes one pair-level common logit shift chosen to match the **observed total wet incidence**, so a route-night factor that merely raises all cells together is conditioned away at first order; the remaining object concerns how that fixed amount of activity is allocated within species across stops.

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

### Species-level marginal calibration

A separate route-cross-fitted falsification allowed each information-eligible species one constant calibration intercept on top of the strongest fixed q comparator, estimated only on the opposite route fold and followed by the same pair-level incidence rematching. This directly tests whether persistent species-level under- or overprediction is masquerading as a species × route-night effect.

The recalibrated null remained insufficient:

- concentration residual = **0.2608**, null 95% interval **−0.1326 to 0.1355**, P = **0.000999**;
- dry-route-silent bounded dependence = **0.2866**, P = **0.000999**;
- far-lag 7–9 dependence = **0.2737**, P = **0.000999**.

Thus a constant species calibration error is not the missing state variable; the residual is genuinely event-specific at the species × route-night level.

### Contemporaneous stop-night hotness shared across taxa

We then used the same wet survey itself as a deliberately strong common-cause falsification while preventing target-taxon leakage. For each target taxon and stop, a ridge-penalized stop-night intercept was estimated from **all other fixed-support taxa only**, using their fixed q values as offsets. This can absorb contemporaneous local conditions shared across taxa, including route-order/time progression, unmeasured local weather or hydrology, and other stop-wide observation conditions.

The adjustment was non-trivial: mean stop-richness prediction RMSE improved from **0.7752 to 0.5810**. Yet the target-taxon structure did not disappear:

- concentration residual = **0.3182**, null 95% **−0.1386 to 0.1220**, P = **0.000999**;
- dry-route-silent bounded dependence = **0.2985**, P = **0.000999**;
- far-lag 7–9 dependence = **0.2842**, P = **0.000999**.

Thus the remaining event-level state is not adequately described as a stop-night condition shared uniformly across taxa. The supported statistical structure is more specific: a **taxon-specific route-night gate whose spatial expression varies among sites**.

### Taxonomic breadth

A breadth audit fixed before the bounded repair used the historical D score. All **40/40** information-eligible taxa had positive departures; the largest positive numerator contributor accounted for **11.7%** of positive mass, and every leave-one-species-out pooled D remained positive. Because D is unbounded, its specieswise numerical values are not treated as comparable effect sizes. The audit supports breadth of the positive departure, not a common effect magnitude or mechanism.

### Descriptive magnitude of the shared species × route-night state

A separately fixed logistic-normal model treated the strongest measured-comparator `logit(q)` as an offset and added one random intercept shared by the ten stops of each species × route-night cluster. This does not replace the bounded simulation test; it only asks how large a latent common shift is required in that model.

- all clusters: **sigma = 2.563**, latent-logistic variance share **0.666**, +1 SD odds multiplier **13.0×**;
- dry-route-silent clusters: **sigma = 2.884**, latent-logistic variance share **0.717**, +1 SD odds multiplier **17.9×**.

A prespecified numerical audit passed: the 20-node sigma values differed from 60-node estimates by **1.03%** and **1.69%**, and 40-node estimates by **0.02%** and **0.12%**. These quantities are model-based latent-scale descriptions, not occupancy ICCs, monitoring design effects or route-clustered confidence statements. The primary inferential quantity remains bounded `rho_b` against the independent-Bernoulli null.

### Is one uniform species-night scalar state enough?

A stronger structural test estimated the dry-route-silent latent distribution in one deterministic route fold and generated only the opposite fold. The transferred scalar state **was sufficient for the concentration endpoint**: observed concentration β = **1.7136**, scalar prediction = **1.9204**, and the observed conditional residual **−0.2069** lay inside the scalar-generator interval **−0.2797 to 0.2867**.

However, the same scalar state was **too coherent across stops**. It predicted near-lag and far-lag residual dependence of about **0.475** in both cases, whereas the observations were only **0.296** and **0.272**; both observed values lay below the scalar-generator predictive intervals.

This rules out the simplest picture of a whole-route all-or-none species switch. The pattern is instead **route-spanning but spatially non-uniform**: enough species-night state variation exists to generate the heavy within-taxon tail, but its expression is restricted to a subset of sites.

### Does the non-uniform deep state align with the historical site template?

A fixed exact-k placement test then linked the two pieces directly. It retained dry-route-silent taxa, fixed each observed wet activation depth k exactly, and used the strongest fixed q values to define the conditional independent-Bernoulli distribution over which k of the ten stops should be active. The only remaining question was whether those active stops overlapped strictly-prior CI2/3 SiteIDs more often than q predicted.

Among **409 deep k ≥ 4 species × route-night clusters**, historical-template alignment increased with rainfall contrast (**β = 0.02659**, P = **0.001998**). Mean q-conditioned overlap excess was **0.0760** in deep clusters versus **−0.0108** in shallow k=1–3 clusters. Because significance in one subgroup and not another is not itself evidence of a difference, we then fixed an explicit post-hoc contrast. The direct **deep−shallow rainfall-coefficient contrast was 0.02970**, above its simulated 95% interval **−0.02532 to 0.02889** (P = **0.02098**); the cluster-mean contrast was likewise positive (0.08685; P = **0.00599**).

This is the missing direct bridge: the unusual deep tail is not merely non-uniform; coupling to the taxon's recurrent strong-chorus site template is directly stronger in deep than shallow activation after exact k and the fixed q site propensities are held constant. The parsimonious structural description is therefore a **fast species-night gate expressed through a distributed slow species × place template**.

## Biological interpretation now supported

> **A frog species' acoustic state on a given route-night is distributed across the landscape but not uniformly: after measured weather, recorded acoustic conditions, historical physical-site use, dry-state persistence and total activity are represented, a fast species-night gate is expressed across a spatially separated subset of recurrent sites.**

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
3. describe the remaining object as a **distributed, non-uniform species-by-route-night state**: a scalar gate explains concentration but overpredicts whole-route coherence;
4. link that fast state to the independently observed slow historical site template, yielding a fast-gate × slow-template description;
5. note that same-observer and measured detection-condition adjustments leave the dependence essentially intact;
6. elevate the monitoring-design implication cautiously: clustered uncertainty is broadly larger across species, but no published occupancy-trend estimator has yet been re-fit;
7. keep WFTS as the prospective confirmation under `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`, including the frozen secondary common-environment / bounded-dependence / far-lag diagnostics.
