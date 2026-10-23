#!/usr/bin/env python3
"""Ecological, NOT predictive, macroecological plant–frog community hierarchy.

USGS NAAMP (7,848 standardized runs) × original response-blind 12-shard USFWS
NWI (5,147 mapped physical SiteIDs). 6,236 environmentally complete route nights.
Describes nested spatial/temporal variance, vegetation-stratified acoustic
richness, and alpha/gamma/Whittaker community organization, 2001–2015.

Plant variables are 250-m mapped wetland polygon cover proxies, NOT live
species or time-matched vegetation. No fish, insects or causal competition data.
Independent inference clusters = physical monitoring routes, NOT stop records.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
SOURCE="exploration/NAAMP_HIERARCHICAL_VEGETATION_MACRO_SPEC_2026_10_23.md"
SOURCE_NWI_RUN=39450277196
SEED=26010230
PERMS=4999
FRACTIONS=("pem","aquatic_bed","woody","all_wetland")
PRESENCE=("pem_present","aquatic_bed_present","woody_present","all_wetland_present")
DIVERSITY=("alpha_any","alpha_strong","active_any")
VARS=FRACTIONS+DIVERSITY

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise RuntimeError(f"Missing dependency {path}")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def group_decomposition(stopdf,variables):
    """Law of total variance: State -> route -> run -> stop. No p-values."""
    keys=["state","route","run_id"]
    run=stopdf.groupby(keys,sort=False)[variables].mean().reset_index()
    route=run.groupby(["state","route"],sort=False)[variables].mean().reset_index()
    state=route.groupby("state",sort=False)[variables].mean().reset_index()
    ds=stopdf.merge(run,on=keys,how="left",suffixes=("","_run"),validate="many_to_one")
    dr=run.merge(route,on=["state","route"],how="left",
                 suffixes=("","_route"),validate="many_to_one")
    dg=route.merge(state,on="state",how="left",
                   suffixes=("","_state"),validate="many_to_one")
    nroute=route.groupby("state").size()
    report={}
    for col in variables:
        vstop=((ds[col]-ds[col+"_run"])**2).groupby([ds.state,ds.route]).mean()
        vrun=((dr[col]-dr[col+"_route"])**2).groupby([dr.state,dr.route]).mean()
        route_error=(dg[col]-dg[col+"_state"])**2
        veq=route_error.groupby(dg.state).mean()
        state_means=state.set_index("state")[col]
        out={}
        for weight in ("state_equal","route_equal"):
            if weight=="state_equal":
                grand=float(state_means.mean())
                vs=float(((state_means-grand)**2).mean())
                vr=float(veq.mean())
                vn=float(vrun.groupby(level=0).mean().mean())
                vt=float(vstop.groupby(level=0).mean().mean())
            else:
                grand=float(route[col].mean())
                vs=float(np.average(((state_means-grand)**2).loc[nroute.index],
                                    weights=nroute.to_numpy()))
                vr=float(route_error.mean())
                vn=float(vrun.mean())
                vt=float(vstop.mean())
            vals=dict(among_states=vs,routes_within_state=vr,
                      nights_within_route=vn,stops_within_night=vt)
            if any(x<-1e-10 or not math.isfinite(x) for x in vals.values()):
                raise RuntimeError("Nonfinite or negative variance component")
            total=sum(vals.values())
            if total<=0:raise RuntimeError("No variation in mapped habitat or acoustic richness")
            # Reconstruct from the full weighted stop observations as independent QA.
            if weight=="state_equal":
                expected=(ds.assign(sq=(ds[col]-grand)**2)
                          .groupby(["state","route","run_id"]).sq.mean()
                          .groupby(["state","route"]).mean()
                          .groupby(level=0).mean().mean())
            else:
                expected=(ds.assign(sq=(ds[col]-grand)**2)
                          .groupby(["state","route","run_id"]).sq.mean()
                          .groupby(["state","route"]).mean().mean())
            if abs(total-expected)>1e-7*max(total,1):
                raise RuntimeError(f"Variance decomposition mismatch {col} {weight}: {total} vs {expected}")
            out[weight]={"mean":grand,"variance_total":total,
                         "variance_components":vals,
                         "pct_total_variance":{k:100*v/total for k,v in vals.items()}}
        report[col]=out
    return report

def test_synthetic():
    """Exact variance QA using independent orthogonal +/- state/route/run/stop signals."""
    rows=[]
    for s in (-1,1):
        for r in (-1,1):
            for n in (-1,1):
                for st in (-1,1):
                    rows.append({"state":f"S{s}","route":f"R{s},{r}",
                      "run_id":f"N{s},{r},{n}","stop":1 if st<0 else 2,
                      "qa_y":float(s+2*r+3*n+4*st)})
    v=group_decomposition(pd.DataFrame(rows),["qa_y"])["qa_y"]["state_equal"]
    arr=list(v["variance_components"].values())
    assert np.allclose(arr,[1.,4.,9.,16.],atol=1e-10),v
    assert abs(v["variance_total"]-30.)<1e-10
    assert math.isclose((2.-1.)/(2.+1.),1/3)
    return {"status":"PASS","decomposition_components_recovered":arr,
            "variance_total_recovered":v["variance_total"],
            "nonindependent_stops_not_replicated":True}

def load_data():
    source=load_module("frog_hier_vegetation",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=source.read_nwi(
        ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
        ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if (not audit.get("preflight_eligible") or audit.get("mode")!="full"
        or len(audit["overlay"].get("shards",[]))!=12
        or audit["overlay"]["site_records"]!=5147
        or audit["matched_route_source_only_audit"]["frog_outcomes_read"] is not False):
        raise RuntimeError("Pinned NWI source-only geometry and independence not established")
    if len(nwi)!=5147:raise RuntimeError("Physical NWI site table not 5147")
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    if len(runs)!=7848:raise RuntimeError("Standard NAAMP 7,848 route-run source changed")
    eligible=set(runs.RunID.astype(str))
    sampled,_=source.spatial.stop_matrix(raw,eligible)
    sites=source.hist.site_map(raw,eligible)
    ci=source.hist.ci_map(raw,eligible,sampled)
    env=source.get_temps_and_detection(raw,runs,sampled)
    stoprows=[]
    runrows=[]
    contrasts=[]
    counts=Counter()
    state_routes=defaultdict(set)
    for obs in runs.itertuples(index=False):
        rid=str(obs.RunID)
        state=str(obs.State)
        rno=str(obs.RouteNumber)
        route=str(obs.route_cluster)
        year=int(obs.SurveyYear)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:raise RuntimeError("Standard survey lacks ten stops")
        IDs=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,rno,str(sid)) not in nwi.index for sid in IDs):
            counts["missing_complete_mapped_10stops"]+=1
            continue
        if len(set(IDs))!=10:
            counts["duplicate_siteids"]+=1
            continue
        ss=[env.get((rid,st),{}) for st in stops]
        if any(any(not math.isfinite(float(z.get(k,float("nan"))))
                   for k in ("stop_air_temp_c","stop_sound_index")) for z in ss):
            counts["missing_temp_or_noise"]+=1
            continue
        plants=nwi.loc[[(state,rno,str(sid)) for sid in IDs]]
        v=np.column_stack([plants[x].astype(float).to_numpy() for x in (
                 "nwi_emergent_cover_250m","nwi_aquatic_bed_cover_250m",
                 "nwi_woody_cover_250m","nwi_all_wetland_cover_250m")])
        if not np.isfinite(v).all() or v.min()<-1e-9 or v.max()>1+1e-9:
            raise RuntimeError("Mapped wetland fraction missing/out of range")
        acts={mode:[] for mode in ("any","strong")}
        for st in stops:
            call=ci.get((rid,st),{})
            acts["any"].append({sp for sp,c in call.items() if int(c)>=1})
            acts["strong"].append({sp for sp,c in call.items() if int(c)>=2})
        counts["environment_complete_runs"]+=1
        state_routes[state].add(route)
        row_values={x:v[:,j] for j,x in enumerate(FRACTIONS)}
        for j,(sid,st) in enumerate(zip(IDs,stops)):
            d={"state":state,"route":route,"run_id":rid,"year":year,
               "site_id":str(sid),"stop":int(st),"alpha_any":len(acts["any"][j]),
               "alpha_strong":len(acts["strong"][j]),
               "active_any":float(bool(acts["any"][j]))}
            for p in range(len(FRACTIONS)):
                d[FRACTIONS[p]]=float(v[j,p])
                d[PRESENCE[p]]=int(v[j,p]>0)
            stoprows.append(d)
        metrics={"state":state,"route":route,"run_id":rid,"year":year}
        for mode,stax in acts.items():
            gamma=len(set().union(*stax))
            alpha=sum(map(len,stax))/10.
            beta=(gamma/alpha-1.)/9. if alpha>0 else np.nan
            metrics.update({f"gamma_{mode}":gamma,f"alpha_{mode}":alpha,
                            f"beta_{mode}":beta,
                            f"active_stops_{mode}":sum(bool(a) for a in stax)})
        runrows.append(metrics)
        n_rich_any=np.array([len(z) for z in acts["any"]],float)
        n_rich_strong=np.array([len(z) for z in acts["strong"]],float)
        for j,habitat in enumerate(FRACTIONS):
            flag=v[:,j]>0
            n=int(flag.sum())
            if n not in range(1,10):continue
            contrasts.append({"state":state,"route":route,"run_id":rid,
                "year":year,"habitat":habitat,
                "n_mapped_positive_stops":n,
                "delta_any":float(n_rich_any[flag].mean()-n_rich_any[~flag].mean()),
                "delta_strong":float(n_rich_strong[flag].mean()-n_rich_strong[~flag].mean())})
    if counts["environment_complete_runs"]!=6236 or len(stoprows)!=62360:
        raise RuntimeError(f"Source cohort did not reproduce: {dict(counts)}, rows={len(stoprows)}")
    # Geography source is static and often nonexclusive.
    geo=nwi.reset_index()
    frac={}
    for name,col in zip(FRACTIONS,("nwi_emergent_cover_250m","nwi_aquatic_bed_cover_250m",
                       "nwi_woody_cover_250m","nwi_all_wetland_cover_250m")):
        a=geo[col].astype(float).to_numpy()
        frac[name]={"mapped_physical_sites_positive":int((a>0).sum()),
                    "mapped_site_fraction":float(np.mean(a>0)),
                    "mean_mapped_fraction_all_sites":float(a.mean()),
                    "median_fraction_with_positive_map":float(np.median(a[a>0])) if np.any(a>0) else None}
    flags={n:(geo[c].astype(float).to_numpy()>0) for n,c in zip(FRACTIONS,(
      "nwi_emergent_cover_250m","nwi_aquatic_bed_cover_250m","nwi_woody_cover_250m",
      "nwi_all_wetland_cover_250m"))}
    overlaps={f"{a} x {b}":int((flags[a]&flags[b]).sum())
              for i,a in enumerate(FRACTIONS) for b in FRACTIONS[i+1:]}
    scope={"NAAMP_standard_runs":len(runs),
           "NWI_environment_complete_run_nights":counts["environment_complete_runs"],
           "stop_records":len(stoprows),
           "NWI_source_physical_site_records":len(geo),
           "n_routes":len(set(z["route"] for z in runrows)),
           "n_states":len(state_routes),
           "state_route_count":{k:len(z) for k,z in sorted(state_routes.items())},
           "source_skips":dict(counts),"mapped_class_frequencies":frac,
           "mapped_class_overlaps":overlaps,
           "NWI_source_workflow":SOURCE_NWI_RUN}
    return pd.DataFrame(stoprows),pd.DataFrame(runrows),pd.DataFrame(contrasts),scope

def route_sign_flip(values,seed,n=PERMS):
    rng=np.random.default_rng(seed)
    obs=abs(float(np.mean(values)))
    extreme=0
    for start in range(0,n,300):
        m=min(300,n-start)
        avg=(rng.choice(np.array([-1.,1.]),size=(m,len(values)))@values)/len(values)
        extreme+=int(np.count_nonzero(np.abs(avg)>=obs-1e-14))
    return {"n":n,"extreme":extreme,"p_plus_one_two_sided":(1+extreme)/(n+1),
           "null_is_symmetric_route_mean_sign_not_plant_randomization":True}

def bh_family(result):
    tests=[x for x in result]
    ps=[r.get("route_t_p",1.) if r.get("status")=="estimated" else 1. for r in tests]
    ranks=sorted(range(len(ps)),key=lambda i:ps[i])
    best=1.
    for j in range(len(ranks)-1,-1,-1):
        i=ranks[j]
        best=min(best,len(ps)*ps[i]/(j+1))
        tests[i]["BH_eight_q"]=best
        tests[i]["observational_richness_association_supported"]=bool(
            tests[i]["status"]=="estimated"
            and best<.05 and
            (tests[i]["ci95_route"][0]>0 or tests[i]["ci95_route"][1]<0))
    return tests

def estimate_richness(contrasts):
    test=[]
    for k,name in enumerate(FRACTIONS):
        sub=contrasts[contrasts.habitat==name]
        for mode in ("any","strong"):
            col="delta_"+mode
            rr=sub.groupby(["state","route"])[col].mean().reset_index()
            n=int(len(rr)); states=int(rr.state.nunique())
            base={"mapped_class":name,"mode":mode,
                  "n_mixed_runs":int(sub.run_id.nunique()),
                  "n_physical_routes":n,"n_states":states,
                  "not_an_individual_species_preference":True}
            if n<30 or states<5:
                test.append({**base,"status":"underpowered"})
                continue
            x=rr[col].to_numpy(float)
            mean=float(x.mean()); se=float(x.std(ddof=1)/math.sqrt(n))
            tcrit=float(student_t.ppf(.975,n-1))
            p=float(2*student_t.sf(abs(mean/se),n-1)) if se>0 else 1.
            ci=[mean-tcrit*se,mean+tcrit*se]
            stmean=rr.groupby("state")[col].mean().to_numpy(float)
            e=rr.groupby("state")[col].mean()
            early=sub[sub.year<=2009].groupby("route")[col].mean()
            late=sub[sub.year>=2010].groupby("route")[col].mean()
            test.append({**base,"status":"estimated",
                 "route_equal_delta_taxon_units_per_stop":mean,
                 "se_route":se,"ci95_route":ci,"route_t_p":p,
                 "route_signflip":route_sign_flip(x,SEED+10*k+(0 if mode=="any" else 1)),
                 "fraction_routes_positive":float(np.mean(x>0)),
                 "n_states_positive":int((e>0).sum()),
                 "state_equal_delta_sensitivity":float(stmean.mean()),
                 "early_2001_2009_route_mean":float(early.mean()) if len(early) else None,
                 "early_routes":int(len(early)),
                 "late_2010_2015_route_mean":float(late.mean()) if len(late) else None,
                 "late_routes":int(len(late)),
                 "time_periods_not_independent_training_or_NWI_validation":True})
    if len(test)!=8:raise RuntimeError("Predeclared 8 plant richness tests lost")
    return bh_family(test)

def balanced_community(run):
    measures=[f"{a}_{b}" for a in ("alpha","gamma","beta","active_stops")
              for b in ("any","strong")]
    routes=run.groupby(["state","route"],sort=False)[measures].mean()
    states=routes.groupby(level=0).mean()
    outputs={}
    for var in measures:
        n_valid=int(run[var].notna().sum())
        outputs[var]={"overall_equal_route":float(routes[var].mean()) if routes[var].notna().any() else None,
           "overall_equal_state":float(states[var].mean()) if states[var].notna().any() else None,
           "n_valid_route_nights":n_valid,
           "zero_route_nights":int((run[var]==0).sum())}
    return outputs

def frozen_biotic_evidence():
    fp=ROOT/"exploration"
    s=json.loads((fp/"NAAMP_TAXON_SPECIFIC_AQUATIC_VEGETATION_RESULT_V0_1.json").read_text())
    p=json.loads((fp/"NAAMP_PLANT_CONDITIONED_FROG_PAIR_NETWORK_RESULT_V0_1.json").read_text())
    t=json.loads((fp/"NAAMP_THIRD_TAXON_AQUATIC_PLANT_RESULT_V0_1.json").read_text())
    if len(s["summary"]["BH_FDR_05_taxa"])!=5 or s["summary"]["eligible_taxa"]!=25:
        raise RuntimeError("Previous source single-taxon findings changed")
    result={"first_order_species_site_vegetation":{
             "n_eligible_taxon_units":25,"n_BH_positive_taxon_units":5,
             "named_positive_taxa":[x["taxon"] for x in s["summary"]["BH_FDR_05_taxa"]]},
            "second_order_conditional_acoustic_pair_edges":{},
            "third_order_acoustic_motif":{},
            "causal_plant_x_interacting_species_demonstrated":False}
    for mode in ("any","strong"):
        cov=p["modes"][mode]["coverage"]
        result["second_order_conditional_acoustic_pair_edges"][mode]={
          "eligible_pairs":cov["n_eligible_species_pairs"],
          "BH_supported_pairs":cov["n_supported_edges"],
          "positive":cov["positive_supported_edges"],"negative":cov["negative_supported_edges"],
          "n_reference_route_nights":cov["original_test_runs"]}
        m=t["modes"][mode]
        result["third_order_acoustic_motif"][mode]={
          "centered_triads_p":m["global_motifs"]["triad_sq"]["cluster_inference"]["p_two_sided"],
          "third_order_excess_supported":m["classification"]["centered_triplet_excess_over_crossfit_NWI"],
          "causal_third_order_interaction":False}
    assert result["second_order_conditional_acoustic_pair_edges"]["any"]["BH_supported_pairs"]==43
    assert result["second_order_conditional_acoustic_pair_edges"]["strong"]["BH_supported_pairs"]==14
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_hierarchical_vegetation_macro")
    p.add_argument("--synthetic-only",action="store_true")
    a=p.parse_args()
    qa=test_synthetic()
    if a.synthetic_only:
        print(json.dumps(qa,sort_keys=True))
        return
    stop,run,contrasts,scope=load_data()
    nested=group_decomposition(stop,VARS)
    matched=estimate_richness(contrasts)
    community=balanced_community(run)
    out={"analysis":"NAAMP_hierarchical_vegetation_frog_metacommunity_v0_1",
         "status":"empirical_multilevel_NAAMP_vegetation_macrostudy_executed",
         "date":"2026-10-23","frozen_spec":SOURCE,"synthetic_QA":qa,
         "source":scope,"variance_partition":nested,
         "within_night_mapped_vegetation_richness_eight_tests":matched,
         "alpha_gamma_beta":community,
         "existing_taxon_pair_triplet_levels":frozen_biotic_evidence(),
         "scientific_limits":{
             "forecast_or_predictive_model_fitted":False,
             "NWI_contemporaneous_2001_2015_botanical_plant_cover":False,
             "NWI_fraction_is_mapped_wetland_polygon_class_not_plant_abundance":True,
             "plant_causal_frog_effect_identified":False,
             "frog_frog_interaction_causal":False,
             "fish_and_predatory_insects_measured":False,
             "three_biotic_species_causal_interaction_identified":False,
             "JAE_RC6_main_paper_and_SI_modified":False}}
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("HIERARCHICAL_NAAMP_MACRO_BEGIN")
    print(json.dumps({"status":out["status"],"QA":qa,
        "source":scope,
        "variance_pct_state_equal":{k:v["state_equal"]["pct_total_variance"] for k,v in nested.items()},
        "variance_pct_route_equal":{k:v["route_equal"]["pct_total_variance"] for k,v in nested.items()},
        "within_night_richness_contrasts":matched,
        "metacommunity_diversity":community,
        "existing_multitaxon_hierarchy":out["existing_taxon_pair_triplet_levels"]},sort_keys=True,allow_nan=False))
    print("HIERARCHICAL_NAAMP_MACRO_END")

if __name__=="__main__":
    main()
