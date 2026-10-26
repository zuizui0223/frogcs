# Ontogenetic trophic role reversal in wetland frog communities — prospective study v0.1

Date: 2026-10-25. Status: **new prospective research track; no outcomes from this study examined or claimed**.

**Boundary:** This document does not revise the locked RC6 Journal of Animal Ecology manuscript, the NAAMP inferential endpoints, the submission branch, or the decision not to pursue WFTS. It is an independent extension of the ecological questions raised by [frogcs RC6](../paper/manuscript.md) and the [prospective local-hydrology discrimination plan](../revision/PROSPECTIVE_LOCAL_HYDROLOGY_DISCRIMINATION_SPEC_V0_2.md).

## 1. What the current repository can and cannot establish

- **Observed (acoustic):** NAAMP matched 4,236 wetter–drier comparisons, 53 positive taxon labels, 585 routes and 21 states; strong calling is re-expressed at recurrent sites and within-taxon multi-stop concentration exceeds the primary null (history-eligible 2,916 pairs; observed 1.6503, expected 1.3535, residual 0.2969, MC P = 0.000999).
- **Observed (interspecific acoustic participation):** alpha richness at active stops and route gamma richness increase after recent rain (matched slopes +0.0794 and +0.2859); about 71.1% of the active-stop alpha slope is richness beyond the second caller. This is multi-taxon co-calling, **not** evidence for facilitation, competition, predation or simultaneous calling.
- **Not supported:** the held-out response-diversity × rainfall buffering test (P = 0.419), mean pairwise functional-distance expansion (P = 0.285), and primary between-year turnover change (P = 0.104). Do not promote null/unstable traits to mechanisms.
- **Not measured in NAAMP:** adult frog abundance/sex, eggs, tadpoles, metamorphs, salamander larvae/eggs, dragonfly nymphs/emergence, direct attacks, predator cues, event-level macrophyte architecture, local water level/hydroperiod or survival to recruitment. CallingIndex is an ordinal *calling* outcome, not spawning success or abundance.
- **Geographic QC:** the pinned 12,064-row SiteID coordinate file contains implausible within-route distances and transcription errors (including one positive US longitude); see [QC](../revision/NAAMP_COORDINATE_GEOMETRY_QC_V0_1.md). No wetland-level or cross-taxon raster join is valid until a response-blind, externally verified site geometry table exists.

## 2. Verified mechanism modules (literature, not frogcs results)

| Module | Verified example | Interpretation boundary | Primary source |
|---|---|---|---|
| Odonate-to-frog direct predation | Anax papuensis nymphs take Litoria aurea tadpoles | Stage-specific, not all Odonata or all frogs | Beranek et al. 2023 review of paired evidence, https://doi.org/10.1002/ecy.4108 |
| **Same species pair reciprocal direction** | Litoria aurea juveniles/adults ate Anax papuensis nymphs during emergence/metamorphosis | Observed predation events; field-level population effect and net flux not measured | Beranek et al. 2023, https://doi.org/10.1002/ecy.4108 |
| Gape/size dependence | Hyla gratiosa tadpoles rapidly exceeded Ambystoma talpoideum larval capture size, while Anax junius nymphs could capture slightly larger tadpoles | Does not imply ontogenetic reversal of direction | Caldwell et al. 1980, https://doi.org/10.1007/BF00346253 |
| Direct amphibian larval predation | Hynobius retardatus larvae prey on Rana pirica tadpoles | Predator morph and prey defense are inducible | Kishida et al. 2009, https://doi.org/10.1890/08-0238.1 |
| Tritrophic indirect interaction | Risk cues from Aeshna nigroflava altered Hynobius retardatus predator behavior/morphology, reducing predation on Rana pirica tadpoles | Dragonflies can be direct enemies yet indirectly relieve salamander pressure; net effect unknown | Kishida et al. 2009, https://doi.org/10.1890/08-0238.1 |
| Tadpole-to-salamander egg predation | Wood frog (Rana/Lithobates sylvatica) tadpoles ate Ambystoma maculatum embryos; egg predation depends on schooling tadpole density | Later direct reversal by *this same species pair* is not established by these sources | Burley et al. 2006, https://doi.org/10.1007/s00442-006-0398-z |
| Conditional positive effect of predation | Partial consumption/thinning of Ambystoma maculatum egg-jelly layers by wood frog tadpoles improved hatching under some tested conditions | Not evidence that egg predation generally benefits salamanders | Ecology and Evolution 2023, https://pubmed.ncbi.nlm.nih.gov/37614696/ |
| Habitat structure changes encounter process | Leaf-litter refuge changed dragonfly-nymph:tadpole functional-response shape from type II toward type III under sufficient cover | Refuge benefit is predator-, prey- and structure-specific | Hossie & Murray 2010, https://doi.org/10.1007/s00442-010-1568-6 |
| Predator-specific larval plasticity | Rana pirica tadpoles deploy different body/tail defenses to salamander vs dragonfly predators | Phenotypic defense is not direct field predation flux | Kishida & Nishimura 2006, https://doi.org/10.1111/j.1365-2656.2006.01091.x |

