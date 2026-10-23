# NAAMP vegetation and frog acoustic community hierarchy — species-pair identity after conditioning on richness

**2026-10-23, executed real NAAMP × NWI macroecological study.** This is a post-hoc, nonpredictive observational analysis on the SAME original USGS NAAMP 2001–2015 acoustic monitoring archive and original response-blind USFWS 250-m mapped wetland polygons, not independent sample replication, new literature review or experimental vegetation manipulation. The central JAE RC6 paper, Supporting Information and `main` remain frozen.

## Biological result

Across the original monitoring region, **mapped emergent-wetland/PEM sites show more acoustically detected frog taxon units** and larger equal-effort multi-stop species pools. However, **the identities of frog taxon pairs co-detected together across those PEM sites do not show a globally robust additional pattern once richness at every stop, each taxon's 10-stop attendance, and the existing route-heldout NWI habitat-affinity null are preserved.**

The distinction matters ecologically: more frogs *by acoustic taxon units* at vegetation-associated sites does not itself establish that mapped vegetation reorganizes a pairwise animal community interaction network.

## Exact original source and conditional network test

- Original source: 7,848 standardized NAAMP ten-stop nights; USFWS NWI 12-geometry-shard, 5,147 physical-site verified crosswalk, 6,236 full NWI+stop-condition ten-stop nights across 499 physical routes/20 States. Original GIS source gate [#39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- Use the original route-held-out NWI+PEM taxon-specific environmental models trained in [#39516056663](https://github.com/zuizui0223/frogcs/actions/runs/39516056663), and original previously screened eligible resolved frog taxon pairs. The original original-checkerboard matrices are exactly **3,659 any-call route-nights/478 routes** and **1,766 strong-call/398 routes**; each original C-score was reverified against immutable run diagnostics.
- Test only route-nights with **≥2 PEM-positive and ≥2 PEM-unmapped stations within mapped NWI wetland footprint**. This yields **2,112** any-call and **1,014** strong-call mixed environment matrices. Source reference subsets are not silently expanded/replaced.
- Candidate *taxon-pair labels* fixed from original 127 any-call and 57 strong-call fitted edges. New geography-only/null-variability coverage yields **120** and **55** tested edges, respectively. All taxon complexes remain represented in the original source matrix margins even though only resolved taxa are used for candidate pair-identity tests.
- For each matrix, the previous **199-draw weighted Curveball** sampler uses the opposite-route-fold species NWI weights; each taxon's observed 10-stop detection count and every stop's full species richness are **exactly fixed**. Original original route-run date/vegetation flags fixed. Mean accepted feasible move ratio ≈0.692 any-call / 0.677 strong-call.

**Mathematical negative control:** with the stop richness margins fixed, the *number of all-taxon co-detection pairs* at PEM or nonPEM stops is fixed by Σ C(richness_stop,2). It CANNOT be tested as though it varies under the null. The tested statistic therefore changes only with **which taxon pair** is colocated, not with total acoustic species-pair counts.

For a given pair p, measure within-wetland PEM co-detection rate minus nonPEM rate on a same survey-run; subtract the original crossfitted species NWI-weighted fixed-margin expectation. Average over each original same-pair coactive mixed run. A single global score T is the average **squared** identity-specific residual across all preeligible pairs. Compare it to 199 full fixed-margin matrix draws aggregated over the same source matrices, using leave-one-null-draw-out centring.

**Critical geographic correction:** the same physical monitoring route is repeatedly visited. A separate 4,999-draw **whole-physical-route vector sign-flip** transforms the complete multi-species residual profile of each route together; this preserves correlation among source survey nights within each route and among its original taxon pairs. It assumes approximate symmetry of independently sampled route-level null residuals, not actual randomization of vegetation. A robust main ecological call requires BOTH fixed-margin Monte Carlo and route-level null comparisons plus geographic fold direction checks.

## Executed, source-verified results

| Whole-community statistic | Any-call CI≥1 | Strong-call CI≥2 |
|---|---:|---:|
| Source matrices with mapped PEM group comparison | **2,112** | **1,014** |
| Original fitted taxon pairs carried to new contrast | **120 of 127** | **55 of 57** |
| Source routes represented in whole-route null | **269** | **223** |
| Global observed mean squared edge residual T | **0.00093739** | 0.00079856 |
| Original independent-matrix fixed-margin null mean T | 0.00059224 | 0.00062465 |
| Ratio observed / matrix-null mean | **1.583** | 1.278 |
| Matrix-null Monte Carlo upper-tail plus-one P | **0.005** | 0.120 |
| Whole-route signflip null mean T | 0.00086494 | 0.00076257 |
| **Whole-route signflip P** | **0.3276** | **0.3844** |
| Edge residual signs agreeing between geographic route folds | 54/112 (**48.2%**) | 21/48 (**43.8%**) |
| Pre-locked joint robustness verdict | **not supported** | **not supported** |

CI≥1 observed mean-square identity-specific network deviation exceeds the fully fixed-margin independent-run comparator and both original geographic folds individually exceed their descriptive null mean. **BUT** the route-blocked inference does not support a landscape-wide stable PEM-conditioned pair-identity network excess, and edge signs do not replicate consistently by geographic fold. Thus calling the individual-run P=.005 a confirmed biological change to interspecific interactions would be misleading.

The established original per-edge PEM screen (2 candidates/121 any-call edge tests, 0/57 strong) already found both individual PEM moderators to fail stricter geographic/temporal robustness. The new global all-pair statistic likewise does not rescue those selected individual pairs. Ten largest absolute pair deviations are **descriptive examples only**, not newly significance-tested biological effects, and remain available in the aggregate file for diagnostic follow-up.

### What survives as a positive ecological finding?

**Vegetation-associated acoustic enrichment itself survives.** The earlier independent *analysis endpoints* on the same archive (not independent external samples) yielded:
- local detected taxon richness: PEM +0.27150 taxa/stop (same-night comparisons, 388 routes);
- adjusted local richness: PEM +0.23777 taxa/stop (499-route FE adjusted habitat/temperature/noise model);
- same-effort 2–5-stop community gamma: PEM +0.33184 taxa (286 routes);
- **within NWI-mapped wetland stops only**: PEM +0.29837 expected taxa in matched pools (281 routes);
- taxon contribution distributed: **39/48** monitoring taxon labels positive and nine negative (not 39 independent species-significance tests);
- for any calls CI≥1, 62.6–67.9% of the local adjusted PEM count difference can be algebraically attributed to additional taxon units beyond the first at a stop in the previous joint woody/PEM model; strong-call partition differs;
- prior vegetation×richness covariance mainly at same-night stop scale (PEM positive), with a negative State-level covariance (descriptive scale-dependent sign reversal).

These robust local/pooled *taxon-count* findings are **separate from** global partner-identity network statistics and do not entail detectable PEM-driven partner rewiring.

## Biological hierarchy and claim status

| Level | Ecological inference possible from current data |
|---|---|
| Mapped habitat (NWI emergent/woody/wetland) | 250m habitat polygon categories; proxy for structure, not direct observed 2001–15 plant cover |
| Local frog activity | Positive PEM–acoustic richness association, both calling thresholds, repeat-route uncertainty accounted for |
| Taxon pool gamma and nestedness-resultant | More taxon units in equally sampled PEM wetland sites; descriptive compositional nestedness component |
| Taxon-pair identity | Previously identified species-pair-specific fixed-margin acoustic residuals; **new global PEM-specific network reorganization not route-robust** |
| Irreducible biological three-species interactions | Not supported/identifiable: fish, predatory insects, frogs are not co-observed in a causal experimental design |

The reported difference between naïve repeated-run and route-vector sign-flip reference distributions **could reflect clustered/persistent route-context dependence and different null assumptions**; it does not prove a particular route memory or interaction mechanism. Two geographically held-out route folds show excess *magnitude* but not stable *sign* of pair deviations. No causal vegetation or frog–frog interaction inference is authorised.

## Workflow audit, diagnosed and repaired

1. Complete 199-draw scientific source analysis **actually succeeded** in [Actions #39895380126](https://github.com/zuizui0223/frogcs/actions/runs/39895380126), producing full result [artifact 12476157985](https://github.com/zuizui0223/frogcs/actions/runs/39895380126/artifacts/12476157985). That run was marked overall `failure` only because the last QA script referred to a **nonexistent JSON field**, `eligible_mixed_PEM_pair_labels`, rather than the actual `included_original_labels_with_20_mixed_nights_10_routes_5_null_variable_nights`.
2. The original full scientific workflow's QA field name was fixed, without changing scientific code or refitting environmental effects. To avoid needless reexecution of the expensive original 199-draw computation, its self-push trigger was removed; script changes still trigger full QA, and manual dispatch remains supported.
3. The original output JSON was pinned **unchanged**, including all 199-draw numeric results, in `exploration/NAAMP_PEM_CONDITIONAL_GLOBAL_PAIR_IDENTITY_AGGREGATE_2026_10_23.json`. A dedicated independent validation workflow fetched that immutable original result artifact, checked byte-equivalent parsed `modes` values against the versioned output, verified original population and all null results, and completed successfully: [Actions #39895990777](https://github.com/zuizui0223/frogcs/actions/runs/39895990777). This is **source-artifact readback QA, not a second independent biological replication**.

Code: `exploration/run_naamp_pem_fixedmargin_pair_network_global_v0_1.py`. Research contract: `exploration/NAAMP_PEM_FIXEDMARGIN_PAIR_IDENTITY_GLOBAL_SPEC_2026_10_23.md`. Scope limited to this exploration branch; original main JAE RC6 manuscript, SI, submission and release remain unchanged.
