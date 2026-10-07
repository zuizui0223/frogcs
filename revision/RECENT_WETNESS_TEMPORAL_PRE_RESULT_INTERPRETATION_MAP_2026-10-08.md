# Recent-wetness temporal validation: pre-result interpretation map — 2026-10-08

## Why this validation matters

The surface-hydrology mechanism tests separate two ecological questions that should not be conflated:

1. **Where is reproductive activity allocated among stops once total activation is fixed?**
2. **How likely is a taxon to enter a strong reproductive acoustic state at all?**

Current JRC and DSWEmod results are negative for question 1.

In the separate out-of-route prediction analysis for question 2, the only hydrology increment with a fully positive bootstrap interval was the fixed three-month route-level wetness history (`route_recent3`). Current-month water did not help, and 12-month variability worsened prediction.

The temporal holdout is therefore a direct discriminator between a transferable ecological memory signal and a route-fold-specific predictive pattern.

## If temporal validation supports

Required result:
- equal-species mean held-out log-loss gain > 0;
- route-block bootstrap 95% interval wholly > 0.

Interpretation:

> Recent wetland history predicts the transition into strong reproductive acoustic activity across future years, even though the same hydrological measurements do not explain the higher-order spatial concentration of that activity.

This would imply a separation between:
- **breeding readiness / activation magnitude**, carrying a multi-month hydrological history;
- **spatial allocation once activated**, controlled by some other unresolved local or biological process.

Preferred language:
- hydrological history;
- lagged breeding readiness;
- environmental memory at the population/activity level.

Do not call it:
- individual memory;
- reproductive success;
- hydroperiod causality;
- the mechanism of spatial concentration.

## If temporal validation does not support

Interpretation:

> The positive three-month increment transfers across routes but not across the fixed early-to-late temporal boundary.

Then:
- do not promote hydrological memory as a general result;
- retain it only as a post-discovery predictive clue;
- continue the predeclared E1–E3 concentration-mechanism sequence independently.

## If temporal validation is mixed

Examples:
- observed gain > 0 but bootstrap interval overlaps zero;
- overall gain supported but concentrated in few taxa;
- log-loss gain positive but Brier score worsens.

Interpretation:
- evidence for temporal transfer is suggestive, not confirmatory;
- report species heterogeneity and leave-one-species-out diagnostics;
- do not change the split or endpoint.

## Consequence for the broader paper architecture

If supported, the landscape/remote-sensing work does **not** turn RC6 into a single hydrology-mechanism paper.

Instead it yields a potentially stronger ecological distinction:

> Environmental history helps determine **when/how strongly** reproductive activity is expressed, whereas the observed taxon-by-place concentration contains additional spatial structure that persists after measurable hydrology is represented.

That distinction is more informative than the original generic statement that unmeasured wetland condition may explain the residual.
