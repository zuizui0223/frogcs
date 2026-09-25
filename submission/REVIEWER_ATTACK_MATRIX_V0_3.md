# Reviewer attack matrix v0.3 — activation-decomposition revision

| Likely attack | Current answer | Status |
|---|---|---|
| Rainfall effects on frog calling/richness are old. | Agreed. Raw rain association is context; the contribution is empirical decomposition of participation versus residual association, plus independent continental replication. | Addressed |
| P(>=2 | >=1) still rises under independent activation. | Agreed. The manuscript explicitly withdraws the old stronger inference. NAAMP rain effect on P(>=2 | >=1) is null (OR 0.988, P=.402). | Addressed |
| Shared environmental response versus residual association is not a new concept. | Agreed; Royan et al. 2016 and Swallow et al. 2016 are now cited. Novelty is empirical application and dissociation in large-scale frog acoustics. | Addressed |
| Temperature may explain the NAAMP rain effect. | Joint rain+temperature: rain OR=.942, P=1.71e-4. With nonlinear DOY: OR=.946, P=5.44e-4. | Addressed |
| H3 omitted the shoulder main effect. | Hierarchy-corrected model gives beta=-.0480, P=.0698; four-window sensitivity P=.628. Original H3 remains unsupported and is not upgraded. | Addressed |
| H4 network null conflicts with temporal-compression story. | Temporal-compression story has been removed. H4 null is now concordant evidence for activation without pairwise rewiring. | Addressed |
| Your new independence diagnostic is post hoc. | Explicitly labelled reviewer-motivated post-opening; contract was frozen before its own fit and cannot replace original decisions. | Qualified |
| Plug-in independence probabilities are estimated from the same 10 stops. | Stated as a limitation; pairwise excess-covariance and pre-existing network H4 provide concordant sensitivities. | Qualified |
| FrogID version/source is inconsistent. | Submission identifies the exact SHA-pinned ALA dr14760 snapshot and Dataset 7.0 temporal scope; GBIF DOI remains the logical resource identifier. | Addressed |
| FrogID eventTime offset handling was wrong for some records. | Outcome-blind audit found 151/40,754 hour and 6 date mismatches; frozen timezone-aware repair changed OR only .852822→.852945 and within-cell beta -0.04265→-.04262. Repaired values are now submission values. | Addressed |
| FrogID conditional design proves synchrony. | No longer claimed. FrogID validates only the event-level one-versus-multiple pattern. | Addressed |
| DaysSinceRain contains sentinel/outliers. | Publisher range 0–180; audit found no numeric out-of-range values. Only 11 numeric records exceed 30 days. | Addressed |
| “Prospectively specified” is unverifiable. | ANALYSIS_PROVENANCE_V0_1.md records public commit SHAs and timestamps for contract freezes preceding corresponding runs. Post-opening diagnostics are labelled separately. | Addressed |
| NAAMP stops mix space and time. | Explicit limitation: a 5-min stop is both a spatial station and temporal window; the paper no longer calls the response a pure temporal-niche metric. | Addressed |
| NAAMP primary effect is tiny/borderline. | Reported exactly; complete-10 p=.058. Paper relies on cross-system direction, adjusted rain robustness, within-space persistence and mechanism decomposition rather than primary p alone. | Addressed |
| The study is causal. | No. Observational language retained throughout. | Hard boundary |

## Strongest current claim

> Recent rainfall is associated with broader multispecies acoustic participation across independent frog monitoring systems; standardized NAAMP decomposition finds no detectable strengthening of residual co-calling associations after marginal activity is accounted for.
