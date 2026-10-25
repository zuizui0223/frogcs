# frogcs: RC6-to-stage-legacy future integration — scientific contract v1.1

Created: 2026-10-25; integration policy revised: 2026-10-26. **PROSPECTIVE / RESEARCH-ONLY. NO NEW EMPIRICAL RESULT.**  
Authority: [RC6 README](../README.md) is locked for submission; this file owns *only the future stage–hydrology–community extension*. The former [stage reversal prospectus](ONTOGENETIC_TROPHIC_REVERSAL_PROSPECTIVE_V0_1.md), [local hydrology M0/M1/M2 proposal](../revision/PROSPECTIVE_LOCAL_HYDROLOGY_DISCRIMINATION_SPEC_V0_2.md), NPS acoustic-history contracts, GloBI stage-topology pilot, and synthetic network examples remain source-specific records; this one file is the coordinating prospective test contract.


## Integration policy: one repository, two scientific release layers

1. **Do not revise RC6**: \`frogcs/main\`, \`release/jae-multisite-rc6\`, and \`submission/jae-multisite-v6\` own the finished Journal of Animal Ecology acoustics article. Preserve its fixed NAAMP population, metrics, null models, manuscript and submission QA.
2. **New scientific development stays in frogcs**: this branch \`integration/stage-legacy-unified-2026-10-25\` owns the acoustic-to-stage bridge, hydrology alternatives, evidence schema, new scripts and all later estimates. There is no independent integration or meta-repository to update; reference external methods or data without copying another repository's scientific ownership.
3. **Keep observed evidence distinct**: locked NAAMP spatial configuration, observed NPS annual acoustic-history replication, GloBI-stage links, verified pond-stage data (future), and synthetic trophic simulations remain separate within the same source-evidence hierarchy; do not pool unlike estimands.
4. **Only after G0–G3** consider a *future combined mechanism paper* connecting RC6's acoustic pattern to measured stage and recruitment outcomes. A successful G1 proxy calibration alone cannot demonstrate predation. If G2/G3 fail, report a valid separate acoustic-history/observability or hydrological-filtering result rather than rewriting RC6.
5. **The execution entry point** is [STAGE_LEGACY_INTEGRATION_MANIFEST_V1.json](STAGE_LEGACY_INTEGRATION_MANIFEST_V1.json) and [scripts/stage_legacy_integration_gate.py](scripts/stage_legacy_integration_gate.py). Its status does not itself confer mechanistic evidence or release permission.

## One biological question

> When a wetland's past community leaves surviving aquatic life stages, how does that **latent ontogenetic legacy** constrain where, when, and which frogs call, reproduce, and recruit after changing rainfall and hydroperiod?

Do not call an acoustic correlation "predation." Define *three different endpoints*: same-year adult acoustic site selection; same-season egg/tadpole survival and stage abundance; later cohort recruitment to calling adults. Their timescales and evidentiary requirements differ.

### The one linked causal/observation system

```text
    atmospheric forcing + local hydroperiod H(i,t) + habitat V(i,t)
                     |                  |
                     v                  v
   adult calling C(s,i,t)     larval stages L(s,i,t), odonate/salamander/fish
         ^  |                        |     ^
         |  +-- breeding/eggs -------+     |
         |                                (past cohorts, survival)
         |                stage × size × predator/prey encounters
         |                                |
         +---- [later maturation lag] ----+--> egg/larva survival / metamorph output

    Y_call   <- adult activity × acoustic detection / effort
    Y_trap   <- actual larval abundance × catchability / effort
    Y_water  <- hydroperiod sensor / independently verified inundation
    Y_edge   <- recorded attack/experiment, not mere GloBI edge presence
