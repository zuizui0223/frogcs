# NAAMP × aquatic vegetation — frozen exploratory design (2026-10-21)

## Authorization, question, and scope

User-directed new ecological analysis on 2026-10-21, separate from the closed JAE RC6 paper. Test whether wetland vegetation structure corresponds to (1) preferential chorus recurrence at previously used physical sites and (2) between-taxon checkerboard segregation across listening stops. No RC6 manuscript, SI, submission records, or frozen claims may be modified. Results are **post-hoc exploratory**, not independent confirmation.

Do not equate existing "prior strong-chorus use" with individual memory, site fidelity, occupancy, or environmental independence. Do not interpret checkerboard as evidence of frog competition without stronger experimental evidence.

## Plant data and exact ecological interpretation

Source: **U.S. Fish and Wildlife Service (USFWS), National Wetlands Inventory (NWI), official wetlands mapping service**, `https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0`.

Cowardin feature ATTRIBUTE classes (do not substitute general wetland cover for plant cover):
- `PEM*` = palustrine **emergent herbaceous hydrophytes** (marsh/sedge/reed-like).
- `PAB*`, `LAB*`, `RAB*` = **aquatic bed** (submerged/floating/algal plants); track `PAB*` separately for freshwater palustrine bed.
- `PFO*`, `PSS*` = wooded/shrub wetlands; vegetation but **not aquatic macrophyte evidence**.
- `PUB*`, `LUB*`, `RUB*` = unconsolidated bottom; water/pond type rather than proof of no aquatic plants.
- Unknown/no NWI polygon must be coded **unmapped**, NOT "aquatic vegetation absent". Absence of mapped `PEM/PAB` means only absence of *mapped polygons* at the resolution and date of NWI.

Source issue: 2001–2015 NAAMP sampling is historical, whereas NWI polygon provenance may be heterogeneous and relatively recent. The overlay is **current/available NWI landscape context**, not a measurement of species or cover at the actual frog survey date. NWI imagery class may omit submerged vegetation, small ponds and roadside breeding patches.

## Coordinates and quality gate: before reading any frog outcomes

Pinned NAAMP coordinate source `RouteNumber, SiteID, lat, lon`, SHA256 `f71a87df9fc94e0d6c5d4466b4745c3bbaff874cbe7c28796b3f9eb44c2e6e83`; see `revision/NAAMP_COORDINATE_GEOMETRY_QC_V0_1.md`. Known >100-km transcription errors prevent blind exact-distance overlays.

1. Download only pinned source CSVs for `Runs`, `Stops` and coordinates. Check SHA256 and `State × RouteNumber × SiteID` uniqueness, requiring NAAMP unified-protocol 2001–2015, ten valid stops per run and >=8 valid stop temperature readings. Do not inspect `Counts.csv` or outcome results in the geometry pilot.
2. Geographic plausibility: latitude 24–50°N, longitude −126 to −65°; unique `State × RouteNumber × SiteID` must have unique coordinates; for each route calculate geodesic distance from all its physical stations to the route's **median** position; **exclude entire routes** if any station deviates by more than 25 km or if <8 geocoded physical stations. This is a conservative pre-outcome geometry rule, not a repair of erroneous raw coordinates. Report both exclusions and their original IDs without published corrected coordinates.
3. For reproducible pilot select **two geometry-eligible routes per state** by SHA256 of `State|RouteNumber`, independent of calling outcomes. Save all audit and source signatures.
4. Query all vegetation polygons from the official NWI REST layer once per route bounding envelope (500-m padding), and compute 250-m point-buffer intersections in local metre-based azimuthal projection. Two additional controls/sensitivities: 100-m and 500-m buffers. Flag server failures, unclassified polygons, geometry problems and incomplete pagination, **never** code a failed request as vegetation absence.

## Frozen analysis plan, only after geometry service / coverage passes

Preflight to continue to frog response linkage: at least 100 spatially validated stops across >=10 distinct routes, ≥50% successful NWI requests and recognizable `ATTRIBUTE` class coding; a missing feature is coded `no mapped polygon` rather than absence of wetland. The total % of mapped PEM and PAB sites must be reported before response modelling. If fewer than 20 sites have mapped aquatic bed, refrain from separate PAB-effect inference.

Primary hypothesis, within the **same species × matched survey pair**:
- Outcome wet CallingIndex ≥2 by physical SiteID.
- Historical prior strong calling (`CI≥2`) at the same taxon × SiteID from years strictly prior to both paired surveys.
- Exposure = **NWI mapped emergent cover (PEM) around SiteID, 250 m** (pre-declared continuous fraction) and aquatic-bed cover separately as secondary; control **NWI total mapped wetland cover** (water/habitat availability), 250-m radius.
- Fit route-clustered within-species × pair linear-probability model, compared on exactly matched rows:
  M0 historical strong use;
  M1 + total wetland cover + emergent cover + aquatic-bed cover + woody cover + stop-time air temperature + stop number + other-taxa contemporaneous CI≥2;
  M2 add `history × emergent cover` interaction to test whether historical-site preference is stronger in aquatic vegetation.
- Preserve environmental measurement boundaries: static cover cannot exclude hydroperiod, fish predation, or historic local vegetation shifts. Report marginal effects with 95% CIs, sample size, number routes, complete-case exclusions. If within-pair vegetation variation is inadequate, mark as not estimable.

Checkerboard mechanism (separate second question):
- Reference: previously computed within-survey fixed-row/fixed-column Stone–Roberts C-score deviations; taxa × ten stops.
- For each complete run, compute among-stop variance of NWI PEM cover (250 m) and proportion of NWI PAB sites. Test whether C-score residual increases with **heterogeneous vegetation across stops**, after run year/season, State, observed alpha and gamma activity, and route-clustered error. This is between-route association and **not direct evidence of taxon competition**.
- Negative/sensitivity: use woody wetland heterogeneity and open-water fraction; 100/500m radii. Distinguish wetland availability from aquatic vegetation type; no post-hoc best radius search.

## Operational gates

Phase 1: run NWI API probe + response-blind coordinate preflight; record point-level vegetation proxy and geospatial coverage, no frog outcomes.

Phase 2: only if Phase 1 passes, run same-sample history × NWI and independent checkerboard models; record provenance, exclusion/coverage, uncertainty; never update JAE RC6 submission automatically.

A source failure or lack of coverage is **an unresolved data linkage**, not a biological negative result.
