# 2024 Hungary restored wetland amphibian monitoring (Zenodo 15044115)

**Source and attribution:** Mizsei, Edvárd & Wenner, Bálint (2025). *Effectiveness of wetland restoration on amphibians in a drying grassland habitat losing its breeding sites.* Zenodo. DOI: https://doi.org/10.5281/zenodo.15044115

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. The two source files are preserved unmodified with their original column names. The research analysis, derived tables, source data and code must all retain the above credit and DOI. No claim of author endorsement is made.

Raw source access:
- https://zenodo.org/records/15044115/files/wetland_amp_site_data.csv?download=1 — source MD5 `795da443249760fbc0bf30249910a4ef` (per Zenodo record).
- https://zenodo.org/records/15044115/files/wetland_amp_surv_data.csv?download=1 — source MD5 `edcd6f12518192c01e3dbae8521c16c9` (per Zenodo record).

## Data and limitations

- 2024, Hungary; **29 unique site records**, 381 survey rows and nine named amphibian taxa. Survey methods: acoustic 129, visual 129, dipnet 59, bottletrap 64. Acoustic surveys detect call presence **not chorus intensity**. Non-acoustic survey records are different detection processes.
- Site covariates: water depth, emergent plant percent cover, submerged plant cover, count of plant species, restoration class, hay/mud interventions, fish presence (only **two fish-positive sites**), elevations.
- Weather in survey table includes day-of-year, temperature, humidity and precipitation. These are **not NAAMP matched Wetter–Drier rain contrasts**.
- No repeat years, so strictly prior year-to-year strong SiteID site-history cannot be evaluated. Never equate within-spring detection to true individual site fidelity.
- Seasonal survey dates and methods differ among sites. Any pooled visit model must control observation method and date/phenology, plus site-level clustering and imperfect detection.
- Two fish-positive sites make an emergent × fish effect too poorly supported to estimate credibly; tests must predeclare **non-estimable** for this interaction in this dataset.
- Site-level covariates are measured for 2024; cannot infer their change or environmental causality from this one-year panel.
- Source data are available as CC BY; please cite and credit original creators as above.

Analyses are defined in [../../scripts/hungary_vegetation_chorus.py](../../scripts/hungary_vegetation_chorus.py) and separate from locked frogcs RC6.
