# Post-positive follow-up: at which ecological hierarchy does vegetation–frog richness covariance arise?

2026-10-23. This analysis is designed **after** real NAAMP route-night unadjusted/adjusted richness patterns were observed. Not preregistration, not an independent source replication, not hypothesis fishing for significance. No predictive or forecasting models, no literature search.

Biological macro question: The previously completed variance partition found ~75.3% of mapped PEM cover variation at within-run stops versus ~54.9% of frog CI>=1 richness variation there, with another ~24.2% of frog richness variation among survey nights within route. Does the actual *mapped vegetation–frog richness covariance* therefore arise chiefly among States, among routes, among run nights, or among listening stops of the same route-night?

Use same 6,236 environmentally complete NAAMP survey nights, 62,360 stops, 499 physical routes and 20 States, original 250m NWI source; include acoustic zeros and no condition on positive calling. Eight fixed pairs:
- X = binary NWI PEM presence, aquatic-bed presence, woody-wetland presence, or **continuous total wetland cover fraction**;
- Y = local CI>=1 or CI>=2 number of acoustically detected monitoring taxon units.

Exact **law of total covariance** under nested equal-State -> equal-route -> equal-night -> equal-stop sampling weights:
Cov(X,Y)=Cov(State means X, State means Y)
 + E_state Cov(route means X, route means Y | State)
 + E_route Cov(run means X, run means Y | route)
 + E_run Cov(site X, site Y | run).

Also calculate equal-route national weighting as geographic sensitivity. These contributions can be negative; calculate signed values and **absolute contribution proportions**, not invalid percentage-of-net-covariance interpretations when cancellation occurs. Verify exact decomposition against direct weighted covariance to 1e-8 relative. For each level, calculate component correlation Cov_level/sqrt(Var_level_X Var_level_Y) if identified. The primary descriptive question is which levels concentrate **positive habitat–richness covariance** under the actual NWI data, not whether to predict new communities.

No p values or plant causal assertions follow from this accounting identity. For inferential evidence use the separately completed 499-route matched same-night contrasts and 20-State robust adjusted results; do not pretend covariance is a second independent discovery. Mapped vegetation class is nonexclusive and static, whereas frog calls vary across nights; the temporal/plant comparison is structural and not by itself surprising. The data do not measure fish, insects, macrophyte identity, larval fitness or direct interspecific interaction. No updates to original JAE RC6 main or submission.
