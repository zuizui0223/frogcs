# frogcs — unified manuscript source/claim and figure audit (2026-10-31)

**Scope:** one integrated manuscript, not three submissions. [Working English manuscript](ONE_INTEGRATED_FROGCS_MANUSCRIPT_DRAFT_2026-10-31.md). This audit preserves the original numerical authorities and flags any cross-study interpretation that remains unsupported.

## A. Source hierarchy / no silent independent replication

| Evidence unit | Exact authoritative files | Dataset grain | Not independent from |
|---|---|---|---|
| RC6 pulse spatial allocation | [archived manuscript](../paper/manuscript.md), [original RC6 release](../submission/RC6_RELEASE_RECEIPT.md), [focal endpoint](../revision/CURRENT_ENDPOINT_PAPER_SPINE_V0_2.md) | 4,236 paired wetter/drier route runs ×53 taxa; 2,916 prior-history-eligible comparisons | Macro NAAMP sample: some source monitoring records are shared. Not independent ecological replication |
| Macro calling×guild suitability | [final macro numerical report](../research/FROGCS_MACRO_ANALYSIS_FINAL_REPORT_2026-10-26.md), [main integrated study](../research/manuscript/TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md) | 4,248 physical acoustic locations; 28 SDM species; 432 route components | RC6 uses same NAAMP programme but different filters, units and reference periods |
| Main stage-network screen | [final mechanism report](../research/manuscript/FINAL_MECHANISM_COMPARISON_2026-10-27.md) | 3,600 candidate configurations; 20 candidates×24 nuisance contexts | Later PR finite-N models share some original seasonal biology but use different outputs and assumptions |
| Finite-N/q stage model | [q3/6/9/12 verified report](https://github.com/zuizui0223/frogcs/blob/research/SF-population-scale-intermediate-q6-q9-20261031/research/SF_PREDATION_Q3_Q6_Q9_Q12_12SEED_SOURCE_VERIFIED_RESULT_2026-10-31.md), [source audit run](https://github.com/zuizui0223/frogcs/actions/runs/41202367237) | Original 120-day F/S/D trophic + 80-year delayed cohort model, 8 synthetic ring patches, 12 independent RNG seeds/fixed condition | Cannot be used as numerical fit or independent validation of adult NAAMP vocal activity |
| Frozen RC6 submission package | [RC6 readiness](../submission/SUBMISSION_READINESS.md), [October20 final source receipt](../submission/FINAL_INITIAL_SUBMISSION_RECEIPT_2026-10-20.md) | Source files and QA for a now-superseded JAE-formatted separate draft | The *single integrated* manuscript must be formatted and QA'd afresh |

The single manuscript does not imply a pre-existing independent natural-site dataset testing both acoustic pulse and actual larval predation at the same physical pond/time. No WFTS data were requested or analysed, and WFTS must not appear as external confirmation or a required gate.

## B. Claim ledger

| ID | Claim permitted in manuscript | Source/number | Qualification required |
|---|---|---|---|
| E1 | Rain-related chorus activity includes direct silent→strong states | RC6 original Results, 4,236 pairs, 53 taxa | The transition is observed CI0→CI2/3, not colonization or new adults |
| E2 | Within-taxon multi-site concentration exceeds first-order null | observed1.650 vs 1.353, residual0.297, P=0.000999, 2,916 history-eligible | Comparator represents species rainfall sensitivity, past physical-site propensity, dry persistence and matched expected incidence; sequential stops ≠ simultaneous calling or movement |
| E3 | Deep spread and earlier taxon-specific site targeting | third-and-later stops CI2/3 97.3%; β0.151 [0.129,0.173] | Study-specific conditioning and historical physical-site; not known individual site fidelity |
| E4 | Calling–odonate relation weak at regional scale | 4,248 sites, regional Spearman uniform−0.095/target-group−0.086 | Environmental suitability is not local nymph density; within-route weaker |
| E5 | Third-guild context changes the regional correlation | high−low caudate high−low uniform −0.385 [−0.509,−0.240], target-group −0.179 [−0.328,−0.029] | Backgrounds are same occurrence source; low stratum uniform +0.101 vs target-group −0.004, so do not claim robust sign flip |
| E6 | Landscape vegetation interactions are conditional | O×V −0.087/−0.064, S×V +0.058/+0.046, three-way +0.037 [+0.008,+0.068] / +0.027 [−0.024,+0.073] | Target-group S×V and both-area three-way uncertainties; 1-km EarthEnv summarized at 3km ≠ pond vegetation refuge |
| E7 | Physical sites with strong calls were used before | matched4,040; prior strong calling difference+27.68 pp [25.07,30.17] | Does not show true individual return, breeding success or larval survival |
| E8 | Previous year satellite water detection differs | matched3,907 water-detected eligible pairs; −1.481 pp [−2.601,−0.294] | Frequency conditional on detected water pixels is not pond hydroperiod; water area had no similarly clear difference |
| M1 | Some stage-structured networks can reproduce restricted directional contrasts | 3,600 source catalogue; finalist1/24 of common sensitivity conditions | Parameter search makes its occurrence no independent empirical validation |
| M2 | Model did not reproduce empirical three-way direction | empirical macro uniform positive +0.037, model coarse −0.0482 / fine −0.0104 | Distinct statistical predictors, so not a formal model likelihood rejection; report mismatch anyway |
| M3 | Species' arrival order was NOT isolated by early finite-N contrast | both contexts D arrival0/S arrival20; changed S growth0.014→0.030 and D aquatic duration40→60 | Historical name D_first_S_overtakes is a label, not actual arrival-order experiment |
| M4 | Single growth-factor sign reversal not general over rate IDs | growth sign reversal original rate ID0 yes, rateID4/8/12 no, among 4 hypothetical LHS draws | Synthetic rates not an ecological posterior; one of four selected vector classes |
| M5 | rho and conversion are structurally nonidentifiable when immigration OFF | local annual recruitment proportional to rho×conversion | Do not label two independently supported mechanisms; migration vs recolonization and environmental suitability are not equivalent |
| M6 | In selected synthetic q3/high-recruitment regime, S→F direct predation is necessary/sufficient for strict sign pattern | [PR #153 full edge audit](https://github.com/zuizui0223/frogcs/actions/runs/41200093960) | Required *for model-defined strict growth-dependent reversal*, not natural ecological necessity/sufficiency |
| M7 | q alters strict sign reversal | q3:2/2, q6:1/2, q9:0/2, q12:0/2 source plant inputs, 12seed each, high recruitment, OFF immigration | q6/q9 added after q12 failure; count per density unit arbitrary; one plant function inactive when D→S disabled |
| M8 | Original FE reverse predation is a null in PR149–152 two-context source | F completed day65; D emergence ends by day45/65; exact zero | PR148 third scenario D later, FE active; PR147 different individual ABM, do not generalize null |
| M9 | Reoccupation is not identical to long-run rescue | year-to-year exact integer0→positive return events, 3y persistence, year80 occupancy separately | No parent UID and no field colonization / acoustic observation process |

## C. Five-figure manuscript structure

1. **Fig1: short behavioural pulse**. Do not show independent-site movements; show sequential route stop sampling, original one focal comparator.
2. **Fig2: prior physical-site use and water detection**. Show β0.151 from RC6 and +27.68pp from macro as different measures; −1.481pp in different eligibility set.
3. **Fig3: modelled three-guild suitability and vegetation**. Report BOTH SDM backgrounds, high-v-low caudate heterogeneity, whole-region vs weaker within-route and uncertain three-way.
4. **Fig4: main 3,600 mechanism screen**. Include the one-of-24 conditional success and original observed-vs-model three-way sign discrepancy prominently.
5. **Fig5: finite-N stage/predation/recruitment/synthetic q boundary**. Keep q3,q6,q9,q12; all-active/SF-only/no-SF/no-predation; 12 independent source seed labels and floor/ceiling, no observed wetland demographic labels.

No figure files were rendered or validated at this stage. Source run artifacts and original output CSVs must be transformed into final resolution-appropriate figures later; never replace an absent original-data figure with a visually persuasive but ungrounded illustration.

## D. Journal and submission gate

Current first target: [Freshwater Biology Research Article](https://onlinelibrary.wiley.com/page/journal/13652427/homepage/productinformation.html), because it accepts freshwater behavioural, population, community, geographically broad and theoretically informed work. An ambitious alternative is [Journal of Animal Ecology](https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/aims-and-scope/read-full-aims-and-scope) if the one-paper novelty is defensible to a broad animal-ecology readership; existing JAE QA is for a **different earlier manuscript**. The same **one manuscript** may be submitted sequentially to an alternative journal following an editorial decision, never simultaneously to multiple journals.

**Pre-submission checks pending:** exact source and reference cross-check, Figures1–5, linked SI with all failures, source-data archive/code-access terms, author affiliations, funding, ethics/permissions if applicable, CRediT/COI statements, coauthor sign-off and fresh target-journal manuscript/format QA. **No journal submission has yet occurred.**
