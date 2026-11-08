# R5 preflight: original field and source geometry verified; observer-power inference NOT YET RUN

**2026-11-08.** Successful [preflight Actions #42445478134](https://github.com/zuizui0223/frogcs/actions/runs/42445478134), original G4 source run [#42173236906](https://github.com/zuizui0223/frogcs/actions/runs/42173236906). R5 prospectively frozen design is [here](R5_VIRTUAL_ECOLOGIST_OBSERVABILITY_FROZEN_PROTOCOL_2026-11-08.md). This receipt contains **source/geometry diagnostics only**; simulated observer replicates: **zero**. Do not claim this study has identified a real natural mechanism or explained a real negative prediction.

## Actual original-source numerical results

| Checked item | Result |
|---|---:|
| Original NAAMP listening sites | **4,248** |
| Original completed visits, with actual site-specific opportunities | **63,180** |
| Original strong-call events | **36,554** |
| Original spatial blocks | **56** |
| Original sites with positive mapped landscape flooded vegetation | **506** |
| Source model arms | **00** (both vegetation pathways OFF); **11** (both ON) |
| Eight-corner mechanism surface projection max residual (uniform; OFF/ON) | **4.11e−15 / 4.88e−15** |
| Eight-corner mechanism surface projection max residual (target group; OFF/ON) | **9.21e−15 / 8.83e−15** |
| Odonata suitability-rank Spearman, uniform vs target-group | **0.62545** |
| Pond-breeding Caudata suitability-rank Spearman, uniform vs target-group | **0.73634** |

**Exact interpretive point:** G4 trilinear interpolation of original model aquatic-cohort log responses in O,S,V is a polynomial in 1,O,S,V,OS,OV,SV,OSV. The source response is therefore **algebraically contained in the unrestricted empirical interaction basis**. Observing only those O/S/V covariates cannot establish uniquely that the source food-web mechanism is the wild causal explanation, **regardless of adding more calls or sites**. This does not imply that no association is detectable or that a fixed source template can never beat an additive model.

**Model both-vegetation-functions ON minus OFF, original 256×3 source-mean log aquatic-cohort model response evaluated on field rank geometry** (not an observed abundance change):

| Conditional interpolation world | Mean ON−OFF model log cohort | Across-site SD | Residual SD after projecting contrast onto frozen flexible additive field design |
|---|---:|---:|---:|
| Uniform O/S rank world | **−0.0205203** | **0.0604433** | **0.0176520** |
| Target-group O/S rank world | **−0.0167656** | **0.0498298** | **0.0152724** |

The averaged original source responses produce a **small remaining nonadditive spatial signal in *log cohort units*** under this particular exploratory original rate/source set. No conversion to adult calling exists; even an apparently small signal could map to a large or small call effect depending on an **unknown observation link**. Therefore do not convert those SDs to an empirical power percentage.

The input variation between original SDM backgrounds is real (rank correlations above), but neither background measures predator density. Mapped landscape vegetation is not a pond-level refuge assay. Similarly, original 2012–2016 independent USGS G18 same-survey association supports a cross-method co-recording, **not** a source likelihood for synthetic log larval abundance → NAAMP call probability.

## Gate decisions

- Original G14 field inputs and historical 56-block folds: **PASS**.
- Original G4 00/11 source requirements and eight-term algebra: **PASS**.
- Mechanism shape uniquely identifiable relative to unrestricted empirical interactions: **NO, mathematical aliasing confirmed**.
- Source 11−00 contrast entirely zero across site geometry: **NO; nonzero but small remaining log-cohort variation**.
- Virtual ecologist observation-power comparison (100 preregistered replicates per scenario, both backgrounds): **NOT RUN**.
- Conditional causes of original G5/G14 field failure identified: **NO**.
- A practical empirically calibrated 80%-power sampling design: **NOT AVAILABLE**.
- Original source R1 and G12–G18 manuscript claims modified: **NO**.

**Scientific next operation only if authorized to complete R5:** implement the preregistered complete synthetic observer experiment, present all positive/negative source scenarios and spatially heldout comparisons, and retain these identification limits. Do not inject this preflight as an empirical biological confirmation in the manuscript. The existing frozen Ecology Letters author package/PR #183 remains a separate authority.
