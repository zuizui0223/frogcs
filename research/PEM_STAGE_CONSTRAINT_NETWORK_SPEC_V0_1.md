# PEM（Palustrine Emergent Wetland）を介したカエル・サンショウウオ・ヤゴ制衡ネットワーク v0.1

Date: 2026-10-25. **Prospective extension**, not an observed RC6 mechanism. JAE RC6 `main` unchanged. PEM here means **Cowardin/NWI Palustrine Emergent Wetland**, NOT Phylogenetic Eigenvector Maps (also PEM) or spatial MEM.

## 1. Explicit correction: what PEM is, and what frogcs has already established

**PEM** = palustrine freshwater herbaceous emergent marsh/wet meadow ([USFWS legend](https://www.fws.gov/node/268025), [NWI code guide](https://www.fws.gov/sites/default/files/documents/A-Guide-to-Understanding-National-Wetlands-Inventory-Mapping-Codes.pdf)). Crossed with hydroperiod and persistence subclass:
- **PEM1A** = persistent erect emergents, temporarily flooded.
- **PEM1C** = persistent erect emergents, seasonally flooded.
- **PEM1F** = persistent erect emergents, semipermanently flooded.
- **PEM2** = nonpersistent emergent vegetation (subclass, with hydrologic modifier).
All are *mapped habitat classes*, not event-by-event water-level measurements, direct stem counts, experimentally manipulated controls, or claims that fish/odonate/salamanders always occur/are absent. *PEM1 vs PEM2* may provide a direct static structural persistence contrast in future fieldwork.

**What actually exists in repo**: FROGCS NAAMP 4,236 wetter/drier pairs, +0.1511 strict species×physical SiteID strong-history targeting, spatial concentration observed 1.6503 vs model 1.3535 with **+0.2969 unexplained residual (P=.000999)** despite prior site history, rainfall response, dry-state persistence and activation magnitude. NPS independent 2016–2023 annual acoustics yields adjusted +0.4642 past same-species strong site selectivity after broad `Hydroperiod`/generic-other-species-night-hotness/record-effort control. **Neither NAAMP nor NPS directly classified these station locations as NWI PEM1A/C/F**; prior site's true pond polygon and event water hydroperiod were not audited. Historical EarthEnv 1° flooded-vegetation background showed NO consistent boost in matching documented predator-prey reporting beyond alternative prey (32 joint-sampled stage links median high-minus-near-zero −0.0281). Treat NWI PEM, NPS broad hydroperiod, EarthEnv class 8 and actual emerged Typha stems as **different covariates**.

The prior **JAE paper's scientific focus** remains 3 observational questions: rainfall gate into strong CI, multi-site selective configuration, recurrence at historical species-specific physical stops. A PEM/trophic interpretation is a hypothesis for another programme, not a retcon of established RC6 causal results.

## 2. Three different kinds of "mismatch": do not collapse them

1. **Within-frog cohort age mismatch**: late frog eggs/hatchlings face older, larger *conspecific* tadpoles. This effect is **experimentally supported** in synchronously breeding wood frogs: Petranka & Thomas (1995), *Animal Behaviour* 50:731–739, DOI [10.1016/0003-3472(95)80133-2](https://doi.org/10.1016/0003-3472(95)80133-2). Synchronized early cohorts avoided cannibalism; late eggs/hatchlings were consumed by larger conspecific tadpoles. This supports *frog within-species reproductive-pulse synchrony*, **not** that frogs collectively synchronize to avoid salamanders and dragonflies.
2. **Predator–prey relative arrival / size mismatch**: tadpoles delayed into larger salamander larvae or established odonate larvae can suffer elevated predation; **not** the same as simply nonoverlapping phenology. Rudolf (2022) [DOI 10.1002/ecy.3704](https://doi.org/10.1002/ecy.3704) manipulated *temperature × nutrients × relative phenology* in salamander–bronze frog and odonate–leopard frog systems; prey arriving late increased predation under tested conditions. Body/gape limits can produce predator-stage windows in seasonal hydroperiod wetlands.
3. **Predator-specific induced defence mismatch**: `Rana pirica` tadpoles require different phenotypes for a biting odonate vs swallowing `Hynobius retardatus` larvae; mismatched morphs survive less than the appropriately induced one in experiments (Kishida & Nishimura 2005/2006, [DOI 10.1111/j.1365-2656.2006.01091.x](https://doi.org/10.1111/j.1365-2656.2006.01091.x)). The correct defence can change sequentially within the same pond. This is separate from the calendar phase.

**Careful inequality:** overlap of predator attack-capable stage with vulnerable prey *can increase* encounter exposure; a mismatch in predator/defence phenotype *can increase* vulnerability; but a **large temporal displacement** can also protect larvae by eliminating overlap. Consequently, `more developmental synchrony → more coexistence` and `more mismatch → more predation` are not universal claims.

## 3. Directed stage-specific three-guild interaction and emergent vegetation function

In the **Hokkaido** `Aeshna nigroflava` (nymph) / `Hynobius retardatus` (larva) / `Rana pirica` (tadpole) system:
- **D nymph → F tadpole** direct biting predation risk (− for frog).
- **S larva → F tadpole** swallowing predation risk (− for frog), strongly gape-size/defence morphology dependent.
- **D nymph → S larva** predation risk/trait cue reduces salamander activity and attack morph (− for S predation intensity). Combined `D nymph ⊣ S larva ⊣ F tadpole` gives **positive trait-mediated indirect** effects on frog tadpoles **even if D also directly harms tadpoles**. Experimental [Kishida et al. 2009](https://doi.org/10.1890/08-0238.1). The direct + indirect net sign is site/age/density-dependent.

A **different Australian species-pair** shows a genuine qualitative reversed feeding direction: `Anax papuensis` nymph → `Litoria aurea` tadpole, whereas postmetamorphic/juvenile `L. aurea` consumed vulnerable emerging `Anax papuensis`, often 30–60 cm up *Typha orientalis* or *Bolboschoenus fluviatilis* emergent stems ([Beranek et al. 2023](https://doi.org/10.1002/ecy.4108)). **These Australian reversed directions must not be attributed to the Hokkaido three-guild species**. Net mortality/energy flow reversal is still unknown.

### Stage- and layer-specific PEM effects

| Layer | Variable | Stage-specific interaction |
|---|---|---|
| **Annual inundation window** | PEM1A/C/F code plus survey-date water depth, rain-triggered wet/dry transition and drying speed | F egg survival vs premature drying; long wet phase can retain D/S larval enemies, but not automatically |
| **Persisting waterline stems** | PEM1 persistent vs PEM2 nonpersistent, stem height, species, density and emergence-ready stems | dragonfly nymph climbs to emerge; frog juveniles can hunt vulnerable dragonfly emergence |
| **Submerged shelter** | fine leaf and stem/refuge complexity, litter, root density and inundated fraction | can reduce effective D/S attacks on tadpoles or aggregate ambush predators; sign not universal |
| **Adult frog calling** | acoustic recorder adult chorus CI, strict previous site histories and synchronized conspecific calling, individual density | rain state, reproductive site selection, mate cue; may attract heterospecific eavesdroppers; not automatically true breeding output |
| **Tadpole developmental phenotype** | body depth, tail depth, escape behaviour, predator-cue detection and induction lags | wrong induced defence (relative to active predator identity) can increase fatal attacks even when season unchanged |

## 4. Four competing hypotheses and tests

- **H-PEM historical site filter:** strongly used species×acoustic stops are recurrent because they are embedded in PEM1 vegetation/wetland architecture and repeated inundation windows; `strictly prior site CI × PEM class` interaction and `PEM1/PEM2 × taxon`. Test versus PUB/PAB open pond, PSS/PFO woody wetlands, with effort/season controlled. Does direct historical site targeting attenuate after wetland PEM × dynamic hydroperiod and verified site→pond join? This is **not yet fitted**: NAAMP site coordinate source has known transcription errors.
- **H-FROG pulse/cohort match:** a concentrated frog chorus predicts *actual eggs* deposited in a short window; late-laid offspring have greater **within-species** size-asymmetric cannibalism or predator-specific vulnerability; mass reproduction may dilute/saturate predators but also attract them. Experimentally contrast synchrony after matching total eggs, water level, predator density and stage availability. Frog chorus only an acoustic proxy.
- **H-D-S three-way constraint:** simultaneous D and S active larvae can reduce direct salamander attacks via D risk cues while D nymphs directly kill F tadpoles; **net D effect can be + or − depending on densities and refuge**. Compare additive pairwise `D→F+S→F` to `D→F+S→F+D⊣S`, with and without PEM structural refuge. Predator cue effect not an inference of competition.
- **H-ontogenetic reversal and coexistence:** F juvenile/adult may consume vulnerable emerging D even while D nymph eats F tadpoles at an earlier stage. Test windows `F tadpole × D nymph` and `F postmetamorph × D emerge` independently. Increased overlap with either predator stage may harm its corresponding prey; *phase offsets can reduce one hazard yet intensify the other*. Coexistence needs repeated recruitment and **invasion when rare**, not two contemporaneous GBIF species observations.

## 5. Minimal scientific model and evidence boundary

Let `f(t),s(t),d(t)` be frog vulnerable tadpole, salamander predatory larva, odonate nymph activity fractions (0–1). Let `W(t)` be actual inundation, `V_uw(t)` underwater shelter and `V_stem(t)` stems available for emergence. A stylized frog per-capita hazard can be decomposed:

```text
lambda_F(t) =  a_DF * D_nymph(t) * W(t) * (1-r_D*V_uw(t)) / (1+h*F_vuln(t))
             + a_SF * S_larva(t) * W(t) * (1-r_S*V_uw(t)) / (1+q*D_nymph(t))
             + a_C * older_frog_cohort_exposure(t) 
```

where `q` is behavioural risk suppression from D on S, `h` predator satiation on a concentrated prey cohort, and `a_C` frog-size mismatch/cannibalism. A separate **reverse** edge `F_postmetamorph(t) → D_emerging(t)` is gated by stem availability and species' natural-history evidence.

- All coefficients are **synthetic until measured**, and positive effects of D on F arise by reducing the **S** term, not magically turning a predator into a mutualist. Stage variables cannot be substituted by total species presence.
- Initial direction of increasing D density at fixed stage exposure:
  `d(lambda_F)/dD = a_DF*(1-r_D*V_uw)/(1+h*F_vuln) - a_SF*S*q*(1-r_S*V_uw)/(1+q*D)^2`.
  If the second term exceeds the first, adding odonates can **locally reduce frog predation hazard**, despite direct attacks; otherwise D raises hazard. This describes a *model sign constraint*, not an observed full population response.
- PEM hydrology can alter all three life stages through recruitment/phenological constraints. One should compare **positive direct D→F vs positive indirect D→S→F** and inverse adult frog→D emergence edges under PEM1A/C/F to identify network mechanisms.
- Before claiming stable co-existence, assess the continuous or annual demographic system's **invasion growth of each species when rare in a resident two-species assembly**, and outcome stability across initial conditions. Simple equal co-occurrence counts, or a toy persistence fraction, do not constitute mutual invasibility.

### Fixed exploratory synthetic QA

An illustrative annual-model parameter ensemble (fixed random seed, no empirical fit) should compare PEM1A/C/F windows; vegetation shelter weak/strong; conspecific frog breeding concentrated versus dispersed; D/S seasonal relative offset; D risk suppression weak/strong. The purpose is to demonstrate **counterexamples** to monotonic "more synchrony = more three-species coexistence", and constrain field parameters required to distinguish mechanisms. Mark every output `SYNTHETIC_NOT_EMPIRICAL`. Do not present simulation parameter proportions as actual wetland data.

## 6. Next genuine empirical test

Independent, verified 1:1 matching **NWI PEM wetland polygons ↔ corrected site coordinates ↔ site/year-call histories**, plus measured same-date water depth/hydroperiod and larval D/S/F stage indices. NWI mapping codes are the **hypothesized stable spatial template**, not actual sensor water-level, plant abundance or current tadpole refuge. NAAMP geometry must be fixed blind to call outcomes. Strong historical calling in PEM1C/F vs PEM1A and ephemeral PUB/PAB should be tested with true habitat and predatory-stage covariates, not retrospective post-hoc selection of the best PEM code.

Competing field outcomes: (i) PEM/local hydrology alone removes prior-site targeting and spatial residual → **environmental explanation**; (ii) adding observed D/S stages, conspecific cohorts and their interactions adds out-of-wetland/year configuration prediction → **biotic network mechanism**; (iii) residual remains → uncertain social/demographic or unmeasured environmental cause. Never assert that synchronized chorus itself was adaptive from observational NAAMP matched contrasts alone.
