# v5.3 — Real 673-row frog monitoring audit: field observation method versus published species×site×period grain

**v5.5 official source identity update:** [Original CEWH MDMS sample points matched to original government frog SamplePoint strings](V5_5_REAL_MDMS_FLOWMER_SAMPLEPOINT_CROSSWALK_AND_WETLAND_UNIT_BOUNDARY.md), [CI 38015127655 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38015127655). All **48** distinct public frog sample labels (Murrumbidgee **28**, Gwydir **6**, Lachlan **14**) exactly and uniquely match the official government MDMS `NAME` point feature, and all 48 features have different exact coordinate pairs **without publishing any coordinates**. This fixes the **point LABEL/feature-ID correspondence**. It does **not** verify independence of physical wetland ecological units: multiple point features may reside inside one wetland; site-label bootstrap intervals remain clustered by **source monitoring point**, not authenticated wetland. Original genus-level larvae and net-effort provenance still missing.


**v5.4 taxonomic correction (2026-10-10, actual government source):** [Aggregate source genus tie audit](V5_4_REAL_GENUS_CPUE_TIE_CLASSES_AND_SOURCE_CORRECTION.md), [GitHub Actions 38014198140 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38014198140), shows the **seven exactly equal POSITIVE tadpole CPUE cases** comprise only **one** pair of different `Limnodynastes` species, **one** other within-genus pair, and **five CROSS-GENUS pairs**. Thus seven positive coincidences are **NOT evidence that `Limnodynastes` pooled field tallies were systematically copied to all species rows**. Seven species codes each mapped to a single public speciesName; that does **not** verify larvae-to-species field identification. The original report's genus-pooled larvae note remains true, separate from the source table's CPUE ties. The v5.2 descriptive sign reversal stays a **table-level** result, not demonstrated conspecific reproductive payoff.
**2026-10-10 JST. Real-source ecological *interpretability audit*, not a new biological effect estimate.**
**CRITICAL: v5.2 numerical sign reversal stays true for the source rows, but a same-species reproductive-payoff interpretation is NOT currently supported.**

## 1. A substantially stronger primary method source was located

