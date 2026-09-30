# Integrated figure rebuild specification v0.1

## Design principle

The figures must tell the frog-ecology story without requiring the reader to understand the null machinery first:

**silence → strong chorus → higher-order multi-site coherence → historical site recurrence → simple generators fail**

The old alpha/beta/gamma and boundary-allocation figures become supporting context rather than the visual spine.

## Figure 1 — Rain shifts the expressed chorus state

### Biological question
Does recent-rain change merely make existing callers louder/more detectable, or switch previously silent species × sites into substantial chorus states?

### Panels
**A. Matched-route schematic.** One ten-stop route shown in dry and wet surveys. Use the same physical stops. Encode one focal species with 0, CI1, CI2 and CI3 symbols. This is explanatory only, not a result panel.

**B. Baseline community expansion.** Forest plot for rainfall coefficients:
- active-stop count: 0.384 (0.240–0.528)
- active-stop alpha: 0.0794 (0.0231–0.1357)
- route gamma: 0.2859 (0.1646–0.4072)

**C. CallingIndex coefficient decomposition.**
- total CallingIndex slope = 2.8410
- 0→positive = 1.8549 (65.3%)
- already-positive intensity change = remainder
- within 0→positive, show 0→CI1 versus 0→CI2/3; CI2/3 = 1.6150 (87.1% of activation)

**D. Full-chorus endpoint.**
- full sample 0→CI3 β = 0.4406 (0.1136–0.7675)
- same observer + same physical SiteID β = 0.5141 (0.1008–0.9273)

### Source
- frozen RC11 headline response outputs
- `exploration/full-chorus-activation-v1/exploration/run_naamp_new_full_chorus_activation.py`
- final synthesis JSON for CallingIndex decomposition totals

### Message printed in figure
**Most rain-associated CallingIndex change enters from silence, and most new activation is already overlapping/full chorus.**

---

## Figure 2 — Recruited taxa show higher-order route-scale spatial coherence

### Biological question
After a taxon enters the wet-state route, is its extra spatial participation merely a first-order consequence of recruiting more taxa and more occupied stops, or is spread unusually deep within the same taxa?

### Panels
**A. Spatial-depth decomposition.**
Show observed rainfall coefficients:
- second stop: β = 0.132; not outside either primary null
- third+ stops: β = 0.473; outside both primary-null 95% ranges
- fourth+ stops: β = 0.363; outside null ranges

Overlay κ=2 uniform and a=0.75 persistence-preserving 95% null ranges.

**B. Higher-order conditional concentration.**
Explain the endpoint visually:
- for each route-new taxon, e = occupied stops − 1
- higher-order mass = choose(e,2)
- k=2 → 0; k=3 → 1; k=4 → 3; k=5 → 6

Plot:
- observed higher-order β = 1.524
- uniform-null prediction = 1.138
- persistence-null prediction = 0.784
- cross-fit species-response prediction = 1.198
- joint cross-fit species + strictly-prior site-history + dry-persistence prediction (2,916-pair subset): 1.353 vs 1.650 observed
- all conditional upper-tail P = 0.000999

Add a robustness inset:
- same observer + same physical SiteID: observed higher-order β = 1.817
- uniform prediction = 1.400; persistence prediction = 0.918
- both P = 0.000999

Annotate prominently:
**conditions on both recruited-taxon count and total extra-stop spread.**

**C. Route-topology corroboration.**
Show adjacent-stop-link rainfall coefficient:
- β = 0.419
- conditional on total extra-stop spread: P=0.000999 under both primary nulls.

Make clear that StopNumber adjacency is route topology, not exact geographic distance.

**D. Calling strength within third+ depth.**
- CI2/3 share of third+ coefficient = 97.3%
- CI1-only remainder = 2.7%
- same-observer + same-SiteID CI2/3 share = 95.4%

### Source
- `exploration/route-new-spatial-depth-v1/exploration/run_naamp_route_new_spatial_depth.py`
- `exploration/route-new-coherence-v1/exploration/run_naamp_route_new_coherence_conditional.py`
- `exploration/higher-order-spatial-coherence-v1/exploration/run_naamp_higher_order_spatial_coherence.py`
- `exploration/route-new-contiguity-v1/exploration/run_naamp_route_new_contiguity.py`
- `exploration/spatial-depth-chorus-v1/exploration/run_naamp_spatial_depth_chorus_decomposition.py`

### Message printed in figure
**At the same amount of first-order recruitment and spread, wet-state activity remains too deeply concentrated within the same recruited taxa even after cross-fitted species rainfall sensitivity and strictly-prior site history are added.**

---

## Figure 3 — Strong chorus placement follows a persistent species × site template

### Biological question
Does the route-scale coherence occur at arbitrary sites, or preferentially where the same species has previously formed strong choruses?

### Panels
**A. Recurrence context.**
Show descriptively:
- route-new incidence recurrent: 98.1% leave-pair-out; 98.9% strictly prior
- new CI3 any-history recurrent: 98.1%
- new CI3 same-SiteID recurrent: 90.4%
- strictly-prior same-SiteID recurrent: 82.6%

Label these **availability-sensitive descriptive shares**, not the inferential endpoint.

