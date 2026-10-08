# v2.3: Actual same-collection Annual NLCD confidence at the five previously identified class-loss pixels

**2026-10-08. Response-unread environmental quality audit; no change to JAE RC6.**

The seven-route C1V0 2011–2013 source-only raster screen (run [37763029907](https://github.com/zuizui0223/frogcs/actions/runs/37763029907)) found five 250m gross forest→nonforest class pixels at two nominal sites, but only 1/70 sites had any net forest proportion reduction. It did **not** support a common 2012 regional forest-clearing treatment.

After inspecting that environmental result, we selected exactly those five mapped pixels as a **post-selection quality-control diagnostic**. The [corrected original-source workflow](https://github.com/zuizui0223/frogcs/actions/runs/37765088259), [full immutable confidence receipt](https://github.com/zuizui0223/frogcs/actions/runs/37765088259/artifacts/11544052209), compared original C1V0 class labels with **Annual NLCD C1V0 Land Cover Confidence** from the same 2011, 2012 and 2013 source catalogues, at the same exact EPSG:5070 30m cells. The raster class SHA256 values matched the prior frozen seven-route source. An earlier failed run had an x/y tuple order error producing an empty 250m mask, which was identified and fixed with an explicit empty-mask gate; *no environment threshold, site identity, or prior target loss count was changed*.

## Matched pixel results

| Frozen source group | No. cells | Source category (2011→2012) | 2012 class-confidence index |
|---|---:|---|---|
| Route 360104, stop 3, SiteID 6613 | 3 | 41→82, 41→82, 41→21 | **44, 46, 7** |
| Route 360412, stop 7, SiteID 7247 | 2 | 41→82, 41→82 | **39, 34** |
| All previously mapped forest-loss pixels | **5** | Four agriculture; one developed | **median 39 (min 7, max 46)** |
| Unchanged 2011→2012 forest cells within the same two 250m circles | **130** | forest remains forest | **median 61** |

All five loss labels still read nonforest in 2013, but **temporal persistence in the same automated classifier does not constitute independent field confirmation**. The 2012 source category label confidence index is **lower at all five chosen change cells** than the unchanged-forest group median; this is a diagnostic comparison of model-assigned index values, not a statistical sampling test or a calibrated probability of the forest-to-agriculture conversion being false.

The official latest Annual NLCD **Collection 1.2** exists, but the public Esri services queried at [run 37764311875](https://github.com/zuizui0223/frogcs/actions/runs/37764311875) explicitly returned **Collection 1.0** for Land Cover, Confidence and Change; they cannot be mislabelled C1.2.

## Scientific stop

No independent field-dated historical physical site coordinates are verified; no newly selected route's `Counts.csv` or amphibian response has been inspected for this source-only confidence check. With **two already-selected stops and just five low-confidence mapped class-change cells**, even a seemingly consistent frog response would not supply a credible climate→habitat-conversion→reallocation inference. The earlier fixed 9-route Daymet prediction remains a negative result and the earlier surface-water concentration mechanism remains unsupported.

The next source task is not climate-window retuning or selecting species; it is **obtaining Collection 1.2 land-cover + confidence pixels and independently dated physical-station relocation history** for a genuinely broader pre-outcome sample. A landscape-change manuscript claim remains *unestablished*.
