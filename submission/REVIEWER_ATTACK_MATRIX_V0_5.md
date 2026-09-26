# Reviewer attack matrix v0.5 — RC6 metacommunity synthesis

| Likely attack | RC6 answer | Status |
|---|---|---|
| “Rain makes frogs call” is textbook natural history. | Agreed. The raw rainfall association is context. The contribution is localization across active spatial footprint, local alpha, route gamma, beta diversity and four exact species × site incidence components. | Addressed |
| “Metacommunity” implies dispersal-connected demographic populations, which NAAMP does not measure. | The manuscript defines an operational behaviourally realized active community / metacommunity-scale sampling system and explicitly disclaims demographic connectivity, dispersal, colonization and extinction. | Addressed with terminology boundary |
| Alpha and gamma increasing makes the beta result partly mathematical. | RC6 reports pairwise Sørensen, turnover, nestedness and normalized Whittaker beta in addition to alpha and gamma. The matrix decomposition is also incidence-level rather than inferred from diversity arithmetic. | Addressed |
| A non-significant beta coefficient does not prove beta diversity is unchanged. | Correct for the beta metrics: RC6 uses “no detectable shift.” Separately, active-matrix fill passed a frozen ±0.05 practical-equivalence margin in both the primary and exact-year samples. This equivalence applies only to matrix fill, not to every beta-diversity quantity. | Addressed with explicit SESOI boundary |
| The matrix decomposition is just relabelling richness. | No. The four incidence components are mutually exclusive and sum exactly to total species × stop incidence change. They distinguish new species/new sites, existing species/new sites, new species/existing sites and within-core rearrangement. | Addressed |
| “Route-new species” sounds like colonization. | Route-new means detected only in the wetter member of a paired acoustic survey. The manuscript explicitly blocks colonization/occupancy language. | Addressed |
| Local alpha rises only because newly active stops enter the denominator. | Same-StopNumber analysis restricted to stops active in both surveys remains positive (beta≈+0.095 species/stop, P≈.002). | Addressed |
| More multispecies stops could be only a 1→2 threshold effect. | Exact depth decomposition shows ~71% of the active-stop alpha slope lies beyond the second species. | Addressed |
| Wet surveys may simply have better acoustic detectability. | Adjusting recorded hearing impairment, major-noise timeout and wind retains footprint, alpha and gamma effects. Traffic and MassNoiseIndex sensitivities agree. This constrains recorded detection conditions but does not eliminate unmeasured masking. | Addressed with qualification |
| Large choruses may mask some species. | Species-specific masking cannot be fully modelled from NAAMP. Recorded noise/timeout robustness helps, but the manuscript keeps acoustic detectability as a limitation. | Open limitation |
| Season/phenology explains everything. | Pairs are within the same RunNumber seasonal window with DOY-difference adjustment; breeding-season/phenology follow-ups did not supply a robust simple mechanism. Species-specific seasonal confounding cannot be claimed eliminated. | Partly addressed |
| Rainfall amount is not measured—only DaysSinceRain. | Correct. Claims concern rainfall recency/contrast, not precipitation amount, soil moisture or causal hydrology. | Hard boundary |
| Post-opening analysis proliferation looks like p-hacking. | The original rainfall programme endpoint was frozen before readback. Community extensions are explicitly post-opening; each was versioned/frozen before its own endpoint readback, negative tests are retained, exact identities are used where possible, and no failed mechanism was retuned into a positive claim. | Addressed with transparent evidence hierarchy |
| Exact-year sensitivity is not independent replication. | Correct. It is a stricter within-dataset sensitivity, not independent validation. | Hard boundary |
| Functional traits are too coarse to support filtering conclusions. | RC6 does not claim comprehensive filtering. The four-axis panel is finite, coverage is reported, CWM/MPD results are bounded to that space, and unmeasured response traits are named as a limitation. | Addressed |
| Functional distance failing to predict rain response may just reflect phylogeny. | A 100,000-permutation within-family sensitivity is also null. This still does not constitute a phylogenetic comparative analysis. | Addressed with boundary |
| Species-specific rain responses are not temporally stable. | Overall wet/dry response magnitude has weak rank repeatability, but a different species property—the opportunity-corrected placement of wet-gain incidences at newly active versus already-active sites—is strongly repeatable across non-overlapping periods (rho=.774; 15/16 same sign). RC6 distinguishes response magnitude from response geometry. | Addressed by response-trait decomposition |
| Activation geometry is just a consequence of some routes having more inactive stops available. | The species model uses logit(q_pair), where q_pair is the drier-run inactive-stop fraction, as an offset. The species intercept therefore measures gain placement relative to available spatial opportunity. Pairs with q=0 or 1 are structurally uninformative and excluded before fitting. | Addressed |
| Activation geometry is a disguised dispersal or colonization trait. | No. It is explicitly defined as acoustic gain placement conditional on wetter-run gains. No occupancy, movement, colonization or dispersal mechanism is inferred. | Hard boundary |
| Activation geometry could simply reflect family/phylogeny. | Possible. Family-adjusted temporal validation did not meet the frozen coverage requirement, so RC6 does not claim phylogenetic independence. Conventional four-axis life-history traits show no strong descriptive alignment, but that does not substitute for a phylogenetic comparative analysis. | Open limitation |
| Response diversity should stabilize richness if it is ecologically important. | A held-out 2001–2007 → 2008–2015 buffering test was performed and was unsupported. Response diversity is described as a distinct response dimension, not as demonstrated insurance. | Addressed by falsification |
| Spatial specialists should be the rain-recruited species. | A held-out early spatial-breadth test falsified the prespecified specialist prediction; the opposite pooled association was not family-robust and is not promoted. | Addressed by falsification |
| Baseline spatial heterogeneity should expose more latent species under rain. | A held-out positive-moderation hypothesis failed its frozen support rule; secondary opposite-direction patterns are not used as a headline mechanism. | Addressed by falsification |
| The ≥8-day timescale reference is sparse. | Agreed. Week-scale language was removed from title/abstract/core inference. Timing is secondary and supports only “not strictly same-day”. | Addressed |
| Main effect sizes are small. | Effect sizes and CIs are reported in native units; the paper’s contribution is multiscale structure, not a claim of large demographic change. | Addressed |
| Stops within routes are not independent. | Models use route-clustered covariance with State and RunNumber controls; key comparisons are wet-minus-dry within route × seasonal-window strata. | Addressed |
| Stop habitat heterogeneity could drive composition. | Pairing holds route and numbered stop structure fixed across years; same-stop analysis further fixes stop identity. NAAMP source tables do not provide a complete habitat covariate set, so time-varying habitat cannot be fully excluded. | Partly addressed |
| Null functional and beta results could be underpowered. | RC6 reports CIs rather than interpreting P>0.05 as proof. Exact-year sensitivities and multiple beta metrics are shown. Any stronger “equivalence” language requires a frozen SESOI test. | Hard boundary |

## Strongest current claim

> **Recent-rain surveys expand the behaviourally realized frog community along both spatial and taxonomic axes, with most added incidences opening matrix boundaries; species also show a temporally repeatable activation geometry that separates spatial-edge activators from local taxonomic deepeners, while conventional life-history traits do not strongly encode that response mode.**

## What would change the paper materially

Only three classes of new evidence justify changing the main story:
1. a prespecified test showing material change/equivalence in an explicit matrix-structure quantity;
2. a genuinely proximal, independently sourced response trait with adequate coverage and frozen prediction;
3. an external/independent monitoring system estimating the same multiscale quantities.

Everything else belongs in Supporting Information or future work.
