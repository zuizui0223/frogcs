# New targeted question: are pooled NWI vegetation effects hiding opposite taxon-specific calling-site responses?

Status: **post-hoc exploratory**, frozen before reading any new taxon-specific NWI association outcome; separate from JAE RC6. Outcomes from NAAMP have been seen for other endpoints, so these tests are **not prespecified independent confirmation**.

## Biological question
Among route-night surveys when a frog taxon produces strong calls somewhere on the route, is its CallingIndex≥2 spatial placement within ten stops associated with **mapped** emergent aquatic-wetland vegetation (`PEM`) after shared route-night conditions and broad wetland availability are controlled? Are opposite signed taxon patterns masked by pooled coefficients?

## Data
- USGS pinned NAAMP 2001–2015 fixed ten-stop survey runs, same SHA-pinned underlying files as RC6.
- USFWS NWI 12-shard response-blind source crosswalk from run 39450277196 (only 5,147 geocoded sites, 501 successfully queried routes).
- NWI within 250 m: `nwi_emergent_cover_250m` primary; total mapped wetland and woody wetland cover mandatory controls; aquatic-bed much rarer and **not** tested taxon-by-taxon.
- Stop air temperature (converted to Celsius), recorded masking (MassNoiseIndex or fallback Noise) and survey-stop number are controls.
- Missing NWI/request failures exclude a whole route-run; no mapped vegetation polygon is **not equivalent to no actual aquatic plants**.

## Fixed population and inferential choices
- Require ten unique geocoded stop `SiteID`s on the source-blind vegetation crosswalk and all ten stops with valid measured temperature and sound controls.
- Conditional response: CI≥2 by species×stop on route-runs where that taxon had ≥1 CI≥2 at some stop. Thus this is spatial placement *conditional on acoustic activation*, not occurrence probability across all nights.
- For each taxon, demean response and covariates within every complete survey run; fit without intercept, cluster SE by State×RouteNumber. Primary explanatory effect: fraction of mapped PEM vegetation in 250m radius with total mapped wetland fraction, mapped woody-wetland fraction, stop air temperature, masking and linear stop position as covariates.
- Eligible taxon before coefficient readback: at least 120 strong-calling stop records, at least 80 active route-runs, at least 25 independent routes, at least 30 route-runs with within-route PEM variation and full design matrix rank. No changing these cutoffs to rescue preferred species.
- Report β for +10 percentage points of PEM cover, 95% route-clustered CI, p, sample counts, and Benjamini-Hochberg q over all eligible taxa.
- Exploratory secondary: CallingIndex≥1 at the same sites/runs, and 100m/500m vegetation radii only as explicit follow-up **without selecting whichever is most significant**.
- If no taxon meets eligibility, report insufficient sample, not no plant preference.

## Interpretation
A taxon-specific NWI PEM coefficient describes spatial association of **acoustic calling**, not preference behavior observed directly. Distinct taxon slopes cannot identify competition, facilitation, hydrology, shelter, fish effects or historical plant community. NWI is not a time-matched macrophyte survey. Stronger inference requires contemporaneous local plant and hydrological measurements.

## Links to prior findings
- Pooled historical-site reuse remains +0.1444 adjusted in 10,166 cells and 241 routes.
- Pooled NWI emergent cover coefficient is not supported; a species-specific signal could cancel in the pool.
- Fixed-margin checkerboard excess is positive, but plant-heterogeneity associations are weak under geographic State clustering and must not be upgraded by taxon screening.
