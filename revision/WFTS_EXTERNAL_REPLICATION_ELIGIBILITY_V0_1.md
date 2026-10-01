# WFTS external replication eligibility audit v0.1

**Status:** DESIGN_ELIGIBLE / DATA_ACCESS_PENDING  
**Frozen before inspection of any WFTS species × station × year outcome matrix.**

## Purpose

Assess only whether the Wisconsin Frog and Toad Survey (WFTS) can structurally support the prospectively frozen replication of the NAAMP **within-taxon multi-site concentration** result.

This audit does not calculate any frog-response endpoint.

## Discovery-data separation

The NAAMP discovery analysis in this repository uses 21 states and does not include Wisconsin.

WFTS is therefore external to the discovery outcome dataset.

However, official WFTS materials state that the programme is coordinated by the Wisconsin Department of Natural Resources in cooperation with USGS and NAAMP. Protocol similarity is therefore an advantage for estimand alignment, not evidence of methodological independence.

Preferred wording:

> **external to the 21-state discovery dataset**

Avoid:

> independent monitoring protocol

## Structural eligibility audit

### Repeated identifiable sites — PASS

Official WFTS documentation describes approximately 100 permanent roadside routes.

Each traditional route contains exactly 10 listening stations.

Route-description forms are intended to let later observers survey from the exact same physical locations.

### Multi-site unit — PASS

Ten stations per route comfortably exceed the frozen minimum of three sites required to define third-and-later participation.

Official guidance states that sites should be separated so the same individual frogs cannot be heard from two stations.

### Repeated temporal sampling — PASS

Traditional routes are surveyed three times per year:
- early spring;
- late spring;
- summer.

All ten stations must be surveyed on the same evening for a route-run to be valid.

Permanent statewide survey routes began in 1984.

### Taxon-level acoustic response — PASS

At each station observers record calling species and a qualitative call index:
- CI1: individuals countable, no overlap;
- CI2: calls overlap but individuals remain distinguishable;
- CI3: continuous/full chorus, individuals not distinguishable.

This is closely aligned with the NAAMP acoustic-state scale.

### Observation duration — PASS

Observers listen for five minutes at each site, with allowance for extra time when needed because of noise.

### Rainfall linkage — DESIGN PASS / IMPLEMENTATION PENDING

WFTS data sheets record survey date and route timing; station coordinates/route locations are documented publicly for traditional routes.

This should permit external linkage to gridded weather/rainfall products without using frog outcomes.

Before any response endpoint is opened, the replication implementation must freeze:
- rainfall product;
- grid resolution;
- wet-day threshold;
- antecedent window;
- local-date/time conversion;
- treatment of surveys conducted during/after rain;
- missing-weather rules.

### Strictly-prior taxon × site history — DESIGN PASS / DATA ACCESS PENDING

The long-running permanent-site design is structurally sufficient to estimate prior taxon × station propensity.

Actual eligibility requires row-level historical species × station records across repeated years.

Public programme pages document the design and annual summaries, but this audit has **not established a public row-level download**.

## Data-access gate

WFTS becomes the confirmatory dataset only if, before opening the concentration endpoint, an obtainable dataset contains at minimum:

- route identifier;
- station identifier;
- survey date;
- survey period/run;
- taxon identity;
- call index or presence/absence by station;
- repeated years sufficient for strictly-prior history.

If one of these is unavailable, classify WFTS **structurally/data-access ineligible** and move to the predeclared Iowa fallback without inspecting the WFTS concentration effect.

## Outcome embargo

Allowed before the eligibility decision:
- programme manuals;
- blank/sample forms;
- route maps;
- schema/column names;
- file sizes and date coverage;
- missingness summaries that do not use species-response values.

Not allowed:
- species × station occupancy/calling matrices;
- concentration summaries;
- wet-versus-dry effect estimates;
- species-level response direction;
- subset choice based on apparent ecological signal.

## Official design sources

1. Wisconsin Frog and Toad Survey, Survey Overview, Wisconsin Aquatic and Terrestrial Resources Inventory / Wisconsin DNR.
2. *Wisconsin Frog and Toad Survey Manual*, Wisconsin Department of Natural Resources, 2022.
3. Wisconsin Frog and Toad Survey blank/sample field data sheet and route-description form.
4. Wisconsin DNR 2026 WFTS volunteer announcement, used only to confirm that the traditional 10-stop / three-night design remains active.

## Decision

**WFTS is the first external candidate and passes the design-eligibility screen.**

It is **not yet declared confirmatory-data-ready** because response-level data access and schema completeness remain unresolved.

No WFTS frog outcome has been inspected for this decision.