[Commonwealth Environmental Water Office / Charles Sturt University: Wassens et al. (2021), *Murrumbidgee River System Technical Report 2014–2020*](https://cdn.csu.edu.au/__data/assets/pdf_file/0008/3853403/Murrumbidgee-2019-20-MER-Technical-Report_final.pdf), **section 4.5, original PDF page 92 / printed page 89, and Table 4-23 PDF page 109**.

The report says original Murrumbidgee sampling (beginning 2014) took place at **12 wetland monitoring sites, generally four rounds each water year (Sep, Nov, Jan, Mar)**, except when dry or too shallow for nets; two additional wetland sites sampled in 2019–20. The actual *field events* included:
- **Adults/calling:** after dark, **two 20-minute transects**, detecting and counting frogs either encountered or heard calling. These are not 31-day uninterrupted recordings, and are not directly equivalent to the 5-minute Ocock census or NAAMP CI scale.
- **Tadpoles:** usually two large + two small **fyke nets**, set **overnight for an average of 14 hours**; smaller D-fyke nets substituted at shallow sites. Tadpole CPUE = number captured divided by the **average net soak time** of the four nets. The publicly released 2014–22 frog CSV has **no net-soak time, gear type, or complete unsuccessful gear-deployment ledger among its 16 data columns**.
- **Stage-to-taxon limitation:** the report's **Table 4-23 explicitly pools *Limnodynastes* spp. tadpoles at genus**, because the tadpoles were not distinguishable to species in the field. This alone invalidates an automatic interpretation of every listed-species `CPUETadpoles` value in the modern public CSV as *the identified offspring of exactly that calling species* until the original data-custodian mapping is verified.
- Original wetland analyses include month, water year, wetland zone, water temperature, depth and fish/vegetation/water-quality summaries; these potential drivers are **not** directly represented as response-aligned columns in the public frog CSV.

A newer [official Murrumbidgee 2024–2030 area-scale plan](https://www.dcceew.gov.au/sites/default/files/documents/flow-mer-murrumbidgee-area-scale-evaluation-research-plan-2024-30.pdf) describes **three 2-minute recordings at 10-minute intervals and a 40-minute nocturnal transect**. It illustrates that source protocol versions change; do **not** retrospectively assume the current monitoring scheme was employed in 2014–2022.

**Vital correction to v5.1:** The government's `sampleDateStart` → `sampleDateEnd(Date/Time)` >31-day spans reflect the **CSV observation/aggregation interval**. They are NOT proof observers continuously listened or netted tadpoles for 31+ days. Event times may exist in underlying field records; the CSV does not preserve them at the required granularity.

## 2. New actual SOURCE UNIT QA: 579 species-labelled rows share just 98 site×interval units

A **post-v5.2 outcome-exposure** but pre-QA frozen structural check, [v5.3 original source/field protocol contract](V5_3_CEWO_FIELD_PROTOCOL_AND_SPECIES_STAGE_GRAIN_QA_CONTRACT.md), was committed before running this particular source-unit comparison. It is not a preregistered biological confirmatory analysis.

[Official data QC GitHub Actions run **38013002316 (SUCCESS)**](https://github.com/zuizui0223/frogcs/actions/runs/38013002316), [reproducible source-only code](scripts/audit_flowmer_repeated_cpue_across_species_v53.py). Query selected `Program, SamplePoint, SampleDate, sampleDateStart, sampleDateEnd(Date/Time), speciesCode, callingEvidence, CPUETadpoles`; no coordinates, taxonomic names or free-text were requested. Only aggregate site×interval structure and **exact positive CPUE collision counts** printed; raw species/site labels and values were not exposed.

Same frozen Murrumbidgee primary scope as v5.2:
- Source Murrumbidgee: **591** published listed-species rows.
- Exclude **10** zero-length source intervals and **both records under one duplicate site×species×interval source key**, leaving **579** distinct listed-species×sample-point×long-interval rows.
- These are attached to only **98 distinct sample-point × start × end interval groups**, with **3–7 listed species per interval**, distributed:
  - 3 species: **3** interval groups
  - 4 species: **15**
  - 5 species: **14**
  - 6 species: **22**
  - 7 species: **44**
- In **30/98** groups, all listed species' tadpole CPUE values equal **zero**; in **68/98**, species-level values differ.
- In **7/98**, **two or more different listed species** in exactly the same sample-point×interval had an **identical strictly positive tadpole CPUE value**. This *is not proof* of a taxonomic mistake: true values and rounding may tie. However, given original *Limnodynastes* genus pooling, **the original-stage crosswalk is especially important**.
- In **81/98** groups, at least two listed species have different recorded Y/N calling statuses. In **64** of those groups, some tadpole CPUE is positive. This is **between-species status heterogeneity inside a shared site/interval**, not 81 independent rainfall events.
- The original 2014–20 report describes 12 core wetlands (plus additional monitored wetlands), while the published 2014–22 CSV has **24 distinct `SamplePoint` labels** in the eligible v5.2 rows. We have **not verified whether each public `SamplePoint` equals one distinct physical wetland, subpoint, renaming, or habitat segment**. Therefore the v5.2 bootstrap clusters should be described as **source SamplePoint-label clusters**, *not 24 confirmed independent physical wetlands*.

## 3. How this changes what v5.2 actually found

[v5.2 original real result](V5_2_REAL_CALLING_TADPOLE_SIGN_REVERSAL_AND_NONCAUSAL_INTERPRETATION.md):
- across **579 listed-species×samplepoint×long-interval source rows**, tadpole-CPUE-positive rate `73/374=19.52%` with calling Y versus `73/205=35.61%` with N; pooled difference **−16.09 percentage points** (site-label cluster bootstrap 95% `[-24.14,-10.55]`).
- within **58 site-label×speciesCode repeated groups** in which C=Y and C=N were both reported (359 rows), equal-pair contrast **+19.85 points**; post-outcome same-pair-subset ordinary pooled difference **+10.93 points** and exploratory label-cluster interval for equal-pair contrast **[+11.42,+28.52]**.
- These are **correct descriptive computations on the chosen public CSV**. But the 579 entries are **not independent species-specific breeding events**; they are grouped inside 98 season/period-level sample units. Mixed observational methods, gear/water-dependent survey availability, genus-aggregated larvae, and unknown publication/effort mapping can alter their biological interpretation.

**Revised scientific classification:** `REAL_SOURCE_ROW_SIGN_REVERSAL; SPECIES_SPECIFIC_LARVAL_PAYOFF_UNIDENTIFIED`. The Simpson-like sign reversal can be described as a **source-table-level composition pattern**. It cannot yet support a claim that within-species calling favors larval production, that calling suppresses larvae across taxa, or that species-specific reproductive returns reverse by statistical aggregation.

This is **not a biological null result**. The necessary biological identification facts are absent from the publication-ready 2014–22 frog CSV.

### Why a naïve "corrected" regression would be counterproductive

Adding site random intercepts or rainfall covariates to the published aggregate rows cannot restore:
- missing actual individual 20-min transect dates and multiple rounds,
- actual fyke-net dates, soak duration, gear method and failed deployment,
- taxonomic correspondence of genus-only tadpoles,
- independent dates for adult calling and offspring presence,
- exposure to event-specific local wetland depth/inundation/rain sound,
- complete surveyed-but-unlisted species negatives.

No outcome-driven restricted species analysis was run here and none is justified before the **source codebook/crosswalk**. This maintains separation from locked JAE RC6 and avoids overstating an appealing empirical sign flip.

## 4. Next useful source action (NOT SENT)

Contact the CEWH Flow-MER programme custodian **only if the author approves it**, initially requesting **method/dictionary metadata, not records or precise coordinates**:
1. Does `CPUETadpoles` represent a *truly species-specific* fyke-net measure for each `speciesCode`, and how are field-unidentified *Limnodynastes* spp. tadpoles handled in this 2014–22 public upload? Do any genus-level tallies get copied to constituent species rows, assigned an arbitrary species, or stored under a genus code?
2. What do `callingEvidence=N` and a numeric CPUE=0 mean in terms of an actually completed survey? Were calls and fyke nets always sampled on the same nights and sites, even when wetlands dried or nets could not be set?
3. Why do **581/591** Murrumbidgee entries have **publication interval endpoints >31 days** although field monitoring used 4 survey rounds/year, and can authentic *short survey event timestamps* be accessed?
4. What original source mapping defines a genuine physical wetland across the 24 `SamplePoint` labels in the eligible release and the report's 12 longstanding wetland locations? Site-alias-to-core-wetland counts only are sufficient initially, with no coordinates or sensitive animal records.

Do **not** send messages or access protected documents without user authorization. The high-value result now is a well-defined **source classification and stop**, not another regression.

### Data source citations

- Wassens et al. 2021 Murrumbidgee Technical Report 2014–20: field Methods around PDF p.92, Table 4-23 PDF p.109.
- Australian government 2023 [Flow-MER Frog Abundance 2014–22 metadata/data dictionary](https://data.gov.au/data/dataset/flow-mer-frog-abundance).
- Government 2024–2030 updated programme plan for distinct later monitoring methods.
- Original public v5.2 code/results and source-only v5.3 Actions report.
- **JAE RC6 main remains unchanged**.
