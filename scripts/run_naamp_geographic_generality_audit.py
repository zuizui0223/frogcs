#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s)
    assert s.loader; s.loader.exec_module(m); return m

meta=loadmod("meta",ROOT/"run_naamp_metacommunity_alpha_beta_gamma.py")
RESPONSES=["delta_active_stops","delta_alpha_active","delta_gamma"]

def fit_ols(d,response,include_state=True):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    state=" + C(State)" if include_state else ""
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap{state} + C(RunNumber)"
    f=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(f.params["rain_contrast"]); se=float(f.bse["rain_contrast"])
    return {"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(f.pvalues["rain_contrast"])}

def state_specific(d,response):
    out=[]
    for state,g in d.groupby("State",sort=True):
        z=fit_ols(g,response,include_state=False)
        z["state"]=str(state); out.append(z)
    return out

def loso(d,response):
    out=[]
    for state in sorted(d.State.astype(str).unique()):
        g=d[d.State.astype(str)!=state].copy()
        z=fit_ols(g,response,include_state=True)
        z["omitted_state"]=state; out.append(z)
    return out

def mixed(d,response):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(RunNumber)"
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        try:
            f=smf.mixedlm(form,x,groups=x["State"],re_formula="~rain_contrast").fit(reml=True,method="lbfgs",maxiter=1000,disp=False)
            cov=f.cov_re
            sd=float(np.sqrt(max(float(cov.loc["rain_contrast","rain_contrast"]),0)))
            pop=float(f.params["rain_contrast"])
            blups={str(k):pop+float(v.get("rain_contrast",0.0)) for k,v in f.random_effects.items()}
            return {"converged":bool(f.converged),"population_rain_slope":pop,"state_slope_sd":sd,
                    "state_BLUP_slopes":blups,"warnings":[str(w.message) for w in ws]}
        except Exception as e:
            return {"converged":False,"error":repr(e),"warnings":[str(w.message) for w in ws]}

def main():
    d=meta.build()
    result={"analysis":"rc6_geographic_generality_audit_v0_1",
            "contract":"NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1.json",
            "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "n_states":int(d.State.nunique()),"responses":{}}
    for response in RESPONSES:
        ss=state_specific(d,response); lo=loso(d,response); mx=mixed(d,response)
        result["responses"][response]={
            "state_specific":ss,"leave_one_state_out":lo,"random_slope":mx,
            "state_positive_fraction":float(np.mean([z["beta"]>0 for z in ss])),
            "loso_all_positive":bool(all(z["beta"]>0 for z in lo)),
            "loso_all_ci_positive":bool(all(z["ci95"][0]>0 for z in lo)),
            "loso_beta_range":[float(min(z["beta"] for z in lo)),float(max(z["beta"] for z in lo))]
        }
    result["decision"]={
        "pass":bool(all(result["responses"][r]["loso_all_positive"] for r in RESPONSES)),
        "strong_pass":bool(all(result["responses"][r]["loso_all_ci_positive"] for r in RESPONSES)),
        "no_retuning":True
    }
    Path("NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_RECEIPT_V0_1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__": main()
