# Macro result snapshot, 2026-10-26

The result payload is frozen at source commit `b8d30ea2d2766c8508a7d7e133a141afb0bf6de4`.
The snapshot manifest inventories its tracked research files, research workflows and root README.
These include input tables, full coefficients, uncertainty, sensitivity results, scripts and source receipts.
SHA256 uses LF-normalized bytes for text (Windows checkout compatibility), exact bytes for binary files.
The new verification wrapper and this documentation are versioned by the enclosing Git commit, not self-hashed.

After the 2026-10-27 navigation cleanup, the original root and research READMEs
are preserved under `legacy/frozen_navigation_20261026/`. The explicit mapping
in `snapshot_path_overrides_20261027.json` redirects only these two navigation
files during verification. Their original expected hashes and the frozen
manifest are unchanged. All scientific inputs, scripts and results still verify
at their original paths. Current READMEs describe the latest research and are
versioned normally, rather than masquerading as the old frozen navigation.

## Offline verification and numerical replay

From the repository root, in a dedicated Python 3.10 environment:

```console
python -m pip install -r research/reproducibility/requirements-macro-replay.txt
python research/scripts/verify_macro_snapshot.py
python -m unittest discover -s research/scripts -p "test_*.py"
python research/scripts/verify_macro_snapshot.py --replay
```

The replay reads only committed inputs, writes only to an automatically removed temporary directory,
and recomputes every saved vegetation coefficient (including 1,000 bootstrap draws and 1-km sensitivities),
all prior-water comparisons (2,000 draws), coverage, strata and the 4,040-pair joint table.
Seven complete tables are compared with `rtol=1e-10, atol=1e-12`; row/column order, types and missing values
are also checked. This is numerical replay, not a claim of identical compressed-file or figure bytes.
Seeds, cohorts and resampling units are in the tracked analysis scripts and metadata.
The snapshot is verified again after replay to detect accidental writes.

## From external sources

Offline replay is conditional on the committed NAAMP, fitted-niche and raster-extraction tables.
It does not reacquire raw data or refit SDMs. Those are separate stages:

1. NAAMP history and fixed-pair construction: `.github/workflows/research_naamp_three_guild_occurrence.yml`
   and `research/results/naamp_three_guild_occurrence/`. Retain source-native survey and taxon definitions.
2. Regional candidate inventory and GBIF/GloBI joins: `research/results/regional_species_pool_20261026/`
   and `research/results/three_guild_globi_live/`. Preserve source receipts and unresolved taxa.
3. Species fitting: `.github/workflows/research_broad_species_sdm.yml`. Verified source run
   `40280662127` at `378347495ddad7c7ecc0c9b54b235eadc7d6b71f` used its own Python 3.11/package pins.
   Do not silently replace that environment with the later macro-analysis environment above.
4. EarthEnv extraction: `python research/scripts/naamp_remote_vegetation_context.py`.
   Original URLs and SHA256 are in `research/results/earthenv_wetland_1deg/observed_results.json`;
   the extraction rejects source-hash drift. Cache: `../earthenv_cache` relative to the repository.
5. GLAD extraction: `python research/scripts/naamp_prior_water_context.py`.
   The 72 original URLs, sizes and hashes are in
   `research/results/naamp_prior_water_20261026/source_receipts.csv` (about 2.86 GB).
   Cache: `../glad_annual_cache`. The downloader checks existing cache receipts, but a fresh download
   creates a new receipt: compare every `(tile, year, sha256)` against the frozen receipt before accepting
   a source replay. Remote changes or unavailability must be reported, not accepted as the frozen dataset.

Run source-stage commands in a separate checkout: they intentionally write derived result files.
Compare extracted CSV values rather than gzip headers, and retain the original receipts before running.
Raw rasters are external, not bundled; provider availability is not guaranteed.
No full raw-source reacquisition or cross-platform replay is asserted merely by adding these instructions.

## Interpretation retained with the snapshot

The outcome is strong calling frequency, not breeding success. Suitability is an environmental model,
not observed predator density. Three-kilometre flooded vegetation is landscape context, not pond structure.
Annual water frequency is the fraction of classified satellite observations, not inundation days.
Reported interactions are exploratory associations with fixed fitted SDMs, without multiple-testing
correction or propagation of SDM uncertainty. All backgrounds and spatial sensitivities remain available.
