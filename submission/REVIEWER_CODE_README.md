# Anonymous reviewer code bundle

This directory is supplied for double-anonymized peer review.

It contains analysis code, versioned analysis specifications, frozen figure inputs and derived numerical summaries supporting the submitted manuscript. Raw third-party source datasets are not redistributed.

## Source data

The analyses use public third-party datasets identified in the manuscript Data Availability statement:

- North American Amphibian Monitoring Program (NAAMP): DOI 10.5066/F7G44NG0
- FrogID / Atlas of Living Australia records: DOI 10.3897/zookeys.912.38253

Reviewers can obtain the source data from those public providers. Paths in the scripts are intended to be configured locally when reproducing analyses.

## Contents

- `scripts/naamp/`: principal NAAMP processing and baseline analysis scripts
- `exploration/`: versioned later-analysis scripts and specifications retained for provenance
- `revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json`: frozen inputs for the five submitted figures
- `revision/build_pulse_template_figures.py`: deterministic figure renderer
- `provenance/CURRENT_RESULTS.json`: current derived numerical synthesis
- `provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json`: current analysis-routing/provenance record

The internal filenames preserve the historical development record and do not imply that every exploratory analysis contributes to the headline claim.

## Review boundary

The manuscript-level inference is exploratory. Cross-fitting protects fitted comparator components from focal-route leakage but is not independent confirmation.

No WFTS response data were requested or analysed. Historical WFTS materials are not part of this reviewer code bundle.

## Final archive

After review/finalization, the code and derived analysis package will be archived publicly in Zenodo with a persistent identifier. This anonymous bundle is only the peer-review copy.
