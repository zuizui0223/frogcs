#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    assert s.loader;s.loader.exec_module(m);return m
base=loadmod("pulse",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")
Q=1.959963984540054

def community_metrics(rid,stops,ss):
    sets=[set(ss.get((rid,st),set())) for st in stops]
    active=[x for x in sets if x]
    n=len(active)
    gamma=len(set().union(*active)) if active else 0
    incid=sum(len(x) for x in active)
    alpha=incid/n if n else np.nan
    if n>=2:
        sor=[];turn=[];nest=[]
        for i in range(n):
            for j in range(i+1,n):
                A,B=active[i],active[j]
                a=len(A&B);b=len(A-B);c=len(B-A)
                den=2*a+b+c
                s=(b+c)/den if den else 0.0
                mn=min(b,c); td=a+mn
                t=mn/td if td else 0.0
                sor.append(s);turn.append(t);nest.append(s-t)
        beta_norm=((gamma/alpha)-1)/(n-1) if alpha>0 else np.nan
        return dict(n_active=n,gamma=gamma,alpha_active=alpha,
                    mean_pairwise_sorensen=float(np.mean(sor)),
                    mean_pairwise_turnover=float(np.mean(turn)),
                    mean_pairwise_nestedness=float(np.mean(nest)),
                    whittaker_beta_normalized=float(beta_norm))
    return dict(n_active=n,gamma=gamma,alpha_active=alpha,
                mean_pairwise_sorensen=np.nan,mean_pairwise_turnover=np.nan,
                mean_pairwise_nestedness=np.nan,whittaker_beta_normalized=np.nan)

def build():
    raw=base.load();runs,route_sets=base.build_runs(raw)
    eligible=set(runs["RunID"].astype(str))
    sampled,ss=spatial.stop_matrix(raw,eligible)
    pairs=base.pair_runs(runs,route_sets)
    rows=[]
    for p in pairs.itertuples(index=False):
        w,d=str(p.wet_RunID),str(p.dry_RunID)
        sw=set(sampled[w]);sd=set(sampled[d])
        if len(sw)!=10 or sw!=sd:raise RuntimeError("stop alignment failure")
        stops=sorted(sw)
        W=community_metrics(w,stops,ss);D=community_metrics(d,stops,ss)
        row=p._asdict()
        row.update({
          "delta_alpha_active":W["alpha_active"]-D["alpha_active"],
          "delta_gamma":float(W["gamma"]-D["gamma"]),
          "delta_mean_pairwise_sorensen_active":W["mean_pairwise_sorensen"]-D["mean_pairwise_sorensen"],
          "delta_whittaker_beta_normalized_active":W["whittaker_beta_normalized"]-D["whittaker_beta_normalized"],
          "delta_mean_pairwise_turnover_active":W["mean_pairwise_turnover"]-D["mean_pairwise_turnover"],
          "delta_mean_pairwise_nestedness_active":W["mean_pairwise_nestedness"]-D["mean_pairwise_nestedness"],
          "delta_active_stops":float(W["n_active"]-D["n_active"]),
          "wet_alpha_active":W["alpha_active"],"dry_alpha_active":D["alpha_active"],
          "wet_gamma":W["gamma"],"dry_gamma":D["gamma"],
          "wet_beta_sor":W["mean_pairwise_sorensen"],"dry_beta_sor":D["mean_pairwise_sorensen"],
          "wet_beta_whittaker":W["whittaker_beta_normalized"],"dry_beta_whittaker":D["whittaker_beta_normalized"]
        })
        rows.append(row)
    return pd.DataFrame(rows)

def fit(d,response):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    f=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(f.params["rain_contrast"]);se=float(f.bse["rain_contrast"])
    return {"response":response,"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "beta_rain_contrast":b,"se_cluster":se,"ci95":[b-Q*se,b+Q*se],
            "p_value":float(f.pvalues["rain_contrast"])}

def package(d):
    names=["delta_alpha_active","delta_gamma","delta_mean_pairwise_sorensen_active",
           "delta_whittaker_beta_normalized_active","delta_mean_pairwise_turnover_active",
           "delta_mean_pairwise_nestedness_active","delta_active_stops"]
    return {n:fit(d,n) for n in names}

def desc(d):
    return {"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "mean_wet_alpha_active":float(d.wet_alpha_active.mean()),
            "mean_dry_alpha_active":float(d.dry_alpha_active.mean()),
            "mean_wet_gamma":float(d.wet_gamma.mean()),"mean_dry_gamma":float(d.dry_gamma.mean()),
            "mean_wet_pairwise_sorensen":float(d.wet_beta_sor.mean()),
            "mean_dry_pairwise_sorensen":float(d.dry_beta_sor.mean()),
            "mean_wet_whittaker_beta":float(d.wet_beta_whittaker.mean()),
            "mean_dry_whittaker_beta":float(d.dry_beta_whittaker.mean())}

def main():
    d=build();primary=package(d);exact=d[d.year_gap==1].copy()
    result={
      "analysis":"naamp_metacommunity_alpha_beta_gamma_v0_1",
      "contract":"NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1.json",
      "descriptive":desc(d),"primary_models":primary,
      "exact_consecutive_year":{"descriptive":desc(exact),"models":package(exact)},
      "interpretation_boundary":{
        "metacommunity":"Behaviourally realized acoustic metacommunity, not occupancy.",
        "beta":"Among-stop compositional differentiation conditional on stops being acoustically active.",
        "causal_rainfall_claim_authorized":False,
        "endpoint_retuning_after_readback_authorized":False
      }}
    Path("NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
