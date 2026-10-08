# v3.9 — River-flow arrival without local rain: an independent six-site acoustic contrast

**2026-10-08. Published-data extraction + ecological hypothesis clarification ONLY.**
This is an **external published paper's design**, not new frogcs biological analysis, replication, experimental result or preregistered validation. No original frog calling files or new model outcomes were read; JAE RC6 and `main` remain unchanged.

## 1. A stronger natural contrast exists than the Nebraska two-site series

Sarker et al. (2022), *Ecological Indicators* **145:109640**, DOI [10.1016/j.ecolind.2022.109640](https://doi.org/10.1016/j.ecolind.2022.109640), monitored frog acoustic chorusing at **six separate Gwydir catchment sites** for up to four nights immediately before and after river-flow arrival. Flow consisted of managed environmental releases together with water from natural catchment runoff and tributaries. The paper provides site-specific rainfall and temperature context, rather than only a broad wet/dry route-level indicator.

**Immutable transcription of their published Table 2 exposure columns:** `reference_routes/GWYDIR_SARKER_2022_SIX_SITE_EXPOSURE_TABLE2_V39.csv`. These rows contain **no calling responses** and should never be treated as a newly collected raw source dataset. See the [publisher's original full article](https://www.sciencedirect.com/science/article/pii/S1470160X2201113X) and [author-university published PDF](https://researchonline.jcu.edu.au/77067/1/77067.pdf).

### Prespecified source-only pattern visible in Table 2

| Flow-arrival recording site | Prior period rain (mm) | After period rain (mm) | Site environment |
| --- | ---: | ---: | --- |
| Allambie Bridge (ALLB) | **0** | **0** | temporary river channel |
| Gundare (GNDR) | **0** | **0** | permanent in-stream weir |
| Carol Creek (CARC) | 0 | 4.6 | permanent creek |
| Combadello (CMBD) | 0 | 4.6 | permanent in-stream weir |
| Tyreel (TYRL) | 0 | 4.6 | permanent in-stream weir |
| Gingham Waterhole (GINW) | 35.5 | 0 | temporary floodplain wetland |

**Two of six sites have zero reported rain in both recorded exposure periods** despite flow arrival. Three other sites have zero rain in the prior period and 4.6 mm in the after period. One site has 35.5 mm prior and zero after. These are the **paper's original rainfall summary fields**, not a guaranteed complete minute-by-minute rain-audio record. Do not infer there was no running-water or other acoustic cue, because a flow event itself produces sound.

**Published biological results** (from the original Sarker authors; not freshly calculated here): nocturnal chorusing species richness increased modestly overall, with three sites showing increased richness and others not, and certain species responding in opposite directions (e.g. *Limnodynastes tasmaniensis* increased, *L. fletcheri* decreased). Some acoustic taxa were only measured for one historical flow event per site. This pattern **supports the biological plausibility of direct hydrological opportunities with little local rainfall**; however **before–after observational comparisons cannot isolate the causal effect of water versus temperature, phenology, managed upstream operation, social cues or flow sounds**. A non-significant rain coefficient in the published model is also not equivalence/no-rain-causality proof.

## 2. Why this helps the frogcs causal problem

The existing frogcs/JAE RC6 study already established:
- rain selectively associated with stronger full-chorus expression at historically strong species×physical-site locations (directional β 0.02449, CI 0.00700–0.04198);
- the route-cross-fitted rain×prior-site propensity generator **underpredicts** the observed within-taxon cross-site concentration (1.3323 predicted vs 1.6503 observed);
- direct event-varying local hydrology remains **unmeasured** in national USGS NAAMP `Stops.csv`.

Sarker provides a **natural exposure separation**:

```
river-flow arrival ──> new wetland water/inundation
         |                          |
       (could make sound)           ↓
                             opportunity to chorus

local rainfall ──> rain sound / immediate weather cue
```

In sites without local recorded rain during those comparison windows, acoustic changes following flow arrival cannot all be described as **immediate local rainfall sound as a necessary condition**. This does **not** prove that the actual change was caused solely by water. The paper does not randomly assign local rain, river flow, temperature or site occupancy, and the local acoustic stimulus of running water remains distinct from rain sound.

**The new research discriminant is an event-specific 2×2 exposure matrix, not just adding a rainfall interaction:**
- **no local rain / physical inundation arrives** (Sarker-like natural water arrival);
- **local rain / no local water rise yet** (possible immediate rain-sound cue);
- **rain + inundation**;
- **neither**.

All four cells require verified environmental exposure, **species-presence opportunity** and comparable acoustic detection. The published Gwydir six-site observational study does not, on its own, supply a balanced causal factorial with all four cells. Do not invent its missing cells from site labels.

## 3. Could the published 6-site data be a frogcs spatial replication?

**No direct replication.** The original study summarizes nine species and site-specific chorusing around one flow arrival, but:
- the independent wetland site count is six, not ten fixed route stops, and water arrivals vary across calendar dates/site types;
- no strictly prior, independent species×physical-wetland **historically strong CI2–3 site template** or analogous CallingIndex depth series is supplied in the summary;
- flow/rain windows, nocturnal recording opportunity and site availability differ;
- the published repository researchdata.edu.au entry for the underlying long-term Sarker research data indicates **closed access** for the archived raw dataset, so only paper-level observational contrasts are presently usable here (no auth bypass or private access).
- one site (GINW) has seven instead of eight acoustic nights owing to a missed post-flow night.

Thus a site-level pre/post difference in the published paper, even when rainfall is 0, is **not** a held-out test of the NAAMP conditional within-taxon concentration, deep k≥4 coupling or history targeting.

## 4. Better Stage 0 sampling design grounded in real phenomena

A source-grounded future observational study should first seek **true independently timed water arrivals and rain cues** at multiple verified wetlands:

1. Record physical water height, inundation, locally measured precipitation, water temperature, and *airborne sound spectrum* continuously, before, during and after actual water changes. Water-arrival sound itself may trigger calls.
2. Sample several independent historical-chorus/less-historical ponds and use synchronized recorders, with a measured sound-propagation/interference map. Record preexisting acoustic activity and probable animal availability separately.
3. Freeze rain and water-state *lead/lag definitions* from the source metadata and environmental monitors before reading frog outcomes. Confirm there are actual observations in **both cue-discordant strata** (`rain=0, water_change=1` and `rain=1, water_change=0`), not only the trivial jointly dry/jointly wet cases.
4. Distinguish marginal animal-produced calling, entire joint calling vector under interventions, and **exact-k conditional spatial prediction** (a predictive, not controlled causal effect).
5. Use planned within-pond and across-pond negative controls, observer/detector calibration, exact time-of-night and site-year blocking, and no post-selection of taxa/cases based on favourable signs.

**Stop early** if rainfall and local water are always perfectly coupled, if physical sites cannot be validated, if wetland detection is too masked during rain, or if only a two-wetland series is obtainable. Do not use a fabricated simulation to supply environmental events that were not observed.

## 5. Sources and status

- Sarker et al. (2022), DOI 10.1016/j.ecolind.2022.109640, published Table 2, Fig. 5 and methods; see source link above.
- Original public long-term data catalog: [Long-term monitoring of frog populations in Response to environmental watering in the Gwydir River Catchment, NSW](https://researchdata.edu.au/long-term-monitoring-australia-dataset/2972434), **Access: Closed** in the catalogue.
- Nebraska other candidate: [Brinley Buckley et al. (2020) Mendeley](https://doi.org/10.17632/p6nbn2hyz9.1), two wetlands, data-file API 401 and candidate PMC HEAD 404; [actual source access receipt](V3_8_ACCESS_RECEIPT_AND_SCIENTIFIC_STOP_2026_10_08.md).

**This is an incremental real-data *source-design* advance**: water without local rain is a documented environmental comparison. It is **not a novel result about frogcs**, nor proof that water alone explains chorus changes. No new amphibian response values, power analysis, field intervention, custodian communication or RC6 scientific changes were made.
