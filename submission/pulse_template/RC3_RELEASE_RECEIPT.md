# Integrated JAE RC3 release receipt

## Scientific authority

- release branch: `release/jae-multisite-rc3`
- submission branch: `submission/jae-multisite-v3`
- **validated scientific source commit:** `bea996b3bf59fa1e66dedcc5cbd0a68833fa311d`

The release/submission branches are documentation-only descendants of that validated scientific source. Scientific files listed below are unchanged from the validated source commit.

## Scientific package

Title:

**Rainfall-associated frog chorus activation shows within-taxon multi-site coherence and species-specific site recurrence**

Frozen scientific files:
- `paper/manuscript_pulse_template_v0_4.md`
- `paper/supporting_information_pulse_template_v0_2.md`
- canonical five-figure set under `figures_pulse_template/`
- `revision/INTEGRATED_RESULTS_V0_2.json`
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_2.md`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_3.md`
- `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_1.md`
- prospective external-replication specification and WFTS authority tuple.

## Same-head scientific validation

All required workflows passed on the same scientific source commit
`bea996b3bf59fa1e66dedcc5cbd0a68833fa311d`:

1. manuscript QA — run `36798468716` — **PASS**
2. canonical figure QA — run `36798468724` — **PASS**
3. scientific submission bundle — run `36798468743` — **PASS**
4. WFTS Daymet weather adapter QA — run `36798468773` — **PASS**
5. WFTS confirmatory code synthetic QA — run `36798468713` — **PASS**

## JAE manuscript/bundle measurements

- manuscript words: **7,443**
- abstract words: **341**
- keywords: **8**, alphabetized
- anonymous manuscript DOCX: **58,827 bytes**
- Supporting Information DOCX: **68,879 bytes**
- canonical SVG figures: **5**
- canonical PNG figures: **5**
- continuous line numbering: PASS
- double spacing: PASS
- page numbering: PASS
- reviewer-facing identity scan: PASS
- metadata renderer smoke test: PASS
- scientific bundle assembly: PASS

## Submission artifact

Workflow artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: `11135165910`
- size: **818,122 bytes**
- digest: `sha256:1a5c6013ff2132d118e15ae468f209c26b91b8622fb8a7410f228dc68ad645fc`

## Prospective WFTS code QA

WFTS remains:

**DESIGN_ELIGIBLE / DATA_ACCESS_PENDING**

No WFTS frog-response outcome was used to validate RC3.

Frozen real-data authority:
- schema: `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
- weather/analysis spec: `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`
- Daymet spec: `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- weather adapter: `scripts/wfts/build_daymet_covariates.py`
- outcome-blind preflight: `scripts/wfts/preflight_wfts_structure.py`
- confirmatory core: `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

Synthetic confirmatory artifact:
- artifact ID: `11134882150`
- digest: `sha256:8e12558c7b506bacf84951ec9fc91b1c21ec710de4d1f22f0931994d5c1b5634`

Synthetic Daymet artifact:
- artifact ID: `11134172975`
- digest: `sha256:5585e406f2d9cbcfa9e439cb7260b0d5db74c812836f511867fff2de2db2bcdf`

Synthetic PASS/FAIL direction has no scientific inferential role; these workflows validate code-path integrity only.

## RC3 scientific changes relative to RC2

RC3:
- demotes the exchangeable exact N,K null to a secondary combinatorial diagnostic;
- makes cross-fit species response + strictly-prior physical-site history + dry persistence the principal comparator;
- uses within-taxon multi-site concentration/coherence terminology instead of “higher-order” in reader-facing text;
- explicitly states that cross-fitting is not independent confirmation;
- explicitly states that no untouched NAAMP confirmation partition remains;
- freezes prospective external replication before WFTS outcome access.

## Stop rule

RC3 is scientifically frozen.

No additional same-NAAMP mechanism search is authorized.

Allowed post-freeze work:
- private author metadata;
- copy-editing that does not change scientific claims;
- license/archive DOI;
- outcome-blind WFTS raw-data acquisition/schema adaptation;
- the one-shot WFTS confirmation under the frozen authority tuple.
