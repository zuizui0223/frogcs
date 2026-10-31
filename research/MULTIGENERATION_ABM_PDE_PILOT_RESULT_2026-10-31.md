# Initial 20-year synthetic reversal experiment (2026-10-31)

**Executable evidence:** [GitHub Actions #41157576060](https://github.com/zuizui0223/frogcs/actions/runs/41157576060), SUCCESS. Eight structural tests passed. The fixed default experiment simulated 8 synthetic periodic patches, 7 stages, ABM replicates with seeds 101–104 and deterministic stage-density PDE, with and without F-adult→D-emerging predation. All uncalibrated rates were fixed before inspecting trajectories. **These are hypothetical model responses, not population observations or parameter estimates.**

## Numerical response to switching on the adult frog→emerging dragonfly edge

All numbers are (reversal ON − reversal OFF), in synthetic individuals or density units, aggregated over eight patches. ABM values average four independent stochastic runs, each contrast using the same starting population and same seed labels, not pathwise identical noise.

| Years after intervention | ABM ΔD adults (4-seed mean) | PDE ΔD adults | ABM ΔF adults (mean) | PDE ΔF adults |
|---:|---:|---:|---:|---:|
| 1 | −63.75 | −44.09 | −15.00 | +1.31 |
| 2 | −132.25 | −126.87 | −23.50 | +17.38 |
| 5 | −511.00 | −512.55 | +273.75 | +339.37 |
| 10 | −968.50 | −904.48 | +1558.50 | +1514.68 |
| 20 | −731.25 | −691.37 | +2113.75 | +2063.15 |

ABM year 20: the reversal-ON arm had **zero occupied dragonfly patches in all 4 seeds** relative to 8 still occupied in reversal-OFF; a strong synthetic regime, not evidence that such local extinction is likely in nature. The deterministic PDE retains small positive densities after depletion and cannot express finite-individual stochastic extinction in the same way. The F effect even changes sign across the first two years among ABM seeds, illustrating why immediate and multigeneration outcomes should not be conflated.

The predation deaths on D emergence are concentrated early (PDE year 1: 51.72; year 5: 99.23; year 20: 0.001). Later losses of D adults are largely **carryover through reduced emergence and reproduction**, not direct late-year capture events. This depends on the model's closed eight-patch ring, no external immigration and uncalibrated attack intensity `a_fe=0.12` per adult per model year.

## Scientific boundary

The original frogcs cohort model **already** allowed an F postmetamorph→emerging D predation edge and annual recruitment feedback. The contribution of the new implementation is individual parentage, stochastic encounters, local extinction, stage-dependent dispersal and a same-reaction PDE benchmark. It is **not** a first demonstration of multiyear trophic feedback.

The 2023 observation by Beranek et al. (DOI 10.1002/ecy.4108) reports the trophic reversal for *Litoria aurea* and *Anax papuensis*, but not its population-level effect size or prevalence across wetlands. These coefficients are not estimated from that study. Adult salamander predation is not included without a pair- and stage-specific evidence audit.

**Important next diagnostic:** the default rate is intentionally illustrative and creates severe D collapse. Follow-up *post-pilot* parameter and mobility sensitivity must test whether the response persists with weaker reversal and recruitment/movement buffers, without presenting the current default as a robust biological prediction. The counterfactual and every numerical test remain in the artifact; they were not tuned to NAAMP's acoustic coefficients.
