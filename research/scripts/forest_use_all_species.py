"""Compare species' wetland interactions with documented postmetamorphic habitat."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from forest_use_wetland_species import COMPARISON, FOREST, build_outcomes, estimates, sdm

OUT = sdm.ROOT / "forest_use_wetland_species_20261111"


def summarize(values):
    finite = values[1:][np.isfinite(values[1:])]
    bounds = np.quantile(finite, [.025, .975]) if len(finite) else [np.nan, np.nan]
    return [values[0], *bounds, len(finite)]


def run(raw):
    traits = pd.read_csv(OUT / "forest_traits_44.csv").set_index("species")
    freq, counts, support, _ = build_outcomes(raw, sdm.site)
    named = support.loc[~support.label.str.contains(" complex")].set_index("label")
    assert len(traits) == 44 and traits.index.is_unique and set(traits.index) == set(named.index)
    named = named.loc[traits.index]
    y = freq[:, [counts.columns.get_loc("species|" + n) for n in traits.index]]
    wet = pd.read_csv(sdm.ROOT / "annual_nlcd_wetlands_20261111/site_wetlands.csv.gz").set_index("site").loc[sdm.site.site]
    models = sdm.models.query("background == 'uniform'")
    guilds = [np.mean([sdm.refit(m, sdm.base) for m in models[models.guild.eq(g)].itertuples()], axis=0)
              for g in ["Odonata", "Caudata"]]
    x = np.column_stack([*guilds, wet.herb_fraction, wet.woody_fraction])
    checks = pd.read_csv(OUT / "species.csv").query("domain == 'all'")
    interactions = checks.query("scale == 'rank' and within_route == 0").pivot(
        index="species", columns="term", values="estimate")
    traits.join(named[["strong_visits", "sites", "routes"]]).join(interactions).to_csv(
        OUT / "forest_traits_44_species.csv")
    results = []
    for scale in ["rank", "10pp"]:
        arr = np.stack([estimates(x[i], y[i], sdm.routes[i], scale) for i in sdm.draws])
        for within in [0, 1]:
            for term, component in enumerate(["herbaceous", "woody", "woody_minus_herbaceous"]):
                vals = arr[:, within, term]
                check = checks.loc[(checks.scale == scale) & (checks.within_route == within) &
                                   (checks.term == component)].set_index("species").loc[traits.index]
                np.testing.assert_allclose(vals[0], check.estimate, atol=1e-10)
                for panel, mask in {
                    "all44": np.ones(len(traits), bool),
                    "routes_ge10": named.routes >= 10,
                    "routes_ge25": named.routes >= 25,
                    "exclude_original_six": ~traits.index.isin(FOREST + COMPARISON),
                    "omit_forest_swamp_and_historic_split": ~traits.index.isin(["Hyla avivoca", "Pseudacris brachyphona"]),
                }.items():
                    for metric in ["class0", "class1", "class2", "slope", "within_genus_slope"]:
                        scores = traits.forest_score[mask]
                        z = scores.to_numpy(dtype=float)
                        selected = vals[:, mask]
                        if metric.startswith("class"):
                            keep = z == int(metric[-1])
                            v = selected[:, keep].mean(axis=1)
                            size = keep.sum()
                        else:
                            if metric == "within_genus_slope":
                                genera = scores.index.str.split().str[0]
                                z -= scores.groupby(genera).transform("mean").to_numpy()
                            else:
                                z -= z.mean()
                            keep = abs(z) > 1e-12
                            v = selected[:, keep] @ z[keep] / (z @ z)
                            size = len(z)
                        results.append([scale, within, component, panel, metric, size, *summarize(v)])
    pd.DataFrame(results, columns=["scale","within_route","component","panel","metric","species",
                                  "estimate","low","high","complete_route_draws"]).to_csv(OUT / "forest_traits_44_results.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    with threadpool_limits(limits=1):
        run(parser.parse_args().raw)
