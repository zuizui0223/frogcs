# Mechanism screen ledger v0.1 — rainfall-associated community reassembly

This ledger prevents repeated post hoc trait hunting after the ecological reassembly result was opened.

## Established ecological endpoint

Species-selective reassembly is the article-level result:
- wetter matched runs have higher active-species richness;
- exact consecutive-year turnover increases with rainfall contrast;
- species wet/dry responses are strongly heterogeneous;
- >50% of family-matched heterogeneity remains within families.

## Mechanism screens already consumed

### 1. Body size — pooled association, not family-robust
- AmphiBIO pooled adjusted-response slope: beta = -0.3670, P = 1.23e-6.
- family-stratified permutation: two-sided P = 0.314.
- Status: **not mechanism authority**.

### 2. ATraiU hydroperiod flags — nonestimable
- run: `36149886621`
- artifact: `10870827233`
- 23/29 species matched.
- all 23 matched species were coded for both temporary and permanent breeding water after species-level “ever true” collapse.
- Status: **trait aggregation has no variation; hypothesis not tested**.

### 3. Breeding-season breadth — null
- run: `36200924952`
- artifact: `10892240883`
- 20 species with explicit-month parsing.
- beta = -0.00123, 95% CI -0.1437 to 0.1413, P = 0.986.
- within-family permutation two-sided P = 0.906.
- Status: **unsupported**.

### 4. Route-local core–satellite recruitment — null
- run: `36201285720`
- artifact: `10892047154`
- primary matched-pair delta local prevalence: P = 0.207.
- prior-only sensitivity: P = 0.830.
- species-FE event model local prevalence: P = 0.691.
- prevalence × rain contrast interaction: P = 0.844.
- Status: **unsupported**.

## Final mechanism slot

The remaining prespecified mechanism question is **species-specific post-rain activity persistence**.

It is tested with a temporally disjoint design:
- 2001–2007: estimate each species’ within-route rain-recency sensitivity;
- 2008–2015: independently estimate matched-pair wet-recruitment response;
- test whether species with stronger early-period rain-pulse sensitivity are preferentially wet-recruited later.

No additional trait or mechanism family is opened if this test is null. Further mechanism analysis then requires new external data or an editor/reviewer request.
