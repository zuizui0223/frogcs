#!/usr/bin/env python3
"""Continental same-night frog community turnover at mapped emergent NWI boundaries.

NAAMP (2001–2015) plus USFWS NWI 250-m site overlay. Public source reused from
frogcs, not refetched from external papers. No direct plant or species causality.

One survey route-night = one 10-stop community set; repeated nights grouped at
physical route. Cluster inference and site-pair outcomes are NOT independent.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
SEED=2601023
R=4999
STOPS=10
CUTOFF="PEM > 0 fraction within 250 m; NOT measured local plant presence"
NUI=("dist_2","dist_3","dist_4","dist_5","dist_6","dist_7","dist_8","dist_9",
     "abs_wetland_frac_diff","abs_airtemp_c_diff","abs_noise_index_diff",
     "abs_acoustic_richness_diff","mean_acoustic_richness")
N_ALL=7848
N_NWI=6236
N_SITES=5147
SOURCE_NWI=39450277196
Z=float(student_t.ppf(.975,300))

def loadmod(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    mod=importlib.util.module_from_spec(spec)
    if spec is None or spec.loader is None:raise RuntimeError(f"Cannot import {path}")
    spec.loader.exec_module(mod)
    return mod

def sorensen(a,b):
    inter=len(a&b)
    denom=len(a)+len(b)
    return (denom-2*inter)/denom if denom else None

def simpson(a,b):
    if not a or not b:return None
    shared=len(a&b)
    bcount=len(a)-shared
    ccount=len(b)-shared
    small=min(bcount,ccount)
    denom=shared+small
    return small/denom if denom else None

def synthetic_qa():
    A={"a","b"};B={"b","c"}
    assert abs(sorensen(A,B)-.5)<1e-12
    assert abs(simpson(A,B)-.5)<1e-12
    assert sorensen(set(),set()) is None
    assert sorensen(A,set())==1.0
    assert simpson(A,set()) is None
    assert simpson(A,A)==0.
    assert simpson({"a"},{"b"})==1.
    rng=np.random.default_rng(SEED+30)
    # 120 synthetic nights on 60 independent routes, known boundary
    # difference +0.3 after a nuisance term and run fixed effects.
    data=[]
    for run in range(120):
        for j in range(12):
            bb=int((j+run)%3==0)
            nu=((j%5)-2)/2
            y=0.3 + 0.3*bb + 0.2*nu + 0.003*run
            data.append({"route":f"r{run%60}","run_id":f"x{run}",
                         "boundary":bb,"Y":y,"nu":nu})
    d=pd.DataFrame(data)
    f,_=fit_core(d,"Y",("nu",),equal_route=True)
    assert abs(f["boundary_beta"]-.3)<1e-10, f["boundary_beta"]
    return {"status":"PASS","sorensen_empty_denominator_guard":True,
            "simpson_community_definition":True,
            "known_within_run_boundary_beta_recovery":f["boundary_beta"]}

def records():
    source=loadmod("frog_nwi_vegetation",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=source.read_nwi(
        ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
        ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if not audit.get("preflight_eligible") or audit.get("mode")!="full":
        raise RuntimeError("Full NWI response-blind source audit failed")
    if len(audit["overlay"]["shards"])!=12 or audit["overlay"]["site_records"]!=N_SITES:
        raise RuntimeError("Source NWI shard or physical-site count drift")
    if audit["matched_route_source_only_audit"]["frog_outcomes_read"] is not False:
        raise RuntimeError("NWI geography not response-blind")
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    if len(runs)!=N_ALL:raise RuntimeError(f"NAAMP initial standardized-run count drift: {len(runs)}")
    eligible=set(runs.RunID.astype(str))
    sampled,_=source.spatial.stop_matrix(raw,eligible)
    sites=source.hist.site_map(raw,eligible)
    ci=source.hist.ci_map(raw,eligible,sampled)
    stop_env=source.get_temps_and_detection(raw,runs,sampled)
    rows={"any":[],"strong":[]}
    counter=Counter()
    sites_per_route=defaultdict(dict)
    routes_by_state=defaultdict(set)
    other_counts=Counter()
    coverage_by_mode={mode:Counter() for mode in rows}
    representative_sites_per_route={}
    for obj in runs.itertuples(index=False):
        rid=str(obj.RunID)
        route=str(obj.route_cluster)
        state=str(obj.State)
        route_num=str(obj.RouteNumber)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=STOPS:raise RuntimeError(f"Missing complete 10 stops for run {rid}")
        siteids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,route_num,str(sid)) not in nwi.index for sid in siteids):
            counter["unlinked_NWI_10stops"]+=1
            continue
        if len(set(siteids))!=STOPS:
            counter["duplicate_physical_SiteID"]+=1
            continue
        env=[stop_env.get((rid,st),{}) for st in stops]
        if any(not math.isfinite(float(v.get(k,float("nan"))))
               for v in env for k in ("stop_air_temp_c","stop_sound_index")):
            counter["missing_stop_temperature_or_sound"]+=1
            continue
        counter["full_10stops_with_NWI_and_conditions"]+=1
        site_index=[(state,route_num,str(sid)) for sid in siteids]
        mat=nwi.loc[site_index]
        wet=mat.nwi_all_wetland_cover_250m.astype(float).to_numpy()
        pem=mat.nwi_emergent_cover_250m.astype(float).to_numpy()
        woody=mat.nwi_woody_cover_250m.astype(float).to_numpy()
        if not np.isfinite(np.concatenate([wet,pem,woody])).all():
            raise RuntimeError("Nonfinite NWI 250m layer, do not coerce missing plants to zero")
        if ((wet<0)|(wet>1)|(pem<0)|(pem>1)|(woody<0)|(woody>1)).any():
            raise RuntimeError("NWI fractional cover outside [0,1]")
        mapped=pem>0
        n=int(np.count_nonzero(mapped))
        if n<2 or n>8:
            counter["insufficient_environment_only_PEM_cross_boundary"]+=1
            continue
        counter["NWI_mixed_2to8_runs"]+=1
        routes_by_state[state].add(route)
        tmp_sites=representative_sites_per_route.setdefault(route,{})
        for stop,sid,pr in zip(stops,siteids,mapped):
            tup=(str(sid),bool(pr))
            if stop in tmp_sites and tmp_sites[stop]!=tup:
                raise RuntimeError("Source physical site identity or PEM overlap changed within route")
            tmp_sites[stop]=tup
        temp=np.array([float(v["stop_air_temp_c"]) for v in env])
        noise=np.array([float(v["stop_sound_index"]) for v in env])
        for mode,threshold in (("any",1),("strong",2)):
            activity=[]
            for st in stops:
                taxa={str(taxon) for taxon,v in ci.get((rid,st),{}).items() if int(v)>=threshold}
                activity.append(taxa)
            gamma=len(set().union(*activity))
            coverage_by_mode[mode]["eligible_env_runs"]+=1
            if gamma<2:
                coverage_by_mode[mode]["less_than_2_active_taxa_routes"]+=1
                continue
            coverage_by_mode[mode]["gamma_at_least_two_runs"]+=1
            for i in range(STOPS):
                for j in range(i+1,STOPS):
                    s=sorensen(activity[i],activity[j])
                    if s is None:
                        coverage_by_mode[mode]["both_silent_stop_pairs"]+=1
                        continue
                    a,b=activity[i],activity[j]
                    boundary=int(mapped[i]!=mapped[j])
                    sim=simpson(a,b)
                    dist=j-i
                    d={
                        "run_id":rid,"route":route,"state":state,
                        "boundary":boundary,"sorensen":s,
                        "simpson":np.nan if sim is None else sim,
                        "dist":dist,
                        "pem_cover_abs_diff":float(abs(pem[i]-pem[j])),
                        "abs_wetland_frac_diff":float(abs(wet[i]-wet[j])),
                        "abs_airtemp_c_diff":float(abs(temp[i]-temp[j])),
                        "abs_noise_index_diff":float(abs(noise[i]-noise[j])),
                        "abs_acoustic_richness_diff":abs(len(a)-len(b)),
                        "mean_acoustic_richness":.5*(len(a)+len(b))
                    }
                    for k in range(2,10):
                        d[f"dist_{k}"]=int(dist==k)
                    if any(not math.isfinite(d[c]) for c in ("sorensen","pem_cover_abs_diff",
                          "abs_wetland_frac_diff","abs_airtemp_c_diff","abs_noise_index_diff",
                          "abs_acoustic_richness_diff","mean_acoustic_richness")):
                        raise RuntimeError("Nonfinite ecological pair statistics")
                    rows[mode].append(d)
                    coverage_by_mode[mode]["valid_stop_pairs"]+=1
                    coverage_by_mode[mode]["cross_boundary_pairs"]+=boundary
                    coverage_by_mode[mode]["within_PEM_status_pairs"]+=1-boundary
                    if math.isfinite(d["simpson"]):
                        coverage_by_mode[mode]["simpson_both_active_pairs"]+=1
    if counter["full_10stops_with_NWI_and_conditions"]!=N_NWI:
        raise RuntimeError(f"Cannot reproduce 6,236 source NWI-complete survey runs: {dict(counter)}")
    return {k:pd.DataFrame(v) for k,v in rows.items()},{
        "source_NAAMP_standard_runs":len(runs),
        "source_10stop_NWI_complete":counter["full_10stops_with_NWI_and_conditions"],
        "NWI_mixed_2to8_runs":counter["NWI_mixed_2to8_runs"],
        "NWI_matched_physical_site_records":N_SITES,
        "excluded":dict(counter),
        "mode_counts":{mode:dict(z) for mode,z in coverage_by_mode.items()},
        "states_with_eligible_routes":{state:len(route_ids) for state,route_ids in routes_by_state.items()},
        "unique_routes_in_mixed_env":len(representative_sites_per_route),
        "NWI_source_workflow":SOURCE_NWI,
        "mapped_PEM_is_NOT_actual_plant_presence":True
    }

def demean(arr,grp,counts):
    return arr-np.bincount(grp,weights=arr,minlength=len(counts))[grp]/counts[grp]

def fit_core(df,outcome,controls,equal_route=True):
    d=df[np.isfinite(pd.to_numeric(df[outcome],errors="coerce"))].copy()
    if len(d)<500:raise ValueError(f"Insufficient stop-pair outcome records: {len(d)}")
    rid,runidx=np.unique(d.run_id.astype(str).to_numpy(),return_inverse=True)
    routes,routeidx=np.unique(d.route.astype(str).to_numpy(),return_inverse=True)
    G=len(routes);N=len(d)
    if G<50:raise ValueError(f"Under 50 independent mapped route clusters: {G}")
    y=d[outcome].to_numpy(float)
    b=d["boundary"].to_numpy(float)
    z=d[list(controls)].to_numpy(float)
    if not np.isfinite(y).all() or not np.isfinite(z).all():
        raise ValueError("NAAMP outcome/controls nonfinite")
    if np.min(y)<-1e-12 or np.max(y)>1+1e-12:
        raise ValueError("Community dissimilarity outside 0..1")
    nn=np.bincount(runidx)
    yc=demean(y,runidx,nn)
    bc=demean(b,runidx,nn)
    zc=np.column_stack([demean(z[:,i],runidx,nn) for i in range(z.shape[1])])
    # Any within-run invariant nuisance is omitted with a recorded rationale,
    # not replaced or re-selected according to the association outcome.
    sd=zc.std(axis=0)
    if (sd<1e-8).any():
        raise ValueError(f"Prespecified nuisance lacks usable within-run contrast: {[str(controls[i]) for i in np.where(sd<1e-8)[0]]}")
    zc/=sd
    X=np.column_stack((bc,zc))
    K=X.shape[1]
    if np.linalg.matrix_rank(X)<K:
        raise ValueError("NWI boundary association not identifiable after controls")
    wroutes=np.bincount(routeidx)
    w=(1/wroutes[routeidx]) if equal_route else np.ones(len(y))
    A=(X.T*w)@X
    rhs=X.T@(w*yc)
    coeff=np.linalg.solve(A,rhs)
    e=yc-X@coeff
    gscore=np.zeros((G,K),float)
    np.add.at(gscore,routeidx,((w*e)[:,None]*X))
    V=np.linalg.inv(A)
    correction=(G/(G-1))*((N-1)/(N-K))
    cov=correction*V@(gscore.T@gscore)@V
    se=np.sqrt(np.maximum(0,np.diag(cov)))
    if se[0]<1e-12:raise ValueError("Singular route-cluster boundary uncertainty")
    tcrit=float(student_t.ppf(.975,G-1))
    tp=float(2*student_t.sf(abs(coeff[0]/se[0]),G-1))
    info={
       "n_stop_pairs":N,"n_survey_nights":len(rid),"n_physical_routes":G,
       "boundary_beta":float(coeff[0]),
       "boundary_effect_sorensen_pp":float(100*coeff[0]),
       "route_cluster_se":float(se[0]),
       "route_cluster_ci95":[float(coeff[0]-tcrit*se[0]),float(coeff[0]+tcrit*se[0])],
       "p_cluster_t":tp,
       "same_PEM_pair_mean_dissimilarity":float(d.loc[d.boundary==0,outcome].mean()),
       "cross_PEM_pair_mean_dissimilarity":float(d.loc[d.boundary==1,outcome].mean()),
       "cross_PEM_pair_fraction":float(b.mean()),
       "route_equal_weighted":equal_route,
       "within_run_FE":True,"route_nested_observation":True,
       "controls":list(controls),"site_count_10":True
    }
    # FWL residual scores under null, for independent-route symmetric sign flips.
    Az=(zc.T*w)@zc
    if np.linalg.matrix_rank(Az)<Az.shape[0]:
        raise ValueError("Null nuisance regression rank deficient")
    xr=bc-zc@np.linalg.solve(Az,zc.T@(w*bc))
    yr=yc-zc@np.linalg.solve(Az,zc.T@(w*yc))
    nullscore=np.bincount(routeidx,weights=w*xr*yr,minlength=G)
    observed_score=float(nullscore.sum())
    if not math.isclose(info["boundary_beta"],observed_score/float(np.dot(w*xr,xr)),rel_tol=1e-8,abs_tol=1e-10):
        raise ValueError("FWL score does not reproduce full FE coefficient")
    return info,nullscore

def wild_route_score(scores,seed,nrep=R):
    rng=np.random.default_rng(seed)
    obs=float(np.sum(scores))
    extreme=0
    for start in range(0,nrep,300):
        batch=min(300,nrep-start)
        signs=rng.choice(np.array([-1.,1.]),size=(batch,len(scores)))
        perm=signs@scores
        extreme+=int(np.count_nonzero(np.abs(perm)>=abs(obs)-1e-12))
    return {"status":"route_signflip_null_not_plant_randomization",
            "original_signed_cluster_score":obs,
            "route_clusters":len(scores),
            "draws":nrep,"extreme_signflip_draws":extreme,
            "two_sided_plus_one_p":(1+extreme)/(nrep+1),
            "assumes_approximately_symmetric_independent_route_scores":True}

def summarize(dd,scope):
    QA=synthetic_qa()
    out={
      "analysis":"NAAMP_same_night_frog_metacommunity_turnover_mapped_PEM_boundary_v0_1",
      "status":"empirical_NAAMP_source_linked_macro_community_composition_test",
      "date":"2026-10-23",
      "protocol":"exploration/NAAMP_MACRO_PEM_BOUNDARY_TURNOVER_SPEC_2026_10_23.md",
      "source":scope,"synthetic_QA":QA,
      "responses":{},"inference_limits":{
         "observational_plant_or_interspecific_causality":False,
         "actual_2001_2015_macrophyte_species_or_cover_measured":False,
         "NWI_polygon_absence_is_true_plant_absence":False,
         "fish_or_predatory_insects_recorded":False,
         "species_observed_simultaneously_across_stops":False,
         "route_cluster_independence_unproven":True,
         "post_hoc_with_historically_explored_NAAMP":True,
         "JAE_RC6_main_or_SI_modified":False}}
    for mode in ("any","strong"):
        d=dd[mode]
        if d.empty:raise RuntimeError(f"Empty field outcome: {mode}")
        stats,score=fit_core(d,"sorensen",NUI,equal_route=True)
        stats["wild_route_score"]=wild_route_score(score,SEED+(0 if mode=="any" else 1))
        route_obs,_=fit_core(d,"sorensen",NUI,equal_route=False)
        stats["equal_observation_sensitivity"]={
            k:route_obs[k] for k in ("boundary_beta","route_cluster_ci95","p_cluster_t","n_physical_routes")}
        sim=d[np.isfinite(d["simpson"])].copy()
        if len(sim)>=500 and sim.route.nunique()>=50:
            try:
                simstats,_=fit_core(sim,"simpson",NUI,equal_route=True)
                stats["simpson_turnover_secondary"]=simstats
            except ValueError as ex:
                stats["simpson_turnover_secondary"]={"status":"nonidentifiable_under_frozen_controls","reason":str(ex)}
        else:
            stats["simpson_turnover_secondary"]={"status":"underpowered","n_pairs":len(sim),"n_routes":sim.route.nunique()}
        stats["source_gamma_condition"]="At least 2 acoustic taxa somewhere along 10-stop night; pairs with both silent stops excluded"
        stats["mode"]="CallingIndex>=1" if mode=="any" else "CallingIndex>=2"
        stats["exploratory_boundary_association_supported"]=bool(
            stats["route_cluster_ci95"][0]>0 or stats["route_cluster_ci95"][1]<0
            ) and stats["equal_observation_sensitivity"]["boundary_beta"]*stats["boundary_beta"]>0 and stats["wild_route_score"]["two_sided_plus_one_p"]<.05
        out["responses"][mode]=stats
    out["primary_decision"]=(
       "exploratory_mapped_PEM_boundary_turnover_association"
       if out["responses"]["any"]["exploratory_boundary_association_supported"]
       else "not_supported_by_route_robust_primary_gates")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",type=Path,default=ROOT/"build"/"naamp_macro_pem_boundary")
    ap.add_argument("--synthetic-only",action="store_true")
    a=ap.parse_args()
    qa=synthetic_qa()
    if a.synthetic_only:
        print(json.dumps(qa,sort_keys=True))
        return
    dd,scope=records()
    out=summarize(dd,scope)
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"result.json").write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("NAAMP_MACRO_PEM_TURNOVER_BEGIN",flush=True)
    print(json.dumps({"status":out["status"],"source":scope,"QA":qa,"primary_decision":out["primary_decision"],
         "responses":{m:{k:x for k,x in v.items() if k in (
          "mode","n_stop_pairs","n_survey_nights","n_physical_routes","boundary_effect_sorensen_pp",
          "boundary_beta","route_cluster_ci95","p_cluster_t","cross_PEM_pair_mean_dissimilarity",
          "same_PEM_pair_mean_dissimilarity","wild_route_score","equal_observation_sensitivity",
          "exploratory_boundary_association_supported","simpson_turnover_secondary")}
          for m,v in out["responses"].items()}},sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_MACRO_PEM_TURNOVER_END",flush=True)

if __name__=="__main__":main()
