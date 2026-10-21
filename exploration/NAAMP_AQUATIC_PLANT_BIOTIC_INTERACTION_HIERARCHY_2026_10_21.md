# Aquatic plants and unseen biotic interaction layers in frog calling networks
Status: 2026-10-21 post-hoc user-directed synthesis, **not** RC6 manuscript evidence.

## Core scientific question

Could the observed relation between mapped emergent wetland plants and some frog taxa's calling locations be a footprint of hidden **biotic mediation** instead of a direct plant–frog response? If so, where in the ecological hierarchy does the unexplained assemblage structure appear: taxa alone, taxon pairs, taxon triples, or different trophic levels?

## What the NAAMP data demonstrably support

**Layer 1 — physical habitat filter:** in a previous NWI–NAAMP analysis, five monitored frog taxon units had positive within-survey associations of strong calling location with mapped 250m emergent wetland PEM cover after BH correction. The effect is **acoustic detection**, not direct observation of individual habitat choice or actual plant species at the frogs' calling stations.

**Layer 2 — pair-identity allocation:** the present novel weighted fixed-row/column NWI null leaves a highly supported **pairwise squared covariance excess** (which is unsigned; it implies some over- and/or under-overlaps among particular taxa).
- CI1–3: **3,659 runs / 478 routes**; observed mean pairwise-squared-centered moment **0.0038623**, expected cross-fitted NWI fixed-margin null **0.0035147**, excess **+0.00034756**, route-clustered 95% CI **+0.00028748 to +0.00040764**, upper-tail MC P **0.005**.
- CI2–3: **1,766 runs / 398 routes**; observed **0.0037683**, expected **0.0033990**, excess **+0.00036931**, route CI **+0.00027620 to +0.00046243**, MC P **0.005**.
- This is still an **association network pattern**, not proven species–species competition or facilitation. Sum of *signed* pairwise covariance over every taxon pair is exactly determined by fixed column and row margins; therefore this test uses **squared individual-pair moments**, not a mathematically invariant total.

**Layer 3 — named three-taxon organization:** a new centered third-order co-calling moment, with pairwise/first-order terms algebraically centered, **does not display robust excess** over the cross-fitted NWI first-order fixed-margin null.
- CI1–3: observed **0.000475972** versus null **0.000478005**; Δ **−0.000002034**, route-cluster CI **−0.000012198 to +0.000008130**, MC upper-tail P **0.670**.
- CI2–3: observed **0.000502990** versus null **0.000487407**; Δ **+0.000015583**, route-cluster CI **−0.000003415 to +0.000034581**, MC upper-tail P **0.030**. Fold A delta **+0.000032865**, fold B **−0.000002500**, and the route-cluster CI covers zero. Therefore **NOT** independently supported under the fixed decision rule.
- The PEM-localized squared third-order moment had no positive upper-tail excess: P **0.935** for any calling and P **0.930** for strong calls.
- Across **29 primary-eligible** and **22 strong-call-eligible** taxon units, none met all three positive network-hub criteria: BH q<0.05, positive route-clustered CI, and both route folds positive. Isolated nominal/taxon-wise deviations exist, but do not establish biological organizers.

Under the present NAAMP/NWI information, the smallest detectable unexplained level is **pair-identity co-calling structure**. The evidence does **not** force a distinct three-species interaction term or a causal chain from plants through frogs to other frogs. A true higher-order process could exist but be missed by 10-stop sequential acoustic sampling, weak regional coverage, taxonomic grouping and the choice of squared centered third moment.

## Biotic hierarchy worth testing, not inferred from NAAMP

1. **Plant habitat engineering:** emergent stalks and floating/submerged vegetation can change breeding/calling surfaces, refuges, prey/predator encounter rates, and acoustic partitioning. Evidence: Burrow et al. 2022, *How plants affect amphibian populations* [Biological Reviews](https://doi.org/10.1111/brv.12861).
2. **Predator / prey mediation:** aquatic plant structure influences where fish and insect predators encounter tadpoles; predator-mediated **indirect facilitation** is real in experimental amphibian systems. Adams et al. 2003 observed non-native fishes increasing bullfrog tadpole survival by depressing dragonfly larvae [Ecology Letters](https://doi.org/10.1046/j.1461-0248.2003.00435.x); Werner & McPeek 1994 showed direct/indirect predator effects across anuran pond gradients [Ecology](https://doi.org/10.2307/1937461).
3. **Behavioural habitat assessment:** male gray treefrog calling-site choice can respond to fish predators and conspecific tadpoles. Resetarits & Wilbur 1991 [Ecology](https://doi.org/10.2307/1940580) explicitly found weak correspondence between calling locations and female oviposition or egg placement.
4. **Acoustic community organization:** mixed-species frog choruses can show central versus peripheral species; Duarte et al. 2021, *Structure and dynamics of mixed-species choruses* [Ethology](https://doi.org/10.1111/eth.13198). Observed coupling is not necessarily direct frog–frog behavioural recruitment.

All four are **literature-backed biological candidates** rather than measured NAAMP causal paths.

## Best discriminating data / intervention

Use precisely co-located and survey-time-matched observations: emergent/submerged plant cover by species and structural class, wetland depth and hydroperiod, water temperature, fish occurrence, odonate/invertebrate predator abundance, acoustic recordings at sub-minute temporal resolution, and repeated taxa-by-site CI/outcome. Measure actual tadpole and egg densities rather than equating male advertisement calls with reproductive success.

An experimentally replicated 2×2 wetland setting (structured emergent vegetation high/low × fish/predator presence/absence) with repeated acoustic recorders and aquatic invertebrate surveys would distinguish biotic mediation from habitat sorting more strongly than more satellite buffers. If frog social acoustic interaction is the focus, add a controlled conspecific/heterospecific playback treatment at fixed local plant/hydrology conditions.

## Provenance and scientific boundary

- Frozen triplet plan: `exploration/NAAMP_THIRD_TAXON_AQUATIC_PLANT_CONTRACT_2026_10_21.md`.
- Numeric full third-taxon result: `exploration/NAAMP_THIRD_TAXON_AQUATIC_PLANT_RESULT_V0_1.json`.
- [Successful GitHub workflow 39527248267](https://github.com/zuizui0223/frogcs/actions/runs/39527248267), archive artifact ID **12313683533**.
- Original plant-conditioned NWI null coefficients were trained on opposite route folds (workflow 39516056663), preserving each species' observed stop total and each stop's total frog-richness. Both third-order modes maintained fixed margins under 199 MCMC draws each, and sufficient varying matrices remained (**2,908 primary**, **1,323 strong**) for tested statistics.
- This is **exploratory reuse of the same monitoring programme**, not independent replication or causation; source NWI is temporally mismatched to frog surveys. Raw acoustic surveys were sequential and do not prove literal simultaneous co-signaling.
- Frozen RC6 manuscript, SI, submission and scientific release are untouched.
