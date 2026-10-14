# v3.8 source-access receipt — real metadata attempts, no biological result

**2026-10-08. Independent external public-data feasibility. JAE RC6 unchanged.**
This is a closed source-access audit with **no downloaded calling observations**. This receipt distinguishes remote API reachability from paper/dataset existence.

## Verified sources and inferences

**Publication exists and openly lists data.** [Mendeley Data: p6nbn2hyz9 v1](https://data.mendeley.com/datasets/p6nbn2hyz9) publicly describes Nebraska *Pseudacris maculata* calling, daily rain, temperature and two non-equivalent habitat hydrology variables. The related [Data in Brief article](https://doi.org/10.1016/j.dib.2020.106581) mentions supplementary `mmc1.zip` approximately 3 MB. These are **source bibliographic/publication findings** only.

**Official Mendeley FILE METADATA API: HTTP 401**. [Actions run 37794396810](https://github.com/zuizui0223/frogcs/actions/runs/37794396810) completed successfully as a *bounded source-check workflow*, but its receipt classified the attempted official public-files API `api.data.mendeley.com/datasets/publics/p6nbn2hyz9/files?version=1` as `SOURCE_HTTP_BLOCKED`, HTTP **401**. That status demonstrates the programmatic route requires authentication at the tested endpoint and runner. It does **not** prove the public dataset cannot be downloaded through normal UI or another legitimate access method, nor that files are absent. No credentials were obtained, and raw response rows were not inspected.

**Two candidate PMC supplementary links returned HTTP 404**. [Actions run 37794497677](https://github.com/zuizui0223/frogcs/actions/runs/37794497677), HEAD only, tested two *constructed URL candidates* of the named `mmc1.zip` on `pmc.ncbi.nlm.nih.gov` and the legacy `www.ncbi.nlm.nih.gov` prefix. Both returned **404**. They are **not a canonical link verified from PMC's HTML/XML**. Hence this is NOT proof the published supplementary archive is unavailable, and one must not reclassify the Mendeley dataset as unpublished or inaccessible universally. The workflow fetched **no ZIP bytes**.

**Source-only test health:** synthetic metadata contract passed, journal HEAD request executed, metadata receipts uploaded successfully. A green GitHub Actions status means the **test ran**, not that the original data were accessible.

## Correct scientific decision

- The source dataset and its declared measures exist. A **limited two-wetland** rain/hydropattern exploratory analysis is scientifically imaginable.
- The original CSV/ZIP field contents have **not** been fetched or validated; **no new rain × water × call coefficient exists**.
- There are only two breeding habitats, with `HYDRO` signifying different constructs. A frogcs-style **k≥4 independent-wetland** placement diagnostic cannot be estimated.
- The existing original authors **already studied hydropattern and precipitation** as predictors of calling activity. Replication of that descriptive association alone is not a strong new ecological contribution.
- Stop unproductive retries of unverified URLs or introduce credentials without the user's explicit choice. Normal Mendeley public interface or the publisher's **verified actual supplementary URL** would be a legitimate later data-access route, but the study does **not** require this to hold up RC6.

## Future independent work (not executed)

If source becomes accessible with file identities and hashes, **freeze** one question at a time before reading any activity responses:
1. within **wet meadow only**, does measured image-derived inundation add out-of-year predictive skill beyond meteorological/seasonal context, using complete daily records and only a prespecified comparator? This addresses a **narrow and already related-to-published** prediction, not causation.
2. use forested slough's **river streamflow** as its own separately labeled environmental index; never pool it as the same hydrology scale.
3. avoid claiming rainfall *sound*, individual movement, deep chorus placement or reproductive success. All remain unsupported by this tabular time series.

If originality is the priority, the stronger path remains v3.7's **simultaneous, physically separate multi-wetland Stage 0 measurement**, not forcing a two-site legacy dataset into a 10-stop mechanism narrative.

**No data contact emails, requests, private login, frog outcomes, animals or manuscript inputs were changed in this work.**
