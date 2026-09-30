# Pulse × persistent chorus template: gap and claim map v0.1

**Status:** post-freeze integrated reframing. The frozen RC11 submission remains preserved on `main` at commit `015a675324800f2e5ac9ab0985b080fe88adc375`. This document does not retroactively convert post-freeze analyses into preregistered tests.

## 1. The ecological gap

### What is already known

1. **Rain and weather affect frog calling.**
   Anuran calling is a reproductive behaviour whose timing and intensity are often associated with rainfall, temperature, humidity and season. Recent work has scaled this from single species to assemblage-wide calling dynamics.

2. **Frog assemblages change over short timescales.**
   Passive acoustic studies show that species composition can vary within nights and among days, with local habitat and landscape heterogeneity affecting those dynamics.

3. **Breeding-site fidelity and spatial recurrence exist in frogs and other animals.**
   Individual amphibians can return to breeding sites, and site fidelity is a broad animal phenomenon linked to spatial predictability.

4. **Environmental pulses and ecological memory are general ecological ideas.**
   Short-lived forcing can trigger rapid responses, while historical conditions or stable spatial heterogeneity can leave persistent structure.

### What is not resolved by those literatures

These literatures usually ask different questions:

- weather/calling studies ask **whether or how much activity changes**;
- chorus studies ask **how callers interact within a chorus**;
- site-fidelity studies ask **whether individuals return to locations**;
- community studies ask **how composition or diversity changes**;
- ecological-memory studies ask **whether past conditions alter later response**.

The missing question is:

> **When a short environmental pulse activates a spatial animal community, does it simply increase activity everywhere, or does it selectively re-express a persistent species × place structure that is normally hidden while animals are silent?**

That is the gap this study can occupy.

The novelty is therefore not "rain makes frogs call". It is the connection of **fast behavioural activation** to **slow spatial recurrence** at the community level.

## 2. General ecological principle

### Fast gate × slow template

The integrated evidence supports the following general model:

```
slow ecological template
(species × site combinations that repeatedly support strong activity)
                    ×
fast environmental gate
(recent-rain conditions)
                    ↓
temporarily expressed active community
```

The general principle is:

> **A short environmental pulse can reveal persistent spatial organization by gating which historically favoured species × site combinations enter an active state.**

This differs from both a static habitat model and a uniform activity model.

A static habitat model says "good sites are always more likely to be active."
A uniform pulse model says "rain raises all cells similarly."
The observed frog pattern contains both temporal gating and spatial recurrence, but even their simple additive/cross-fit combinations do not reproduce the full allocation.

This makes the result a **state-dependent re-expression of spatial structure**, rather than merely an increase in detectability or richness.

## 3. What was learned about frog ecology

### Finding A — rain is associated with chorus-state switching, not only more weak calling

Across 4,236 matched NAAMP wetter–drier comparisons:

- 65.3% of the CallingIndex rain slope is assigned to 0→positive activation;
- 87.1% of that activation slope is direct 0→CI2/3;
- 0→CI3 alone: β = 0.441, 95% CI 0.114–0.768;
- same observer + same physical listening site: β = 0.514, 0.101–0.927.

CallingIndex 3 is the full-chorus state in which calls overlap continuously and individuals cannot be distinguished.

**Ecological interpretation:** rainfall-associated change often resembles a switch from acoustic silence to a substantial breeding chorus, rather than a small increase in the audibility of already-calling frogs.

**Boundary:** this is an acoustic reproductive-behaviour state, not direct evidence of spawning, abundance, occupancy or demographic recruitment.

### Finding B — recruited species do not merely appear at one pond; they deepen across the route

The unusual allocation appears after a species has entered the active route:

- second-stop incidence: β = 0.132, not exceptional under the primary nulls;
- third-and-later-stop incidence: β = 0.473, above both null 95% ranges;
- fourth-and-later-stop incidence: β = 0.363, also above the null ranges;
- 97.3% of the third-and-later-stop coefficient is carried by CI2/3 activity.

**Ecological interpretation:** the rainfall response is spatially coordinated at the scale of multiple breeding/listening sites. It is not mainly a collection of isolated first detections.

This is a key frog result because it changes the biological picture from "one more frog species was heard somewhere" to "the same species joins substantial choruses across several sites during the wet state."

