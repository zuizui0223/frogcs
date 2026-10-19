# Recent history: transparent feasibility amendment, 2026-10-19

## Executed first attempt (retained, NOT called an effect)

Run 39192305646 / artifact 12160706355 executed the original frozen 2008 cutoff. Eight code tests passed; all three NAAMP source SHA256 values matched. The original complete-survey loader returned 7,848 eligible surveys. Excluding ambiguous stratum-year visits and requiring identical physical sites, exact annual lags and three background visits yielded 497 target surveys. Informative taxon-surveys: training 2006–2008 = 166 frames / 29 routes / 10 states / 15 taxa; test 2009–2015 = 969 frames / 106 routes / 18 states / 34 taxa. The minimum of 200 frames and 50 routes on each side was not met. **No coefficient, model comparison or p-value was computed.** The successful workflow is computational success, not support for recency or memory.

The chosen feasibility thresholds are analyst-set safeguards, not a theorem that inference with 29 routes is impossible. It would be wrong to disguise the halt as a biological null result.

## What changes, and why this is not the original frozen test

Retain the first stopped result and label any subsequent execution an AMENDED EXPLORATORY DESIGN. Do not retrospectively claim the original protocol succeeded. The only change is the time cutoff, chosen algorithmically from source metadata while model performance remains unseen. Species, calling threshold, lags, background history, site matching, likelihood, optimizer bounds, original data, model contrasts, primary MR−MO comparison and uncertainty calculation remain unchanged.

Before loading Counts.csv in the amendment's source pass, reconstruct survey eligibility with the original Runs.csv and Stops.csv and an empty Counts table. Build target survey identities using year, route, run number and ten physical SiteIDs only. Candidate cutoffs c are 2008, 2009, 2010, 2011, 2012 in that order. Select the EARLIEST c for which each side has ≥100 structurally eligible target surveys and ≥50 routes. The test side is c+1 through 2015, always at least three calendar years. Never choose a cutoff using strong-calling frequencies, model coefficients or held-out scores. If no candidate qualifies, stop. After the chosen c is printed and recorded, load the original Counts data and retain the unchanged ≥200 informative taxon-frames and ≥50 routes per side rule. If this second gate fails, STOP; do not choose a later cutoff.

This source-metadata-based redesign occurs AFTER the first coverage result, but BEFORE any model in either design is fitted. It is neither pristine independent confirmation nor the original fixed-2008 test. Code must preserve every candidate's structural counts, selected cutoff and subsequent outcome-informed coverage. Publish the result regardless of sign.

## Inference boundary remains unchanged

Conditioning on current k predicts which stops are strong, not how many stops are active. Historic rate is an imperfect estimate of persistent site propensity, not exact conditioning on all environment. No local hydrology, physical abundance, individual identity, generation or experimental experience is added. A recency gain remains compatible with environmental persistence, demographic persistence and detection. No JAE main modification, new animal experiment, custodian contact, source search or forest-exposure claim follows.
