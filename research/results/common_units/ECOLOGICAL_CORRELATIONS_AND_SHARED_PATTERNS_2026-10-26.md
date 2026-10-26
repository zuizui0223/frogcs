# One frogcs common-unit ecological correlation and phenophase synthesis — 2026-10-26

**Classification:** real original-data observation and **post-readback exploratory correlation**, not a finished mechanistic test or independent confirmatory replication. User question: are rain-responsive multisite frog chorus localities predator/competitor-poor, close in developmental timing with other taxa, or primarily favorable wetland environments with persistent water and emergent plant refuge? All results use original source namespaced units and keep noncomparable source types distinct.

**Canonical data engine:** [unit/zero semantics](../../CANONICAL_SITE_TIME_STAGE_OBSERVATION_CONTRACT_V1.md); [raw-source crosswalk script](../../scripts/build_common_ecology_units.py), [native-stage correlation script](../../scripts/common_ecology_correlations.py); [original-data source profile](observed_profile.json); [observed correlation JSON](observed_correlations.json); [successful workflow and downloadable compressed canonical tables](https://github.com/zuizui0223/frogcs/actions/runs/40263090203).

## 1. Data consolidation actually executed

Pinned and source-authenticated source files were parsed into common `source ID × original site token × year × month × taxon × source-verified stage × assay type` without making recording stations into ponds:

| Original source domain | Source-observation rows in comparable long table | Actual physical source unit / measured state |
|---|---:|---|
| NAAMP, source standardized completed stop opportunities | **198,757** | Surveyed roadside listening stop; species-specific absence not established |
| NAAMP, positive original calling records | **310,683** | Source species code and ordinal CallingIndex of positive reports, original physical SiteID/time/DaysSinceRain when present |
| NPS GLKN 2016–2023 | **147,913** | Taxon×soundfile ManualCIV, 66 recorder stations, date/season and source broad Hydroperiod class |
| INBO Flanders 2016–2025, chorus protocol | **1,436** | Stage-labelled adult chorus survey, exact publisher site/event/date |
| INBO Flanders 2016–2025, larval protocol | **2,995** | Explicit larvae/adult/metamorph source-status including non-detections |
| Hungary 2024, 29 measured wetland sites | **3,429** | Seven frog/toad and two newt taxa by acoustic/visual/dipnet/trap visit, source water depth, visit rain, static macrophyte percent |

**Total 665,213 source-observation rows, 506,653 source-site×year×month×taxon×stage×method cells**, not 506,653 independent aquatic sites or ponds. GloBI×GBIF 1° annual-monthly stage-reporting cubes remain a *separate macro-grain linked summary*, rather than a fabricated site join to NAAMP.

**Availability limitations, observed:** NPS audio source has no actual predator-stage or water-level data. Hungary provides static site macrophyte percent but not new shoot/emergence dates and fish was recorded in only two sites. INBO’s three linked steps include explicit acoustic/larva survey time, but dynamic permanent-water-column measurements are absent from all 245 focal *Hyla* matched observations. Original NAAMP `DaysSinceRain` is populated on only a subset of standardized source observations; these unfiltered source-native rows are **not** the frozen 4,236 wetter–drier RC6 matched pairs. No pooled shared pond hydrology×fish/odonate/newt stage×egg-cohort fate panel exists.

## 2. Question: is calling concentrated where there are fewer competitors/predators?

**Source event co-reporting is NOT aquatic enemy intensity.** In the INBO same-exact-location *Hyla arborea* matched site-year panel (245 pairs, 93 sites):

- **239/245** site-years had **zero OTHER positive adult frog chorus species reported in the available prior source choir protocol**; only **6/245** had ≥1. It would be invalid to interpret this as 239 truly competitor-free ponds. Source collection focus and detection determine which frog species get recorded. The raw rho between prior other adult chorus taxon richness and subsequent focal larva detection is **−0.0762**, site-bootstrap 95% **−0.1749 to +0.0383**, but the exposure is too sparse to identify a competition-release ecological effect. **GATE: NONESTIMABLE, descriptive statistic retained only for transparency.**
- Among **189 source larval-census events** that explicitly included both *Hyla* larvae and ≥1 Caudata larvae assessment, the status pairs were **both recorded present 122**, *Hyla* absent / Caudata present 55, *Hyla* present / Caudata absent **3**, and both recorded absent **9**; source event φ **+0.2263**. Caudata larvae were recorded present in **177/189** eligible events, leaving only **12** without their recorded presence. A true local predator-exclusion or competitor-release coefficient is thus also unsupported by scarce absent exposure and unknown guild diets. Both species-stage source reports may simply select permanent, suitable, well-sampled habitats.
- Global GloBI×GBIF month stage overlap showed seasonality in **16/18** source pairs relative to arbitrary cyclic month shifts; this stage overlap was *not specific to known partner links* under stringent guild-/effort-matched alternative prey (**26/56** higher than matched alternative at ≥5 reports). It is NOT predator avoidance evidence for a real NAAMP pond.

**Decision:** present evidence does **not establish** the user hypothesis “strong acoustic sites have fewer competitors” nor the opposite trophic facilitation. Actual measured enemy richness or size-stage exposure at the source waterbody is required.

## 3. Question: are chorus and aquatic developmental stages near in time?

**Within *Hyla* (INBO)**, strictly earlier positive adult chorus was followed by a positive sampled larva stage at 132 source site-years; first positive adult call to first later larva positive report was **median 53 days, IQR 39–69 days**. The first eligible larval assessment had 149/245 positives and 96 explicit absent, and prior chorus had 212/245 positives and 33 source-documented non-calling pairs. Binary past-chorus/later-larva association **φ +0.2623**, raw conditional detection fraction difference **+0.3802**. These are survey and reporting associations, **not developmental time for an individual or a cohort survival percentage**. Earlier [held-out study](../part2_inbo_hyla_g1/REPORT.md) found a site-heldout Brier gain but an **adverse 2024–2025 future-year validation**, so stable year-transfer is not shown.

**Between co-occurring frog/newt larval stages (INBO)**: 107 original source location-years had a positive *Hyla* larva and Caudata larva report. **107/107 first positive reports fell on the very same survey date** (median difference 0 days). This is a crucial **observational schedule artifact**: larval community cohorts are sampled in the same event. It is **not** independent proof that the species hatched at the same time, were the same Gosner stage/size, were competitors, or experienced a size-matched predator window. True developmental synchrony remains unidentifiable from the once-per-period stage snapshot.

**Contemporaneous adult calls (NPS)**: 16,561 real source soundfiles (147,913 scored taxon×recording rows) had ≥5 tested taxa each; an acoustic recording with ≥2 species ManualCIV≥2 is an actual multi-taxon **co-chorus on one recording**, a different estimand from NAAMP sequential stop concentration. Among 66 independent stations, ordinal broad water permanence vs each site’s fraction of multi-strong audio files had Spearman **ρ −0.2295**, 2,000-site-bootstrap 95% interval **−0.4597 to +0.0227**. This is weak negative evidence, not a significantly demonstrated early/persistent pool rank slope, and source park/latitude, month and recording intensity vary. Contrast it with a separate NPS within-species **prior-location recurrence** coefficient stronger in semi-permanent and permanent classes: the two acoustic endpoints have different physical and temporal interpretations.

**Decision:** adult–larval *record* phase separation is observable; interspecific fine-stage synchrony and overlap with actual predator gape/size remain to be demonstrated. Same-survey date equality cannot supply a biological null test.

## 4. Question: does rain and emergent vegetation select the chorusing ponds, or act as refuge?

**Hungary 2024: exact field sites and measured cover**, 29 wetlands, 129 acoustic visits. Correlation unit = independent source *wetland*, response = fraction of its actual acoustic visits recording ≥1 frog/toad species (not CallingIndex concentration). Predeclared marginal Spearman correlation with 2,000 original-site bootstrap sensitivity:

| Actually measured source habitat | Spearman ρ | Site-bootstrap 95% interval |
|---|---:|---:|
| Site water depth | +0.2057 | −0.1537 to +0.5294 |
| Emergent vegetation **percent cover** | **+0.0637** | **−0.3466 to +0.4656** |
| Submerged vegetation percent cover | +0.2202 | −0.2228 to +0.6170 |
| Mean source precipitation value across sampled visits | −0.1833 | −0.5303 to +0.2206 |

A postreadback **partial rank correlation** between emergent cover and calling-positive fraction after controlling source water depth, mean visited rain, number of audio visits and wetland class was **+0.1816** (29 original wetlands). This unstable descriptive partial association does not imply an independent refuge effect. With only **19 sites** having a positive call, static emergent percent vs **first positively recorded call survey day** correlated **−0.1843**, site bootstrap 95% **−0.6734 to +0.3443**; survey time and true initial calling are not the same. No time-varying aquatic plant growth/height/biomass, submerged refuge utilization or larval survival was measured.

The prior *actual held-out forecasting* (same original field source, different estimand) found wetland class + depth improving weather/season site-block Brier **0.2080→0.1742** while static emergent percent did **not** improve beyond habitat (Brier **0.1753**). These two observations jointly constrain—but do **not falsify**—an emergent stem-architecture refuge hypothesis.

**Additional plant corpus:** BioFresh public BF76 was previously audited with 17,532 records and 6,561 broad macrophyte-labelled records, but **0 source `eventDate` / `year` fields**, and `locality` is not a fully globally disambiguated source wetland ID. It cannot supply the missing plant **emergence date** or frog/plant at the same pond×event.

**NPS Hydroperiod** contains stable broad categories, not site event water depth. Its reported own-species prior strong site acoustic slope was **Ephemeral +0.3523**, Semi-permanent **+0.5022**, Permanent **+0.4950** under a post-hoc interaction model. These are associations with acoustic recurrence and hydroperiod **category**, not observed natural reflood or evidence of a wetland refuge predation effect.

**NAAMP** already has the frozen rain-associated conditional multi-site acoustic concentration residual **+0.29685**. The new same-source unit includes original `DaysSinceRain` when recorded, but the Hungarian rain−frog site-average rho is **not a contradictory refit of NAAMP’s paired rain contrast**: both time windows and response units differ. A direct rainfall×vegetation×prey-stage test requires measured rain and vegetation in the *same* source wetland×night.

## 5. Cross-study ecological commonalities, with exact claim levels

| Ecological commonality candidate | Independent source facts | Authorized conclusion |
|---|---|---|
| **Environmental breeding opportunity and stable site history** | RC6 rainy multi-stop chorus residual; NPS historic same-species source site preference; Hungary wetland class+depth improved acoustics over weather alone; controlled *L. fuscus* drawdown associates with stage-46 survivor mass | Plausible common ecological **filtering/opportunity theme**, but not one pooled causal coefficient or a demonstrated RC6 mechanism |
| **Developmental-stage observation windows** | INBO adult call→later larvae median 53 recorded-day lag; true simultaneous adult frog call soundfiles in NPS; global GBIF life-stage seasonal overlap | Phenology of **observations** is structured and source unit/date matters |
| **Specific predator avoidance or suppressed competitors at chorus centers** | Other adult frog source choir only 6/245 INBO site-years, Caudata absence only 12/189 stage events, GloBI matched prey-specific overlap 26/56 positive at strict threshold | **Not identified**; no direct dietary partner, pond-level predator census, or recorded prey-fate experiment in the NAAMP units |
| **Emergent-plant phenophase / cover as refuge** | Hungary has one static per-pond cover percent; GBIF/BioFresh plant reports not same-event measured refuge; NWI Cowardin codes static | **Not measured** as a seasonal refuge mechanism |

**Best defensible thesis today:** episodic breeding activity has nontrivial taxon-specific spatial organization and a measurable relationship with recurrent acoustic monitoring places. Environmental heterogeneity and phenology constitute credible shared filters, but **predator/competition release and developmentally stage-specific refuge remain open alternatives**, not demonstrated drivers of the RC6 residual. Stronger explanations should first beat a **local pond state + changing source-effort + calendar phenology** comparator in genuinely matched wetlands.

## 6. GBIF neighborhood/pond geometry stop rule

[Audited geometry/GBIF/NWI receipt](naamp_gbif_nwi_neighborhood_g0.json), [source CI](https://github.com/zuizui0223/frogcs/actions/runs/40261164561): 24 sampled source-coordinate-consistent NAAMP routes and 48 listening points. Only nine original recorder points overlap any official NWI mapped polygon and **none** directly overlap a mapped PEM polygon; these are recorder **points**, not nearest ponds. GBIF 2010–2015 neighborhood API had HTTP429 (Anura 31/48 failed, Caudata 19/48, Odonata 25/48); data retrieval and exact stage precision are not adequately comprehensive. No animal source null or within-pond competitive release conclusion may be made by interpreting HTTP429/missing GBIF as no predator.

## 7. Next **one** mechanistic dataset gate

To discriminate all user hypotheses in ONE coherent ecological model, minimum design is an independently verified **physical wetland × survey date × focal species and actual egg/tadpole development stage** panel including:

1. **Rain and actual inundation:** wetland/date rainfall, 1–3–7 day precipitation, measured water depth, actual dry-down/re-wetting/pond area and hydroperiod class.
2. **Vegetation temporal structure:** date-measured `Phragmites`/`Typha`/other emergent new shoot state, stems/m², inundated stem shelter complexity, submerged cover/height; note source effective refuge depends on predator gape/size and prey-stage vulnerability.
3. **Interaction guild and response:** fish, large overwintering frog tadpole, newt and odonate larval size/abundance **at that same pond**, other frog egg/larval species size/density, repeated prey fate or exclosure experiment.
4. **Adult chorus and season:** exact site-level adult call event, time/effort/observer, taxon and within-season peak, not NAAMP sequence alone.
5. **Cross-tested comparisons:** environment/hydroperiod/vegetation-only vs additional measured competition/predator stage, vs proximity/lag of stages, vs interactions under rain/drying; same ponds/years/effort, held-out entire ponds and years, plus **preplanned correlations, signed lag distributions and matched negative controls**. Do not use GBIF "not reported" as absence.

Until this panel is available, do **not** claim **specific predator avoidance**, **contemporaneous plant refuge causal filtering** or **physical ponds synchronizing their choruses** from the current source-commonality report.

**RC6 freeze and editorial status:** the historic JAE candidate remains complete and scientifically immutable. Immediate stand-alone submission is deferred by [one-paper editorial decision](../../INTEGRATED_PAPER_DECISION_2026-10-26.md). This commonality synthesis is a research-only support to the [integrated working paper](../../manuscript/INTEGRATED_FROG_ECOLOGY_DRAFT_V0_1.md).