```

Never equate NAAMP roadside stop with one pond, CallingIndex with abundance/spawning, a positive voice record with a surviving cohort, or overlap with attack events. Unobserved waterbody-to-stop mapping and detection must be treated as unresolved.

## Biological lag correction: two distinct hypotheses, not one H1

**H1A (immediate behavioural/site-selection signal, exploratory in historical NAAMP).** Previous-year calling by a long-larval-period taxon predicts a smaller spring-breeder's **current adult calling at the listening stop**, conditional on focal own-site history, hydroperiod, site and year structure, breeding phenology, weather, observer and other taxa. This predicts *acoustic avoidance or co-location*, not egg predation. Directional cross-lag asymmetry is useful predictive evidence but not identification: dynamic habitat and different detection phenologies can produce it. A reverse-lag and a negative-control taxon help diagnose shared drivers, not prove causality.

**H1B (direct mechanistic endpoint, preferred).** Independently measured overwintered large tadpoles predict the subsequent small species' *egg survival, tadpole emergence, or metamorph output* within an identified pond; a stage/size-matched predation or exclusion experiment isolates the feeding path from competition and habitat. Focal precedent: *Lithobates clamitans* tadpoles eat *L. sylvaticus* eggs (Petranka & Kennedy 1999, Oecologia 120:621–631). This documented pair cannot be generalized by simply grouping all small frogs/toads, or all large tadpoles, together.

**H1C (delayed cohort consequence).** Failed eggs or reduced metamorph recruitment in year t can affect reproductive adult calling only after the target species' age-at-first-breeding lag, often 1–3+ years, and with dispersal/survival uncertainty. A same-spring adult chorus cannot be a direct consequence of eggs eaten after that chorus. Species-, sex- and latitude-dependent maturity distributions are required before setting lags.

**Primary inference hierarchy:** first calibrate `P(L_predator(i,t) > 0 | C_predator(i,t-1), H, site, region, season)` in a genuinely co-located multi-year acoustic + larval panel. If that mapping is not predictive out of pond/year, retain previous calling as an *acoustic-history covariate* and **do not** rename it "hidden predator pressure." Then assess H1B with direct larval measures; H1A remains an exploratory NAAMP prediction only.

## All proposed tests inside one comparison ladder

| Stage | Competing mechanism/model | Target and valid inference |
|---|---|---|
| **M0** | Wetland/site persistence, focal own-calling history, species/region/year/season, observer/effort, weather; **no cross-taxon lag** | Baseline adult CallingIndex or stage-specific baseline; acoustic association only |
| **M1** | M0 + strictly preceding long-larval-period taxon calling history, reverse history, biologically defined early-breeder interaction; sensitivity for common-site other-taxon history | Extra held-out calling prediction attributable to a **proxy**, not mechanistic predation |
| **M2** | M1 + **observed** wetland water level / verified dry-reflood state + **observed** tadpole stages, size, egg success, fish/odonate/salamander and habitat cover; interactions with stage/season/drying | Discriminate hydrological filtering, stage encounters, behavioural avoidance and delayed recruitment; causal claim requires exposure or intervention identification |

This M0–M2 is **specific to the new ontogenetic programme**, not the locked RC6 local-hydrology M0/M1/M2 naming. Keep the two comparison families explicitly separate. For a fair test use identical eligible rows, exact outcome definitions, matched training blocks, held-out pond/year geography, and a null model preserving first-order calling magnitude. For an RC6-style configuration endpoint repeat exact-`k` conditional simulations only on new authorized data; do not compare residual differences across changed denominators.

### H2: within-season interaction is stage-specific, not necessarily weaker later

Predefine the biological stage-overlap window `egg_focal × overwintered_tadpole_predator` and size mismatch at each survey. NAAMP `RunNumber` targets geographically variable state/region breeding periods, and cannot by itself be treated as an equal-unit phenological clock. **No universal negative time trend** is assumed: egg predation may peak when eggs appear, competition later, and adult calling windows need not reflect either. Compare actual day-of-year relative to species/regional peak with temperature and length-of-season controls.

### H3: drought reset as a conditional triple contrast, not generic dry-year response

`dried_in_warm_season(t-1)` must be based on *same-pond measured hydroperiod* or independently validated sufficiently resolved imagery. ERA5-Land soil moisture (~9 km) is **meteorological drought context**, not direct pond drainage. JRC 30 m can miss small, shaded and ephemeral breeding ponds; do not assign 'all tadpoles killed' from either raster. After confirmed re-wetting, contrast (historically overwinterer-positive vs negative) × (dry-reset vs continuously wet) × (before vs after) on larval prey success, and separately on calling. Include water depth, hydroperiod, fish status, temperature and recolonization; drought also independently hurts focal prey. Assess pre-trends where possible. Same-year calls can respond to reflooding even without a predator mechanism.

### H4: spatial concentration and conditional residual

RC6 observed concentration **1.6503** vs null **1.3535**, residual **0.2969** (2,916 history-eligible comparisons; simulation P = 0.000999). The null **already includes strictly prior focal taxon × physical-site history**. Reduction of the residual after adding other-taxon history is only an increment in prediction; it is not a proportion of variation proven to be due to aquatic predators. The new null must also condition on magnitude, focal own-history, generic stop propensity and dynamic local inundation. Substantiate biologically only with co-located pond-stage measurements.

### H5: adult trophic size ratio (secondary)

Postmetamorphic bullfrogs can prey on smaller anurans; however, same-night call co-location and an adult body-size ratio cannot measure ingestion or learned avoidance. Treat adult predator–prey size/call associations as a *separate* behavioural sensitivity, controlling habitat, phenology, survey/detection time, body-size uncertainty and range overlap. Not a substitute for H1B.

## Frozen groups and source discipline

- **Prey-primary, documented interaction:** overwintering *L. clamitans* tadpole -> *L. sylvaticus* egg. Match geographic coexistence and verify the exact taxon codes/synonyms in each dataset *before looking at new outcomes*.
- **Predator/proxy extensions:** *L. catesbeianus* may be long-lived as a tadpole, but field egg-predation evidence and season/cold-region differences must be checked **per interaction**, never pooled by assumed guild.
- **Other potential spring breeders:** treefrogs, chorus frogs, toads, and cricket frogs require a prior species×stage×pair evidence table and target-specific direction. Negative association in a previous exploratory 'partner' analysis is not training-independent confirmation.
- **Negative controls:** regionally available species not expected to be exposed to the specified aquatic stage, and *lead* histories (placebo predictors). Leads can also correlate via persistence; interpret as bias screens, not definitive negative proof.
- No post-hoc sign, taxa, lag, season-window, drought threshold or stopping-rule selection may be reported as pre-registered. This entire programme follows inspection of NAAMP and other data and is **exploratory**, until a future source-blind protocol and new untouched holdout are independently locked.

## Sources, observable units, and actual readiness

| Evidence source | Measured variables / observational unit | Valid role | Status as of 2026-10-25 |
|---|---|---|---|
| **NAAMP, frogcs RC6** | 53 taxon labels; roadside 5-minute ordinal call indices; fixed stops, dates and observers | Frozen broad-scale adult acoustic discovery, cross-lag **feasibility audit only** if separately authorized; no eggs/tadpoles | **Existing/locked**; several SiteID coordinate errors; not one pond per stop |
| **NPS GLKN acoustic data** | 66 stations, seven parks, eight years; ManualCIV and broad `Hydroperiod` category; asynchronous repeated recordings | Independent focal own-history and hydroperiod association; cross-taxon acoustic proxy diagnostic if species overlap verified | Existing frogcs stage branch; no measured tadpole abundances |
| **Carroll, Saenz & Rudolf, 2023, Dryad** | Eight southeast-Texas ponds over six years; calling activity and weekly tadpole funnel traps | Co-located **call→larva proxy calibration**, stage phenology; not automatically *green frog→wood frog* and not a direct predation experiment | Public source located, DOI 10.25338/B8G92P; workbook/schema not yet independently ingested in this integration |
| **Petranka & Kennedy, 1999** | Direct field/laboratory egg predation by overwintered green-frog tadpoles on wood-frog eggs | Focal **mechanistic precedent**; not a common-pond bridge with NAAMP | Published external evidence |
| **GloBI, frogcs research** | Published interaction-edge records with variable predator/prey stage annotation | Candidate stage-edge **topology/QA**; no co-located stage abundance or feeding flux | Pilot available; non-random source sample |
| **Measured hydrology / eggs / survival** | Pond-year-season water depth, actual dry-out/refill, egg/hatch/metamorph and fish/vegetation | Essential for H1B/H3 causal discrimination | **Absent at linked NAAMP sites**; must not be invented |

Carroll is a phenology/larval-count bridge; its available data do not by themselves establish the postulated overwinterer egg-predation edge or its demographic effect. The reported '61 days' green-frog lead is not re-estimated or asserted here.

## Strict release/evidence gates

1. **G0 geometry & taxa:** externally verify aquatic-unit coordinates, stop-to-pond identity, pair overlap, source years, taxonomic harmonization, adult versus larva stage and observation effort. Fail closed on unsupported joins.
2. **G1 proxy calibration:** fit the nested M0/M1 call→larva calibration with held-out pond and year, likelihood and detection controls; report both positive/negative performance and prevalence. If incremental out-of-block calibration fails, stop describing prior calls as latent predators.
3. **G2 primary biological mechanism:** seek stage-resolved same-pond **egg/survival** endpoint with hydrology and negative controls, ideally predator-stage exclusion or additions. Otherwise state H1B/H3 remain unidentifiable.
4. **G3 recruitment and configuration:** propagate species-specific age-at-maturity distribution to future calls; evaluate spatial null after held-out magnitude/first-order adjustment; report cohort mediation only with linked cohorts.
5. **G4 external generality:** independent taxa/regions and prospective recording. WFTS stays **NOT PURSUED** unless a new explicit separate study authorizes it.

## Internal frogcs modules and their evidence ceiling

| Frogcs-owned component | Canonical local evidence/implementation | Contribution to future synthesis |
|---|---|---|
| **RC6 locked paper** | \`paper/\`, \`provenance/CURRENT_RESULTS.json\`, \`release/jae-multisite-rc6\` | Observed rain-associated chorus spatial configuration and own-site history. **Read-only**. |
| **Independent acoustic history** | \`research/scripts/nps_glkn_strict_history.py\`, \`research/results/nps_glkn_history/\` | Species-specific strong calling history beyond broad hydroperiod class; not fish/tadpole or predation. |
| **Phenology & same-waterbody proxy bridge** | Future Carroll coverage audit and stage-linked pond-year panel | Whether prior calls predict measured overwintered larva, with held-out source/pond/year evaluation. |
| **Stage interaction topology** | \`research/STAGE_INTERACTION_EVIDENCE_V0_1.csv\`, frozen GloBI/source-QC results | Hypothesized size-stage predator/prey edges, *not* simultaneous local feeding. |
| **Wetland-water and vegetation exposure** | Stage-hydrology design; future verified wetland surveys | Physical dry/reset timing, encounter conditions and competing habitat explanations. |
| **Integrated model & QA** | This contract, manifest, \`research/scripts/stage_legacy_integration_gate.py\` | Model M0/M1/M2, response-blind checks, evidence gates, and shared reporting within frogcs. |

No external portfolio management repository or physical repository merge is required. Other projects' mathematical ideas can inform implementations, but the source-linked frog ecology, integration logic, data contracts, code, and eventual manuscript remain **within frogcs**. Re-use methods with correct attribution; do not equate mathematical analogy with new frog field evidence.

## Next executable gate

Prepare a **source-blind Carroll workbook schema + coverage audit**: list observed species × pond × year × life-stage, effort and missingness, then verify whether separate prior-year stage and next-year responses actually co-occur. Only then select the primary lag, study population and endpoint. This is a coverage-first, not outcome-selection, gate. Re-use the existing NPS and GloBI source receipts within frogcs rather than copying the same datasets into new project roots.
