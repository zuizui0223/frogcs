# Amphibian pairwise acoustic networks: do partner identities transfer to new routes?
2026-10-22, `frogcs` exploratory research branch (frozen JAE RC6 untouched)

## Question and current result

**Observed partner-specific same-night frog co-calling structure is only partially transferable as independent partner predictors.** Among frog calling groups previously found on the same route-run, the location of **`Lithobates catesbeianus`** adds robust conditional information about where **`L. clamitans`** is acoustically recorded after static NWI wetland/PEM context, strictly earlier same-site calling propensity, and generic other-taxon same-stop richness. By contrast, once `L. catesbeianus` is included, adding `Anaxyrus fowleri` or `Hyla versicolor` yields **no demonstrable additional heldout prediction** under the fixed route-clustered gates.

The source observational **negative** `L. clamitans × A. fowleri` and `L. clamitans × H. versicolor` co-calling residuals remain as prior descriptive facts. An effect's *signed observation statistic* is not identical to its independently incremental heldout predictive value.

This is neither direct competition/facilitation, nor an irreducible three-species interaction, nor literal simultaneous calling: NAAMP stops were visited sequentially.

## Previously verified ecology

- `L. clamitans × L. catesbeianus` had more same-stop positive calls than the NWI+PEM fixed-margin expectation, and `L. clamitans × A. fowleri` and `L. clamitans × H. versicolor` had less.
- Those **opposite signed components** were previously recovered within the very same 10-stop survey, with all detected taxon row sums and stop-species richness held exactly fixed.
- Adding strictly **previous-year only** species × physical SiteID use reduced the same-run paired contrast by ~**19.9%** (A. fowleri comparison) and **24.4%** (H. versicolor comparison), but the primary any-calling residual remained above 0 on the same complete samples.
- Broad mapped PEM structure, current-month surface water and recent-month water summaries could not generate the observed between-species checkerboard excess under the earlier model sequence.

## New predictive experiment: exact two-row exchange conditional on the entire acoustic community

Condition on a ten-stop route-run where `L. clamitans`, `L. catesbeianus` and one of the negative partners were heard somewhere. For each possible additional calling taxon j, enumerate all possible reallocations of the **exclusive** `L. clamitans` versus j calling stops. The two focal partner rows and every other species row stay fixed; therefore *both the total stops per species and species richness per stop stay exactly unchanged*. At most 252 allocations enter one exactly normalized conditional logistic pseudolikelihood.

The fixed first-order offset uses species-specific total NWI wetland and 250m PEM associations, plus prior-year same physical-SiteID calling log odds. A generic number of remaining frog taxa per listening stop is an explicit fitted control.

- **M0:** first-order offset + generic other-calling richness;
- **M_P:** M0 + `L. catesbeianus` at-stop acoustic record;
- **M_PN:** M_P + `A. fowleri` or `H. versicolor` at-stop record.

All model coefficients are fit only in the training geographic route fold with identical ridge=3 and bounds ±3. Crucial **nested route firewall**: on training fold A, the first-order NWI coefficients must also be trained on A and are applied to heldout B *without accessing B to fit either stage*. Reverse for B-to-A. The first preliminary Actions run 39712455457 was **invalid for the new two-stage heldout inference** because its second-stage training NWI offset had been fitted on the eventual evaluation fold. It is explicitly superseded by corrected primary Actions 39712895709 and the present nested v0.3 Actions 39713551897; do not cite or reuse its apparent heldout estimates.

This is an **exact fixed-row/column conditional pseudolikelihood**, *not* the joint likelihood of whole frog community composition.

## Primary result (CallingIndex 1–3)

| Candidate negative partner in same surveyed triplet | `A. fowleri` | `H. versicolor` |
|---|---:|---:|
| Eligible route-runs / routes | 240 / 97 | 220 / 111 |
| Alternate row-swap observations | 556 | 379 |
| M_P versus M0: **positive partner increment** | **+0.09648 nats/run** | **+0.11118 nats/run** |
| 95% route bootstrap for M_P−M0 | +0.05671 to +0.13842 | +0.06548 to +0.15708 |
| M_PN versus M_P: **negative partner increment** | +0.01424 | −0.00587 |
| 95% route bootstrap for M_PN−M_P | **−0.00108 to +0.02855** | **−0.01483 to +0.00215** |
| Negative increment's BH q, two fixed trios | **0.11446** | **0.17411** |
| Joint M_PN versus M0 | +0.11072 | +0.10531 |
| CI for joint increment | +0.06449 to +0.15593 | +0.05932 to +0.15361 |

