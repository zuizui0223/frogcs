# Ontogenetic environmental association: global aquatic immature vs adult reporting in 1° wetland structure

2026-10-25. **Specification fixed before opening this cross-stage habitat outcome**, following a non-supportive matched GloBI prey-partner/wetland background control. Exploratory spatial reporting test, not preregistered causal inference, no RC6 main modifications.

### Ecological question

For species appearing in the *full fixed-release GloBI aquatic-focused food web* and in the **GBIF public experimental August 2026 entire Anura/Odonata taxon-partition** scan, are records explicitly marked as aquatic `Larva/Nymph/Tadpole` more commonly associated with **historical regularly flooded vegetation** than records marked `Adult/Imago`, within the *same species × comparable region × seasonal survey month*?

A larger within-species immature-stage flooded-vegetation context would indicate **reported-stage spatial niche segregation**, which is a necessary precursor for a wetland stage-dependent interaction hypothesis. It is **not** a survival advantage, prey/captured interaction, natural abundance, habitat preference or individual developmental movement.

### Data and fixed sources

- Original GBIF 2026-08 experimental 1° species×stage×grid×year×month occurrence stage cube, limited to **expanded source-selected ~73 Anura/Odonata species** aligned to full 2026-09 GloBI v0.11 (DOI 10.5281/zenodo.22691479). No Caudata/Dytiscidae full partition or native-range exhaustiveness.
- EarthEnv Tuanmu & Jetz 2014 full 1km source class 8 *regularly flooded vegetation*, class 12 *open water*, class 6 *generic herbaceous* 1° average, historical 1990s–2000s conditions. Exclude missing raster cells, **open water ≥50% of the 1° cell** as ocean-dominated coastal backgrounds; keep them separate in QC.
- Subset stages `adult` and `aquatic_immature` exactly, excluding unknown, egg or juvenile. Keep species eligibility based on **GBIF label/report volumes before examining landcover**: at least 30 distinct species-stage × 1°×year×month reporting cells for each stage and at least 5 distinct 1° cells per stage. This guards scarce age-labels but does not fully correct missingness.
- Deduplicate by 1° grid-cell identity **within calendar month** across years when comparing spatial backgrounds to avoid giving 15 years of reports from the same 1° grid 15 pseudo-replicates.

### Main within-stage reporting contrast

1. Spatial background terms: `flooded_vegetation_pct`, `open_water_pct`, `generic_herbaceous_pct`. All are raw consensus percentage scores, not guaranteed mutually exclusive wetland fractions.
2. Within **species × latitude decile (floor(latitude/10)×10°) × calendar month (1…12)** strata, compute mean EarthEnv landcover over unique 1° cells with reported adult and immature stage. Require at least **3 distinct stage-positive grid cells on each side**, and at least **two non-identical total cells**; otherwise stratum is insufficient and excluded with counts. Longitude is not controlled by the latitude band, so report continental range bias as a remaining limitation.
3. Define `Δ_stratum = mean(flooded | immature reports) − mean(flooded | adult reports)`; also `Δ(open_water)` and `Δ(generic_herbaceous)` as independent, identically computed negative/background comparisons.
4. Equally weight eligible latitude-band/month strata within species (do not weight by number of GBIF photographs), and then equally weight species within Anura and Odonata orders. Report distribution/median/sign of species deltas and ***species-cluster bootstrap confidence intervals*** only when ≥8 species are eligible in a given order. These are exploratory reporting-structure uncertainty, not effects on life-stage abundance.
5. Sensitivity stricter **species×latitude band×calendar YEAR×month** with ≥2 distinct grid cells per stage; report if feasible; do not change eligibility thresholds based on results.
6. Negative controls: compare the `Δ flooding` to `Δ generic herbaceous` and `Δ open water` *within the same species and strata*. If flooded does not separate stages more consistently than generic vegetation, the wetland-specific structural-niche claim is not supported.
7. No adaptive optimization or global p-values; retain all excluded species and strata. Document regional/hemispheric bias and variation across sources, introduced species, taxonomic drift and differential detectability/observer effort.

### Not inferable

GloBI's named diet edges do not indicate prey capture where GBIF reported stages. Neither field colony, frog chorus, antiphonal response, larval survival, annual hydrological variability, current reed/cattail density, eDNA methylation nor predator/prey demographic dominance is provided. This is a global **life-stage observation-environment association** only, not a causal tropic-reversal test.
