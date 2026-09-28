# RC10 pre-submission review disposition v0.1

This memo records how the final pre-submission review of RC9 was resolved in RC10. It is an internal audit surface, not part of the submitted manuscript.

## Review issue 1 — FrogID was overstated as independent/external validation

### Concern

Earlier FrogID work had already shown a rain-associated multispecies signal. The later continuous excess-richness endpoint was therefore not a blind independent validation, and the NAAMP and FrogID estimators also differ.

### RC10 disposition

**Accepted and corrected.**

Current wording is **cross-dataset consistency / directional agreement**, not independent or external validation.

- NAAMP: matched wetter–drier route-stop analysis.
- FrogID: recording-level regression against standardized dry-spell exposure.
- Shared ecological estimand: taxonomic depth conditional on acoustic activity.
- Effect sizes are not pooled or treated as equal.
- Worldwide/universal generality is explicitly prohibited.

Current manuscript wording states that earlier FrogID work had already shown a positive multispecies result.

Status: **closed**.

## Review issue 2 — original uniform null may weaken species × stop persistence through shrinkage

### Concern

Hierarchical shrinkage toward species means could make stable species × stop cells too exchangeable and inflate expected within-core rearrangement. Dry-rare/rain-associated combinations could also be difficult for a dry-based null to generate.

### RC10 disposition

**Accepted and tested with a separately frozen stress test.**

Before endpoint readback, RC10 froze a persistence-preserving null:

- no species-level hierarchical shrinkage;
- dry-history cell-only Jeffreys-smoothed probabilities;
- pair-specific dry-state anchoring:
  - a = 0.50;
  - a = 0.75 primary;
  - a = 0.90;
- one common log-odds activation shift;
- expected wet incidence magnitude matched pair by pair;
- same observed four-component estimand and same 4,236 pairs.

Primary a = 0.75:

- observed boundary crossing = **92.0%**;
- null mean = **77.9%**;
- 95% null interval = **73.4–82.8%**;
- within-core = **22.1% expected vs 8.0% observed**;
- four-component omnibus Monte Carlo **P = .000999**.

Sensitivity:

- a = 0.50: omnibus **P = .000999**;
- a = 0.90: omnibus **P = .000999**;
- a = 0.90 boundary upper 95% bound = **82.3%**.

Frozen decision: **strong rejection under persistence anchoring**.

Therefore the allocation departure cannot be explained simply by the original shrinkage weakening persistent cell identity.

Ecological interpretation remains bounded: preferential activation of combinations rare under dry conditions is supported relative to the null; temporary/intermittently suitable wet sites are only a plausible discussion-level hypothesis.

Status: **closed**.

## Review issue 3 — “without practical homogenization” was the weakest title claim

### Concern

The ±0.025 Sørensen margin was chosen after the conventional coefficient was known, and the observed Sørensen slope is not unusual under the uniform-activation null.

### RC10 disposition

**Accepted and removed from the headline.**

Old title:
> Rainfall-associated expansion of frog active communities crosses spatial and taxonomic boundaries without practical homogenization

Current title:
> **Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts**

Sørensen is retained only as secondary bounded context:

- primary β = -0.000492;
- 90% CI = -0.0107 to +0.00968;
- exact-year interval also lies within the post hoc ±0.025 bound;
- observed Sørensen slope lies inside the original uniform-null Sørensen distribution.

The manuscript explicitly says that beta diversity is not what rejects uniform activation.

Status: **closed**.

## Review issue 4 — manuscript length

### Concern

RC9 approached the JAE Research Article word limit and carried too much robustness-method detail in the main text.

### RC10 disposition

**Accepted and compressed.**

Geographic-generalization and protocol-window Methods were shortened in the main manuscript, with full specifications retained in Supporting Information.

Current package metrics:

- manuscript ≈ **7,964 words**;
- title page ≈ **130 words**;
- combined proxy ≈ **8,094 / 8,500**;
- abstract ≈ **314 / 350**;
- cover letter ≈ **369 / 500**.

Current JAE compliance workflow passes.

Status: **closed**.

## Final scientific hierarchy

1. Recent-rain conditions are associated with spatial and taxonomic expansion of the behaviourally realized NAAMP frog community.
2. The four-component species × stop incidence allocation is more boundary-biased than the original magnitude-matched uniform-activation null predicts.
3. The same allocation departure survives a persistence-preserving null that strongly retains pair-specific dry species × stop identity.
4. NAAMP and FrogID show the same direction of active-unit taxonomic deepening, reported only as cross-dataset consistency.
5. Pairwise Sørensen is secondary context, not a headline discovery.
6. No unique mechanism, rainfall causality, demographic recruitment or worldwide universality is claimed.

## Submission decision

**RC10 is frozen for submission. No further ecological endpoint search is authorized without an editor/reviewer request or a documented implementation defect.**

Authoritative story freeze:
- `submission/RC10_STORY_FREEZE_V0_1.json`

Key robustness result:
- `NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json`

Current manuscript:
- `MANUSCRIPT_JAE_V1_2.md`
