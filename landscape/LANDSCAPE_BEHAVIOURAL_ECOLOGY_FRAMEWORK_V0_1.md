# Landscape behavioural ecology framework v0.1

**PARKED — 2026-10-05.** This framework is retained for provenance only. No further NAAMP landscape outcome analysis is authorized. See `landscape/PARKED_STATUS_2026-10-05.md`.

## Core question

RC6 asks whether response magnitude fully describes the realised multi-site chorus pattern.

The landscape extension asks:

> **When reproductive acoustic activity expands across a route, what spatial configuration does that expansion take?**

Two biologically different responses can have the same activation depth k:

- **compact expression** — active stops are clustered along the route;
- **networked/dispersed expression** — active stops are separated across the route.

Counting k alone cannot distinguish them.

## Level 1 — route topology (authoritative without coordinate repair)

Primary axis:
- ordered route positions 1..10.

Primary metric:
- **mean pairwise stop-number separation** among active positions.

Secondary metrics:
- **topological span** = max position − min position;
- **contiguous component count** = number of separate active blocks along the ordered route.

All geometry is conditioned on exact observed k and the strongest fixed-q stop probabilities.

Ecological alternatives:

### Compact local expansion
A taxon becomes active at several neighboring route positions.

Prediction:
- mean pairwise separation <= q-conditioned expectation;
- span <= expectation;
- component count <= expectation.

### Dispersed network expression
A taxon becomes active at separated route positions.

Prediction:
- mean pairwise separation > q-conditioned expectation;
- span > expectation;
- component count may also exceed expectation.

Interpretation boundary:
- route topology, not exact geographic distance;
- no inference of movement or acoustic propagation;
- survey order and stop topology are partly confounded.

## Level 2 — validated geographic geometry (future)

Only after an outcome-blind coordinate repair/validation authority is frozen.

Desired metrics:
- geodesic active-site span;
- mean pairwise geographic distance;
- radius of gyration;
- nearest-neighbor distance;
- distance-decay of residual dependence.

Required before analysis:
1. externally validate or repair known coordinate transcription errors;
2. freeze inclusion/exclusion rules using geometry only;
3. freeze repaired coordinate table and digest;
4. inspect frog outcomes only after geometry lock.

No post-outcome distance thresholding is allowed.

## Level 3 — landscape structure (future landscape-ecology layer)

Once reliable site geometry exists, add environmental configuration rather than only distance.

Candidate predictors:
- wetland density around each stop;
- proportion wetland/open water;
- road/stream network connectivity;
- topographic wetness;
- hydrographic connectivity;
- land-cover resistance between recurrent chorus sites.

The biological question becomes:

> **Does landscape configuration explain whether a favourable-night taxon state is expressed compactly or across a dispersed recurrent-site network?**

## Relationship to RC6

This line cannot upgrade or alter RC6.

RC6 result:
- response magnitude does not fully describe the realised taxon-by-place pattern.

Landscape line:
- quantify the **shape** of that pattern.

A positive route-topology result would generate an external prediction, not a new RC6 endpoint.

## Strong future hypothesis

If Level 1 supports topological dispersion:

> **Favourable-night reproductive activity can expand through a dispersed set of recurrent sites rather than by simple local spatial filling.**

If Level 1 does not support excess dispersion:

> **The RC6 multi-site excess reflects taxon-level depth and recurrent-site selection, but not additional route-topological dispersion beyond fixed stop propensities and exact k.**

Both outcomes are ecologically informative.
