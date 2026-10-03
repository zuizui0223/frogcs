# Closest prior-study and novelty audit v0.1

## Purpose

Identify the closest published precedents to the current frogcs claim and define the narrowest novelty statement that remains defensible in 2026.

This is a targeted literature audit, not a systematic review. It does not authorize "first ever" language.

## Closest ecological precedents

| Study | Biological scale | What it already established | What it did not test |
|---|---|---|---|
| Brooke, Alford & Schwarzkopf 2000, *Behavioral Ecology and Sociobiology* 49:79–87, DOI 10.1007/s002650000256 | 1 species, 6 locations along a 560-m transect, one breeding season | Daily calling varied among sites; after persistent site differences were removed, up to 35.8% of among-day variation was attributable to factors common across sites such as weather, moonlight or large-scale social facilitation | Multi-species allocation of a pulse; conditioning on total activation; taxon-specific historical site use |
| Trenham et al. 2003, *Ecological Applications* 13:1522–1532, DOI 10.1890/02-5206 | 8 wetland-breeding species, statewide Wisconsin monitoring | Population/calling fluctuations showed weak intraspecific synchrony across sites up to 50–100 km; rainfall was more strongly synchronized and abundance was associated with rainfall 1–4 years earlier | Short rain-recency pulse; joint species × site calling allocation; recurrent strong-chorus SiteID targeting |
| Guzy et al. 2012, *Journal of Applied Ecology* 49:941–952, DOI 10.1111/j.1365-2664.2012.02172.x | Calling intensity at 42 Florida wetlands over multiple years | Repeated calling-index data revealed persistent species groups and wetland structure; species co-occurrence and wetland condition could be identified from call data | Event-scale pulse allocation; whether a fixed amount of calling becomes disproportionately concentrated within the same taxa |
| Sugai et al. 2021, *Journal of Animal Ecology* 90:673–684, DOI 10.1111/1365-2656.13399 | 39 Pantanal anuran assemblages, fine temporal acoustic sampling | Calling assemblage composition changes strongly at fine temporal resolution; habitat and ecological context explain part of temporal compositional change | Repeated fixed-site pulse allocation and historical taxon × physical-site recurrence |
| Sarker et al. 2022, *Ecological Indicators* 145:109640, DOI 10.1016/j.ecolind.2022.109640 | 9 acoustically detected species at 6 sites, four nights before/after river-flow arrival; longer 16-site surveys | An explicit hydrological pulse changed chorus richness and species-specific chorusing; richness increased at three sites but not others and species responses differed | Conditional allocation of a fixed amount of post-pulse calling among taxa; strictly-prior species × site history; deep-tail/site-pair concentration |
| Thompson et al. 2022, *Diversity and Distributions* 28:2375–2387, DOI 10.1111/ddi.13634 | 100 Australian frog species, >150,000 citizen-science records, continental scale | Species-specific meteorological determinants of calling and strong heterogeneity among taxa | Repeated local species × site matrix structure or within-taxon multi-site dependence |
| Brodie, Allen-Ankins & Schwarzkopf 2025, *Ecosphere* 16:e70153, DOI 10.1002/ecs2.70153 | 17 species, 3 fixed breeding sites, Oct 2012–Apr 2014, two wet seasons | Nightly chorusing was highly correlated among sites for many species; many explosive breeders began chorusing on/around the same rain events across sites; species had consistent or idiosyncratic site patterns | A multi-species test asking whether the same total post-rain calling is more concentrated within taxa than species-specific response and site structure predict |
| Chirino et al. 2025, *Philosophical Transactions B* 380:20240050, DOI 10.1098/rstb.2024.0050 | 1 species, 18 months PAM | Direct/indirect environmental drivers of calling, including recent rainfall and humidity | Community-level spatial allocation |
| Rush et al. 2026, *Ecology and Evolution* 16:e74191, DOI 10.1002/ece3.74191 | 1 species, 10 populations, 12 months | Region-specific synchrony, phenology and rainfall/environmental windows across sites | Multi-species allocation and conditional dependence after first-order species/site effects |

## Which papers are genuinely closest?

### Closest in ecological design: Sarker et al. 2022

Sarker et al. already contains:
- an explicit environmental pulse (arrival of river flow/inundation);
- multiple frog species;
- multiple acoustic sites;
- before/after event comparison;
- species- and site-specific heterogeneity in chorusing.

Therefore frogcs must **not** claim that it is the first multi-species, multi-site frog study of an environmental pulse.

What frogcs adds is an allocation-level question:
> Given the amount of calling expressed after the pulse, how is that activity distributed among taxa and sites?

### Closest in cross-site chorus organization: Brodie et al. 2025

Brodie et al. already contains:
- 17 species;
- three fixed breeding sites;
- nightly chorusing over two wet seasons;
- pairwise correlations of chorusing activity among sites for each species;
- strong cross-site correlation for many species;
- rain-associated onset of explosive breeding.