### Finding C — apparently new wet-state activity is usually re-expression of historical activity

Among physically stable comparisons:

- 98.1% of route-new rain-associated incidence is assigned to species recorded previously in the route-season history;
- strictly prior-only recurrence share = 98.9%;
- prior-only one-off/no-prior component: β = 0.009, 95% CI −0.141–0.160;
- 98.1% of new-CI3 rain-associated activity is historically recurrent;
- 90.4% of leave-pair-out new-CI3 activity recurs at the same physical SiteID;
- strictly prior-only same-site share = 82.6%.

The raw percentages are descriptive, not by themselves proof of selective recurrence because long histories create many opportunities for recurrence.

### Finding D — historical site use predicts where strong choruses return

Conditioning on the same pair and species:

- previously strong SiteID → later wet CI2/3: β = 0.151, 95% CI 0.129–0.173;
- CI3-only version: β = 0.0778, 0.0619–0.0937;
- same-observer pairs: β = 0.159, 0.134–0.183.

Opportunity-normalized strictly-prior analyses additionally show that increasing rain contrast selectively favours historically recurrent full-chorus candidate cells:

- β = 0.0245, 95% CI 0.0070–0.0420;
- same-observer β = 0.0307, 0.0133–0.0480.

**Ecological interpretation:** rain does not only coincide with activity at generally good sites. The wet-state response is preferentially expressed at species-specific sites with a history of strong chorusing.

Do not call this individual memory or philopatry. The persistent template could arise from stable local hydrology, vegetation, microtopography, recurring breeding suitability, individual/site fidelity, social structure, or combinations of these.

### Finding E — neither species sensitivity nor static site history is sufficient

The observed four-component species × site allocation rejects a sequence of increasingly permissive nulls:

1. uniform activation;
2. strong dry-state persistence;
3. route-cross-fit species-specific rainfall shifts;
4. strictly-prior local species × SiteID probabilities;
5. cross-fit species shifts + prior local memory + dry persistence;
6. held-out rain × local-history gating.

The final held-out null is still rejected (plus-one Monte Carlo P = 0.000999). In the 2,916-pair strictly-prior subset:

- observed boundary crossing = 0.921 vs null mean 0.814;
- observed taxonomic-deepening share = 0.399 vs 0.316;
- observed within-core share = 0.079 vs 0.186.

**Ecological interpretation:** frog chorus reactivation has organization beyond independent species rain sensitivity plus a fixed map of historically good sites.

This is a positive ecological finding, not merely a failed model: **the active chorus community behaves as a structured state-dependent system.**

## 4. The strongest unexpected result

The most surprising result is not the 98% recurrence by itself.

The strongest unexpected conjunction is:

> **Previously silent species × sites often jump directly to strong/full chorus states, and once a species re-enters a route, the excess response is concentrated in third-and-later occupied sites rather than its first or second site. Those multi-site strong choruses preferentially reappear at historically favoured physical sites.**

A simple "rain makes more frogs audible" model does not naturally predict all three:

1. direct silent → full-chorus transitions;
2. coordinated multi-site spatial deepening;
3. historical site-specific recurrence.

This conjunction should be the centre of the Results and Discussion.

## 5. Novelty claim: strong but defensible wording

Avoid an absolute "first demonstration" unless a systematic review is completed.

Preferred wording:

> **Previous studies have established rainfall-sensitive anuran calling, short-term assemblage turnover and breeding-site fidelity separately. Here we connect these levels by testing how an environmental pulse is allocated across a repeated species × site community matrix. The results show that recent-rain conditions preferentially re-express historically recurrent, site-structured strong chorus states rather than producing a uniform increase in acoustic activity.**

Higher-level version:

> **The study turns a familiar natural-history response—frogs calling after rain—into a community-level test of how fast environmental forcing exposes slow spatial structure.**

## 6. Three questions for the integrated manuscript

### Q1. Does recent rain simply amplify calling, or switch silent local assemblage elements into strong chorus states?

Primary evidence:
- active footprint / local richness / route richness;
- CallingIndex decomposition;
- 0→CI2/3 and 0→CI3;
- same-observer + same-site and acoustic-condition robustness.

### Q2. Is the spatial pattern created de novo, or does rain re-express a persistent species × site template?

