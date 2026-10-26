# PEM抽水湿地 × カエル繁殖地点履歴 × 三者発生段階ネットワーク：追加検証の実測・数理報告

Date: 2026-10-25. `frogcs` independent research branch. Frozen JAE RC6 `main` has not been changed. **Separate data types and do not pool effect sizes or treat simulated toy draws as field replicate sites.**

## 1. Empirical milestone: official GBIF point × actual USFWS NWI PEM polygons

[Results JSON](nwi_gbif_stage_point_pilot/observed_results.json) | [real source-georeferenced code](../scripts/gbif_us_nwi_stage_point_pem_audit.py) | [CI source verification](https://github.com/zuizui0223/frogcs/actions/runs/40205269009) | [pre-outcome plan](../NWI_GBIF_FOCAL_STAGE_PEM_GEO_QA_SPEC_2026-10-25.md).

Five source-vetted US species with exact accepted GBIF keys: `Anax junius` (Odonata), `Taricha torosa` and `Ambystoma maculatum` (Caudata), `Anaxyrus boreas` and `Pseudacris regilla` (Anura), each adult versus explicitly labelled immature. Source GBIF 2010–2025 georeferenced records (with explicit uncertainty <=100 m), head/middle/tail window first-five sample; public official NWI feature layer 0 point intersections, code table layer 1.

- **110** precisely georeferenced GBIF sightings were accepted from the 10 stage strata (not a random survey), **110/110** NWI point queries succeeded.
- **29/110** were inside any officially **mapped NWI wetland polygon**, but **only five/110** inside a `PEM` polygon. Those five comprised **PEM1A ×1, PEM1C ×3, PEM1Fm ×1**. *PEM1Fm* has extra Cowardin modifier; it is not the same exact code string as PEM1F, do not silently overwrite it.
- Source stage pairs each had at most 5–15 coordinates; **four** adult points and **one** larval point were identified inside mapped PEM in the sample. This is data-access feasibility, **not evidence that adults prefer PEM or larvae avoid it**. No NPS/NAAMP acoustic SiteID was attached.
- Explicitly missing coordinate uncertainty removed many observations; nonrandom GBIF source sorted offsets, preservation/citizen science, and NWI non-mapped polygons prohibit sample prevalence or habitat preference inference.
- Source geography guard: a point not in NWI polygon may be outside mapped extents or in an unmapped ephemeral waterbody; not `wetland absent` or `PEM avoidance`. Precise GBIF coordinates may reflect human collector position beside water rather than organism life-stage microhabitat.

### Immediate bottleneck for a real NWI × acoustic hypothesis

The public NPS GLKN 2016–2023 species-recording CSV has `SiteLocation` identifiers and `Hydroperiod` (Ephemeral, Semi-permanent, Permanent) but **no officially verified recorder latitude/longitude or NWI 1:1 wetland polygon IDs**. The NAAMP 12,064-coordinate source has a known positive U.S. longitude and geographic geometry outliers. Neither broad NPS Hydroperiod nor the 1° EarthEnv regularly flooded vegetation raster may be renamed as NWI PEM. A source-verified point crosswalk from authoritative station coordinates is required; never use park centroids or post-outcome spot corrections.

## 2. Empirical chorus-history × local permanence result (NPS, different outcome)

[Actual NPS code](../scripts/nps_hydroperiod_strict_history.py) | [NPS 1,815-row effect JSON](nps_hydroperiod_history/observed_results.json) | [successful CI](https://github.com/zuizui0223/frogcs/actions/runs/40203501528).

The adjustment model compares past same-species CI≥2 at exactly the same station with subsequent-year CI≥2 in fixed `park×species×year` strata, with recording effort, earlier other-species calling and history. *Post-hoc moderator of the earlier NPS main result.*

| Broad **NPS Hydroperiod**, NOT NWI PEM | Past-strong-site coefficient, linear-probability scale | 95% park×taxon trajectory cluster-bootstrap |
|---|---:|---|
| Ephemeral | +0.3523 | [+0.2516,+0.4417] |
| Semi-permanent | +0.5022 | [+0.3961,+0.6028] |
| Permanent | +0.4950 | [+0.4112,+0.5676] |
| Semi−Ephemeral | +0.1500 | [+0.0436,+0.2633] |
| Permanent−Ephemeral | +0.1428 | [+0.0450,+0.2426] |

A strict **within-hydroperiod × species×park×year** contrast is informative for Semi-permanent (212 rows/53 strata; adjusted β=+0.465) and Permanent (339 rows/69 strata; β=+0.455), but **not estimable for Ephemeral** due to sparse within-stratum history variation. Hence the ephemeral +0.352 estimate relies on the *pooled class-interaction model* and cannot be promoted to within-ephemeral independent corroboration. This does not explain why the same places are selected, because persistent taxon×site microhabitat could underlie past calling and the outcome.

Frogcs locked RC6: NAAMP +0.1511 strictly prior physical-site historical targeting and +0.2969 multi-site configuration residual after prior use, rainfall response, dry persistence and activation magnitude. **NPS differs in geographic sample, annual maximum CI, and conditional estimand; do not pool β coefficients.**

## 3. Completed PEM1A/C/F simulated three-guild developmental-network ablation

[Source-defined switch protocol](../PEM_TRIAD_STAGE_NETWORK_EDGE_ABLATION_SPEC_2026-10-25.md) | [reproducible ablation code](../scripts/pem_stage_edge_knockout_test.py) | [CI](https://github.com/zuizui0223/frogcs/actions/runs/40205567800) | [machine-readable output](pem_stage_edge_ablations/synthetic_results.json).

**432 models total**: 3 hypothetical PEM water durations × 3 salamander phases × 3 odonate phases × 2 refuge strengths × 2 odonate-salamander cue strengths × four network toggles, each under 32 identical **invented** parameter draws. Same frog egg-pulse width (=0.05 annual cycle). Tested invasion-when-rare of each missing species into resident two-species dynamics (more informative than simple all-present presence, but **still within a toy map**, not proof of real coexistence).

Knockouts on 108 matched environmental/stage settings:
- **Remove D risk suppression of S foraging, keep D→S direct effects**: all-guild invadability decreased in **29/108**, unchanged **79/108**, never improved under chosen parameters; median effect zero. **But whether phase-shifting predators was advantageous did not change:** 86/96 nonzero relative D/S phase shifts better than synchronized baseline, 10 ties, zero worse *both with cue and without*. Hence the toy's asynchrony advantage does **not require** the D⊣S⊣F pathway despite its beneficial tadpole-hazard effect in some conditions.
- **Remove frog juvenile/adult→emerging dragonfly reverse feeding**: all-guild invadability improves in **56/108**, decreases in **7/108**, ties 45/108. This reciprocal trophic edge can depress three-way invadability under the chosen model. It is not a universal rescue/stabilizing interaction.
- **Remove nymph dragonfly→frog tadpole direct feeding**: invadability improves in **48/108**, decreases in 28/108, ties 32/108. Removing a trophic edge changes consumer food benefit as well as prey kill pressure, so its network effect is not simply “fewer deaths means higher coexistence”.
- **Phase shifts still help** in the majority/all chosen settings in every knockout; the toy is structurally predisposed to asynchrony under fixed parameter ranges and aquatic stage kernels. This is an **explicit limitation**, not a universal ecological conclusion. A genuine hypothesis test needs observed vital-rate/trait parameters and a null that permits synchrony and asynchrony both to win.

**Counterexample to “explosive breeding is always advantageous”**: previous strict rare-invader synthetic width comparison showed no invented aggregation cost → narrow frog cohort better in 108/108 contexts, but adding a *hypothetical* narrow-pulse reproductive/aggregation cost of 0.3 caused diffuse reproduction to outperform narrow in 108/108 contexts. Thus simple results are strongly **assumption sensitive**, not field support for a selected breeding strategy.

## 4. The ecological mechanism worth preserving

Three NON-equivalent synchronies must remain separate:

1. **Within-frog cohort synchrony**: a brief reproductive pulse can reduce asynchronous older-conspecific tadpole predation on later hatchlings in some frogs, experimentally documented in wood frogs (Petranka & Thomas 1995; DOI [10.1016/0003-3472(95)80133-2](https://doi.org/10.1016/0003-3472(95)80133-2)). This does **not** mean synchronized frogs are safe from odonates/salamanders.
2. **Between species/stage synchrony**: D nymph×F tadpole and S larva×F tadpole may raise attack exposure if the predator is large/active; D nymph×S larva may indirectly release frog tadpoles from S attack by risk-mediated behavior (Kishida et al. 2009, DOI [10.1890/08-0238.1](https://doi.org/10.1890/08-0238.1)). Calendar mismatch is not monotonically high-risk — large mismatch can remove encounters.
3. **Opposite trophic window**: a different, Australian frog-odonate species pair shows D nymph eats F tadpole, while F postmetamorph/juvenile consumes D during plant-stem emergence (Beranek et al. 2023, DOI [10.1002/ecy.4108](https://doi.org/10.1002/ecy.4108)); this can make aquatic and emergent plant stem habitat play opposite roles in time, but the network’s *net* demographic sign remains unmeasured.

PEM emergent architecture must split **hydroperiod**, **above-water stable stems** (dragonfly emergence, terrestrial vulnerability, frog vocalising perches) and **submerged shelter** (tadpole/predator contact). No NWI code alone measures these live traits. Note the genus/systems mismatch: 2009 Japan and 2023 Australia are not a single observed naturally co-occurring trio.

## 5. Strict next ecological data gate

1. **Authoritative NPS recorder points or independently cleaned NAAMP SiteID coordinates → official NWI PEM1A/C/F polygon mapping**, capture source image dates and wetland overlap uncertainty, then re-test historical species×site acoustic effects out of site/year. NPS dataset does not currently provide station GPS; GBIF individual point overlay doesn't solve that gap.
2. **Same wetland, same time** acoustic frog CI → eggs → tadpole size cohorts → morph/behavior and actual D/S larval abundance/size/gape, direct attacks, water-level dynamics, **submerged vs emergent stem geometry**, and odonate emergence. Compare actual environmental filtering and interaction multipliers vs null.
3. To establish true three-guild coexistence, estimate population vital rates and rare-invader growth of stage-structured species under competing phase relations, replicated across PEM hydrologic classes; do not treat different GloBI/GBIF country/grid occurrence data as these measurements.
4. Original NAAMP JAE `main` stays frozen. A mechanistic claim about historical use cannot simply be appended to a paper whose required environmental/biotic variables were unobserved.
