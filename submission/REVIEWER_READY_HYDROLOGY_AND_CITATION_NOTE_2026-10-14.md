# Reviewer-ready post-hoc hydrology response and Kusano (1999) author-name correction — 2026-10-14

## Scope and submission boundary

This document is a **reviewer-response preparation note**, not a change to the frozen NAAMP inference or a claim of independent confirmation. The JAE paper's scientific endpoints, principal comparators, figures, and numerical results remain unchanged. The current PR changes only one bibliography spelling in `paper/manuscript.md`; it does **not** incorporate post-hoc hydrology into the manuscript's Results or abstract. This document is not evidence that the paper was submitted to or accepted by JAE.

## Ready-to-use reviewer response (English, one paragraph)

We examined whether the within-taxon multi-site concentration might reflect dynamic wetland hydrology using two post-hoc satellite-based proxies. In 1,881 matched survey pairs, adding JRC monthly visible surface-water extent (250-m site support) changed the concentration residual from 0.1745 to 0.1823, a −4.45% reduction. In 1,649 matched pairs, adding MODIS DSWEmod partial/potential-wetland state, three-month persistence and twelve-month variability (500-m site support) changed the residual from 0.5022 to 0.5302, a −5.59% reduction; the residual remained beyond the simulated null envelope. DSWEmod water-state changes were also not preferentially aligned with strong-chorus stops (CallingIndex ≥2; 1,211 informative pair–taxon clusters, permutation P = 0.646). Thus, the tested monthly surface-water proxies did not explain the excess concentration. These results cannot exclude finer hydrological states, such as water depth, water temperature, small ephemeral pools, water beneath vegetation, substrate moisture or changes within days. As these are post-hoc analyses of subsets of the same monitoring programme, we regard them as exploratory checks rather than independent confirmation or grounds for a causal claim.

## Separate prediction question (do not conflate with concentration)

The other DSWEmod analysis studied **whether** an acoustically strong chorus occurs, not **where** a fixed amount of activation is allocated. Route-held-out prediction initially showed a positive incremental gain for the recent three-month wetness metric (equal-species mean Bernoulli log-loss gain +0.010569, route-bootstrap 95% interval +0.002535 to +0.025074). However, the prospectively frozen forward-in-time test (train 2003, 2005–2009; validate 2010–2015) yielded log-loss gain **−0.003588**, 95% route-bootstrap interval **[−0.005858, −0.002186]**. Consequently, the cross-route signal is not established as a temporally transferable hydrological-memory or breeding-readiness predictor. Do not upgrade the intermediate positive route-held-out increment into a general biological finding.

## Key source records (satellite branch only)

- [Remote-sensing hydrology mechanism closure, 2026-10-07](https://github.com/zuizui0223/frogcs/blob/remotesensing/naamp-dynamic-hydrology-v1/remotesensing/REMOTE_SENSING_HYDROLOGY_MECHANISM_CLOSURE_2026-10-07.md): JRC, DSWEmod, null intervals, support/coverage and restrictions.
- [Detailed surface-hydrology closure](https://github.com/zuizui0223/frogcs/blob/remotesensing/naamp-dynamic-hydrology-v1/remotesensing/SURFACE_HYDROLOGY_MECHANISM_CLOSURE_2026-10-07.md): 250-/500-m and classes 1–4 sensitivity, CI≥2 spatial-bridge null.
- [DSWEmod activity prediction result](https://github.com/zuizui0223/frogcs/blob/remotesensing/naamp-dynamic-hydrology-v1/remotesensing/DSWEMOD_REPRODUCTIVE_ACTIVITY_PREDICTION_RESULT_2026-10-07.md): held-out spatial transfer only, with frozen negative overall B0→B3 rule.
- [Frozen temporal-validation specification](https://github.com/zuizui0223/frogcs/blob/remotesensing/naamp-dynamic-hydrology-v1/revision/NAAMP_DSWEMOD_RECENT_WETNESS_TEMPORAL_VALIDATION_V0_1.md): split and stopping rule before outcome readback.
- [Temporal validation and NWI closure commit](https://github.com/zuizui0223/frogcs/commit/e46921824019e1f8a492af945c0abd5bd68db508): recorded temporal gain and confidence interval.
- [Post-hydrology manuscript decision](https://github.com/zuizui0223/frogcs/blob/remotesensing/naamp-dynamic-hydrology-v1/revision/POST_HYDROLOGY_MANUSCRIPT_DECISION_2026-10-07.md): limits, post-hoc designation and paper-use ceiling.

### Interpreting a negative mechanism test

These results constrain **what the tested remotely sensed monthly surface-water proxies can explain**, not whether hydrology matters for frogs. No wetland-by-wetland direct water-depth time series was available for the historical NAAMP comparison. Avoid phrases such as “hydrology ruled out,” “no environmental mechanism,” “individual site fidelity demonstrated,” or “independently confirmed.”

## Bibliographic correction: Kanenko / Kaneko is a source conflict, not an unchecked typo

The 1999 *Herpetological Journal* article has **SHIGENORI KANENKO** printed in the author byline on page 9, and the [publisher's article metadata](https://www.thebhs.org/publications/the-herpetological-journal/volume-9-number-1-january-1999/1556-02-breeding-site-fidelity-in-the-japanese-toad-buja-japonicus-formosus) also says **Kanenko**. But the same original [PDF](https://www.thebhs.org/publications/the-herpetological-journal/volume-9-number-1-january-1999/1556-02-breeding-site-fidelity-in-the-japanese-toad-buja-japonicus-formosus/file) displays **S. KANEKO** in its running author header on page 10 and cites “Kusano, Maruyama & Kaneko, 1995” on page 9.

Corroborating the identity rather than the 1999 title-page spelling:

- [Kusano, Maruyama & Kaneko, 1995, *Journal of Herpetology*](https://www.jstor.org/stable/1564755) lists **Shigenori Kaneko**.
- [Kusano, Maruyama & Kaneko, 2010, *Current Herpetology*](https://www.jstage.jst.go.jp/article/hsj/29/1/29_1_23/_article/-char/en/) lists **Shigenori Kaneko**.
- [Tamotsu Kusano's bibliography](https://salamander.la.coocan.jp/salamander/shiryou/hiki93.html) explicitly lists **S. Kaneko** for the **1999** paper itself.

**Editorial decision proposed in this PR:** the author is Shigenori **Kaneko**; change the reference entry to `Kusano, T., Maruyama, K., & Kaneko, S. (1999).` because the writer's own bibliography and the same author's other records support that spelling. Preserve this source-conflict record because the publisher's original byline/index retains “Kanenko”; a journal production editor may prefer literal source-metadata transcription. The 2026-10-05/06 historical frozen submission receipts correctly recorded their former choice and are not retroactively overwritten.

## Project boundary

- Do **not** reopen or retune the NAAMP primary analysis, rain windows, water-product pixels/radii or post-hoc species subsets.
- Keep the Iowa/ARMI/Hoefer independent draft PR separate; its original survey comparisons do not establish a biological mechanism for the JAE allocation result.
- The next discriminating experiment needs authenticated physical wetland identity, repeated valid audio observation opportunities including non-calls, **direct local depth/hydroperiod and vegetation/substrate conditions**, and a time-blocked test of allocation beyond environmental state and strictly prior site propensity. Seek a real monitoring custodian or collaborator; do not infer this has been acquired from source-discovery records.
- If JAE has already received the frozen bundle, treat the one-word citation edit as an author-side proof/revision decision rather than silently modifying a deposited article.
