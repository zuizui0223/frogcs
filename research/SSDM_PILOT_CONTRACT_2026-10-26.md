# Three-group SSDM pilot

User steering: first predict diversity of frogs, salamanders and odonates, and
ask whether niche differences explain calling-site use. Use the completed
18-species cohort now, without claiming that these are all regional species.
The pool contains 5 Anura, 8 Caudata and 5 Odonata; a pond-breeding Caudata
subset contains Notophthalmus viridescens and the three Ambystoma species.

Reproduce the fitted species scores from the saved environmental tables with
the same scikit-learn 1.6.1 runtime. Verify projected percentiles against the
original artifact. For each species, threshold its fitted score at the 10th
percentile of training-presence scores; sensitivity uses 5th and 20th.
Report held-out presence retention using thresholds determined ONLY from each
training spatial fold. This threshold is an operational suitability rule,
not a calibration to true occupancy. Sum binary suitable-species indicators
within each group to predict potential richness within the modeled species
pool. Also retain continuous mean percentile and full species composition.
Never sum the logistic scores and label the result expected species richness.

Compare group potential richness and Jaccard composition dissimilarity within
the frozen 4,040 strong-call/silent pairs, using equal-route means and 2,000
route bootstraps. Report all thresholds and both background choices.

For the primary 10%-omission rule, test predictive explanation of allocation:
richness differences (three groups), continuous composition differences
(18 species), prior-use difference alone, and each niche model plus prior use.
Use five held-out route folds, symmetric paired logistic regression without
intercept, training-only scaling and fixed L2 regularization C=1. Weight routes
equally. Score held-out pair log likelihood against chance (log 0.5), and
compare additions against history-only. Bootstrap route-level score gains.
These are exploratory predictive comparisons, not causal tests of competition.
Vegetation interactions, actual hydroperiod and broader species-pool expansion
remain separate unfinished analyses.

Method context: Schmitt et al. (2017), SSDM,
https://doi.org/10.1111/2041-210x.12841 . The software used here is the documented
Python pipeline, not an invocation of the R SSDM package or an ensemble of
multiple SDM algorithms. The use of predicted assemblages follows the stacking
idea; resulting richness depends on threshold, background and modeled pool.
