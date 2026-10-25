# Rain-pulse chorus, recurrent frog locations and emergent wetland interaction architecture — empirical macro synthesis

Date: 2026-10-25. **This synthesis combines independent evidence; it is not a pooled effect-size meta-analysis.** It does not alter frogcs's frozen RC6 manuscript. Observational and published findings have distinct data units and estimands.

## 1. Supported facts on a shared hierarchy

| Biological scale | Data and truly supported result | What is NOT identified |
|---|---|---|
| Hours/days (environmental pulse) | [frogcs RC6](../../provenance/CURRENT_RESULTS.json): 4,236 wetter/drier NAAMP pairs; acoustic silence→overlapping/full chorus and observed same-taxon multi-site concentration 1.6503 versus matched comparator 1.3535 (+0.2969 residual). | Actual spawning, abundance, weather causality, direct predators or wetland water level. |
| Species×location years | [NPS 2016–2023](nps_glkn_history/observed_results.json): 66 fixed stations, 7 parks, 13 taxa total. Conditional historical prior CI≥2 predicts later-year same-taxon CI≥2: park×species×year fixed-effect slope +0.4674; +0.4642 (+0.3826,+0.5331 cluster CI) after other-species prior station hotness, hydroperiod class and effort. | Individual philopatry, vegetation and hydroperiod events, rain response, synchronized 10-stop concentration. |
| Additional strong vs weak prior site use | [NPS post-hoc sensitivity](nps_glkn_weak_vs_strong/observed_results.json): conditional on prior same-species detection, earlier strong vs weak CI predicts later strong CI (+0.3889 adjusted, cluster interval +0.2965 to +0.4621), with leave-one-park-out all positive +0.4267 to +0.5057. | Confirmatory preregistered effect or stable genetic/demographic memory. |
| Site / year with macrophyte fraction | [Hungary 2024](hungary_2024_screen/observed_results.json): 29 sites, 129 acoustic visits. Weather/season site-balanced Brier 0.2080; +depth/class 0.1742. Adding emergent percent cover to that model 0.1753 (no gain, 2000-site-bootstrap score-gain interval includes zero). | Strong-call CI intensity, multi-year site fidelity, vegetation structure, fish moderation (only 2 fish-positive sites). |
| Plant × fish at site occupancy | Hamer et al. 2021, 55 Australian wetlands / 11 species: community occupancy coefficient fish −1.223 (95% BCI −2.381 to −0.128), fish × emergent +1.183 (+0.269,+2.162), but plant main effect −0.871 (−1.816,+0.030). DOI 10.1002/eap.2293. | Acoustic history at these sites or predation rates; direct comparability to Hungarian Brier or NPS FE slope. |
| Plant-engineering manipulation | Lishawa et al. 2023, Great Lakes coastal Typha manipulation: fish/invertebrates, larval amphibians, plants, dissolved oxygen measured across treatment/control and aquatic channels; plant biomass/litter removal and connection changed communities. DOI 10.1111/fwb.14141, raw data DOI 10.5061/dryad.wdbrv15tb. | Frog adult chorus or same-site strong CI2/3 history in this experiment. |
| Ontogenetic network mechanisms | GloBI recorded stage-resolved predation edges in a first occurrence-level pilot, including reciprocal same-species pairs. [Pilot](../GLOBI_TROPHIC_DIRECTION_PILOT_2026-10-25.json). | Verified *population-flux* direction reversal, simultaneous co-occurrence or exact local predation rates. |

## 2. Specific new conclusion and unresolved mechanism

**Strongest now-supported macro-level statement:** species-specific strong frog chorus use at repeatedly monitored locations is temporally persistent across both NAAMP (prior physical SiteID) and an independent NPS programme, and a uniform broad-weather or generic site-wide chorus proxy alone is insufficient to account for all observed organization in the models evaluated.

**Not supported:** a direct conclusion that vegetation or trophic interaction causes the unexplained NAAMP configuration, or that a vegetation interaction explains the NPS annual strong-site memory. These must remain future hypotheses.

The **site-history statistic is not equivalent** between programmes. NAAMP: β=0.151 for within-pair/site historical CI2/3 targeting and joint multi-site concentration residual +0.297. NPS: +0.464 annual within park×species×year strong calling adjusted risk-difference-style association. Do not pool or express a '2.8x replication effect'.

