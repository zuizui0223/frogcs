#!/usr/bin/env python3
"""Post-hoc NPS site-specific strong-vs-weak acoustic history sensitivity.

Not a prespecified main test; see contract in research/.
"""
import argparse
import json
import tempfile
from pathlib import Path

import pandas as pd

from nps_glkn_strict_history import (
    fetch_csv, build_yearly, strict_prior_panel,
    informative_groups, fit_with_block_bootstrap, GRAIN)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="research/results/nps_glkn_weak_vs_strong")
    args = p.parse_args()
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "source.csv"
        fetch_csv(path)
        annual, source = build_yearly(path)
    additional = []
    for (park, site, sp), group in annual.groupby(
        ["ParkCode", "SiteLocation", "ScientificName"], sort=False):
        saw = 0
        for a in group.sort_values("EventYear").itertuples():
            additional.append(dict(ParkCode=park, SiteLocation=site,
                                   ScientificName=sp, EventYear=int(a.EventYear),
                                   prior_any=int(saw)))
            saw = max(saw, int(a.any_call))
    prior = pd.DataFrame(additional)
    panel = strict_prior_panel(annual).merge(
        prior, on=GRAIN, how="left", validate="one_to_one")
    all_info, _ = informative_groups(panel)
    weak_set = panel.loc[panel.prior_any == 1].copy()
    informative, k = informative_groups(weak_set)
    result = {
        "source": "NPS GLKN DOI 10.57830/2320505 fixed 2016–2023 release",
        "posthoc": True,
        "contract": "research/NPS_GLKN_HISTORY_WEAK_VS_STRONG_SENSITIVITY_V0_1.md",
        "prior_positive_site_taxon_years": int(len(weak_set)),
        "historical_prior_weak_n": int(
            ((weak_set.prior_any == 1) & (weak_set.prior_strong == 0)).sum()),
        "historical_prior_strong_n": int(
            (weak_set.prior_strong == 1).sum()),
        "eligible_strata_considered": int(k),
        "informative_rows": int(len(informative)),
        "informative_strata": int(informative.groupby(
            ["ParkCode", "ScientificName", "EventYear"]).ngroups)
            if len(informative) else 0,
        "weak_versus_strong_results": {},
        "leave_one_park_out_main": [],
        "high_current_effort_sensitivity": None,
        "boundary": "Acoustic observation-history strengths; does not "
                    "identify behavior, real abundance or plant effects"
    }
    if len(informative):
        for key, adjusted in [("unadjusted", False), ("adjusted", True)]:
            result["weak_versus_strong_results"][key] = fit_with_block_bootstrap(
                informative, "strong", adjusted, 2000, seed=20261201)
    for park in sorted(all_info.ParkCode.unique()):
        sub = all_info.loc[all_info.ParkCode != park].copy()
        z = fit_with_block_bootstrap(sub, "strong", False, 200,
                                     seed=20261202)
        result["leave_one_park_out_main"].append({
            "omitted_park": park, "n":len(sub),
            "coefficient": z.get("own_prior_strong_beta"),
            "estimable": z.get("estimable")})
    higher = panel.loc[panel.n_species_recordings >= 10]
    highinfo, cnt = informative_groups(higher)
    result["high_current_effort_sensitivity"] = {
        "threshold_species_scored_recordings": 10,
        "groups_considered":cnt,
        "informative_rows":len(highinfo),
        "unadjusted":fit_with_block_bootstrap(highinfo, "strong",
                                               False, 500, seed=20261203),
    }
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/"observed_results.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_NPS_WEAK_HISTORY_RESULTS")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    print("END_NPS_WEAK_HISTORY_RESULTS")


if __name__=="__main__":
    main()
