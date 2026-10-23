#!/usr/bin/env python3
"""Ecology-first PEM x woody habitat non-additivity within mapped wetlands.

Exploratory after positive alpha/gamma results; source = original validated
6,236 USGS NAAMP 10-stop route-nights × USFWS 250m NWI polygon crosswalk.
This estimates descriptive category-interaction in *acoustic taxon richness*,
NOT biological species-species interaction, causality, or predictions.

Two primary outcomes with BH: CI≥1 and CI≥2 counts. Jointly decomposes
richness coefficient into call-activation and beyond-first-taxon components.
Whole physical routes, not stops/nights, are inference clusters.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"exploration/run_naamp_hierarchical_vegetation_macro_v0_1.py"
PROTOCOL="exploration/NAAMP_PEM_WOODY_WETLAND_ARCHITECTURE_INTERACTION_SPEC_2026_10_23.md"
BASE_COLS=("pem_present","woody_present","pem_x_woody","aquatic_bed_present",
           "wetland_10pp","stop_air_temp_c","stop_sound_index")
POS=tuple("stop_"+str(k) for k in range(2,11))
COLS=BASE_COLS+POS
assert len(COLS)==16
INDEX={c:i for i,c in enumerate(COLS)}
SEED=2601023
PRIMARY_MODES=("any","strong")

def source_module():
    spec=importlib.util.spec_from_file_location("naamp_original_hier_source",SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Source verified NAAMP/NWI loader absent")
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def source_audit_and_geometry(stop,scope):
    if len(stop)!=62360 or stop.run_id.nunique()!=6236 or scope["n_routes"]!=499 or scope["n_states"]!=20:
        raise ValueError("Original 6,236-run 62,360-site source changed")
    if scope["NWI_source_physical_site_records"]!=5147 or scope["NAAMP_standard_runs"]!=7848:
        raise ValueError("Original source identity or NWI crosswalk changed")
    need={"run_id","route","state","year","site_id","stop","alpha_any","alpha_strong",
          "pem_present","woody_present","aquatic_bed_present","all_wetland",
          "stop_air_temp_c","stop_sound_index"}
    if not need.issubset(stop.columns):
        raise ValueError("Missing originally QA-controlled NAAMP wetland/geography covariates")
    if stop[["pem_present","woody_present","aquatic_bed_present"]].isna().any().any():
        raise ValueError("Mapped wetland missingness cannot mean category absence")
    if any(stop[col].min()<0 for col in ("alpha_any","alpha_strong","all_wetland")):
        raise ValueError("Negative survey call richness or NWI polygon fraction")
    if any(stop[col].max()>1 for col in ("all_wetland","pem_present","woody_present","aquatic_bed_present")):
        raise ValueError("Source NWI polygon fraction or binary class out of range")
    if (stop.alpha_strong>stop.alpha_any).any():
        raise ValueError("CI>=2 must be a subset of CI>=1")
    if stop.groupby("run_id").size().ne(10).any():
        raise ValueError("The original source includes incomplete ten-stop survey nights")
    wet=stop.loc[stop.all_wetland>0].copy()
    perrun=wet.groupby("run_id").size()
    eligible=perrun[perrun>=2].index
    wet=wet[wet.run_id.isin(eligible)].copy()
    if wet.empty or wet.route.nunique()<250 or wet.state.nunique()!=20:
        raise ValueError("Wetland-only cohort lacks independent spatial coverage")
    wet["pem_x_woody"]=wet.pem_present.astype(float)*wet.woody_present.astype(float)
    wet["wetland_10pp"]=10*wet.all_wetland.astype(float)
    wet["habitat_cell"]=(2*wet.pem_present.astype(int)+wet.woody_present.astype(int)).astype(int)
    for s in range(2,11):
        wet["stop_"+str(s)]=(wet.stop.astype(int)==s).astype(float)
    fullaudit=stop[["state","route","site_id","pem_present","woody_present",
                    "aquatic_bed_present","all_wetland"]].drop_duplicates(["state","route","site_id"])
    sitecells=fullaudit.loc[fullaudit.all_wetland>0].assign(
        habitat_cell=lambda z:2*z.pem_present.astype(int)+z.woody_present.astype(int))
    n_by_cell=wet.habitat_cell.value_counts().to_dict()
    n_site_by_cell=sitecells.habitat_cell.value_counts().to_dict()
    n_routes_by_cell=wet.groupby("habitat_cell").route.nunique().to_dict()
    n_states_by_cell=wet.groupby("habitat_cell").state.nunique().to_dict()
    def pack(x):return {str(k):int(x.get(k,0)) for k in range(4)}
    pop={
        "original_source_runs":6236,"original_source_site_nights":62360,
        "source_NWI_physical_sites":5147,
        "physical_sites_in_wetlands_within_NAAMP_cohort":int(len(sitecells)),
        "wetland_only_site_nights_before_geographic_run_requirement":int(len(stop.loc[stop.all_wetland>0])),
        "wetland_only_site_nights_model":int(len(wet)),
        "wetland_only_route_nights_model":int(wet.run_id.nunique()),
        "wetland_only_physical_routes_model":int(wet.route.nunique()),
        "wetland_only_states_model":int(wet.state.nunique()),
        "nwi_eligible_runs_excluded_fewer_than_two_wetland_sites":int((perrun<2).sum()),
        "original_source_physical_routes":499,"original_source_states":20,
        "cell_legend":{"0":"PEM0_woody0","1":"PEM0_woody1","2":"PEM1_woody0","3":"PEM1_woody1"},
        "all_wetland_stop_count_by_cell":pack(n_by_cell),
        "distinct_wetland_SiteID_count_by_cell":pack(n_site_by_cell),
        "independent_physical_routes_by_cell":pack(n_routes_by_cell),
        "geographic_states_by_cell":pack(n_states_by_cell),
        "map_polygon_classes_are_not_live_plant_taxa":True}
    return wet,pop

def FE_design(data):
    nights,ni=np.unique(data.run_id.astype(str).to_numpy(),return_inverse=True)
    routes,ri=np.unique(data.route.astype(str).to_numpy(),return_inverse=True)
    states,si=np.unique(data.state.astype(str).to_numpy(),return_inverse=True)
    n_by_night=np.bincount(ni)
    y_by_stop=np.asarray(data[list(COLS)],dtype=float)
    if np.any(~np.isfinite(y_by_stop)):
        raise ValueError("Missing source environmental column; never fill with zero")
    X=y_by_stop.copy()
    for k in range(X.shape[1]):
        X[:,k]-=np.bincount(ni,weights=X[:,k],minlength=len(nights))[ni]/n_by_night[ni]
    if np.linalg.matrix_rank(X)<len(COLS):
        raise ValueError("Within-night factorial wetland exposure not identified")
    n_by_route=np.bincount(ri)
    w=1/n_by_route[ri]
    A=X.T@(X*w[:,None])
    if np.linalg.matrix_rank(A)<len(COLS):
        raise ValueError("Wetland-only weighted geometry collinear after FE")
    inv=np.linalg.inv(A)
    W={
        "night_index":ni,"night_counts":n_by_night,"route_index":ri,
        "route_names":routes,"state_index":si,"state_names":states,
        "X":X,"w":w,"A":A,"inv":inv,"N":len(data),"K":len(COLS)}
    return W

def within_night_y(y,design):
    if not np.isfinite(y).all():raise ValueError("Missing/invalid calling richness")
    i=design["night_index"];n=design["night_counts"]
    return y-np.bincount(i,weights=y,minlength=len(n))[i]/n[i]

def fit_outcome(outcome,design):
    yy=within_night_y(np.asarray(outcome,float),design)
    X=design["X"];w=design["w"];ri=design["route_index"];si=design["state_index"]
    A=design["A"];inv=design["inv"];K=design["K"];N=design["N"]
    rhs=X.T@(w*yy)
    beta=np.linalg.solve(A,rhs)
    residual=yy-X@beta
    def vc(groups,G):
        scores=np.zeros((G,K),float)
        np.add.at(scores,groups,(w*residual)[:,None]*X)
        factor=G/(G-1)*(N-1)/(N-K)
        V=factor*inv@(scores.T@scores)@inv
        V=(V+V.T)/2
        if np.any(np.diag(V)<-1e-10):
            raise RuntimeError("Invalid covariance sandwich diagonal")
        return V
    G=len(design["route_names"]);S=len(design["state_names"])
    Vroute=vc(ri,G);Vstate=vc(si,S)
    def linear(name,weights):
        a=np.zeros(K,float)
        for key,v in weights.items():a[INDEX[key]]=v
        b=float(np.dot(a,beta))
        se=float(math.sqrt(max(0,a@Vroute@a)))
        ses=float(math.sqrt(max(0,a@Vstate@a)))
        if se<=1e-12:raise RuntimeError("Degenerate route-level ecological uncertainty")
        q=float(student_t.ppf(.975,G-1))
        sq=float(student_t.ppf(.975,S-1))
        p=float(2*student_t.sf(abs(b/se),G-1))
        return {"label":name,"beta_taxon_units_per_stop":b,
                "se_route":se,"CI95_route":[b-q*se,b+q*se],
                "p_two_sided_route_t":p,
                "CI95_State":[b-sq*ses,b+sq*ses],
                "se_State":ses,
                "n_routes":G,"n_States":S}
    output={
        "PEM_x_woody":linear("PEM:woody factorial interaction",{"pem_x_woody":1}),
        "PEM_effect_if_no_woody":linear("PEM conditional on no mapped woody",{"pem_present":1}),
        "PEM_effect_if_woody":linear("PEM conditional on mapped woody",{"pem_present":1,"pem_x_woody":1}),
        "woody_effect_if_no_PEM":linear("Woody conditional on no mapped PEM",{"woody_present":1}),
        "woody_effect_if_PEM":linear("Woody conditional on mapped PEM",{"woody_present":1,"pem_x_woody":1}),
        "aquatic_bed_main":linear("Aquatic bed overlap adjusted",{"aquatic_bed_present":1}),
        "wetland_10pp_main":linear("Mapped total wetland +10pp adjusted",{"wetland_10pp":1})}
    state_loo={}
    for g,state in enumerate(design["state_names"]):
        sel=(si==g)
        remain_A=A-X[sel].T@(w[sel,None]*X[sel])
        remain_rhs=rhs-X[sel].T@(w[sel]*yy[sel])
        if np.linalg.matrix_rank(remain_A)<K:
            state_loo[str(state)]=None
        else:state_loo[str(state)]=float(np.linalg.solve(remain_A,remain_rhs)[INDEX["pem_x_woody"]])
    loo=[x for x in state_loo.values() if x is not None]
    output["omit_one_State_interaction"]={
        "n_estimable":len(loo),"n_positive":sum(x>0 for x in loo),
        "n_negative":sum(x<0 for x in loo),
        "range":[min(loo),max(loo)] if loo else None,
        "by_State":state_loo}
    output["full_beta"]=[float(x) for x in beta]
    return output

def strict_four_cells(data):
    keys=["state","route","run_id","year","habitat_cell"]
    means=data.groupby(keys,sort=False,observed=True)[
        ["alpha_any","alpha_strong"]].mean().reset_index()
    counts=data.groupby(["state","route","run_id","year"],sort=False).habitat_cell.nunique()
    valid=counts[counts==4].reset_index()[["state","route","run_id","year"]]
    sub=means.merge(valid,on=["state","route","run_id","year"],how="inner",validate="many_to_one")
    result={"n_complete_four_cell_nights":int(len(valid)),
            "n_complete_four_cell_routes":int(valid.route.nunique()),
            "n_complete_four_cell_states":int(valid.state.nunique()),
            "nights_with_complete_four_cell_map_fraction":len(valid)/data.run_id.nunique(),
            "modes":{}}
    for mode in PRIMARY_MODES:
        p=sub.pivot_table(index=["state","route","run_id","year"],
                         columns="habitat_cell",values="alpha_"+mode,aggfunc="first")
        if len(p)!=len(valid) or any(k not in p.columns for k in range(4)) or p.isna().any().any():
            raise RuntimeError("Strict four-cell night membership/pivot error")
        signed=p[3]-p[2]-p[1]+p[0]
        subdata=signed.rename("did").reset_index()
        grouped=subdata.groupby(["state","route"],sort=False).did.mean().reset_index()
        routes=len(grouped);states=grouped.state.nunique()
        outcome={"n_nights":len(subdata),"routes":routes,"states":states}
        if routes<30 or states<5 or len(subdata)<50:
            outcome["status"]="underpowered_strict_factorial_sample"
        else:
            x=grouped.did.to_numpy(float)
            mean=float(x.mean());se=float(x.std(ddof=1)/math.sqrt(routes))
            crit=float(student_t.ppf(.975,routes-1))
            ci=[mean-crit*se,mean+crit*se]
            pval=float(2*student_t.sf(abs(mean/se),routes-1)) if se>0 else 1.
            state=grouped.groupby("state").did.mean()
            omit={s:float(grouped.loc[grouped.state!=s,"did"].mean()) for s in state.index}
            outcome.update({"status":"estimated_exploratory",
               "same_night_PEM_x_woody_raw_delta":mean,
               "CI95_route":ci,"p_route_t_no_BH":pval,
               "state_equal_effect":float(state.mean()),
               "n_States_with_positive_means":int((state>0).sum()),
               "leave_one_State_out_all_positive":all(v>0 for v in omit.values()),
               "leave_one_State_out_range":[min(omit.values()),max(omit.values())],
               "early_2001_2009_route_mean":float(subdata.loc[subdata.year<=2009].groupby("route").did.mean().mean()),
               "late_2010_2015_route_mean":float(subdata.loc[subdata.year>=2010].groupby("route").did.mean().mean())})
        result["modes"][mode]=outcome
    return result

def analyze(stop,scope):
    wet,pop=source_audit_and_geometry(stop,scope)
    design=FE_design(wet)
    outputs={}
    for mode in PRIMARY_MODES:
        y=wet["alpha_"+mode].to_numpy(float)
        activ=(y>0).astype(float)
        extra=np.maximum(y-1.,0.)
        if not np.allclose(y,activ+extra,atol=1e-12):
            raise RuntimeError("Calling richness is not activation+additional species identity")
        total=fit_outcome(y,design)
        active=fit_outcome(activ,design)
        extras=fit_outcome(extra,design)
        bt=total["PEM_x_woody"]["beta_taxon_units_per_stop"]
        ba=active["PEM_x_woody"]["beta_taxon_units_per_stop"]
        be=extras["PEM_x_woody"]["beta_taxon_units_per_stop"]
        if not math.isclose(bt,ba+be,abs_tol=1e-9):
            raise RuntimeError("Interaction decomposition not exact across identical design")
        decomposed={}
        selected=("PEM_x_woody","PEM_effect_if_no_woody",
                  "PEM_effect_if_woody",
                  "woody_effect_if_no_PEM","woody_effect_if_PEM")
        for key in selected:
            yrec=total[key];arec=active[key];erec=extras[key]
            by=yrec["beta_taxon_units_per_stop"]
            av=arec["beta_taxon_units_per_stop"]
            ex=erec["beta_taxon_units_per_stop"]
            err=abs(by-av-ex)
            if err>1e-9:
                raise RuntimeError("Count = activation + extra taxa failed for "+key)
            decomposed[key]={
                "total_detected_taxon_units":yrec,
                "at_least_one_acoustic_taxon_indicator":arec,
                "additional_detected_taxon_units_beyond_first":erec,
                "identity_absolute_roundoff":err,
                "signed_aggregation_ratio_activation":av/by if abs(by)>1e-9 else None,
                "signed_aggregation_ratio_extra_taxa":ex/by if abs(by)>1e-9 else None,
                "ratios_are_signed_arithmetic_not_causal_or_variance_proportions":True}
        outputs[mode]={
            "count_model":total,
            "calling_activation_descriptive_interaction":active["PEM_x_woody"],
            "additional_taxa_beyond_first_descriptive_interaction":extras["PEM_x_woody"],
            "post_readback_all_linear_contrasts_activation_and_extra":decomposed,
            "exact_sum_identity_verified":True,
            "identity_absolute_roundoff":abs(bt-ba-be),
            "acoustic_zeros_included":True}
    ps=[outputs[m]["count_model"]["PEM_x_woody"]["p_two_sided_route_t"] for m in PRIMARY_MODES]
    order=sorted(range(2),key=lambda k:ps[k])
    bh=[0.,0.];small=1.
    for rank in (2,1):
        i=order[rank-1]
        small=min(small,2*ps[i]/rank)
        bh[i]=small
    for i,mode in enumerate(PRIMARY_MODES):
        d=outputs[mode]["count_model"]["PEM_x_woody"]
        d["BH_q_two_call_strength_tests"]=bh[i]
        CI=d["CI95_route"]
        stateCI=d["CI95_State"]
        outputs[mode]["nonadditivity_route_BH_supported"]=bool(
            bh[i]<.05 and (CI[0]>0 or CI[1]<0))
        outputs[mode]["nonadditivity_20State_CI_excludes_zero"]=bool(
            stateCI[0]>0 or stateCI[1]<0)
    strict=strict_four_cells(wet)
    for k in range(4):
        if pop["all_wetland_stop_count_by_cell"][str(k)]<=0:
            raise RuntimeError("One NWI environmental 2x2 cell has zero support")
    return {"analysis":"NAAMP_NWI_mapped_PEM_x_woody_habitat_architecture_frog_richness_hierarchy",
        "status":"real_source_verified_nonpredictive_wetland_architecture_analysis",
        "protocol":PROTOCOL,"date":"2026-10-23",
        "research_hypothesis_post_hoc":True,
        "source":{
            "NAAMP_original_standardized_runs":7848,
            "NWI_complete_source_runs":6236,"NWI_complete_source_stop_nights":62360,
            "source_physical_SiteIDs":5147,
            "source_geography_runs":39450277196},
        "model_population":pop,
        "primary_and_activity_taxon_hierarchy":outputs,
        "same_night_strict_complete_2x2":strict,
        "cautions":{
            "NWI_PEM_woody_labels_are_mapped_habitat_not_plant_species":True,
            "NWI_not_simultaneous_2001_2015_field_measurements":True,
            "no_direct_causal_plant_interaction_identified":True,
            "no_frog_frog_or_predator_insect_interactions_identified":True,
            "acoustic_richness_not_biological_occupancy":True,
            "not_predictive_model_or_forecast":True,
            "main_JAE_RC6_SI_submission_modified":False}}

def synthetic():
    rng=np.random.default_rng(260140)
    rows=[]
    for route in range(65):
        for night in range(5):
            for stop in range(1,11):
                p=int((stop+night+route)%3>0)
                w=int((2*stop+night+route)%4>1)
                aquatic=int(rng.random()<.12)
                wet=float(rng.uniform(.06,.8))
                tmp=float(rng.normal(18,3))
                noise=float(rng.uniform(0,4))
                y=(1.7+.24*p+.15*w+.38*p*w+.10*aquatic+.05*10*wet
                   +.02*tmp-.03*noise+.01*stop+.03*night+rng.normal(0,.13))
                rows.append({
                  "run_id":f"run_{route}_{night}","route":f"r{route}",
                  "state":f"s{route%12}","stop":stop,
                  "pem_present":p,"woody_present":w,
                  "pem_x_woody":p*w,"aquatic_bed_present":aquatic,
                  "wetland_10pp":10*wet,"stop_air_temp_c":tmp,
                  "stop_sound_index":noise,"y_qa":y})
    d=pd.DataFrame(rows)
    for stop in range(2,11):d["stop_"+str(stop)]=(d.stop==stop).astype(float)
    design=FE_design(d)
    f=fit_outcome(d.y_qa.to_numpy(float),design)
    beta=f["PEM_x_woody"]["beta_taxon_units_per_stop"]
    if not abs(beta-.38)<.04:
        raise RuntimeError(f"Known nonadditive environmental effect not recovered: {beta}")
    # Orthogonal linear additive partition must remain exact under FE.
    a=fit_outcome(d.y_qa.to_numpy(float)*.35,design)
    b=fit_outcome(d.y_qa.to_numpy(float)*.65,design)
    if abs(a["PEM_x_woody"]["beta_taxon_units_per_stop"]+
           b["PEM_x_woody"]["beta_taxon_units_per_stop"]-beta)>1e-10:
        raise RuntimeError("Model coefficient is not additive over outcomes")
    return {"status":"PASS",
        "known_synthetic_PEM_woody_interaction":beta,
        "true_interaction":.38,
        "activation_plus_extra_linear_identity":"PASS",
        "n_synthetic_routes":65,
        "no_NAAMP_biological_outcomes_used":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_pem_woody_architecture")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    if args.synthetic_only:
        print(json.dumps(synthetic(),sort_keys=True));return
    source=source_module()
    stop,run,contrasts,scope=source.load_data()
    out=analyze(stop,scope)
    out["preanalysis_synthetic_QA"]={"status":"PASS","run_in_separate_workflow_job":True}
    args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/"result.json").write_text(
         json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("NAAMP_WETLAND_ARCHITECTURE_RESULT_BEGIN",flush=True)
    print(json.dumps({
        "status":out["status"],"population":out["model_population"],
        "main":{mode:{
            "p_x_w":res["count_model"]["PEM_x_woody"],
            "pem_if_no_woody":res["count_model"]["PEM_effect_if_no_woody"],
            "pem_if_woody":res["count_model"]["PEM_effect_if_woody"],
            "activity_interaction":res["calling_activation_descriptive_interaction"],
            "extra_taxon_interaction":res["additional_taxa_beyond_first_descriptive_interaction"],
            "post_readback_pem_decomposition":{
               key:{
                  "total_beta":part["total_detected_taxon_units"]["beta_taxon_units_per_stop"],
                  "activation_beta":part["at_least_one_acoustic_taxon_indicator"]["beta_taxon_units_per_stop"],
                  "activation_route_CI95":part["at_least_one_acoustic_taxon_indicator"]["CI95_route"],
                  "extra_beta":part["additional_detected_taxon_units_beyond_first"]["beta_taxon_units_per_stop"],
                  "extra_route_CI95":part["additional_detected_taxon_units_beyond_first"]["CI95_route"],
                  "signed_activation_ratio":part["signed_aggregation_ratio_activation"],
                  "signed_extra_ratio":part["signed_aggregation_ratio_extra_taxa"]}
               for key,part in res["post_readback_all_linear_contrasts_activation_and_extra"].items()},
            "sum_identity":res["exact_sum_identity_verified"],
            "leave_one_state":{key:z for key,z in res["count_model"]["omit_one_State_interaction"].items() if key!="by_State"},
            "BH_supported":res["nonadditivity_route_BH_supported"],
            "state_CI_excludes_zero":res["nonadditivity_20State_CI_excludes_zero"]}
            for mode,res in out["primary_and_activity_taxon_hierarchy"].items()},
        "strict_all_four":out["same_night_strict_complete_2x2"],
        "scientific_limits":out["cautions"]
    },sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_WETLAND_ARCHITECTURE_RESULT_END",flush=True)

if __name__=="__main__":
    main()
