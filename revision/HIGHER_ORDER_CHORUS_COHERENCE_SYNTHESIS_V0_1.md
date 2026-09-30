# Higher-order chorus coherence synthesis v0.1

## Central frog-ecology result

Across repeated NAAMP routes, recent-rain conditions are associated with a structured change in frog reproductive acoustic state:

1. previously silent species × site cells often enter directly into overlapping/full chorus states;
2. newly recruited taxa do not merely add isolated detections but deepen across three or more sites;
3. at the same number of recruited taxa and the same total amount of extra-stop spread, extra spatial participation is unusually concentrated within the same taxa;
4. this higher-order concentration persists when observer identity and physical SiteID are held constant;
5. it also persists under a cross-fit species-specific rainfall-response null, a joint species + strictly-prior SiteID-history + dry-persistence null, and the pre-existing final held-out rain × local-history gate;
6. strong wet-state activity preferentially reappears at physical sites where the same species had previously formed strong choruses.

## Strongest quantitative chain

### Chorus-state switching
- total CallingIndex rain slope = 2.841
- 0→positive share = 65.3%
- 0→CI2/3 share of activation = 87.1%
- 0→CI3 β = 0.441 (0.114–0.768)
- same observer + same SiteID 0→CI3 β = 0.514 (0.101–0.927)

### Spatial depth
- second-stop β = 0.132, not exceptional under primary nulls
- third+ β = 0.473, P=0.000999 under both primary nulls
- fourth+ β = 0.363
- 97.3% of third+ coefficient carried by CI2/3

### Higher-order within-taxon coherence
Full 4,236 pairs:
- route-new-species β = 0.1847
- extra-stop β = 0.6043
- higher-order β = 1.5240

Conditional residual tests:
- uniform null prediction 1.1384; residual 0.3856 vs 95% −0.0984–0.0959; P=0.000999
- persistence null prediction 0.7836; residual 0.7404 vs −0.0805–0.0824; P=0.000999
- cross-fit species-response null prediction 1.1979; residual 0.3261 vs −0.1006–0.1086; P=0.000999

Strictly-prior-history subset, 2,916 pairs:
- observed higher-order β = 1.6503
- joint cross-fit species + prior SiteID history + dry persistence prediction = 1.3535
- residual 0.2969 vs −0.1319–0.1187; P=0.000999
- final held-out rain × history gate prediction = 1.3323
- final-gate residual 0.3180 vs −0.1172–0.1255; P=0.000999

Same observer + same physical SiteID, 3,115 pairs:
- observed higher-order β = 1.8173
- uniform prediction 1.4002; residual 0.4171 vs −0.1116–0.1106; P=0.000999
- persistence prediction 0.9184; residual 0.8989 vs −0.0972–0.0989; P=0.000999

### Historical spatial template
- within-pair × species prior strong SiteID → wet CI2/3 β = 0.151 (0.129–0.173)
- wet CI3-only β = 0.0778 (0.0619–0.0937)
- same-observer β = 0.159 (0.134–0.183)
- directional opportunity-normalized rain-selective CI3 targeting β = 0.0245 (0.0070–0.0420)
- same-observer β = 0.0307 (0.0133–0.0480)

## What is genuinely new

The novelty is not:
- frogs call after rain;
- activity increases at more sites;
- some sites are historically better;
- simple models do not explain everything.

The defensible novelty is the conjunction:

> **Rain-associated chorus activation contains higher-order spatial dependence: after controlling for the number of newly recruited taxa and the total amount of spread, activation remains too deeply concentrated within the same taxa across multiple sites for uniform activation, dry persistence, transferable species-specific rainfall responses, their additive combination with strictly prior local site history, or the pre-existing held-out rain × history gate to reproduce. The strong chorus states are then preferentially placed at historically favoured species-specific sites.**

## General ecological principle

Preferred:

> **Fast environmental gates can reveal higher-order spatial coherence on slow species × place templates in behaviourally cryptic communities.**

This is a conceptual generalization from the frog system, not a demonstrated universal law.

## Wording discipline

Allowed:
- higher-order spatial coherence
- higher-order spatial dependence
- coherent multi-site expression
- persistent species × site chorus template
- chorus-state switching
- historically structured re-expression

Avoid:
- synchrony / simultaneous activation
- coordinated movement
- metapopulation connectivity
- biological memory as an identified mechanism
- philopatry as the identified mechanism
- rain causes
- spawning or breeding success
- universal anuran rule

## Manuscript hierarchy

Main text:
1. silent → strong chorus
2. second stop ordinary, third+ sites exceptional
3. higher-order coherence after conditioning on recruitment and spread
4. robustness to observer/SiteID and cross-fit species response
5. historical site targeting and rain selectivity
6. nested allocation nulls as supporting falsification
7. breadth and heterogeneity

Supporting Information:
- raw recurrence percentages
- beta diversity / fill
- trait failures
- candidate mediator failures
- memory-age diagnostics
- all secondary null sensitivities

## Stop rule

No new higher-order metric should be introduced after these positive results. Further analyses should be limited to:
- exact reproduction/audit of existing endpoints;
- manuscript/figure clarity;
- prespecified robustness using the same endpoint;
- genuinely external replication if suitable data become available.

The manuscript should not escalate into searching for a lower-level causal mechanism in the same NAAMP data.
