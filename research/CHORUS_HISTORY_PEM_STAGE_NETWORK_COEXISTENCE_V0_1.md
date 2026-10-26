# Chorus history → local environment → stage-network coexistence (prospective v0.1)

Date 2026-10-25. **Research-only extension. Frozen JAE RC6 main unchanged.** Not a new causal result from NAAMP, GloBI or GBIF.

## Two separate frogcs observables

**Historical place use:** NAAMP species×fixed physical SiteID previously strong call → wet strong call: β=+0.151094 (95% CI +0.129127 to +0.173061). Independent NPS 2016–2023 same-species historic site CI≥2 → later annual strong calling remains +0.464188 (95% block CI +0.382566 to +0.533079) after generic other-taxon station acoustic history, Hydroperiod class and recorded effort. Neither establishes that identical individual frogs revisit, nor that wetland plants caused recurrence.

**Concentrated multi-stop spatial pattern:** In NAAMP 2,916 comparisons, observed 1.650320 vs the species×rain response, strictly prior taxon×SiteID probabilities, dry persistence and total wet-activity matched null 1.353466: residual +0.296854 (MC P=.000999). Historic site use is **already in the null**. Do not label the residual directly as history or interactions. Added flexible broad weather removed ~11.4% on the same matched sample, rainfall amount ~6.5% on a different matched comparison, leaving the strong unexplained conditional spatial structure. Local dynamic water level/hydroperiod, flooded calling substrate, plant architecture, species-specific diel timing and predator-stage signals remain unmeasured.

## Spatial/phylogenetic correction

- **Spatial MEM/dbMEM/PCNM** on independently repaired physical SiteID coordinates/verified directed hydrological connectivity: adjust for multiscale spatial dependence. pMEM is predictive Moran eigenvector maps for predictions at unseen sites. The 12,064-row NAAMP coordinate source has serious transcription errors including one positive U.S. longitude, so do not run distance-based MEM until coordinate QA. Route StopNumber is not geographic distance.
- **PEM (Phylogenetic Eigenvector Maps)** instead adjusts inherited similarities among taxa (e.g. reproductive timing, ontogenetic niche shifts, predator guild). Requires external vetted species phylogeny; not a location-adjustment substitute. Separate MEM and PEM can both appear in an integrated model; neither spectral filter demonstrates causality.
- When historical site use correlates with static vegetation and site fixed effects, cross-sectional observation is inadequate to identify which is causal. Use independently measured multi-year within-site changes in local inundation and plant stems, leave-wetland and leave-year-out predictive tests. Do **not** reopen same NAAMP RC6 outcome model; the existing prospective local hydrology spec remains the first experimental comparison.

## Proposed two linked models

**Historical template**:
`logit P(prior_site_strong_{s,i,t}) = b_s + environment_{i,t-1} + local_persistence_{i,t-1} + species×site + spatial_MEM_i + species_phylo_PEM_s + error`

**Current rain expression**:
`logit P(call_CI2plus_{s,i,t}) = a_s + rain_and_weather_{i,t} + past_site_strong_{s,i,<t} + hydroperiod_{i,t} + emergent/submerged_cover_{i,t} + fish/odonate/salamander_stages_{i,t} + interactions + broad_taxon_night_state_{s,route,t} + measurement_detection`.

The first explains why historical acoustic propensity persists; the second tests what reactivates it. Validate against the **conditional multi-site configuration** after preserving first-order wet activity. Spatial eigenvectors/phylogeny are competing controls, not replacement for actual local water and interactions.

## Stage-directed network (consumer → prey)

- Japanese experimental `Aeshna nigroflava` nymphs cue risk to `Hynobius retardatus` larvae, causing reduced salamander attack activity against `Rana pirica` tadpoles and a positive trait-mediated indirect effect for frog larvae (Kishida et al. 2009, DOI 10.1890/08-0238.1).
- Hokkaido tadpoles change inducible morphological defense in response to salamander versus dragonfly larval predators (Kishida & Nishimura 2006, DOI 10.1111/j.1365-2656.2006.01091.x). This is context-dependent niche modulation, not source-inferred predation flux.
- Distinct Australian `Litoria aurea` × `Anax papuensis` case: nymph dragonflies consume tadpoles and postmetamorphic frogs consume emerging dragonflies (Beranek et al. 2023, DOI 10.1002/ecy.4108). This is qualitative **stage-dependent opposite-direction feeding**, not global mortality dominance reversal. Do not merge that system's arrows into a claimed Japanese three-species observation.
- Vegetation can change underwater refuge and predator ambush, emergent stems enable odonate emergence and adult frog foraging, and a changing waterline changes both populations' stage windows. Test submerged stems and emergent emergence substrate separately; coarse EarthEnv class8 is *not* stem density.

## Does more synchronized development imply coexistence?

**No unconditional positive claim.** Synchronizing `odonate_nymph × tadpole` can increase direct attacks. Synchronizing `odonate_nymph × salamander_larva` can reduce tadpole predation indirectly by risk suppression. Synchronizing `frog_postmetamorph × dragonfly_emergence` can reverse who eats whom. Emergence timing and earlier larval grazing also alter species recruitment; relative phase has competing signs.

Define stage potential `E_(i,a→j,b)(x,t)=N_i,a N_j,b encounter(x,t,V,H) attack_success(size,gape,cover)`. Its sign is consumer/prey direction, separate from effect on species growth. GloBI gives candidate edge topology, GBIF stage×1° month cells show source-report opportunity; **neither gives N, encounter rate, attack success or same-pond killing**. For true coexistence require long-run persistence/mutual invasibility of each species under shared seasonal dynamics, not maximum overlap.

## Implemented computational test

[Executable seasonal trophic toy](scripts/simulate_seasonal_trophic_network.py) with four synthetic overlap kernels: salamander_larva→tadpole, odonate_nymph→tadpole, odonate_nymph risk→salamander_larva, frog_adult→emerging_odonate. Annual three-guild population map with stage-time integration and artificial food/attack/refuge/risk feedback. Twenty-one? Actual phase grid is **18 combinations** = 3 salamander offsets × 6 odonate offsets; 256 independent random parameter scenarios, 550 model years, 4 different initial starting conditions; persistence >1 in all three guilds through last 50 years under all starts. **No field calibration, no explicit stage-abundance compartments, no proof of mutual invasibility**.

[Only synthetic output](results/synthetic_stage_network/synthetic_results_summary.json): across phase configurations persistence spans 118/256 to 237/256 parameter draws. Strongest asymmetrical timing occurs in this *chosen artificial ensemble*, not a species-specific prediction. The parameter shape and ordering must not be reported as empirical evidence that staggered phenology always stabilizes communities. Future strict ecological tests need matched local stage censuses and empirical attack/maturation and wetland vegetation coefficients.

## Falsification and next empirical priority

First test **local wetland hydrology and plant architecture vs prior site acoustic use**; only afterward add independently measured larval predators and predation cues and see whether the conditional multi-site chorus residual shrinks **out-of-site/year**. Separately compare actual stage-specific predator attacks/animal recruitment under experimentally staggered vs synchronized emergence windows, controlling overall densities, stage duration and habitat mosaic. Do not join NAAMP acoustic SiteIDs to unrelated GloBI/GBIF records as if they were measured together.
