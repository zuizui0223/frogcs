#!/usr/bin/env python3
"""INBO Hyla arborea adult chorus -> subsequent larvae, exploratory frozen G1.

Frozen design: research/INBO_HYLA_ACOUSTIC_TO_LARVA_G1_FROZEN_2026-10-26.md
This script was written AFTER two response-blind G0 eligibility passes and
BEFORE checking occurrenceStatus. Original published source identities and
file checksums are unchanged. No trophic claim permitted.
"""
from __future__ import annotations
import argparse
import json
import math
import hashlib
from datetime import date
from io import BytesIO
from pathlib import Path
from collections import defaultdict, Counter
import zipfile
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from inbo_stage_taxon_g0 import SOURCES,part_rows
from part2_published_source_g0 import fetch
from xml.etree import ElementTree as ET

SPEC="research/INBO_HYLA_ACOUSTIC_TO_LARVA_G1_FROZEN_2026-10-26.md"
TAXON="Hyla arborea"
SEED=20261026

def require(pred,msg):
    if not pred:raise ValueError(msg)

def load(original):
    blob,content_type=fetch(original["url"])
    digest=hashlib.sha256(blob).hexdigest()
    require(digest==original["sha256"],"Original source checksum changed; abort")
    with zipfile.ZipFile(BytesIO(blob)) as zf:
        root=ET.fromstring(zf.read("meta.xml"))
        core=next(x for x in root if x.tag.rsplit("}",1)[-1]=="core")
        extension=[x for x in root if x.tag.rsplit("}",1)[-1]=="extension"]
        ev={}
        aliases=defaultdict(set)
        for row in part_rows(zf,core):
            eid=row.get("eventID") or row.get("sourceCoreID")
            site=row.get("locationID")
            try: d=date.fromisoformat((row.get("eventDate") or "")[:10])
            except ValueError:continue
            if not eid or not site:continue
            require(eid not in ev,"Duplicated event ID in source")
            ev[eid]=(site,d,row.get("locality","").strip().casefold())
            aliases[site].add(row.get("locality","").strip().casefold())
        occ=defaultdict(list)
        measurements=defaultdict(lambda:defaultdict(list))
        for ext in extension:
            iterator=iter(part_rows(zf,ext))
            sample=next(iterator,None)
            if sample is None:continue
            cols=set(sample)
            if "scientificName" in cols:
                def use(row):
                    if row.get("scientificName") != TAXON:return
                    eid=row.get("eventID") or row.get("linkedCoreID")
                    if eid not in ev:return
                    stage=row.get("lifeStage","").strip().casefold()
                    status=row.get("occurrenceStatus","").strip().casefold()
                    occ[eid].append((stage,status))
                use(sample)
                for row in iterator:use(row)
            elif "measurementType" in cols:
                def use(row):
                    eid=row.get("eventID") or row.get("linkedCoreID")
                    if eid not in ev:return
                    key=row.get("measurementType","").strip().casefold()
                    # This is a measured site covariate, NOT a frog response
                    val=row.get("measurementValue","").strip().casefold()
                    measurements[eid][key].append(val)
                use(sample)
                for row in iterator:use(row)
    return {"events":ev,"species_rows":dict(occ),
            "measurements":dict(measurements),"aliases":aliases,
            "sha256":digest, "source_event_count":len(ev)}

def binary(status):
    if status=="present":return 1
    if status=="absent":return 0
    return None

def unique_event_stage(rows,required_stage):
    values=[binary(st) for stage,st in rows if stage==required_stage and binary(st) is not None]
    if not values:return None
    if len(set(values))>1: return "conflict"
    return values[0]

def standard_measure(vals):
    vv={v for v in vals if v not in ("","unknown","na","n/a","onbekend")}
    if not vv:return None
    if len(vv)>1:return "conflict"
    return list(vv)[0]

