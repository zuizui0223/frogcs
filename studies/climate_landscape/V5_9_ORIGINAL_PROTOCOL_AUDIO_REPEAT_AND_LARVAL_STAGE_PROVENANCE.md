> **2026-10-10 subsequent source update:** [v6.0 real 2016–2025 archived recording-source discovery](V6_0_REAL_MURRUMBIDGEE_ACOUSTIC_HYDROLOGY_ARCHIVE_AND_DISCRIMINATION.md) resolves the earlier *existence* uncertainty: the original 2025–26 government plan records **12 long-term acoustic stations** with five-minute/hour archives, and a later 2026 report actually uses recordings and human-verified frog detections. **Retention/third-party access of a complete site×timestamp scientific analysis table remains unverified.** v5.9's 3-vs-6 acoustic survey *bout* discrepancy concerns an older field protocol, not the continuous/automated recorder's 5-min/hour duty cycle; these must not be conflated.

# v5.9 — original 2019 CEWH field-method reconciliation, not a new frog effect

**2026-10-10 JST. Independent draft PR #135 only.** This is a cross-document *protocol provenance* finding: planned audio/adult/tadpole survey units are different, and the original plan itself gives different audio-repeat counts. JAE RC6/main, the 579-row Flow-MER descriptive result, and the 2014–22 frog response dataset are unchanged.

## Actual original publication reviewed

**Wassens et al., Murrumbidgee Selected Area Monitoring, Evaluation and Research Plan 2019–2022**, original official Australian Government PDF:
https://www.dcceew.gov.au/sites/default/files/documents/mer-plan-murrumbidgee-2019.pdf

Material checked in original source:
- Table 2-1, PDF **page 15** (0-based page index 15) has programme wetland names, short site abbreviations, zone and habitat classifications, including **core versus alternate site** footnotes; this is a published programme *wetland-site table* but **NOT a source-authenticated join** to 2014–22 frog `SamplePoint` values or CEWH MDMS `NAME/SAMO_ID` point IDs.
- Table 4-1, PDF page **34**: **calling** planned as **3 × 2-minute** acoustic surveys, 10-minute intervals, 4 surveys/year; **adult frogs** planned as **2 × 20-minute nocturnal transects**; tadpoles are part of separate wetland fish / fyke-net sampling. Replacing one core wetland with an alternate is documented.
- Table 5-7, PDF page **67** repeats **3 × 2-minute** acoustic bouts and **40-minute adult transects**, ~12 core wetland sites across three regions; Table 5-7 also lists **tadpole development stage** as an intended separate monitoring metric.
- **Methods narrative, PDF page 68**, separately specifies **2 × 20-minute** visual encounters **and 6 × 2-minute audio** surveys. Thus **3 versus 6 acoustic repetitions conflict *within the plan***. This cannot be resolved by choosing one unilaterally; request original field protocol version, visit-level instrument and actual completed effort.
- The same Methods narrative says tadpoles *will be* identified to species and developed stages measured in some specimens. This is an **intended method**, not proof that every original field larva was species-identifiable.
- **Section 5.7.3, PDF page 69** says automatic call recorder units were deployed at each wetland in 2016 and had capacity for hydrology–calling research. This is a **potential historical data-source lead only**, **not proof** that source audio, metadata, permissions or a crosswalk is retained/accessible.

## Contrast with the later executed-field report and public release

Original post-survey report:
https://cdn.csu.edu.au/__data/assets/pdf_file/0008/3853403/Murrumbidgee-2019-20-MER-Technical-Report_final.pdf

Prior [v5.3 source-grain audit](V5_3_REAL_SOURCE_STAGE_GRAIN_QA_AND_SIGN_REVERSAL_DOWNGRADE.md) documents two timed nocturnal transects and separately deployed overnight fyke nets. Table 4-23 in the report **pools some *Limnodynastes* tadpoles at GENUS**, since larvae were not reliably identified to species. This is **not evidence the source violated the 2019 intended protocol**; it is a source-level limit of actual field-stage identification. Clarification is needed about which original events and stage identifications underlie the published species-labelled `CPUETadpoles`.

Public 2014–22 release:
https://data.gov.au/data/dataset/flow-mer-frog-abundance

Prior [v5.0](V5_0_FLOW_MER_ACTUAL_PUBLIC_FROG_SOURCE_AND_FROZEN_QC.md) / [v5.1](V5_1_REAL_FLOWMER_INTERVAL_GRAIN_AND_ACUTE_MECHANISM_STOP.md) verified that the public release has **673 species-labelled rows** but **no separate survey effort, audio-repeat, sampler/method/gear, larval-field-ID, or original event/visit key columns** in its 16-column API projection. In Murrumbidgee, almost all source intervals are **>31 days**, not direct night-level audio/tadpole events.

## Three separate levels must NEVER be silently collapsed

| Level | Unit asserted by source | Is it verified in published frog table? |
| --- | --- | --- |
| 2019 programme plan | 12 planned core wetland monitoring sites, with possible alternates and changing availability | **No physical wetland ↔ 28 public `SamplePoint` point crosswalk** |
| Calling | Repeated, short **acoustic bouts** (3×2 in tables / 6×2 in prose) | **No original bout/actual effort/recording ledger** |
| Adult detections | 2×20-min **visual encounter** transects | **No unequivocal separation from source `callingEvidence` Y/N in public table** |
| Larval abundance | Separate **fyke-net** sampling, original identifiable stage and gear-specific effort | **No original field species/genus crosswalk and event-specific net effort** |
| Archived acoustic source | Automatic recording units reportedly deployed in 2016 | **Archive retention, station linkage and permitted access unverified** |

**The 2019 plan neither contradicts nor verifies specific event-level measurements performed in every 2014–22 water year.** It is a plan; the 2019–20 actual field report, method changes, and public 2023 data extract are different documents/versions.

## Consequences

1. **No new frog outcomes, no estimated same-species reproductive payoff.** The v5.2 `−16.09 pp` pooled versus `+19.85 pp` equal-within-pair *published-row* sign reversal remains exploratory source-table composition, not adult chorus → conspecific offspring.
2. **Do not treat `callingEvidence=N` as a negative listening opportunity** for absent species, or `CPUETadpoles=0` as a completed effort-adjusted non-recruitment event, without an original source event/effort/ID mapping.
3. **Do not assert an exact 2-, 3-, or 6-bout acoustic exposure** for any actual frog-source row. The official plan itself is internally inconsistent on 3 vs 6.
4. **Original site continuity is not automatically validated by the wetland table**: 2019 plan acknowledges site substitutions and temporary wetness; MDMS 2022 points do not necessarily uniquely index wetland-level units through 2014–22.
5. The potentially useful **2016 acoustic recorders** create one new author-approved, **metadata-only** historical availability question, not an authorization to acquire or examine any audio.

## Decisive next source question, not another exploratory regression

The corresponding [v5.9 concise CEWH query remains NOT SENT](V5_9_CEWH_ORIGINAL_ACOUSTIC_AND_WETLAND_LEDGER_QUERY_UNSENT.md). Request only whether authoritative dictionaries exist for (i) source point↔wetland ID and changes, (ii) genuine completed acoustic bout / visit effort and negative opportunities (including 3-vs-6 discrepancy), (iii) larval genus/species field-stage assignment and net effort, and optionally (iv) 2016 recorder archive metadata without audio.

**STOP**: no more field-name similarity joins or published CSV outcome mining until those source-authenticated identifiers are available. No new biology is established by this methods provenance finding.

Original-source disclosure: only public report text and existing audit receipts were reviewed here. No private dataset or custodian email was accessed/sent.
