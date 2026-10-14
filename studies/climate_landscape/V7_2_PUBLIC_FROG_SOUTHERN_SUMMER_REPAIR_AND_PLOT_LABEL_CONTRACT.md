# v7.2 — PUBLIC frog seasonal-year repair and Dry/Wet plot-label contrast (freeze before reading v7.2 outcomes)

**Recorded 2026-10-13 JST, after v7.1 aggregate outcomes were known but BEFORE computing v7.2 repaired/plot-class similarities.** The data are the exact public [Hoefer et al. (2026), Zenodo v2.0](https://zenodo.org/records/21634473), original GitHub blob `e5a419574be5e3f9922989f9aa6001fbb7f09d01`, `frog_data_season.csv`. The authors' published [R analysis lines 92–97](https://github.com/cheloniax/repo_PAM_frogs/blob/v.2.0/scripts/R_code_biodiversityFrogs.qmd) list four fixed plot labels (`DryA`, `DryB`, `WetA`, `WetB`) for six research sites. The authors' R seasonal section lines 1321–1328 states Dec–Mar Summer, Mar–Jun Autumn, Jun–Sep Winter, Sep–Dec Spring. Actual response-blind [v7.0 extended plot/month audit, CI 38364038791](https://github.com/zuizui0223/frogcs/actions/runs/38364038791) verified each site has those four plot labels and detected season/month pairs correspond to December–February summer, March–May autumn, June–August winter, September–November spring. **34 site×plot×summer-season-year strata contain positive detection dates in both December of prior calendar year and January/February of the next.** Therefore v7.1 calendar-year partition into **216** nonempty site×plot×season×year sets **artificially splits summer**: shifting December summer observations into the *following* seasonal cycle produces **197** nonempty site×plot×season×season-cycle-year sets, prior to inspecting any species outcomes. This is a scientifically material unit correction, not a hypothesis tuned for significance.

## New source-independent grouping rule (scope pre-fixed)

For each valid actual published positive `PAM.all` detection row:

- Determine `season_cycle_year = calendar_year + 1` when the source `season == summer` and its `date.month == 12`; for summer January/February and all other season months, use `calendar_year`. This is a local *Dec–Nov season cycle* convention, **NOT** a new calendar field present in the source.
- Validate the source `season` against the expected month sets. Any mismatch stops rather than silently coercing a source label. Deduplicate species within `site × plot × season × season_cycle_year` *positive detections*. The one author-season cell with no source positive detections is not assigned a complete-survey zero.
- Thus the v7.1 published values remain a valid description of an old **calendar-year** binning, but **must no longer be the primary biological seasonal-year interpretation**. Keep prior receipt unchanged with an explicit supersession note in the v7.2 result.

### H (new axis, explicitly exploratory): nominal Dry/Wet plot-label sorting

Compare Jaccard species-list overlap in two classes of plot pairs **at the same source site, same author season, same season-cycle year**:

- **H_within:** `DryA↔DryB` and `WetA↔WetB` (two within-label-class pairs where both have ≥1 positive record).
- **H_between:** each of the four possible Dry↔Wet pairs, likewise with positive records in both cells.

Compute within-class mean and between-class mean per site, then site-level difference `Δ_H=J_within−J_between` averaged with **six sites equally weighted**. Report all pair counts, which sites are evaluable (number only), site contrast positive count, min/max and percentile **six-site bootstrap (5000 replicates, seed 20261013+72)**. A positive Δ_H would show that observed published acoustic species lists tend to be more similar between plots sharing the **author's nominal Dry/Wet plot category** than across categories; it is NOT proof of depth-driven filtering. Recorded Dry/Wet plot labels are NOT date-specific observed inundation or moisture and are not randomized experimental treatment. A negative or zero result is legitimate.

**Exploratory status:** because the author’s dry/wet labels were discovered AFTER seeing aggregate v7.1 temporal results, this is not a preplanned confirmatory independent test. The rule above is frozen before this *particular* habitat-label contrast is evaluated. No post-hoc threshold/model/plot-code switching.

### C (required correction to the previously frozen temporal question)

Re-run the *identical* v7.1 formulas on the corrected season-cycle-year positive assemblage cells:

- **A:** same site, plot, season, *adjacent* cycle-years; **T:** same site/plot/cycle-year but different seasons; **P:** same site/season/cycle-year, different plots.
- Compute site-equal mean Jaccard A/T/P, A−T primary and P−T secondary with same six-site descriptive bootstrap procedure and fixed original v7.1 seeds.
- **Compare corrected metrics with old 216-cell calendar-year values** without selecting whichever is more favorable. Explain that correction repairs summer rather than demonstrating a new biological mechanism.

### Fixed source-support check (H and C)

Repeat each comparison with **≥5 distinct dates with any positive frog detection in each compared cell**, reporting how many site-level contrasts survive. This is not observation-effort correction or confirmed negative availability; no new thresholds after outcome access. Restrict all claims to positive published species lists.

## Verification and claim firewall

Re-fetch the exact source Git SHA over allowlisted HTTPS (max 4 MB), do not share raw data, species names, site IDs, lat/long or species-specific results. Require exactly six sites, 24 site-plot keys and the documented DryA/DryB/WetA/WetB labels, source year/season-month consistency and **197** expected post-correction nonempty cells. Fail closed if mismatch. Add automated rule tests for December+January same summer cycle, fixed four pair categories and no fabricated cells.

The source paper already concludes broader frog activity seasonality and long-duration passive acoustic richness advantages; new results should distinguish the modest plot-label and seasonal recurrence decomposition from those published findings. None address CEWH wetland local water histories, source recorder/depth joins, source recording negative denominators, individual frog memory, site selection, fitness or causal hydrology.

Do not change submitted JAE RC6/main. No TinyFish or external communications. Publish only anonymous aggregate receipts and explicit correction to old calendar-year result; keep independent frogcs PR #135 draft.
