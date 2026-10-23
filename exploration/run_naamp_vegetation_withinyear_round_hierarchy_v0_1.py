#!/usr/bin/env python3
"""NAAMP within-year survey-round hierarchy of mapped wetland frog communities.

Ecology-first, no forecast or causal plants: same route, same YEAR and same
ordered ten physical SiteIDs at NAAMP rounds 1-4. NWI 250m PEM+/PEM0 compared
only among mapped-wetland stops; original source NAAMP 2001-15, 6236 full
site+temperature+noise nights and outcome-blind 5147-site NWI source.
Four pre-frozen categorical omnibus outcomes (CI>=1/2 alpha, rarefied gamma).
Route-year FE, route cluster and State CI; repeated same-Stop taxon labels
are acoustic monitoring incidence, not species populations or interactions.
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
from scipy.stats import t as student_t, f as fdist

ROOT=Path(__file__).resolve().parents[1]
SPEC="exploration/NAAMP_VEGETATION_WITHINYEAR_ROUND_HIERARCHY_SPEC_2026_10_23.md"
MODES=(("any",1),("strong",2))
OUTCOMES=("alpha_any","alpha_strong","gamma_any","gamma_strong")
PREDICTORS=("round2","round3","round4","tempdiff_PEMminus_other_C","noisediff_PEMminus_other")
SEED=26010424
N_FLIPS=4999

def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise RuntimeError("Missing pinned NAAMP+NWI source "+str(path))
    x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
    return x

def source():
    src=mod("naamp_full_vegetation",
         ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    rar=mod("naamp_exact_taxon_rarefaction",
         ROOT/"exploration/run_naamp_rarefied_vegetation_gamma_v0_1.py")
    nwi,audit=src.read_nwi(
         ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
         ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    if (not audit.get("preflight_eligible") or audit.get("mode")!="full"
        or len(audit["overlay"]["shards"])!=12
        or audit["overlay"]["site_records"]!=5147
        or audit["matched_route_source_only_audit"]["frog_outcomes_read"] is not False
        or len(nwi)!=5147):
        raise ValueError("Original 12-shard response-blind physical-site NWI geometry no longer valid")
    raw=src.hist.load_retry()
    runs,_=src.base.build_runs(raw)
    if len(runs)!=7848:raise ValueError("Original NAAMP 7,848 standard runs drift")
    eligible=set(runs.RunID.astype(str))
    sampled,_=src.spatial.stop_matrix(raw,eligible)
    sites=src.hist.site_map(raw,eligible)
    ci=src.hist.ci_map(raw,eligible,sampled)
    stop_env=src.get_temps_and_detection(raw,runs,sampled)
    observers={str(x.get("RunID") or "").strip():str(x.get("ObserverTrackingID") or "").strip()
               for x in raw["Runs.csv"]}
    good={}
    coverage=Counter()
    for obs in runs.itertuples(index=False):
        rid=str(obs.RunID)
        stops=sorted(sampled.get(rid,set()),key=int)
        if len(stops)!=10:raise ValueError("Standard source run has not ten stops")
        state=str(obs.State)
        route_no=str(obs.RouteNumber)
        siteids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,route_no,str(sid)) not in nwi.index
               for sid in siteids):
            coverage["NWI_missing_complete_10stop_geography"]+=1;continue
        if len(set(siteids))!=10:
            coverage["nonunique_physical_SiteID_run"]+=1;continue
        env=[stop_env.get((rid,st),{}) for st in stops]
        if any(any(not np.isfinite(e.get(name,np.nan))
                 for name in ("stop_air_temp_c","stop_sound_index")) for e in env):
            coverage["missing_temperature_or_noise"]+=1;continue
        mapped=nwi.loc[[(state,route_no,str(sid)) for sid in siteids],
              ["nwi_emergent_cover_250m","nwi_all_wetland_cover_250m"]].to_numpy(float)
        if not np.isfinite(mapped).all() or (mapped<-1e-9).any() or (mapped>1+1e-9).any():
            raise ValueError("Mapped NWI cover nonfinite or outside [0,1]")
        pem=mapped[:,0]>0
        wet=mapped[:,1]>0
        if np.any(pem&~wet):raise ValueError("Mapped PEM not inside mapped total wetland")
        group=(state,route_no,int(obs.SurveyYear))
        roundn=int(obs.RunNumber)
        if roundn not in (1,2,3,4):
            raise ValueError("Protocol round outside pre-fixed 1 to 4")
        good[rid]={
            "rid":rid,"group":group,
            "route":state+":"+route_no,"state":state,
            "year":int(obs.SurveyYear),"round":roundn,
            "doy":int(obs.doy),"observer":observers.get(rid,""),
            "physical_sites":tuple(str(x) for x in siteids),
            "pem":tuple(bool(x) for x in pem),
            "wet":tuple(bool(x) for x in wet),
            "stoplabels":tuple(stops),
            "temp":np.asarray([x["stop_air_temp_c"] for x in env],float),
            "noise":np.asarray([x["stop_sound_index"] for x in env],float)}
        coverage["NWI_environment_complete_run_nights"]+=1
    if len(good)!=6236 or coverage["NWI_environment_complete_run_nights"]!=6236:
        raise ValueError("Original 6,236 complete NAAMP+NWI source population drift")
    if len({v["route"] for v in good.values()})!=499 or len({v["state"] for v in good.values()})!=20:
        raise ValueError("Source 499 routes/20 States no longer reproduced")
    return good,ci,rar,{
      "source_NAAMP_standard_runs":7848,
      "source_NWI_complete_run_nights":6236,
      "source_all_complete_stop_nights":62360,
      "source_NWI_original_physical_SiteIDs":5147,
      "source_routes":499,"source_states":20,
      "source_verified_geography_Actions_run":39450277196,
      "source_geo_exclusions":dict(coverage)}

def build_rounds(good,ci,rare):
    groups=defaultdict(lambda:defaultdict(list))
    for rid,meta in good.items():
        groups[meta["group"]][meta["round"]].append(rid)
    rows=[]
    count=Counter()
    cell_dist=Counter()
    d_monotonic_bad=0
    group_eligible={}
    for group,allrounds in sorted(groups.items()):
        count["route_year_groups_source"]+=1
        roundmap={}
        for r,values in allrounds.items():
            if len(values)==1:roundmap[r]=good[values[0]]
            else:
                count["duplicate_source_route_year_round_cells"]+=1
                count["duplicate_source_runs_excluded"]+=len(values)
        if len(roundmap)<2:
            count["route_year_groups_lt_2_unique_rounds"]+=1
            continue
        visits=[roundmap[r] for r in sorted(roundmap)]
        siteids=visits[0]["physical_sites"]
        if any(x["physical_sites"]!=siteids or x["stoplabels"]!=visits[0]["stoplabels"]
               for x in visits[1:]):
            count["route_year_groups_physical_stop_relocation"]+=1
            continue
        if any(x["pem"]!=visits[0]["pem"] or x["wet"]!=visits[0]["wet"] for x in visits[1:]):
            raise ValueError("NWI source GIS exposure drift at identical physical SiteID")
        wet=np.asarray(visits[0]["wet"],bool)
        pem=np.asarray(visits[0]["pem"],bool)
        pindices=np.flatnonzero(pem&wet)
        nindices=np.flatnonzero(wet&~pem)
        m=min(len(pindices),len(nindices))
        if m<2:
            count["route_year_groups_no_2plus_PEM_vs_other_wetland"]+=1
            continue
        if any(visits[j]["doy"]>=visits[j+1]["doy"] for j in range(len(visits)-1)):
            d_monotonic_bad+=1
        gid="|".join(map(str,group))
        group_eligible[gid]=len(visits)
        count["accepted_source_route_year_groups"]+=1
        count["same_site_accepted_source_nights"]+=len(visits)
        for v in visits:
            r=v["round"]
            cell_dist[r]+=1
            data={
                "route_year_id":gid,"route":v["route"],"state":v["state"],
                "year":v["year"],"round":r,"rid":v["rid"],
                "doy":v["doy"],"observer":v["observer"],
                "m_rarefaction":m,
                "n_PEM_mapped_wetland_stops":len(pindices),
                "n_other_mapped_wetland_stops":len(nindices),
                "tempdiff_PEMminus_other_C":float(v["temp"][pindices].mean()-v["temp"][nindices].mean()),
                "noisediff_PEMminus_other":float(v["noise"][pindices].mean()-v["noise"][nindices].mean())}
            for mode,threshold in MODES:
                stop_taxa=[{str(t) for t,c in ci.get((v["rid"],st),{}).items() if int(c)>=threshold}
                            for st in v["stoplabels"]]
                richness=np.asarray([len(x) for x in stop_taxa],float)
                activation=(richness>0).astype(float)
                extra=np.maximum(richness-1,0)
                if not np.array_equal(richness,activation+extra):
                    raise ValueError("Taxon count != activated+additional taxa")
                for name,x in (("alpha",richness),("activation",activation),("additional_taxa",extra)):
                    data[f"{name}_{mode}"]=float(np.mean(x[pindices])-np.mean(x[nindices]))
                expected=rare.stats_for_pools(
                   [stop_taxa[i] for i in pindices],
                   [stop_taxa[i] for i in nindices],m)
                data[f"gamma_{mode}"]=expected["delta_gamma"]
            rows.append(data)
    if not rows:raise RuntimeError("No seasonally repeated same-site NWI vegetation-source records")
    d=pd.DataFrame(rows)
    n_groups=d.route_year_id.nunique()
    if d.groupby("route_year_id").size().lt(2).any():
        raise RuntimeError("Accepted seasonal route-year has fewer than two survey rounds")
    if d.groupby("route_year_id").rid.nunique().lt(2).any():
        raise RuntimeError("Duplicate survey run in fixed route-year")
    for mode,_ in MODES:
        check=d[f"alpha_{mode}"]-(d[f"activation_{mode}"]+d[f"additional_taxa_{mode}"])
        if np.max(np.abs(check))>1e-10:
            raise RuntimeError("Source frog calling alpha is not additive in local activation and additional taxon classes")
    coverage={
       "source_complete_run_nights":6236,
       "eligible_unchanged_physical_site_route_year_groups":n_groups,
       "eligible_source_run_nights":len(d),
       "eligible_independent_physical_routes":int(d.route.nunique()),
       "eligible_states":int(d.state.nunique()),
       "sampled_survey_round_count":{str(r):int(cell_dist.get(r,0)) for r in (1,2,3,4)},
       "sampled_route_year_groups_per_round":{
             str(r):int(d.loc[d["round"]==r,"route_year_id"].nunique()) for r in (1,2,3,4)},
       "source_only_exclusions":dict(count),
       "route_year_groups_nonchronological_calendar_DOY":int(d_monotonic_bad),
       "fraction_groups_nonmonotonic_DOY":d_monotonic_bad/n_groups,
       "equal_rarefaction_m_distribution":{str(k):int(v) for k,v in d.m_rarefaction.value_counts().items()},
       "retained_original_taxon_complexes":True,
       "source_stop_SiteIDs_aligned_within_each_route_year":True,
       "mapped_250m_PEM_nonPEM_comparison_both_inside_wetlands":True}
    return d,coverage

def design(d,linear=False):
    x=d.copy()
    x["round2"]=(x["round"]==2).astype(float)
    x["round3"]=(x["round"]==3).astype(float)
    x["round4"]=(x["round"]==4).astype(float)
    if linear:
        colnames=("round_continuous",
                  "tempdiff_PEMminus_other_C","noisediff_PEMminus_other")
        x["round_continuous"]=x["round"].astype(float)
    else:colnames=PREDICTORS
    grp,gi=np.unique(x.route_year_id.astype(str).to_numpy(),return_inverse=True)
    routes,ri=np.unique(x.route.astype(str).to_numpy(),return_inverse=True)
    states,si=np.unique(x.state.astype(str).to_numpy(),return_inverse=True)
    N=len(x);G=len(routes);S=len(states);H=len(grp);K=len(colnames)
    groupn=np.bincount(gi)
    if np.any(groupn<2):raise ValueError("Missing 2+ survey rounds per fixed route-year")
    X=x[list(colnames)].to_numpy(float)
    if not np.isfinite(X).all():raise ValueError("Nonfinite predeclared nuisance or round contrast")
    for j in range(K):
        X[:,j]-=np.bincount(gi,weights=X[:,j],minlength=H)[gi]/groupn[gi]
    nroute=np.bincount(ri)
    w=1./nroute[ri]
    if np.linalg.matrix_rank(X*np.sqrt(w[:,None]))<K:
        raise ValueError("Categorical/linear survey rounds unidentifiable after route-year fixed effects")
    A=X.T@(w[:,None]*X)
    direct_counts={}
    for later in (2,3,4):
        ids=x.loc[x["round"].isin([1,later])].groupby("route_year_id")["round"].nunique()
        gids=ids[ids==2].index
        sub=x[x.route_year_id.isin(gids)]
        direct_counts[str(later)+"_versus_1"]={
            "paired_route_year_groups":int(len(gids)),
            "independent_routes":int(sub.route.nunique())}
        if not linear and sub.route.nunique()<20:
            raise ValueError("Survey round "+str(later)+" versus 1 lacks 20 independent routes")
    if not linear and (G<50 or S<5 or H<100):
        raise ValueError("Seasonal round ecology lacks independent route/State/year coverage")
    if N-K-H+1<=50:raise ValueError("Survey round route-year FE residual df too low")
    return {
        "data":x,"X":X,"A":A,"N":N,"K":K,"G":G,"S":S,"H":H,
        "grp":grp,"groupidx":gi,"groupn":groupn,
        "routes":routes,"route_i":ri,"states":states,"state_i":si,
        "w":w,"covariates":list(colnames),"n_route_per_round_pair":direct_counts,
        "linear":linear}

def fit(design, response, seed=SEED, full_tests=True):
    d=design["data"]
    Y=d[response].to_numpy(float)
    i=design["groupidx"];N=design["N"];K=design["K"];H=design["H"]
    G=design["G"];S=design["S"];X=design["X"];w=design["w"]
    if not np.isfinite(Y).all():raise ValueError("Missing acoustic composition endpoint")
    YC=Y-np.bincount(i,weights=Y,minlength=H)[i]/design["groupn"][i]
    A=design["A"];inv=np.linalg.inv(A)
    rhs=X.T@(w*YC)
    beta=np.linalg.solve(A,rhs)
    resid=YC-X@beta
    def clustered(idx,count):
        scores=np.zeros((count,K),float)
        np.add.at(scores,idx,X*(w*resid)[:,None])
        factor=count/(count-1)*(N-1)/(N-K-H+1)
        V=factor*inv@(scores.T@scores)@inv
        return (V+V.T)/2
    Vr=clustered(design["route_i"],G)
    Vs=clustered(design["state_i"],S)
    if np.any(np.diag(Vr)<-1e-12) or np.any(np.diag(Vs)<-1e-12):
        raise ValueError("Non-positive covariance diagonal at geographic clustering")
    coeff={c:float(v) for c,v in zip(design["covariates"],beta)}
    diag={}
    tcrit=float(student_t.ppf(.975,G-1))
    for j,c in enumerate(design["covariates"]):
        se=float(math.sqrt(max(0,Vr[j,j])))
        diag[c]={"beta":float(beta[j]),
                 "CI95_route":[float(beta[j]-tcrit*se),float(beta[j]+tcrit*se)],
                 "cluster_se_route":se,
                 "p_route_t":float(2*student_t.sf(abs(beta[j]/se),G-1)) if se>1e-12 else None}
    result={"outcome":response,"coefficients":coeff,"round_nuisance_CI95":diag,
            "independent_physical_routes":G,
            "states":S,"route_year_groups":H,"source_run_nights":N,
            "inference_unit":"whole_physical_monitoring_route",
            "exact_within_route_year_fixed_effects":True,
            "source_sequential_survey_round_proxy_not_universal_calendar_phenology":True}
    if not full_tests:return result
    if design["linear"]:
        return result
    if K!=5 or len(design["covariates"])!=5:
        raise RuntimeError("Frozen four-season categorical structure has drifted")
    Wald=beta[:3]
    Croute=Vr[:3,:3];Cstate=Vs[:3,:3]
    if np.linalg.matrix_rank(Croute)<3 or np.linalg.matrix_rank(Cstate)<3:
        raise RuntimeError("Cannot identify full three-df clustered round contrast")
    Froute=float(Wald@np.linalg.solve(Croute,Wald)/3)
    Fstate=float(Wald@np.linalg.solve(Cstate,Wald)/3)
    p_route=float(fdist.sf(Froute,3,G-1))
    p_state=float(fdist.sf(Fstate,3,S-1))
    # Wald test is descriptive route-robust observational categorical association.
    # A different route-symmetric null follows from the route-aggregated
    # FWL nuisance-orthogonalized three-vector under beta_rounds=0.
    Z=X[:,3:]
    Gram=Z.T@(w[:,None]*Z)
    if np.linalg.matrix_rank(Gram)<2:
        raise ValueError("Cannot form FWL nuisance-only null")
    residual_X=X[:,:3]-Z@np.linalg.solve(Gram,Z.T@(w[:,None]*X[:,:3]))
    residual_Y=YC-Z@np.linalg.solve(Gram,Z.T@(w*YC))
    weighted_scores=np.zeros((G,3),float)
    np.add.at(weighted_scores,design["route_i"],
              residual_X*(w*residual_Y)[:,None])
    score_sum=weighted_scores.sum(axis=0)
    score_v=weighted_scores.T@weighted_scores
    if np.linalg.matrix_rank(score_v)<3:
        raise ValueError("Physical route score covariance rank too low")
    st=float(score_sum@np.linalg.solve(score_v,score_sum))
    if not np.isfinite(st):raise RuntimeError("Nonfinite 3-round score reference")
    rng=np.random.default_rng(seed)
    large=0
    for begin in range(0,N_FLIPS,200):
        batch=min(200,N_FLIPS-begin)
        signs=rng.choice(np.array([-1.,1.]),size=(batch,G))
        sums=signs@weighted_scores
        invscore=np.linalg.inv(score_v)
        t=np.einsum("bi,ij,bj->b",sums,invscore,sums)
        large+=int(np.count_nonzero(t>=st-1e-12))
    flip_p=(large+1)/(N_FLIPS+1)
    # Same geography/state omitted fixed source and model; no reselection.
    state_omit={}
    for j,state in enumerate(design["states"]):
        sel=design["state_i"]==j
        Ai=A-X[sel].T@(w[sel,None]*X[sel])
        Bi=rhs-X[sel].T@(w[sel]*YC[sel])
        if np.linalg.matrix_rank(Ai)<K:state_omit[str(state)]=None
        else:state_omit[str(state)]=[float(v) for v in np.linalg.solve(Ai,Bi)[:3]]
    v=[x for x in state_omit.values() if x is not None]
    result.update({
      "three_df_categorical_round_omnibus":{
          "route_wald_F":Froute,"route_Wald_F_two_sided_P":p_route,
          "state_wald_F":Fstate,"State_Wald_F_P":p_state,
          "degree_of_freedom_round_contrasts":3,
          "route_cluster_student_denominator_df":G-1,
          "State_cluster_student_denominator_df":S-1},
      "route_multiround_FWL_signflip":{
          "draws":N_FLIPS,"plus_one_omnibus_P":flip_p,
          "score_stat_observed":st,
          "route_vector_scores_flipped_not_stop_or_night_records":True,
          "approximate_cluster_symmetry_not_vegetation_randomization":True},
      "leave_one_State_out":{
          "n_estimable":len(v),
          "round4_minus_round1_positive":sum(x[2]>0 for x in v),
          "round4_minus_round1_negative":sum(x[2]<0 for x in v),
          "round4_minus_round1_minmax":[min(x[2] for x in v),max(x[2] for x in v)] if v else None,
          "coefficient_vectors_by_omitted_State":state_omit}})
    return result

def BH(scores):
    p=[scores[x]["three_df_categorical_round_omnibus"]["route_Wald_F_two_sided_P"]
       for x in OUTCOMES]
    order=sorted(range(len(p)),key=lambda k:p[k])
    value=1.
    for rank in range(len(order),0,-1):
        k=order[rank-1]
        value=min(value,len(order)*p[k]/rank)
        scores[OUTCOMES[k]]["BH_q_four_omnibus"] =value
    primary=scores["alpha_any"]
    om=primary["three_df_categorical_round_omnibus"]
    fwl=primary["route_multiround_FWL_signflip"]
    return ("exploratory_route_robust_withinyear_PEM_phenological_heterogeneity"
            if om["route_Wald_F_two_sided_P"]<.05
              and primary["BH_q_four_omnibus"]<.05
              and fwl["plus_one_omnibus_P"]<.05
              and om["State_Wald_F_P"]<.05
            else "not_supported_by_joint_withinyear_multilevel_gates")

def diagnostics(d):
    years=d.groupby("route_year_id").size()
    groups=set(d.route_year_id.unique())
    table={}
    for r in (1,2,3,4):
        sub=d.loc[d["round"]==r]
        routes=sub.route.nunique()
        if not len(sub):raise ValueError("A protocol survey round has no source support")
        report={
           "round":r,"route_year_groups":int(sub.route_year_id.nunique()),
           "physical_routes":int(routes),
           "source_states":int(sub.state.nunique()),
           "sampled_stop_nights":int(10*len(sub)),
           "calendar_DOY_mean":float(sub.doy.mean()),
           "calendar_DOY_median":float(sub.doy.median()),
           "calendar_DOY_quantiles_25_75":[float(x) for x in sub.doy.quantile([.25,.75])],
           "observed_route_equal_delta":{}}
        for y in OUTCOMES:
            report["observed_route_equal_delta"][y]=float(sub.groupby("route")[y].mean().mean())
        table[str(r)]=report
    return {
       "survey_rounds":table,
       "n_source_route_year_groups":int(len(groups)),
       "n_route_year_groups_with_2rounds":int((years==2).sum()),
       "n_route_year_groups_with_3rounds":int((years==3).sum()),
       "n_route_year_groups_with_4rounds":int((years==4).sum())}

def same_observer(d):
    parts=[]
    for gid,group in d.groupby("route_year_id",sort=False):
        avail=group.loc[group.observer.astype(str).ne("")]
        if len(avail)<2:continue
        vc=avail.observer.astype(str).value_counts()
        top=sorted(vc.loc[vc==vc.max()].index)[0]
        chosen=avail.loc[avail.observer==top]
        if len(chosen)>=2:parts.append(chosen)
    if not parts:return None
    sub=pd.concat(parts,ignore_index=True)
    if sub.route.nunique()<40 or sub.route_year_id.nunique()<75:
        return {"status":"insufficient_same_observer_multi_round_source",
            "routes":int(sub.route.nunique()),"groups":int(sub.route_year_id.nunique())}
    try:ds=design(sub)
    except ValueError as e:
        return {"status":"design_not_identifiable_in_same_observer_source","reason":str(e)}
    return {"status":"descriptive_only_not_independent_replication",
            "routes":ds["G"],"route_year_groups":ds["H"],"source_nights":ds["N"],
            "models":{key:fit(ds,key,seed=SEED+90+i)
                      for i,key in enumerate(("alpha_any","alpha_strong"))}}

def synthetic():
    rng=np.random.default_rng(2602024)
    rows=[]
    for rt in range(100):
        for year in (2010,2011,2012):
            group=f"s{rt%20}|r{rt}|{year}"
            for rd in (1,2,3,4):
                temp=float(rng.normal(0,1))
                noise=float(rng.normal(0,1))
                shift=float(rt%17)/40+float(year-2010)/7
                val=.20+(.065*(rd==2)+.14*(rd==3)+.19*(rd==4))+.16*temp-.07*noise+shift+float(rng.normal(0,.02))
                rows.append({"route":f"s{rt%20}:r{rt}","state":f"s{rt%20}",
                             "route_year_id":group,"round":rd,"year":year,"rid":group+"|"+str(rd),
                             "doy":float(70+rd*40+rng.uniform(-5,5)),
                             "observer":f"o{rt}",
                             "tempdiff_PEMminus_other_C":temp,
                             "noisediff_PEMminus_other":noise,
                             "alpha_any":val,"activation_any":.4*val,
                             "additional_taxa_any":.6*val})
    d=pd.DataFrame(rows)
    q=design(d)
    actual=fit(q,"alpha_any",full_tests=True,seed=SEED)
    b=actual["coefficients"]
    if abs(b["round4"]-.19)>.015 or abs(b["round2"]-.065)>.015:
        raise AssertionError("Known source-free categorical season effects not recovered")
    if actual["three_df_categorical_round_omnibus"]["route_Wald_F_two_sided_P"]>.001:
        raise AssertionError("Known strong synthetic seasonal acoustic effect not detected")
    act=fit(q,"activation_any",full_tests=False)
    ex=fit(q,"additional_taxa_any",full_tests=False)
    if not all(abs(b[k]-act["coefficients"][k]-ex["coefficients"][k])<1e-10
               for k in PREDICTORS):
        raise AssertionError("Acoustic richness seasonal coefficient not exactly decomposed")
    return {"status":"PASS",
            "known_round4_vs1":.19,"recovered_round4_vs1":b["round4"],
            "route_year_frozen_geography_FE":True,
            "categorical_3_df_and_route_score_signflip":True,
            "all_5_coefficients_alpha_activation_additional_identity":True,
            "synthetic_monitoring_routes":100,
            "no_real_NAAMP_outcomes_used_in_QA":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,default=ROOT/"build/naamp_vegetation_withinyear_hierarchy")
    p.add_argument("--synthetic-only",action="store_true")
    a=p.parse_args()
    qa=synthetic()
    if a.synthetic_only:
        print(json.dumps(qa,sort_keys=True));return
    good,ci,rare,scope=source()
    df,sampling=build_rounds(good,ci,rare)
    ds=design(df)
    scores={name:fit(ds,name,seed=SEED+i) for i,name in enumerate(OUTCOMES)}
    verdict=BH(scores)
    anatomy={}
    for mode,_ in MODES:
        activation=fit(ds,"activation_"+mode,full_tests=False)
        additional=fit(ds,"additional_taxa_"+mode,full_tests=False)
        alpha=scores["alpha_"+mode]
        diff={}
        for k in PREDICTORS:
            target=alpha["coefficients"][k]
            act=activation["coefficients"][k]
            extra=additional["coefficients"][k]
            if abs(target-act-extra)>1e-10:
                raise RuntimeError("Seasonal PEM enrichment did not decompose exact acoustic taxon counts")
            diff[k]={"observed_alpha_beta":target,"acoustic_activation_beta":act,
                    "additional_taxa_beyond_first_beta":extra,
                    "absolute_roundoff":abs(target-act-extra)}
        anatomy[mode]={
            "source_acoustic_taxon_count_identity_test":"PASS",
            "round_specific_components_without_new_inference_P":diff,
            "activation_route_CI95_by_round":{k:activation["round_nuisance_CI95"][k]["CI95_route"]
                    for k in ("round2","round3","round4")},
            "additional_taxa_route_CI95_by_round":{k:additional["round_nuisance_CI95"][k]["CI95_route"]
                    for k in ("round2","round3","round4")}}
    linear={}
    dl=design(df,linear=True)
    for key in OUTCOMES:
        lin=fit(dl,key,full_tests=False)
        linear[key]={"slope_per_additional_survey_round":lin["coefficients"]["round_continuous"],
                     "route_CI95":lin["round_nuisance_CI95"]["round_continuous"]["CI95_route"],
                     "description":"Secondary directional summary only; categorical three-degree test is primary"}
    result={
        "analysis":"NAAMP_wetland_vegetation_withinyear_acoustic_metacommunity_round_hierarchy",
        "status":"original_NAAMP_NWI_repeated_same_route_year_stops_phenological_ecology_completed",
        "date":"2026-10-23",
        "source_pre_frozen_research_spec":SPEC,
        "post_hoc_same_archive_prior_alpha_gamma_known":True,
        "source_coverage":scope,"ecological_same_route_year_geography":sampling,
        "scientific_design":{"physical_route_year_round_FE":True,
            "four_outcomes_BH_family":list(OUTCOMES),
            "independent_physical_route_cluster":True,
            "n_weighted_routes":ds["G"],
            "route_year_fixed_effect_groups":ds["H"],
            "same_physical_site_10stops_all_rounds":True,
            "within_wetland_PEM_vs_other_only":True,
            "survey_round_comparison_route_year_support":ds["n_route_per_round_pair"]},
        "synthetic_QA":qa,
        "primary_and_secondary_categorical_round_effects":scores,
        "joint_predeclared_classification":verdict,
        "acoustic_activation_vs_additional_taxa_exact_hierarchy":anatomy,
        "secondary_linear_survey_round_direction":linear,
        "unadjusted_by_survey_round":diagnostics(df),
        "same_ObserverTrackingID_same_route_year_sensitivity":same_observer(df),
        "scientific_limits":{
             "plant_category_is_static_NWI_polygons_not_live_2001_2015_vegetation":True,
             "survey_round_not_uniform_calendar_phenology":True,
             "correlated_same_route_year_records_not_independent":True,
             "no_frog_frog_direct_interaction_measured":True,
             "taxon_calling_not_occupancy_or_survival":True,
             "no_intervention_on_plants_or_predatory_insects":True,
             "not_a_forecast_or_prediction":True,
             "frozen_main_RC6_manuscript_SI_unchanged":True}}
    a.outdir.mkdir(parents=True,exist_ok=True)
    (a.outdir/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("NAAMP_PEM_SEASONAL_HIERARCHY_BEGIN",flush=True)
    print(json.dumps({
       "status":result["status"],"source":scope,"sample":sampling,
       "classification":verdict,
       "geometry":result["scientific_design"],
       "results":{k:{i:v for i,v in score.items()
                      if i in ("coefficients","round_nuisance_CI95","three_df_categorical_round_omnibus",
                               "route_multiround_FWL_signflip","BH_q_four_omnibus","leave_one_State_out")}
                  for k,score in scores.items()},
       "acoustic_components":anatomy,
       "linear_round_sensitivity":linear,
       "unadjusted_by_round":result["unadjusted_by_survey_round"],
       "same_observer":result["same_ObserverTrackingID_same_route_year_sensitivity"]},
       sort_keys=True,allow_nan=False),flush=True)
    print("NAAMP_PEM_SEASONAL_HIERARCHY_END",flush=True)

if __name__=="__main__":
    main()
