# frogcs — high-tier macro→mechanism single-paper claim / figure audit (2026-10-31)

**Editorial authority:** [new macro-first English manuscript](MACRO_TO_MECHANISM_HIGH_IMPACT_MANUSCRIPT_2026-10-31.md) and [high-tier first-shot plan](FROGCS_PUBLICATION_PORTFOLIO_AND_SUBMISSION_DECISION_2026-10-31.md). The earlier five-figure pulse-first ledger is superseded; previous git revisions preserve its historical content.

## I. Exact source denominators and what is not evidence

| Source and data unit | Source evidence | Main text role | Unacceptable interpretation |
|---|---|---|---|
| **4,248 acoustic listening locations** | [Main 2026-10-26 macro report](../research/FROGCS_MACRO_ANALYSIS_FINAL_REPORT_2026-10-26.md) and [original manuscript](../research/manuscript/TWO_PART_MANUSCRIPT_DRAFT_2026-10-26.md) | **MAIN empirical question** | 4,248 physically independent ponds; directly measured adult frog abundance, larval predation or reproductive success |
| **28 source-modelled potential guild taxa** (Anura15, Caudata7, Odonata6) | GBIF occurrence-derived SDMs and GloBI candidate evidence, 30 candidates with 28 meeting modelling eligibility | Environmental suitability in macro patterns | All potential species present at sampled acoustic locations; direct nymph density or true local interaction |
| **4,040 strictly prior calling site comparison pairs** | Main fixed network matched pairs; +27.68 percentage points historical calling | Secondary empirical context | Individual return / site fidelity or recruitment |
| **3,907 prior-year water-eligible matched pairs** | Satellite water *conditional detection frequency* −1.481 points | Secondary site hydrological context | Direct pond inundation duration, area-specific water persistence or a predation condition |
| **3,600 biological process structures**; **20×24 followup** | [original mechanism report](../research/manuscript/FINAL_MECHANISM_COMPARISON_2026-10-27.md) | **MAIN mechanism feasibility / failure test** | 3,600 independent ecological hypotheses or fitted empirical ecological models; one-of-24 as a posterior |
| **source 120-day +80year finite-N model** | [Original source PR #146–155](https://github.com/zuizui0223/frogcs/pulls) and [q3/6/9/12 verified source](https://github.com/zuizui0223/frogcs/blob/research/SF-population-scale-intermediate-q6-q9-20261031/research/SF_PREDATION_Q3_Q6_Q9_Q12_12SEED_SOURCE_VERIFIED_RESULT_2026-10-31.md) | Mechanism's conditional prediction and population-scale counterexamples | Explaining local NAAMP adult calls, actual S→F mortality or measured frog demographics |
| **RC6 historical rainfall / spatial concentration** | [old source manuscript](../paper/manuscript.md) and [author's main source editorial decision](../research/MACRO_FIRST_EDITORIAL_DECISION_2026-10-26.md) | **ONE short Introduction motivation only** | Abstract headline, main Results, Figure 1, independently replicated ecological evidence, or a second submission |

Both the current macro and historic RC6 share the NAAMP monitoring programme. **No independent acoustic replication** should be inferred. Uniform and target-group are two specifications of the same GBIF occurrence sources.

## II. Claims for the only four main figures

### Figure 1 — Third-guild conditionality (macro principal result)

- Pooled odonate suitability vs frog strong-calling rho: **−0.095 uniform / −0.086 target-group** (whole region).
- Low/high pond-breeding Caudata suitability stratum rho: **+0.101 / −0.284** uniform and **−0.004 / −0.183** target-group.
- High-minus-low difference: **−0.385 [−0.509,−0.240]** and **−0.179 [−0.328,−0.029]**, with route-group resampling.
- **Supported:** contextual difference in correlation strength persists across the two backgrounds. **Not supported:** positive-to-negative sign flip under both backgrounds; direct predation; within-pond mechanism.
- **High-tier unresolved gate:** disentangle between-region shared climatic/geographic suitability versus within-route variation and survey detection/effort. Current within-route result is weaker. Original source code/outputs are authoritative, no post hoc selection of best geographical subset.

### Figure 2 — Landscape vegetation, site history and hydrological eligibility

- Whole-region 3km model O×Caudata **−0.166 [−0.229,−0.108] uniform / −0.086 [−0.151,−0.023] target-group**.
- O×V **−0.087 [−0.124,−0.048] / −0.064 [−0.115,−0.014]**.
- S×V **+0.058 [+0.015,+0.101] / +0.046 [−0.022,+0.109]**.
- O×S×V **+0.037 [+0.008,+0.068] / +0.027 [−0.024,+0.073]**. **Not robust across original source background/within-route/radius**.
- Historical same-physical-site calling difference **+27.68 points [25.07,30.17] /4,040 matched pairs**; water detection frequency **−1.481 points [−2.601,−0.294] /3,907 eligible pairs**.
- Historical calling is not individual field philopatry; satellite detected-water frequency is not original site hydroperiod or seasonal salinity. These are a distinct site-environment analysis, not adjustments that remove all confounding from the main three-way relationship.

### Figure 3 — Original process-model feasibility and negative evidence

- Original catalogue **3,600** unique process structures; **20 candidate configurations ×24 common sensitivity contexts**.
- Winner 1479 and reduced1455 matched three target pairwise directions and hazard/survival in **only 1/24 contexts**. Not observational fitted likelihood or valid unique mechanism selection.
- Observed macro O×S×V 3-way **+0.037** uniform; source model candidate **−0.0482 at coarse 3-level rank grid / −0.0104 at fine 21-level grid**. **Full macro pattern not reproduced**.
- Candidate model's direct and indirect pathways, vegetation refuge, nonlinear odonate capture have source justification but do not establish actual field interactions. Distinct source predictors (supplies, refuge multiplier and juvenile hazards) vs macro predictors (SDM suitability, EarthEnv 3km vegetation and adult calling).
- **High-tier unresolved gate:** define observation-to-process mapping or a genuinely discriminating prediction. Preserving the failure is essential to avoid a fabricated full-fit narrative.

### Figure 4 — Demographic conditionality and finite-N limitations

- Original source **120-day stage-specific predation +80-year lagged recruitment**, synthetic eight-ring-patch movement fraction .15, model-native end-of-year80 F occupied-patch count, not adult CallingIndex.
- In original rateID12+rho(ID0) high synthetic recruitment / immigration OFF and q3, S-larva→F-larva edge removal eliminates strict low-growth positive / high-growth negative movement effect; **S→F-only preserves** it. This is model-native **conditional necessary and sufficient for strict sign criterion**, not nature.
- q population count-per-density scale is arbitrary; strict sign reversal over two fixed plant-input settings with active S→F: **q3 2/2, q6 1/2, q9 0/2, q12 0/2**. Test 12 RNG seeds per frozen condition. q6/q9 follow q12 findings (exploratory).
- Only **1/4 hypothetical process-rate vectors** showed original S-growth-induced strict reversal. With immigration OFF, rho×conversion is a **product** (structural non-identifiability): not separate independent biological mechanisms.
- In the SF-only network, the nominal vegetation mechanism protecting salamanders from odonates is **inactivated** if odonate→salamander predation is removed. Two input plant configurations are not independent tests of two fully active plant pathways.
- F-completed→emerging-D reverse predation FE is stage-nonoverlapping and zero in the finite-N two-context subset; it is active in the third developmental context of PR148 and not comparable to the PR147 individual ABM.
- **High-tier unresolved gate:** source population q scale and process rates lack field calibration; model does not map to adult calling.

## III. One manuscript, not a results catalogue

**Authoritative flow:** macro conditioned contrast → vegetation/environment/history patterns → stage mechanism screen including mismatch → scale- and recruitment-limited alternative demographic outcomes.

**What gets demoted:**
- RC6 full old 4,236 wet/dry comparisons and within-taxon concentration: Introduction's idea history and provenance only.
- Early PR146 rate screens, late q grids and every per-shard technical test: SI/provenance, not five or ten extra Results.
- Large numbers of synthetic return events (hundreds of thousands) as if independent tests: SI receipts only, never ecological sample size.
- After-results selected mechanism labels or q thresholds as field validated general ecological processes.

## IV. High-tier editorial go/no-go

| Gate | Minimum for ambition | Current status |
|---|---|---|
| **G1 / field-context discrimination** | Show whether macro contrast remains beyond geography/shared environment/survey effects, with robust within-region or held-out variation | **NOT ESTABLISHED**. Existing within-route weaker, both-background regional difference supported |
| **G2 / observation-to-process mapping** | Compare ecological model and measured macro coefficient on a justified common process/observation scale, including observed positive three-way and background sensitivity | **NOT ESTABLISHED**. Model currently wrong-sign three-way; no real co-pond predator density |
| **G3 / broad theory/independent prediction** | One testable principle whose predictions generalize to relevant biological-rate/population ranges and independent data | **NOT ESTABLISHED**. Current q3 necessary/sufficient sign pattern breaks with q/biological rate |

**Working journal ambition** (official verified 2026 criteria): [Nature Ecology & Evolution](https://www.nature.com/natecolevol/content) stretch, [Ecology Letters](https://onlinelibrary.wiley.com/page/journal/14610248/homepage/ForAuthors.html) first-shot development goal if gates are addressed, [Global Ecology and Biogeography](https://onlinelibrary.wiley.com/page/journal/14668238/homepage/productinformation.html) strong macro-focused target otherwise. These are **alternative sequential destinations for the same manuscript**, not parallel or split papers.

## V. Real submission state

[High-tier macro-first draft](MACRO_TO_MECHANISM_HIGH_IMPACT_MANUSCRIPT_2026-10-31.md) now has one Abstract, Introduction, Materials & Methods, Results, Discussion, Conclusion and four-figure design. **No actual Figures1–4 were produced yet.** No article has been submitted, reviewed, accepted or authorized by all coauthors. Original code, raw data and PR #146–155 source outcomes unchanged. Target-specific final figure, SI, reference, author, code/data policy and submission QA remain to be done.
