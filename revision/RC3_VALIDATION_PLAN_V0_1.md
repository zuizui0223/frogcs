# RC3 validation plan v0.1

## Prospective release refs

Create only after every required check below passes on the same commit:

- `release/jae-multisite-rc3`
- `submission/jae-multisite-v3`

Until then, RC2 remains the frozen integrated authority.

## Scientific manuscript authority

- `paper/manuscript_pulse_template_v0_4.md`
- `paper/supporting_information_pulse_template_v0_2.md`
- title: **Rainfall-associated frog chorus activation shows within-taxon multi-site coherence and species-specific site recurrence**

Required manuscript properties:
- no public use of “higher-order” as the focal term;
- principal spatial comparator = cross-fit species response + strictly-prior physical-site history + dry persistence;
- exact N,K exchangeable calculation = secondary diagnostic only;
- post-opening exploratory provenance explicit;
- cross-fitting explicitly not independent confirmation;
- no untouched NAAMP confirmation partition claimed;
- prospective external replication required.

## Figure authority

Canonical renderer:
- `revision/build_pulse_template_figures.py`
- `revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json`

Required visible Figure 3:
- principal species + prior-site-history comparator first;
- held-out rain × history gate second;
- species-only / uniform / persistence as secondary sensitivities;
- exact N,K diagnostic secondary and caveated;
- public filename `fig3_within_taxon_concentration.svg/png`.

## Submission authority

Workflow:
`.github/workflows/pulse_template_submission_pipeline.yml`

Must PASS:
- manuscript QA;
- metadata smoke test;
- canonical figure render;
- anonymous DOCX + SI build;
- anonymity/format checks;
- five PNG submission figures;
- SHA256 submission manifest.

## External replication authority

WFTS remains **DESIGN_ELIGIBLE / DATA_ACCESS_PENDING**.

No WFTS frog-response outcome has been inspected for the RC3 discovery claim.

Sole real-data confirmation tuple:
- `revision/WFTS_CANONICAL_SCHEMA_V0_2.json`
- `revision/WFTS_WEATHER_AND_ANALYSIS_SPEC_V0_4.md`
- `revision/WFTS_DAYMET_WEATHER_SPEC_V0_1.md`
- `scripts/wfts/build_daymet_covariates.py`
- `scripts/wfts/preflight_wfts_structure.py`
- `scripts/wfts/run_wfts_confirmatory_analysis_v0_4.py`

Required before RC3 freeze:
- Daymet synthetic weather QA PASS;
- WFTS confirmatory synthetic QA PASS;
- confirmatory QA must not assert ecological PASS/FAIL direction;
- stale v0.3 real-data workflow removed;
- development v0.1–v0.3 scripts remain history only.

## RC3 freeze rule

RC3 may be created only from one commit for which all of these workflows PASS:

1. `pulse-template manuscript QA`
2. `build pulse-template figures`
3. `pulse-template submission pipeline`
4. `WFTS Daymet weather adapter QA`
5. `WFTS confirmatory code QA`

A workflow PASS on an earlier commit is insufficient.

## Scientific stop

No additional same-NAAMP mechanism search is authorized.

Allowed after RC3 freeze:
- copy editing;
- private author metadata;
- archive license/DOI;
- outcome-blind WFTS data acquisition/schema adaptation;
- one-shot WFTS confirmation under the frozen authority tuple.


## Figure synchronization receipt

The canonical figure renderer has been executed after the RC3 terminology/comparator changes.

Generated repository outputs now include:
- `fig3_within_taxon_concentration.svg/png`;
- no canonical `fig3_higher_order_null_ladder.svg/png`;
- Figure 5 visible title uses within-taxon multi-site concentration terminology.

The bot-generated figure commit is part of this validation lineage. This human-authored commit exists only to trigger the final same-head QA suite after GitHub declined to auto-run PR workflows from the bot-authored commit.
