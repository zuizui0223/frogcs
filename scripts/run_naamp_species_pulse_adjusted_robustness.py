#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import chi2, spearmanr

ROOT=Path(__file__).resolve().parent
BASE_SCRIPT=ROOT/"run_naamp_ecological_pulse.py"
spec=importlib.util.spec_from_file_location("pulse_base",BASE_SCRIPT)
base=importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(base)
Q95=1.959963984540054

def bh(results):
    idx=[i for i,r in enumerate(results) if r.get("estimable")]
    if not idx:return results
    order=sorted(idx,key=lambda i:results[i]["p_value"])
    m=len(order); running=1.0; adj={}
    for rr,pos in enumerate(reversed(order),start=1):
        rank=m-rr+1
        val=min(1.0,results[pos]["p_value"]*m/rank)
        running=min(running,val);adj[pos]=running
    for i in idx:results[i]["fdr_bh"]=float(adj[i])
    return results

def load_species_family():
    obj=json.loads(Path("NAAMP_SPECIES_PULSE_HETEROGENEITY_RECEIPT_V0_1.json").read_text())
    if int(obj["global"]["eligible_species"])!=29:
        raise SystemExit("eligible species family drift")
    raw={}
    for x in obj["species_results"]:
        w=int(x["wet_gains"]);d=int(x["dry_losses"])
        raw[x["species_code"]]={
            "raw_log_odds":float(np.log((w+.5)/(d+.5))),
            "raw_wet_gain_share":w/(w+d),
            "raw_fdr":float(x["fdr_bh"]),
            "wet_gains":w,"dry_losses":d
        }
    return raw

def fit_species(sp,events):
    x=pd.DataFrame(events)
    if len(x)<40 or x.route_cluster.nunique()<10:
        return {"species":sp,"estimable":False,"n_events":int(len(x)),"reason":"eligibility_drift"}
    for col in ["rain_contrast","temp_difference","doy_difference","year_gap"]:
        x["c_"+col]=x[col]-x[col].mean()
    formula="y ~ c_rain_contrast + c_temp_difference + c_doy_difference + c_year_gap"
    try:
        fit=smf.glm(formula,data=x,family=sm.families.Binomial()).fit(
            cov_type="cluster",cov_kwds={"groups":x.route_cluster}
        )
        b=float(fit.params["Intercept"]);se=float(fit.bse["Intercept"]);p=float(fit.pvalues["Intercept"])
        if not all(np.isfinite([b,se,p])) or se<=0:
            raise ValueError("nonfinite intercept")
        lo=b-Q95*se;hi=b+Q95*se
        return {
            "species":sp,"estimable":True,
            "n_events":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "intercept_log_odds":b,"intercept_se_cluster":se,
            "ci95_log_odds":[lo,hi],"p_value":p,
            "adjusted_wet_probability":float(1/(1+np.exp(-b))),
            "slopes":{
              "rain_contrast":float(fit.params["c_rain_contrast"]),
              "temp_difference":float(fit.params["c_temp_difference"]),
              "doy_difference":float(fit.params["c_doy_difference"]),
              "year_gap":float(fit.params["c_year_gap"])
            }
        }
    except Exception as e:
        return {"species":sp,"estimable":False,"n_events":int(len(x)),"reason":str(e)}

def main():
    raw_effects=load_species_family()
    raw=base.load()
    runs,sets=base.build_runs(raw)
    pairs=base.pair_runs(runs,sets)

    events=defaultdict(list)
    for r in pairs.itertuples(index=False):
        W=sets[str(r.wet_RunID)];D=sets[str(r.dry_RunID)]
        discord=W^D
        for sp in discord:
            if sp not in raw_effects:continue
            events[sp].append({
                "y":int(sp in W),
                "route_cluster":str(r.route_cluster),
                "rain_contrast":float(r.rain_contrast),
                "temp_difference":float(r.temp_difference),
                "doy_difference":float(r.doy_difference),
                "year_gap":float(r.year_gap)
            })

    results=[]
    for sp in sorted(raw_effects):
        rr=fit_species(sp,events.get(sp,[]))
        rr.update(raw_effects[sp])
        results.append(rr)
    results=bh(results)

    est=[r for r in results if r.get("estimable")]
    if len(est)>=2:
        theta=np.array([r["intercept_log_odds"] for r in est],float)
        var=np.array([r["intercept_se_cluster"]**2 for r in est],float)
        w=1/var
        mu=float(np.sum(w*theta)/np.sum(w))
        q=float(np.sum(w*(theta-mu)**2))
        df=len(est)-1
        phet=float(chi2.sf(q,df))
        rawv=np.array([r["raw_log_odds"] for r in est],float)
        rho,prho=spearmanr(rawv,theta)
        heterogeneity={"Q":q,"df":df,"p_value":phet,"weighted_mean_log_odds":mu}
        concordance={"spearman_rho":float(rho),"p_value":float(prho),"n_species":len(est)}
    else:
        heterogeneity=None;concordance=None

    result={
      "analysis":"naamp_species_pulse_adjusted_robustness_v0_1",
      "contract":"NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_CONTRACT_V0_1.json",
      "fixed_species_family":29,
      "estimable_species":len(est),
      "fdr_positive_species":int(sum(r.get("estimable") and r.get("fdr_bh",1)<=.05 and r["intercept_log_odds"]>0 for r in results)),
      "fdr_negative_species":int(sum(r.get("estimable") and r.get("fdr_bh",1)<=.05 and r["intercept_log_odds"]<0 for r in results)),
      "heterogeneity_test":heterogeneity,
      "raw_adjusted_concordance":concordance,
      "species_results":results,
      "boundary":{
        "status":"post-opening robustness frozen before adjusted readback",
        "trait_free":True,
        "causal_claim_authorized":False
      }
    }
    Path("NAAMP_SPECIES_PULSE_ADJUSTED_ROBUSTNESS_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
