# Reviewer attack matrix v0.4 — participation/conditioning revision

| Likely attack | Current answer | Status |
|---|---|---|
| Rainfall effects on frog calling/richness are old. | Agreed. Raw weather association is context; novelty is the standardized decomposition of participation versus within-active/residual association. | Addressed |
| NAAMP and FrogID do not estimate the same response. | Correct. NAAMP primary includes inactive + active stops; FrogID is conditional on >=1 caller. The manuscript now treats FrogID as an activity-conditioned cross-system contrast, not direct replication. | Addressed |
| The corresponding conditional effects conflict. | Correct and reported: NAAMP P(>=2 | >=1) OR=.988, 95% CI .959–1.017, P=.402; FrogID conditional OR=.853, 95% CI .827–.879. Possible biological/observation explanations are discussed rather than pooled away. | Addressed |
| “Independent species activation” is not what NAAMP actually proves. | Correct. Wording is now stop-level participation breadth: rain is associated with more active stops and a broader run-level active pool, while multiplicity within active stops is null. | Addressed |
| Null residual results may just be underpowered. | Conditional OR CI excludes the adjusted all-stop OR=.946. Plug-in residual rain-direction bound (-.00112) and fixed-marginal shuffle bound (-.00110) are ~8% of the within-route all-stop coefficient magnitude. Presented as descriptive precision, not formal equivalence. | Addressed with qualification |
| Plug-in independence uses the same 10 stops. | A fixed-marginal 1,024-permutation/run shuffle preserving every species’ exact stop frequency gives the same null rain result: beta=.000933, 95% CI -.00110–.00296, P=.368. | Addressed |
| Shuffle destroys stop identity and habitat structure. | Explicit limitation. Persistent stop-level habitat/detectability heterogeneity remains part of observed excess. | Qualified |
| Temperature may explain NAAMP rain. | Rain remains negative after temperature adjustment (OR=.942) and temperature + nonlinear DOY adjustment (OR=.946, P=5.44e-4). | Addressed |
| H3 omitted the shoulder main effect. | Hierarchy-corrected beta=-.0480, P=.0698; four-window sensitivity P=.628. Original H3 remains unsupported. | Addressed |
| H4 null conflicts with synchrony story. | Synchrony/temporal-compression story was removed. H4 is concordant with the participation-without-residual-strengthening interpretation. | Addressed |
| FrogID source/time handling is unstable. | Exact SHA-pinned ALA snapshot is identified; timezone audit repaired 151 hours and 6 dates. Repaired OR=.852945 and within-cell beta=-.04262, essentially unchanged. | Addressed |
| DaysSinceRain contains sentinel values/outliers. | Publisher range 0–180; 9,401 numeric values all in range, 10,648 NULL; median 1 day, 95th percentile 7 days. | Addressed |
| NAAMP 5-min stops mix space and time. | Explicit limitation. The paper describes standardized sampling-unit participation, not a pure temporal-niche metric. | Addressed |
| NAAMP primary effect is small. | Reported exactly; complete-10 sensitivity P=.058. The paper does not depend on the primary threshold alone. | Addressed |
| The study is causal. | No. Observational language retained throughout. | Hard boundary |

## Strongest current claim

> In standardized NAAMP monitoring, recent rainfall broadens acoustic participation across sampling units without detectable strengthening of within-active-unit or residual co-calling association; FrogID shows that the activity-conditioned component can differ across systems or observation processes.
