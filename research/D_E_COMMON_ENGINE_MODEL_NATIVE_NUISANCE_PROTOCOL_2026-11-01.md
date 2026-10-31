# Frogcs D+E common-source mechanism comparison — 80-year finite-N nuisance pilot (2026-11-01)

## Scientific purpose

ONE paper: empirical macro third-guild conditional association (B), followed by ONE combined D+E trophic/vegetation mechanism analysis. The E long-run population consequences should not become an unrelated second mechanism claim. Instead, compare trophic structures while dispersal mode and count scale are nuisance assumptions, and extract model-native contrasts and demographic outcomes from the SAME original biological execution.

PR146 D: original 120-day seasonal predation + 80-year delayed cohort recurrence, 12 structures ×256 hypothetical LHS biological-rate draws, four model-native signs OS− OV− SV+ OSV+, canonical plant prior sensitivity.
PR149–155 E: same predation and annual conditional means WITH newly added binomial completion/survival, Poisson recruitment, integer 8-patch ring movement, true N=0→positive reoccupation. This is NOT the separate PR147 seven-stage pedigree ABM. Deterministic PR146 homogeneous/off replay is exact, but individual finite-N stochastic trajectories are not deterministic replays.

## Source-locked original model design — first pass

Use immutable PR155 scientific-source commit 19d45ffb833e2970aff8d88de101736aee289d26 and import original seasonal/annual/finite-N source without editing the kernels.

- Original fixed LHS rate IDs 0,4,8,12 from 256 exploratory *hypothetical* biological rate vectors. Same attack, growth, rho, conversion, juvenile/adult survival and 2/3y maturation per θ across every nuisance/net contrast.
- Source biological contexts original and D_first_S_overtakes. Both have D arrival0/S arrival20; the latter changes S growth and D aquatic duration together, and is NOT an isolated arrival-order intervention.
- Two main-legal plant inputs SF1_DF0_DS0_L1 and SF0_DF0_DS1_L0. A plant refuge whose predator edge is absent is functionally inactive.
- Reverse predator flag OFF only: original source F-completed→emerging D has zero time overlap in these two contexts, so its ON counterpart is response-equivalent and not an independent draw; the PR148 third timing context *can* activate FE.
- Six directed predator networks, paired at same θ: all_active (SF,DF,DS,SD), SF_only, no_SF, no_DF, no_DS and all_off. This allows source-equivalent edge-ablation tests, rather than selecting an edge by optimizing different rates.
- Nuisance movement modes off, recruits, carryover, both EXACT as original finite_n_source_cohort_bridge, not PR147 larval/adult migration. Fixed annual integer-conserving ring transfer fraction .15 across 8 synthetic patches.
- Nuisance count-per-density scale q=3 or q=12, balanced by design, NO measured natural animal population size. External immigration OFF. Four original RNG labels 101–104 per model cell; patches/corners/years are not independent RNG samples.

## Model-native POM from the SAME model runs

For each structure×θ×network×q×movement×seed, compute:
- Beginning-of-season F aquatic cohort density averaged over synthetic patches and years 61–80, at every original 2×2×2 factorial vertex in V, S supply and D supply.
- Source orthogonal contrasts OS,OV,SV,OSV using original PR146 four_contrasts; retain both raw F_B and log1p(F_B). log1p is mandatory when F can be truly zero; it is NOT numerically identical to original PR146 log(F_B).
- Accepted four signs target −,−,+,+ only as source-MODEL-NATIVE pattern feasibility, not actual site fit.
- SAME execution year80 occupied frog patches, exact local N=0→positive reoccupation and local extinction, with movement ON versus OFF compared at same original source structure, θ, q, network and seed. RNG labels pair treatments but random streams are not pathwise synchronized across movement modes.

Report exact acceptance by context×plant×trophic network, under each q/mode/θ, as well as equal balanced average over illustrative nuisances and source rate draws. Marginalizing a nuisance does NOT prove robustness. Stratified ranks must be reported, including any sign reversals or instability. Four fixed θ samples cannot estimate an ecological prior.

## Field-model distinction

The observed 4,248-site, 28-species macro dataset has six continuous statistics: O×S,O×V,S×V,O×S×V and low-/high-S subset correlations on GLOBAL ranks, two SDM backgrounds and 56 spatial-block/999-resample covariance. Earlier site-POM found 0/132 original candidate response surfaces within all six descriptive 95% marginal intervals. Site environmental suitability and adult CallingIndex are NOT the model D/S source density and juvenile F cohort. There is NO validated F_B-to-adult-calling observation process.

This first pilot IS NOT a field-conditioned posterior ABC or a forecast. Full field ABC requires exactly the SAME structure×θ×q/mobility site-emission model, six site-level effect magnitudes with covariance, an explicit independently justified or labelled proxy observation map, and absolute adequacy. If none fits, report NO_FIELD_CONDITIONED_DEMOGRAPHIC_PREDICTIONS.

## Hard gates and status

1. Original source biology, complete unique 8 vertices, θ identity and actual network edge-control source tests.
2. Real 4-year source smoke and q/mode mass/nonnegative integer checks, but no 4y result called biological evidence.
3. Genuine source 80y runs for ALL 2 q ×4 modes ×two 2-seed shards, four original rates and all six networks.
4. Independent artifact audit must check all rate×plant×context×network×q×mode×seed source vertices, old true reoccupation event count and source seasonal consistency.
5. Preserve all negative and positive matched effects; update PR156 Results only after genuine 80y audit passes. PR158 is independent Draft stacked on PR156; no original main or PR146–155 code/data mutated.

### Limits

- q, .15 annual transfer and biological rate priors illustrative; q6/q9 post hoc from PR155 are a distinct prior sensitivity, not evidence of invariance.
- Selected D_first context couples growth and D duration; do not call it change in species arrival order.
- Model-native 2×2×2 signs do not have same quantitative estimand as measured macro site-level correlations.
- Original deterministic and stochastic finite-N source models use same conditional hazard/annual mean but different stochastic sampling assumptions; no pathwise numerical equality claimed.