def construct(ch,lr):
    aliases_a=ch["aliases"];aliases_l=lr["aliases"]
    shared=set(aliases_a)&set(aliases_l)
    valid_shared=set()
    locality_conflicts=0
    for site in shared:
        aa={x for x in aliases_a[site] if x}
        bb={x for x in aliases_l[site] if x}
        if len(aa)>1 or len(bb)>1 or (aa and bb and not aa.intersection(bb)):
            locality_conflicts+=1
        else:valid_shared.add(site)
    require(locality_conflicts==0,"Contradictory locality names for exact original IDs")
    a=defaultdict(list);l=defaultdict(list)
    for eid, (site,dt,name) in ch["events"].items():
        if site not in valid_shared:continue
        status=unique_event_stage(ch["species_rows"].get(eid,[]),"adult")
        if status=="conflict":continue
        if status is not None:a[(site,dt.year)].append((dt,eid,status))
    for eid,(site,dt,name) in lr["events"].items():
        if site not in valid_shared:continue
        status=unique_event_stage(lr["species_rows"].get(eid,[]),"larva")
        if status=="conflict":continue
        if status is not None:l[(site,dt.year)].append((dt,eid,status))
    out=[];discard=Counter()
    for key in sorted(set(a)&set(l)):
        site,year=key
        larval=sorted(l[key],key=lambda z:(z[0],z[1]))
        adults=sorted(a[key],key=lambda z:(z[0],z[1]))
        # first valid explicit larva census with at least one prior adult
        candidate=None;prior=[]
        for dt,eid,y in larval:
            earlier=[z for z in adults if z[0]<dt]
            if earlier:
                candidate=(dt,eid,y);prior=earlier;break
        if candidate is None:
            discard["no_adult_preceding_first_valid_larval_census"]+=1
            continue
        dt,eid,y=candidate
        known={z[2] for z in prior}
        if not known<=set([0,1]):discard["bad_adult_status"]+=1;continue
        water=lr["measurements"].get(eid,{})
        permanent=standard_measure(water.get("permanente waterkolom",[]))
        effort=standard_measure(water.get("sampling effort type",[]))
        if permanent=="conflict" or effort=="conflict":
            discard["contradictory_larval_site_covariates"]+=1;continue
        out.append({"site":site,"year":year,"year_day":dt.timetuple().tm_yday,
            "lag_days":(dt-max(z[0] for z in prior)).days,
            "n_adult_prior":len({z[1] for z in prior}),
            "x_any_chorus":int(any(z[2]==1 for z in prior)),
            "y_larval_record":y,
            "permanent_water":permanent,"effort_type":effort})
    return out,{"shared_site_ids":len(shared),"distinct_eligible_raw_site_year_rows":len(out),
                "discards":dict(discard),"locality_contradictions":locality_conflicts}

def safe_logscore(y,prob):
    p=np.clip(prob,1e-9,1-1e-9)
    return -(y*np.log(p)+(1-y)*np.log(1-p))

def compute_model(rows,config):
    y=np.array([r["y_larval_record"] for r in rows],int)
    X0=np.array([[r["year"],r["year_day"],r["lag_days"],r["n_adult_prior"]]
                 + ([1 if r["permanent_water"]=="true" else 0] if config["use_permanent"] else [])
                 for r in rows],float)
    X1=np.column_stack([X0,np.array([r["x_any_chorus"] for r in rows],float)])
    return X0,X1,y

