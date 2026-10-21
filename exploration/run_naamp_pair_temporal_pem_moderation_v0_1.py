#!/usr/bin/env python3
"""Retrospective NAAMP frog-pair year stability and within-run PEM moderation.

All weighted fixed-row/fixed-column nulls reuse the previously frozen
route-crossfit species-wise NWI coefficients. Outcome years are held out for
pair screening, but NOT for the original habitat coefficient estimation; no
chronological independent validation or causal biological edges are claimed.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import random
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
SEED=2840293
B=199
BURN=40
THIN=8
Q=1.959963984540054
EARLY_MAX=2009
FOCAL=[
    ("Hyla versicolor","Lithobates clamitans"),
    ("Lithobates catesbeianus","Lithobates clamitans"),
    ("Anaxyrus fowleri","Lithobates clamitans")
]

def importfile(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(obj)
    return obj

prev=importfile("nwi_pair_temporal_parent",
                ROOT/"exploration/run_naamp_plant_conditioned_pair_network_v0_1.py")
prior=prev.prior
KEYS=("State","RouteNumber","SiteID")

def actual_matrix(rows):
    arr=np.zeros((len(rows),10),dtype=float)
    for i,pos in enumerate(rows):
        if pos:arr[i,list(pos)]=1.
    return arr

def synthetic_test():
    test=[{0,2},{1,3},{0,4,6},{3,7,8},{5,8,9}]
    fixed=prior.fixed_margins(test)
    E=np.asarray([0.,.04,0.1,0.,0.,.02,.12,0.,.03,.10])
    has=E>0
    assert has.sum()==6 and (~has).sum()==4, "PEM synthetic QA group count"
    m1=actual_matrix(test)
    ov=(m1@m1.T)/10-np.outer(m1.mean(axis=1),m1.mean(axis=1))
    assert np.allclose(ov,prev.cov_matrix(test))
    rand=random.Random(SEED)
    visited=set()
    for k in range(400):
        prior.weighted_trade(test,np.zeros((len(test),10)),rand)
        if k%10==0:
            assert prior.fixed_margins(test)==fixed
            A=actual_matrix(test)
            visited.add(round(float(A[0]@A[1]),4))
    assert len(visited)>=2
    assert sorted([min(a,b) for a,b in FOCAL]) and all(a!=b for a,b in FOCAL)
    return {"status":"PASS","fixed_margins":"PASS",
            "PEM_group_consistency":"PASS",
            "pair_covariance_identical_to_prior":"PASS",
            "pairwise_overlap_changes_under_fixed_margins":"PASS"}

def load(authority):
    records,oldrefs,coefs,scope=prev.prior_inputs(authority)
    sourcemod=importfile(
        "vegetation_epoch_source",
        ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    raw=sourcemod.hist.load_retry()
    runs,_=sourcemod.base.build_runs(raw)
    year_map=dict(zip(runs.RunID.astype(str),runs.SurveyYear.astype(int)))
    if any(k not in year_map or not 2001<=year_map[k]<=2015 for k in records):
        raise RuntimeError("Run-year metadata absent or outside frozen 2001–2015")
    return records,oldrefs,coefs,scope,year_map

def fit_cluster(frame,column):
    if frame.empty or len(frame)<20 or frame.route.nunique()<10:
        return {"status":"insufficient","runs":int(len(frame)),
                "routes":int(frame.route.nunique()) if len(frame) else 0}
    X=np.ones((len(frame),1),float)
    fit=sm.OLS(frame[column].astype(float).to_numpy(),X).fit(
        cov_type="cluster",cov_kwds={"groups":frame.route.astype(str)})
    beta=float(fit.params[0])
    se=float(fit.bse[0])
    return {"status":"fitted","delta":beta,"route_se":se,
            "ci95":[beta-Q*se,beta+Q*se],
            "p_two_sided":float(fit.pvalues[0]),
            "runs":int(len(frame)),"routes":int(frame.route.nunique())}

def fold_info(frame,field="delta"):
    return {
      z:{"mean":float(f[field].mean()),"n":int(len(f)),"routes":int(f.route.nunique())}
      for z,f in frame.groupby("fold")
    }

def eligibility(frame,early=False,late=False,mixed=False):
    if early:
        return (len(frame)>=30 and frame.route.nunique()>=12
                and frame.null_varies.sum()>=10
                and all(len(frame[frame.fold==f])>=5 for f in ("A","B")))
    if late:
        return (len(frame)>=40 and frame.route.nunique()>=15
                and frame.null_varies.sum()>=10
                and all(len(frame[frame.fold==f])>=5 for f in ("A","B")))
    if mixed:
        return (len(frame)>=30 and frame.route.nunique()>=12
                and frame.moderation_null_varies.sum()>=10
                and all(len(frame[frame.fold==f])>=5 for f in ("A","B")))
    raise ValueError("Eligibility mode missing")

def summary_mode(mode,records,reference,coefficients,year_map,outdir):
    ref=reference.copy()
    if ref.RunID.duplicated().any():raise RuntimeError("Duplicate frozen reference RunID")
    ref=ref.set_index("RunID")
    ids=sorted(set(records)&set(ref.index.astype(str)))
    if (mode=="any" and len(ids)!=3659) or (mode=="strong" and len(ids)!=1766):
        raise RuntimeError("Frozen matched sample membership drift "+mode+" "+str(len(ids)))
    by_pair=defaultdict(list)
    run_rows=[]
    for n_run,rid in enumerate(ids,1):
        run=records[rid]
        taxa,rows=prior.ref_rows(run,mode)
        k=len(taxa)
        if k<3 or not prior.exchangeable(rows):
            raise RuntimeError("Frozen NWI run had unexchangeable species matrix")
        c_obs=float(prior.cscore(rows))
        if not np.isclose(c_obs,float(ref.loc[rid,"observed"]),atol=1e-8,rtol=0):
            raise RuntimeError("Frozen observed C-score did not match "+rid)
        observed=actual_matrix(rows)
        theta=np.stack([
            np.asarray(coefficients[prior.complementary(run["fold"])].get(sp,{})
                       .get("wetland_and_emergent",np.zeros(2)),dtype=float)
            for sp in taxa])
        if theta.shape!=(k,2):raise RuntimeError("Frozen coefficient dimensions drift")
        score=theta@run["v"][:,[0,1]].T
        trial=[set(x) for x in rows]
        fixed=prior.fixed_margins(trial)
        rng=random.Random(int.from_bytes(hashlib.sha256(
            f"{SEED}|{mode}|{rid}".encode()).digest()[:8],"big"))
        feasible=accepted=0
        for i in range(BURN*k):
            f,a=prior.weighted_trade(trial,score,rng)
            feasible+=f; accepted+=a
        pem=run["v"][:,1].astype(float)/10.
        plant=pem>0
        mixed=bool(plant.sum()>=2 and (~plant).sum()>=2)
        cov_obs=prev.cov_matrix(rows)
        joint_obs_pem=(observed[:,plant]@observed[:,plant].T)/plant.sum() if mixed else None
        joint_obs_other=(observed[:,~plant]@observed[:,~plant].T)/(~plant).sum() if mixed else None
        sum_cov=np.zeros((k,k),dtype=float)
        sum_cov_sq=np.zeros((k,k),dtype=float)
        sum_pem=np.zeros((k,k),dtype=float)
        sum_other=np.zeros((k,k),dtype=float)
        sum_contrast=np.zeros((k,k),dtype=float)
        sum_contrast_sq=np.zeros((k,k),dtype=float)
        for step in range(B):
            for i in range(THIN*k):
                f,a=prior.weighted_trade(trial,score,rng)
                feasible+=f; accepted+=a
            mat=actual_matrix(trial)
            cov=(mat@mat.T)/10-np.outer(mat.mean(axis=1),mat.mean(axis=1))
            sum_cov+=cov
            sum_cov_sq+=cov**2
            if mixed:
                p=(mat[:,plant]@mat[:,plant].T)/plant.sum()
                o=(mat[:,~plant]@mat[:,~plant].T)/(~plant).sum()
                sum_pem+=p;sum_other+=o
                diff=p-o
                sum_contrast+=diff
                sum_contrast_sq+=diff**2
            if step in (0,B//2,B-1) and prior.fixed_margins(trial)!=fixed:
                raise RuntimeError("Weighted Curveball row/column margin drift")
        if feasible==0 or accepted==0:
            raise RuntimeError("No weighted trade accepted in exchangeable run "+rid)
        expect=sum_cov/B
        variance=np.maximum(sum_cov_sq/B-expect**2,0.)
        if mixed:
            expected_pem=sum_pem/B
            expected_other=sum_other/B
            exp_diff=sum_contrast/B
            var_diff=np.maximum(sum_contrast_sq/B-exp_diff**2,0.)
        for i,sp in enumerate(taxa):
            if not prev.is_resolved(sp):continue
            for j in range(i+1,k):
                partner=taxa[j]
                if not prev.is_resolved(partner):continue
                name=sp+" || "+partner
                row={"route":run["route"],"fold":run["fold"],
                     "RunID":rid,"SurveyYear":year_map[rid],
                     "early":year_map[rid]<=EARLY_MAX,
                     "delta":float(cov_obs[i,j]-expect[i,j]),
                     "null_varies":bool(variance[i,j]>1e-14),
                     "n_PEM_sites":int(plant.sum()),
                     "moderation_eligible":mixed}
                if mixed:
                    row["pem_delta"]=float(joint_obs_pem[i,j]-expected_pem[i,j])
                    row["nonpem_delta"]=float(joint_obs_other[i,j]-expected_other[i,j])
                    row["contrast"]=row["pem_delta"]-row["nonpem_delta"]
                    row["moderation_null_varies"]=bool(var_diff[i,j]>1e-14)
                else:
                    row.update(pem_delta=np.nan,nonpem_delta=np.nan,contrast=np.nan,moderation_null_varies=False)
                by_pair[name].append(row)
        run_rows.append({"RunID":rid,"route":run["route"],"SurveyYear":year_map[rid],
                         "n_taxa":k,"n_PEM_sites":int(plant.sum()),"mixed_PEM":mixed,
                         "accepted_given_feasible":accepted/feasible})
        if n_run%550==0:
            print(f"{mode} {n_run}/{len(ids)} weighted pair matrices and PEM strata completed",flush=True)
    runframe=pd.DataFrame(run_rows)
    data={}
    early_candidates=[]
    for pair,rs in sorted(by_pair.items()):
        df=pd.DataFrame(rs)
        a=df[df.early]
        b=df[~df.early]
        m=df[df.moderation_eligible]
        item={"pair":pair.split(" || "),"joint_runs":len(df),
              "early_runs":len(a),"late_runs":len(b),
              "early_routes":int(a.route.nunique()) if len(a) else 0,
              "late_routes":int(b.route.nunique()) if len(b) else 0,
              "n_runs_PEM_mixed":len(m),"PEM_mixed_routes":int(m.route.nunique()) if len(m) else 0}
        if eligibility(a,early=True):
            fit=fit_cluster(a,"delta")
            item["early"]={"fit":fit,"folds":fold_info(a)}
            early_candidates.append((pair,item))
        else:item["early"]={"status":"not_eligible"}
        if eligibility(b,late=True):
            item["late"]={"fit":fit_cluster(b,"delta"),"folds":fold_info(b)}
        else:item["late"]={"status":"not_eligible"}
        if eligibility(m,mixed=True):
            item["PEM_moderation"]={
                "fit":fit_cluster(m,"contrast"),
                "folds":fold_info(m,"contrast"),
                "mean_PEM_signed_residual":float(m.pem_delta.mean()),
                "mean_nonPEM_signed_residual":float(m.nonpem_delta.mean())}
        else:item["PEM_moderation"]={"status":"not_eligible"}
        data[pair]=item

    # Selection is early-only, with FDR across all eligible early-discovery pairs.
    early_selected=[]
    if early_candidates:
        qs=multipletests([row["early"]["fit"]["p_two_sided"] for _,row in early_candidates],method="fdr_bh")[1]
        for (name,item),q in zip(early_candidates,qs):
            e=item["early"]
            e["BH_q"]=float(q)
            beta=e["fit"]["delta"]
            signs=e["folds"]
            consistent=bool("A" in signs and "B" in signs and signs["A"]["mean"]*signs["B"]["mean"]>0
                            and signs["A"]["mean"]*beta>0)
            ci=e["fit"]["ci95"]
            e["discovery"]=bool(q<.05 and (ci[0]>0 or ci[1]<0) and consistent)
            if e["discovery"]:early_selected.append(name)
    # Later-year inference is evaluated only on eligible early discoveries;
    # FDR over the WHOLE eligible follow-up list, never over significant late results alone.
    late_eligible=[name for name in early_selected if "fit" in data[name]["late"]]
    if late_eligible:
        qlate=multipletests([data[name]["late"]["fit"]["p_two_sided"] for name in late_eligible],method="fdr_bh")[1]
        for name,q in zip(late_eligible,qlate):
            item=data[name]
            e=item["early"];l=item["late"]
            l["BH_q_among_early_discoveries"]=float(q)
            same=bool(l["fit"]["delta"]*e["fit"]["delta"]>0)
            ci=l["fit"]["ci95"]
            fold=l["folds"]
            l["temporal_persistence_pass"]=bool(same and q<.05 and (ci[0]>0 or ci[1]<0)
                and "A" in fold and "B" in fold
                and fold["A"]["mean"]*e["fit"]["delta"]>0
                and fold["B"]["mean"]*e["fit"]["delta"]>0)

    moderation_eligible=[name for name,item in data.items() if "fit" in item["PEM_moderation"]]
    if moderation_eligible:
        qs=multipletests([data[name]["PEM_moderation"]["fit"]["p_two_sided"]
                        for name in moderation_eligible],method="fdr_bh")[1]
        for name,q in zip(moderation_eligible,qs):
            m=data[name]["PEM_moderation"]
            m["BH_q"]=float(q)
            ci=m["fit"]["ci95"]
            fold=m["folds"]
            m["PEM_context_candidate"]=bool(q<.05 and (ci[0]>0 or ci[1]<0)
                and "A" in fold and "B" in fold
                and fold["A"]["mean"]*m["fit"]["delta"]>0
                and fold["B"]["mean"]*m["fit"]["delta"]>0)
    discovered=[name for name in early_selected]
    persistent=[name for name in late_eligible if data[name]["late"]["temporal_persistence_pass"]]
    moderation_found=[name for name in moderation_eligible if data[name]["PEM_moderation"]["PEM_context_candidate"]]
    def fixed_focus(item):
        return {"pair":item,"result":data.get(" || ".join(sorted(item)),
                    {"status":"not_present"})}
    focal=[fixed_focus(pair) for pair in FOCAL]
    concise={
        "mode":mode,
        "sample":{"n_runs":len(runframe),"routes":int(runframe.route.nunique()),
                  "early_runs":int((runframe.SurveyYear<=EARLY_MAX).sum()),
                  "late_runs":int((runframe.SurveyYear>EARLY_MAX).sum()),
                  "PEM_mixed_runs":int(runframe.mixed_PEM.sum()),
                  "PEM_mixed_routes":int(runframe.loc[runframe.mixed_PEM,"route"].nunique()),
                  "mean_feasible_trade_acceptance":float(runframe.accepted_given_feasible.mean())},
        "temporal":{
            "eligible_early_pairs":len(early_candidates),
            "early_BH_discovered_count":len(discovered),
            "late_eligible_early_discoveries":len(late_eligible),
            "late_BH_persistent_count":len(persistent),
            "early_BH_discovered_pairs":[{"pair":name,"delta":data[name]["early"]["fit"]["delta"],
                 "early_q":data[name]["early"]["BH_q"]} for name in discovered],
            "late_BH_persistent_pairs":[{"pair":name,
                 "early_delta":data[name]["early"]["fit"]["delta"],
                 "late_delta":data[name]["late"]["fit"]["delta"],
                 "late_q":data[name]["late"]["BH_q_among_early_discoveries"]}
                 for name in persistent],
            "NWI_filter_training_includes_later_years":True,
            "independent_chronological_validation_claim":False},
        "PEM_context":{
            "eligible_pair_moderation_tests":len(moderation_eligible),
            "BH_supported_count":len(moderation_found),
            "BH_supported":[{"pair":name,"PEM_minus_nonPEM_delta":data[name]["PEM_moderation"]["fit"]["delta"],
                 "ci95":data[name]["PEM_moderation"]["fit"]["ci95"],
                 "q":data[name]["PEM_moderation"]["BH_q"]} for name in moderation_found],
            "mapped_PEM_overlap_is_not_actual_plant_absence":True,
            "causal_plant_mediation_identified":False},
        "focal_pairs":focal,
        "all_pairs":data}
    outdir.mkdir(parents=True,exist_ok=True)
    runframe.to_csv(outdir/f"{mode}_matrix_year_PEM_QA.csv",index=False)
    print("MODE_COMPLETE",mode,json.dumps({"run_count":len(runframe),
            "early_discoveries":len(discovered),"late_persistent":len(persistent),
            "PEM_context_supported":len(moderation_found),
            "focal":[{"pair":z["pair"],"early":z["result"].get("early"),"late":z["result"].get("late"),
                     "PEM":z["result"].get("PEM_moderation")} for z in focal]}),flush=True)
    return concise

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-inputs",type=Path)
    p.add_argument("--synthetic-only",action="store_true")
    p.add_argument("--outdir",type=Path,default=ROOT/"build"/"naamp_frog_pair_time_PEM")
    args=p.parse_args()
    qa=synthetic_test()
    print("TEMPORAL_PEM_PAIR_SYNTHETIC_QA",json.dumps(qa),flush=True)
    if args.synthetic_only:return
    if not args.frozen_inputs:raise RuntimeError("Missing fixed NWI null artifact")
    records,refs,coefs,source,years=load(args.frozen_inputs)
    result={"analysis":"naamp_NWI_pair_temporal_PEM_moderation_v0_1",
            "contract":"exploration/NAAMP_FROG_PAIR_TEMPORAL_PEM_MODERATION_CONTRACT_2026_10_21.md",
            "status":"posthoc_temporal_split_and_within_route_PEM_heterogeneity_no_causal_interaction",
            "source_weighted_NWI_coefficients_workflow":39516056663,
            "source_previous_pair_network_workflow":39528330890,
            "source_NWI_geography_workflow":39450277196,
            "QA":qa,
            "settings":{"seed":SEED,"MCMC_draws":B,"burn_per_taxon":BURN,
                        "thin_per_taxon":THIN,
                        "fixed_taxon_stop_counts":True,"fixed_stop_richness":True,
                        "early_years":"2001-2009","late_years":"2010-2015",
                        "NWI_coefficient_training_across_both_epochs":True},
            "source_coverage":source,
            "modes":{},
            "inference_boundaries":{
                "PEM_polygon_overlap_does_not_equal_true_plant_presence":True,
                "temporal_year_split_is_not_independent_model_training":True,
                "no_direct_predator_fish_or_invertebrate_records":True,
                "causal_pair_interactions_established":False,
                "RC6_manuscript_modified":False}}
    for mode in ("any","strong"):
        result["modes"][mode]=summary_mode(mode,records,refs[mode],coefs[mode],years,args.outdir)
    (args.outdir/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("PAIR_YEAR_PEM_RESULT_BEGIN")
    brief={k:v for k,v in result.items() if k!="modes"}
    brief["modes"]={}
    for mode in result["modes"]:
        v=result["modes"][mode]
        brief["modes"][mode]={k:value for k,value in v.items() if k!="all_pairs"}
    print(json.dumps(brief,ensure_ascii=False,sort_keys=True))
    print("PAIR_YEAR_PEM_RESULT_END",flush=True)

if __name__=="__main__":
    main()
