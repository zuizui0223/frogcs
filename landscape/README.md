# frogcs behavioural-landscape extension

## Status

**PARKED — 2026-10-05.**

Independent post-RC6 landscape branch:

`landscape/naamp-behavioural-landscape-v1`

This branch does not alter RC6. The prespecified landscape prediction failed; the compactness interpretation is post-hoc. No further NAAMP outcome-driven landscape analysis is authorized. See `PARKED_STATUS_2026-10-05.md`.

## Current landscape result

The current evidence separates three spatial properties of favourable-night frog activity:

### 1. Depth
How many route stops the same taxon occupies.

RC6 result:
- marginal depths 4–10 exceed activation-null expectations;
- deep spread is dominated by CI2/3 strong chorus.

### 2. Geometry
How those k active stops are arranged in route order.

Stage A1 result:
- prespecified fragmented/selective-spanning hypothesis failed;
- deep k>=4 active sets are modestly **more compact** than exact-k fixed-q expectation.

Deep topology:
- 767 clusters across 243 routes;
- holes excess = −0.1535;
- span excess = −0.1535;
- component excess = −0.1210;
- mean pairwise StopNumber-lag excess = −0.0987;
- route-bootstrap CI for holes excess = −0.2578 to −0.0494.

Interpretation:
> **Deep activation tends to form relatively compact route-order domains, not unusually scattered sets of stops.**

### 3. Historical recurrence
Which physical locations participate.

RC6/post-hoc result:
- prior taxon-specific strong SiteIDs are preferentially included in deep activity.

Stage A2 asked whether compactness is specifically organized around those recurrent sites.

Result:
- 337 eligible deep clusters across 159 routes;
- core-distance excess = −0.0766;
- lower-tail P = 0.0305;
- route-bootstrap CI = −0.1486 to −0.0051;
- but the observed value did not cross the prespecified exact-null 2.5% boundary;
- formal support classification = **FAIL**;
- adjacency-to-core corroboration also failed.

Therefore:
> **Compactness and historical recurrence are both present, but the data do not justify treating recurrent sites as the demonstrated geometric cores of compact activation domains.**

## Current landscape interpretation

The strongest authorized statement is:

> **Favourable-night frog activity has separable landscape dimensions: taxon-level spatial depth, route-order geometry, and historical site recurrence. Deep activation is slightly more compact than expected, while recurrent strong-chorus sites are preferentially involved, but the two patterns cannot yet be collapsed into one identified mechanism.**

This is more informative than calling the result simply “route-scale dependence.”

## Stage status

### Stage A — route topology
**CLOSED**

Authority:
- `NAAMP_ROUTE_TOPOLOGY_GEOMETRY_CONTRACT_V0_1.json`
- `NAAMP_ROUTE_TOPOLOGY_GEOMETRY_RECEIPT_V0_1.json`
- `NAAMP_RECURRENT_CORE_EXPANSION_CONTRACT_V0_1.json`
- `NAAMP_RECURRENT_CORE_EXPANSION_RECEIPT_V0_1.json`
- `NAAMP_BEHAVIOURAL_LANDSCAPE_STAGE_A_CLOSURE_V0_1.md`

No new StopNumber-derived topology metric or threshold may be added after these results.

### Stage B — exact geographic geometry
**BLOCKED**

Reason:
- pinned USGS SiteID coordinates contain gross transcription errors;
- previous exact-distance result is non-authoritative.

Required before reopening:
- independently validated coordinate concordance table fixed without frog outcomes.

### Stage C — external landscape covariates
**PARKED — DO NOT RUN ON NAAMP OUTCOMES**

Independent sources:
1. Marsh et al. 2017 Dryad DOI 10.5061/dryad.8ns60
   - 587 NAAMP survey sites;
   - land-use/road variables from 300 m to 10 km buffers.

2. Marsh & Cosentino 2019 supplementary landscape data
   - nested compilation from 406 NAAMP routes;
   - stops 1,4,7,10;
   - 1-km forest, agriculture, development, wetland and road-density metrics.

First allowed operation:
- SiteID/route/schema coverage only;
- no frog outcome associations.

Coverage authority:
- `EXTERNAL_NAAMP_LANDSCAPE_COVERAGE_CONTRACT_V0_1.json`

## Why Stage C matters

Stage A establishes **shape** but not its cause.

Independent landscape variables can discriminate among possibilities such as:
- compact activation follows contiguous/similar wetland habitat;
- recurrent strong sites correspond to stable high-quality habitat nodes;
- road/development structure fragments or weakens multi-site expression;
- compactness remains after measured landscape structure, implying another shared behavioural/hydrological process.

No Stage-C biological test should be run on NAAMP under the current park. External sources are retained only for a future independently reopened study.

## Boundaries

Do not infer:
- exact kilometre scale from StopNumber;
- movement among stops;
- acoustic propagation;
- hydrological connectivity;
- individual fidelity;
- causal rainfall effects.

The route-order geometry is a landscape-scale behavioural pattern, not a validated movement network.
