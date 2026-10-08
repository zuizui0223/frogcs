# Frog climate × terrestrial transition study — v0.6 evidence and implementation

**2026-10-08 — independent exploratory line. RC6 manuscript, figures and frozen endpoints unchanged.**

## Source authority and selection caveat

The actual Landsat metadata source is the earlier E3 necessary-metadata artifact (`e3-ndmi-metadata-coverage-v01`, artifact 11522991495; source SHA256 `f375494c3ee4897d45729866f771521753a1a9ed070908ce4002d1db3ab599ce`). It covers 3,811 runs and 395 routes. **The underlying E3 subset was selected by a previously developed frog-analysis pipeline** (`flex.prepare_subset()`); the new metadata-only audit itself does not read frog outcomes, but **the universe cannot be called outcome-independent** and is not the complete 7,848-run eligible NAAMP sampling frame. All numeric scene-availability counts below are therefore conditional pilot feasibility findings, not biological estimates or national coverage.

The independently sourced full NAAMP Runs/Stops-only cohort and externally verified physical SiteID ledger remain separate gates. USGS ScienceBase raw acquisition cannot run from the local container network; GitHub Actions source-feasibility run 37730102259 was still `pending` at the time of this status. Do not substitute metadata scene coverage for actual external site verification.

## Real Landsat metadata-only longitudinal sensitivity

We rebuilt the existing E3 calendar-matched route-year comparisons and tested stricter **exact satellite platform and WRS path/row**, **strict pre-survey acquisition (1+ days)**, matched image seasons and survey-to-image lag conditions, without reading Landsat pixels or calling outcomes.

| Temporal comparison | Previous ±21-day survey-season matching | Same platform/pathrow; imagery within 32 d, image season ≤21 d | Same platform/pathrow; image season ≤14 d | Strict: image season ≤14 d, acquired 1–16 d prior, lag mismatch ≤7 d |
|---|---:|---:|---:|---:|
| Adjacent-year route-year comparisons | 1,817 pairs | 1,817 | 1,814 | **1,421 pairs / 316 routes** |
| Exactly five years | 571 pairs | 571 | 571 | **428 pairs / 133 routes** |
| ≥5 years, maximally separated pair per route | 179 routes | 177 | 176 | **123 routes / 17 states** |
| Early 2001–05 to late 2011–15, one pair per route | 91 routes | 89 | 89 | **58 routes / 12 states** |

Under the strict ≥5-y criterion, 113 of 123 pairs use Landsat 7 ETM+ (`LE07`), and 10 use Landsat 5 TM (`LT05`). For the strict early–late period, 53 of 58 use `LE07`. **This is a material cloud/gap-quality risk** because the Landsat 7 scan-line corrector failed on 2003-05-31, producing missing scan-line areas in scenes. See USGS: https://www.usgs.gov/publications/landsat-7-scan-line-corrector-gap-filled-product-development . The exact-scene metadata pairs are *candidates only*, and the fixed time-pair selector can miss alternative years on the same route. Pixel-QA coverage must be measured directly; these counts are not lower bounds on usable pixels.

Real metadata receipt:
`receipts/LANDSAT_STRICT_PLATFORM_PATHROW_LONGITUDINAL_FEASIBILITY_V0_1.json`

## New response-blind land-change extraction

Instead of interpreting a difference in separately aggregated forest fractions as forest conversion, we added *same-pixel two-year categorical transition extraction* from official **USGS Annual NLCD Collection 1.2** land-cover GeoTIFFs (30 m, CONUS 1985–2025):

- `scripts/build_nlcd_transition_requests.py`: only known external-verified route+physical-SiteID+survey events; two 250 m / 1 km buffers; years `survey.year−6` and `survey.year−1` to avoid future imagery.
- `scripts/extract_nlcd_paired_transitions.py`: exactly aligned projected raster grids, valid 16-class land-cover codes, no-data preservation, minimum 80% **pairwise** pixel validity, forest loss *and* gain separately, forest→developed and forest→agriculture conversion, wetland transition fractions and a forest mass-balance invariant.
- Unexpected classes, mismatched tile grids, within-survey-year or future rasters, missing official years, missing station verification, and inputs containing frog-response columns fail closed.

**This distinction is scientifically important:** equal initial and final forest shares can conceal near-complete reciprocal forest→development and development→forest transition. Separate pre/post percentages cannot distinguish these processes, but a pixelwise transition table can. Such classification remains a *mapped terrestrial environmental proxy*, not physical habitat quality or breeding success.

USGS Annual NLCD Collection 1.2 has six annual products, including land-cover confidence and land-cover change, as well as fractional imperviousness and spectral change day-of-year. The current extractor uses **land-cover category only**, not the independent confidence product yet. Accordingly it is an implementation component, **not a finished ecological overlay or validated disturbance dataset**. Source: https://www.usgs.gov/centers/eros/science/nlcd-product-suite

## Main biological falsification to reserve for an independently sampled study

**Question:** after a documented terrestrial habitat conversion, is species-specific strong calling redistributed among physical sites, or does previously recurrent acoustic use persist despite change?

1. **Responsive tracking**: repeatedly sampled, season-matched sites with forest→developed/other conversion lose prior strong calling relative to other sites on the same route and independently held-out routes, after short-term weather and observer detectability adjustment.
2. **Acoustic-site legacy**: prior strong calling persists initially despite confirmed mapped terrestrial change, with reduction only in later repeats. A lag requires *multiple independently verified repeat surveys after conversion*; two endpoint years alone cannot establish this process.
3. **Environmental buffering/mismatch**: long-run antecedent warmth/dryness interacts with forest retention or imperviousness, but the effect on calling-site **configuration** must be tested separately from the effect on marginal calling intensity.

Do not conclude demographic occupancy, successful reproduction, individual site fidelity, or anthropogenic attribution from calling records. The old JRC and DSWEmod negative mechanism tests remain closed; no retuning old water-buffer definitions to rescue them. Report complete NAAMP cohort coverage, state selection, station relocations, missing pixel fraction, and temporal/geographical holdouts before any new response-stage analysis.

## Validated status

Synthetic suite: **86 passed, 0 failed** (local, 2026-10-08). The real Landsat scene candidate counts above are independently reproducible from the frozen **publicly retrieved E3 metadata artifact**, but no actual NLCD 1.2 GeoTIFFs, Daymet/PRISM site series or new frog outcomes were measured in this study. The climate-landscape ScienceBase source-feasibility GitHub Actions job remains an unconfirmed run, not a receipt.

## Post-audit correction (2026-10-08)

A previous action ([37728326242](https://github.com/zuizui0223/frogcs/actions/runs/37728326242)) **actually passed** original USGS data downloads and full metadata-only site-repeat audit: 7848 eligible runs, 78480 surveyed stop visits, 8223 route–SiteID keys, 29986 candidate adjacent-year within-season **stop** comparisons (not independent route samples), 28751 geometry-pass candidate comparisons, and zero independently field-verified sites. The artifact upload failed silently due to a literal `${RUNNER_TEMP}` path; this workflow is fixed and full counts appear in `ACTUAL_NAAMP_LONGITUDINAL_FEASIBILITY_LOG_V0_1.md`. The original pending-status paragraph is superseded.
