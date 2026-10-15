# From hydric state to ecological configuration: landscape and external-test plan v0.1

**Created:** 2026-10-14  
**Status:** DISCOVERY-LED FUTURE DESIGN / NOT PREREGISTERED CONFIRMATION. The NAAMP soil outcomes and interactions were already inspected on 2026-09-30. This plan freezes the *next question* but cannot retrospectively turn prior NAAMP checks into independent hypothesis tests.

**Submission rule:** The JAE `main` manuscript, Figures, SI, scientific bundle, and original claim hierarchy remain frozen. This file is not a submission change request.

## Biological question

> Do broadly shared shallow-soil wetting conditions alter **whether/how far** frogs call, while persistent species × site context and terrestrial habitat connectivity constrain **which sites** express that calling?

Three distinct hypotheses should not be silently combined:

- **H-additive (presently favoured as a descriptive fit):** route-scale soil-water change relates to strong calling / spatial depth; strictly prior species × SiteID history separately predicts which stops host strong calling. The interactions may be zero.
- **H-gating (previously *not* supported in two NAAMP primary tests):** positive hydric change specifically amplifies historical-site targeting within the species × route event, rather than simply increasing the number of stops calling.
- **H-terrestrial-connection (untested for the key configuration residual):** terrestrial habitat around and between listening stops allows more shared species-specific activation than expected from independent stop responses and first-order site-history probabilities. Effects are larger for independently classified terrestrial-dependent taxa.

The full claim requires testing **configuration conditional on the amount of calling**, not merely fitting calling intensity.

## 0. Evidence boundary and non-repetition rule

Read `research/STATE_HISTORY_HYDRIC_EVIDENCE_AUDIT_2026-10-14.md` first. In particular:

- soil × remembered-SiteID primary interaction: unsupported, β=0.0102, CI [-0.0088, 0.0292];
- soil × prior-strong breadth primary depth interaction: unsupported, β=0.0729, CI [-0.0201, 0.1659];
- **both main axes** in the joint depth model: supported;
- higher-order JAE concentration residual: not explained merely by separate marginal predictions;
- 0.25° ERA5 `swvl1` cannot represent which individual 300-m listening stop was moist.

Do not rerun these same endpoints with new radii, guild thresholds, rain windows, named species subsets or interactions chosen after outcome inspection to obtain a positive gate.

## 1. Two lanes with separate claims

### Lane A — NAAMP macro-heterogeneity audit (post hoc, exploratory)

Use the original frozen NAAMP data and original `q` comparator only if exactly reproducible. This can characterize **which taxa / routes contribute** to the residual, but **not** confirm a new mechanism independently.

- Population: use the exact eligible strictly prior SiteID-history population for the focal comparator (2,916 pairs, 439 routes, 20 States); report any loss under geographic, landscape or taxonomic metadata gates. **Do not silently substitute the 4,236-pair full set or 585-route study size**. A verified response-blind 2026-10-14 coordinate preflight found 1,028/1,183 public routes with exactly 10 unambiguous coordinates, and a SHA-verified Runs/Stops-only reconstruction now establishes **2,422/2,916 pairs and 358/439 routes in all 20 states** after the strict 10-coordinate gate (see `research/NAAMP_TERRESTRIAL_C1V2_EVIDENCE_GATE_2026-10-15.md`). These are geometry/source eligible only, not forest raster-verified (see `research/NAAMP_TERRESTRIAL_GEOMETRY_PREFLIGHT_RESULT_2026-10-14.md`).
- For each taxon × route × eligible event, calculate cross-stop residual-pair products using the same `e = y - q` and denominator `sqrt(q(1-q))` conventions as the archived residual-dependence diagnostic. Preserve all eligible route events and their candidate taxon support, including events without positive outcomes.
- These residual-pair summaries are **not the focal global conditional concentration coefficient**; call the new target `residual_stop_dependence`, and report direct conditional-concentration simulations separately if feasible.
- Estimate latent variance attributable to taxon, route, taxon × route and route × event (where identifiable). Use partial pooling and account for very unequal cluster sizes, repeated pairs/routes, and uncertain per-cell residuals. Do not infer a taxon trait from its noisy unshrunk coefficient.
- Descriptive result: a variance partition and out-of-block prediction for which species × route events have positive residual dependence. Compare predictive gain against a no-heterogeneity baseline; do not report only the largest variance component and call it a cause.
- Covariate sources/predictions must be registered **in a separate amendment before the new target residual summaries are inspected**; all of Lane A remains exploratory at the manuscript-programme level.
- A true species main effect and a stable species × route interaction need multi-route species coverage; lack of overlap is **non-identifiable**, not evidence of a zero biological interaction.

### Lane B — independent repeated fixed-site monitoring (needed for evidential upgrade)

Acquire a dataset that has:

1. Stable physical listening locations with site IDs and coordinates across events;
2. Uniform visit/recorder effort and explicit acoustic zero opportunities;
3. Repeat pre-event and post-event sampling and a consistently measured strong-chorus state (or a validated intensity analogue);
4. Site-level terrestrial habitat description; preferably direct measurements of shallow upland soil-water content and wetland depth at survey times;
5. Sufficient species × site × event overlap to estimate both within-species spatial breadth and historical recurrence.

