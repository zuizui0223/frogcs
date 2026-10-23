# New macroecological evidence — NWI mapped wetland habitat does not account for frog acoustic-community turnover in NAAMP

**Executed 2026-10-23** on an isolated exploratory branch. Real USGS NAAMP 2001–2015 acoustic community data linked to the existing response-blind 12-shard USFWS NWI map crosswalk; **no literature searches, no simulations passed off as data, no JAE RC6 changes**.

## Biology first: two explicit metacommunity questions

**Q1:** Is the turnover of frog acoustic taxon lists between any two sites of a single ten-stop survey higher across mapped NWI emergent wetland / nonoverlap boundaries than within the same mapped status? **Not supported.**

**Q2:** Is continuous difference in mapped total wetland cover between sites a better *held-out route* predictor of turnover than the binary emergent wetland boundary? **Not supported** as an incremental signal after observed site-level call richness, night effects, survey-stop separation, temperature and sound masking.

These are **bounded tests of mapped static wetland geometry**, not proof that plants/hydroperiods have no ecological effects. Heterospecific competition, fish/odonate mediation and causal ≥3-body interactions remain unidentified.

## Exact source and outcome scope

- NAAMP standardized source: **7,848** ten-stop survey runs, from the pinned release (21,934 original run rows). Full mapped NWI + sound/temperature data: **6,236** complete route-nights and **5,147** physical NWI sites, source [NWI source gate #39450277196](https://github.com/zuizui0223/frogcs/actions/runs/39450277196).
- **3,717** route-nights have 2–8 mapped PEM-positive stops and thus within-survey environment-boundary comparisons. Of these, 3,430 runs / **285** routes have ≥2 CI≥1 taxon units. Exactly **143,615** stop pairs had at least one acoustic record; all-empty stop pairs excluded (10,735 among eligible runs), not silently set to zero.
- CI≥2 stronger chorus: **2,660** nights / **280** routes / **103,528** valid stop pairs. Within-run 45 possible pairs are correlated; *physical route* is the inferential cluster, not each pair.
- Exposure defined as `NWI PEM cover fraction > 0` in 250m or `abs(NWI total wetland cover difference)`. These are present-day mapping proxies and may be temporally mismatched with NAAMP 2001–15 surveys. Any absence of NWI PEM polygon is **not measured absence of live aquatic plants**.

## Analysis A: same-night, richness- and wetland-adjusted Sørensen

Exactly within-run fixed-effects Sørensen model controlling: eight stop-separation dummies, absolute mapped wetland fraction difference, temperature difference, masking difference, observed species richness difference and mean richness. Equal physical route weights; route-clustered 95% Student intervals and 4,999 route-score sign flips. 250-m geometry and controls were frozen before the first result.

| Outcome | Route-night and pair scale | Adjusted boundary effect on Sørensen dissimilarity | 95% route CI | route P | score flip P |
|---|---|---:|---:|---:|---:|
| CI≥1 any caller | 3,430 nights / 143,615 pairs / 285 routes | **+0.0871 percentage points** | −0.3803 to +0.5544 | .7141 | .7220 |
| CI≥2 strong caller | 2,660 nights / 103,528 pairs / 280 routes | **+0.0808 percentage points** | −0.4501 to +0.6117 | .7648 | .7698 |

Under the original same-survey cohort, Simpson turnover among **both-active** pairs had +0.5776 pp in any calling (route P=.255) and +0.6562 pp in strong calling (P=.246), again no support for a clear mapped boundary effect.

**Executed/tested:** [Actions #39875845459 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39875845459), script `exploration/run_naamp_macro_pem_boundary_turnover_v0_1.py`. Source-sample NWI and mathematical QA both passed; first two synthetic QA attempts are transparently superseded rather than called empirical failures.

## Analysis B: 2-fold strictly held-out routes, continuous wetland vs PEM category

This was **explicitly chosen post-hoc after Analysis A's null**. Fits four conditional-within-night models on whole training routes and evaluates identical held-out whole routes, with equal physical route weight. Baseline M0 uses observed same-night acoustic richness difference/mean, station separation, temperature and sound; M_PEM adds binary mapped PEM boundary; M_WET adds continuous absolute mapped total wetland-cover difference; M_BOTH adds both. Changes measure **held-out reduction in squared Sørensen error** over this rich conditional baseline (higher is better), not intervention effects or general future-night forecasts.

| Main contrast | CI≥1 MSE gain vs baseline | Relative M0 gain | 95% route CI in squared Sørensen | route P |
|---|---:|---:|---|---:|
| M_WET − M0 | **−0.00000550** | **−0.0101%** | −0.00002147 to +0.00001048 | .4987 |
| M_PEM − M0 | **−0.00000998** | **−0.0183%** | −0.00001786 to −0.00000209 | .0133 |

Total baseline M0 CI≥1 heldout squared error = **0.0546160**. Continuous wetland difference adds no supported transferable predictive information: one heldout fold had **negative** gain, the other **positive**. Binary PEM decreases conditional heldout accuracy very slightly in both folds (a minuscule numerical loss, *not a detrimental effect on frog populations*).

**Secondary strong CI≥2:** M_WET gain **−0.00002825** (−0.0531% of M0; 95% route CI −0.00005399 to −0.00000252, P=.0315), but folds **disagree in sign** and this was not the chosen primary test. M_PEM gain **−0.00000345** (−0.00648%, P=.308); no pattern of transferable improvement. Both-feature models were not an improvement over baseline.

**Executed/tested:** [Actions #39876782424 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39876782424), script `exploration/run_naamp_macro_pem_wetland_transfer_v0_1.py`, 80-route synthetic recovery QA PASS. The full derived numerical JSON lives in the workflow artifacts (not in `main`).

## Integration with earlier macro observations

The previously verified single-taxon NAAMP site-placing analysis found **5 of 25** eligible taxon units with positive BH-supported associations of strong calling with mapped NWI emergent wetland fraction. Earlier pairwise network analysis found sign-heterogeneous residual co-detection (e.g. 43 of 127 eligible any-call species-pair edges), but mapped NWI taxon-specific habitat-only nulls generated essentially none of the originally observed fixed-margin C-score excess. A separate 57-strong / 110-any node-permuted macro test of plant preference *divergence* likewise had no statistically supported landscape-wide effect; [Actions #39869396031 SUCCESS](https://github.com/zuizui0223/frogcs/actions/runs/39869396031): strong node-permutation one-sided P=.3264; any P=.1021.

**Nontrivial ecological interpretation:** the presence of species-specific acoustic habitat associations is **not sufficient to establish** that coarse mapped emergent-wetland boundaries or coarse total-wetland-cover contrasts organize the *realized community-level turnover* of NAAMP frogs on the same ten-stop night. First-order wetland affinities, historical acoustic site structure and partner-specific acoustic residuals remain distinct layers. It would be scientifically invalid to convert this outcome into a statement that (a) plants never alter frog interactions, (b) the residual acoustic edges are direct competition, or (c) absent measured PEM means no plants in 2001–2015.

## Decision: avoid endless radius tests

Do **not** choose a new radius/state/taxon/season after these two negative macro tests merely to find positive P values. A genuinely new macroscopic direction requires **new ecological exposure dimensions or a distinct observation grain**, preferably independently sourced time-varying hydrological habitat area/exposure, not more variations of the same static NWI proxy. This decision is evidence-driven and keeps the frozen JAE RC6 submission intact.

**Source/analysis code:** `exploration/NAAMP_MACRO_PEM_BOUNDARY_TURNOVER_SPEC_2026_10_23.md`; `exploration/NAAMP_MACRO_WETLAND_CONTINUOUS_TRANSFER_SPEC_2026_10_23.md`; `.github/workflows/naamp_macro_pem_boundary_turnover.yml`; `.github/workflows/naamp_macro_pem_wetland_transfer.yml`. Raw third-party datasets were not committed.