Primary evidence:
- exact four-component matrix decomposition;
- multi-stop spatial-depth decomposition;
- strong-chorus contribution to third-and-later stops;
- strictly-prior recurrence;
- same-site targeting;
- opportunity-normalized rain × historical recurrence.

### Q3. Can simple ecological ingredients generate the observed chorus-state geometry?

Primary evidence:
- nested null ladder from uniform activation through held-out rain × local-history gating.

Conclusion:
- structured reactivation is established;
- a unique lower-level generator is not.

## 7. Generality without overclaiming

### Strong generality supported inside NAAMP

- 57 species represented in strong-chorus decomposition;
- 28 have positive contributions;
- top species = 13.9% of positive mass;
- top five = 49.2%;
- HHI = 0.074;
- leave-one-species-out totals remain positive;
- leave-one-state-out totals and CIs remain positive.

### Heterogeneity that must remain visible

- state-specific positive point estimates: 13/19;
- state-specific entirely positive CIs: 6/19;
- population slope = 1.65;
- state random-slope SD = 3.46.

Thus the correct statement is:

> **The phenomenon is not dependent on one species or one state, but its strength is geographically heterogeneous.**

### External scope

FrogID supports the broader phenomenon that wetter conditions are associated with greater taxonomic depth within already-active frog recordings, but it cannot replicate NAAMP's species × site matrix geometry.

Universality of the full fast-gate × slow-template mechanism is therefore not established.

## 8. Manuscript hierarchy

The paper should remain unmistakably a **frog ecology paper**.

### Biological object
Rainfall-sensitive reproductive acoustic behaviour of frog assemblages.

### Core frog discovery
Rainfall is associated with coordinated re-entry into strong chorus states across historically recurrent breeding/listening sites.

### General ecological consequence
Short behavioural pulses can expose persistent spatial organization that is invisible in inactive snapshots.

### Methodological machinery
Incidence decomposition and nested null models are evidence for the biological claim, not the story itself.

## 9. Candidate titles

Preferred:

**Rainfall gates the re-expression of persistent spatial structure in frog chorus communities**

Alternative, more frog-forward:

**Rain reactivates historically structured frog choruses across breeding sites**

Alternative, more general:

**Environmental pulses reveal persistent spatial structure in frog chorus communities**

Avoid:
- "memory" in the title;
- "latent network" unless clearly defined;
- "metacommunity" as the main noun if it invites demographic-connectivity interpretation;
- a title centred only on "boundary-biased" allocation.

## 10. One-sentence take-home

> **Across 15 years of standardized frog surveys, recent-rain conditions did not merely increase calling: they repeatedly switched historically favoured species × sites from silence into strong, spatially deep choruses, revealing a persistent chorus landscape whose full organization cannot be reduced to uniform activation, species-specific rain sensitivity or static site history.**


## 11. Higher-order spatial coherence update

A new post-freeze endpoint-fixed test directly evaluated whether multi-site spread contains higher-order dependence beyond first-order recruitment and spread.

For each route-new taxon with k occupied wet stops, e=max(k-1,0) and higher-order mass=choose(e,2). The statistic is therefore zero through the second occupied stop and grows when extra-stop incidences accumulate within the same taxon at third-and-later sites.

Observed:
- route-new-species β = 0.1847;
- extra-stop β = 0.6043;
- higher-order within-taxon β = 1.5240.

At the observed first-order coefficients:
- uniform null predicted higher-order β = 1.1384; conditional residual 0.3856 vs null 95% −0.0984–0.0959; P=0.000999;
- persistence null predicted 0.7836; conditional residual 0.7404 vs −0.0805–0.0824; P=0.000999.

The prefixed PASS rule was met under both nulls.

This materially strengthens the ecological interpretation. The key result is no longer only that recruited taxa occupy more sites. **At the same number of recruited taxa and the same total amount of extra-stop spread, the extra spatial participation is too concentrated within the same taxa for the tested independent-cell activation processes.**

The preferred general principle is now:

> **A fast environmental gate can expose higher-order spatial coherence on a slow species × site template.**

For frogs, the biological discovery is:

> **Recent-rain conditions are associated with silent-to-strong chorus transitions that deepen disproportionately within the same taxa across several sites and preferentially reappear at historically strong species-specific sites.**

Do not replace "coherence" with "synchrony": route stops were surveyed sequentially.
