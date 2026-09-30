# Higher-order spatial coherence decision note v0.1

**Status:** fixed while PR CI run was in progress and before endpoint readback.

## Primary question

After conditioning on both:
1. the rainfall-associated number of route-new species, and
2. the rainfall-associated total extra-stop incidence carried by those species,

is the remaining extra-stop response more concentrated within the same recruited species at third-and-later occupied stops than expected under the two existing activation nulls?

The primary statistic is the conditional residual of `higher_order_within_species_mass`, where for a route-new species occupying k wet stops,

`e = max(k - 1, 0)`

and

`higher_order_mass = choose(e, 2)`.

This is zero at k<=2 and grows convexly from k>=3.

## If the prefixed gate PASSES

Gate:
- observed conditional residual > upper 95% residual bound under kappa=2 uniform activation; AND
- observed conditional residual > upper 95% residual bound under a=0.75 persistence-preserving activation.

Authorized interpretation:

> Rainfall-associated multi-site expression contains higher-order within-taxon spatial dependence: after accounting for how many taxa are newly recruited and how much total extra-stop spread occurs, that spread is more concentrated within the same recruited taxa at third-and-later sites than expected under the tested independent-cell activation processes.

Preferred biological wording:

> Recruited frog taxa do not merely accumulate extra detections independently across sites; their wet-state activity is unusually deep within the same taxa across multiple sites.

Allowed generalization:

> This supports route-scale spatial coherence of the expressed chorus state.

Not authorized:
- literal simultaneity or synchrony;
- coordinated individual movement;
- hydrological connectivity;
- social facilitation;
- causal rainfall forcing;
- a universal anuran mechanism.

Manuscript consequence:
- promote higher-order spatial coherence to the main Results, immediately after the third-and-later-stop result;
- retain adjacency as corroborating route-topology evidence;
- revise the general principle from only "fast gate x slow template" to "fast gate reveals higher-order spatial coherence on a persistent template."

## If the prefixed gate FAILS

Authorized interpretation:

> Rainfall-associated route-new taxa show excess multi-site spread and excess third-and-later depth under the existing nulls, but we do not establish an additional higher-order concentration of extra-stop incidences within the same recruited taxa after conditioning on first-order recruitment and spread.

Manuscript consequence:
- do not use "higher-order spatial dependence";
- retain "multi-site deepening" and "route-scale spatial coherence" only in the already-tested conditional-spread / adjacency sense;
- do not reinterpret the failure as evidence for diffuse coordination;
- keep fast-gate x slow-template as the general framing.

## Regardless of outcome

The following existing results remain unchanged:
- conditional extra-stop coherence versus route-new species recruitment: P=0.000999 under both primary nulls;
- adjacent-stop links conditional on extra-stop spread: P=0.000999 under both primary nulls;
- third-and-later-stop excess: P=0.000999 under both primary nulls;
- strong CI2/3 share of third-and-later coefficient: 97.3%;
- within-pair x species historical-site targeting: beta=0.151;
- opportunity-normalized rain-selective targeting: beta=0.0245.

No alternative higher-order statistic will be substituted after endpoint readback.
