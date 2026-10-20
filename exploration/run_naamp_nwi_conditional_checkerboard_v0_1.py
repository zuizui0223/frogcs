#!/usr/bin/env python3
"""Route-cross-fitted NWI vegetation-weighted fixed-margin frog checkerboard nulls.

New post-hoc exploration, scientifically/firewall separated from JAE RC6.
Exactly retains ten-stop taxon row sums and stop-column species totals.
The conditional logistic training is independent of each held-out route.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[1]
CONTRACT="exploration/NAAMP_NWI_CONDITIONAL_CHECKERBOARD_CONTRACT_V0_1.md"
SEED=2840267
B=199
RIDGE=3.0
LIMIT=3.0
MIN_TRAIN_RUNS=30
MIN_TRAIN_ROUTES=12
Z=1.959963984540054
MODES=(("any",1),("strong",2))
BURN=40
THIN=8
MASKS={}
for k in range(1,10):
    combos=list(itertools.combinations(range(10),k))
    mat=np.zeros((len(combos),10),dtype=np.float64)
    for idx,stops in enumerate(combos):
        mat[idx,list(stops)]=1.
    MASKS[k]=mat

def getmod(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod

def route_fold(route):
    digest=hashlib.sha256(str(route).encode()).digest()
    return "A" if digest[0]%2==0 else "B"

def complementary(fold):
    return "B" if fold=="A" else "A"

def cscore(rows):
    n=len(rows)
    if n<2:return float("nan")
    masks=[sum(1<<j for j in s) for s in rows]
    n_pairs=0
    total=0.
    for i in range(n-1):
        a=masks[i]
        ki=a.bit_count()
        for j in range(i+1,n):
            b=masks[j]
            common=(a&b).bit_count()
            total+=(ki-common)*(b.bit_count()-common)
            n_pairs+=1
    return total/n_pairs

def fixed_margins(rows):
    return ([len(x) for x in rows],
            [sum(j in x for x in rows) for j in range(10)])

def exchangeable(rows):
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):
            if rows[i]-rows[j] and rows[j]-rows[i]:
                return True
    return False

def weighted_trade(rows,scores,rng):
    n=len(rows)
    i=rng.randrange(n)
    j=rng.randrange(n-1)
    if j>=i:j+=1
    old_i=rows[i]
    old_j=rows[j]
    only_i=old_i-old_j
    only_j=old_j-old_i
    if not only_i or not only_j:
        return 0,0
    pool=sorted(only_i|only_j)
    new_i=set(rng.sample(pool,len(only_i)))
    if new_i==only_i:
        return 1,0
    # Symmetric Curveball proposal; the common sites remain in both rows.
    delta=float(sum(scores[i,t]-scores[j,t] for t in new_i) -
                sum(scores[i,t]-scores[j,t] for t in only_i))
    if delta>=0 or rng.random()<math.exp(max(-745.,delta)):
        shared=old_i&old_j
        rows[i]=shared|new_i
        rows[j]=shared|(set(pool)-new_i)
        return 1,1
    return 1,0

def synth_test():
    initial=[{0,1,2},{1,3},{2,3,4},{0,4}]
    target=fixed_margins(initial)
    rng=random.Random(284076)
    rows=[set(s) for s in initial]
    score=np.asarray([[.01*i+.02*j for j in range(10)] for i in range(4)],float)
    for t in range(400):
        weighted_trade(rows,score,rng)
        if t%20==0:
            assert fixed_margins(rows)==target, "weighted Curveball violated matrix margins"
    assert cscore([{0},{1},{2}])>cscore([{0},{0},{0}])
    # Exact two-matrix stationary distribution test at a fixed margin.
    tiny=[{0},{1}]
    two_scores=np.asarray([[0.,0.],[0.,2.]],float)
    rng=random.Random(2840271)
    seen=0
    for t in range(12000):
        for _ in range(3):
            weighted_trade(tiny,two_scores,rng)
        if t>=2000:
            seen+=int(1 in tiny[1])
    observed=seen/10000
    expected=math.exp(2)/(1+math.exp(2))
    assert abs(observed-expected)<.05, (observed,expected)
    assert route_fold("State:000001")==route_fold("State:000001")
    return {"status":"PASS","fixed_fixed_margins":"PASS",
            "weighted_two_by_two_stationary_probability":observed,
            "weighted_two_by_two_theoretical_probability":expected}

def load_run_context():
    source=getmod("frog_nwi_vegetation",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    nwi,audit=source.read_nwi(
        ROOT/"build/vegetation_context/site_nwi_vegetation_context.csv",
        ROOT/"build/vegetation_context/geometry_nwi_preflight.json")
    assert audit["preflight_eligible"] and audit["mode"]=="full"
    assert len(audit["overlay"]["shards"])==12 and audit["overlay"]["site_records"]==5147
    raw=source.hist.load_retry()
    runs,_=source.base.build_runs(raw)
    eligible=set(runs.RunID.astype(str))
    sampled,_=source.spatial.stop_matrix(raw,eligible)
    sites=source.hist.site_map(raw,eligible)
    ci=source.hist.ci_map(raw,eligible,sampled)
    stop_env=source.get_temps_and_detection(raw,runs,sampled)
    # Observed counts are not used to select which NWI locations enter a route.
    records={}
    skipped=Counter()
    folds=Counter()
    for r in runs.itertuples(index=False):
        rid=str(r.RunID)
        route=str(r.route_cluster)
        state=str(r.State)
        route_no=str(r.RouteNumber)
        stops=sorted(sampled[rid],key=int)
        if len(stops)!=10:
            raise RuntimeError("complete NAAMP ten-stop identity drift")
        siteids=[sites.get((rid,st)) for st in stops]
        if any(sid is None or (state,route_no,str(sid)) not in nwi.index for sid in siteids):
            skipped["no_complete_ten_site_vegetation"]+=1
            continue
        if len(set(siteids))!=10:
            skipped["duplicate_physical_site_id"]+=1
            continue
        if any(any(not np.isfinite(stop_env.get((rid,st),{}).get(key,np.nan))
                   for key in ("stop_air_temp_c","stop_sound_index")) for st in stops):
            skipped["missing_stop_temperature_or_noise"]+=1
            continue
        mat=nwi.loc[[(state,route_no,str(sid)) for sid in siteids]]
        v=np.column_stack([
            10*mat.nwi_all_wetland_cover_250m.astype(float).to_numpy(),
            10*mat.nwi_emergent_cover_250m.astype(float).to_numpy()
        ])
        if not np.isfinite(v).all():raise RuntimeError("nonfinite NWI input")
        activity={}
        for name,threshold in MODES:
            by_taxon=defaultdict(set)
            for k,st in enumerate(stops):
                for taxon,x in ci.get((rid,st),{}).items():
                    if int(x)>=threshold:by_taxon[taxon].add(k)
            activity[name]={sp:spots for sp,spots in by_taxon.items() if spots}
        fold=route_fold(route)
        records[rid]={"rid":rid,"route":route,"state":state,"fold":fold,
                      "v":v,"activity":activity}
        folds[fold]+=1
    audit_out={
        "source_complete_runs":int(len(runs)),
        "ten_stop_vegetation_plus_observation_runs":len(records),
        "routes":len(set(x["route"] for x in records.values())),
        "fold_run_counts":dict(folds),
        "skipped":dict(skipped),
        "coordinate_blind_NWI_source_run":39450277196,
        "response_counts_not_used_for_geographic_selection":True
    }
    return records,audit_out

def ref_rows(run,ref):
    rows=run["activity"][ref]
    taxa=sorted(rows)
    return taxa,[rows[k] for k in taxa]

def training_by_mode(records,mode):
    group={"A":defaultdict(list),"B":defaultdict(list)}
    for run in records.values():
        if np.ptp(run["v"][:,0])<1e-8 and np.ptp(run["v"][:,1])<1e-8:
            continue
        for sp,sites in run["activity"][mode].items():
            k=len(sites)
            if k<=0 or k>=10:continue
            obs=np.sum(run["v"][sorted(sites)],axis=0)
            group[run["fold"]][sp].append({
                "v":run["v"],"k":k,"obs":obs,
                "route":run["route"]})
    return group

def exact_fit(records,features):
    data=[x for x in records if np.ptp(x["v"][:,0])>1e-8 or np.ptp(x["v"][:,1])>1e-8]
    n=len(data)
    routes=len(set(z["route"] for z in data))
    if n<MIN_TRAIN_RUNS or routes<MIN_TRAIN_ROUTES:
        return np.zeros(len(features)),{"status":"insufficient","training_runs":n,"training_routes":routes}
    obs=np.sum([x["obs"][features] for x in data],axis=0)
    blocks=[]
    for k in range(1,10):
        items=[z["v"][:,features] for z in data if z["k"]==k]
        if not items:continue
        stacked=np.stack(items,axis=0)
        subset=np.einsum("mjd,sj->msd",stacked,MASKS[k],optimize=True)
        blocks.append(subset)
    d=len(features)
    def objective(params):
        loss=.5*RIDGE*float(np.dot(params,params))-float(np.dot(params,obs))
        grad=RIDGE*params-obs.copy()
        for matrix in blocks:
            score=np.einsum("msd,d->ms",matrix,params,optimize=True)
            logz=logsumexp(score,axis=1)
            weights=np.exp(score-logz[:,None])
            loss+=float(logz.sum())
            grad+=np.einsum("ms,msd->d",weights,matrix,optimize=True)
        return loss,grad
    solved=minimize(objective,np.zeros(d,float),method="L-BFGS-B",jac=True,
                    bounds=[(-LIMIT,LIMIT)]*d,options={"maxiter":70,"ftol":1e-10})
    beta=np.clip(np.asarray(solved.x,float),-LIMIT,LIMIT)
    if not np.isfinite(beta).all():
        return np.zeros(d),{"status":"nonfinite_fit_fallback","training_runs":n,"training_routes":routes}
    return beta,{"status":"fitted" if solved.success else "numerical_nonconvergence",
                 "training_runs":n,"training_routes":routes,
                 "coefficients":beta.tolist(),"optimizer_iterations":int(solved.nit),
                 "optimizer_success":bool(solved.success),
                 "penalty":RIDGE,"bounds":[-LIMIT,LIMIT]}

def fit_fold_coefficients(records,mode):
    trainings=training_by_mode(records,mode)
    coefficients={}
    audits={}
    for fold in ("A","B"):
        species=sorted(trainings[fold])
        coef={}
        meta={}
        for idx,sp in enumerate(species):
            observations=trainings[fold][sp]
            wet,wet_meta=exact_fit(observations,[0])
            both,both_meta=exact_fit(observations,[0,1])
            if wet_meta["status"]!="fitted":wet=np.zeros(1)
            if both_meta["status"]!="fitted":both=np.zeros(2)
            coef[sp]={"wetland":wet,"wetland_and_emergent":both}
            meta[sp]={"wetland":wet_meta,"wetland_and_emergent":both_meta}
        coefficients[fold]=coef
        audits[fold]={
            "n_taxa_with_train_records":len(species),
            "n_training_taxa_wetland_fitted":sum(x["wetland"]["status"]=="fitted" for x in meta.values()),
            "n_training_taxa_joint_fitted":sum(x["wetland_and_emergent"]["status"]=="fitted" for x in meta.values()),
            "n_joint_positive_PEM_slopes":sum((x["wetland_and_emergent"]["status"]=="fitted"
                and float(coef[sp]["wetland_and_emergent"][1])>0) for sp,x in meta.items()),
            "n_joint_negative_PEM_slopes":sum((x["wetland_and_emergent"]["status"]=="fitted"
                and float(coef[sp]["wetland_and_emergent"][1])<0) for sp,x in meta.items()),
            "per_taxon":meta}
    return coefficients,audits

def conditional_logprob(v,occupied,theta,which):
    k=len(occupied)
    if k in (0,10):return 0.
    feat=v[:,which]
    observed=float(np.dot(theta,np.sum(feat[sorted(occupied)],axis=0)))
    subset=MASKS[k]@feat
    logz=float(logsumexp(subset@theta))
    return observed-logz

def heldout_scores(records,refs,mode,coefs):
    # Cross-fitted log probability with only row margins conditioned;
    # zero/predictive gains are not direct significance of C-score.
    results={"A":dict(uniform=0.,wetland=0.,wetland_and_emergent=0.,clusters=0),
             "B":dict(uniform=0.,wetland=0.,wetland_and_emergent=0.,clusters=0)}
    for rid in sorted(refs):
        run=records[rid]
        train=coefs[complementary(run["fold"])]
        f=results[run["fold"]]
        for sp,occupied in run["activity"][mode].items():
            k=len(occupied)
            if k in (0,10):continue
            beta=train.get(sp,{"wetland":np.zeros(1),
                               "wetland_and_emergent":np.zeros(2)})
            f["uniform"]-=math.log(MASKS[k].shape[0])
            f["wetland"]+=conditional_logprob(run["v"],occupied,beta["wetland"],[0])
            f["wetland_and_emergent"]+=conditional_logprob(run["v"],occupied,beta["wetland_and_emergent"],[0,1])
            f["clusters"]+=1
    out={}
    for fold,record in results.items():
        n=record["clusters"]
        out[fold]={**record,
                  "wetland_minus_uniform_per_cluster":(record["wetland"]-record["uniform"])/n if n else None,
                  "emergent_increment_over_wetland_per_cluster":(record["wetland_and_emergent"]-record["wetland"])/n if n else None}
    n=sum(x["clusters"] for x in results.values())
    return {"folds":out,"total_clusters":n,
            "wetland_minus_uniform_total":sum(x["wetland"]-x["uniform"] for x in results.values()),
            "emergent_increment_over_wetland_total":sum(x["wetland_and_emergent"]-x["wetland"] for x in results.values()),
            "emergent_increment_per_cluster":sum(x["wetland_and_emergent"]-x["wetland"] for x in results.values())/n if n else None}

def fixed_margin_sampler(rows,score,rng):
    current=[set(s) for s in rows]
    target=fixed_margins(current)
    burn=BURN*len(current)
    thin=THIN*len(current)
    feasible=accepted=0
    for _ in range(burn):
        a,b=weighted_trade(current,score,rng);feasible+=a;accepted+=b
    draws=np.empty(B,float)
    for i in range(B):
        for _ in range(thin):
            a,b=weighted_trade(current,score,rng);feasible+=a;accepted+=b
        draws[i]=cscore(current)
        if i in (0,B//2,B-1):
            if fixed_margins(current)!=target:
                raise RuntimeError("Weighted Curveball changed observed row/column sums")
    return draws,{"n_feasible_proposals":feasible,"n_accepted_changed":accepted,
                  "accepted_given_feasible":accepted/feasible if feasible else 0.,
                  "cscore_sim_sd":float(draws.std(ddof=1)),
                  "n_distinct_cscore_draws":int(np.unique(np.round(draws,10)).size)}

def route_cluster_effect(d,field):
    fit=sm.OLS(d[field].astype(float).to_numpy(),
               np.ones((len(d),1),float)).fit(cov_type="cluster",
                                             cov_kwds={"groups":d.route.astype(str)})
    b=float(fit.params[0]);se=float(fit.bse[0])
    return {"mean":b,"se_route_cluster":se,
            "ci95":[b-Z*se,b+Z*se],
            "p_two_sided":float(fit.pvalues[0]),"routes":int(d.route.nunique()),
            "n_runs":int(len(d))}

def simulation_results(records,ref,mode,coef,qa_only=False):
    ref=ref.copy()
    if ref.RunID.duplicated().any():raise RuntimeError("Frozen checkerboard source duplicates RunID")
    baseline={}
    for row in ref.itertuples(index=False):
        baseline[str(row.RunID)]=row
    ids=sorted(set(baseline)&set(records))
    if not qa_only and (len(ids)<100 or len(set(records[x]["route"] for x in ids))<30):
        raise RuntimeError("Cannot estimate NWI-conditioned checkerboard with fewer than 100 runs/30 routes")
    sums={"wetland":np.zeros(B,float),"wetland_and_emergent":np.zeros(B,float)}
    stats={"wetland":[],"wetland_and_emergent":[]}
    out=[]
    for idx,rid in enumerate(ids,1):
        run=records[rid]
        taxa,rows=ref_rows(run,mode)
        if not exchangeable(rows):raise RuntimeError("Existing checkerboard sample had no feasible Curveball trade")
        observed=cscore(rows)
        previous=baseline[rid]
        if not np.isclose(observed,float(previous.observed_cscore),atol=1e-8,rtol=0):
            raise RuntimeError(f"Frozen C-score mismatch run={rid} ref={previous.observed_cscore} now={observed}")
        fold=run["fold"]
        other=coef[complementary(fold)]
        sloped={model:[] for model in sums}
        for sp in taxa:
            values=other.get(sp,{})
            sloped["wetland"].append(np.asarray(values.get("wetland",np.zeros(1)),float))
            sloped["wetland_and_emergent"].append(np.asarray(values.get("wetland_and_emergent",np.zeros(2)),float))
        info={"RunID":rid,"route":run["route"],"fold":fold,
              "observed":observed,"baseline_mean":float(previous.null_mean),
              "baseline_null_sd":float(previous.null_sd),
              "n_taxa":len(taxa),
              "n_active_stops":len(set().union(*rows))}
        for model,cols in (("wetland",[0]),("wetland_and_emergent",[0,1])):
            theta=np.stack(sloped[model],axis=0)
            score=theta@run["v"][:,cols].T
            hashinput=f"{SEED}|{mode}|{model}|{rid}".encode("utf-8")
            rng=random.Random(int.from_bytes(hashlib.sha256(hashinput).digest()[:8],"big"))
            draws,diagnostic=fixed_margin_sampler(rows,score,rng)
            info[model+"_null_mean"]=float(draws.mean())
            info[model+"_residual"]=float(observed-draws.mean())
            info[model+"_accepted_feasible"]=float(diagnostic["accepted_given_feasible"])
            info[model+"_sim_sd"]=float(diagnostic["cscore_sim_sd"])
            info[model+"_mix_flag"]=bool(float(previous.null_sd)>1e-8
                and diagnostic["n_distinct_cscore_draws"]<2)
            sums[model]+=draws
            stats[model].append(diagnostic)
        info["baseline_residual"]=info["observed"]-info["baseline_mean"]
        info["wetland_model_gain"]=info["wetland_null_mean"]-info["baseline_mean"]
        info["emergent_model_gain"]=info["wetland_and_emergent_null_mean"]-info["wetland_null_mean"]
        info["full_model_gain"]=info["wetland_and_emergent_null_mean"]-info["baseline_mean"]
        out.append(info)
        if idx%450==0:
            print(f"{mode}: processed {idx}/{len(ids)} held-out checkerboard matrices",flush=True)
    d=pd.DataFrame(out)
    mean_obs=float(d.observed.mean())
    mean_base=float(d.baseline_mean.mean())
    res={
        "mode":mode,
        "n_heldout_runs":int(len(d)),
        "n_routes":int(d.route.nunique()),
        "n_training_heldout_fold_A":int((d.fold=="A").sum()),
        "n_training_heldout_fold_B":int((d.fold=="B").sum()),
        "observed_mean_Cscore":mean_obs,
        "fixed_fixed_mean_Cscore":mean_base,
        "fixed_fixed_mean_excess":float(d.baseline_residual.mean()),
        "route_cluster_effects":{
            field:route_cluster_effect(d,field) for field in (
                "baseline_residual","wetland_residual","wetland_and_emergent_residual",
                "wetland_model_gain","emergent_model_gain","full_model_gain")},
        "folds":{},
        "generator":{}
    }
    for fold in ("A","B"):
        sub=d[d.fold==fold]
        res["folds"][fold]={
            "n_runs":int(len(sub)),"n_routes":int(sub.route.nunique()),
            "fixed_excess":float(sub.baseline_residual.mean()),
            "wetland_residual":float(sub.wetland_residual.mean()),
            "wetland_and_emergent_residual":float(sub.wetland_and_emergent_residual.mean()),
            "emergent_gain_over_wetland":float(sub.emergent_model_gain.mean())}
    for model in sums:
        expected=sums[model]/len(d)
        # Plus-one directional Monte Carlo P against the observed mean.
        numeric_mean=float(d[model+"_null_mean"].mean())
        target=float(expected.mean())
        if abs(numeric_mean-target)>1e-7:raise RuntimeError("C-score simulation aggregation drift")
        st=stats[model]
        original_info=d.baseline_null_sd>1e-8
        zero_mix=int(d[model+"_mix_flag"].sum())
        n_info=int(original_info.sum())
        res["generator"][model]={
            "mean_null_Cscore":numeric_mean,
            "mean_Cscore_residual":float(mean_obs-numeric_mean),
            "simulation_null_ci95":[float(x) for x in np.quantile(expected,[.025,.975])],
            "upper_tail_plus_one_p":float((1+np.sum(expected>=mean_obs))/(B+1)),
            "mean_accepted_given_feasible":float(np.mean([x["accepted_given_feasible"] for x in st])),
            "informative_reference_matrices":n_info,
            "lack_of_Cscore_mixing_matrices":zero_mix,
            "no_mixing_fraction_among_informative":zero_mix/n_info if n_info else None,
            "sampling_unreliable":bool(n_info and zero_mix/n_info>.20),
            "posthoc_vs_fixed_fraction_of_excess_explained":
                float((numeric_mean-mean_base)/(mean_obs-mean_base)) if abs(mean_obs-mean_base)>1e-8 else None}
    return d,res

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--ref-any",type=Path)
    parser.add_argument("--ref-strong",type=Path)
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"nwi_conditional_checkerboard")
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    synth=synth_test()
    print("SYNTHETIC_CURVEBALL_QA",json.dumps(synth),flush=True)
    if args.synthetic_only:return
    if not(args.ref_any and args.ref_strong):
        raise SystemExit("--ref-any and --ref-strong required")
    refs={"any":pd.read_csv(args.ref_any,dtype={"RunID":str}),
          "strong":pd.read_csv(args.ref_strong,dtype={"RunID":str})}
    records,scope=load_run_context()
    out={"analysis":"naamp_nwi_species_conditional_checkerboard_crossfit_v0_1",
         "contract":CONTRACT,
         "status":"new_posthoc_exploration_not_independent_confirmation",
         "source_synthetic_qa":synth,
         "source_data_coverage":scope,
         "settings":{
            "fold":"SHA256 route_cluster -> A/B; trained only on opposite fold",
            "primary_any_CI123_secondary_strong_CI23":True,
            "training":"exact fixed-k conditional logistic odds for taxa with >=30 informative records and >=12 routes",
            "training_ridge":RIDGE,"theta_bounds":[-LIMIT,LIMIT],
            "reference_fixed_fixed_draws":399,
            "weighted_sampler_draws":B,"burn_in_proposals_per_taxon":BURN,
            "thin_proposals_per_taxon":THIN,
            "random_seed":SEED,"fixed_row_margins":True,"fixed_col_margins":True,
            "mapped_vegetation_not_time_matched":True,
            "frozen_RC6_not_modified":True
         },"modes":{}}
    args.outdir.mkdir(parents=True,exist_ok=True)
    for mode,_ in MODES:
        coefficients,training=fit_fold_coefficients(records,mode)
        candidates=sorted(set(refs[mode].RunID.astype(str))&set(records))
        predictive=heldout_scores(records,candidates,mode,coefficients)
        result_df,analysis=simulation_results(records,refs[mode],mode,coefficients)
        out["modes"][mode]={
            "training":{
                fld:{key:val for key,val in d.items() if key!="per_taxon"}
                for fld,d in training.items()},
            "train_full_taxon_detail":training,
            "heldout_conditional_location_logscore":predictive,
            "checkerboard":analysis
        }
        result_df.to_csv(args.outdir/f"{mode}_heldout_run_diagnostics.csv",index=False)
        (args.outdir/f"{mode}_train_coefficients.json").write_text(
           json.dumps({f:{s:{k:v.tolist() for k,v in z.items()}
                        for s,z in coefs.items()} for f,coefs in coefficients.items()},
                       indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print("MODE_COMPLETE",mode,
              json.dumps({"heldout_runs":analysis["n_heldout_runs"],
                          "fixed_excess":analysis["fixed_fixed_mean_excess"],
                          "plant_gain":analysis["route_cluster_effects"]["emergent_model_gain"]["mean"],
                          "plant_adjusted_residual":analysis["generator"]["wetland_and_emergent"]["mean_Cscore_residual"]}),
              flush=True)
    (args.outdir/"result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("VEGETATION_CONDITIONAL_CHECKERBOARD_BEGIN",flush=True)
    print(json.dumps(out,sort_keys=True),flush=True)
    print("VEGETATION_CONDITIONAL_CHECKERBOARD_END",flush=True)

if __name__=="__main__":
    main()