def execute(rows,eligibility):
    out={"status":"NOT_ESTIMABLE","source_blind_eligibility":eligibility}
    x=np.array([r["x_any_chorus"] for r in rows],int)
    y=np.array([r["y_larval_record"] for r in rows],int)
    sites=np.array([r["site"] for r in rows])
    nsite=len(set(sites))
    raw_water_counts=Counter((r["permanent_water"] or "MISSING") for r in rows)
    raw_effort_counts=Counter((r["effort_type"] or "MISSING") for r in rows)
    out["site_environment_source_qa"]={
        "permanent_water_raw_labels":dict(sorted(raw_water_counts.items())),
        "larval_effort_category_labels":dict(sorted(raw_effort_counts.items())),
        "note":"Raw site-metadata category distribution at exact matched events; not outcome-selected"
    }
    out.update({"complete_case_site_years":len(rows),"independent_site_ids":nsite,
                "outcome_recorded_present":int(sum(y==1)),
                "outcome_recorded_absent":int(sum(y==0)),
                "prior_choir_recorded_present":int(sum(x==1)),
                "prior_choir_recorded_absent":int(sum(x==0)),
                "years":sorted({r["year"] for r in rows}),
                "simultaneous_measured_predator_stage":False,
                "true_larval_survival_recorded":False,
                "real_drought_drydown_recorded":False,
               })
    # Eligibility based on preregistered minimum counts (no threshold hunting).
    if (len(rows)<25 or nsite<15 or min(sum(y==1),sum(y==0))<10
        or min(sum(x==1),sum(x==0))<10):
        out["reason"]="FROZEN_MINIMUM_SURVEYED_BINARY_OUTCOME_OR_EXPOSURE_VARIATION_NOT_MET"
        return out
    permanent=[r["permanent_water"] for r in rows]
    possible=[z for z in permanent if z in ("true","false")]
    use_permanent=(len(possible)/len(rows)>=.85
                   and set(possible)=={"true","false"})
    config={"use_permanent":use_permanent,
       "permanent_water_coverage":float(len(possible)/len(rows)),
       "permanent_water_levels":sorted(set(possible)),
       "effort_type_observed_fraction":float(sum(r["effort_type"] is not None for r in rows)/len(rows)),
       "sampling_effort_numeric_measured":False}
    X0,X1,Y=compute_model(rows,config)
    prediction={}
    errors={}
    Group=GroupKFold(n_splits=5)
    for m,X in [("M0_time_hydrology_recording",X0),("M1_add_prior_chorus",X1)]:
        p=np.full(len(Y),np.nan)
        for train,test in Group.split(X,Y,sites):
            if len(set(Y[train]))<2:
                out["reason"]="SOME_HELDOUT_FOLD_TRAINING_OUTCOME_SINGLE_CLASS"
                out["design"]=config
                return out
            model=make_pipeline(StandardScaler(),LogisticRegression(
                C=1.,solver="lbfgs",max_iter=1000))
            model.fit(X[train],Y[train])
            p[test]=model.predict_proba(X[test])[:,1]
        require(np.isfinite(p).all(),"NaN out of site predictions")
        loss=safe_logscore(Y,p)
        brier=(Y-p)**2
        prediction[m]={
          "held_out_site_group_brier":float(np.mean(brier)),
          "held_out_site_group_logloss":float(np.mean(loss)),
          "probability_range":[float(np.min(p)),float(np.max(p))]
        }
        errors[m]={"brier":brier,"logloss":loss}
    diff=errors["M0_time_hydrology_recording"]["brier"]-errors["M1_add_prior_chorus"]["brier"]
    di2=errors["M0_time_hydrology_recording"]["logloss"]-errors["M1_add_prior_chorus"]["logloss"]
    unique=sorted(set(sites))
    arr=np.array([float(np.mean(diff[sites==s])) for s in unique])
    arr2=np.array([float(np.mean(di2[sites==s])) for s in unique])
    rng=np.random.default_rng(SEED)
    draws=rng.integers(0,len(unique),size=(2000,len(unique)))
    # Site-balanced bootstrap across whole location histories
    ci1=np.quantile(arr[draws].mean(axis=1),[.025,.975])
    ci2=np.quantile(arr2[draws].mean(axis=1),[.025,.975])
    out.update({
      "status":"EMPIRICAL_G1_FIT_EXPLORATORY","model_config":config,
      "models":prediction,
      "M1_minus_M0_heldout_BRIER_improvement_observation_weighted":float(np.mean(diff)),
      "M1_minus_M0_heldout_LOGLOSS_improvement_observation_weighted":float(np.mean(di2)),
      "site_equal_weight_bootstrap_CI95_BRIER_gain":[float(a) for a in ci1],
      "site_equal_weight_bootstrap_CI95_LOGLOSS_gain":[float(a) for a in ci2],
      "site_block_bootstrap_conditions":"2000 resamples of source-site mean OOF differences, not refitted",
      "note":"Same species cross-stage recorded call→larva, not wetland-specific trophic predation or larval survival."
    })
    recent=np.array([r["year"]>=2024 for r in rows])
    train=np.where(~recent)[0];test=np.where(recent)[0]
    if len(test)>=15 and len(set(Y[train]))==2 and len(set(Y[test]))==2 and len(set(sites[test]))>=10:
        hold={}
        for label,X in [("M0",X0),("M1",X1)]:
            model=make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=1000))
            model.fit(X[train],Y[train])
            pred=model.predict_proba(X[test])[:,1]
            hold[label]={"brier":float(np.mean((Y[test]-pred)**2)),
                         "logloss":float(np.mean(safe_logscore(Y[test],pred)))}
        out["temporal_2024_2025_validation"]={
          "estimable":True,"n_future_rows":int(len(test)),
          "n_future_distinct_sites":int(len(set(sites[test]))),"models":hold}
    else:
        out["temporal_2024_2025_validation"]={"estimable":False,
           "reason":"Holdout minimum 15 rows, >=10 sites and both outcome classes not met"}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    ch=load(SOURCES["adult_chorus"])
    la=load(SOURCES["larval_census"])
    rows,qa=construct(ch,la)
    result=execute(rows,qa)
    result.update({
      "source":"INBO Meetnetten.be original 2026 event DwC-A versions; CC0",
      "original_DOIs":["10.15468/d4bu8j","10.15468/swgure"],
      "prior_outcome_blind_frozen_spec":SPEC,
      "focal_taxon":TAXON,
      "comparison_species_Pelobates_fuscus":"NOT_ESTIMABLE_AT_G0_1_2_SITE_YEARS",
      "no_reanalysis_of_RC6":True,
      "raw_sensitive_location_ids_exported":False,
      "causal_stage_predation_interpretation":False,
      "reproduction_success_interpretation":False,
    })
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_INBO_HYLA_G1")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("END_INBO_HYLA_G1")
if __name__=="__main__":main()
