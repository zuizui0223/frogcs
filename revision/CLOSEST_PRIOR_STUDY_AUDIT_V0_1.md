# Closest prior-study audit v0.1

## Purpose

Identify the frog studies closest to the RC4 design and state exactly what remains novel after those precedents are acknowledged.

This is a targeted literature audit, not a systematic review. It does not authorize "first ever" language.

## Closest precedents

| Study | Scale / design | What it already shows | What it does not test |
|---|---|---|---|
| Brooke, Alford & Schwarzkopf 2000, *Behavioral Ecology and Sociobiology* 49:79–87, DOI 10.1007/s002650000256 | one species, six locations along a 560-m transect, repeated through a breeding season | day-to-day calling covaries among nearby locations; common environmental factors and local/social factors both matter | multi-species species × site allocation; conditioning on taxon-specific response and historical site use |
| Trenham et al. 2003, *Ecological Applications* 13:1522–1532, DOI 10.1890/02-5206 | statewide monitoring, eight wetland-breeding species, sites separated up to 50–100 km | population fluctuations show weak spatial synchrony; rainfall is correlated with population dynamics | short-term acoustic-state allocation within repeated ten-stop matrices |
| Guzy et al. 2012, *Journal of Applied Ecology* 49:941–952, DOI 10.1111/j.1365-2664.2012.02172.x | calling intensity monitored at 42 wetlands over multiple years; species × site calling-index clustering shown explicitly for 18 wetlands | frog calling data can reveal repeated species–wetland structure and positive co-occurrence groups | environmental-pulse contrast and conditional allocation of added calling across taxa after holding total incidence fixed |
| Ceron et al. 2020, *Ecology and Evolution* 10:4630–4639, DOI 10.1002/ece3.6217 | 25 species in an Atlantic Forest metacommunity, repeated through the year | calling composition varies spatially and temporally; climate–community relationships are seasonal/nonstationary; spatial synchrony is weak | within-taxon concentration of a short pulse after taxon and site marginals are represented |
| Sugai et al. 2021, *Journal of Animal Ecology* 90:673–684, DOI 10.1111/1365-2656.13399 | 21 recorders rotated among ponds, assemblage-wide calling at fine temporal resolution | rapid assemblage-wide calling dynamics and environmental context | repeated fixed-site species × place recurrence and conditional multi-site allocation |
| Sarker et al. 2022, *Ecological Indicators* 145:109640, DOI 10.1016/j.ecolind.2022.109640 | 16 long-term sites; six acoustic sites; nightly recordings four days before and after river-flow arrival | an explicit hydrological pulse changes frog richness and chorusing; responses differ among species and sites | whether a fixed amount of pulse-associated acoustic activation is disproportionately concentrated within the same taxa, and whether that allocation reuses taxon-specific historical sites |
| Thompson et al. 2022, *Diversity and Distributions* 28:2375–2387, DOI 10.1111/ddi.13634 | 152,534 records, 100 Australian frog species, continental FrogID data | broad species-specific meteorological determinants of calling; strong seasonality and heterogeneous environmental responses | repeated physical-site matrix structure and residual dependence after species response is modeled |
| Brodie et al. 2025, *Ecosphere* 16:e70153, DOI 10.1002/ecs2.70153 | multiple frog species, three breeding sites, two wet seasons | rainfall thresholds and species-specific chorusing patterns; cross-site synchrony assessed for each species | multi-site allocation across a large repeated network and historical species × site recurrence |
| Chirino et al. 2025, *Philosophical Transactions B* 380:20240050, DOI 10.1098/rstb.2024.0050 | one species, 18 months of PAM, environmental causal-model framing | detailed direct and indirect environmental drivers of calling | community-level species × site dependence |
| Rush et al. 2026, *Ecology and Evolution* 16:e74191, DOI 10.1002/ece3.74191 | one species, ten populations, near-continuous recordings for one year | geographically heterogeneous calling phenology; relatively synchronous wet-season calling in one region; rainfall windows differ among regions | multi-species allocation and residual within-taxon concentration conditional on first-order structure |

## Strongest overlap with RC4

### Sarker et al. 2022

This is the closest **environmental-pulse × multi-site frog-community** precedent.

