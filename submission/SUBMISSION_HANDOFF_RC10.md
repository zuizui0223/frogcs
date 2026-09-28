# JAE submission handoff — RC10 persistence-null release

## Article

**Title:** Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts

**Target:** Journal of Animal Ecology — Research Article

## Current authority

- `main`
- `release/jae-v1-rc10`
- `submission/jae-v1`

RC9 remains the frozen fallback on `release/jae-v1-rc9`.

## Scientific authority

- manuscript: `MANUSCRIPT_JAE_V1_2.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC10_V0_1.md`
- cover letter: `submission/COVER_LETTER_JAE_V0_13.md`
- novelty audit: `submission/NOVELTY_AUDIT_V0_10.md`
- reviewer attack matrix: `submission/REVIEWER_ATTACK_MATRIX_V0_10.md`
- story freeze: `submission/RC10_STORY_FREEZE_V0_1.json`
- RC10 scope: `submission/RC10_SCOPE_UNFREEZE_V0_1.json`
- persistence-null contract: `NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1.json`
- persistence-null summary: `NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json`
- story decision tree: `submission/RC10_STORY_DECISION_TREE_V0_1.json`
- original uniform-null summary: `NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`
- cross-dataset depth summary: `CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json`
- figures: `figures_ecology_v1_0/FIGURE_1_METACOMMUNITY_EXPANSION_V0_1.svg`, `figures_ecology_v1_2/`
- title-page template: `JAE_TITLE_PAGE_V0_8.template.md`
- metadata template: `submission/SUBMISSION_METADATA_TEMPLATE_V0_7.yml`
- citation template: `submission/CITATION_V0_5.cff.template`
- human-finalization guide: `submission/HUMAN_FINALIZATION_RC10.md`

## Question spine

- **Q1 — expansion:** do recent-rain conditions expand spatial and taxonomic participation?
- **Q2 — allocation:** is the four-component species × stop allocation more boundary-biased than uniform activation predicts, including when the null strongly preserves pair-specific dry cell identity?
- **Q3 — consistency/context:** does active-unit taxonomic depth point in the same recent-rain direction in NAAMP and FrogID, and what happens to pairwise composition?

## Main RC10 result — allocation survives persistence-preserving null

Observed:
- boundary crossing = **92.0%**
- corner = **36.9%**
- spatial spread = **15.2%**
- taxonomic deepening = **39.9%**
- within-core = **8.0%**

Original κ=2 null:
- boundary mean = **80.9%**
- 95% interval = **74.2–87.4%**
- omnibus P = **.000999**

Persistence-preserving primary a=.75:
- boundary mean = **77.9%**
- 95% interval = **73.4–82.8%**
- corner = **28.6% expected**
- spatial spread = **19.3%**
- taxonomic deepening = **30.1%**
- within-core = **22.1%**
- omnibus P = **.000999**

Persistence sensitivities:
- a=.50 omnibus P = **.000999**
- a=.90 omnibus P = **.000999**
- at a=.90, boundary upper 95% null bound = **82.3%**

Frozen decision: **strong rejection under persistence anchoring**.

Interpretation:
> The allocation departure cannot be explained simply by hierarchical shrinkage weakening stable species × stop identity.

Temporary or intermittently suitable wet-site activation is discussion-level only; no mechanism is identified.

## FrogID wording

FrogID is **not** an independent/external validation claim.

The aligned continuous-depth result is treated as **directional cross-dataset consistency** because an earlier FrogID multispecies signal was already known.

- NAAMP active-stop richness β = +0.0794 [0.0231, 0.1357]
- FrogID excess-richness β per 1 SD dryness = −0.0818 [−0.0982, −0.0654]

No pooled effect size or worldwide generality claim.

## Sørensen position

Pairwise Sørensen:
- primary β = −0.000492
- 90% CI = −0.0107 to +0.00968
- exact-year also inside the post hoc ±0.025 bound

This is **secondary bounded context**, not a title-level discovery, because the margin was selected after the conventional coefficient was known and the observed slope lies inside the uniform-activation null distribution.

## JAE package metrics

- manuscript ~**7,964 words**
- title page ~**130 words**
- combined proxy ~**8,094 / 8,500**
- abstract ~**314 / 350**
- cover letter ~**369 / 500**
- keywords 8
- references alphabetical

## Completed scientific gates

- [x] RC10 scope frozen before persistence-null endpoint readback
- [x] persistence-null contract frozen before readback
- [x] title/story decision tree frozen before readback
- [x] workflow run 36396060661 success
- [x] strong rejection at a=.50,.75,.90
- [x] boundary-biased title gate passed
- [x] FrogID language demoted to cross-dataset consistency
- [x] Sørensen removed from title-level claim
- [x] robustness Methods compressed to SI
- [x] RC10 candidate QA success
- [x] RC10 merged to main
- [x] RC10 story freeze created
- [x] RC10 scientific package QA on main/release/submission
- [x] RC10 anonymous v1.2 DOCX QA
- [x] RC10 canonical submission QA
- [x] RC10 JAE compliance QA
- [x] final review package artifact recorded

## Latest verified RC10 runs and artifacts

- persistence-preserving null: run **36396060661** — success; artifact **10957954308**
- scientific package QA on submission authority: run **36398245492** — success
- anonymous v1.2 DOCX: run **36398245608** — success; artifact **10959337221**
- JAE compliance: run **36398245550** — success
- canonical submission QA: run **36398245570** — success
- canonical review package: `frogcs-jae-rc10-review-package`, artifact **10958853754**
- release-branch scientific package / DOCX / compliance runs also passed on the same authority HEAD

## Human metadata still unresolved

Final authors/order, full affiliations, corresponding-author details, contributions where applicable, funding, acknowledgements, Conflict of Interest, Statement on Inclusion, approvals, archive license and final DOI remain human finalization inputs.
