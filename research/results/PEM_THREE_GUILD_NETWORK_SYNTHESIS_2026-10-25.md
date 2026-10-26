# NWI PEM抽水湿地 × カエル繁殖同調 × サンショウウオ・ヤゴの発生段階ネットワーク

**2026-10-25 — Forward mechanistic research, not a second result of the frogcs frozen JAE RC6 manuscript.** `PEM` is the U.S. NWI **Palustrine Emergent Wetland** geomapping code, NOT phylogenetic eigenvector maps. Primary programme: predict when a shared hydroperiod/vegetation class permits breeding-site recurrence and stage-dependent predator constraints, not claim existing NAAMP audio already measured these attacks.

## Q. Had PEM-related tendencies already been found?

**No NWI PEM1A/1C/1F class-vs-chorus slope has been calculated from verified NAAMP or NPS wetland polygons.** The exact `main` RC6 outputs support species-specific strict prior-site chorus targeting (β=+0.1511) and rain-gated multi-site concentration residual (+0.2969 after conditioning on history and other terms); NPS independent acoustics supports repeat use after broad hydroperiod/generic other-taxon site chorus and monitoring effort (adjusted association +0.4642). These are *not a causal or specific PEM classification result*.

Two genuinely relevant but **not NWI PEM-specific** wetland findings:
- Hamer et al. (2021) [10.1002/eap.2293](https://doi.org/10.1002/eap.2293) reports fish×emergent cover positive interaction for some frog species in occupancy across 55 Australian wetlands. This is literature external to NAAMP and *not a species-specific past-site chorus test*.
- Our source-audited EarthEnv 2014 (historical class-8 **regularly flooded vegetation**, not a USFWS NWI PEM polygon) × GloBI/GBIF full-source stage reporting found a primary low-to-high flooded-vegetation-background change in known-vs-matched-prey phase specificity **−0.0281** among 32 same pairs, no consistent positive habitat mediation; dragonfly larva/adult source-reporting in 19 species showed a small open-water background shift, but 1° flooded vegetation association uncertainty spanned zero. [Actual data report](GLOBAL_WETLAND_ONTOGENETIC_INTERACTIONS_2026-10-25.md).

### NWI source and why it is the correct hypothesis variable

[USFWS official code + REST schema audit](NWI_PEM_OFFICIAL_CODE_READINESS_2026-10-25.json) has exact NWI names:
- `PEM1A`: palustrine emergent, persistent stems, **temporary flooding**.
- `PEM1C`: palustrine emergent, persistent stems, **seasonal flooding**.
- `PEM1F`: palustrine emergent, persistent stems, **semipermanent flooding**.
- `PEM2F`: palustrine emergent, **nonpersistent** stems, semipermanent flooding.
- Official service https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer, polygon layer 0 `ATTRIBUTE` and `WETLAND_TYPE`, code table layer 1 with explicit `WATER_REGIME_NAME` etc.

These **mapped static classes** do not measure survey-event water, underwater refugia, plant stem density, larval odonate abundance, or animal community. A 'historically chorused SiteID = PEM1C' statement requires response-blind repair of known USGS NAAMP point transcription errors, authoritative wetland polygon and source image date QA. Do **not** auto-attach NWI by unreliable raw USGS coords.

## One integrated biological hypothesis, three constraints

> **Rain-triggered frog adults may congregate at historically repeatable PEM wetlands because their seasonal hydroperiod and emergent-stem mosaic provide a persistent reproductive and refuge template. A short frog breeding pulse can synchronize same-species hatchlings and avoid cannibalism by older conspecific tadpoles, while independently the relative timing and size of dragonfly nymphs and salamander larvae create direct predation and an indirect dragonfly→salamander→frog positive pathway. Changing PEM water permanence shifts both risk windows and the opportunity for postmetamorphic frogs to consume emerging odonates, potentially reversing a species pair's trophic arrow.**

Three **non-equivalent mismatches**:
1. **frog old→young cohort size mismatch**: an established mechanism. Petranka & Thomas 1995, *Explosive breeding reduces egg and tadpole cannibalism in the wood frog, Rana sylvatica*, [DOI 10.1016/0003-3472(95)80133-2](https://doi.org/10.1016/0003-3472(95)80133-2). >80% wood frogs bred within 3 days, protected synchronous offspring; delayed eggs and hatchlings were consumed by larger older tadpoles. **This is intraspecific**, not evidence salamanders/odonates also cannot prey.
2. **frog larval timing/size vs D/S attack-capable stages**: Rudolf 2022 [DOI 10.1002/ecy.3704](https://doi.org/10.1002/ecy.3704) in separate salamander–bronze frog and dragonfly–leopard frog experiments found prey arriving late dramatically increased predation; sign and magnitude depended on temperature/nutrients/gape limitation. *Maximal temporal disjunction* can instead eliminate predator encounters, so generic mismatch ≠ universally higher mortality.
3. **predator-specific defensive phenotype mismatch**: Japanese `Rana pirica` tadpoles must grow body/tail phenotype appropriate for `Hynobius retardatus` suction/gape versus `Aeshna nigroflava` biting, or suffer higher attacks (Kishida & Nishimura 2005/2006 [DOI 10.1111/j.1365-2656.2006.01091.x](https://doi.org/10.1111/j.1365-2656.2006.01091.x)). `Aeshna` predator-risk cues suppress `Hynobius` foraging and their antagonistic armament, indirectly protecting `Rana` (Kishida et al. 2009 [DOI 10.1890/08-0238.1](https://doi.org/10.1890/08-0238.1)). The opposite signed **D→F direct versus D⊣S⊣F indirect** effects exist simultaneously.

**Different species-pair role reversal**: `Anax papuensis` nymph consuming `Litoria aurea` tadpoles versus adult/juvenile frogs consuming dragonflies during emergence on `Typha orientalis` and `Bolboschoenus fluviatilis` stems (Beranek et al. 2023 [DOI 10.1002/ecy.4108](https://doi.org/10.1002/ecy.4108)). Do **not** project the Australian reverse feeding arrow as if proven for the Japanese Hokkaido triad. No observed net mortality/biomass flux dominance reversal.

## First executed PEM-specific theoretical model — importantly synthetic

[Source specification](../PEM_STAGE_CONSTRAINT_NETWORK_SPEC_V0_1.md) | [Code](../scripts/simulate_pem_three_guild_stage_balance.py) | [source outputs](pem_three_guild_stage_balance/synthetic_results.json) | [GitHub Actions pass](https://github.com/zuizui0223/frogcs/actions/runs/40203066228).

Modeled three hypothetical wetland hydroperiod windows (PEM1A/C/F), frog narrow vs diffuse egg pulses, 3 dragonfly-larval seasonal offsets, 3 salamander-larval offsets, submerged cover (2 levels), dragonfly→salamander behavioral risk strength (2 levels), two opposing synchronized-cohort density-crowding assumptions. Shared **128 synthetic parameter draws**, 250 annual Beverton–Holt recurrence years and rare-start initial conditions from an existing illustrative model. 432 model cases; **216 exact-paired narrow-vs-diffuse contrasts**.

- With **no additional frog-brood crowding cost**, narrow frog pulses yielded higher heuristic three-guild persistence in all **108/108** scenario contrasts. This is to be expected because the mechanism includes **assumed** frog cohort size-match/satiation advantages.
- With deliberately **large countervailing brood crowding/resource-depletion or predator-aggregation cost**, diffuse pulses were higher in **96/108**, 12 tied. A mathematical counterexample to the universal `breeding synchrony → larger three-species coexistence` claim, **not evidence that PEM wetlands are diffuse breeders**.
- In some hypothetical high-dragonfly-risk-cue settings, the indirect reduction in salamander attack can outweigh direct dragonfly→frog attack for parts of the drawn parameter ensemble, matching the **logic**, not field effect size, of the 2009 cue study.
- Short-hydroperiod PEM1A is highly sensitive in this **assumed phenology** to egg-laying spread: eligible continuous-water-through-metamorph frogs differ massively by artificial brood timing assumptions. The absolute PEM-specific persistence fractions are **model outputs not fit to wetlands, not empirical results, and not valid prevalence estimates**.
- Coexistence in script = positive abundance over late 30 years under four initial conditions, **NOT mutual invasibility**. Annual lineages plus fixed stage activity kernels are **not a complete age-structured ABM/PDE**. Finer model requires actual cohorts, individual growth/gape defense induction lags, pond-specific water-depth history and food-web stage attack parameters.

## What remains scientifically unresolved and the next test

**Direct question 1: persistent PEM and historical frog chorus sites**: does `PEM1A/C/F`, `PEM1 vs PEM2`, ephemeral `PUB/PAB`, mapped wetland-to-pond interface, true event hydroperiod and reed-stem class explain historical same-species calling spots *and* the remaining conditional multistop spatial concentration when tested on out-of-wetland/year data? Main RC6 model must remain frozen; old site geometry must be repaired blind to frog calls first.

**Direct question 2: predator stage avoidance vs same-species cohort synchronization**: distinguish frog first adult chorusing → actual egg deposition timing → tadpole cohort stage/body-size distribution → predator-specific size/gape defense match, independently of frog cohort cannibalism. Need egg/tadpole weekly time series and recorded adult chorus, not co-report across country or GBIF 1° month.

**Direct question 3: triple risk balancing**: in each wetland × fortnight estimate direct D nymph→F tadpole, S larva→F tadpole, D nymph→S larva behavioral risk, and F juvenile→D emerging attack where natural-history verified; compare additive pairwise to stage-specific 3way risk-mediated model. Record both predator and prey stage, growth/gape, vegetation refuge and emergence substrate, and independent measurement of predator abundance.

**Direct question 4: coexistence**: three-guild **invasion growth rates** into realistic two-species resident assemblages with measured stage survival and wetland hydroperiod, plus 5/10/20-year temporal persistence and dispersal across PEM mosaics. Species×stage time synchrony and gape/defense mismatch have **distinct** possible signs. No observed co-reports or model's four rare starts prove actual coexistence.

**Main discriminating prediction:** If PEM1A+C wetland water windows and independent D/S larval stages explain history and rain concentration but adding interspecific risk adds no predictive gain, the original effect is environmental; if stage-matched D/S interaction has held-out predictive value beyond water/PEM and conspecific cohort timing, a trophic constraint model is supported. If neither resolves the RC6 concentration residual, social/demographic readiness and unmeasured microhydrology remain alternatives.