**B. Within-pair × species historical-site targeting.**
Coefficient plot:
- prior strong SiteID → wet CI2/3: 0.1511 (0.1291–0.1731)
- prior strong SiteID → wet CI3: 0.0778 (0.0619–0.0937)
- same-observer CI2/3: 0.1589 (0.1344–0.1833)

Annotate that comparisons are among the ten sites for the **same focal species and pair**.

**C. Rain-selective historical targeting.**
Coefficient plot:
- target-rain-advantage × historical CI3 targeting: 0.02449 (0.00700–0.04198)
- same-observer: 0.03067 (0.01331–0.04804)

Inset: mirror wet-as-target versus dry-as-target within the same matched pair.

**D. Inferential ladder.**
raw recurrence → same-site recurrence → within-pair × species targeting → directional rain-selective targeting

Use typography to distinguish descriptive from inferential evidence.

### Source
- `exploration/recurrent-activation-memory-v1/exploration/run_naamp_recurrent_activation_memory.py`
- `exploration/full-chorus-site-memory-v1/exploration/run_naamp_full_chorus_site_memory.py`
- `exploration/local-chorus-memory-v1/exploration/run_naamp_local_chorus_memory_targeting.py`
- `exploration/rain-selective-memory-v1/exploration/run_naamp_rain_selective_local_memory.py`

### Message printed in figure
**Spatially coherent strong chorusing is not placed arbitrarily: it preferentially reappears at species-specific physical sites with a prior strong chorus record.**

---

## Figure 4 — A nested null ladder localizes what simple explanations cannot generate

### Biological question
Can the pattern be generated by increasingly realistic combinations of independent species response and stable site history?

### Layout
Rows ordered by increasing ecological structure:

1. common uniform activation
2. dry-state persistence
3. cross-fit species-specific rain shifts
4. strictly-prior species × SiteID history
5. cross-fit species + prior local history + dry persistence
6. held-out rain × local-history gate

Columns:
- omnibus plus-one Monte Carlo P
- boundary-crossing share
- taxonomic-deepening share
- within-core share

For rows 1–2, show null intervals where available.
For the final row show:
- boundary: observed 0.921 vs null 0.814
- taxonomic deepening: 0.399 vs 0.316
- within-core: 0.079 vs 0.186
- P = 0.000999

Visually mark every rejection identically; do **not** make later nulls look like independent replications.

### Source
- frozen uniform and persistence-null outputs
- cross-fit species null contract/output
- prior-memory null
- joint species-memory null
- `exploration/crossfit-memory-gating-null-v1/exploration/FINAL_MECHANISM_SYNTHESIS_V0_1.json`

### Message printed in figure
**Adding transferable species sensitivity, local history and a held-out rain × history gate improves biological realism but still does not reproduce the observed chorus-state allocation.**

---

## Figure 5 — Broad within NAAMP, heterogeneous among states, narrower consistency in Australia

### Panels
**A. Higher-order taxonomic contribution concentration.**
Rank higher-order taxon contributions; annotate:
- 53 taxa total
- 25 positive
- 19 contribute ≥1% of positive mass
- top 1 = 18.8%
- top 5 = 54.2%
- HHI = 0.0855
- all leave-one-taxon-out totals positive

Optionally show the strong-activation concentration values (57 taxa, top1 13.9%, top5 49.2%, HHI 0.074) as a small corroborating inset.

**B. Geographic robustness.**
Leave-one-state-out strong-activation coefficient with 95% intervals.

**C. State heterogeneity.**
State-specific slopes plus random-slope population estimate:
- 13/19 positive point estimates
- 6/19 wholly positive CIs
- population β = 1.65
- state SD = 3.46

Make the visual distinction between **robustness to omission** and **homogeneity** explicit.

**D. FrogID scope panel.**
Show only the shared active-unit taxonomic-depth estimand:
- NAAMP wetter direction: +0.0794 (0.0231–0.1357)
- FrogID dry_z: −0.0818 (−0.0982 to −0.0654)

Do not place these on a common standardized-effect axis or imply equality.

### Source
- `exploration/strong-activation-species-concentration-v1/exploration/run_naamp_strong_activation_species_concentration.py`
- `exploration/strong-activation-geography-v1/exploration/run_naamp_strong_activation_geographic_generality.py`
- `exploration/strong-activation-state-heterogeneity-v1/exploration/run_naamp_strong_activation_state_heterogeneity.py`
- frozen FrogID continuous-depth workflow

### Message printed in figure
**The chorus-state response is distributed across species and insensitive to one-state omission, but its strength varies substantially among states; Australia supports only the broader taxonomic-depth direction.**

---

## Supporting figures to retain from RC11

Move rather than delete:
- alpha/beta/gamma decomposition details;
- Sørensen practical-equivalence result;
- matrix-fill equivalence;
- κ and anchor-weight null sensitivities;
- detection-quality robustness;
- protocol-window sensitivity;
- activation-geometry falsification;
- functional/trait failures;
- memory-age diagnostic that failed the formal route-count gate;
- coarse NWI and multicue mediator failures.

## Figure-story test

A reader who sees only Figures 1, 2, 4 and 5 should recover the full biological argument:

> rain-associated state switch → higher-order multi-site chorus coherence → historically targeted placement → not generated by simple species/site processes → broad but heterogeneous frog-community phenomenon.

If that sequence is not obvious from the rendered figures, the redesign has failed.
