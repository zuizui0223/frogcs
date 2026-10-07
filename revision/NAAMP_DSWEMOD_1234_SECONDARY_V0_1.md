# DSWEmod classes 1–4 secondary mechanism v0.1 — 2026-10-07

**Status:** frozen after closure of the classes 1–3 primary mechanism and before any classes 1–4 frog endpoint is calculated.

## Role

This is the fixed class sensitivity already named in `NAAMP_MODIS_DSWEMOD_MECHANISM_CONTRACT_V0_1.md`.

It cannot replace, rescue, or redefine the negative classes {1,2,3} primary result.

## Exposure

Primary spatial support remains 500 m.

For each focal SiteID-month:

`DSWEmod_1234 = n(class in {1,2,3,4}) / n(valid class in {0,1,2,3,4})`.

Use the same 2004 source-unavailable repair.

## Mechanism test

Evaluate current-state M0 vs M1 only.

Use exactly the same:
- 1,500 pairs / 300 routes / 15 states coverage gate;
- strict coordinate gate;
- opposite-route-fold species-specific fitting;
- broad covariate controls;
- >=20 positive cells / >=5 positive routes estimability;
- SiteID then RunID centering;
- dry-state persistence anchor a=0.75;
- pair-level total-incidence matching;
- 1,000 simulations and existing M0/M1 seeds;
- conditional within-taxon concentration endpoint.

Report predicted concentration, residual, null 95% interval, upper-tail P, and fraction residual removed.

## Interpretation

A positive result would mean the low-confidence class 4 contains spatial information missed by the stricter classes 1–3 metric.

A negative result would close the predeclared DSWEmod class sensitivity.
