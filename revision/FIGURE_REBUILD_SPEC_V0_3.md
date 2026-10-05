# Integrated figure specification v0.2 — multi-site coherence

## Canonical story

**silence → strong chorus → spatial depth → within-taxon multi-site concentration → historical site recurrence → breadth/heterogeneity**

Canonical renderer:
- `revision/build_pulse_template_figures.py`
- `revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json`

## Figure 1 — chorus-state switching
Show:
- direct 0→CI3 estimate with 95% CI;
- same-observer + same-SiteID 0→CI3 estimate with 95% CI;
- descriptive annotation that 65.3% of the total CallingIndex slope came from 0→positive activation and 87.1% of activation entered CI2/3.

Do not mix bars without uncertainty intervals with CI-bearing point estimates.

## Figure 2 — spatial-depth shape
Show:
- marginal j-th occupied-stop coefficients for j=1,...,10;
- observed profile against uniform-activation and persistence-preserving 95% envelopes;
- depths 1–3 within the uniform-activation envelope;
- under the persistence-preserving null, depths 1–2 below the envelope and depth 3 within it;
- depths 4–10 above both null envelopes;
- cumulative third+ β=0.473 retained as context;
- 97.3% of cumulative third+ carried by CI2/3.

Interpretation:
- no discrete threshold at exactly the third stop;
- no exponential increase with depth;
- the signal is a heavier/deeper within-taxon spatial tail than expected.

## Figure 3 — principal species/site comparator versus within-taxon concentration

Main-text Figure 3 now shows **only the two ecologically strongest tests**:

1. principal species-specific rainfall response + strictly-prior SiteID history + dry-persistence comparator;
2. the stronger held-out rain × history gate.

Show:
- principal conditional residual = 0.297 with simulated null 95% interval −0.132 to 0.119;
- final rain × history conditional residual = 0.318 with simulated null 95% interval −0.117 to 0.126;
- observed residuals as squares against the null intervals;
- both conditional upper-tail P ≈ 0.001, the minimum plus-one value from 1,000 simulations.

The figure should visualize the inferential comparison directly rather than connect prediction and observation across empty plotting space.

Do **not** show in the main figure:
- uniform activation;
- persistence-only;
- species-response-only;
- exact exchangeable N,K diagnostic.

Those remain in Supporting Information as falsification/defence analyses.

Output:
`fig3_within_taxon_concentration.svg/png`

## Figure 4 — historical site targeting
Keep:
- prior strong site → wet CI2/3 β=0.151;
- prior strong site → wet CI3 β=0.0778;
- same-observer β=0.159;
- rain-selective CI3 targeting β=0.0245;
- same-observer β=0.0307.

## Figure 5 — breadth and heterogeneity
Visible title:
**Within-taxon multi-site concentration is broad but geographically heterogeneous.**

Keep:
- 53 taxa, 25 positive;
- top1 18.8%, top5 54.2%, HHI 0.0855;
- all leave-one-taxon-out totals positive;
- all 21 leave-one-state-out coefficients/CIs positive;
- state-specific heterogeneity: 14/17 positive, 2/17 wholly positive CIs.

## Terminology rule

Visible main-figure text:
- within-taxon concentration;
- multi-site coherence;
- multi-site concentration.

Do not use:
- higher-order;
- synchrony;
- simultaneous activation.

Historical internal analysis filenames may retain `higher_order` for provenance.


## Submission-figure formatting rule

Do not place "Fig. N" or the full manuscript legend title inside the plotted image. Figure numbers and descriptive titles belong in the manuscript legends. Panel labels such as A/B are allowed where needed.
