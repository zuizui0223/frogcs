# Fixed-model failure diagnosis

Analyze existing1479/1455 without new catalogue selection or empirical sign tuning.

1. Audit all24savedcontexts: separate physical high-vegetation S-by-D contrast, othervegetationcontrasts, rankcriterion, floor and convergence.
2. Separate physicalhazardpathways in block13: difference of D effects between highandlowS, split H_DF and H_SF. Use saved3/9/21 grids to identify rank/aggregation artifacts.
3. Before newrun: base block13; change each of12contextaxes to every other value already present in the24design. Keep all otheraxes fixed. Runbothmodels. Additionally inspect thecomplete2x2x2 cube linking13and21 (Sarrival20/40,coverstrength1/.5,refuge_orderD/S), reuse duplicatecontexts. Original80years,window20,dt.25,18supplycells. No choose-best result.
4. Trace the unchanged seasonal kernel at savedblock13 mean startingcohorts. Verifytraceintegratedhazards and comparewithsavedannualmeans. Algebraically partition H_DF interaction into predatorabundance and prey-density-response factors using symmetric product decomposition; do not call algebraic decomposition an independentlyidentifiednaturalcause.
5. Ifnewcounterfactual passes hinge on numerical error, rerun thatcontrast atdt.125; otherwise do not expandthecatalogue. Preserve originaldata,code,criteria.

Deliverables: pre-run contexts, allnewcells/scores, sourceaudit, trace/decomposition, explicit reasonsforweaknessand1/24, reproducible report.

## Completed execution

27uniquecontexts x2fixedmodels x18cells; baseline13replayedbothmodels. Eightcontexts x2models checked athalfstepand160years. Reduced1455 Fduration75 changedclassificationat.125; .0625confirmedfailure. Thisborderlinecoarsesuccessisnotcountedasrobust. Two read-onlyseasontracesverifiedtheexacthazardproductandstoredmeanreplayerrors. Highvegetation1479cancellation75.6%; rankingalonechangesDSVsignbutrawDSisalsoweak. Original24successrecordunchanged; nofieldmechanismclaim.
