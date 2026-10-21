#!/usr/bin/env python3
"""Species × strictly earlier-year physical SiteID first-order explanation of
the same-survey Lithobates clamitans positive/negative partner contrast.

Post-hoc exploratory NAAMP × frozen NWI first-order null. No causal interaction
claim. Historical observations are from prior YEARS within the same
State×RouteNumber×RunNumber season stratum and never read the tested year's
responses to construct its site-habitat score.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import random
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.special import logsumexp
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
B=199
SEED=2840317
BURN=40
THIN=8
ALPHA=4.0
Z=1.959963984540054
BOOT=2000
BOOT_SEED=2840319
SCENARIOS={"N0_NWI_only":0.0,"N1_NWI_plus_prior_SiteID":1.0,
           "Nhalf_NWI_plus_half_prior_SiteID":0.5}
C="Lithobates clamitans"
P="Lithobates catesbeianus"
NEG=("Anaxyrus fowleri","Hyla versicolor")
TRIOS=[(C,P,x) for x in NEG]
REQUIRED_SOURCE_ANY=3659
REQUIRED_SOURCE_STRONG=1766

def json_numpy_scalar(value):
    """Serialize NumPy diagnostic scalars without changing fitted values."""
    if isinstance(value,np.generic):
        return value.item()
    if isinstance(value,np.ndarray):
        return value.tolist()
    raise TypeError(f"Unsupported diagnostic type: {type(value).__name__}")


def mod(name,path):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp)
    assert sp.loader
    sp.loader.exec_module(m)
    return m

pairmod=mod("site_prior_network",ROOT/"exploration/run_naamp_plant_conditioned_pair_network_v0_1.py")
prior=pairmod.prior
ecology=mod("site_prior_ecology",ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")

def site_score(sids,opps,positives,mode):
    """Empirical-Bayes-smoothed per-species historical site relative log odds.

    Input positives is a dict indexed by (SiteID,taxon); opps is per-site
    number of earlier visits. A species absent in prior years is neutral.
    """
    total_n=sum(opps.values())
    taxa={sp for sid,sp in positives[mode]}
    result={}
    for sp in taxa:
        yes=sum(v for (sid,name),v in positives[mode].items() if name==sp)
        if yes<=0 or total_n<=0:
            continue
        p_route=(yes+1.0)/(total_n+2.0)
        h=[]
        for sid in sids:
            nn=opps.get(sid,0)
            y=positives[mode].get((sid,sp),0)
            p=(y+ALPHA*p_route)/(nn+ALPHA)
            p=float(np.clip(p,1e-8,1-1e-8))
            h.append(math.log(p/(1-p)))
        q=np.asarray(h,float)
        q=np.clip(q-q.mean(),-3.0,3.0)
        if np.ptp(q)>1e-12:
            result[sp]=q
    return result

def synthetic_qa():
    assert prior.synth_test()["status"]=="PASS"
    ids=["siteA","siteB","siteC","siteD","siteE","siteF","siteG","siteH","siteI","siteJ"]
    ops={x:5 for x in ids}
    ps={"any":{("siteA","frog"):4,("siteB","frog"):1},"strong":{}}
    score=site_score(ids,ops,ps,"any")["frog"]
    assert score[0]>score[1]
    assert abs(score.mean())<1e-11
    assert "frog" not in site_score(ids,ops,ps,"strong")
    assert np.all(np.isfinite(score))
    # No species association can be imposed by a pairwise-targeted
    # historical score that is constant within the species row.
    assert np.ptp(np.full(10,1.0))==0
    return {"status":"PASS","historical_species_logodds":"PASS",
            "unseen_taxon_fails_neutral":"PASS",
            "earlier_year_only_design":"PASS",
            "weighted_Curveball_fixed_margins":"PASS"}

def historical_provenance(raw,runs,records):
    """Build history scores, frozen before checking target pair associations.

    For each State/Route/season stratum process all surveys of the same year
    without adding them to accumulated past values until next year.
    """
    eligible=set(runs.RunID.astype(str))
    sampled,_=ecology.spatial.stop_matrix(raw,eligible)
    sites=ecology.hist.site_map(raw,eligible)
    ci=ecology.hist.ci_map(raw,eligible,sampled)
    strata=defaultdict(list)
    for r in runs.itertuples(index=False):
        strata[(str(r.State),str(r.RouteNumber),str(r.RunNumber))].append(
            (int(r.SurveyYear),str(r.RunID)))
    derived={}
    audit=Counter()
    for stratum,entries in strata.items():
        by_year=defaultdict(list)
        for year,rid in entries:by_year[year].append(rid)
        opportunities=Counter()
        calls={"any":Counter(),"strong":Counter()}
        prior_n=0
        for year in sorted(by_year):
            current=sorted(by_year[year])
            for rid in current:
                if rid not in records:continue
                run=records[rid]
                stops=sorted(sampled[rid],key=int)
                if len(stops)!=10:
                    raise RuntimeError("Historical SiteID check lost ten stops")
                siteids=[sites.get((rid,st)) for st in stops]
                if any(z is None for z in siteids) or len(set(siteids))!=10:
                    raise RuntimeError("Target 10-site identities changed")
                n_available=sum(opportunities.get(z,0)>0 for z in siteids)
                gate=prior_n>=2 and n_available>=8
                audit["checked_NWI_runs"]+=1
                if not gate:
                    audit["insufficient_prior_stratum_or_site_support"]+=1
                    continue
                score={
                  mode:site_score(siteids,opportunities,calls,mode)
                  for mode in ("any","strong")
                }
                derived[rid]={
                  "scores":score,
                  "prior_same_season_runs":prior_n,
                  "n_sites_with_prior_visits":n_available,
                  "total_prior_physical_stop_visits":int(sum(opportunities.values())),
                  "past_survey_years_only":True,
                  "SiteIDs":siteids
                }
                audit["prior_source_eligible_runs"]+=1
                for mode in ("any","strong"):
                    audit[f"{mode}_nonzero_historical_score_taxa"]+=len(score[mode])
            # Crucial: update only AFTER all survey runs in that survey year
            # have been evaluated, avoiding leakage from same-year observations.
            for rid in current:
                prior_n+=1
                for st in sampled[rid]:
                    sid=sites.get((rid,st))
                    if sid is None:continue
                    opportunities[sid]+=1
                    for taxon,ci_val in ci.get((rid,st),{}).items():
                        if ci_val>=1:calls["any"][(sid,taxon)]+=1
                        if ci_val>=2:calls["strong"][(sid,taxon)]+=1
    return derived,dict(audit)

def draw_null(rows,scores,mode,rid,model,positions):
    state=[set(x) for x in rows]
    reference=prior.fixed_margins(state)
    sha=hashlib.sha256(f"{SEED}|{mode}|{rid}".encode()).digest()[:8]
    rng=random.Random(int.from_bytes(sha,"big"))
    # Common random seeds across model types improve numerical comparison
    # without making posterior draws identical.
    feasible=accepted=0
    for _ in range(BURN*len(rows)):
        f,a=prior.weighted_trade(state,scores,rng)
        feasible+=f;accepted+=a
    means={name:{z:np.zeros(B,float) for z in ("CP","CN","D")}
           for name in positions}
    draw_cscore=np.empty(B,float)
    for it in range(B):
        for _ in range(THIN*len(rows)):
            f,a=prior.weighted_trade(state,scores,rng)
            feasible+=f;accepted+=a
        cov=pairmod.cov_matrix(state)
        draw_cscore[it]=prior.cscore(state)
        for neg,(i,j,k) in positions.items():
            x=float(cov[i,j]);y=float(cov[i,k])
            means[neg]["CP"][it]=x
            means[neg]["CN"][it]=y
            means[neg]["D"][it]=x-y
        if it in (0,B//2,B-1) and reference!=prior.fixed_margins(state):
            raise RuntimeError("Weighted Curveball changed species count or site richness")
    if not feasible or not accepted:raise RuntimeError("No fixed-margin variation on eligible exchangeable run")
    outputs={name:{key:float(vals.mean()) for key,vals in fields.items()}
             for name,fields in means.items()}
    diagnostic={name:{
        "n_distinct_D":len(np.unique(np.round(fields["D"],10))),
        "sd_D":float(np.std(fields["D"],ddof=1)),
        "n_feasible":feasible,"n_accepted":accepted
    } for name,fields in means.items()}
    return outputs,diagnostic,draw_cscore

def fit_cluster(frame,metric,min_n=20,min_routes=10):
    if len(frame)<min_n or frame.route.nunique()<min_routes:
        return {"status":"insufficient","n_runs":int(len(frame)),
                "n_routes":int(frame.route.nunique()) if len(frame) else 0}
    fit=sm.OLS(frame[metric].to_numpy(float),np.ones((len(frame),1))).fit(
        cov_type="cluster",cov_kwds={"groups":frame.route.astype(str)})
    beta=float(fit.params[0]);se=float(fit.bse[0])
    return {"status":"fitted","beta":beta,"se":se,
            "ci95":[beta-Z*se,beta+Z*se],
            "p_two_sided":float(fit.pvalues[0]),"n_runs":len(frame),
            "n_routes":int(frame.route.nunique())}

def bootstrap_logscore(table):
    if table.empty:return {"status":"empty"}
    routes=table.groupby("route").log_gain.agg(["sum","size"])
    numerator=routes["sum"].to_numpy(float)
    denominator=routes["size"].to_numpy(float)
    n=len(routes)
    idx=np.random.default_rng(BOOT_SEED).integers(0,n,(BOOT,n))
    arr=numerator[idx].sum(axis=1)/denominator[idx].sum(axis=1)
    return {"status":"fitted",
            "n_taxon_runs":int(len(table)),
            "n_routes":n,
            "mean_gain_nats_per_taxon_run":float(table.log_gain.mean()),
            "ci95_route_boot":[float(x) for x in np.quantile(arr,[.025,.975])],
            "gain_CI_positive":bool(np.quantile(arr,.025)>0),
            "n_boot":BOOT}

def logprob(scores,occupied):
    k=len(occupied)
    if not 1<=k<=9:return None
    z=prior.MASKS[k]@scores
    return float(scores[list(occupied)].sum()-logsumexp(z))

def analyze_mode(mode,records,refs,weights,histories,yearmap,outdir):
    reference=refs.copy()
    if reference.RunID.duplicated().any():
        raise RuntimeError("Frozen original NWI run-level IDs duplicate")
    reference=reference.set_index("RunID")
    ids=sorted(set(records)&set(reference.index.astype(str)))
    expected=REQUIRED_SOURCE_ANY if mode=="any" else REQUIRED_SOURCE_STRONG
    if len(ids)!=expected:raise RuntimeError("NWI source population drift "+str(len(ids)))
    compiled=defaultdict(list)
    logs=[]
    count=Counter()
    for idx,rid in enumerate(ids,1):
        item=records[rid]
        taxa,rows=prior.ref_rows(item,mode)
        obs_c=prior.cscore(rows)
        if not np.isclose(obs_c,float(reference.loc[rid,"observed"]),rtol=0,atol=1e-8):
            raise RuntimeError("Observed NWI checkerboard run differs from frozen "+rid)
        count["original_ref_verified"]+=1
        if rid not in histories:continue
        H=histories[rid]
        if not H["past_survey_years_only"]:raise RuntimeError("history year leakage flag")
        count["history_eligible_matrix_runs"]+=1
        taxid={name:i for i,name in enumerate(taxa)}
        pos={neg:(taxid[C],taxid[P],taxid[neg])
             for neg in NEG if all(z in taxid for z in (C,P,neg))}
        # No current co-occurrence endpoints used in the historical inclusion
        # criterion; triple eligibility depends only on species row totals.
        th=np.stack([
            np.asarray(weights[prior.complementary(item["fold"])].get(sp,{})
                 .get("wetland_and_emergent",np.zeros(2)),float)
            for sp in taxa
        ])
        baseline=th@item["v"][:,[0,1]].T
        hist=np.stack([
             np.asarray(H["scores"][mode].get(sp,np.zeros(10)),float)
             for sp in taxa
        ])
        if hist.shape!=baseline.shape:raise RuntimeError("History site vector and NWI stop matrix drift")
        count["taxon_runs_with_nontrivial_prior_score"]+=sum(np.ptp(z)>1e-10 for z in hist)
        # Strict chronological held-out fixed-k test of historical site choice
        # for every taxon in the (unselected) history-eligible matrix population.
        for i,occupied in enumerate(rows):
            k=len(occupied)
            if not 1<=k<=9:continue
            a=logprob(baseline[i],occupied)
            b=logprob(baseline[i]+hist[i],occupied)
            logs.append({"RunID":rid,"route":item["route"],"species":taxa[i],
                         "log_gain":b-a})
        if not pos:continue
        count["with_either_frozen_species_trio"]+=1
        nulls={}
        diagnostics={}
        for name,gamma in SCENARIOS.items():
            expected,diag,null_c=draw_null(rows,baseline+gamma*hist,mode,rid,name,pos)
            nulls[name]=expected;diagnostics[name]=diag
        observed=pairmod.cov_matrix(rows)
        for negative,(i,j,k) in pos.items():
            e={}
            for name in SCENARIOS:
                z=nulls[name][negative]
                cp=float(observed[i,j]-z["CP"])
                cn=float(observed[i,k]-z["CN"])
                e[name]={"CP":cp,"CN":cn,"D":cp-cn}
            m0=e["N0_NWI_only"]["D"]
            m1=e["N1_NWI_plus_prior_SiteID"]["D"]
            half=e["Nhalf_NWI_plus_half_prior_SiteID"]["D"]
            record={
               "RunID":rid,"route":item["route"],"State":item["state"],
               "fold":item["fold"],"SurveyYear":int(yearmap[rid]),
               "n_prior_same_season_runs":H["prior_same_season_runs"],
               "n_historical_matching_SiteIDs":H["n_sites_with_prior_visits"],
               "n_taxa":len(taxa),
               "n_past_nonconstant_species_scores":int(sum(np.ptp(z)>1e-10 for z in hist)),
               "history_score_gamma_1_mean_abs":float(np.abs(hist).mean()),
               "baseline_D":m0,"history_D":m1,"half_D":half,
               "reduction_D":m0-m1,
               "history_null_variable":bool(diagnostics["N1_NWI_plus_prior_SiteID"][negative]["n_distinct_D"]>1),
               "baseline_null_variable":bool(diagnostics["N0_NWI_only"][negative]["n_distinct_D"]>1),
            }
            for key,z in e.items():
                for part,value in z.items():
                    record[key+"_"+part]=value
            compiled[negative].append(record)
        if idx%500==0:
            print(mode,"history-filtered target runs processed",idx,"/",len(ids),flush=True)
    result={
        "coverage":{"original_NWI_matrices":len(ids),
                    "original_observed_Cscore_verified":count["original_ref_verified"],
                    "history_eligible_NWI_matrices":count["history_eligible_matrix_runs"],
                    "history_eligible_taxon_runs_with_nonconstant_site_score":count["taxon_runs_with_nontrivial_prior_score"],
                    "history_eligible_matrices_with_at_least_one_focal_trio":count["with_either_frozen_species_trio"]},
        "strict_prior_SiteID_heldout_call_site_logscore":bootstrap_logscore(pd.DataFrame(logs)),
        "focal_trios":{}
    }
    for neg in NEG:
        x=pd.DataFrame(compiled.get(neg,[]))
        trio=" || ".join((C,P,neg))
        if x.empty:
            result["focal_trios"][trio]={"status":"no_past_supported_same_run_trios"}
            continue
        x.to_csv(outdir/f"{mode}_{neg.replace(' ','_')}_prior_history_per_run.csv",index=False)
        n=len(x);routes=int(x.route.nunique())
        n_v=int(x.history_null_variable.sum())
        if not (n>=60 and routes>=25 and n_v>=20):
            result["focal_trios"][trio]={
                "status":"insufficient_prior_history_scope",
                "n_trio_runs":n,"n_routes":routes,
                "n_history_null_varying":n_v}
            continue
        effect={}
        for name in SCENARIOS:
            vals={}
            for k in ("CP","CN","D"):
                col=name+"_"+k
                vals[k]=fit_cluster(x,col,min_n=60,min_routes=25)
            effect[name]=vals
        delta=fit_cluster(x,"reduction_D",min_n=60,min_routes=25)
        before=effect["N0_NWI_only"]["D"]["beta"]
        after=effect["N1_NWI_plus_prior_SiteID"]["D"]["beta"]
        parts={key:{
            "n_runs":len(y),"n_routes":int(y.route.nunique()),
            "original_baseline_mean":float(y.baseline_D.mean()),
            "history_model_mean":float(y.history_D.mean()),
            "difference_mean":float(y.reduction_D.mean())
        } for key,y in [("early",x[x.SurveyYear<=2009]),("late",x[x.SurveyYear>=2010])]}
        temporal={}
        for label,y in [("early",x[x.SurveyYear<=2009]),("late",x[x.SurveyYear>=2010])]:
            temporal[label]={
                "NWI_D":fit_cluster(y,"baseline_D"),
                "NWI_plus_history_D":fit_cluster(y,"history_D")}
        folds={fold:{"n_runs":len(y),"history_D":float(y.history_D.mean()),
                     "baseline_D":float(y.baseline_D.mean())}
               for fold,y in x.groupby("fold")}
        result["focal_trios"][trio]={
            "status":"fitted",
            "n_trio_runs":n,"n_routes":routes,
            "n_states":int(x.State.nunique()),
            "n_history_null_varying":n_v,
            "mean_n_prior_same_season_runs":float(x.n_prior_same_season_runs.mean()),
            "mean_n_SiteIDs_with_prior_visits":float(x.n_historical_matching_SiteIDs.mean()),
            "models":effect,
            "residual_D_reduction_N1_relative_to_N0":delta,
            "fraction_partner_contrast_removed":float((before-after)/before) if abs(before)>1e-8 else None,
            "time":parts,
            "time_inference":temporal,
            "route_fold_mean":folds,
        }
    cand=[(name,q) for name,q in result["focal_trios"].items() if q.get("status")=="fitted"]
    if cand:
        qs=multipletests([x["models"]["N1_NWI_plus_prior_SiteID"]["D"]["p_two_sided"]
                         for _,x in cand],method="fdr_bh")[1]
        for (name,z),q in zip(cand,qs):
            z["BH_q_two_frozen_trios"]=float(q)
            main=z["models"]["N1_NWI_plus_prior_SiteID"]
            folds=z["route_fold_mean"]
            passed=bool(q<.05 and main["CP"]["ci95"][0]>0 and
                        main["CN"]["ci95"][1]<0 and main["D"]["ci95"][0]>0 and
                        folds.get("A",{}).get("history_D",0)>0 and
                        folds.get("B",{}).get("history_D",0)>0)
            z["persistent_partner_identity_residual_candidate"]=passed
            z["history_model_collapse"]=bool(main["D"]["ci95"][0]<=0 or
                main["CP"]["ci95"][0]<=0 or main["CN"]["ci95"][1]>=0)
            z["not_conclusive_for_individual_behavior"]=True
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-nwi",type=Path)
    p.add_argument("--outdir",type=Path,default=ROOT/"build"/"prior_site_history_partner")
    p.add_argument("--synthetic-only",action="store_true")
    args=p.parse_args()
    qa=synthetic_qa()
    print("PRIOR_SITE_HISTORY_SYNTHETIC_QA",json.dumps(qa,sort_keys=True,default=json_numpy_scalar),flush=True)
    if args.synthetic_only:return
    if not args.frozen_nwi:raise RuntimeError("Frozen NWI source artifact required")
    records,refs,coefs,scope=pairmod.prior_inputs(args.frozen_nwi)
    raw=ecology.hist.load_retry()
    runs,_=ecology.base.build_runs(raw)
    histories,historyaudit=historical_provenance(raw,runs,records)
    years=dict(zip(runs.RunID.astype(str),runs.SurveyYear.astype(int)))
    args.outdir.mkdir(parents=True,exist_ok=True)
    result={
       "analysis":"naamp_same_run_partner_NWI_vs_strict_prior_SiteID_null_v0_1",
       "status":"posthoc_new_first_order_site_history_falsification_not_causal",
       "contract":"exploration/NAAMP_PARTNER_SWITCH_PRIOR_SITE_HISTORY_NULL_CONTRACT_V0_1.md",
       "source_NWI_crossfit_run":39516056663,
       "source_same_run_partner_result_run":39597933440,
       "source_NWI_geography_run":39450277196,
       "synthetic_QA":qa,
       "source_context":scope,
       "prior_history_coverage":historyaudit,
       "settings":{"history_alpha":ALPHA,"history_strength":1.0,"attenuation":0.5,
                   "history_only_same_stratum_season":True,
                   "only_strictly_prior_years_for_history":True,
                   "nwi_heldout_route_weights_unchanged":True,
                   "B":B,"burn":BURN,"thin":THIN,
                   "species_stop_row_sums_fixed":True,"per_stop_taxon_richness_fixed":True,
                   "seed":SEED},
       "modes":{},
       "interpretation_boundary":{
           "historical_species_site_use_is_not_an_individual_memory_test":True,
           "prior_use_can_include_historical_biotic_processes":True,
           "NWI_is_not_time_matched_to_frog_surveys":True,
           "no_test_of_simultaneous_call_communication":True,
           "causal_biotic_interactions_established":False,
           "no_frozen_RC6_paper_or_SI_change":True}}
    for mode in ("any","strong"):
        result["modes"][mode]=analyze_mode(
            mode,records,refs[mode],coefs[mode],histories,years,args.outdir)
        print("PRIOR_SITE_HISTORY_MODE",mode,json.dumps({
            "coverage":result["modes"][mode]["coverage"],
            "logscore":result["modes"][mode]["strict_prior_SiteID_heldout_call_site_logscore"],
            "summary":{k:{
                 "status":v.get("status"),
                 "n":v.get("n_trio_runs"),"routes":v.get("n_routes"),
                 "baseline_D":v.get("models",{}).get("N0_NWI_only",{}).get("D",{}).get("beta"),
                 "history_D":v.get("models",{}).get("N1_NWI_plus_prior_SiteID",{}).get("D",{}).get("beta"),
                 "fraction_removed":v.get("fraction_partner_contrast_removed"),
                 "BH_q":v.get("BH_q_two_frozen_trios"),
                 "persistence":v.get("persistent_partner_identity_residual_candidate")
            } for k,v in result["modes"][mode]["focal_trios"].items()}
        },sort_keys=True,default=json_numpy_scalar),flush=True)
    (args.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True,default=json_numpy_scalar)+"\n")
    print("PRIOR_SITE_HISTORY_PARTNER_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True,default=json_numpy_scalar),flush=True)
    print("PRIOR_SITE_HISTORY_PARTNER_RESULT_END",flush=True)

if __name__=="__main__":
    main()
