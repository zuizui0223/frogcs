# Integrated figure specification v0.2 — multi-site coherence

## Canonical story

**silence → strong chorus → spatial depth → within-taxon multi-site concentration → historical site recurrence → breadth/heterogeneity**

Canonical renderer:
- `revision/build_pulse_template_figures.py`
- `revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json`

## Figure 1 — chorus-state switching
Use point estimates throughout; show 95% CIs only for the direct CI3 endpoints because those are the inferential intervals stored in the frozen figure data. Do not mix bars and points. Place the note **above** the axes so it cannot overlap the lower CI bars, and state explicitly: top three = point estimates only; bottom two = 95% CI.

Keep:
- total CallingIndex;
- 0→positive;
- 0→CI2/3;
- 0→CI3;
- same-observer + same-SiteID 0→CI3.

## Figure 2 — spatial-depth shape
Show:
- marginal j-th occupied-stop coefficients for j=1,...,10;
- observed profile against uniform-activation and persistence-preserving 95% envelopes;
- depths 1–3 within the uniform-activation envelope;
- depths 1–2 below the persistence-preserving two-sided envelope, depth 3 within it;
- depths 4–10 above both upper 95% envelopes;
- cumulative third+ β=0.473 retained as context;
- 97.3% of cumulative third+ carried by CI2/3.

Interpretation:
- no discrete threshold at exactly the third stop;
- no exponential increase with depth;
- the signal is a heavier/deeper within-taxon spatial tail than expected.

## Figure 3 — principal and blocked transferability tests

Main-text Figure 3 shows four conditional-residual tests:

1. principal species-specific rainfall response + strictly-prior SiteID history + dry-persistence comparator;
2. held-out rain × history gate;
3. focal-State-excluded species-response training;
4. temporal block with response and physical-site history frozen through 2008 and evaluated in 2009–2015.

Show:
- principal: observed 1.650, prediction 1.353, residual 0.297, null 95% −0.132 to 0.119;
- held-out gate: observed 1.650, prediction 1.332, residual 0.318, null 95% −0.117 to 0.126;
- State-blocked: observed 1.650, prediction 1.356, residual 0.295, null 95% −0.120 to 0.130;
- temporal block: observed 3.006, prediction 2.429, residual 0.577, null 95% −0.225 to 0.238;
- conditional residuals as squares;
- simulated 95% null-residual intervals as horizontal bars;
- all four upper-tail P ≈ 0.001.

Use a light separator between the first two principal/sensitivity rows and the two post-hoc blocked-transferability rows. The lower two rows must remain labelled **post-hoc within-programme transferability**, not independent confirmation.

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


## Visible-title rule

Main figure files must not contain manuscript-style titles such as “Fig. 1 …” inside the image. Figure titles belong in the manuscript legends. Panel labels such as “A” and “B” may remain where needed.
