# Gap and claim map v0.2 — higher-order chorus coherence

**Status:** integrated post-freeze synthesis.  
**Current manuscript:** `paper/manuscript_pulse_template_v0_3.md`  
**Frozen submission authority:** `main` at `015a675324800f2e5ac9ab0985b080fe88adc375`.

## 1. Literature gap

Established frog ecology already shows that:

- rainfall, temperature, humidity and hydroperiod affect calling;
- assemblage composition and calling intensity change over short timescales;
- calling/population activity can covary across sites;
- some anurans repeatedly use the same breeding sites.

The unresolved level is not whether frogs call after rain or whether sites covary. It is:

> **When a short environmental pulse recruits taxa into a repeated multi-species × multi-site chorus landscape, is the resulting spatial expression only the first-order sum of recruited taxa and occupied sites, or does activation contain higher-order within-taxon dependence—and is that dependence historically placed at species-specific sites?**

This is the paper's gap.

## 2. Frog-specific discovery

The empirical chain is:

1. **Acoustic state switching**
   - 65.3% of the CallingIndex rainfall slope comes from 0→positive activation.
   - 87.1% of that activation enters directly at CI2/3.
   - 0→CI3: β=0.441, 95% CI 0.114–0.768.
   - same observer + same SiteID: β=0.514, 0.101–0.927.

2. **Spatial depth**
   - second-stop β=0.132 and is not exceptional under the primary nulls.
   - third+ β=0.473 and exceeds both primary null ranges.
   - fourth+ β=0.363.
   - 97.3% of the third+ coefficient is carried by CI2/3.

3. **Exact higher-order coherence**
   - within every pair/direction, condition exactly on target-new taxon count N and total target incidence K.
   - raw higher-order excess β=0.2439, 95% CI 0.1474–0.3404.
   - standardized excess β=0.09075, 0.05946–0.12203.
   - same observer + same SiteID raw excess β=0.2543, 0.1375–0.3712.

4. **Historical placement**
   - within pair × taxon, prior strong SiteID → wet CI2/3 β=0.1511, 0.1291–0.1731.
   - wet CI3 β=0.0778, 0.0619–0.0937.
   - rain-selective historical CI3 targeting β=0.02449, 0.00700–0.04198.
   - same-observer rain-selective β=0.03067, 0.01331–0.04804.

Thus the biological result is:

> **Recent-rain conditions are associated with silent-to-strong chorus transitions that become unusually deep within the same frog taxa across multiple sites and preferentially reappear at historically strong species-specific physical sites.**

## 3. Why the result is surprising

The strongest surprise is **not** the raw 98% recurrence share.

The key surprise is that two wet-state communities with the same:

- number of newly recruited taxa, and
- total number of route-new incidences

still differ in how that activity is allocated.

Nearer recent rain, extra incidences are disproportionately concentrated within the same taxa at third-and-later sites.

Therefore the discovery is about the **dependence structure of activation**, not the amount of activation.

## 4. Strong falsification chain

Higher-order within-taxon concentration survives increasingly structured first-order generators.

Full 4,236-pair sample:

| Comparator | Observed β | Predicted β | Conditional P |
|---|---:|---:|---:|
| uniform activation | 1.524 | 1.138 | 0.000999 |
| dry-state persistence | 1.524 | 0.784 | 0.000999 |
| route-cross-fit species rain response | 1.524 | 1.198 | 0.000999 |

Strictly-prior-history subset, 2,916 pairs:

| Comparator | Observed β | Predicted β | Conditional P |
|---|---:|---:|---:|
| cross-fit species + prior SiteID + dry persistence | 1.650 | 1.353 | 0.000999 |
| above + held-out rain × history gate | 1.650 | 1.332 | 0.000999 |

Same observer + same physical SiteID, 3,115 pairs:

- observed β=1.817;
- uniform prediction=1.400, P=0.000999;
- persistence prediction=0.918, P=0.000999.

Authorized interpretation:

> **The tested transferable species responses and static species × site propensities do not reproduce the higher-order within-taxon concentration.**

