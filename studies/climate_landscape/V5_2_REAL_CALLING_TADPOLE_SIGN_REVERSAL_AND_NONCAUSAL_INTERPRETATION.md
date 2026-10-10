# v5.2 — REAL Flow-MER source concordance reverses sign within repeated species×sites


**v5.4 taxonomic correction (2026-10-10, actual government source):** [Aggregate source genus tie audit](V5_4_REAL_GENUS_CPUE_TIE_CLASSES_AND_SOURCE_CORRECTION.md), [GitHub Actions 38014198140 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/38014198140), shows the **seven exactly equal POSITIVE tadpole CPUE cases** comprise only **one** pair of different `Limnodynastes` species, **one** other within-genus pair, and **five CROSS-GENUS pairs**. Thus seven positive coincidences are **NOT evidence that `Limnodynastes` pooled field tallies were systematically copied to all species rows**. Seven species codes each mapped to a single public speciesName; that does **not** verify larvae-to-species field identification. The original report's genus-pooled larvae note remains true, separate from the source table's CPUE ties. The v5.2 descriptive sign reversal stays a **table-level** result, not demonstrated conspecific reproductive payoff.
**Run: 2026-10-10 JST. Exploratory independent ecological description. Do not amend or merge into JAE RC6 `main`.**
**Source:** Australian Government/CEWH [Flow-MER Frog Abundance 2014–2022](https://data.gov.au/data/dataset/flow-mer-frog-abundance), public CKAN resource `70f3b7c9-990b-4770-b306-57c4e7cdac61`. `callingEvidence` is Y/N for a **listed species**; `CPUETadpoles` is mean tadpole catch per unit effort. The interval ends are exclusive. These are not measures of rain sound, NAAMP CI2–3, metamorphosis survival or known breeding events.

**Critical temporal provenance:** [v5.2 source-metadata-exposed, response-blind frozen plan](V5_2_PRE_RESPONSE_PERIOD_LEVEL_CALLING_TADPOLE_CONCORDANCE_CONTRACT.md) was committed as **`383494d` BEFORE** the first workflow that read Y/N frequencies and positive tadpole CPUE. The primary full-panel 2×2 and optional within-species×site contrast were frozen then. The **same-both-state-pairs restricted pooled contrast and its paired-cluster interval were added after viewing the initial results**, expressly as **post-outcome diagnostics**, not preregistered confirmation.

## Updated v5.3 source-method interpretation (2026-10-10)

**IMPORTANT QUALIFICATION:** [Source-backed v5.3 follow-up](V5_3_REAL_SOURCE_STAGE_GRAIN_QA_AND_SIGN_REVERSAL_DOWNGRADE.md) verified that adult frogs/calling were sampled with **two 20-minute nocturnal transects** but tadpole CPUE arose from **overnight fyke-net catches divided by net soak time**, with missing opportunities when wetlands were dry/shallow. The CEWO/CSU report's Table 4-23 expressly **pooled *Limnodynastes* tadpoles at genus**. Thus published `CPUETadpoles` is **not automatically identified conspecific offspring of every row's listed `speciesCode`**.

Actual aggregate-only [v5.3 source-unit CI](https://github.com/zuizui0223/frogcs/actions/runs/38013002316) shows the **579 public species-labelled rows occupy only 98 site-label×period groups**, 3–7 species/group; seven groups have the **same positive tadpole CPUE in two or more different species rows**, not by itself proof of an error. The apparent >31-day durations are **published aggregation windows**, not 31-day continuous surveys; original physical site correspondence for 24 listed `SamplePoint` labels remains unverified.

**Therefore revise the biological claim:** the pooled/within-pair sign reversal is a **real property of the released table**, but **species-specific reproductive payoff and ecological mechanism are NOT identifiable** without the original stage taxonomic crosswalk, visit timestamps, gear/effort and explicit genuine negatives. The bootstrap resamples public `SamplePoint` labels, **not 24 verified independent wetlands**. The original frozen v5.2 arithmetic below is retained unchanged for transparency; it is not being retuned after this audit.

## Source and fixed inclusion

Actual official government [Flow-MER](https://data.gov.au/data/dataset/flow-mer-frog-abundance) records: **673** species-record rows across Gwydir 36, Murrumbidgee **591**, Lachlan 46.

Frozen primary panel:
- Murrumbidgee only; `sampleDateStart < sampleDateEnd(Date/Time)` and period **strictly >31 days**;
- include only explicit, nonmissing `callingEvidence` Y/N and numeric `CPUETadpoles >=0` for listed species;
- exclude **10 zero-length-interval records**;
- exclude **both records** representing the **one nonunique `SamplePoint×speciesCode×start×end` key** (two records), rather than arbitrarily choosing one;
- resulting **579 unique species×site×interval source rows**, covering **24 sample sites**, **142 distinct site×species pairs**. These are **not 579 short-term surveys** and not a census of fully surveyed-but-unlisted species.

Source-verified [original interval QC](V5_1_REAL_FLOWMER_INTERVAL_GRAIN_AND_ACUTE_MECHANISM_STOP.md): Murrumbidgee's other **581** source rows span **>31 days**, so this analysis is inherently **long-period**, without inferred calling→tadpole lag.

[Initial outcome-stage source CI **38012383021 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38012383021). [Same-frame/weighting post-outcome QA **38012465613 — SUCCESS**](https://github.com/zuizui0223/frogcs/actions/runs/38012465613).
Scripts: `scripts/audit_flowmer_predeclared_call_tadpole_concordance_v52.py`. The raw record source projection excluded species names, latitude/longitude and free-text site descriptions. The code uses source `SamplePoint` and `speciesCode` internally to prevent pseudoreplication but emits **only aggregate counts, anonymously**.

## Original descriptive comparison (frozen before outcome values)

Define `C=1` if **the listed frog species was heard calling (Y)**, `C=0` if N; `T=1` if **tadpole CPUE>0** in the row's original interval; `T=0` if numeric zero. `T=0` is no tadpoles caught in the source's effort-based index, **NOT proof of absent or failed offspring**.

| Source rows (Murrumbidgee 579) | Tadpole CPUE=0 | Tadpole CPUE>0 | Total | Proportion tadpole-positive |
| --- | ---: | ---: | ---: | ---: |
| **Calling Y** | **301** | **73** | **374** | **19.52%** |
| **Calling N** | **132** | **73** | **205** | **35.61%** |
| **Total** | **433** | **146** | **579** | 25.22% |

**Unadjusted pooled risk difference:** `P(T>0|Calling Y) - P(T>0|Calling N) = -0.16091` (**−16.1 percentage points**).

**Site-cluster 1000-draw bootstrap 95% descriptive interval** (fixed seed 20261010): **[−0.2414, −0.1055]**. It treats site as the resampling cluster, but does not correct observational ascertainment, variable tadpole effort, species composition, shared dates or event clustering. No p-value; not a causal CI.

Both mismatch categories appear:
- **73 Y/T-positive** versus **301 Y/T=0**: call observed, but no tadpoles captured in the same summarized interval;
- **73 N/T-positive** versus **132 N/T=0**: no calling recorded for listed species, but tadpoles captured. This is **not** a detected taxon loss, silent site proof or reproduction from an earlier inferred call.

## The predeclared *within species×site* comparison has the opposite sign

The frozen secondary evaluability gate was met: **58 species×site pairs** observed with **both Y and N calling statuses**, representing **359 source rows** at **12 distinct sites**. Equal pair weighting of each pair's difference `fraction(T-positive when Y) − fraction(T-positive when N)` gives:

**+0.19848 (+19.85 percentage points)** (58 equal-weight pairs, within each physical sample site and taxon code).

This is a real, **descriptive positive association**, in contrast to the full pooled negative one. It is still not a time-lagged causal relation or an independently evaluated strong-chorus/payoff effect.

### Post-outcome diagnostic: does the positive direction persist on *the same 359 rows*?

The above secondary and full pooled summaries differ **both by row subset and weighting**. To avoid prematurely naming the reversal a mathematical Simpson paradox, the following **post-outcome nonconfirmatory check** used exactly those same 58 both-state pairs:

| Both-state-pair subset only (359 rows) | Tadpole=0 | Tadpole>0 | Total |
| --- | ---: | ---: | ---: |
| Calling Y | **194** | **50** | **244** |
| Calling N | **104** | **11** | **115** |

`50/244 − 11/115 = +0.10927` (**+10.93 percentage points**). Thus, the **positive sign on the comparable both-state-pair subset survives ordinary row weighting**; raising it to **+19.85 points** with equal species×site weights shows weighting also matters.

Source rows **outside** that within-pair-eligible subset number **220** by subtraction. They include C/Y:T+ **23**, C/Y:T0 **107**, C/N:T+ **62**, C/N:T0 **28**. Their very different stage-status mixture drives substantial change when moving from all rows to the within-pair comparable subset. However these rows reflect missing repeated contrasts and distinct species/site/interval composition, not necessarily a classic Simpson partition with identical underlying strata.

An **explicitly post-outcome** site-resampling descriptive 95% interval for the within-pair equal-weight difference: **[+0.1142, +0.2852]**, using the **12 sites** contributing pairs and seed 20261010. It is **NOT a frozen primary uncertainty result**, not a confirmatory finding, and not adjusted for year/catchment/flow, species detection or varying effort.

## What is and is not biologically new

**Empirical finding that is actually supported:** in the publicly released Murrumbidgee **long-period listed-species records**, the sign of the association between calling Y/N and tadpole CPUE-positive **depends sharply on whether species×site histories are mixed across groups or compared within repeatable species×site groups**. Both overall negative and repeated-pair positive summaries are real measured source characteristics, not synthetic fixtures.

**Plausible but UNTESTED generators:**
- differences in species' phenology, call conspicuousness and tadpole capture/detection;
- long aggregation interval could mix adult chorus and tadpole stages from different dates;
- water management and hydroperiod favoring tadpole capture while adult calling was not detected;
- heterogeneous wetlands/species/source ascertainment and composition of records included in the within-pair eligible set.

**Neither comparison shows that calling reduces reproduction in the pooled data nor that calling increases individual reproductive payoff within a site.** A sign flip is not evidence of ecological adaptation, attraction–fecundity trade-offs, rain-sound effects, or frog movement. We explicitly have **no** local rainfall data, temperature, separate 5-minute chorus intensity, complete visit-zero ledger, author-verified hydroperiod, or actual successful metamorph outcomes in this public source.

Crucially, the duration of most row intervals exceeds a month and the same species×site may contribute repeated rows over multiple years. **Differences in the exposed selection set and weighting, not biological causation, are sufficient to explain the mathematical possibility of a sign reversal.** The exact causal generator remains unidentified.

## Hard next-stage decision

The next step should be **source-specific protocol/effort verification** (particularly original meaning of Y/N=N and whether tadpole CPUE and calling refer to one physically comparable long interval), plus genuine visit-level observation times and site hydroperiod, before explanatory modelling. If no such source linkage is obtained, **do not iterate over taxa, dates, hydrologic windows or p-values to rescue a rain-to-breeding claim**.

Keep the present result labeled **exploratory observational period-level data**, independent from submitted frogcs JAE RC6. The original strong chorus-space-history rainfall paper remains unchanged.
