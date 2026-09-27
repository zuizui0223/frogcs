# JAE submission handoff — RC8 uniform-null benchmark candidate

## Candidate status

RC8 is an inferential repair of RC7 prompted by pre-submission review. It adds exactly two headline analyses:
1. a magnitude-matched uniform-activation null for the four incidence components;
2. a fixed-margin practical-equivalence test for pairwise Sørensen.

No new species trait or replacement mechanism is authorized.

## Article

**Title:** Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization

**Target:** Journal of Animal Ecology — Research Article

## Scientific authority

- manuscript: `MANUSCRIPT_JAE_V1_0.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC8_V0_1.md`
- cover letter: `submission/COVER_LETTER_JAE_V0_9.md`
- novelty audit: `submission/NOVELTY_AUDIT_V0_7.md`
- reviewer attack matrix: `submission/REVIEWER_ATTACK_MATRIX_V0_7.md`
- RC8 scope: `submission/RC8_SCOPE_UNFREEZE_V0_1.json`
- story decision tree: `submission/RC8_STORY_DECISION_TREE_V0_1.json`
- uniform-null contract: `NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1.json`
- uniform-null repairs: `NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1.json`, `_V0_1_2.json`, `_V0_1_3.json`
- uniform-null summary: `NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`
- Sørensen-equivalence contract: `NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1.json`
- Sørensen-equivalence summary: `NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json`
- figures: `figures_ecology_v1_0/`

## Core empirical result

The RC7 multiscale expansion remains:
- active stops β = **+0.384**;
- local alpha β = **+0.0794**;
- route gamma β = **+0.2859**;
- 92.0% of total incidence slope crosses at least one spatial/taxonomic boundary;
- 8.0% is within-core rearrangement.

## New RC8 result 1 — uniform activation is strongly rejected

The null preserves dry-side species × stop acoustic propensities and applies one common log-odds activation shift per matched pair, calibrated so expected wet incidence count matches the observed wet count.

Primary κ = 2:
- uniform-null mean boundary crossing = **80.9%**;
- 95% null interval = **74.2–87.4%**;
- observed = **92.0%**;
- four-component omnibus Monte Carlo P = **.000999**.

Component shares:
- corner: **36.9% observed vs 27.4% null mean**;
- spatial spread: **15.2% vs 22.9%**;
- taxonomic deepening: **39.9% vs 30.5%**;
- within-core: **8.0% vs 19.1%**.

Strong rejection is robust:
- κ = 1: P = .000999; null boundary 95% interval 73.8–86.3%;
- κ = 2: P = .000999; 74.2–87.4%;
- κ = 5: P = .000999; 75.9–89.8%.

Authorized interpretation:
> the observed incidence allocation is more taxonomically recruiting and less core-rearranging than a uniform increase in baseline acoustic propensities predicts.

Not authorized:
- the null rejection identifies a unique mechanism;
- heterogeneous thresholds are proven;
- rainfall causality.

## New RC8 result 2 — pairwise Sørensen is practically stable

Fixed post hoc margin: **±0.025 slope units**.

Primary:
- β = -0.000492;
- 90% CI = **-0.0107 to +0.00968**;
- PASS.

Exact consecutive years:
- β = +0.00215;
- 90% CI = **-0.00973 to +0.0140**;
- PASS.

Authorized interpretation:
> pairwise Sørensen differentiation is practically equivalent to zero change within the fixed margin in both samples.

This does not establish exact invariance or equivalence of every beta metric.

## Important separation

The uniform-null rejection is driven by the **four-component incidence allocation**.

The observed Sørensen slope itself lies inside the uniform-null Sørensen distribution:
- null mean = -0.00615;
- 95% null interval = -0.0130 to +0.00178;
- observed = -0.00049.

Therefore RC8 does not claim that an unusual beta response rejects uniform activation.

## Existing robustness retained

- 21/21 leave-one-state-out refits retain CI-positive footprint/alpha/gamma slopes;
- 3-day protocol-window primary sensitivity strong-passes;
- hearing/noise/wind, traffic and MassNoiseIndex sensitivities agree;
- exact consecutive-year analyses retain the main multiscale signal;
- activation geometry remains falsified and demoted.

## Promotion gate

- [x] RC8 scope recorded before analyses
- [x] uniform-null contract frozen before endpoint readback
- [x] implementation repairs recorded before successful endpoint readback
- [x] story decision tree frozen before successful uniform-null readback
- [x] uniform activation strongly rejected under κ=1,2,5
- [x] Sørensen equivalence passes primary and exact-year samples
- [x] v1.0 manuscript created
- [x] RC8 SI created
- [x] RC8 cover letter created
- [x] RC8 novelty and reviewer audits created
- [x] RC8 Figure 2 created
- [ ] RC8 scientific-package QA passes
- [ ] RC8 anonymous DOCX QA passes
- [ ] merge RC8 candidate to main
- [ ] create release/jae-v1-rc8 and promote submission/jae-v1
- [ ] freeze RC8 story after promotion

## Human metadata still unresolved

Final authors, affiliations, corresponding author details, CRediT, funding, acknowledgements, Conflict of Interest, Statement on Inclusion, all-author approval, archive license and DOI remain finalization-stage inputs.
