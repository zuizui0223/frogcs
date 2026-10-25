# マクロ生態学研究：生活史段階が作る潜在的な捕食・被食の時間窓
Date: 2026-10-25. Main branch JAE RC6 untouched. **No new literature-survey task**; original GBIF macro data collection.

## Biological question
At continental spatial scales, do adult reproduction and aquatic larval phases of frogs, salamanders and odonates align differently across latitudinal regions, potentially changing the *opportunity* for (1) wood-frog-like tadpoles to meet salamander eggs, (2) salamander larvae to meet frog larvae, and (3) odonate larvae to encounter frog larvae? This is a new macro **phenology** study, not a direct predator-prey interaction dataset. Species identities and pond microhabitats differ; never call co-temporal regional occurrence a recorded predation event, a pond-level overlap or a causal interaction.

## Original source and strata
GBIF public Occurrence API live taxon orders `Anura=952, Caudata=953, Odonata=789` independently verified from species matching, 2015–2025, `hasCoordinate=true`, distinct nested 5–10° latitude strips:
- United States 25–30, 30–35, 35–40, 40–45, 45–50°N;
- Canada 45–50, 50–55, 55–60°N;
- France 40–50°N; Germany 45–55°N; UK 50–60°N;
- Japan 30–40, 40–45°N;
- Australia −40 to −30, −30 to −20° latitude.
Country selection is intended to span temperate and subtropical phenology, but is **not a random global sample** and must not be called global prevalence.

Query real monthly facet counts by taxonomic order and verbatim GBIF `lifeStage` labels:
`frog_egg=Anura/Egg`; `frog_larva=Anura/Larva + Anura/Tadpole`;
`salamander_egg=Caudata/Egg`; `salamander_larva=Caudata/Larva`;
`odonate_larva=Odonata/Larva + Odonata/Nymph`;
`odonate_adult=Odonata/Adult + Odonata/Imago`.
Original stage label coding is heterogeneous: keep both source labels in auditable separate queries; `Egg` may include egg masses; `Larva` broad; a salamander `Tadpole` is excluded as biologically ambiguous. Invalid labels such as frog `Chick` excluded. No inferred stage transitions in the individual records.

For each region also query all records in each taxonomic order by month as a **seasonal observation-effort proxy**, not a true survey probability. All raw response URL and SHA256, stage monthly counts, top `datasetKey`, `basisOfRecord` facets, exact coordinate/time filters retained. Exclude `datasetKey` source effects from inferential claims unless actually checked.

## Descriptive macro stage-window metrics, fixed before outcomes
For a region and guild stage `g`, raw monthly p[m] = stage records m / sum_m stage records. Effort-adjusted alternative p_adj[m] ∝ (stageRecords[m]+0.5)/(allOrderRecords[m]+1), renormalized across months. Report both. This accounts some observation seasonality **only within orders**, not reporting effort, uneven datasets or non-detection.

The three directed trophic-*opportunity* comparisons are:
 A: frog larva vs salamander egg;
 B: salamander larva vs frog larva;
 C: odonate larva vs frog larva.
For two positive monthly distributions `p,q`, seasonal overlap `O=sum(min(p[m],q[m]))` ∈ [0,1]. Report `O_raw`, `O_adj`, circular shifts by 0–11 months as descriptive **timing-alignment baseline**. Neither the overlap itself nor its difference among groups is a direct predation rate.
Stage coverage gate: each of the two stages ≥30 original coordinate records across study period AND ≥2 nonempty months; else `non_estimable_low_stage_coverage`, never report 0 biological overlap.
Report winter breeding and southern hemisphere circular seasonality. Do NOT infer actual female oviposition dates from incidental egg records nor live adult Odonata flight as dragonfly egg laid.

## Higher-quality subset and independent data
A high-quality analysis must condition on shared source dataset, year, and fine-scale site/event, or explicitly label region-scale timing as only an availability window. GBIF full-order records cannot prove same-pond contact. Publish stage label source dataset coverage; strong relative timing patterns may be observation-platform artifacts.

If macro source has enough actual data, next effort is **record-level stage-tagged** `taxon × grid × year × week` data, spatial grid approx 25–50km, requiring same site/observer/dataset stratification; do not treat missing stages as zero. Supplement independent NAAMP stage surveys only if their lifeStage is actually recorded (NAAMP CallingIndex is adult sound).

## Stopping & interpretation
No `Counts.csv` NAAMP, no new broad literature searching, no post-hoc grouping based on sign. If GBIF stage coverage differs so strongly that stage-window overlap cannot be robustly compared between regions or label platforms, conclude insufficient ecological comparability and prioritize a macro species-stage event dataset with consistent source effort. A new *ecological conclusion* demands robust common-source cross-stage timing, not just millions of undifferentiated GBIF observations.