Therefore frogcs must **not** claim that it is the first demonstration that frog choruses covary across sites or that rain can be associated with coordinated-looking cross-site chorus expression.

What frogcs adds is a conditional matrix test:
> Does within-taxon multi-site expression exceed the amount expected after species-specific rain response, prior species × physical-site use, dry-state persistence and total wet incidence are represented?

### Closest in repeated species × wetland structure: Guzy et al. 2012

Guzy et al. already used repeated calling-index data across 42 wetlands and found persistent species/wetland group structure.

Therefore frogcs must **not** claim that recurrent species × wetland acoustic structure is itself novel.

What frogcs adds is the coupling of that slow site structure to a short rain-recency contrast, and a direct test of whether prior species × site propensity is sufficient to generate the observed wet-state allocation.

## What is *not* novel

Do not sell any of the following as the central discovery:

- frogs call more under favourable wet/weather conditions;
- environmental events can trigger explosive chorusing;
- calling responses differ among species;
- frog chorusing can covary across spatially separated sites;
- species have repeated/persistent differences among chorus sites;
- frog community richness/composition can change after inundation;
- species × site incidence matrices contain non-random structure;
- constrained null models can detect aggregation/co-occurrence;
- the number of sites at which a species is recorded is an ecological incidence summary.

All have strong prior literature.

## What remains novel

The narrow novelty is the **conditional allocation question**.

For 2,916 matched comparisons with strictly-prior physical-site history, frogcs asks whether a fixed wet-state calling response can be reconstructed from:

1. route-cross-fitted taxon-specific rainfall response;
2. strictly-prior taxon × physical-SiteID propensity;
3. dry-state persistence;
4. matched total wet calling incidence;
5. and, in the strongest sensitivity, a held-out rain × local-history gate.

The observed within-taxon site-pair concentration remains larger than the comparator expectation:
- observed concentration beta = 1.6503;
- principal prediction = 1.3535;
- conditional residual = 0.2969;
- null residual 95% interval = -0.1319 to 0.1187;
- P = 0.000999.

The exact-depth audit further shows that this is not a third-stop threshold:
- marginal depths 1–3 lie within both primary null envelopes;
- marginal depths 4–10 exceed both;
- the biological pattern is a **deeper/heavier calling-incidence tail than expected**.

Historical targeting then adds a second distinct piece:
- prior strong physical SiteID predicts later wet CI2/3 within the same pair and taxon (beta = 0.1511);
- rain advantage strengthens full-chorus targeting at those historically strong sites (beta = 0.02449).

## The actual gap filled

The literature has separately established:

```
environmental pulse/weather
        ↓
calling amount / phenology / richness
        ↓
species-specific responses

and

repeated sites
        ↓
cross-site covariance / synchrony
        ↓
persistent species × site differences
```

frogcs asks a different conditional question at their intersection:

> **After those first-order species and site patterns are explicitly represented, is the joint species × site expression of the pulse still non-independent?**

The supported answer within NAAMP is yes: wet-state calling is more concentrated within the same taxa than the tested first-order generators reproduce.

## Strongest novelty wording

### Frog-specific

> Recent-rain calling is expressed across an unexpectedly deep set of separated route stops within the same taxa, and strong calling is preferentially re-expressed at taxon-specific historical physical sites.

### Analytical

> After matching total calling incidence and representing transferable taxon rainfall responses, strictly-prior taxon × site propensity and dry-state persistence, the observed wet-state calling remains more concentrated within taxa than predicted.

### General ecological

> Environmental pulses may change not only marginal activity but the **dependence structure of joint species × place expression**.

## Claims to avoid

Do not claim:
- first multi-site frog chorus study;
- first multi-species environmental-pulse frog study;
- first evidence of cross-site chorus synchrony;
- first evidence of recurrent chorus locations;
- first evidence that weather coordinates frog chorusing;
- first demonstration of hidden/latent spatial community structure;
- a third-stop biological threshold;
- exponential spatial spread;
- movement, colonization or arrival among stops;
- individual memory or philopatry;
- universal pulse-revealed dependence.

## Novelty assessment

The novelty **survives**, but only in a narrower form than a generic "rain reveals spatial structure" claim.

Sarker 2022 and Brodie 2025 remove novelty from:
- pulse-associated multi-site chorus change;
- cross-site chorus correlation;
- species-specific site responses.

Guzy 2012 removes novelty from:
- repeated species × wetland calling structure.

Thompson 2022 and recent PAM work remove novelty from:
- broad species-specific environmental response functions.

What remains is not a new component but a **new conditioning problem**:
> whether the multi-site allocation of a short behavioural pulse contains residual within-taxon dependence after the known component processes are already represented.

That is sufficiently distinct to support the present manuscript, especially because it is tested over 53 taxa, 585 routes, 21 states and 15 years rather than demonstrated in one species or a handful of sites.
