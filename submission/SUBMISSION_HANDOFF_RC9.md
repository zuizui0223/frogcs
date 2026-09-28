# JAE submission handoff — RC9 cross-continental depth release candidate

## Article

**Title:** Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization

**Target:** Journal of Animal Ecology — Research Article

## Current authority

- `main`
- `release/jae-v1-rc9`
- `submission/jae-v1`

RC8 remains the frozen fallback on `release/jae-v1-rc8`.

## Scientific authority

- manuscript: `MANUSCRIPT_JAE_V1_1.md`
- Supporting Information: `SUPPORTING_INFORMATION_JAE_RC9_V0_1.md`
- cover letter: `submission/COVER_LETTER_JAE_V0_12.md`
- novelty audit: `submission/NOVELTY_AUDIT_V0_9.md`
- reviewer attack matrix: `submission/REVIEWER_ATTACK_MATRIX_V0_9.md`
- story freeze: `submission/RC9_STORY_FREEZE_V0_1.json`
- cross-continental unfreeze: `submission/RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1.json`
- cross-continental contract: `CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1.json`
- cross-continental decision tree: `submission/RC8_CROSSCONTINENTAL_DEPTH_DECISION_TREE_V0_1.json`
- cross-continental summary: `CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json`
- North American uniform-null summary: `NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json`
- Sørensen-equivalence summary: `NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json`
- figures: `figures_ecology_v1_0/`
- title-page template: `JAE_TITLE_PAGE_V0_7.template.md`
- metadata template: `submission/SUBMISSION_METADATA_TEMPLATE_V0_6.yml`
- human-finalization guide: `submission/HUMAN_FINALIZATION_RC9.md`
- citation template: `submission/CITATION_V0_4.cff.template`

## Question spine

- **Q1:** does recent-rain activity expand the realized community, and is active-unit taxonomic deepening directionally consistent across independent North American and Australian systems?
- **Q2:** within fixed North American routes, is species × stop allocation distinguishable from magnitude-matched uniform activation?
- **Q3:** does expansion materially erode local pairwise-Sørensen differentiation?

## New RC9 result — cross-continental taxonomic deepening

Frozen North American result:
- active-stop richness β = **+0.0794**;
- 95% CI = **+0.0231 to +0.1357**.

Frozen Australian FrogID validation:
- 40,754 recordings / 1,623 ERA5 cells / 13,148 recorders;
- excess richness = species richness − 1;
- β per 1 SD increasing log dry-spell exposure = **−0.08176**;
- 95% CI = **−0.09816 to −0.06535**;
- P = **1.54 × 10^-22**.

Sensitivities:
- recorder-clustered CI = **−0.09490 to −0.06862**;
- within-ERA5-cell β = **−0.09984**, 95% CI **−0.11822 to −0.08146**.

Secondary depth endpoints:
- ≥3 species OR = **0.8458**, 95% CI **0.8115–0.8815**;
- excess beyond two species β = **−0.04833**, 95% CI **−0.05997 to −0.03668**.

Frozen decision: **STRONG PASS**.

Authorized wording:
> Cross-continental consistency in rainfall-associated taxonomic deepening within already-active acoustic units across independent North American and Australian monitoring systems.

Not authorized:
- worldwide/universal response;
- pooled or equal US–Australia effect sizes;
- identical mechanisms across continents;
- FrogID replication of fixed ten-stop matrix geometry.

## North American matrix geometry retained

Primary κ=2 uniform-activation null:
- expected boundary crossing = **80.9%**;
- 95% null interval = **74.2–87.4%**;
- observed = **92.0%**;
- four-component omnibus Monte Carlo P = **.000999**.

Component shares:
- corner: **36.9% observed vs 27.4% null**;
- spatial spread: **15.2% vs 22.9%**;
- taxonomic deepening: **39.9% vs 30.5%**;
- within-core: **8.0% vs 19.1%**.

## Practical non-homogenization retained

Pairwise Sørensen:
- primary β = −0.000492; 90% CI **−0.0107 to +0.00968**;
- exact-year β = +0.00215; 90% CI **−0.00973 to +0.0140**;
- both inside fixed post hoc ±0.025 margin.

## Historical threshold reconciliation

The old NAAMP activity-conditioned ≥2-species result remains:
- OR = **0.988**;
- P = **.402**.

RC9 does not erase it. The common US–Australia signal is **continuous/deeper taxonomic multiplicity**: ~71% of the NAAMP alpha slope lies beyond the second species, and the Australian ≥3 and beyond-two endpoints are strongly rain-associated.

## JAE package metrics

- manuscript: ~**7,759 words**
- title-page template: ~131 words
- combined proxy: ~**7,890 / 8,500**
- abstract: ~**322 / 350**
- cover letter v0.12: ~**355 / 500**
- keywords: 8
- references: alphabetical

## Completed scientific gates

- [x] external-validation unfreeze committed before Australian continuous-depth readback
- [x] response/model/sensitivity contract frozen before readback
- [x] story decision tree frozen before readback
- [x] Australian workflow run 36388273135 success
- [x] cross-continental decision STRONG PASS
- [x] RC9 candidate QA run 36389086419 success
- [x] v1.1 manuscript and RC9 SI created
- [x] RC9 story freeze created
- [x] main / release/jae-v1-rc9 / submission/jae-v1 aligned on the same scientific authority
- [x] archive-DOI finalization preserves NAAMP, FrogID and AmphiBIO provenance
- [x] RC9 canonical package QA on main/release/submission
- [x] RC9 anonymous v1.1 DOCX QA
- [x] RC9 canonical submission QA
- [x] RC9 JAE compliance QA
- [x] final RC9 review-package artifact generated

## Latest verified RC9 artifacts

- canonical review package: `frogcs-jae-rc9-review-package`, artifact ID **10956272327**
- anonymous v1.1 DOCX package: `frogcs-jae-v1-1-rc9-anonymous-docx`, artifact ID **10955682513**
- canonical submission QA run: **36390487764** — success
- RC9 scientific package QA runs on main/release/submission: **success**

## Human metadata still unresolved

Final authors/order, full institutional addresses, corresponding-author contact details, multi-author contributions where applicable, funding, acknowledgements, Conflict of Interest, Statement on Inclusion, all-author and relevant-institution approval, originality/legal confirmations, archive license and final DOI remain human finalization inputs.
