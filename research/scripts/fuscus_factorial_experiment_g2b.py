#!/usr/bin/env python3
"""Exploratory source-pinned experimental G2B: frog tadpole development.

Runs only after response-blind 2x2x2 assignment / bath nesting G0. The
biologically important prey-stage endpoints are metamorph mass/time conditional
on being reported and bounded survival under uncertain missing original rows.

Lab predator chemical cues are NOT observed animal consumption.
Lab drawdown is NOT actual field pond drying. Pseudoreplicated larval rows
are collapsed to containers for outcome fits; leave entire bath pools out
of prediction folds to honor nested thermal experimental units.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from fuscus_pinned_ooxml import original_source,decode,SOURCE_SHA256

ROOT=Path(__file__).resolve().parents[2]
G0=ROOT/"research/results/part2_g2/fuscus_assignment_g0.json"
SPEC="research/FUSCUS_EXPERIMENT_G2B_FROZEN_ANALYSIS_2026-10-26.md"
COLS=["Temperature","Pool","Predator","water_level","Nest",
      "Replicate","ID_tadpole","survival_G46","mass_46","time_to_46"]
SEED=20261026

def code(v):
    if v is None:return ""
    if isinstance(v,float) and v.is_integer():return str(int(v))
    return str(v).strip()

def num(v):
    if v is None or code(v).upper() in ("","NA","N/A","UNKNOWN","#N/A","-999"):return None
    try:
        n=float(v)
    except (TypeError,ValueError):
        return None
    return n if math.isfinite(n) else None

def assert_source_eligible(rows,receipt):
    assert receipt["source_sha256"]==SOURCE_SHA256
    assert receipt["data_rows"]==226
    assert receipt["distinct_individual_ids"]==226
    assert receipt["distinct_small_replicate_containers"]==79
    assert receipt["distinct_large_temperature_bath_pools"]==8
    assert receipt["containers_with_less_than_three_source_rows"]==10
    assert receipt["outcome_columns_read"] is False
    assert len(rows)==226

def prepare(rows):
    containers=defaultdict(list)
    unique=set()
    counts=Counter()
    errors=Counter()
    assignments={}
    observed_survival={}
    for r in rows:
        group=code(r["Replicate"])
        animal=code(r["ID_tadpole"])
        if not group or not animal or animal in unique:
            raise ValueError("Missing/duplicated original replicate or animal")
        unique.add(animal)
        temp=int(float(r["Temperature"]))
        pool=code(r["Pool"])
        predator=code(r["Predator"])
        water=code(r["water_level"])
        clutch=code(r["Nest"])
        if temp not in (30,35) or predator not in ("P","NP") or water not in ("DD","HW"):
            raise ValueError("Source factorial assignments invalid")
        state=(temp,pool,predator,water,clutch)
        if group in assignments and assignments[group]!=state:
            raise ValueError("Treatment confounded within same replicate")
        assignments[group]=state
        arm=(temp,predator,water)
        counts[arm]+=1
        surv=num(r.get("survival_G46"))
        if surv is None: errors["survival_unknown_or_empty"]+=1
        elif surv not in (0,1):
            raise ValueError("Source binary survival value outside 0/1: "+str(surv))
        else:
            observed_survival[arm, int(surv)]+=1
        mass=num(r.get("mass_46"))
        time=num(r.get("time_to_46"))
        if mass is None:errors["mass46_missing"]+=1
        elif mass<=0:
            raise ValueError("Metamorph mass must be positive")
        if time is None:errors["time46_missing"]+=1
        elif time<=0 or time>500:
            raise ValueError("Time-to-G46 invalid")
        if surv==0 and mass is not None:
            errors["mass_recorded_despite_zero_survival"]+=1
        if surv==0 and time is not None:
            errors["time_recorded_despite_zero_survival"]+=1
        containers[group].append({"state":state,"animal":animal,"survival":surv,
                                  "mass":mass,"time":time})
    if len(containers)!=79:raise ValueError("Source container count drift")
    return containers,counts,observed_survival,errors

def bounded_survival(counts,survival,errors):
    report=[]
    for temp in (30,35):
        for pred in ("P","NP"):
            for water in ("HW","DD"):
                arm=(temp,pred,water)
                obs=counts.get(arm,0)
                yes=survival.get((arm,1),0)
                no=survival.get((arm,0),0)
                if obs>30 or yes+no>obs:raise ValueError("Factorial arm over 30 or double scored")
                unknown=obs-yes-no
                absent=30-obs
                report.append({
                    "temperature_C":temp,"predator_cue":pred,"water_level":water,
                    "planned_initial_tadpoles":30,
                    "rows_in_public_workbook":obs,
                    "observed_survival_one":yes,"observed_survival_zero":no,
                    "missing_survival_status_in_observed_rows":unknown,
                    "unlisted_planned_animals":absent,
                    "missing_as_dead_lower_sensitivity":yes/30,
                    "missing_as_survived_upper_sensitivity":(yes+unknown+absent)/30,
                    "cannot_treat_missing_as_death_without_source_verification":True
                })
    return report

def aggregate_containers(containers,key):
    collected=[];allmissing=Counter()
    for rid,animals in containers.items():
        state=animals[0]["state"]
        temp,pool,pred,water,clutch=state
        if key=="mass":
            vals=[z["mass"] for z in animals if z["survival"]==1 and z["mass"] is not None]
        else:
            vals=[z["time"] for z in animals if z["survival"]==1 and z["time"] is not None]
        if not vals:
            allmissing["no_observed_survivor_with_endpoint"]+=1
            continue
        collected.append({
            "replicate":rid, "bath":pool,"temp":temp,
            "pred":int(pred=="P"),"dry":int(water=="DD"),
            "clutch":clutch,"value":float(np.mean(vals)),
            "survivors_with_endpoint":len(vals)
        })
    return collected,dict(allmissing)

def design(dat,mode):
    clutches=sorted(set(z["clutch"] for z in dat))
    if len(clutches)!=3:raise ValueError("Expected three source nests/clutches")
    mat=[]
    for d in dat:
        row=[float(d["temp"]==35),float(d["dry"])]
        row+=[float(d["clutch"]==cc) for cc in clutches[:-1]]
        if mode in ("M1","M2"):row.append(float(d["pred"]))
        if mode=="M2":row.append(float(d["pred"]*d["dry"]))
        mat.append(row)
    return np.array(mat,float)

def lobo_one(dat):
    groups=np.array([d["bath"] for d in dat])
    bath_ids=sorted(set(groups))
    if len(bath_ids)!=8:
        return {"estimable":False,"reason":"Not all eight independent temperature baths represented"}
    yraw=np.array([d["value"] for d in dat],float)
    if np.min(yraw)<=0:return {"estimable":False,"reason":"Nonpositive endpoint in source"}
    y=np.log(yraw)
    logo=LeaveOneGroupOut()
    metrics={}
    err={}
    for name in ("M0","M1","M2"):
        X=design(dat,name)
        pred=np.full(len(y),np.nan)
        for train,test in logo.split(X,y,groups):
            model=make_pipeline(StandardScaler(),Ridge(alpha=10.0))
            model.fit(X[train],y[train])
            pred[test]=model.predict(X[test])
        if not np.isfinite(pred).all():raise ValueError("Missing bath-heldout result")
        errs=(y-pred)**2
        vals=np.array([float(np.mean(errs[groups==b])) for b in bath_ids])
        metrics[name]={
            "n_test_containers":len(dat),
            "bath_equal_weight_LOBO_MSE_log_endpoint":float(np.mean(vals)),
            "container_weighted_LOBO_MSE_log_endpoint":float(np.mean(errs)),
        }
        err[name]=vals
    rng=np.random.default_rng(SEED+len(dat))
    draws=rng.integers(0,len(bath_ids),size=(2000,len(bath_ids)))
    outcomps={}
    for a,b in [("M1","M0"),("M2","M1"),("M2","M0")]:
        diff=err[b]-err[a]
        bt=diff[draws].mean(axis=1)
        outcomps[a+"_vs_"+b]={
           "positive_is_addition_improves_MSE":True,
           "bath_balanced_MSE_gain":float(np.mean(diff)),
           "bootstrap_95ci_conditional_on_fixed_LOBO_models":[float(x) for x in np.quantile(bt,[.025,.975])],
           "n_independent_thermal_baths":len(bath_ids),
           "bootstrap_repetitions":2000,
        }
    return {
       "estimable":True,"models":metrics,"contrasts":outcomps,
       "metric":"squared error on log(container mean measured survivor phenotype)",
       "heldout_group":"original 400-L experimental temperature bath",
       "ridge_alpha_fixed":10,
    }

def group_means(dat):
    groups=defaultdict(list)
    for d in dat:
        groups[(d["temp"],d["pred"],d["dry"])].append(d["value"])
    cells=[]
    for temp in (30,35):
      for pred in (0,1):
        for dry in (0,1):
            xs=groups.get((temp,pred,dry),[])
            cells.append({"temperature_C":temp,"predator_cue_present":bool(pred),
                          "drydown":bool(dry),"n_independent_small_containers":len(xs),
                          "mean_measured_survivor_container_endpoint":float(np.mean(xs)) if xs else None})
    contrasts=[]
    for temp in (30,35):
        def mean(pred,dry):
            vals=groups[(temp,pred,dry)]
            return float(np.mean(vals)) if vals else math.nan
        if all(groups[(temp,p,d)] for p in (0,1) for d in (0,1)):
            contrasts.append({
                "temperature_C":temp,
                "cue_effect_drydown":mean(1,1)-mean(0,1),
                "cue_effect_highwater":mean(1,0)-mean(0,0),
                "difference_in_difference_raw_units":(mean(1,1)-mean(0,1))-(mean(1,0)-mean(0,0)),
                "observational_survivors_only_unadjusted":True,
            })
    return cells,contrasts

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    receipt=json.loads(G0.read_text(encoding="utf-8"))
    cols,rows=decode(original_source(),COLS)
    assert_source_eligible(rows,receipt)
    containers,counts,survival,errors=prepare(rows)
    bounds=bounded_survival(counts,survival,errors)
    outcome={}
    for endpoint in ("mass","time"):
        cont,missing=aggregate_containers(containers,endpoint)
        cell_means,cell_did=group_means(cont)
        outcome[endpoint]={
           "n_containers_with_measured_survivor_endpoint":len(cont),
           "n_survivor_measurements":sum(x["survivors_with_endpoint"] for x in cont),
           "missing_small_containers":missing,
           "source_factorial_cell_means":cell_means,
           "within_temperature_Pcue_x_water_difference_in_difference":cell_did,
           "leave_entire_thermal_bath_out":lobo_one(cont),
           "selection_on_surviving_stage":"These are survivors with observed metamorphs, NOT all allocated larvae",
        }
    report={
       "status":"REAL_FACTORIAL_OBSERVATION_REANALYSIS_POST_PUBLICATION",
       "source_dataset":"CSIC 10261/411885, Delgadillo-Mendez et al. 2025, CC BY 4.0",
       "source_SHA256":SOURCE_SHA256,
       "protocol":SPEC,
       "source_design":"2 temperatures x 2 water regimes x 2 predator cues, three original nests/clutches",
       "experimentally_exposed_predator":"CHEMICAL_CUE_ONLY_NOT_CONSUMPTION",
       "experimental_drawdown":"CONTROLLED_WATER_LEVEL_NOT_FIELD_WETLAND_DROUGHT",
       "n_original_expected_allocation":240,
       "n_observed_individual_rows":len(rows),
       "unlisted_planned_individuals":240-len(rows),
       "intended_small_containers":80,
       "observed_small_containers":len(containers),
       "thermal_bath_groups":8,
       "source_binary_survival_qc":{
          "recorded_true":sum(v for (arm,s),v in survival.items() if s==1),
          "recorded_false":sum(v for (arm,s),v in survival.items() if s==0),
          "recorded_unknown":errors.get("survival_unknown_or_empty",0),
          "source_rows":len(rows),
       },
       "recorded_treatment_survival_bounds":bounds,
       "individual_stage_trait_qa":dict(errors),
       "survivor_conditional_endpoint_models":outcome,
       "real_causal_pond_predation_identified":False,
       "real_persistent_overwintered_larval_population_identified":False,
       "hydroperiod_x_predator_stage_attack_identified":False,
       "RC6_untouched":True,
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_FUSCUS_G2B_REAL_EXPERIMENT")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    print("END_FUSCUS_G2B_REAL_EXPERIMENT")

if __name__=="__main__":
    main()
