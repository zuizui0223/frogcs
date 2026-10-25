# Independent NPS GLKN 2016–2023: strict prior-species chorus history persists after generic site conditions

**Real empirical result**, not a second NAAMP reanalysis. Developed from a schema-only study contract [before reading NPS outcome estimates](../../NPS_GLKN_STRICT_HISTORY_HYDROPERIOD_CONTRACT_V0_1.md). Primary frozen 2016–2023 data package: U.S. National Park Service, Casper et al. 2026, DOI [10.57830/2320505](https://doi.org/10.57830/2320505), public-domain. Input source [CSV](https://irma.nps.gov/DataStore/DownloadFile/763377?Reference=2320505), SHA256 `b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2` at the time of the audit.

[Full machine-readable observed results](observed_results.json) | [reproducible Python](../../scripts/nps_glkn_strict_history.py) | [successful GitHub Actions run](https://github.com/zuizui0223/frogcs/actions/runs/40180516241).

## Main sample (actually read and analysed)

- **147,913** species×recording scores (all valid ManualCIV 0–3), **66 physical SiteLocation stations**, 7 parks, 2016–2023, **13 positive/monitored taxon tokens**.
- Aggregate by park × physical site × species × year to **4,593 site×taxon×year rows** (annual maximum CIV; survey effort retained). From **3,947** site×taxon×year rows with strictly prior own-species site history, compare **1,815** rows in **195** park × species × year strata where at least four stations and both historically strong/non-strong stations were represented (66 sites, **9 taxa**, 2017–2023). Historical data for species other than the focal species must be from earlier years.
- ManualCIV 1: isolated calls; 2: overlapping calls; 3: full overlapping chorus. Primary outcome: annual maximum **≥2**.
- `Hydroperiod` is a category assigned at wetland selection (Permanent / Semi-permanent / Ephemeral), **not event water level**. The source does not report emergent plant cover or the current fish/odonate/salamander communities.

## Main site-history contrast

| Historical species×physical station category | Later-year annual strong-chorus fraction |
|---|---:|
| Species never previously recorded at CI≥2 | **11.90%** |
| Species previously recorded at CI≥2 | **66.91%** |

This unadjusted contrast includes intrinsic species-specific habitat suitability and differing sampling histories; it does not demonstrate individual returning behavior.

**Stratum-fixed effects, risk-difference-scale slope (within same park×taxon×year):**
- Prior same-species strong chorus: **+0.4674**, 95% **cluster-bootstrap interval +0.3941 to +0.5371**.
- After adding strictly prior *other-species* same-station strong-history fraction, `Hydroperiod` class, current recordings, previous recording effort and years previously observed: **+0.4642**, cluster-bootstrap interval **+0.3826 to +0.5331**.
- **38 park×species trajectory clusters** resampled 2,000 times. The corrected slope is a conditional acoustic-recurrence association, not the directly interpretable crude 66.91−11.90 pp rate difference.

**Temporal split using unchanged rules:**
- 2017–2020: **+0.4629** (bootstrap **+0.3647 to +0.5498**, 1,060 eligible rows).
- 2021–2023: **+0.4739** (**+0.3582 to +0.5874**, 755 eligible rows).
These are temporal-block sensitivity estimates within the same NPS programme, not independent external programmes. The later analysis uses past data to construct the predictor, never future observations.

**Threshold sensitivities:**
- CI≥1 (any calling): **+0.4835** (+0.4066 to +0.5564).
- CI=3 (full chorus): **+0.2776** (+0.1893 to +0.3634).
The CI=3 threshold is stronger but less frequent; coefficient scales differ by endpoint.

## Scientific interpretation

NPS demonstrates that historically strong frog chorus use at a physically fixed location predicts future strong **acoustic activity** for the same taxon in a different monitoring program, even after generic site chorus hotness and broad water permanence class are included. It supports transferability of the **recurrent species×place acoustic association**, not the NAAMP rainfall-conditioned multi-site concentration endpoint.

### Crucial falsifiers / unresolved alternatives

- **Historical acoustic record ≠ individual site fidelity**; repeated site×species detection could be due to persistent species-specific habitat resources (calling perches, emergent cover, mates), local hydrology, resident adult availability, breeding cohort persistence, or ongoing detection differences.
- Broad hydroperiod classes are *not* event-level water depth or hydroperiod shifts, and no Typha, emergent stem height/density, submerged refuge, open-water mosaic or predation stage counts are measured. **Therefore the persistence of the adjusted coefficient does not reject the local vegetation hypothesis**.
- Annual maximum call intensity is positively related to number, duration and timing of recordings. Models adjust total year-specific and historical recording effort but cannot eliminate all phenological/detection confounding (instrument model, microphone, noise, seasonal deployment dates).
- Species whose park×year stratum lacked historically strong/non-strong sites (or fewer than four stations) are excluded from the *conditional* test; results do not cover all 13 taxa/7 parks uniformly.
- There is no rainfall recency variable joined to the NPS file; do not claim a NPS rain-switch result. NPS sites are separate loggers rather than synchronized NAAMP 10-stop runs; **cannot calculate the original conditional 10-stop concentration `C` from these annual data**.
- `other_taxa_prior_strong_fraction` measures a *generic shared station acoustic history*, **not** trophic interaction, fish/odonate predator guild or acoustic eavesdropping.

## Connection to independently observed plant and biotic cases

- NAAMP frogcs RC6 principal within-taxon allocation residual **+0.2969** and history-target coefficient **+0.1511** are **different estimands** from this NPS annual fixed effect +0.4642; do **not** pool or compare magnitude.
- Hamer et al. 2021, 55 Australian wetlands (DOI 10.1002/eap.2293), had a positive `Gambusia × emergent vegetation` term in a species occupancy model, but no strict prior NPS site-year activity and no matched rain comparison.
- Hungarian 2024 29 sites found site management/depth improved calling detectability prediction beyond broad weather, but a simple emergent-cover percentage did not add held-out performance. Plant structural and ecological niche specificity may matter far more than static percent cover alone, still **untested** in frogcs/NPS.

**Next empirical science gate** is a *site-matched historical plant architecture × fish/odonate stage × water-condition panel*, not another reanalysis of the frozen JAE manuscript. Verify geolocation and measurement dates and test whether species-specific site-history association shrinks after plant structural trajectory and guild controls.
