"""Within-route rank associations of calling with each predator guild's suitability."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, t
from statsmodels.stats.multitest import multipletests
from threadpoolctl import threadpool_limits

import sdm_flooded_omission as sdm
from naamp_species_strong_call_sensitivity import build_outcomes


def estimate(x, y, routes):
    # Rank within the comparison domain, then remove route means.
    data = pd.DataFrame({"x": rankdata(x), "y": rankdata(y)})
    residual = data - data.groupby(routes).transform("mean")
    a, b = residual.to_numpy().T
    n, g = len(a), len(set(routes))
    if min(a.std(), b.std()) == 0 or g < 2 or n <= g+1:
        return [np.nan]*4
    a, b = a/a.std(), b/b.std()
    ss = a @ a
    r = (a @ b)/ss
    scores = pd.Series(a*(b-r*a)).groupby(routes).sum()
    se = np.sqrt((scores@scores)*g/(g-1)*(n-1)/(n-g-1))/ss
    margin = t.ppf(.975,g-1)*se
    return [r,r-margin,r+margin,2*t.sf(abs(r)/se,g-1)]


def main(raw):
    freq,counts,support,ranges = build_outcomes(raw,sdm.site,all_species_ranges=True)
    models = sdm.models.query("background == 'uniform'")
    guilds = {g: np.mean([sdm.refit(m,sdm.base) for m in rows.itertuples()],axis=0)
              for g,rows in models.groupby("guild")}
    results = []
    for sp, detected in ranges.items():
        y = freq[:,counts.columns.get_loc("species|"+sp)]
        for domain,keep in [("all",np.ones(len(y),bool)),("detected_routes",np.isin(sdm.routes,list(detected)))]:
            for guild,x in guilds.items():
                values = estimate(x[keep],y[keep],sdm.routes[keep])
                results.append([sp,guild,domain,len(detected),support.set_index("label").at[sp,"routes"],
                                keep.sum(),*values])
    frame = pd.DataFrame(results,columns=["species","guild","domain","detected_routes","strong_routes","sites","r","low","high","p"])
    # Use the existing 25 strong-route support panel; preserve all taxa in the output.
    for domain in frame.domain.unique():
        mask = (frame.domain==domain)&(frame.strong_routes>=25)&frame.p.notna()
        frame.loc[mask,"holm_p"] = multipletests(frame.loc[mask,"p"],method="holm")[1]
    assert frame.species.nunique()==44 and len(frame)==176
    out=sdm.ROOT/"species_predator_correlations_20261111"
    out.mkdir(exist_ok=True)
    frame.to_csv(out/"within_route.csv",index=False)
    print(frame.query("domain=='detected_routes' and holm_p<0.05")[["species","guild","r","holm_p"]].to_string(index=False))
    print("supported species", frame.query("strong_routes>=25").species.nunique())

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("raw",type=Path)
    with threadpool_limits(limits=1):
        main(parser.parse_args().raw)