It already demonstrates:
- a discrete hydrological event;
- repeated acoustic sampling before and after the event;
- multiple frog species;
- multiple sites;
- richness and chorus responses that differ among species and sites.

Therefore RC4 must not claim novelty for:
- environmental pulses reorganizing frog chorusing;
- chorus richness changing after wetting/inundation;
- heterogeneous species/site responses to a pulse.

The remaining difference is the **allocation question**. RC4 conditions on how much acoustic activation occurred and asks whether those incidences are distributed among taxa as expected from species-specific rainfall responses, prior species × physical-site use and dry-state persistence.

### Guzy et al. 2012

This is a particularly important **species × site matrix** precedent.

It explicitly constructed average calling-index patterns across wetlands and identified species and wetland clusters. Therefore RC4 must not claim that representing frog choruses as species × site calling matrices is itself novel.

The difference is that Guzy et al. studied long-term wetland condition/co-occurrence structure, whereas RC4 asks how a **within-route short-term wet-state contrast is allocated inside a repeated matrix**, with historical local structure treated as part of the null rather than the response of interest.

### Brooke et al. 2000 / Brodie et al. 2025 / Rush et al. 2026

Together these studies remove any generic novelty claim about cross-site coordination:
- one-species calling can covary among nearby sites;
- multi-species chorusing can be rainfall-sensitive at multiple sites;
- calling phenology can be relatively synchronous across populations.

RC4 therefore uses neither "first cross-site coherence" nor "rain synchronizes frogs" language.

## Novelty that remains

The strongest defensible novelty is **conditional allocation**, not weather response, site fidelity, synchrony or a species × site matrix by themselves.

RC4 asks:

> Given the number of taxa that became acoustically expressed, the total amount of multi-site calling, each taxon's transferable rainfall response, strictly-prior taxon × physical-site use, dry-state persistence and observed wet-incidence magnitude, is the remaining calling allocation still more concentrated within the same taxa than expected?

The answer in the principal 2,916-pair subset is yes:
- observed concentration beta = 1.6503;
- principal comparator prediction = 1.3535;
- conditional residual = 0.2969;
- null residual 95% interval = -0.1319 to 0.1187;
- plus-one P = 0.000999.

The separate depth audit further shows that the effect is not a third-stop threshold. Depths 1–3 are compatible with the uniform-activation null; under the persistence-preserving null, depths 1–2 are lower than expected and depth 3 remains within the envelope, while depths 4–10 exceed both null envelopes. The profile therefore shifts toward a deeper within-taxon tail.

## Novelty hierarchy after this audit

### Not novel
- frogs call differently with rain, humidity or temperature;
- rainfall/wetting can increase frog richness or chorus activity;
- species differ in weather response;
- calling varies among sites;
- frog populations or choruses can covary across sites;
- species × wetland calling matrices have structure;
- historical site use can persist.

### Moderately distinctive
- strong 0→CI2/3 acoustic-state switching across a 21-state repeated monitoring network;
- a deep multi-site calling-incidence tail across spatially separated stops;
- repeated strong calling at taxon-specific physical sites.

### Strongest novelty
- **residual within-taxon concentration after explicit first-order ecological comparators**;
- **linking that conditional dependence to recurrent taxon-specific physical sites**.

## Recommended novelty statement

> Previous studies show that environmental conditions can alter frog calling across species and sites, that choruses can covary spatially, and that species × wetland calling structure can persist. Here we ask a different question: after the amount of acoustic activation, transferable taxon-specific rainfall responses and strictly-prior taxon × physical-site use are represented, is the remaining wet-state activity still non-independently allocated across sites within taxa? The observed excess indicates that it is.

## Claims to avoid

- first demonstration that environmental pulses coordinate frog communities;
- first evidence of cross-site frog calling coherence;
- first species × site acoustic community matrix;
- first evidence of recurrent frog chorus sites;
- rain causes route-scale activation;
- taxa arrive at or move through successive stops;
- a third-stop threshold;
- universal pulse-revealed dependence.

## Bottom line

The closest literature substantially narrows, but does not erase, the contribution.

The paper remains novel if it is sold as a **dependence-level community analysis of pulse-associated calling allocation**, not as a discovery that rain affects frogs or that frog calling has spatial structure.
