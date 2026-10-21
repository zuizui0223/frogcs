# Same-night partner contrast versus strictly prior species×physical-site use
Frozen exploratory protocol, 2026-10-21, written before newly conditioned result readback.

## Biological question
The NAAMP/NWI acoustic network showed that *Lithobates clamitans* shares listening stops with *L. catesbeianus* more often, and with *Anaxyrus fowleri* or *Hyla versicolor* less often, than expected from species-specific mapped wetland/PEM responses. In a follow-up, *all three named taxa were heard on the very same route-run* and the **paired partner difference persisted** (538 runs/175 routes for A. fowleri and 744/198 for H. versicolor, CI≥1).

Could this still reflect **stable species×SiteID suitability**, rather than coupling among current frog species? This is a different, falsifiable FIRST-ORDER explanation: each species repeatedly calls in its own preferred physical sites regardless of the other current species.

## Frozen data and exact site identity
- USGS NAAMP 2001–2015, original SHA-pinned Runs/Stops/Counts, 7,848 valid standardized route-runs; no source repair.
- Frozen source-only NWI 250m wetland and PEM cover at 5,147 geocoded stations from [Actions 39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196). NWI is time-mismatched to original surveys.
- Frozen opposite-route-fold taxon-specific mapped NWI wetland+emergent coefficients and original run-level C-scores from [Actions 39516056663](https://github.com/zuizui0223/frogcs/actions/runs/39516056663). Reconstruct exactly the 3,659 any-calling and 1,766 strong-calling matrices and check observed C-score per run.
- **Predeclared triple identities** (no reselecting based on outcomes):
  1. central `Lithobates clamitans`, positive partner `Lithobates catesbeianus`, negative `Anaxyrus fowleri`.
  2. same central and positive, negative `Hyla versicolor`.

## Strict earlier-year-only history
- Use historical surveys that precede the target survey **in year**, not same-year earlier run, preventing same-year leakage.
- Season/phenology is controlled by matching previous surveys from the same **State × RouteNumber × RunNumber** stratum, where RunNumber identifies the seasonal survey window. No data from the current or later years enter historical species×SiteID propensities.
- A source-eligible test route-run must have **≥2 previous standardized surveys of the same seasonal stratum** and **≥8/10 physically matching SiteIDs with ≥1 historical opportunity**. These gates depend only on Runs/Stops/SiteIDs, not current frog calls or any test outcomes.
- For every species in each candidate matrix, including nonfocal species and complexes, estimate species×physical-SiteID historical calling probability at primary CI≥1 or secondary CI≥2:
  - `p_route = (positive prior species×site visits + 1)/(all prior sampled site visits + 2)` in the same seasonal route history;
  - `p_site = (positive past visits to SiteID + 4*p_route)/(opportunities at that SiteID + 4)`;
  - `h_site = clip(logit(p_site) − mean(logit(p_site) over target 10 SiteIDs), −3, +3)`.
  - Previous non-positive frog records count as 0 only where a physical site was successfully visited. Unseen SiteIDs receive neutral route-derived `p_site=p_route`. Shared seasonal route prevalence is not a proxy for an individual marked animal's memory.
- **No fitted history effect from the target or later surveys.** The additive coefficient for `h_site` is fixed to **1.0** in the primary null and **0.5** in the mandatory attenuation sensitivity. Do not tune strength to match observed pair signs.

## Matched-null comparison
In every eligible surveyed matrix, retain **all observed species-by-stop positive counts per taxon** and **all stop-level species richness**.

N0: frozen cross-fitted taxon-specific NWI wetland+PEM site weights only.  
N1: exactly N0 + earlier-year taxon×SiteID logit site-history score (strength 1.0).  
Nhalf: N0 + 0.5×historical site score (sensitivity; no optimisation).

- Weighted Curveball Metropolis–Hastings with **199 draws per matrix, 40×n_taxa burn-in, 8×n_taxa thinning**, deterministic seed 2840317. For N0/N1/Nhalf reuse the same per-run seed and original margins; initial states are the observed matrix. Independent draws of weighted chains are not a direct pairwise matched permutation, so report route-clustered differences.
- Run matrix eligibility must match the originally frozen checkerboard sample and both focal trios; no selection by pair overlap or pair residual.
- For all three nulls compute central-positive and central-negative residual co-calling covariance and same-run contrast `D = residual(C,P) − residual(C,N)`. Report N1−N0 expected D, residual reduction fraction (using identical runs), 95% route-clustered CIs and early/late strata; main N1 vs N0 is the prespecified decision.
- For each tested trio require at least **60 eligible runs**, **25 distinct routes**, **20 runs with variable randomized pair contrast**. If not, report `insufficient_prior_history_scope`, not a biological null.
- Require **positive partner residual CI>0, negative partner residual CI<0, and paired D CI>0**, geographic route fold A/B D>0; BH q<.05 across the two fixed trios. Only then call a `persistent_partner_identity_residual_candidate`.
- If N1 makes D CI overlap 0 or collapses either signed edge, classify `prior_site_history_sufficient_or_partially_sufficient`; this is a **first-order statistical sufficiency**, not necessarily abiotic causation. If N1 has a clearly negative mean history transfer log score or extreme mixing failures, do not claim biological sufficiency either.
- Evaluate fixed-k held-out site-choice conditional log likelihood under N0 vs N1 and route-cluster bootstrap (2,000 route replicates, seed 2840319) for overall informative taxon×run units. Because NWI coefficients were fitted on opposite route folds and history is strictly prior-year, the site-history predictor is time-leak-safe, **but the NWI coefficients themselves were trained across years**, so not a fully prospective model.
- Report fraction of null-informative matrices with zero C-score and pair-contrast sampling variation. If >20% unusably mixed, fail closed as `sampling_unreliable`. Original C-score and every pair of row/column margins must match.

## Boundaries
A positive same-survey residual does not identify animal interactions, spatial movement, attraction, competition, or fish/insect mediation. Stable site-use propensity may reflect predation, geography, microhabitat, detection, species occupancy and even past biotic processes. NWI is not actual aquatic plant composition at the survey date. Site survey visits are sequential, not proof of simultaneous signaling. Post-hoc archive extension, never amend frozen RC6 manuscript or SI.
