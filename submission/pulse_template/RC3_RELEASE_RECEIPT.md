# Integrated JAE RC3 release receipt

## Frozen authority

- release branch: `release/jae-multisite-rc3`
- submission branch: `submission/jae-multisite-v3`
- frozen commit: `fc9509dac8c8374041a0ddb86538bbf58240a748`

Both branches are byte-identical to the frozen commit.

## Scientific package

Title:

**Rainfall-associated frog chorus activation shows within-taxon multi-site coherence and species-specific site recurrence**

Frozen files include:
- `paper/manuscript_pulse_template_v0_4.md`
- `paper/supporting_information_pulse_template_v0_2.md`
- canonical five-figure set under `figures_pulse_template/`
- `revision/INTEGRATED_RESULTS_V0_2.json`
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_2.md`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_3.md`
- `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_1.md`
- frozen prospective external-replication specifications and WFTS code authority.

## Same-head validation

All required workflows passed on `fc9509dac8c8374041a0ddb86538bbf58240a748`:

1. manuscript QA — run `36798162816` — **PASS**
2. canonical figure QA — run `36798162733` — **PASS**
3. scientific submission bundle — run `36798162846` — **PASS**
4. WFTS Daymet weather adapter QA — run `36798162751` — **PASS**
5. WFTS confirmatory code synthetic QA — run `36798162730` — **PASS**

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
- artifact ID: `11134124522`
- size: **818,124 bytes**
- digest: `sha256:b166759661673d0e4ed6a381eb2d48950904e49b0d999c14ebbbb6dbd038ed98`

## Prospective WFTS code QA

WFTS remains:

**DESIGN_ELIGIBLE / DATA_ACCESS_PENDING**

No WFTS frog-response outcome was used to validate RC3.

Frozen WFTS authority:
- schema: `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
- weather/analysis spec: `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`
- Daymet spec: `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- weather adapter: `scripts/wfts/build_daymet_covariates.py`
- outcome-blind preflight: `scripts/wfts/preflight_wfts_structure.py`
- confirmatory core: `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

Synthetic confirmatory artifact:
- artifact ID: `11134207458`
- digest: `sha256:1c0027eccc1fc7ea632f24f657f589a16b32d2f29d79c38c533885f3c0199c3b`

Synthetic Daymet artifact:
- artifact ID: `11134761857`
- digest: `sha256:c1193088b7b56f6475ea631b067d98d971ccce0793fb3103a1375f0bab0cf131`

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
