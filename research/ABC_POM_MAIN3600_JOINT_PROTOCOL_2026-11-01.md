# Joint structure × rate ABC–POM of the original 3,600 main mechanisms (2026-11-01)

**Status:** executable, independent post-main research PR; the main manuscript and original frozen tables are unchanged. Results require successful source audit and GitHub Actions. Never treat a queued/running workflow as completed data.

## Questions

1. Does the previously reported **158 of 10,800** four-sign result reproduce from the **archived 194,400 original deterministic cells** without resimulating?
2. If model identity, stage timing and nuisance parameters are sampled **together before simulating**, what share of prior draws generate the four signs, and how do conditional acceptance rates vary among structural axes?
3. How sensitive are outcomes to raw vs log response and the original 5% survival screen? Is selecting model 1479 or identifying S→D as essential justified?

These questions are **not** empirical posterior inference. The source targets and the simulated quantities differ (real geographically modelled suitability × adult chorus vs synthetic aquatic F_B under supplied cohort densities). Sign-generation compatibility does not identify field trophic interactions.

## Precommitted ABC–POM experiment

**Prior proposal unit** is one tuple (catalogue model ID, stage context, attack, density retention, annual conversion, vegetation-strength multiplier, refuge ordering, size gate). Sample independent uniform categorical priors, without selecting the original 20 finalists.

| Variable | Synthetic prior |
|---|---|
| Structure | Uniform across all 3,600 IDs returned by unchanged final_mechanism_common.catalog() |
| Ontogenetic arrangement | Uniform across the 3 original CONTEXTS (including S arrival day 0) |
| Predator attack multiplier | Uniform on {0.5, 1.5, 3.0} |
| Annual density feedback rho | Uniform on {0.25, 0.50, 0.75} |
| Recruit conversion | Uniform on {2, 4, 8} |
| Vegetation effect strength | Uniform on {0.5, 1.0} |
| Refuge order | Uniform on {S, equal, D} |
| Size gate | Uniform on {none, 0.5} |
| Draws and RNG | 20,000, NumPy Generator seed 20261101, shard-invariant proposal IDs |
| Seasonal and annual dynamics | **Unmodified** original kernel; 40 years, final 10-year mean, half-day time step |
| Within proposal | 8 balanced corners: V={0,1}, S source={0.25,2}, D source={0.25,2} |

Eight corners × 20,000 proposals = **160,000 actual seasonal/annual scenario evaluations** (each integrated 40 years). Each full draw is constructed once from a precommitted RNG, and shard ID is determined from proposal ID, never by results. Multiple proposals can sample the same model ID; their rates and stage setting remain independently drawn. Workflows use eight shards in parallel, followed by a complete-ID aggregation check.

### Frozen four-direction statistic

For y(v,s,d) = log(mean aquatic F_B), with v,s,d in {0,1} after mapping each S and D source to low or high level, define:

- OS = mean over v of [y(v,1,1) − y(v,1,0) − y(v,0,1) + y(v,0,0)].
- OV = mean over s of [y(1,s,1) − y(1,s,0) − y(0,s,1) + y(0,s,0)].
- SV = mean over d of [y(1,1,d) − y(1,0,d) − y(0,1,d) + y(0,0,d)].
- OSV = [OS within V=1] − [OS within V=0], **not** the averaged OS.

Acceptance: **OS < −1e−6, OV < −1e−6, SV > 1e−6, OSV > 1e−6**, all four simultaneously. Raw F_B and minimum 5% survival are diagnostic sensitivities, never silently substituted as the primary outcome. This is categorical-summary rejection ABC with a zero/one kernel and an artificial prior; accepted structure shares are **not** field-calibrated posterior probabilities.

Unlike main's score(), the present criterion (i) uses eight source corners, (ii) is log-F_B only, (iii) includes OSV, and (iv) does not require four separate response scales, 18-cell rank regression or 5% survival. Consequently rankings need not match original model 1479. Note that reported 158 cannot be certified until source reproduction with the exact contrast definition is complete.

## Immutable provenance / run commands

Source main commit: 5e2f0a87c639df373fa2700b29403d2ab417a1cc. Frozen output directory: research/results/final_mechanism_20261027/.

On the repository root with NumPy, Pandas and SciPy installed:

~~~bash
python -m unittest discover -s research/scripts -p 'test_abc_pom_main3600.py'
python research/scripts/audit_main3600_direction.py
python research/scripts/abc_pom_main3600.py --draws 20000 --shards 8 --shard 0
# Repeat --shard 1 ... 7, preserving --draws/--seed; do not change priors.
python research/scripts/abc_pom_main3600.py --draws 20000 --shards 8 --summarize-only
~~~

Workflow: .github/workflows/research_abc_pom_main3600.yml. This records source audit tables, 20,000 prior rows, accepted parameter region, conditional acceptance rates and their Wilson Monte Carlo intervals as downloadable artifacts. It does not rewrite original main results. Separate audit reads every frozen screen source compressed file, checks exactly 194,400 rows/10,800 model-context units, and re-derives all signs.

## Interpretation safeguards

- First compare saved-source audit against reported **158**, explicitly explain any discrepancy in contrast standardization or conditioning. Mismatch must not be quietly relabeled as reproduced.
- Distinguish **prior share**, **conditional acceptance rate**, **accepted-draw share**, and **enrichment relative to prior**. Catalog IDs overrepresent some functional combinations; model-level acceptance does not imply ecological prevalences.
- Evaluate whether edge_SD=0 remains strictly impossible across sampled rates; frozen-rate "0%" alone was not proof of biological necessity.
- Do not infer a universal single winner from 20,000 draws over 3,600 IDs (mean 5.6 proposals per ID). Structural-axis contrasts and broad functional groups are more stable.
- Test alternative biologically justified prior laws and empirical observation mapping before calling accepted share an ecological posterior.
- Related PR #146 varies 108 function classes and rates over true 80-year simulation; it did not jointly sample all 3,600 models. PR #156 records real 4,248-site six-pattern/source mismatch. Keep distinct.

## Output boundary

Until workflow finishes, only the source design and executable protocol are verified. CI success verifies execution and numerical checks, not an ecological causal claim or source-to-observation calibration.
