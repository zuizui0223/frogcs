# Frog species identity in a common survey: independent-route predictive falsification (2026-10-22)

**Study status:** newly frozen user-directed exploratory follow-up to the prior species×SiteID first-order null. Outside RC6/JAE submission evidence.

## Scientific question

The prior same-route and strictly-prior SiteID history tests show an unusually positive central `Lithobates clamitans` × `L. catesbeianus` signed co-calling residual and negative central × `Anaxyrus fowleri` / `Hyla versicolor` residual. Those are already proven *descriptive* pair configurations; repeatedly testing their means cannot independently establish a mechanism.

This study instead asks a predictive question: **Given a previously unseen surveyed route and the positions of the other calling species on that route, does knowing the identity of the two partner taxa predict where the central frog was heard, beyond both past site use and general same-stop chorus richness?**

Two fixed focal triples, no taxon/radius/threshold selection after results:
1. central C = `Lithobates clamitans`, established positive partner P = `Lithobates catesbeianus`, candidate negative partner N = `Anaxyrus fowleri`.
2. C and P unchanged; N = `Hyla versicolor`.

This is **not** a test of causal biotic interactions, physical coexistence, animal memory or the existence of a genuine irreducible three-way interaction. Listening stops were visited sequentially.

## Frozen source and longitudinal gate

- Exactly the successful original NWI site-complete 3,659 CI1–3 matrices (primary) and 1,766 CI2–3 matrices (secondary), original observed C-score reproduced for every matrix.
- Source geocoding: pre-outcome USFWS NWI full 12-shard source overlay from Actions 39450277196. First-order taxon-specific total wetland + PEM 250-m coefficients trained on *opposite geographic route folds* and frozen in artifact from Actions 39516056663.
- Historical species×SiteID scores, fixed from previous analysis (Actions 39603785733): exactly the same **strictly earlier survey years** within each State × RouteNumber × seasonal RunNumber. At least **2 previous surveys in the same seasonal stratum and at least 8/10 revisited physical SiteIDs**. Per-site empirical Bayes-smoothed log odds, fixed strength **1.0**, cap ±3. The current survey year is never used to construct historical scores.
- All nonfocal species and unresolved monitoring taxa remain in the original fixed-margin matrix; no outcome-based route deletion. The response is conditional acoustic allocation **given that C, P, N were heard somewhere**.
- The 250-m NWI map need not match 2001–2015 plant communities. Site-history covariate may reflect predators, previous biotic interactions, microenvironment or detection bias.

## The exact fixed-margin conditional choice test

For one qualifying route-run with central species C and both partner taxa P and N active, select every *alternate taxon j* also active on the same route-run, excluding C/P/N, satisfying that both `C\\j` and `j\\C` have at least one stop. Each choice event exchanges **only** the exclusive listening stops belonging to C versus j.

The choice of which of the exclusive sites belongs to C (the remaining sites belong to j) is enumerated over all possible equally-sized candidate subsets, with

- each species' observed ten-stop number of positive-call sites fixed exactly;
- every stop's observed species richness fixed exactly;
- every other taxon's presence vector (including P and N) held fixed for that event.

This is an **exact** `choose(|S|,|C\\j|)` conditional logistic scoring problem with at most 252 candidate sets. It is a local fixed-margin **pseudolikelihood**, **not** the joint probability/likelihood of a complete frog community matrix.

For candidate C sites, the **fixed offset** is the sum of
`[frozen NWI+priorSiteID score_C(site) - frozen NWI+priorSiteID score_j(site)]` over the candidate exclusive sites. These offsets are *not re-fitted* here.

Additional candidate features are the respective sums at sites assigned to C:
- `R`: count of all calling taxon units *other than C, j, P, N* at each site, accounting for generic community chorus richness (nuisance);
- `XP`: whether P called at that stop;
- `XN`: whether N called at that stop.

**M0**: fixed NWI+strict prior-SiteID offset + fitted nuisance coefficient gamma for `R`.
**M1**: the identical fixed offset + gamma for `R` + *both separately fitted* partner coefficients betaP and betaN.

Training: conditional logistic exact-subset maximum likelihood, **ridge penalty (3/2)·sum(coefficients²)**, each coefficient bounded **[-3,+3]**. Identical optimizer, eligibility and per-run weighting for M0/M1; if any model fails to converge or its design has insufficient rank, use baseline/fail-closed and explicitly report why, never replace with a different method. Every run contributes equal total weight, dividing its objective over qualifying alternatives j.

## Primary inference and gates

- Deterministic original SHA256 route folds A/B. Fit all coefficients **only on one route fold**, predict the opposite. Aggregate log predictive probability **per route-run** (average over its eligible nonfocal swap partners).
- Require ≥60 qualified survey runs, ≥25 routes, ≥20 runs *per* held-out fold, ≥40 candidate informative swap events and ≥20 runs with variation of each partner feature. Otherwise report `insufficient_scope`, not a zero effect.
- Main metric = **held-out M1−M0 conditional log-pseudolikelihood in nats/run**; 2,000 route-cluster bootstrap replicates (seed 2840327), 95% CI. Both held-out geographic fold mean gains must be positive, and CI lower bound must exceed 0.
- Mechanism-consistent signed prediction further requires betaP>0 and betaN<0 in **both independent training folds**; BH q<0.05 (two-sided route-level normal/cluster-robust test) across the **two fixed trios**. A positive held-out gain *without* both predicted directions is not a `signed_partner_prediction_candidate`.
- **Same-sample 2001–2009 train → 2010–2015 test** is a named descriptive transfer check; require ≥30 early informative runs across ≥15 routes and ≥30 late informative runs across ≥15 routes. The original NWI coefficients were trained across years, so this is **not** an independent chronological confirmation; label accordingly. Run-fold and temporal procedures are NOT interchangeable.
- Primary = any calling CI1–3. Strong chorus CI2–3 = fixed secondary; cannot override a negative primary.
- Report number of candidate swaps/run, active taxa, nonfocal alternatives, exact candidate set counts, training rank and optimizer convergence, route-fold signs, historical rows, source C-score match, and all holdout score changes.
- A positive result supports **transferable partner-identity information** under this exact local fixed-margin choice test; it does **not** imply active choice by an individual animal, acoustic attraction or physical predation-mediated mechanism.
- If M1 fails to beat M0 under held-out scoring, the previously observed same-night residual remains real but the proposed pair-identity predictive model is **not transferable** under this scoring rule.

## Limits and stop rule

- Do not hunt among other partner taxa, new radius scales, species subsets, alternate seasonal windows, interaction orders or ridge penalties after readback.
- Stop modeling if this gate fails. An independent organism-level study measuring actual aquatic plants, wetland hydrology, fish/odonate predator context and continuously recorded frog calls would then be the useful next evidence.
- No edits to RC6 frozen JAE manuscript, SI, main branch or submission.
