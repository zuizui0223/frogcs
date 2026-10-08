# Seven Iowa routes: actual source-only C1V0 raster outcome (v2.2)

**2026-10-08. Frozen original data readback, no new frog outcomes opened.** Separate from submitted RC6 and the previously frozen negative nine-route Daymet climate forecasting pilot.

The predefined seven nominal Iowa routes 360104, 360110, 360125, 360213, 360219, 360316 and 360412 were independently screened using original USGS NAAMP Runs/Stops/coordinates, and homogeneous USGS-authored NLCD **Collection 1.0, not 1.2** categorical rasters for 2011, 2012 and 2013. The original [successful GitHub Actions workflow](https://github.com/zuizui0223/frogcs/actions/runs/37763029907) contains the [216KB site-by-buffer result with per-year catalog IDs, raw image hashes and pixel metrics](https://github.com/zuizui0223/frogcs/actions/runs/37763029907/artifacts/11543361593). Receipt SHA256: `2c6f78c379f60becbccbebb9187427bdfe4b6bf93a4c1c915bcf796ed3f67015`.

All **7/7 routes**, **70/70 nominal stops**, and **140/140 station×buffer records** had complete 2011/2012/2013 image coverage, with 100% valid 30m pixels. All source-only synthetic tests passed. **No external independent confirmation of 2001–2015 field station continuity.**

| 2011→2012 mapped classes | 250m buffers | 1000m buffers |
|---|---:|---:|
| Stops with ≥1 forest-class loss pixel | **2/70** | 26/70 |
| Sum gross forest-class loss pixels | 5 | 92 |
| Sum forest-class gain pixels | 12 | 66 |
| Forest→agriculture pixels | 4 | 62 |
| Forest→developed pixels | 1 | 4 |
| Loss pixels still classified nonforest in 2013 | 5 | 91 |

The 250m gross forest losses were isolated to `360104` stop 3/SiteID 6613 (3 pixels), and `360412` stop 7/SiteID 7247 (2 pixels). **At 360412 stop 7, net forest cover increased**, despite two gross forest-loss cells. Overlapping 1km buffers must **not** be aggregated as independent areas. More broadly, 2012 was selected after examining NLCD near exploration route 360417; it is not an independent regional disturbance date.

**Scientific decision:** The notion that 2012 provides a common forest-clearing treatment at these seven routes is **unsupported at the pre-outcome exposure gate**. This does not falsify the broader landscape hypothesis, but it prevents treating the 360417 post-hoc before/after calling fluctuation as a replicated multi-route response to 2012 clearing. Do not open/tune new-route calls to rescue this exposure-poor test. A prospective different ecological analysis would first obtain consistently versioned NLCD **C1.2 and confidence**, and contemporaneous historical field-station evidence, then predefine all annual habitat exposures across independently monitored routes.

Status: **new-route frog Counts.csv not opened**, no acoustic effect or cause estimated, no RC6 alteration.