## 3. The central distinction: role reversal vs predation dominance

**Role reversal** is evidence for two directed feeding edges between the *same taxon pair* under different stages, e.g. Anax nymph → Litoria tadpole and Litoria postmetamorph → Anax emerging individual. Cross-species analogies (e.g. salamander species A consuming frog B, frog C consuming salamander D) are **not** a same-pair reversal.

**Dominance reversal** is stronger. It requires that both trophic directions be measured on comparable pond × time × area exposure scales with known life-stage availability, effort and detectability. An observed pair of opposite arrows alone does not identify which arrow dominates population mortality, energy flow or per-individual hazard.

Let m(A_stage → B_stage | wetland, time, H, V) be observed-attack-conditioned kill probability or predation rate. Estimate directed predation flux for each stage combination from **measured predator/prey availability, encounter exposure and stage-specific kill rate**, not from literature edge existence. For each wetland-day, estimate F(frog → odonate) and F(odonate → frog) on the same event-count scale and report their posterior difference Δ = F(frog → odonate) − F(odonate → frog), with uncertainty. Test whether Δ changes sign through phenological windows. Report per-prey hazard and biomass flux separately (their dominance rankings need not agree). Structural zeros caused by absent life stages are biologically different from failed detections.

## 4. Four prospective questions and refutable predictions

**Q1 — The chorus-to-nursery link.** Does taxon × site strong adult calling during a rainfall window forecast that same taxon's later egg/tadpole incidence or metamorph recruitment once hydroperiod, vegetation, fish/predator presence, seasonal phenology, observation effort and historical sites are represented? Alternative: calling remains predictive only of mating display, with no larval recruitment relationship.

**Q2 — The ontogenetic switching surface.** Do size/gape ratio, stage overlap and hydroperiod predict a directed edge's existence and strength better than species identity and broad wetland class alone? Falsification: stage × size terms add no held-out predictive value.

**Q3 — Two-sided vegetation mediation.** Distinguish submerged cover/leaf litter (potential tadpole refuge) from emergent stems (odonate emergence substrate and terrestrial frog hunting interface). Test separate stage × vegetation interactions rather than assuming 'more vegetation = less predation'. Falsification: effects are indistinguishable after hydrology, species identity and predator densities are controlled.

**Q4 — Indirect network effects.** Test whether dragonfly presence reduces salamander predation on tadpoles through behavior and induced morphs, even while direct dragonfly attacks remain possible. Falsification: no mediator shift or no survival difference in controlled comparisons. Distinguish predator cues from physical consumption.

## 5. New prospective data, with necessary grain

