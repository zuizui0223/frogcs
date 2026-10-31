"""Post-hoc acoustic-R²-calibrated direction-only POM for three frogcs catalogs.

Every scenario receives only *one* noise scale fitted to observed site-level
8-term rank-OLS R².  Calibration is outcome-informed through R² alone, never
through OS/OV/DeltaS/DeltaV/low-S signs.  Separate calibration and evaluation
Gaussian fields. No biological acoustic observation model or ABC posterior.

rank_signal: rank(F_B) + noise.  This cannot recover differences in effect
magnitudes lost when ranking.  log_signal: log(F_B) + noise then rank.
Per-scenario R² tuning can still cancel global signal amplitude scaling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from select_macro_trophic_scenarios import ROOT, SITE, VISITS, SEED, LEVELS, load_cohort
from pattern_oriented_abc_pilot import (
    BACKGROUNDS, get_design, bootstrap_observed, stats_from_y,
    site_response, group_exact_surfaces,
)
from directional_context_modulation_pom import (
    METRICS, joint_observed_bootstrap, contrast_point, selected_observed_signs,
)
from directional_pom_132 import observational_categories
from pattern_oriented_archive132 import FILES, DESIGN, archived_full_catalog

OUT=ROOT/"research/results/macro_r2_matched_directional_20261031"
PROCESS=ROOT/"research/results/macro_pom_process_prior_20261031"
DANGER=ROOT/"research/results/macro_s_facilitated_danger_20261031"
MODES=("rank_signal","log_signal")
NOISE_TYPES=("iid","spatial_block_025")
N_CAL=16
N_EVAL=128
STEPS=18
MAX_REL_NOISE=32.
R2_ABS_TOL=.002
SIGN_CONF=.90
TERNARY_FLOOR=.05
PENALTY=.25
FAMILIES=("frozen132","realrate192","facilitation72")
FIVE=METRICS+("O_with_S_low",)


def orthogonal_regression(design):
    x=np.asarray(design["x"],dtype=float)
    q,r=np.linalg.qr(x,mode="reduced")
    if x.shape[1]!=8 or q.shape[1]!=8 or np.linalg.matrix_rank(r)!=8:
        raise ValueError("Full-rank eight-term rank-regression design required")
    if np.abs(np.dot(q[:,0],np.ones(len(x)))/np.sqrt(len(x)))<.999999:
        raise AssertionError("First orthogonal column must be intercept")
    return q[:,1:],design["pinv"]


def rankrows(matrix):
    """Original global ranks per row, with tie handling at noise sigma=0."""
    a=np.asarray(matrix,dtype=float)
    if a.ndim!=2 or not np.isfinite(a).all():
        raise ValueError("Expect finite (draw,site) matrix")
    ranks=rankdata(a,axis=1)
    ranks-=ranks.mean(axis=1,keepdims=True)
    sd=ranks.std(axis=1,keepdims=True)
    if np.any(sd<1e-12):
        raise ValueError("Constant simulated cohort rank cannot predict patterns")
    return ranks/sd


def site_rank_r2(ranked_y,q):
    y=np.asarray(ranked_y,dtype=float)
    if y.ndim!=2 or q.shape[0]!=y.shape[1]:
        raise ValueError("R2 shape mismatch")
    proj=y@q
    var=np.sum((y-y.mean(axis=1,keepdims=True))**2,axis=1)
    if np.any(var<=0):raise ValueError("Zero response variance")
    r2=np.sum(proj*proj,axis=1)/var
    if np.any((r2<-1e-8)|(r2>1+1e-8)):
        raise AssertionError("Invalid rank R²")
    return np.clip(r2,0,1)


def signal_at_sites(d,background,grid,mode):
    if mode not in MODES:raise ValueError("Unexpected observation mode")
    original=site_response(d,background,grid,warps=(1.,1.))
    if not np.isfinite(original).all() or np.any(original<=0):
        raise ValueError("Invalid source response")
    if mode=="rank_signal":
        signal=rankrows(original[None,:])[0]
    else:
        signal=np.log(original)
    if signal.std()<1e-12:
        raise ValueError("Unidentifiable source variation")
    return signal


def common_noise(d,n,seed,noise_type):
    """Independent standard Gaussian fields; optionally a shared block term."""
    if noise_type not in NOISE_TYPES:raise ValueError(noise_type)
    rng=np.random.default_rng(seed)
    noise=rng.normal(size=(n,len(d)))
    if noise_type=="spatial_block_025":
        blocks,_=pd.factorize(d.spatial_block,sort=True)
        effects=rng.normal(size=(n,int(blocks.max()+1)))
        noise+=.25*effects[:,blocks]
    noise-=noise.mean(axis=1,keepdims=True)
    noise/=noise.std(axis=1,keepdims=True)
    if not np.isfinite(noise).all():raise AssertionError("Bad noise")
    return noise


def noisy_rank_r2(signal,relative_sigma,innovations,q):
    sig=float(signal.std()*relative_sigma)
    response=rankrows(signal[None,:]+sig*innovations)
    return site_rank_r2(response,q)


def calibrate_r2(signal,target,cal_noise,q,steps=STEPS,tol=R2_ABS_TOL):
    """No category outcomes are consulted here. Single scale per scenario."""
    if not 0<target<1:raise ValueError("Observed rank R² must lie strictly within (0,1)")
    baseline=float(noisy_rank_r2(signal,0.,cal_noise[:1],q).mean())
    if baseline<target-tol:
        return dict(relative_sigma=0.,sigma=0.,original_r2=baseline,
                    calibrated_mean_r2=baseline,r2_abs_error=abs(baseline-target),
                    calibration_status="NOISE_ONLY_R2_UNREACHABLE")
    if abs(baseline-target)<=tol:
        return dict(relative_sigma=0.,sigma=0.,original_r2=baseline,
                    calibrated_mean_r2=baseline,r2_abs_error=abs(baseline-target),
                    calibration_status="MATCHED_WITHOUT_NOISE")
    high=float(noisy_rank_r2(signal,MAX_REL_NOISE,cal_noise,q).mean())
    if high>target+tol:
        return dict(relative_sigma=MAX_REL_NOISE,
                    sigma=float(MAX_REL_NOISE*signal.std()),original_r2=baseline,
                    calibrated_mean_r2=high,r2_abs_error=abs(high-target),
                    calibration_status="NOISE_R2_NOT_BRACKETED")
    lo,hi=0.,MAX_REL_NOISE
    closest=(abs(baseline-target),0.,baseline)
    if abs(high-target)<closest[0]:closest=(abs(high-target),hi,high)
    for _ in range(steps):
        mid=(lo+hi)*.5
        r2=float(noisy_rank_r2(signal,mid,cal_noise,q).mean())
        if abs(r2-target)<closest[0]:closest=(abs(r2-target),mid,r2)
        if r2>target:lo=mid
        else:hi=mid
    err,scale,achieved=closest
    return dict(relative_sigma=float(scale),sigma=float(scale*signal.std()),
                original_r2=baseline,calibrated_mean_r2=float(achieved),
                r2_abs_error=float(err),
                calibration_status=("MATCHED_R2" if err<=tol else "APPROXIMATE_R2_UNMATCHED"))


def correlation_batch(o,y,mask):
    """Pearson correlations on globally ranked O and Y, vectorized by draw."""
    x=np.asarray(o[mask],float)
    sub=np.asarray(y[:,mask],float)
    cx=x-x.mean()
    cy=sub-sub.mean(axis=1,keepdims=True)
    denom=np.sqrt(np.dot(cx,cx)*np.sum(cy*cy,axis=1))
    if np.any(denom<=1e-10):raise ValueError("Degenerate stratum correlation")
    return (cy@cx)/denom


def five_pattern_matrix(ranked,design,pinv):
    """Exact four signed estimands plus low-S correlation for every simulated draw."""
    y=np.asarray(ranked,float)
    coef=y@pinv.T
    masks=design["masks"]
    o=design["o"]
    c={key:correlation_batch(o,y,masks[key])
       for key in ("S_low","S_high","V_zero","V_positive")}
    all_rows=np.column_stack([coef[:,4],coef[:,5],
                              c["S_high"]-c["S_low"],
                              c["V_positive"]-c["V_zero"],
                              c["S_low"]])
    if all_rows.shape!=(len(y),5) or not np.isfinite(all_rows).all():
        raise ValueError("Nonfinite five-point pattern matrix")
    return all_rows


def categories(values,near_zero_width):
    a=np.asarray(values,float)
    if a.ndim!=2 or a.shape[1]!=5 or near_zero_width<=0:
        raise ValueError("Wrong five-state input")
    cat=np.sign(a).astype(np.int8)
    low=a[:,4]
    cat[:,4]=np.where(low<-near_zero_width,-1,
                      np.where(low>near_zero_width,1,0))
    return cat


def category_agreement(obs,sim,selected):
    """Uses JOINT observed bootstrap and JOINT noise draws, never factorized."""
    a=np.asarray(obs,dtype=np.int8)[:,list(selected)]
    b=np.asarray(sim,dtype=np.int8)[:,list(selected)]
    if len(a)<1 or len(b)<1 or np.any(a[:,:-1]==0) or np.any(b[:,:-1]==0):
        raise ValueError("Degenerate direction probability")
    ao,ac=np.unique(a,axis=0,return_counts=True)
    bo,bc=np.unique(b,axis=0,return_counts=True)
    mismatch=(ao[:,None,:]!=bo[None,:,:]).sum(axis=2)
    weights=(ac/ac.sum())[:,None]*(bc/bc.sum())[None,:]
    exact=float(np.sum(weights*(mismatch==0)))
    soft=float(np.sum(weights*(PENALTY**mismatch)))
    return soft,exact


def observed_context(d,bg):
    design=get_design(d,bg)
    q,pinv=orthogonal_regression(design)
    ranks=rankrows(d.strong_rate.to_numpy(float)[None,:])
    observed_r2=float(site_rank_r2(ranks,q)[0])
    current=contrast_point(d.strong_rate,design)
    boot4=joint_observed_bootstrap(d.strong_rate,d,design,n_boot=999,seed=SEED)
    boot6,_,_,_=bootstrap_observed(d.strong_rate,design,d.spatial_block,
                                  n_boot=999,seed=SEED)
    # Both functions draw identical 999 block weights, so their OS/OV entries
    # must replay bit-identically (modulo linear solve roundoff).
    if len(boot4)!=len(boot6) or not np.allclose(boot4[:,:2],boot6[:,:2],rtol=0,atol=1e-9):
        raise AssertionError("Observed bootstrap is not jointly aligned")
    selected,sign,obs_table=selected_observed_signs(current,boot4,confidence=.90)
    _,delta=observational_categories(boot6)
    joint=np.column_stack([boot4,boot6[:,4]])
    state=categories(joint,delta)
    point=np.concatenate([current,[stats_from_y(d.strong_rate,design)[4]]])
    modal=categories(point[None,:],delta)[0]
    if not np.array_equal(np.sign(point[:4]).astype(int),sign):
        raise AssertionError("Inconsistent observed sign benchmark")
    return dict(bg=bg,design=design,q=q,pinv=pinv,target_r2=observed_r2,
                selected=tuple(selected)+(4,),observed_boot5=state,
                modal=modal,delta=delta,point=point,obs_table=obs_table)


def source_families(family):
    if family not in FAMILIES:raise ValueError("Unrecognized source family")
    from directional_process_rate_8 import recover_grid
    if family=="frozen132":
        grids,metadata=archived_full_catalog(
            [pd.read_csv(p) for p in FILES],pd.read_csv(DESIGN))
        source_paths=[DESIGN,*FILES]
        labels={name:dict(case=name,rate_draw=-1,hypothesis="frozen",
                          model_family=family) for name in grids}
    elif family=="realrate192":
        source_paths=[PROCESS/"real_simulator_F_B_cells.csv.gz",
                      PROCESS/"process_prior_predictive_patterns.csv",
                      PROCESS/"receipt.json"]
        for path in source_paths:
            if not path.is_file():raise FileNotFoundError(str(path))
        receipt=json.loads(source_paths[-1].read_text())
        if not receipt.get("model_original_replayed") or receipt.get("n_draws")!=8:
            raise AssertionError("Real parameter draw source is not anchored")
        raw=pd.read_csv(source_paths[0])
        grids={};labels={}
        for (draw,case),group in raw.groupby(["draw","case"]):
            key=f"d{int(draw):02d}_case_{int(case):03d}"
            grids[key]=recover_grid(group)
            labels[key]=dict(case=f"case_{int(case):03d}",rate_draw=int(draw),
                             hypothesis="process_rate",model_family=family)
    else:
        source_paths=[DANGER/"hypothetical_80year_F_B_cells.csv.gz",
                      DANGER/"receipt.json"]
        for path in source_paths:
            if not path.is_file():raise FileNotFoundError(str(path))
        receipt=json.loads(source_paths[-1].read_text())
        if not receipt.get("original_baseline_verified"):
            raise AssertionError("Facilitation source lacks original model replay")
        raw=pd.read_csv(source_paths[0])
        grids={};labels={}
        for (hypothesis,case),group in raw.groupby(["hypothesis","case"]):
            key=f"{hypothesis}_case_{int(case):03d}"
            grids[key]=recover_grid(group)
            labels[key]=dict(case=f"case_{int(case):03d}",rate_draw=-1,
                             hypothesis=str(hypothesis),model_family=family)
    expected={"frozen132":132,"realrate192":192,"facilitation72":72}[family]
    if len(grids)!=expected or len(labels)!=expected:
        raise AssertionError("Source model catalog incomplete "+family)
    label_groups,_=group_exact_surfaces(grids)
    canonical={}
    for case,label in label_groups.items():
        canonical.setdefault(label,[]).append(case)
    if sum(map(len,canonical.values()))!=expected:
        raise AssertionError("Alias grouping omitted source labels")
    return grids,labels,label_groups,canonical,source_paths


def evaluate_family(family,noise_type="iid",cal_reps=N_CAL,eval_reps=N_EVAL,
                    out_dir=OUT):
    if family not in FAMILIES or noise_type not in NOISE_TYPES:
        raise ValueError("Invalid family/noise setting")
    if cal_reps<4 or eval_reps<8:raise ValueError("Too few noise replicates")
    out_dir.mkdir(parents=True,exist_ok=True)
    d=load_cohort(pd.read_csv(SITE),pd.read_csv(VISITS),expected=4248)
    if int(d.n.sum())!=63180 or int(d.V.sum())!=506:
        raise AssertionError("Original site/cohort counts changed")
    grids,labels,group_of,groups,inputs=source_families(family)
    rows=[];calibration=[];observed=[];group_rows=[]
    for bg in BACKGROUNDS:
        context=observed_context(d,bg)
        q=context["q"];design=context["design"]
        offset=(0 if bg=="uniform" else 10000)+(0 if noise_type=="iid" else 40000)
        cal_noise=common_noise(d,cal_reps,seed=SEED+711+offset,noise_type=noise_type)
        eval_noise=common_noise(d,eval_reps,seed=SEED+2711+offset,noise_type=noise_type)
        obs_state=context["observed_boot5"]
        for i,name in enumerate(FIVE):
            if i<4:
                vals=np.mean(obs_state[:,i]==-1)
                low,high=np.quantile(joint_observed_bootstrap(
                    d.strong_rate,d,design,n_boot=999,seed=SEED)[:,i],[.025,.975])
            else:
                vals=np.mean(obs_state[:,4]==0)
                bs=bootstrap_observed(d.strong_rate,design,d.spatial_block,n_boot=999,seed=SEED)[0][:,4]
                low,high=np.quantile(bs,[.025,.975])
            observed.append(dict(family=family,noise_type=noise_type,
                                 background=bg,pattern=name,observed_value=context["point"][i],
                                 observed_bootstrap_low=float(low),observed_bootstrap_high=float(high),
                                 observed_negative_or_nearzero_frequency=float(vals),
                                 selected=bool(i in context["selected"]),
                                 r2_observed=context["target_r2"],
                                 lowS_zero_band=context["delta"] if i==4 else np.nan))
        for mode in MODES:
            for number,(canonical,aliases) in enumerate(sorted(groups.items())):
                source=grids[aliases[0]]
                signal=signal_at_sites(d,bg,source,mode)
                fitted=calibrate_r2(signal,context["target_r2"],cal_noise,q)
                perturbed=rankrows(signal[None,:]+fitted["sigma"]*eval_noise)
                eval_r2=site_rank_r2(perturbed,q)
                statistics=five_pattern_matrix(perturbed,design,context["pinv"])
                sim_states=categories(statistics,context["delta"])
                soft,exact=category_agreement(obs_state,sim_states,context["selected"])
                mode_target=context["modal"][list(context["selected"])]
                match=np.all(sim_states[:,list(context["selected"])]==mode_target[None,:],axis=1)
                # Save one row per exact response group; duplicate labels get
                # exactly the same calibrated sigma and noise sequence.
                fit=dict(family=family,noise_type=noise_type,background=bg,mode=mode,
                         source_group=canonical,n_exact_aliases=len(aliases),
                         r2_target=context["target_r2"],
                         r2_evaluation_mean=float(eval_r2.mean()),
                         r2_evaluation_sd=float(eval_r2.std(ddof=1)),
                         **fitted)
                calibration.append(fit)
                item=dict(**fit,soft_joint_agreement=soft,
                          exact_observed_bootstrap_joint_agreement=exact,
                          modal_complete_frequency=float(match.mean()),
                          modal_complete_count=int(match.sum()),eval_reps=eval_reps,
                          q_lowS_near_zero=float(np.mean(sim_states[:,4]==0)),
                          q_lowS_negative=float(np.mean(sim_states[:,4]<0)),
                          q_lowS_positive=float(np.mean(sim_states[:,4]>0)),
                          n_selected=len(context["selected"]),
                          selected_patterns=";".join(FIVE[j] for j in context["selected"]))
                for j,name in enumerate(METRICS):
                    item["q_negative_"+name]=float(np.mean(sim_states[:,j]<0))
                    item["q_positive_"+name]=float(np.mean(sim_states[:,j]>0))
                    item["mean_model_"+name]=float(np.mean(statistics[:,j]))
                item["mean_model_O_with_S_low"]=float(np.mean(statistics[:,4]))
                group_rows.append(item)
                for case in aliases:
                    rows.append(dict(**item,model_label=case,case=labels[case]["case"],
                                     rate_draw=labels[case]["rate_draw"],
                                     hypothesis=labels[case]["hypothesis"]))
                if number%40==0:
                    print("R2_MATCH_PROGRESS",family,noise_type,bg,mode,
                          number+1,"/",len(groups),"match",fitted["calibration_status"],
                          "R2",round(context["target_r2"],5),
                          "complete",int(match.sum()),flush=True)
    scores=pd.DataFrame(rows)
    grouped=pd.DataFrame(group_rows)
    summary=[]
    for (bg,mode),subset in grouped.groupby(["background","mode"]):
        eligible=subset[subset.calibration_status.isin(["MATCHED_R2","MATCHED_WITHOUT_NOISE"])]
        for cohort,label in [(subset,"all"),(eligible,"r2_matched_only")]:
            if cohort.empty:
                summary.append(dict(family=family,noise_type=noise_type,background=bg,
                                    mode=mode,group_selection=label,n_source_groups=0,
                                    n_with_modal_complete=0,best_group="NONE",best_joint_soft=np.nan,
                                    best_complete_fraction=np.nan,
                                    status="NO_REACHABLE_R2_GROUPS"))
                continue
            best=cohort.sort_values(["soft_joint_agreement","source_group"],
                                    ascending=[False,True]).iloc[0]
            summary.append(dict(family=family,noise_type=noise_type,background=bg,
                                mode=mode,group_selection=label,
                                n_source_groups=len(cohort),
                                n_with_modal_complete=int((cohort.modal_complete_count>0).sum()),
                                best_group=best.source_group,
                                best_joint_soft=float(best.soft_joint_agreement),
                                best_complete_fraction=float(best.modal_complete_frequency),
                                status="POST_OUTCOME_DESCRIPTIVE_NOISE_SENSITIVITY"))
        top=eligible.sort_values(["soft_joint_agreement","source_group"],
                                  ascending=[False,True]).head(6)
        print("R2_MATCH_FAMILY_SUMMARY",family,noise_type,bg,mode,
              "eligible",len(eligible),"best",
              top[["source_group","soft_joint_agreement","modal_complete_frequency",
                   "q_lowS_near_zero","r2_evaluation_mean"]].to_dict("records"),
              flush=True)
    out=dict(candidate_scores=scores,source_group_scores=grouped,
             noise_calibration=pd.DataFrame(calibration),
             observed_r2_and_patterns=pd.DataFrame(observed),
             family_summary=pd.DataFrame(summary))
    stem=f"{family}_{noise_type}"
    for name,frame in out.items():
        frame.to_csv(out_dir/(stem+"_"+name+".csv"),index=False)
    receipt=dict(status="POST_HOC_NOISE_R2_MATCHED_ACOUSTIC_POM_NOT_BIOLOGICAL_ABC",
                 family=family,noise_type=noise_type,sites=len(d),surveys=int(d.n.sum()),
                 n_candidate_labels=len(grids),n_distinct_source_groups=len(groups),
                 observation_modes=list(MODES),n_calibration_noise_fields=cal_reps,
                 n_independent_evaluation_noise_fields=eval_reps,
                 r2_calibration="Identical site 8-term unadjusted globally ranked O/S/V OLS",
                 threshold="0.90 observed common-spatial-block bootstrap 4 directions + low-S observed CI ternary",
                 zero_noise_reachability_flagged=True,
                 model_noise_not_empirically_calibrated="Site iid Gaussian or arbitrary .25 block component; matched only R2",
                 no_inference=["R2 matching is outcome-informed post hoc",
                               "Per-model noise fit is not a full likelihood or true observation-model calibration",
                               "Rank before noise removes source absolute effect magnitude",
                               "Log-source noise sensitivity also cancels uniform amplitude rescaling under per-model calibration",
                               "No prospective NAAMP holdout, no field trophic causal identification"],
                 source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [SITE,VISITS,*inputs]},
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out_dir/(stem+"_receipt.json")).write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true")
    parser.add_argument("--family",choices=FAMILIES,required=True)
    parser.add_argument("--noise-type",choices=NOISE_TYPES,default="iid")
    parser.add_argument("--cal-reps",type=int,default=N_CAL)
    parser.add_argument("--eval-reps",type=int,default=N_EVAL)
    args=parser.parse_args()
    if not args.run:parser.error("Explicit --run required")
    evaluate_family(args.family,args.noise_type,args.cal_reps,args.eval_reps)


if __name__=="__main__":
    main()
