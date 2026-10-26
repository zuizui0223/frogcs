#!/usr/bin/env python3
"""Observed cross-stage seasonal timing + rainfall/plant correlations.

Two real independently observed settings:
 (i) Hungary 2024 same sampled wetland dates, acoustic frog detection,
     source recorded precipitation, fixed emergent/submerged cover and depth;
 (ii) exact original INBO locationID chorus surveys and anuran/newt larvae
     sampled on subsequent calendar dates (source stage labelled).

Correlations are descriptive and post-publication exploratory: not causation,
not metamorph survival, not within-site plant emergence, not competition.
Raw private source IDs retained IN MEMORY only. No raw records copied.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
from datetime import date
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd

from hungary_vegetation_chorus import load_data,FROGS
from inbo_stage_taxon_g0 import SOURCES,part_rows
from part2_published_source_g0 import fetch
from gbif_inbo_event_g3_blind import ANURA_NAMES,CAUDATA_NAMES,stage

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/external/zenodo_15044115"
SEED=20261026

def rho(a,b):
    if len(a)<3 or len(b)<3 or len(set(a))<2 or len(set(b))<2:
        return None
    x=pd.Series(a,dtype=float).rank(method="average").to_numpy()
    y=pd.Series(b,dtype=float).rank(method="average").to_numpy()
    z=float(np.corrcoef(x,y)[0,1])
    return z if math.isfinite(z) else None

def perc_ci(samples):
    if len(samples)<25:return None
    return [float(np.quantile(samples,.025)),float(np.quantile(samples,.975))]

def bootstrap_site_spearman(tbl,unitcol,xcol,ycol,n=1000):
    sites=list(tbl[unitcol].unique())
    rng=np.random.default_rng(SEED+len(tbl))
    original=rho(tbl[xcol].tolist(),tbl[ycol].tolist())
    vals=[]
    source={i:tbl[tbl[unitcol]==i] for i in sites}
    for _ in range(n):
        ids=rng.choice(sites,size=len(sites),replace=True)
        rec=pd.concat([source[i] for i in ids],ignore_index=True)
        z=rho(rec[xcol].tolist(),rec[ycol].tolist())
        if z is not None:vals.append(z)
    return {"descriptive_spearman_r":original,
            "source_units":len(sites),"observations":len(tbl),
            "site_bootstrap_ci95_conditional":perc_ci(vals),
            "successful_bootstrap_draws":len(vals),
            "causal_interpretation_permitted":False}

def hungary():
    sites,visits,joined=load_data(SOURCE)
    audio=joined.loc[joined.method=="acoustic"].copy().reset_index(drop=True)
    assert len(audio)==129 and audio.site.nunique()==29
    audio["date"]=pd.to_datetime(audio["date"])
    audio["frog_any_source"]=(audio[FROGS]>0).any(axis=1).astype(int)
    assert np.array_equal(audio["frog_any_source"],audio["frog_any"].astype(int))
    date_summary=audio.groupby("date",as_index=False).agg(
        n_wetlands=("site","nunique"),
        rainy_covariate_mean=("prec","mean"),
        acoustic_frog_fraction=("frog_any","mean"))
    site=audio.groupby("site",as_index=False).agg(
        n_audio_visits=("frog_any","size"),
        p_call_report=("frog_any","mean"),
        cover_emerged=("cover_emerged","first"),
        cover_submers=("cover_submers","first"),
        depth=("depth","first"),
        restoration_class=("ci","first"),
        first_observed_acoustic_doy=("doy","min"),
        measured_rain_mean=("prec","mean"))
    correlations={}
    for term in ("cover_emerged","cover_submers","depth"):
        correlations["source_site_call_fraction_vs_"+term]=bootstrap_site_spearman(
            site,"site",term,"p_call_report",n=1000)
    # Acoustic visit rain as an observed exposure; bootstrap entire sites.
    correlations["visit_call_report_vs_rain"]=bootstrap_site_spearman(
        audio,"site","prec","frog_any",n=1000)
    # Date-level rain and frog fraction: one seasonal survey day is a unit.
    correlations["date_frog_fraction_vs_rain"]={
      "descriptive_spearman_r":rho(date_summary.rainy_covariate_mean,
                                   date_summary.acoustic_frog_fraction),
      "independent_observed_calendar_dates":int(len(date_summary)),
      "observational_confounding":"DOY/field schedule/temperature; not rainfall manipulation"
    }
    # Basic seasonality and site-mean weather, no plant emergence recording.
    month=audio.groupby(audio.date.dt.month,as_index=True).agg(
        visits=("site","size"),
        observed_frog_calls=("frog_any","sum"),
        sites=("site","nunique"),
        mean_field_prec=("prec","mean"))
    months={}
    for m,z in month.iterrows():
        months[str(int(m))]={
          "survey_events":int(z["visits"]),
          "frog_call_detected_events":int(z["observed_frog_calls"]),
          "surveyed_wetland_sites":int(z["sites"]),
          "prec_mean_over_sampled_events":float(z["mean_field_prec"]),
          "frog_call_fraction_surveyed_events":float(z["observed_frog_calls"]/z["visits"]),
        }
    # Source taxon detectability: not strong CI or breeding pulse.
    taxa_reported={sp:int((audio[sp]>0).sum()) for sp in FROGS}
    return {
      "source":"HUNGARY_2024","record_grain":"actual wetland×dated acoustic observation, stage=adult_call report",
      "n_wetland_sites":int(site.shape[0]),
      "n_acoustic_surveys":len(audio),
      "n_distinct_days":int(len(date_summary)),
      "frogs_positive_survey_count":int(audio.frog_any.sum()),
      "sufficient_multi_site_dates_3plus":int((date_summary.n_wetlands>=3).sum()),
      "calendar_months":months,
      "taxa_call_report_counts":taxa_reported,
      "site_and_date_exploratory_correlations":correlations,
      "plant_emergence_dates_measured":False,
      "individual_shelter_use_measured":False,
      "only_once_site_plant_coverage_measured":True,
      "water_depth_measured_not_permanence":True,
      "source_plant_covariates_pct":["cover_emerged","cover_submers"],
      "strong_chorus_intensity_measured":False,
      "rain_variable_not_naamp_72h":True,
      "all_raw_source_site_IDs_withheld":True,
    }

def read_inbo(tag):
    info=SOURCES[tag]
    binary,_=fetch(info["url"])
    assert hashlib.sha256(binary).hexdigest()==info["sha256"],"Original source drift"
    with zipfile.ZipFile(BytesIO(binary)) as z:
        root=ET.fromstring(z.read("meta.xml"))
        core=next(x for x in root if x.tag.rsplit("}",1)[-1]=="core")
        ext=[x for x in root if x.tag.rsplit("}",1)[-1]=="extension"]
        events={}; aliases=defaultdict(set)
        for r in part_rows(z,core):
            eid=r.get("eventID") or r.get("sourceCoreID")
            site=r.get("locationID")
            try:dt=date.fromisoformat((r.get("eventDate") or "")[:10])
            except ValueError:continue
            if eid and site:
                assert eid not in events
                events[eid]=(site,dt)
                aliases[site].add((r.get("locality") or "").strip().lower())
        observed=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
        conflicting=0
        for node in ext:
            rows=iter(part_rows(z,node))
            sample=next(rows,None)
            if sample is None or "scientificName" not in sample:continue
            for r in [sample]+list(rows):
                eid=r.get("eventID") or r.get("linkedCoreID")
                if eid not in events:continue
                sp=(r.get("scientificName") or "").strip()
                original_stage=stage(r.get("lifeStage"))
                state=(r.get("occurrenceStatus") or "").strip().lower()
                if state not in ("present","absent"):continue
                site,dt=events[eid]
                if tag=="adult_chorus":
                    if sp!="Hyla arborea":continue
                    label="hyla_adult_call"
                else:
                    if original_stage!="aquatic_immature":continue
                    if sp=="Hyla arborea":label="hyla_larva"
                    elif sp in CAUDATA_NAMES:label="caudata_larva"
                    elif sp in ANURA_NAMES:label="other_anuran_larva"
                    else:continue
                observed[label][(site,dt.year)][(eid,dt)].add(state)
    return {"states":observed,"aliases":aliases,"conflicts":conflicting,
            "source_sha256":info["sha256"]}

def inbo():
    call=read_inbo("adult_chorus")
    aquatic=read_inbo("larval_census")
    shared=set(call["aliases"])&set(aquatic["aliases"])
    safe=set()
    for site in shared:
        a={x for x in call["aliases"][site] if x}
        b={x for x in aquatic["aliases"][site] if x}
        if not a or not b or a&b:safe.add(site)
    assert len(safe)==96,"Original source locality mapping changed"
    # Positive rows only for first-observed phenophase, surveyed status kept
    # separately. Earliest of different date surveys may be different individuals.
    available={}
    for label,src in [("hyla_adult_call",call),("hyla_larva",aquatic),
                      ("caudata_larva",aquatic),
                      ("other_anuran_larva",aquatic)]:
        dic={}
        for (site,yr),events in src["states"][label].items():
            if site not in safe:continue
            # Other-anuran/Caudata guilds naturally contain mixed species
            # detections in one event; some species absent while others present
            # is NOT a contradictory survey result. A guild is positive when
            # at least one constituent taxon is explicitly present.
            ambiguous=[(eid,dt) for (eid,dt),ss in events.items()
                       if len(ss)>1 and label in ("hyla_adult_call","hyla_larva")]
            valid={k:ss for k,ss in events.items() if k not in ambiguous}
            pos=sorted(dt for (eid,dt),ss in valid.items() if "present" in ss)
            all_days=sorted(dt for eid,dt in valid)
            dic[(site,yr)]={"positives":pos,"sampled":all_days}
        available[label]=dic
    head=available["hyla_adult_call"]
    baseline={"site_year_chorus_assessed":len(head),
              "distinct_chorus_assessed_sites":len({s for s,y in head}),
              "source_exact_locations_shared":len(safe)}
    timing={}
    for stage_name in ("hyla_larva","caudata_larva","other_anuran_larva"):
        pairs=[]
        opportunities=0
        for (site,yr),source in head.items():
            tar=available[stage_name].get((site,yr))
            if tar is None:continue
            opportunities+=1
            if source["positives"] and tar["positives"]:
                call_dt=source["positives"][0]
                stage_dt=tar["positives"][0]
                pairs.append({"site":site,"year":yr,"call_doy":call_dt.timetuple().tm_yday,
                    "larva_doy":stage_dt.timetuple().tm_yday,
                    "lag_days_first_recorded_larva_minus_first_recorded_call":(stage_dt-call_dt).days,
                    "same_calendar_month":call_dt.month==stage_dt.month,
                    "surveyed_chorus_times":len(source["sampled"]),
                    "surveyed_stage_times":len(tar["sampled"])})
        ages=[p["lag_days_first_recorded_larva_minus_first_recorded_call"] for p in pairs]
        if pairs:
            df=pd.DataFrame(pairs)
            by_year=Counter(p["year"] for p in pairs)
            correlation=bootstrap_site_spearman(df,"site","call_doy","larva_doy",n=1000)
            lag_summ={
                "first_record_lag_median_days":float(np.median(ages)),
                "first_record_lag_quartiles_days":[float(x) for x in np.quantile(ages,[.25,.75])],
                "first_record_lag_minmax_days":[int(min(ages)),int(max(ages))],
                "n_larval_first_positive_after_call_first_positive":int(sum(x>0 for x in ages)),
                "n_larval_first_positive_same_day":int(sum(x==0 for x in ages)),
                "n_larval_first_positive_before_call_first_positive":int(sum(x<0 for x in ages)),
                "same_calendar_month_fraction_among_positive_both":float(np.mean([p["same_calendar_month"] for p in pairs])),
                "first_call_vs_larval_first_positive_DOY_correlation":correlation,
                "year_coverage":{str(y):n for y,n in sorted(by_year.items())},
            }
        else:lag_summ={}
        timing[stage_name]={
            "site_years_with_both_stage_sampling_opportunities":opportunities,
            "site_years_with_positive_reports_in_both_stage_methods":len(pairs),
            "distinct_source_sites_of_positive_pairs":len({x["site"] for x in pairs}),
            "two_stages_are_same_species" if stage_name=="hyla_larva" else "related_taxa_not_verified_trophic":True,
            "seasonal_first_report_summary":lag_summ,
            "same_calendar_month_report_does_not_prove_trophic_encounter":True,
        }
    # Paired within same site-year larval phenologies, distinct from adult calls
    shared_three=set(head)&set(available["hyla_larva"])&set(available["caudata_larva"])
    measured=[]
    for key in shared_three:
        a=head[key]["positives"];f=available["hyla_larva"][key]["positives"];c=available["caudata_larva"][key]["positives"]
        if a and f and c:
            measured.append((f[0]-a[0]).days-(c[0]-a[0]).days)
    out={
        "source":"INBO_CHORUS x INBO_LARVA",
        "source_original_dataset_doI":["10.15468/d4bu8j","10.15468/swgure"],
        "original_source_sha256":[call["source_sha256"],aquatic["source_sha256"]],
        "support":"exact publisher source location ID × year, not NAAMP stop or photo grid",
        "date_based_seasonal_stages_from_actual_surveyed_reports":True,
        "calendar_climate_or_water_effects_not_jointly_measured":True,
        "base":baseline,"phenology":timing,
        "source_site_years_with_all_three_stage_survey_opportunities":len(shared_three),
        "all_three_source_positive_site_years":len(measured),
        "difference_first_hyla_larva_vs_first_caudata_larva_median_days":(
            float(np.median(measured)) if measured else None),
        "numeric_Gosner_or_predator_vs_prey_size_measured":False,
        "emergent_vegetation_phenophase_measured":False,
        "true_survival_or_direct_predation_measured":False,
        "raw_original_site_identifiers_disclosed":False,
        "interpretation":"first detections vs known survey times, phenological co-reporting not true onset, no measured feeding/competition",
    }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    report={
        "status":"REAL_WITHIN_SOURCE_ASSOCIATION_AND_STAGE_PHENOLOGY_EXPLORATORY",
        "report_date":"2026-10-26",
        "hungary":hungary(),
        "inbo":inbo(),
        "no_cross_source_pseudo_pond_join":True,
        "no_inference_of_actual_vegetation_emergence_or_shelter_use":True,
        "no_causal_predation_or_interference_claim_authorized":True
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_FROGCS_SEASONAL_CORRELATIONS_V1")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("END_FROGCS_SEASONAL_CORRELATIONS_V1")

if __name__=="__main__":
    main()