## 3. Biologically distinctive hypotheses for the next full macro-analysis

**H-plant ("habitat structural persistence").** Recurrent sites arise because the same emergent plant **architecture** (stems, stem height, submerged stem area, shallow-margin mosaic, plant taxon, open water) and local hydrology persist or reappear between years; those plants permit species-specific courtship display, egg attachment and habitat access.

**H-interaction ("historical biotic filtering").** Sites differ not just in structural resources but in fish, odonate, salamander and egg/tadpole **stage distributions**; prey refugia and predatory ambush sites alter when calling adults and recruitment cohorts are spatially attractive. Test full `fish×emergent`, `odonate_larva×submerged` and `hydroperiod×predator` and differentiate adult chorus from egg/tadpole survival.

**H-behavior ("conspecific and eavesdropper").** Attraction to existing conspecific choruses or predators/parasites listening to frog acoustic cues (established in bats/biting midges) affects local chorus organization; underwater predator use of airborne frog chorus as a danger cue is not directly established. Playback with appropriate sound propagation controls needed to distinguish from common environmental drivers.

**H-history ("plant-stage interaction template").** A high density of `Typha` may not produce maximal suitability: mixed edge habitats can permit adult calling, eggs and tadpole refuges, but dense monocultures alter fish access, oxygen and predators. Predict stage-specific sign changes rather than a universally positive cover slope. Structural mosaics and vegetation turnover across years are the proper ecological variables.

## 4. Proposed causal/time model and discriminating test

```text
Climate rainfall/temperature (t) -> actual wetland water state (t)
Past plant architecture (t−1) + wetland age/connectivity -> plants/inundated stems (t)
Past predator guild and stages (t−1) -> fish/odonate/salamander stages (t)
[water state × plant architecture × biotic stages × frog reproductive readiness]
    -> frog chorus state/site pattern (t, hours/night)
    -> egg deposition (t + days) -> tadpoles (t + degree-days)
    -> metamorph recruitment (t + weeks/months)
```

Compute two distinct outcomes:
- **Marginal prediction**, detection-adjusted probability of CI≥2 at species×verified physical wetland×event.
- **Conditional spatial configuration** preserving first-order taxon/rain propensity, prior-site use, total activated incidences, without conditioning all `k_i` (which fixes `C`).

A useful future success criterion is *not* finding significant plant coefficients. It is that a hydrology + plant morphology + biotic stage model, trained on earlier years/sites, predicts later **configuration** better and substantively attenuates NAAMP-style species×site residual dependence and prior-strong targeting. If local wetland structure alone removes the residual, that is an informative **environmental mechanism**, and no unsupported species-interaction claim should be retained.

## 5. What remains blocked

- Raw Dryad site-level data for Hamer's 55 ponds and Lishawa's Typha experiment are located/verified but raw downloads were blocked by the remote service in this session. Do not claim we refit them.
- Neither NPS nor Hungary currently contains the simultaneous measurement **strong historical frog chorus + time-varying emergent plant architecture + aquatic predator stage densities**. Literature cases cannot be naïvely concatenated into that panel.
- Site geocoding for original NAAMP is flagged as unreliable in [coordinate QC](../../revision/NAAMP_COORDINATE_GEOMETRY_QC_V0_1.md); do not arbitrarily join NWI polygons or remote-sensing plant fractions.
- Source-dependent survey effort, phenology, method differences and historical occupancy priors require continued QC. NPS source offers broad `Hydroperiod` class, **not** actual rain amount; Hungary reports precipitation at visits but only one season.
- eDNA methylation can be a *later* stage-observation assay after calibration; it is not an existing eavesdropping or trophic-flux sensor.

## 6. Outputs and reproducibility

- [Source-pinned NPS schema](nps_glkn_schema/schema_receipt.json) and [main NPS results](nps_glkn_history/observed_results.json), [source and method](nps_glkn_history/REPORT.md).
- [Post-hoc NPS weak-versus-strong sensitivity](nps_glkn_weak_vs_strong/observed_results.json).
- [Hungary source-backed observed predictive analysis](hungary_2024_screen/observed_results.json), [method and limits](hungary_2024_screen/REPORT.md).
- All scripts and read-only GitHub CI workflows live in [research](../README.md). Neither a new frogcs JAE claim nor eDNA state detection is asserted from these independent datasets.
