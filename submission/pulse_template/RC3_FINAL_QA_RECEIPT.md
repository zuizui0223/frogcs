# RC3 final QA receipt

## Frozen release authority

- release branch: `release/jae-multisite-rc3`
- submission branch: `submission/jae-multisite-v3`
- final release/submission head: `38eb4676320493070ef84ad5e8b803d692878587`
- validated scientific source commit: `bea996b3bf59fa1e66dedcc5cbd0a68833fa311d`

The only changes between the validated scientific source and the final release head are release/readiness documentation corrections. Manuscript, SI, figures, integrated results and WFTS code authority are unchanged.

## Final release-branch QA

All five required workflows passed on the **final release head**
`38eb4676320493070ef84ad5e8b803d692878587`:

1. manuscript QA — run `36804225805` — PASS
2. canonical figure QA — run `36804225841` — PASS
3. scientific submission bundle — run `36804225831` — PASS
4. WFTS Daymet weather adapter QA — run `36804225814` — PASS
5. WFTS confirmatory synthetic QA — run `36804225790` — PASS

## Final submission artifact

- artifact: `frogcs-jae-pulse-template-scientific-submission`
- artifact ID: `11136662824`
- size: **818,122 bytes**
- digest: `sha256:172cfb6dc18842536a1dd0de41a96f0edee58e0a438f192bee774c06111a872c`

## Final prospective WFTS QA artifacts

Daymet synthetic QA:
- artifact ID: `11136797317`
- digest: `sha256:0f0a9f342039052568f7d7076d5613a3061135f475f134e633ffab5f7d9e6800`

Confirmatory-core synthetic QA:
- artifact ID: `11136827299`
- digest: `sha256:33dd62d7dcbde1379e407c0756d1ace4c625ae5a0e2eadd9693add0e9d93bd5c`

Synthetic ecological direction has no inferential meaning.

## Final RC3 scientific package

- manuscript: `paper/manuscript_pulse_template_v0_4.md`
- SI: `paper/supporting_information_pulse_template_v0_2.md`
- figures: canonical five-figure set under `figures_pulse_template/`
- integrated results: `revision/INTEGRATED_RESULTS_V0_2.json`
- evidence hierarchy: `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_2.md`
- claim map: `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_3.md`
- synthesis: `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_1.md`

## Final WFTS authority

Real WFTS response data may be used only with:
- `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`
- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- `scripts/wfts/build_daymet_covariates.py`
- `scripts/wfts/preflight_wfts_structure.py`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

WFTS status remains:

**DESIGN_ELIGIBLE / DATA_ACCESS_PENDING**

No WFTS species × station × year concentration outcome has been inspected.

## Stop rule

RC3 is scientifically frozen.

No additional same-NAAMP mechanism search is authorized.