| Unit | Required measurements |
|---|---|
| wetland × census time | verified wetland_id/geometry; UTC/local time; sample effort; water-level history; depth; inundated area; hydroperiod; water/air temperature; fish; vegetation as submerged cover, litter cover, emergent stem density, canopy, vegetation type |
| taxon × stage × wetland × census | taxon authority and synonym, stage (egg/tadpole/Gosner bin/metamorph/juvenile/adult, salamander egg/larva/juvenile/adult, Odonata nymph instar/emergence/adult), size/gape, abundance and its detection effort/uncertainty |
| frog calling × site × night | CallingIndex or calibrated recorder detections, observer, sampling time and detection covariates, strictly prior call history |
| directed interaction event | predator taxon/stage; prey taxon/stage; successful kill vs attempted strike vs risk cue vs egg grazing; encounter duration, counts, observation protocol and video/experiment provenance |
| cohort × stage transition | egg survival, hatch date, larval survival/size, metamorph output; link to preceding adults only when offspring provenance warrants it |

**Sampling:** independent replicated ponds, within-season repeat visits covering frog oviposition → tadpole growth → odonate emergence and salamander development, plus night frog acoustics. Direct aquatic surveys/videos and emergence-stem surveys are needed; optional ethical mesocosms permit attack-rate discrimination. Power/sample-size must be determined by simulations and pilot detection, not guessed from NAAMP's many calling records.

## 6. Analysis order and separation from the locked RC6

1. Run **response-blind** geography, habitat and taxonomic/stage quality control. Never treat GBIF/iNaturalist same-pond records as measured predation, and never silently convert non-detections to biological zeros.
2. Replicate the locked [local-hydrology M0/M1/M2 comparison](../revision/PROSPECTIVE_LOCAL_HYDROLOGY_DISCRIMINATION_SPEC_V0_2.md) for the independently monitored frog chorus; compare broad weather, direct local hydrology, and taxon-night state × local filter.
3. Fit stage-resolved **direct** attack and recruitment models with wetland/site/year partial pooling, survey effort and imperfect detection. Compare additive size/hydrology/vegetation against explicit stage × size, stage × hydroperiod and predator-stage × vegetation terms using leave-wetland-out and leave-year-out evaluation.
4. Estimate reciprocal-edge presence first; report net stage-dependent flux only when both direction-specific denominators exist. Use a prespecified posterior sign-switch criterion and simultaneous bootstrap/credible bands over phenological windows. A mere pair of observed kills on opposite sides is insufficient.
5. Test mediator pathways (odonate risk cue → salamander activity/attack morph → frog tadpole survival) only with exposure-appropriate data; use intervention/mesocosm contrasts for causal interpretations. Compare with a shared-habitat explanation and negative controls.

## 7. Data discovery verdict

- [NEON aquatic organisms](https://www.neonscience.org/data-collection/aquatic-organisms) provide aquatic macroinvertebrates, macrophytes and hydrology at streams, lakes and rivers. **Not** a plug-in pond-wide frog developmental-stage and reciprocal predation dataset, and sampling may be unsuitable for ephemeral breeding ponds.
- [EPA National Wetland Condition Assessment](https://www.epa.gov/national-aquatic-resource-surveys/nwca) provides vegetation and wetland stress metrics, but does **not** thereby supply simultaneous frog–salamander–odonate trophic events at NAAMP sites.
- [Mendeley 2023 reversal observations](https://data.mendeley.com/datasets/9swstxknpz/1) give an independent occurrence benchmark, **not** a demographic rate or field-validated NAAMP linkage.
- [Dryad 2025 size-structured salamander mesocosm data](https://datadryad.org/dataset/doi%3A10.5061/dryad.6q573n68k) can benchmark a *different* salamander-mediated trophic pathway but is not new frogcs direct evidence or a field-generalizable stage-switch estimate.

## 8. Claim rules

- Existing acoustic multi-site excess = **frogcs result**, not a trophic effect.
- Identified predator/prey reversals, egg-eating and refuge responses = **external published evidence**, not NAAMP outcomes.
- Vegetation-mediated sign switch, stage-dependent net flux reversal, chorus-to-juvenile predictive linkage = **new hypotheses** until measured.
- WFTS is not being pursued and RC6 results are not reopened by this research track. No independent replication or actual new estimates are claimed.
