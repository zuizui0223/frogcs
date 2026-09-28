#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
Q=1.959963984540054
Q90=1.6448536269514722
MARGIN=0.025
RESPONSES=["delta_active_stops","delta_alpha_active","delta_gamma"]


def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m


base=loadmod("pulse",ROOT/"run_naamp_ecological_pulse.py")
spatial=loadmod("spatial",ROOT/"run_naamp_spatial_taxonomic_activation_decomposition.py")


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
                mn=min(b,c);td=a+mn
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
        if len(sw)!=10 or sw!=sd:
            raise RuntimeError("stop alignment failure")
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


def run_metacommunity(d):
    primary=package(d);exact=d[d.year_gap==1].copy()
    result={
      "analysis":"naamp_metacommunity_alpha_beta_gamma_v0_1",
      "contract":"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json#items/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1",
      "descriptive":desc(d),"primary_models":primary,
      "exact_consecutive_year":{"descriptive":desc(exact),"models":package(exact)},
      "interpretation_boundary":{
        "metacommunity":"Behaviourally realized acoustic metacommunity, not occupancy.",
        "beta":"Among-stop compositional differentiation conditional on stops being acoustically active.",
        "causal_rainfall_claim_authorized":False,
        "endpoint_retuning_after_readback_authorized":False
      }}
    Path("provenance/receipts/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


def fit_geo(d,response,include_state=True):
    x=d[np.isfinite(pd.to_numeric(d[response],errors="coerce"))].copy()
    state=" + C(State)" if include_state else ""
    form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap{state} + C(RunNumber)"
    f=smf.ols(form,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.route_cluster})
    b=float(f.params["rain_contrast"]);se=float(f.bse["rain_contrast"])
    return {"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
            "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],"p":float(f.pvalues["rain_contrast"])}


def state_specific(d,response):
    out=[]
    for state,g in d.groupby("State",sort=True):
        x=g[np.isfinite(pd.to_numeric(g[response],errors="coerce"))].copy()
        row={"state":str(state),"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique())}
        try:
            form=f"{response} ~ rain_contrast + temp_difference + doy_difference + year_gap + C(RunNumber)"
            basefit=smf.ols(form,data=x).fit()
            if x.route_cluster.nunique() < 2 or basefit.df_resid <= 0:
                raise RuntimeError("cluster_inference_not_estimable")
            f=basefit.get_robustcov_results(cov_type="cluster",groups=x.route_cluster)
            names=list(basefit.params.index);j=names.index("rain_contrast")
            b=float(f.params[j]);se=float(f.bse[j])
            row.update({"estimable":True,"beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],
                        "p":float(f.pvalues[j]),"estimator":"adjusted_route_cluster"})
        except Exception as e:
            row.update({"estimable":False,"reason":str(e)})
            if len(x)>=3 and pd.to_numeric(x["rain_contrast"],errors="coerce").nunique()>1:
                dfit=smf.ols(f"{response} ~ rain_contrast",data=x).fit()
                row.update({"descriptive_beta":float(dfit.params["rain_contrast"]),
                            "estimator":"descriptive_unadjusted"})
        out.append(row)
    return out


def loso(d,response):
    out=[]
    for state in sorted(d.State.astype(str).unique()):
        g=d[d.State.astype(str)!=state].copy()
        z=fit_geo(g,response,include_state=True)
        z["omitted_state"]=state;out.append(z)
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


def run_geographic(d):
    result={"analysis":"rc6_geographic_generality_audit_v0_1",
            "contract":"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json#items/NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1",
            "n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "n_states":int(d.State.nunique()),"responses":{}}
    for response in RESPONSES:
        ss=state_specific(d,response);lo=loso(d,response);mx=mixed(d,response)
        result["responses"][response]={
            "state_specific":ss,"leave_one_state_out":lo,"random_slope":mx,
            "state_positive_fraction_estimable":float(np.mean([z["beta"]>0 for z in ss if z.get("estimable")])) if any(z.get("estimable") for z in ss) else None,
            "n_state_specific_estimable":int(sum(bool(z.get("estimable")) for z in ss)),
            "loso_all_positive":bool(all(z["beta"]>0 for z in lo)),
            "loso_all_ci_positive":bool(all(z["ci95"][0]>0 for z in lo)),
            "loso_beta_range":[float(min(z["beta"] for z in lo)),float(max(z["beta"] for z in lo))]
        }
    result["decision"]={
        "pass":bool(all(result["responses"][r]["loso_all_positive"] for r in RESPONSES)),
        "strong_pass":bool(all(result["responses"][r]["loso_all_ci_positive"] for r in RESPONSES)),
        "no_retuning":True}
    Path("provenance/receipts/NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


def fit_protocol_set(d):
    out={r:fit(d,r) for r in RESPONSES}
    return {"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "n_states":int(d.State.nunique()),"models":out}


def run_protocol(d):
    primary=d[d["dry_days_since_rain"]>=4].copy()
    outside=d[d["wet_days_since_rain"]>=4].copy()
    p=fit_protocol_set(primary);b=fit_protocol_set(outside)
    result={
      "analysis":"rc7_protocol_window_sensitivity_v0_1",
      "contract":"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json#items/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1",
      "source_pairs":int(len(d)),
      "primary_crosses_three_day_window":p,
      "secondary_both_outside_three_day_window":b,
      "decision":{
        "pass":bool(all(p["models"][r]["beta_rain_contrast"]>0 for r in RESPONSES)),
        "strong_pass":bool(all(p["models"][r]["ci95"][0]>0 for r in RESPONSES)),
        "primary_rule":"dry_days_since_rain >= 4",
        "secondary_rule":"wet_days_since_rain >= 4"},
      "boundaries":{
        "causal_claim_authorized":False,
        "protocol_selection_eliminated":False,
        "state_protocol_membership_inferred":False,
        "endpoint_retuning_after_readback_authorized":False}}
    Path("provenance/receipts/NAAMP_PROTOCOL_WINDOW_SENSITIVITY_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


def sorensen_one(d):
    f=fit(d,"delta_mean_pairwise_sorensen_active")
    b=float(f["beta_rain_contrast"]);se=float(f["se_cluster"])
    ci=[b-Q90*se,b+Q90*se]
    return {"n_pairs":int(f["n_pairs"]),"n_routes":int(f["n_routes"]),
            "beta":b,"se_cluster":se,"ci90":ci,"margin":[-MARGIN,MARGIN],
            "equivalent":bool(ci[0] > -MARGIN and ci[1] < MARGIN)}


def run_sorensen(d):
    primary=sorensen_one(d);exact=sorensen_one(d[d.year_gap==1].copy())
    result={
      "analysis":"naamp_sorensen_equivalence_v0_1",
      "contract":"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json#items/NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1",
      "status":"post-hoc margin frozen before equivalence readback; conventional coefficient already known",
      "primary":primary,"exact_consecutive_year":exact,
      "decision":{
        "primary_pass":primary["equivalent"],
        "exact_year_pass":exact["equivalent"],
        "title_level_equivalence_support":bool(primary["equivalent"] and exact["equivalent"])},
      "interpretation_boundary":{
        "equivalence_applies_only_to_pairwise_sorensen_slope":True,
        "exact_invariance_claim_authorized":False,
        "retuning_margin_after_readback_authorized":False}}
    Path("provenance/receipts/NAAMP_SORENSEN_EQUIVALENCE_RECEIPT_V0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


RUNNERS={
    "metacommunity":run_metacommunity,
    "geographic":run_geographic,
    "protocol_window":run_protocol,
    "sorensen":run_sorensen,
}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--analysis",choices=["all",*RUNNERS],default="all")
    args=ap.parse_args()
    d=build()
    selected=RUNNERS if args.analysis=="all" else {args.analysis:RUNNERS[args.analysis]}
    outputs={}
    for name,fn in selected.items():
        outputs[name]=fn(d)
    print(json.dumps(outputs,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
