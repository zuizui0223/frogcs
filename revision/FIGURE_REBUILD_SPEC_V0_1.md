# Integrated figure rebuild specification v0.1

## Design principle

The figures must tell the frog-ecology story without requiring the reader to understand the null machinery first:

**silence → strong chorus → multi-site depth → historical site recurrence → simple generators fail**

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

## Figure 2 — Recruited species deepen across sites and return to historically strong places

### Biological question
After a species enters the wet-state route, is the response an isolated detection or a spatially deep recurrent chorus pattern?

### Panels
**A. Spatial-depth decomposition.**
Show first recruitment as the reference structure, then observed rainfall coefficients:
- second stop: β = 0.132; not outside either primary null
- third+ stops: β = 0.473; outside both primary null 95% ranges
- fourth+ stops: β = 0.363; outside null ranges

Overlay the κ=2 uniform and a=0.75 persistence-preserving 95% null ranges rather than only P values.

**B. Calling strength within third+ depth.**
Stack or side-by-side:
- CI2/3 share of third+ coefficient = 97.3%
- CI1-only remainder = 2.7%
- same-observer + same-SiteID CI2/3 share = 95.4%

**C. Within-pair × species site targeting.**
Coefficient plot:
- prior strong SiteID → wet CI2/3: 0.1511 (0.1291–0.1731)
- prior strong SiteID → wet CI3: 0.0778 (0.0619–0.0937)
- same-observer CI2/3: 0.1589 (0.1344–0.1833)

Annotate: comparisons are among the ten sites for the **same focal species and pair**.

**D. Rain-selective targeting.**
Coefficient plot:
- target-rain-advantage × historical targeting: 0.02449 (0.00700–0.04198)
- same observer: 0.03067 (0.01331–0.04804)

Small inset illustrates the reverse-direction design: wet-as-target versus dry-as-target for the same pair.

### Source
- `exploration/route-new-spatial-depth-v1/exploration/run_naamp_route_new_spatial_depth.py`
- `exploration/local-chorus-memory-v1/exploration/run_naamp_local_chorus_memory_targeting.py`
- `exploration/rain-selective-memory-v1/exploration/run_naamp_rain_selective_local_memory.py`

### Message printed in figure
**The unusual response begins after recruitment: species deepen into strong choruses across several sites, preferentially at sites with a prior strong record.**

---

## Figure 3 — Historical recurrence is abundant, but raw recurrence is not the inferential endpoint

### Purpose
Prevent the eye-catching 98% number from becoming the causal argument.

### Panels
**A. Route-new incidence decomposition.**
- leave-pair-out recurrent = 98.1%
- strictly-prior recurrent = 98.9%
- strictly-prior one-off β = 0.0094 (−0.1412–0.1600)

**B. New-CI3 recurrence decomposition.**
- leave-pair-out any recurrence = 98.1%
- same-SiteID recurrence = 90.4%
- strictly-prior same-SiteID recurrence = 82.6%

**C. Inferential hierarchy.**
A simple visual arrow:
raw recurrence → same-site recurrence → within-pair × species targeting → directional rain-selective targeting

Label the first two as **descriptive availability-sensitive** and the latter two as the inferential tests.

### Source
- `exploration/recurrent-activation-memory-v1/exploration/run_naamp_recurrent_activation_memory.py`
- `exploration/full-chorus-site-memory-v1/exploration/run_naamp_full_chorus_site_memory.py`

### Editorial option
If main-text figure count must be reduced, move Figure 3 to SI and retain panels 2C–D in the main text.

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
**A. Species contribution concentration.**
Rank positive species contributions; annotate:
- 57 species total
- 28 positive
- top 1 = 13.9%
- top 5 = 49.2%
- HHI = 0.074
- all leave-one-species-out totals positive

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

> rain-associated state switch → strong multi-site chorus → historically targeted placement → not generated by simple species/site processes → broad but heterogeneous frog-community phenomenon.

If that sequence is not obvious from the rendered figures, the redesign has failed.