Do not paraphrase this as “other factors exist” or “site history does not matter.”

## 5. General ecological principle

Preferred formulation:

> **Short environmental pulses can reveal higher-order spatial organization on recurrent species × place templates in behaviourally cryptic communities.**

Operational decomposition:

- **fast gate:** short-term environmental state associated with behavioural expression;
- **slow template:** recurrent species × place structure across years;
- **higher-order layer:** spatial participation concentrated within the same taxa beyond first-order taxon and incidence totals.

The general contribution is a distinction between **creating structure** and **revealing structure that was behaviourally hidden**.

## 6. Generality and heterogeneity

### Taxonomic breadth

Higher-order endpoint:
- 53 taxa represented;
- 25 positive;
- 19 contribute ≥1% of positive mass;
- top 1=18.8%;
- top 5=54.2%;
- HHI=0.0855;
- every leave-one-taxon-out total remains positive;
- minimum leave-one-taxon-out β=1.209.

### Geographic breadth

- 21 sampled states;
- every leave-one-state-out coefficient and 95% CI remains positive;
- LOSO β range=0.967–1.775;
- minimum LOSO CI lower bound=0.397.

### Heterogeneity

State-specific higher-order models:
- 17 estimable states;
- 14 positive point estimates;
- only 2 wholly positive CIs.

Correct wording:

> **Broad programme-scale support with substantial geographic heterogeneity.**

Not:
- spatial invariance;
- nationwide uniformity;
- universal anuran response.

## 7. Analysis scale

NAAMP:
- 2001–2015 unified-protocol period;
- 15 years;
- 7,848 eligible complete route-runs;
- 10 standardized stops per route;
- 4,236 matched wetter–drier comparisons;
- 585 routes;
- 21 states;
- 2,693 exact consecutive-year pairs;
- 3,115 same-observer + same-physical-SiteID pairs;
- 2,916 strictly-prior-history pairs across 439 routes.

The design therefore resolves repeated:

> **taxon × physical site × survey-state**

structure, not only occurrence or route richness.

FrogID:
- 40,754 expert-validated active recordings;
- supports the narrower wet-condition taxonomic-depth direction;
- does not replicate the higher-order species × site geometry.

## 8. Evidence hierarchy for the paper

### Main-text discoveries

1. silence → strong/full chorus;
2. second site ordinary, third+ sites exceptional;
3. exact N,K-conditioned higher-order coherence;
4. observer/SiteID robustness and cross-fit species/history falsification;
5. species-specific historical-site targeting;
6. rain-selective historical targeting;
7. taxonomic breadth + geographic robustness/heterogeneity.

### Supporting context

- 92% boundary crossing;
- exact four-component matrix allocation;
- Sørensen practical equivalence;
- matrix-fill equivalence;
- raw recurrence percentages;
- adjacency corroboration;
- FrogID directional consistency.

### Negative/failed mechanism diagnostics

Retain transparently in SI:
- activation-geometry placebo failure;
- coarse wetland/hydroperiod tests;
- simple social-facilitation proxy;
- short recency-window and multicue diagnostics;
- trait mechanisms;
- memory-age classification that failed its route-count gate.

## 9. Claim boundaries

Do not claim:

- rainfall causally triggers the observed state;
- acoustic zero = physical absence;
- literal synchrony among sequentially surveyed stops;
- individual movement among sites;
- individual memory or philopatry as the identified mechanism;
- hydrological connectivity or social facilitation as identified mechanisms;
- strong chorus = successful spawning;
- demographic metacommunity connectivity;
- worldwide universality;
- unique lower-level mechanism identification.

## 10. Current title and one-sentence take-home

**Rainfall-associated frog chorus activation shows higher-order spatial coherence and species-specific site recurrence**

Take-home:

> **Rain-associated frog chorus activation is not only deeper but higher-order: after first-order recruitment and total spread are fixed, activity remains disproportionately concentrated within the same taxa across multiple sites and preferentially reappears at historically strong species-specific locations.**
