#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np,pandas as pd,statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SOIL_RAIN_DISCORDANCE_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s)
    assert s.loader;s.loader.exec_module(m);return m

soil=loadmod("soil_parent",EXP/"run_naamp_soil_moisture_cue.py")
hydric=soil.hydric;base=soil.base;spatial=soil.spatial;sameobs=soil.sameobs

def build():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw);eligible=set(runs.RunID.astype(str))
    mid=hydric.build_midpoints(raw,runs);weather,audit=soil.extract(mid)
    sampled,_=spatial.stop_matrix(raw,eligible);by=hydric.build_ci(raw,eligible,sampled);site=hydric.site_map(raw,eligible)
    pairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}
    rows=[]
    for p in pairs.itertuples(index=False):
        w=str(p.wet_RunID);d=str(p.dry_RunID)
        if w not in weather or d not in weather:continue
        score,count,ci3=hydric.metrics(p,sampled,by)
        r=p._asdict();r.update({
          "strong_new_score":score,"new_ci3_count":ci3,
          "rain72_log_difference":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
          "soil1_gain_difference":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
          "same_observer_physical_stop":bool((w,d) in same_keys and hydric.stable_pair(p,sampled,site)),
        });rows.append(r)
    d=pd.DataFrame(rows)
    d["rain72_amount_difference_z"],m72,s72=hydric.zscore(d.rain72_log_difference)
    d["soil_wetting_positive"]=(d.soil1_gain_difference>0).astype(int)
    return d,audit,{"rain72_mean":m72,"rain72_sd":s72}

def fit_interaction(d,response):
    form=f"{response} ~ rain_contrast * soil_wetting_positive + rain72_amount_difference_z + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    term="rain_contrast:soil_wetting_positive"
    b=float(m.params[term]);se=float(m.bse[term])
    return {"response":response,"formula":form,"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "interaction_beta":b,"interaction_se":se,"interaction_ci95":[b-Q*se,b+Q*se],
            "interaction_p":float(m.pvalues[term]),"interaction_positive_ci":bool(b-Q*se>0)}

def fit_stratum(d,response):
    form=f"{response} ~ rain_contrast + rain72_amount_difference_z + temp_difference + doy_difference + year_gap + C(State) + C(RunNumber)"
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})
    b=float(m.params["rain_contrast"]);se=float(m.bse["rain_contrast"])
    return {"response":response,"n_pairs":int(len(d)),"n_routes":int(d.route_cluster.nunique()),
            "rain_beta":b,"rain_se":se,"rain_ci95":[b-Q*se,b+Q*se],"rain_p":float(m.pvalues["rain_contrast"]),
            "rain_positive_ci":bool(b-Q*se>0)}

def gate_groups(d,min_pairs,min_routes):
    out={}
    for g in (0,1):
        x=d[d.soil_wetting_positive==g]
        out[str(g)]={"n_pairs":int(len(x)),"n_routes":int(x.route_cluster.nunique()),
                     "pass":bool(len(x)>=min_pairs and x.route_cluster.nunique()>=min_routes)}
    return out

def main():
    d,audit,std=build()
    gg=gate_groups(d,500,150)
    gate=bool(len(d)>=3500 and d.route_cluster.nunique()>=500 and all(v["pass"] for v in gg.values()))
    out={"analysis":"naamp_soil_rain_discordance_v0_1",
         "contract":"exploration/NAAMP_SOIL_RAIN_DISCORDANCE_CONTRACT_V0_1.json",
         "coverage":{"pairs":int(len(d)),"routes":int(d.route_cluster.nunique()),"groups":gg,"gate":gate},
         "weather_audit":audit,"standardization":std,"response_endpoints_read":False}
    if not gate:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True));return

    primary=fit_interaction(d,"strong_new_score")
    strata={name:fit_stratum(d[d.soil_wetting_positive==g].copy(),"strong_new_score") for name,g in [("discordant",0),("concordant",1)]}
    ci3=fit_interaction(d,"new_ci3_count")

    robust=d[d.same_observer_physical_stop].copy()
    rg=gate_groups(robust,350,120)
    rgate=bool(all(v["pass"] for v in rg.values()))
    rfit=fit_interaction(robust,"strong_new_score") if rgate else None

    exact=d[d.year_gap==1].copy()
    eg=gate_groups(exact,300,100)
    egate=bool(all(v["pass"] for v in eg.values()))
    efit=fit_interaction(exact,"strong_new_score") if egate else None

    out.update({
      "response_endpoints_read":True,
      "primary_strong_score":primary,
      "stratified_rain_slopes":strata,
      "secondary_full_chorus_ci3":ci3,
      "same_observer_physical_stop":{"gate":rgate,"groups":rg,"model":rfit},
      "exact_consecutive_year":{"gate":egate,"groups":eg,"model":efit},
      "classification":{"hydric_discordance_gate_supported":bool(primary["interaction_positive_ci"]),
                        "robust_support":bool(rfit and rfit["interaction_positive_ci"]) if rgate else None},
      "interpretation_boundary":{"causal_mediation_established":False,"soil_water_is_body_hydration":False,"soil_water_is_pond_depth":False}
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
