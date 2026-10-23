#!/usr/bin/env python3
"""Exact macroecological multilevel vegetation–acoustic richness covariance.

No prediction or new literature. Polarization of correctly nested
State/route/night/stop variances; direct weighted covariance QA.
Post-readback follow-up to positive NAAMP × 250m NWI acoustic richness.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE_PATH=ROOT/"exploration/run_naamp_hierarchical_vegetation_macro_v0_1.py"
ORDER=("among_states","routes_within_state","nights_within_route","stops_within_night")
CLASSES=("pem_present","aquatic_bed_present","woody_present","all_wetland")
RICHNESS=("alpha_any","alpha_strong")

def source_module():
    spec=importlib.util.spec_from_file_location("plant_frog_nested_macro",SOURCE_PATH)
    if spec is None or spec.loader is None:raise RuntimeError("Original validated NAAMP macro loader absent")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def weighted_mean(df,col,mode):
    m=df.groupby(["state","route","run_id"],sort=False)[col].mean()
    q=m.groupby(level=[0,1]).mean()
    if mode=="route_equal":return float(q.mean())
    if mode=="state_equal":return float(q.groupby(level=0).mean().mean())
    raise ValueError(mode)

def run(data,src):
    variables=list(CLASSES+RICHNESS)
    lookup={}
    for p in CLASSES:
        for y in RICHNESS:
            name="sum_"+p+"_"+y
            data[name]=data[p].astype(float)+data[y].astype(float)
            variables.append(name)
            lookup[(p,y)]=name
    parts=src.group_decomposition(data,variables)
    output={}
    for p in CLASSES:
        for y in RICHNESS:
            key=p+" | "+y
            sumkey=lookup[(p,y)]
            out={}
            for weight in ("state_equal","route_equal"):
                vx=parts[p][weight]["variance_components"]
                vy=parts[y][weight]["variance_components"]
                vxy=parts[sumkey][weight]["variance_components"]
                cov={k:float((vxy[k]-vx[k]-vy[k])*.5) for k in ORDER}
                absall=sum(abs(v) for v in cov.values())
                # independently verify full weighted covariance, not only the polarization identity
                mu_x=weighted_mean(data,p,weight)
                mu_y=weighted_mean(data,y,weight)
                data["_cov_product"]=(data[p].astype(float)*data[y].astype(float))
                direct=weighted_mean(data,"_cov_product",weight)-mu_x*mu_y
                total=sum(cov.values())
                if not math.isclose(total,direct,rel_tol=2e-7,abs_tol=1e-9):
                    raise ValueError(f"Nested covariance does not reconstruct direct source covariance {key}: {total} vs {direct}")
                cor={}
                for k in ORDER:
                    denom=math.sqrt(max(0,vx[k])*max(0,vy[k]))
                    cor[k]=(cov[k]/denom) if denom>1e-10 else None
                    if cor[k] is not None and abs(cor[k])>1+1e-7:
                        raise ValueError("Impossible cross-variable covariance component correlation")
                denom=math.sqrt(parts[p][weight]["variance_total"]*parts[y][weight]["variance_total"])
                out[weight]={
                    "covariance_components":cov,
                    "signed_covariance_total":total,
                    "direct_weighted_covariance_QA":direct,
                    "signed_component_correlations":cor,
                    "absolute_magnitude_share_pct":{k:100*abs(v)/absall if absall else None for k,v in cov.items()},
                    "total_weighted_cross_variable_correlation":total/denom if denom>0 else None,
                    "mean_mapped_plant_variable":mu_x,
                    "mean_acoustic_taxon_units":mu_y}
            output[key]=out
    return output

def synthetic():
    src=source_module()
    vals=[]
    for s in (-1,1):
        for r in (-1,1):
            for night in (-1,1):
                for st in (-1,1):
                    vals.append({"state":f"S{s}","route":f"R{s}-{r}","run_id":f"N{s}-{r}-{night}",
                        "a":float(s+2*r+3*night+4*st),
                        "b":float(2*s+3*r+4*night+5*st)})
    df=pd.DataFrame(vals)
    df["ab"]=df.a+df.b
    v=src.group_decomposition(df,["a","b","ab"])
    p={x:(v["ab"]["state_equal"]["variance_components"][x]
        -v["a"]["state_equal"]["variance_components"][x]
        -v["b"]["state_equal"]["variance_components"][x])/2 for x in ORDER}
    assert np.allclose(list(p.values()),[2,6,12,20],atol=1e-10),p
    return {"status":"PASS","known_nested_covariances":p,"no_biological_data_used_for_test":True}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_plant_frog_nested_covariance")
    a.add_argument("--synthetic-only",action="store_true")
    args=a.parse_args()
    qa=synthetic()
    if args.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    src=source_module()
    stop,runm,paired,coverage=src.load_data()
    if len(stop)!=62360 or coverage["NWI_environment_complete_run_nights"]!=6236:
        raise ValueError("Original source population drift")
    outcomes=run(stop,src)
    out={"analysis":"NAAMP_macro_NWI_vegetation_frog_richness_exact_nested_covariance",
         "status":"real_complete_population_four_scale_covariance_decomposed",
         "date":"2026-10-23",
         "post_readback_protocol":"exploration/NAAMP_PLANT_FROG_COVARIANCE_HIERARCHY_SPEC_2026_10_23.md",
         "synthetic_QA":qa,
         "source_coverage":{"routes":coverage["n_routes"],
             "states":coverage["n_states"],"nights":coverage["NWI_environment_complete_run_nights"],
             "sites":coverage["stop_records"]},
         "covariance_decomposition":outcomes,
         "claim_boundaries":{"not_prediction":True,
             "vegetation_polygons_not_contemporaneous_live_macrophytes":True,
             "not_causal_vegetation_frog_interactions":True,
             "route_site_and_night_are_repeated_crossed_sample":True,
             "third_organism_path_not_measured":True,
             "JAE_RC6_unchanged":True}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("NAAMP_HIERARCHICAL_COVARIANCE_BEGIN")
    print(json.dumps({"status":out["status"],"source_coverage":out["source_coverage"],
          "state_equal":{k:{"signed":v["state_equal"]["covariance_components"],
                 "correlation":v["state_equal"]["signed_component_correlations"],
                 "abs_pct":v["state_equal"]["absolute_magnitude_share_pct"],
                 "overall":v["state_equal"]["total_weighted_cross_variable_correlation"]}
                for k,v in outcomes.items()},
          "route_equal":{k:{"signed":v["route_equal"]["covariance_components"],
                 "abs_pct":v["route_equal"]["absolute_magnitude_share_pct"],
                 "overall":v["route_equal"]["total_weighted_cross_variable_correlation"]}
                for k,v in outcomes.items()}},sort_keys=True,allow_nan=False))
    print("NAAMP_HIERARCHICAL_COVARIANCE_END")

if __name__=="__main__":
    main()