**STOP if these conditions cannot be met.** Do not substitute a collection of opportunistic detections and claim a ten-stop fixed-site replication.

## 2. Two linked likelihoods; do not conflate activation and allocation

For an independent repeated panel, freeze outcome and sampling eligibility before inspecting the new acoustic responses.

**Magnitude model (A):** predict strong calling (e.g. CI>=2) and number of strongly calling stops from hydric state change, known meteorology, sampling schedule, prior route propensity and taxon. Use a split trained on different routes and an earlier period; report held-out log loss and calibration. Positive predictive gain would not show that soil moisture explains the joint spatial configuration.

**Placement model (B), for *where* at fixed species-specific depth only:** for each taxon × event with `k` strongly calling stops, condition exactly on observed `k`. Let `H_j` indicate a strictly-prior strong-chorus site; let `T_j` describe site terrestrial cover and `L_{jk}` the prespecified between-site land-connection matrix. Compare conditional subsets of fixed size `k` with a model that can add:

- historical-site log odds `H_j`;
- `H_j × Δsoil_event`, the **gating** hypothesis;
- terrestrial cover at the listening site;
- species-guild × terrestrial-cover interaction;
- pairwise connectivity contribution `sum_{j<k} active_j active_k L_{jk}` within each event, conditional on exact `k`.

An event-constant route soil score **has no main-effect contrast within an exact-k placement likelihood**: it can only affect conditional placement through a site-varying interaction, or affect the magnitude model.

Use strictly historical `H_j` defined before every scored event. Estimate/fit from geographically and temporally held-out training folds. Predeclared null generators preserve event activity amount, trained species propensities and prior-site information. These per-species exact-`k` comparisons assess **placement / recurrent-site alignment** and possibly forest-linked pair selection at an observed depth. They **cannot test high-order concentration** because fixing every species-specific `k_s` algebraically fixes `C = sum_s choose(max(k_s-1,0), 2)`. The original plan's earlier suggestion that exact-`k` placement alone could reproduce the focal JAE concentration is **withdrawn**.

**Species-allocation model (C), separate from exact-`k` placement:** for a whole pair × route event, keep (i) total observed positive wet cells `K` and (ii) the number `N` of wet-positive species that were dry-route silent fixed, **without fixing `k_s` per species**. Start from the original cross-fitted, species×site `q` matrix at the SAME CallingIndex threshold. Model a **generic** within-taxon pair-dependence term `theta_generic * sum_s sum_{j<l} y_sj y_sl` first, then add forest-patch-specific pair energy `theta_link * sum_s sum_{j<l} y_sj y_sl L_jl` and separately frozen guild moderation and/or wetness×historical-site terms. Compare held-out gains over the generic pair model, not only over independent Bernoulli. If the forest graph links every stop pair, generic and forest-pair energies are collinear and cannot be distinguished: mark those cases non-identifiable rather than attributing generic concentration to forest. Conditional normalizers and simulations use the implemented exact dynamic-programming `research/scripts/conditional_kn_concentration_kernel_v0_1.py`. Evaluate `C` and held-out matrix log likelihood versus the exact-(K,N) baseline, geographically blocked at **route**.

This new exact-(K,N) conditioning defines **a distinct, explicitly post-hoc estimator**; it is not the JAE's original regression/simulation-conditioned β=1.6503 / residual=0.2969 and may have different sampling/error properties. The existing JAE SI already contains a separate exact-N,K structural diagnostic. No new NAAMP environmental mechanism is confirmed by writing this code.

The independent validation would separately examine:
(a) distribution of `C` under allocation model C,
(b) near-versus-far residual dependence, and
(c) excess recurrent-strong-site alignment under placement model B.

A high predictive score for marginal calling **without reproducing the conditional configuration** is a **mechanism insufficiency result**. CI>=1 fitted baseline probabilities must not be reused to model a CI>=2 or CI=3 site-placement vector; train/out-of-block-score a baseline for the SAME acoustic threshold. The exact-k kernel has a fail-closed threshold identity check.

## 3. Landscape sources and biological moderators

### Primary static landscape source (metadata-first)

