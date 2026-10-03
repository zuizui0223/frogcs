# Three-question ecological spine v0.1

## Purpose

This is the current reader-facing logic for the frogcs manuscript.

It separates:
1. biological questions that a frog ecologist would naturally ask;
2. principal evidence that answers those questions;
3. post-hoc diagnostics used to defend or refine the answers.

It must not be rewritten so that post-hoc null-model diagnostics become additional biological questions.

---

## Q1. What changes after recent rain: intensity, or behavioural state?

### Biological question

> **Does recent-rain mainly make already-calling frogs louder/more intense, or does it switch previously silent species × sites into substantial chorus states?**

### Principal evidence

- 65.3% of the CallingIndex slope came from previously silent cells.
- 87.1% of activation entered CallingIndex 2–3.
- Direct 0→CI3 transitions increased.
- Same-observer + same-physical-site sensitivity retained the effect.

### Ecological answer

Recent-rain conditions are associated with rapid changes in **reproductive acoustic state**, not only small increases at already-active sites.

### Boundary

Acoustic zero is not physical absence, and strong chorus is not demonstrated spawning or reproductive success.

---

## Q2. At what spatial unit is that activity organized?

### Biological question

> **When a taxon becomes acoustically active, do route stops behave as independent local wetland responses, or is activity organized across several separated locations?**

### Principal evidence

- acoustically route-new taxa show a deeper-than-expected multi-site tail;
- marginal depths 4–10 exceed both activation-null envelopes;
- the effect is overwhelmingly CI2/3;
- in 2,916 pairs with strictly-prior physical-site history:
  - observed within-taxon concentration = 1.650;
  - principal comparator prediction = 1.353;
  - conditional residual = 0.297, P=0.000999;
- the stronger held-out rain × history gate predicts only 1.332.

### Ecological answer

The realized wet-state response is not well described as ten independent local reactions. Calling by the same taxon is organized across multiple separated route positions beyond the tested taxon response, persistent local propensity and total activation magnitude.

### Post-hoc scale refinement

The NAAMP exploratory diagnostics further constrain the spatial form:
- dry-route-silent bounded dependence remains positive;
- far route-position lags retain most of the near-lag dependence;
- a uniform whole-route taxon-night scalar shift makes the stops too coherent.

Therefore the response lies between:
- independent wetland-level reactions;
- a uniform all-stop route switch.

### Boundary

Stop-number lag is route topology/survey order, not validated exact geographic distance. Literal synchrony is not observed because stops are sampled sequentially.

---

## Q3. Which places participate when activity becomes spatially deep?

### Biological question

> **When a taxon's activity is expressed across many route stops, is that spread spatially arbitrary, or does it preferentially involve physical sites where that taxon has chorused strongly before?**

### Principal evidence

- prior taxon-specific strong SiteID predicts wet-state CI2/3:
  - beta = 0.151;
- historical full-chorus targeting strengthens toward the survey closer to rain:
  - beta = 0.0245.

### Post-hoc placement refinement

After exact wet depth k and fixed-q site propensity are held constant:
- deep k>=4 events preferentially overlap strictly-prior CI2/3 SiteIDs;
- the direct deep-minus-shallow alignment contrast is positive;
- that numerical contrast is Monte-Carlo stable under the frozen audit.

### Ecological answer

Spatially deep activity is selectively expressed at recurrent taxon-specific chorus locations rather than being uniformly scattered across the route.

### Boundary

This does not identify:
- individual fidelity;
- movement;
- memory;
- hydrological causation;
- social facilitation;
- a unique lower-level mechanism.

---

## Synthesis

The manuscript's ecological result is:

> **On favourable nights, frog reproductive acoustic activity is organized at an intermediate spatial scale: broader than independent wetland responses, but more selective than a uniform route-wide switch. The realized multi-site chorus preferentially involves recurrent taxon-specific locations.**

This statement is preferred over:
- fast gate × slow template;
- latent spatial network;
- synchrony;
- hidden community memory;
- a named mechanism.

Those phrases may be useful explanatory shorthand in internal discussion, but they are not the reader-facing biological claim.

---

## Why this matters

### Frog ecology

The paper changes the question from:
> How much more do frogs call after rain?

to:
> At what spatial unit is reproductive calling organized when frogs become active?

It connects short-term acoustic state change with persistent spatial heterogeneity without assuming individual tracking or movement.

### Monitoring ecology

If route stops share taxon-specific behavioural state, then ten acoustic stops need not provide ten independent biological observations.

Post-hoc diagnostics show:
- pair-clustered SE > IID in 38/39 eligible taxa;
- median pair-cluster/IID ratio = 1.61;
- pooled route clustering increases the rainfall-effect SE 2.69-fold.

This is a representative activation-model consequence, not a reanalysis of published occupancy trends.

---

## Evidence routing

### Main text

Keep:
- Q1 state switching;
- Q2 deep multi-site organization;
- principal 2,916-pair comparator;
- held-out rain × history gate;
- Q3 historical-site targeting;
- taxonomic/geographic breadth;
- concise monitoring implication.

### Supporting Information / post-hoc defence

Keep:
- flexible nonlinear weather;
- 72-h rainfall amount;
- detection covariates;
- species calibration;
- leave-one-taxon-out stop-night hotness;
- bounded residual dependence;
- near/far route-position diagnostics;
- same-observer dependence;
- logistic-normal latent-state magnitude;
- scalar-state overcoherence;
- exact-k deep placement;
- deep-vs-shallow contrast;
- Monte Carlo stability;
- monitoring covariance details;
- failed/non-authoritative distance and GEE diagnostics.

These are **defence and refinement analyses**, not additional biological questions.

---

## Historical provenance

The final three-question structure was discovered through analysis; it was not the original frogcs hypothesis.

See:
- `revision/RESEARCH_QUESTION_EVOLUTION_2026-10-03.md`

The reopened same-data mechanism line is closed:
- `revision/NAAMP_POST_REOPENING_CLOSURE_2026-10-03.md`

The next evidential upgrade must be prospective external replication:
- `revision/WFTS_CONFIRMATORY_AUTHORITY_V0_4.md`
