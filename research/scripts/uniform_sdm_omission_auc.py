"""Paired spatial validation of the 11 uniform-background predator SDMs."""
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from broad_species_sdm import evaluate
from sdm_flooded_omission import ROOT, base, bg, models, taxa


def run():
    rows = []
    for m in models.query("background == 'uniform'").itertuples():
        presence = taxa[taxa.species.eq(m.species)]
        data = pd.concat([presence, bg], ignore_index=True)
        y = np.r_[np.ones(len(presence)), np.zeros(len(bg))]
        xy = data[["lon", "lat"]].to_dict("records")
        archived = pd.DataFrame(m.cv).set_index(["block_degrees", "fold"])
        for size in [2, 4]:
            cols = base[:4] + ["flooded", "water"]
            full = evaluate(data[cols].to_numpy(), y, xy, size)
            reduced = evaluate(data[base].to_numpy(), y, xy, size)
            for a, b in zip(full, reduced):
                saved = archived.loc[(size, a["fold"])]
                assert a["positive_test"] == saved.positive_test and a["background_test"] == saved.background_test
                old = np.nan if a["auc"] is None else a["auc"]
                new = np.nan if b["auc"] is None else b["auc"]
                np.testing.assert_allclose(old, saved.auc, atol=1e-8, rtol=0)
                assert np.isfinite(old) == np.isfinite(new)
                rows.append([m.species, m.guild, size, a["fold"], a["positive_test"], a["background_test"], old, new, new-old])
    result = pd.DataFrame(rows, columns=["species","guild","block_degrees","fold","test_presences","test_background","original_auc","omit_flooded_auc","change"])
    assert len(result) == 110 and result.species.nunique() == 11
    result.to_csv(ROOT / "sdm_flooded_omission_20261111/uniform_auc_by_fold.csv", index=False)
    sp = result.groupby(["block_degrees","guild","species"])[["original_auc","omit_flooded_auc","change"]].mean()
    print(sp.round(4))
    print(sp.groupby(level=0).mean().round(5))
    print(result.groupby("block_degrees").change.count())


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        run()
