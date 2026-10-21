#!/usr/bin/env python3
"""Retrospective robustness of two selected post-hoc NWI-PEM moderated frog-pair motifs.

This deliberately does NOT claim independent replication, contemporaneous aquatic
macrophytes, or causal biotic interaction. The NWI species weights are trained
on both eras and used unchanged. Only the two prior BH candidates are tested.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[1]
SEED=2840297
B=199
BURN=40
THIN=8
Z=1.959963984540054
PAIRS=[
    ("Gastrophryne carolinensis","Hyla chrysoscelis"),
    ("Hyla gratiosa","Lithobates sphenocephalus"),
]
ORIGINAL={
    "Gastrophryne carolinensis || Hyla chrysoscelis":
        {"n_mixed":45,"signed_delta":-0.11277924011592352},
    "Hyla gratiosa || Lithobates sphenocephalus":
        {"n_mixed":34,"signed_delta":0.10746854017989109}
}

def importfile(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

pairmod=importfile("frozen_pair_source",ROOT/"exploration/run_naamp_plant_conditioned_pair_network_v0_1.py")
prior=pairmod.prior

def synthetic_checks():
    original=[{0,2,4},{1,2,5},{3,4,5},{0,6,7}]
    shape=prior.fixed_margins(original)
    arr=np.zeros((4,10),float)
    for i,row in enumerate(original):arr[i,list(row)]=1.
    mask=np.array([1,1,1,0,0,0,0,1,0,0],bool)
    pair=list(PAIRS[0])
    assert len(pair)==2
    j1=float(np.mean(arr[0,mask]*arr[1,mask]))
    j0=float(np.mean(arr[0,~mask]*arr[1,~mask]))
    assert 0<=j1<=1 and 0<=j0<=1
    state=[set(x) for x in original]
    rng=random.Random(2840299)
    values=[]
    for n in range(400):
        prior.weighted_trade(state,np.zeros((4,10)),rng)
        assert prior.fixed_margins(state)==shape
        if n%3==0:
            x=np.zeros((4,10),float)
            for i,row in enumerate(state):x[i,list(row)]=1.
            values.append(float((x[0,mask]*x[1,mask]).mean()
                                -(x[0,~mask]*x[1,~mask]).mean()))
    assert np.ptp(values)>0.01, "The PEM moderation statistic must be variable"
    return {"status":"PASS","row_col_margins":"PASS",
            "PEM_presence_groups_nonempty":"PASS","moderation_not_invariant":"PASS"}

def years_from_source():
    src=importfile("nwi_frog_year_source",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    raw=src.hist.load_retry()
    runs,_=src.base.build_runs(raw)
    v=dict(zip(runs.RunID.astype(str),runs.SurveyYear.astype(int)))
    return v

def sample_summary(frame):
    if frame.empty:return {"n":0,"routes":0,"states":0}
    return {"n":int(len(frame)),"routes":int(frame.route.nunique()),
            "states":int(frame.State.nunique()),
            "n_null_variable":int(frame.sim_varies.sum()),
            "n_fold_A":int((frame.fold=="A").sum()),
            "n_fold_B":int((frame.fold=="B").sum())}

def route_fit(frame,minimum_n=12,minimum_routes=6):
    if frame.empty:return {"status":"no_data","scope":sample_summary(frame)}
    scope=sample_summary(frame)
    if scope["n"]<minimum_n or scope["routes"]<minimum_routes:
        return {"status":"underpowered","scope":scope,
                "required_n":minimum_n,"required_routes":minimum_routes,
                "mean_delta":float(frame.moderation.mean())}
    fit=sm.OLS(frame.moderation.to_numpy(float),np.ones((len(frame),1))).fit(
        cov_type="cluster",cov_kwds={"groups":frame.route.astype(str)})
    beta=float(fit.params[0]);se=float(fit.bse[0])
    return {"status":"fitted","scope":scope,"beta":beta,
            "route_se":se,"ci95":[beta-Z*se,beta+Z*se],
            "p_two_sided_nominal":float(fit.pvalues[0]),
            "fold_means":{str(f):float(g.moderation.mean())
                          for f,g in frame.groupby("fold")},
            "n_PEM_site_count_quantiles":[float(x)
                for x in frame.PEM_count.quantile([0,.25,.5,.75,1])],
            "n_nonPEM_site_count_quantiles":[float(x)
                for x in frame.nonPEM_count.quantile([0,.25,.5,.75,1])]}

def state_loo(frame,sign):
    outcomes=[]
    for state in sorted(frame.State.astype(str).unique()):
        d=frame[frame.State!=state]
        fit=route_fit(d)
        if fit["status"]=="fitted":
            outcomes.append({"removed_State":state,"beta":fit["beta"],
                             "ci95":fit["ci95"],"p":fit["p_two_sided_nominal"],
                             "n_runs":len(d),"routes":int(d.route.nunique())})
    if not outcomes:return {"status":"insufficient","n_states_checked":0}
    consistent=[x["beta"]*sign>0 for x in outcomes]
    supported=[x["ci95"][0]*sign>0 if sign>0 else x["ci95"][1]*sign>0 for x in outcomes]
    return {"status":"fitted","n_states_checked":len(outcomes),
            "n_point_estimates_original_direction":int(sum(consistent)),
            "n_CI_excludes_zero_original_direction":int(sum(supported)),
            "fraction_original_direction":float(np.mean(consistent)),
            "range_beta":[min(x["beta"] for x in outcomes),max(x["beta"] for x in outcomes)],
            "all":outcomes}

def generate_target_moderation(mode,records,refs,coefs,yearmap):
    ref=refs.copy()
    if ref.RunID.duplicated().any():raise RuntimeError("Reference RunID not unique")
    ref=ref.set_index("RunID")
    eligible=sorted(set(ref.index.astype(str))&set(records))
    expected_n=3659 if mode=="any" else 1766
    if len(eligible)!=expected_n:
        raise RuntimeError(f"Frozen NWI matched-population drift {len(eligible)} != {expected_n}")
    output=defaultdict(list)
    n_original_matrices=0
    n_eligible_PEM_mixed=0
    n_with_target=0
    for rid in eligible:
        obj=records[rid]
        tax,rows=prior.ref_rows(obj,mode)
        if len(tax)<3:raise RuntimeError("Original null has fewer than 3 taxa")
        orig_c=prior.cscore(rows)
        if not np.isclose(orig_c,float(ref.loc[rid,"observed"]),atol=1e-8,rtol=0):
            raise RuntimeError(f"Observed C-score mismatch {rid}")
        n_original_matrices+=1
        frac=np.asarray(obj["v"][:,1],float)/10.
        group=(frac>0)
        n_plants=int(group.sum())
        n_other=10-n_plants
        if n_plants<2 or n_other<2:continue
        n_eligible_PEM_mixed+=1
        index={sp:i for i,sp in enumerate(tax)}
        active=[(p,index[p[0]],index[p[1]]) for p in PAIRS if p[0] in index and p[1] in index]
        if not active:continue
        n_with_target+=1
        coef=coefs[prior.complementary(obj["fold"])]
        theta=np.stack([np.asarray(coef.get(sp,{}).get("wetland_and_emergent",
                                      np.zeros(2)),float) for sp in tax])
        score=theta@obj["v"][:,[0,1]].T
        state=[set(x) for x in rows]
        fixed=prior.fixed_margins(state)
        seed=int.from_bytes(hashlib.sha256(f"{SEED}|{mode}|{rid}".encode()).digest()[:8],"big")
        rng=random.Random(seed)
        feasible=accepted=0
        for _ in range(BURN*len(tax)):
            f,a=prior.weighted_trade(state,score,rng)
            feasible+=f;accepted+=a
        observed=np.zeros((len(tax),10),float)
        for i,stops in enumerate(rows):
            if stops:observed[i,list(stops)]=1.
        vals={pair:[] for pair,_,_ in active}
        for b in range(B):
            for _ in range(THIN*len(tax)):
                f,a=prior.weighted_trade(state,score,rng)
                feasible+=f;accepted+=a
            if b in (0,B//2,B-1) and prior.fixed_margins(state)!=fixed:
                raise RuntimeError("Curveball row/column drift")
            mat=np.zeros((len(tax),10),float)
            for i,stops in enumerate(state):
                if stops:mat[i,list(stops)]=1.
            for pair,i,j in active:
                vals[pair].append(float((mat[i,group]*mat[j,group]).mean()-
                                        (mat[i,~group]*mat[j,~group]).mean()))
        if not feasible or not accepted:
            raise RuntimeError("No exchangeable weighted changes in target pair-survey")
        for pair,i,j in active:
            obs_p=float((observed[i,group]*observed[j,group]).mean())
            obs_n=float((observed[i,~group]*observed[j,~group]).mean())
            null_arr=np.asarray(vals[pair],float)
            effect=(obs_p-obs_n)-float(null_arr.mean())
            output[" || ".join(pair)].append({
                "RunID":rid,"route":str(obj["route"]),"fold":str(obj["fold"]),
                "State":str(obj["state"]),"year":int(yearmap[rid]),
                "PEM_count":n_plants,"nonPEM_count":n_other,
                "PEM_residual":obs_p-float("nan"),  # replaced explicitly below
                "nonPEM_residual":obs_n-float("nan"),
                "moderation":effect,
                "sim_varies":bool(np.ptp(null_arr)>1e-12),
                "n_distinct_draws":int(len(np.unique(np.round(null_arr,10)))),
                "accepted_given_feasible":float(accepted/feasible)
            })
            # Extract group-specific means directly from the exact same chain
            # using the identity: E_P-E_N and the measured observed values.
            # We only need the contrast for this analysis; avoid inaccurate
            # invented decompositions of the component expectations.
            output[" || ".join(pair)][-1].pop("PEM_residual")
            output[" || ".join(pair)][-1].pop("nonPEM_residual")
    frames={key:pd.DataFrame(rows) for key,rows in output.items()}
    return frames,{"matched_original":n_original_matrices,
                   "mixed_PEM_runs":n_eligible_PEM_mixed,
                   "mixed_runs_with_either_candidate_pair":n_with_target,
                   "null_original_Cscore_verified":True}

def eval_pair(frame,name,mode):
    if frame is None or frame.empty:return {"status":"not_observed"}
    earlier=frame[frame.year<=2009]
    later=frame[frame.year>=2010]
    all_fit=route_fit(frame)
    early=route_fit(earlier)
    late=route_fit(later)
    balanced=route_fit(frame[(frame.PEM_count>=3)&(frame.nonPEM_count>=3)],
                      minimum_n=20,minimum_routes=10)
    original=ORIGINAL[name]["signed_delta"]
    direction=1 if original>0 else -1
    loo=state_loo(frame,direction)
    data={"pair":name.split(" || "),"mode":mode,
          "year_split":{
            "early_2001_2009":early,
            "late_2010_2015":late,
            "original_NWI_filter_trained_across_both_epochs":True,
            "historical_year_split_not_independent_validation":True},
          "full":all_fit,"balanced_PEM_3_to_7_stop_partition":balanced,
          "leave_one_state_out":loo,
          "reference_full_PEM_effect":original if mode=="any" else None}
    if mode=="any":
        data["observed_matched_NWI_mixed_runs_QA"]=bool(len(frame)==ORIGINAL[name]["n_mixed"])
        if not data["observed_matched_NWI_mixed_runs_QA"]:
            raise RuntimeError("Original target pair mixed-PEM run sample drift")
        data["same_sign_simulation_QA"]=bool(all_fit["status"]=="fitted" and
             abs(all_fit["beta"]-original)<0.05)
    else:
        data["observed_matched_NWI_mixed_runs_QA"]=None
        data["same_sign_simulation_QA"]=None
    reliable=bool(all_fit["status"]=="fitted" and
             len(frame)>=30 and frame.route.nunique()>=12 and
             int(frame.sim_varies.sum())>=10)
    if not reliable:
        data["classification"]="underpowered"
        return data
    enough=all(z["status"]=="fitted" for z in (early,late,balanced,loo))
    if not enough:
        data["classification"]="fragile_posthoc_PEM_candidate"
        return data
    historical=all(z["beta"]*direction>0 and
            (z["ci95"][0]>0 if direction>0 else z["ci95"][1]<0)
            for z in (early,late))
    balanced_pos=balanced["beta"]*direction>0 and (
        balanced["ci95"][0]>0 if direction>0 else balanced["ci95"][1]<0)
    loo_pass=loo["fraction_original_direction"]>=.8
    data["classification"]=(
        "stable_noncausal_PEM_context_association"
        if historical and balanced_pos and loo_pass
        else "fragile_posthoc_PEM_candidate")
    data["requirements"]={
        "both_epoch_CI_same_direction":historical,
        "balanced_partition_CI_same_direction":balanced_pos,
        "leave_state_out_ge80pct_original_sign":loo_pass}
    return data

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--source-dir",type=Path)
    cli.add_argument("--outdir",type=Path,default=ROOT/"build"/"naamp_pem_moderator_epoch")
    cli.add_argument("--synthetic-only",action="store_true")
    arg=cli.parse_args()
    qa=synthetic_checks()
    print("PEM_EPOCH_QA",json.dumps(qa),flush=True)
    if arg.synthetic_only:return
    if not arg.source_dir:raise RuntimeError("Missing frozen crossfitted NWI source artifact")
    records,refs,coef,source=pairmod.prior_inputs(arg.source_dir)
    yearmap=years_from_source()
    result={
        "analysis":"naamp_PEM_pair_moderation_epoch_robustness_v0_1",
        "status":"post_selection_retrospective_exploration_not_independent_confirmation",
        "contract":"exploration/NAAMP_PEM_MODERATOR_EPOCH_ROBUSTNESS_CONTRACT_V0_1.md",
        "QA":qa,
        "frozen_NWI_original_route_filter_run":39516056663,
        "NWI_plant_source_run":39450277196,
        "original_candidate_discovery_run":39592028334,
        "method":{"fixed_species_row_sums":True,"fixed_site_richness":True,
                  "curveball_draws":B,"burn_per_taxon":BURN,
                  "thin_per_taxon":THIN,"random_seed":SEED,
                  "PEM_presence_is_mapped_polygon_overlap_not_actual_vegetation":True,
                  "NWI_coefficients_trained_both_eras":True,
                  "two_focal_pairs_selected_after_prior_all_year_analysis":True,
                  "no_new_pair_selection_or_threshold_tuning":True},
        "modes":{}}
    arg.outdir.mkdir(parents=True,exist_ok=True)
    for mode in ("any","strong"):
        frames,scope=generate_target_moderation(mode,records,refs[mode],coef[mode],yearmap)
        result["modes"][mode]={"population":scope,"focal_pairs":{}}
        for pair in PAIRS:
            label=" || ".join(pair)
            frame=frames.get(label)
            if frame is not None:
                frame.to_csv(arg.outdir/f"{mode}_{PAIRS.index(pair)+1}_per_run.csv",index=False)
            result["modes"][mode]["focal_pairs"][label]=eval_pair(frame,label,mode)
            summary=result["modes"][mode]["focal_pairs"][label]
            print("PEM_PAIR_EPOCH_RESULT",mode,label,json.dumps({
                "n_runs":0 if frame is None else len(frame),
                "full":summary.get("full"),
                "early":summary.get("year_split",{}).get("early_2001_2009"),
                "late":summary.get("year_split",{}).get("late_2010_2015"),
                "balanced":summary.get("balanced_PEM_3_to_7_stop_partition"),
                "classification":summary["classification"] if "classification" in summary else summary.get("status")},sort_keys=True),flush=True)
    (arg.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PEM_PAIR_EPOCH_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("PEM_PAIR_EPOCH_RESULT_END",flush=True)

if __name__=="__main__":
    main()
