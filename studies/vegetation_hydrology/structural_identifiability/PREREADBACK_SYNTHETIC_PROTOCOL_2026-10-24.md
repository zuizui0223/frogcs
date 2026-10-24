# SITE-HISTORY × HABITAT: structural identifiability & synthetic measurement test
Date: 2026-10-24. Frozen **before this new synthetic simulation is run**.
Branch: `research/chorus-history-structural-identifiability-2026-10-24`. `main`, JAE RC6 and the separate 2026-10-24 outcome result are NOT modified.
No original NAAMP acoustic `Counts.csv` will be used here.

## Scientific question
Can a strong predictor based on a frog taxon's **previously recurring acoustic listening stations** distinguish two ecological explanations?
- H_ENV: persistent fixed-site differences are ecological habitat suitability.
- H_SITE: persistent fixed-site differences arise from an unmeasured route-site state (e.g. demography/detection/social readiness).
Also, can a **remote monthly open-water proxy** establish a transient local-wetland state mechanism when submerged vegetation masks surface water?

The first two hypotheses are *observationally equivalent without restrictions* on the unmeasured site effects. This is a negative **structural identifiability** statement, not evidence which mechanism truly operates.

## Mathematical test (strict equality, no stochastic acoustic observations)
For route with ten original locations and fixed number `k` of strong chorus stops, use
`P(Y_t=y | sum(y)=k) = exp(sum_i y_i eta_it) / sum_{a:sum a=k} exp(sum_i a_i eta_it)`.
For a time-constant mapped habitat `E_i` and unrestricted latent site effect `U_i`, let `eta_i = beta E_i + U_i`. For ANY `c`, the parameter transformation
`beta_prime=beta+c`; `U_i_prime=U_i-c*E_i`
keeps all `eta_i` and all observable placement probabilities unchanged. Thus `beta` is not identified from conditioned acoustic placement alone even with arbitrarily many repeats. Constraints on `U`, measured dynamic habitat, exogenous manipulation, or truly novel sites could break the equivalence. A route-wide time effect disappears when conditioning on `k`.

Numeric verification: use actual 500-m USGS NLCD Collection 1.2 class proportions at original NAAMP physical stations (environment-only), construct `eta_i=2.0*(woody+emergent wetland fraction) + 0.8*(mapped open-water fraction)` and an equivalent `eta_i=U_i` with `beta_prime=0`, `U_i=eta_i`. Verify identical conditional distributions for `k = 2, 3, 5` across 333 distinct physical routes with EXACTLY 10 mapped sites. No frog outcomes. Tolerance max abs probability difference <1e-12.

## Locked environmental/source sample
- Source `nlcd_c1v2_2001_2015_site_year_buffers.csv`, original full C1V2 500-m habitat, exact SHA256 **137ad705641e39b1a43acfb0d1c5c4aef1fce7024ccb788fb1efc67510a2c67a**, 64,779 site-year rows; **not** raw frog outcomes.
- Collapse survey years by mean per `RouteNumber × SiteID`; restrict to *exactly 10 accepted physical sites per route*; choose 333 routes with smallest SHA256(RouteNumber), sorted. This matches the previous exploratory outcome analysis's **333-route scale** without using its acoustic route membership. The selected routes are a deterministic synthetic design frame, **not an external validation set**.

## Synthetic transient water instrument experiment (illustrative model, not estimated)
- Same 333 route × 10 site habitat backgrounds. A known but **synthetically generated** true preceding-event inundation `W_it~Bernoulli(pi_i)` independently at two occasions, `pi_i=expit(-0.5+1.5*wetland_i+1.0*openwater_i)`. The assumed true effect is `gamma=1.5` log placement weight for `W=1`. Persistent habitat weight `eta_base=2.0*wetland_i + 0.8*openwater_i`. Fix strong-chorus count `k=3` (secondary numerical check `k=5`).
- Truth: `eta_true=eta_base + gamma*W`. Static prediction without event water: `eta_static=eta_base + gamma*pi`.
- Synthetic monthly water classification among accessible pixels: specificity **0.98** (false-positive 0.02). Sensitivity varies with *predeclared* NLCD map class: `open_water>=0.10` → **0.90**; `woody+emergent wetland>=0.25 AND open_water<0.01` → **0.12**; all other sites → **0.55**. These are HYPOTHETICAL illustrative values, NOT estimated pixel sensitivities from the 15-year observational data.
- Given synthetic classification `Z`, use the **known** sensitivity/specificity/true prevalence to calculate `q_i=P(W_i=1 | Z_i)`, then predict `eta_proxy=eta_base + gamma*q_i`. This gives the proxy an *idealised correctly calibrated* observation model, an intentionally optimistic benchmark, not the actual JRC data accuracy. Route×month visibility is simulated at probability **0.79**; complete-route absence is excluded, not coded as 0. NB weather/detection correlated missingness in reality may be worse.
- For each route/occasion generate a full exact-k conditional placement distribution, not realised frog calls. Compare oracle and proxy **expected log score improvement** against static prediction: `sum_y P_true(y) [log(P_target(y)) - log(P_static(y))]`. This is simulation expectation, **not NAAMP held-out log-score gain**. Report when the proxy captures a fraction of the oracle information.
- Replicates `R=80` independent seeded simulations, RNG seed **2840223**; evaluate both `k=3` and `k=5`, 333 routes, no source/response tuning. No effect hypothesis testing on synthetic data. Record Monte Carlo spread as algorithmic variation, not confidence intervals for ecology.

## Decision and stop
If any simulation result depends strongly on these assumed sensitivities, say so. The validity of the structural equivalence theorem does not depend on assumptions. A site-level time-varying environmental predictor is only structurally estimable if it has site × time variation after route-night and fixed-site effects and isn't confounded with time-varying detection, with a known/validated observation process. A null marginal JRC increment in the new exploratory NAAMP fit cannot be construed as no local water effect.

## Negative safeguards
No `Counts.csv`, no source outcome readback, no new NAAMP model refitting, no parameter tuning based on the earlier +0.00593 point estimate. Simulation values are explicitly illustrative and may not be used as estimated frog effect sizes, detection sensitivities, or sampling-power guarantees.
