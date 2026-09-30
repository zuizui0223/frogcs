#!/usr/bin/env python3
from __future__ import annotations

import importlib.util, json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/"exploration"
OUT=EXP/"NAAMP_SOIL_TEMPLATE_DEPTH_RECEIPT_V0_1.json"
Q=1.959963984540054

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

tpl=loadmod("template_base",EXP/"_prior_template_depth_base.py")
soil=loadmod("soil_base",EXP/"run_naamp_soil_moisture_cue.py")
hydric=soil.hydric
base=tpl.base
spatial=tpl.spatial
sameobs=tpl.sameobs

def fit_joint(df,response,soil_col):
    d=df.copy()
    x=pd.to_numeric(d["prior_strong_breadth"],errors="coerce").to_numpy(float)
    sd=float(np.std(x,ddof=0))
    if not sd>0:
        return None
    d["z_breadth"]=(x-float(np.mean(x)))/sd
    d["c_rain_contrast"]=d.rain_contrast-float(d.rain_contrast.mean())
    inter=f"z_breadth:{soil_col}"
    form=(
        f"{response} ~ z_breadth + {soil_col} + z_breadth:{soil_col} + "
        "rain72_z + c_rain_contrast + prior_route_frequency + "
        "temp_difference + doy_difference + year_gap + "
        "C(species) + C(State) + C(RunNumber)"
    )
    m=smf.ols(form,data=d).fit(cov_type="cluster",cov_kwds={"groups":d.route_cluster})

    def term(name):
        b=float(m.params[name]); se=float(m.bse[name])
        return {
            "beta":b,"se":se,"ci95":[b-Q*se,b+Q*se],
            "p":float(m.pvalues[name]),
            "positive_ci":bool(b>0 and b-Q*se>0),
        }

    return {
        "response":response,
        "soil_predictor":soil_col,
        "n_pair_species":int(len(d)),
        "n_routes":int(d.route_cluster.nunique()),
        "n_species":int(d.species.nunique()),
        "prior_strong_breadth_mean":float(np.mean(x)),
        "prior_strong_breadth_sd":sd,
        "prior_strong_breadth":term("z_breadth"),
        "soil_moisture":term(soil_col),
        "breadth_x_soil":term(inter),
        "rain72":term("rain72_z"),
        "rain_contrast":term("c_rain_contrast"),
    }

def classify(model):
    if model is None:
        return "not_estimable"
    b=model["prior_strong_breadth"]["positive_ci"]
    s=model["soil_moisture"]["positive_ci"]
    i=model["breadth_x_soil"]["positive_ci"]
    inter_zero=(model["breadth_x_soil"]["ci95"][0] <= 0 <= model["breadth_x_soil"]["ci95"][1])
    if b and s and inter_zero:
        return "additive_two_axis"
    if b and s and i:
        return "coupled_gate_template"
    if b and not s:
        return "template_only"
    if s and not b:
        return "soil_only"
    return "neither_or_mixed"

