#!/usr/bin/env python3
"""Same 10-stop survey test of partner-specific frog acoustic co-calling.

One central taxon, one positive and one negative previously identified partner,
all three detected on the SAME route-run. Fixed NWI-filter and exact fixed
row/column activity margins. Observational, post-selection; not a true
irreducible third-order interaction or causal competition/facilitation.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

ROOT=Path(__file__).resolve().parents[1]
SEED=2840301
B=199
BURN=40
THIN=8
Z=1.959963984540054
CENTRAL="Lithobates clamitans"
POSITIVE="Lithobates catesbeianus"
NEGATIVES=("Hyla versicolor","Anaxyrus fowleri")
TRIOS=tuple((CENTRAL,POSITIVE,n) for n in NEGATIVES)

def loadmodule(label,path):
    spec=importlib.util.spec_from_file_location(label,path)
    obj=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(obj)
    return obj

pairmod=loadmodule("same_run_frog_pair_ref",ROOT/"exploration/run_naamp_plant_conditioned_pair_network_v0_1.py")
prior=pairmod.prior

def synth():
    rows=[{0,2},{1,3},{0,3,4},{1,4,5},{2,5,6}]
    target=prior.fixed_margins(rows)
    rng=random.Random(SEED)
    values=[]
    for t in range(600):
        prior.weighted_trade(rows,np.zeros((len(rows),10)),rng)
        assert prior.fixed_margins(rows)==target
        if t%5==0:
            co=pairmod.cov_matrix(rows)
            values.append(float(co[0,1]-co[0,2]))
    assert np.ptp(values)>1e-4,"Paired two-edge contrast invariant under null"
    assert len(TRIOS)==2 and len({q[2] for q in TRIOS})==2
    return {"status":"PASS","same_matrix_partner_contrast_non_invariant":True,
            "all_species_and_site_margins_fixed":True}

def estimate(frame,column,min_runs=20,min_routes=10):
    if len(frame)<min_runs or frame.route.nunique()<min_routes:
        return {"status":"underpowered","n_runs":int(len(frame)),
                "n_routes":int(frame.route.nunique())}
    fit=sm.OLS(frame[column].to_numpy(float),np.ones((len(frame),1))).fit(
        cov_type="cluster",cov_kwds={"groups":frame.route.astype(str)})
    beta=float(fit.params[0]);se=float(fit.bse[0])
    return {"status":"fitted","beta":beta,"route_se":se,
            "ci95":[beta-Z*se,beta+Z*se],
            "p_two_sided":float(fit.pvalues[0]),
            "n_runs":int(len(frame)),"n_routes":int(frame.route.nunique())}

def folds(frame,column):
    return {str(f):{"n_runs":int(len(sub)),"n_routes":int(sub.route.nunique()),
                    "mean":float(sub[column].mean())}
            for f,sub in frame.groupby("fold")}

def leave_states(frame,column):
    if frame.State.nunique()<3:
        return {"status":"too_few_states","n_states":int(frame.State.nunique())}
    out=[]
    for state in sorted(frame.State.unique()):
        x=frame[frame.State!=state]
        fit=estimate(x,column,min_runs=20,min_routes=10)
        if fit["status"]=="fitted":
            out.append({"omit_state":str(state),"beta":fit["beta"],"ci95":fit["ci95"]})
    if not out:return {"status":"underpowered"}
    return {"status":"fitted","n_omit_states":len(out),
            "n_positive":sum(v["beta"]>0 for v in out),
            "n_positive_ci":sum(v["ci95"][0]>0 for v in out),
            "positive_fraction":sum(v["beta"]>0 for v in out)/len(out),
            "range_beta":[min(v["beta"] for v in out),max(v["beta"] for v in out)],
            "all":out}

def analyze_mode(mode,records,reference,coefficients,yearmap,outdir):
    if reference.RunID.duplicated().any():
        raise RuntimeError("Frozen reference contains duplicate RunID")
    rmap=reference.set_index("RunID")
    population=sorted(set(records)&set(rmap.index.astype(str)))
    expected=3659 if mode=="any" else 1766
    if len(population)!=expected:
        raise RuntimeError(f"Freeze violation: expected {expected} runs, got {len(population)}")
    n_valid=0
    n_nonmoving=0
    triad_records=defaultdict(list)
    for index,rid in enumerate(population,1):
        item=records[rid]
        taxa,rows=prior.ref_rows(item,mode)
        # Verify every frozen eligible study run, not only focal triad runs.
        obs_c=prior.cscore(rows)
        if not np.isclose(obs_c,float(rmap.loc[rid,"observed"]),atol=1e-8,rtol=0):
            raise RuntimeError("Frozen observed C-score mismatch "+rid)
        present=set(taxa)
        selected=[t for t in TRIOS if set(t).issubset(present)]
        if not selected:
            continue
        n_valid+=1
        tax_to_idx={name:i for i,name in enumerate(taxa)}
        scores=np.stack([
            np.asarray(coefficients[prior.complementary(item["fold"])].get(name,{})
              .get("wetland_and_emergent",np.zeros(2)),float) for name in taxa
        ])@item["v"][:,[0,1]].T
        current=[set(row) for row in rows]
        margins=prior.fixed_margins(current)
        seedbytes=hashlib.sha256(f"{SEED}|{mode}|{rid}".encode()).digest()[:8]
        rng=random.Random(int.from_bytes(seedbytes,"big"))
        feasible=accepted=0
        for k in range(BURN*len(taxa)):
            f,a=prior.weighted_trade(current,scores,rng)
            feasible+=f;accepted+=a
        observed=pairmod.cov_matrix(rows)
        labels={}
        chains={}
        for t in selected:
            name=t[2]
            i,j,k=(tax_to_idx[x] for x in t)
            labels[name]=(i,j,k)
            chains[name]={"CP":[],"CN":[],"D":[]}
        for b in range(B):
            for k in range(THIN*len(taxa)):
                f,a=prior.weighted_trade(current,scores,rng)
                feasible+=f;accepted+=a
            cm=pairmod.cov_matrix(current)
            for label,(i,j,k) in labels.items():
                x=float(cm[i,j]);y=float(cm[i,k])
                chains[label]["CP"].append(x)
                chains[label]["CN"].append(y)
                chains[label]["D"].append(x-y)
            if b in (0,B//2,B-1) and prior.fixed_margins(current)!=margins:
                raise RuntimeError("Weighted Curveball changed fixed margins")
        if not feasible or not accepted:
            n_nonmoving+=1
        for negative,(i,j,k) in labels.items():
            o_cp=float(observed[i,j]);o_cn=float(observed[i,k])
            chain=chains[negative]
            e_cp=o_cp-float(np.mean(chain["CP"]))
            e_cn=o_cn-float(np.mean(chain["CN"]))
            d=e_cp-e_cn
            # Labelled "partner-switch" means paired *association*, not a
            # change in a focal frog's behavior induced by another frog.
            triad_records[negative].append({
                "RunID":rid,"route":item["route"],"State":item["state"],
                "fold":item["fold"],"SurveyYear":int(yearmap[rid]),
                "CP_obs":o_cp,"CN_obs":o_cn,
                "CP_null_mean":float(np.mean(chain["CP"])),
                "CN_null_mean":float(np.mean(chain["CN"])),
                "CP_resid":e_cp,"CN_resid":e_cn,
                "D":d,
                "D_null_varies":bool(np.ptp(chain["D"])>1e-12),
                "PEM_fraction_range":float(np.ptp(item["v"][:,1])/10),
                "n_species_on_run":len(taxa),
                "null_accept_given_feasible":accepted/feasible
            })
        if index%600==0:
            print(f"{mode}: {index}/{len(population)} runs verified; {n_valid} qualifying same-run triads",flush=True)
    samples={"source_reference_matrices":len(population),
             "with_any_focal_trio":n_valid,
             "focal_runs_with_zero_accepted_moves":n_nonmoving}
    outcomes={}
    for negative in NEGATIVES:
        frame=pd.DataFrame(triad_records.get(negative,[]))
        if len(frame):
            frame.to_csv(outdir/f"{mode}_{negative.replace(' ','_')}_per_run.csv",index=False)
        name=" || ".join([CENTRAL,POSITIVE,negative])
        if frame.empty:
            outcomes[name]={"status":"no_common_survey_runs"}
            continue
        n=len(frame);nroute=int(frame.route.nunique());nondeg=int(frame.D_null_varies.sum())
        x={"species_trio":[CENTRAL,POSITIVE,negative],
           "n_same_run_triples":n,"n_routes":nroute,
           "n_states":int(frame.State.nunique()),
           "n_variably_randomizable":nondeg,
           "mean_PEM_cover_range":float(frame.PEM_fraction_range.mean()),
           "mean_weighted_trade_acceptance":float(frame.null_accept_given_feasible.mean()),
           "time":{"early_runs":int((frame.SurveyYear<=2009).sum()),
                   "late_runs":int((frame.SurveyYear>=2010).sum())}}
        x["eligibility"]="eligible" if n>=60 and nroute>=25 and nondeg>=20 else "insufficient_sample"
        x["summary"]={}
        for field in ["CP_resid","CN_resid","D"]:
            x["summary"][field]={"overall":estimate(frame,field,min_runs=60,min_routes=25),
                                 "folds":folds(frame,field),
                                 "early":estimate(frame[frame.SurveyYear<=2009],field),
                                 "late":estimate(frame[frame.SurveyYear>=2010],field)}
        x["LOO_State_D"]=leave_states(frame,"D")
        outcomes[name]=x
    eligible=[(name,x) for name,x in outcomes.items()
              if x.get("eligibility")=="eligible"]
    if eligible:
        p=[x["summary"]["D"]["overall"]["p_two_sided"] for _,x in eligible]
        qs=multipletests(p,alpha=.05,method="fdr_bh")[1]
        for (name,x),q in zip(eligible,qs):
            x["D_BH_q_two_fixed_trios"]=float(q)
            cp=x["summary"]["CP_resid"]["overall"]
            cn=x["summary"]["CN_resid"]["overall"]
            contrast=x["summary"]["D"]["overall"]
            f=x["summary"]["D"]["folds"]
            signed=bool(cp["status"]=="fitted" and cn["status"]=="fitted"
                and contrast["status"]=="fitted" and cp["ci95"][0]>0
                and cn["ci95"][1]<0 and contrast["ci95"][0]>0
                and q<.05 and f.get("A",{}).get("mean",0)>0
                and f.get("B",{}).get("mean",0)>0)
            x["supported_within_run_partner_contrast_candidate"]=signed
            x["year_strata_sign_consistent"]=bool(
                x["summary"]["D"]["early"]["status"]=="fitted"
                and x["summary"]["D"]["late"]["status"]=="fitted"
                and x["summary"]["D"]["early"]["ci95"][0]>0
                and x["summary"]["D"]["late"]["ci95"][0]>0)
            loo=x["LOO_State_D"]
            x["geographic_direction_stable"]=bool(
                loo["status"]=="fitted" and loo["positive_fraction"]>=.8)
    return {"mode":mode,"coverage":samples,"triads":outcomes}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-nwi",type=Path)
    parser.add_argument("--outdir",type=Path,default=ROOT/"build"/"same_run_partner_switch")
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    qa=synth()
    print("SAME_RUN_PARTNER_SYNTHETIC_QA",json.dumps(qa,sort_keys=True),flush=True)
    if args.synthetic_only:return
    if not args.frozen_nwi:
        raise RuntimeError("Original route-cross-fit NWI coefficients and run references required")
    records,refs,coefficients,source=pairmod.prior_inputs(args.frozen_nwi)
    m=loadmodule("same_run_date_source",
                 ROOT/"exploration/run_naamp_aquatic_vegetation_ecological_tests_v0_2.py")
    raw=m.hist.load_retry()
    runmeta,_=m.base.build_runs(raw)
    years=dict(zip(runmeta.RunID.astype(str),runmeta.SurveyYear.astype(int)))
    args.outdir.mkdir(parents=True,exist_ok=True)
    result={
      "analysis":"naamp_frog_partner_specific_same_run_site_contrast_v0_1",
      "status":"posthoc_identical_route_night_partner_comparison_not_causal",
      "contract":"exploration/NAAMP_SAME_RUN_PARTNER_SWITCH_CONTRACT_2026_10_21.md",
      "source_NWI_crossfit_run":39516056663,
      "source_NWI_full_overlay_run":39450277196,
      "source_existing_pair_BH_screen_run":39528330890,
      "frozen_species":TRIOS,
      "synthetic_QA":qa,
      "source_context":source,
      "settings":{"draws":B,"burn_per_taxon":BURN,"thin_per_taxon":THIN,"seed":SEED,
                  "same_10_stops_three_taxa_positive_somewhere":True,
                  "preserves_taxon_positive_stop_margins":True,
                  "preserves_stop_species_richness":True,
                  "route_crossfit_habitat_weights_unchanged":True},
      "modes":{}}
    for mode in ["any","strong"]:
        result["modes"][mode]=analyze_mode(mode,records,refs[mode],coefficients[mode],years,args.outdir)
    result["interpretation_boundary"]={
        "species_coactivation_measured_only_acoustically":True,
        "shared_route_night_does_not_imply_simultaneous_signaling":True,
        "triad_is_common_survey_comparison_not_higher_order_interaction":True,
        "original_first_order_NWI_trained_both_time_periods":True,
        "unmeasured_hydrological_and_predator_context_remains":True,
        "causal_biotic_interaction_inferred":False,
        "RC6_manuscript_and_submission_changed":False}
    (args.outdir/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SAME_RUN_PARTNER_RESULT_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("SAME_RUN_PARTNER_RESULT_END",flush=True)

if __name__=="__main__":
    main()