- Use one internally consistent official **NLCD** release for the historical NAAMP interval; do not mix C1.0 and C1.2 classes/confidence without an independently verified harmonization.
- Draft retrospective exposure-year rule: use the **preceding completed calendar year** (survey_year - 1) for site context; freeze this against the exact analysis clock before viewing new acoustic outcomes. Annual NLCD C1.2 was modelled and published retrospectively in 2026 and could involve imagery after historical survey years, so neither this rule nor a labelled-year layer alone authorizes a **prospective no-future-information** or causal claim.
- Within-site terrestrial habitat: **300-m stop-centred buffer**, predeclared forest classes 41/42/43 of the selected NLCD C1.2 categorical raster. This is a listening-context proxy, **not** a 300-m terrestrial habitat buffer measured from a mapped pond edge. Record no-data, water, developed classes, the source's confidence field and eligible pixel fraction. Do not infer categories from WMS display colours.
- Between-stop forest-patch connectivity: use a predeclared **route-wide raster envelope** (e.g. route convex hull plus 1 km) and an independently chosen 30-m forest pixel adjacency rule; compute actual same-patch connections between the ten 300-m forest neighbourhoods, accounting for corridors outside each individual buffer. This is a landscape proxy, **not proof of dispersal or a single breeding population**. A real 2026-10-14 geometry-only gate found median 7/45 pairs with overlapping 1-km circles and 116/1,028 routes with a fully linked buffer-overlap graph, but **buffer overlap must never substitute for a mapped forest-patch connection**. Avoid treating overlapping circles as independent area replicates.
- Note the historical caveat: verified source coordinates do not establish physical stability of every listening station. Fail closed on known relocation/uncertainty.

### Prespecified taxon axis

- Create a **source-cited, response-blind** guild crosswalk for adult terrestrial dependence vs persistent-water association, with a separate `unknown/complex` class. Apply identical codings at all sites.
- Exclude unresolved species-complex acoustic labels from the primary guild contrast unless an authoritative mapping exists independent of outcomes.
- Primary directional prediction: forest-cover/connection association is stronger for terrestrially dependent species than for aquatic-associated species. This tests habitat moderation of **configuration**; a guild main effect in a calling regression does not suffice.
- Account for phylogenetic relatedness in a sensitivity if a sufficiently resolved matching phylogeny exists. A model with species fixed effects cannot separately identify time-invariant guild **main effects**, but can estimate guild × within-species varying environmental exposures; static route connectivity main effects are not identified with route fixed effects.
- Predeclare a geographic blocking scheme because forest, rainfall climatology and taxon composition covary by State/region.

No selection of buffers, source releases, guild assignments or species subsets based on acoustic effect direction.

## 4. Independent tests and failure branches

**Primary decision family for future independent fixed sites:**

- H-additive supported: `Δsoil` predicts event magnitude or breadth out of block, strictly prior site use predicts conditional placement, and soil × historical-site interaction is compatible with zero.
- H-gating supported only if the predefined **primary** conditional site-history × soil coefficient is positive with complete 95% confidence interval above zero and the model improves held-out conditional placement over additive context.
- H-terrestrial-connection supported only if prospectively fixed forest-patch connectivity improves geographically held-out **exact-(K,N) whole-matrix log score and the conditional distribution of C**, with an independently specified guild contrast, and does not fail prespecified lag-profile diagnostics. Fixed-species-k placement tests are a separate secondary outcome. A mere vegetation coefficient predicting pooled calling is insufficient.
- No macro mechanism supported: positive marginal predictor associations persist but conditional high-order configuration remains unexplained, or data are non-identifiable / too sparse. **Report and stop.**

Cluster uncertainty by the geographically appropriate route/unit; evaluate temporal transfer separately. Report multiplicity, calibration, effect sizes and uncertainty, negative controls for recording effort/protocol, missingness, route/guild overlap and whether one region drives the result.

## 5. FrogID: useful, but **not** a drop-in external replication

FrogID's available opportunistic recording-level detections do not automatically provide fixed ten-stop events, standardized acoustic non-detection opportunities or the NAAMP `CallingIndex` response. Therefore:

- an effort-controlled recording-level moisture association may be a separate Australian **context/triangulation test**, if its denominator, dates, species identities and spatial precision are verified;
- it **cannot** by itself replicate NAAMP's conditional multi-site concentration, exact-k site-selection or recurrence of full choruses;
- if denominator/effort and event granularity cannot be audited, classify this lane as `NOT_TESTABLE` rather than manufacturing pseudozeros or renaming richness as spatial depth.

## 6. Immediate workflow

1. Preserve the evidence audit and original Actions receipts; leave `main` and the submitted JAE paper alone.
2. Retain the verified response-blind 1,028-route, exactly-ten-SiteID source gate and its artifact; determine the **actual intersection** with the frozen 439-route paper sample without changing outcomes. The 2026-10-15 official ScienceBase and WMS source-only test is **blocked for original C1V2 raw pixels** despite confirmed catalogue entries; secure an independently source-verified original C1V2 categorical+confidence raster pair without mislabelling WMS or older C1V0 before conducting real forest extraction, and candidate independent fixed-site programme eligibility inventory. Do not inspect new response outcomes at this stage.
3. Freeze guild taxonomy, land-cover year/geometry, contrasts and analysis code on an independent revision **after** feasibility and **before** any new outcome readback.
4. Run one prespecified independent analysis. Publish supported and negative components together; do not switch outcomes to rescue a gate or connectivity story.

**Conceptual payoff if verified independently:** magnitude of a short reproductive-acoustic pulse and the spatial arrangement of its expression are distinct ecological dimensions; broad hydric conditions may modulate the former, whereas spatially recurrent habitat and possibly terrestrial landscape connections shape the latter. The archive currently supports the **distinction**, not the full proposed causal mechanism.