def main():
    raw=hydric.retry(base.load,"NAAMP load")
    runs,sets=base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=spatial.stop_matrix(raw,eligible)
    site=tpl.site_map(raw,eligible)
    ci=tpl.ci_map(raw,eligible,sampled)
    meta,by_stratum=tpl.history_index(runs)

    mid=hydric.build_midpoints(raw,runs)
    weather,audit=soil.extract(mid)

    allpairs=base.pair_runs(runs,sets).copy().reset_index(drop=True)
    _,same=sameobs.same_observer_pairs(raw,runs,sets)
    same_keys={(str(p.wet_RunID),str(p.dry_RunID)) for p in same.itertuples(index=False)}

    # Standardize hydric contrasts once per qualified matched pair, not once per species.
    qrows=[]
    stable_pairs=[]
    for p in allpairs.itertuples(index=False):
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        if w not in weather or d not in weather:
            continue
        if not tpl.stable_pair(p,sampled,site):
            continue
        qrows.append({
            "wet_RunID":w,"dry_RunID":d,
            "soil1_gain":float(weather[w]["swvl1"]-weather[d]["swvl1"]),
            "soil2_gain":float(weather[w]["swvl2"]-weather[d]["swvl2"]),
            "rain72":float(np.log1p(weather[w]["rain72_mm"])-np.log1p(weather[d]["rain72_mm"])),
        })
        stable_pairs.append(p)
    q=pd.DataFrame(qrows)
    if len(q)<3500:
        raise RuntimeError(f"weather-qualified stable pairs too small: {len(q)}")
    q["soil1_gain_z"],m1,s1=hydric.zscore(q.soil1_gain)
    q["soil2_gain_z"],m2,s2=hydric.zscore(q.soil2_gain)
    q["rain72_z"],mr,sr=hydric.zscore(q.rain72)
    qmap={
        (r.wet_RunID,r.dry_RunID):r
        for r in q.itertuples(index=False)
    }

    rows=[]
    for p in stable_pairs:
        w=str(p.wet_RunID); d=str(p.dry_RunID)
        z=qmap[(w,d)]
        pr=tpl.pair_species_rows(
            p,sampled,site,ci,meta,by_stratum,
            (w,d) in same_keys
        )
        for row in pr:
            row.update({
                "soil1_gain_z":float(z.soil1_gain_z),
                "soil2_gain_z":float(z.soil2_gain_z),
                "rain72_z":float(z.rain72_z),
            })
            rows.append(row)
    d=pd.DataFrame(rows)

    gate=tpl.gate_report(d)
    gate["pass"]=bool(
        len(d)>=1500
        and d.route_cluster.nunique()>=300
        and d.species.nunique()>=20
        and float(d.prior_strong_breadth.std(ddof=0))>=0.10
    )

    out={
        "analysis":"naamp_soil_template_depth_v0_1",
        "contract":"exploration/NAAMP_SOIL_TEMPLATE_DEPTH_CONTRACT_V0_1.json",
        "coverage":{
            "weather_stable_pairs":int(len(q)),
            "focal_pair_species":int(len(d)),
            "routes":int(d.route_cluster.nunique()) if len(d) else 0,
            "species":int(d.species.nunique()) if len(d) else 0,
            "gate_pass":bool(gate["pass"]),
        },
        "weather_audit":audit,
        "standardization":{
            "soil1_gain_mean":m1,"soil1_gain_sd":s1,
            "soil2_gain_mean":m2,"soil2_gain_sd":s2,
            "rain72_mean":mr,"rain72_sd":sr,
            "soil1_rain72_pair_correlation":float(np.corrcoef(q.soil1_gain,q.rain72)[0,1]),
        },
        "response_endpoints_read":False,
    }
    if not gate["pass"]:
        OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
        print(json.dumps(out,indent=2,sort_keys=True))
        return

    primary=fit_joint(d,"third_plus_depth","soil1_gain_z")
    wetk=fit_joint(d,"wet_k","soil1_gain_z")
    strongk=fit_joint(d,"wet_strong_k","soil1_gain_z")
    spatialdepth=fit_joint(d,"spatial_depth","soil1_gain_z")
    soil2=fit_joint(d,"third_plus_depth","soil2_gain_z")

    ds=d[d.same_observer].copy()
    same_gate=bool(len(ds)>=1000 and ds.route_cluster.nunique()>=250 and ds.species.nunique()>=20)
    same_fit=fit_joint(ds,"third_plus_depth","soil1_gain_z") if same_gate else None

    out.update({
        "response_endpoints_read":True,
        "primary_third_plus_depth":primary,
        "secondary_wet_k":wetk,
        "secondary_wet_strong_k":strongk,
        "secondary_spatial_depth":spatialdepth,
        "secondary_swvl2_third_plus":soil2,
        "same_observer_sensitivity":{
            "gate_pass":same_gate,
            "model":same_fit
        },
        "classification":{
            "primary_result":classify(primary),
            "same_observer_result":classify(same_fit) if same_fit else "not_run",
        },
        "interpretation_boundary":{
            "conditions_on_recruitment":True,
            "continuous_occupancy_proven":False,
            "individual_movement_inferred":False,
            "soil_water_is_body_hydration":False,
            "causal_mediation_established":False,
        }
    })
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
