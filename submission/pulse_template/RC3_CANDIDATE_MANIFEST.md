# Integrated multi-site manuscript — RC3 candidate manifest

**Candidate branch:** `candidate/jae-multisite-rc3`

**Source revision commit at candidate creation:** `4224bd13952a3876d71cdfdfe5e94482e4c1589b`

**Status:** scientific reframing complete; GitHub Actions release validation pending.

## RC3 scientific changes relative to RC2

RC3 implements three reviewer-facing repairs without adding a new same-data endpoint.

### 1. Principal comparator changed

RC2 foregrounded the exact N,K-conditioned exchangeable combinatorial diagnostic.

RC3 instead foregrounds the 2,916-pair comparator that includes:
- route-cross-fitted taxon-specific rainfall response;
- strictly-prior taxon × physical-SiteID history;
- dry-state persistence;
- pair-level wet-incidence magnitude matching.

Observed within-taxon concentration:
- β = **1.6503**

Principal comparator:
- predicted β = **1.3535**
- residual = **0.2969**
- null 95% interval = **−0.1319 to 0.1187**
- P = **0.000999**

Stronger sensitivity:
- held-out rain × local-history gate predicted β = **1.3323**
- residual = **0.3180**
- null 95% interval = **−0.1172 to 0.1255**
- P = **0.000999**

### 2. Exact N,K diagnostic demoted

The exact exchangeable diagnostic remains reported:
- raw β = **0.2439**, 95% CI **0.1474–0.3404**.

But it is explicitly secondary because it does not preserve:
- taxon-specific spatial breadth;
- habitat affinity;
- prior site use.

It is not the headline null and does not appear in the Abstract.

### 3. Public terminology changed

Current title:

**Rainfall-associated frog chorus activation shows within-taxon multi-site coherence and species-specific site recurrence**

The main manuscript contains no public use of the term “higher-order”.

Preferred terms:
- within-taxon multi-site concentration;
- within-taxon spatial concentration;
- multi-site coherence.

Historical analysis contracts/scripts may retain `higher_order` internally for provenance.

## Exploration boundary strengthened

The manuscript now states explicitly:
- the integrated multi-site result is post-opening and exploratory within NAAMP;
- cross-fitting prevents route leakage but is not independent confirmation;
- no unexamined NAAMP partition remains a genuine confirmation set;
- prospective external replication is required.

Frozen external confirmation specification:

`revision/PROSPECTIVE_EXTERNAL_REPLICATION_SPEC_V0_1.md`

External candidate work is isolated on:

`prospective/external-multisite-replication-v1`

and must not feed back into RC3 selection based on outcomes.

## Current files

- `paper/manuscript_pulse_template_v0_4.md`
- `paper/supporting_information_pulse_template_v0_2.md`
- `revision/INTEGRATED_RESULTS_V0_2.json`
- `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_2.md`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_3.md`
- `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_1.md`
- `revision/FIGURE_REBUILD_SPEC_V0_2.md`
- `revision/PROSPECTIVE_EXTERNAL_REPLICATION_SPEC_V0_1.md`

## Static validation completed before candidate freeze

- manuscript words: **7,443**
- abstract words: **343**
- main-manuscript occurrences of “higher-order”: **0**
- exact N,K result in Abstract: **no**
- principal comparator in Abstract: **yes**
- principal comparator precedes exact diagnostic in Results: **yes**
- principal comparator precedes exact diagnostic in Discussion: **yes**
- explicit no-untouched-NAAMP statement: **yes**
- explicit prospective external replication statement: **yes**

Figure 3 renderer was also locally executed successfully using the frozen figure data:
- SVG generated successfully;
- 300-dpi PNG generated successfully;
- principal species/history comparator appears first;
- exact N,K result appears only as a secondary annotation.

## Release gate still pending

Do **not** promote this candidate to `release/jae-multisite-rc3` until the current GitHub Actions runs complete successfully for:

1. `pulse-template manuscript QA`
2. `pulse-template submission pipeline`
3. current figure rendering/bundle generation

If any fails, repair on the revision branch and create a new candidate rather than silently moving this frozen candidate.