All values are **mean improvement in the conditional site-assignment log score per route-run (nats/run)** on geographically heldout routes, averaging the available nonfocal row-swap choice sets equally *within each survey*. They are NOT percentage changes in occupancy probability, causal effects, full-community likelihoods, or an unrestricted forecast of where frogs occur.

**Both positive partner increments have route-block 95% intervals above zero.** Their point estimates account for approximately **87%** of the joint observed improvement in the A. fowleri comparison and exceed **100%** of the joint improvement in the H. versicolor comparison (the added negative partner slightly reduces heldout score). The negative partner increments themselves each have intervals overlapping zero and neither passes the post-readback fixed BH test.

### Coefficient direction

- When N is `A. fowleri`: beta(P) positive in both training route folds (**+0.931**, **+1.165**); beta(N) negative in both (**−0.358**, **−0.444**). This is *directional training consistency* but does **not** rescue its unsupported **incremental heldout gain** (q=0.114).
- When N is `H. versicolor`: beta(P) positive in both (**+1.248**, **+0.963**), but beta(N) changes sign (**−0.204**, **+0.156**). The negative partner's incremental prediction is not supported.

The original predeclared joint v0.2 classifier identified a directional `A. fowleri` candidate. **The later targeted v0.3 decomposition narrows that statement:** the joint model predicts, yet the *specific negative partner effect is not independently established once P is included*.

## Time transfer and strong-calling boundaries

A named 2001–09 → 2010–15 split of the partner coefficients (using fixed NWI source coefficients that saw both eras) reproduces positive heldout M_P−M0 increments, but **does not support negative-partner addition**:
- `A. fowleri` later negative increment +0.00891, 95% CI −0.01334 to +0.03086;
- `H. versicolor` later negative increment −0.00397, CI −0.01175 to +0.00372.

Because source NWI coefficients were trained across both periods, this is **descriptive temporal transfer**, not independent chronological validation.

For strong acoustic CallingIndex 2–3, only **30** A. fowleri and **36** H. versicolor runs have a nonfocal swap partner after the fixed previous-history gate; both fail predeclared ≥60-run/≥25-route/≥20-per-fold requirements. No supported positive or negative independent strong-call prediction can be inferred.

## Revised ecological hierarchy

1. **First-order environmental context and history exist:** NWI plant structure is associated with some individual taxa; earlier species×SiteID records help predict future acoustic site assignments.
2. **Residual second-order organization exists descriptively:** particular frog pairs co-call more/less than expected from these first-order components, even on the same route-run.
3. **A positive network connector has portable conditional information:** `L. catesbeianus` acoustic locations predict extra structure in `L. clamitans` assignments on heldout routes.
4. **Named negative partner prediction is unconfirmed:** `A. fowleri` and `H. versicolor` remain observed negative edges but do not add robust incremental heldout information once bullfrog locations are included.
5. **A plant → fish/insect predator → frog route is an unmeasured causal hypothesis, not an empirical conclusion.** NAAMP lacks simultaneous fish, predatory aquatic insects, actual macrophyte identities, water depth, and individual-level acoustic time series.

**Stop this round of source-relative exploratory model expansion.** Another retrospective parameter sweep would be less convincing than replicated wetland field monitoring measuring plants, hydrology, predators and frog sub-minute sound over time or a prospectively declared, independently sourced multi-taxonomic survey.

## Provenance

- Preregistered original joint question `exploration/NAAMP_PARTNER_FIXED_MARGIN_HELDOUT_CHOICE_CONTRACT_2026_10_22.md`.
- Corrected nested geographic fold procedure `exploration/NAAMP_PARTNER_FIXED_MARGIN_HELDOUT_CHOICE_CONTRACT_V0_2.md`.
- Additional post-readback increment attribution `exploration/NAAMP_PARTNER_FIXED_MARGIN_INCREMENTAL_CONTRACT_V0_3.md`.
- Corrected v0.2 exact numerical receipt `exploration/NAAMP_PARTNER_FIXED_MARGIN_HELDOUT_CHOICE_RESULT_V0_2.json`; [Actions 39712895709](https://github.com/zuizui0223/frogcs/actions/runs/39712895709), SUCCESS.
- Full nested incremental v0.3 `exploration/NAAMP_PARTNER_FIXED_MARGIN_INCREMENTAL_RESULT_V0_3.json`; [Actions 39713551897](https://github.com/zuizui0223/frogcs/actions/runs/39713551897), SUCCESS, source artifact ID 12397353997.
- Synthetic QA: fixed species+stop margins, conditional-subset probability normalization, known positive and negative effect recovery: PASS.
- Matched original any/strong survey universe: 3659/1766 C-scores verified, the same original NWI crosswalk and strictly historical physical-site rules. Frozen manuscript, Supporting Information, GitHub main and journal submission files unmodified.
