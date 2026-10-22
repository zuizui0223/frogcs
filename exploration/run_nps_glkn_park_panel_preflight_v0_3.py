#!/usr/bin/env python3
"""Check 2016–2023 NPS GLKN park-specific recording taxon panels WITHOUT frog responses.

Source-only metadata columns are allowed; ManualCIV, SurveyorDetectedStatus,
SoftwareDetectedStatus and acoustic intensity metrics are neither opened nor
materialized. No original recording IDs, locations or raw audio are published.
"""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="b1c11cf70472a906e6c238a690a5a12373cdd20ef4d5e180fa3f376d520118c2"
SRC_BYTES=68581307
HEADER=["FileName","ParkCode","SiteLocation","StartTime","EventYear",
        "ScientificName","SpeciesCode","Hydroperiod","AvgTemperature_C"]
EVENT=["ParkCode","SiteLocation","FileName","StartTime"]
CENTRAL="Lithobates clamitans"
POSITIVE="Lithobates catesbeianus"
NEGATIVE=("Anaxyrus fowleri","Dryophytes versicolor")

def imp(path):
    sp=importlib.util.spec_from_file_location("nps_v02",path)
    module=importlib.util.module_from_spec(sp)
    assert sp.loader
    sp.loader.exec_module(module)
    return module

def main():
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--outdir",type=Path,default=ROOT/"build"/"nps_glkn_park_panel")
    cfg=a.parse_args()
    cfg.outdir.mkdir(parents=True,exist_ok=True)
    previous=imp(ROOT/"exploration/run_nps_glkn_independent_source_only_qa_v0_2.py")
    data,receipt=previous.source(previous.SRC["frog"]["url"],SRC_BYTES,
                                 previous.SRC["frog"]["max_bytes"],SOURCE_SHA)
    df=pd.read_csv(io.BytesIO(data),usecols=HEADER,low_memory=False,
                   dtype={col:"string" for col in HEADER if col!="AvgTemperature_C"})
    if len(df)!=147913:raise RuntimeError("NPS original recording×taxon row total drift")
    for name in HEADER:
        if name!="AvgTemperature_C":
            df[name]=df[name].str.strip()
    if df.duplicated(EVENT+["ScientificName"]).sum()!=0:
        raise RuntimeError("Original recording and species labels no longer unique")
    if df[EVENT+["ScientificName"]].isna().any().any():
        raise RuntimeError("Unexpected missing event or taxon identifier")
    # Group-by numeric species-row panel sizes only, not any acoustic outcomes.
    parkset=df.groupby("ParkCode").ScientificName.agg(lambda q:set(q)).to_dict()
    sitekeys=["ParkCode","SiteLocation"]
    siteset=df.groupby(sitekeys).ScientificName.agg(lambda q:set(q)).to_dict()
    events=df[EVENT+["EventYear","Hydroperiod","AvgTemperature_C"]].drop_duplicates(
        subset=EVENT).copy()
    if len(events)!=16561:raise RuntimeError("NPS number of recording files changed")
    if df.groupby(EVENT).Hydroperiod.nunique(dropna=False).max()>1:
        raise RuntimeError("Hydroperiod changes across taxa inside same recording")
    if df.groupby(EVENT).AvgTemperature_C.nunique(dropna=False).max()>1:
        raise RuntimeError("Average temperature changes across taxa inside same recording")
    per_event=df.groupby(EVENT).ScientificName.agg(lambda q: frozenset(q)).reset_index(name="taxa")
    per_event["park_target"]=[frozenset(parkset[park]) for park in per_event.ParkCode]
    per_event["site_target"]=[frozenset(siteset[(park,site)])
                              for park,site in zip(per_event.ParkCode,per_event.SiteLocation)]
    per_event["complete_park_panel"]=per_event.taxa==per_event.park_target
    per_event["complete_site_panel"]=per_event.taxa==per_event.site_target
    per_event["n_taxon_names"]=per_event.taxa.map(len)
    per_event["n_park_taxa"]=per_event.park_target.map(len)
    per_event["n_site_taxa"]=per_event.site_target.map(len)
    # No target species count is inferred from catalog '14'; all panels are
    # assembled from the independently verified taxon metadata rows.
    for n in [CENTRAL,POSITIVE]+list(NEGATIVE):
        per_event["has_"+n]=per_event.taxa.map(lambda x:n in x)
    pair=per_event[per_event["has_"+CENTRAL]&per_event["has_"+POSITIVE]].copy()
    trio={
      name:per_event[per_event["has_"+CENTRAL]&per_event["has_"+POSITIVE]&
                      per_event["has_"+name]]
      for name in NEGATIVE
    }
    events["date"]=events.StartTime.str.slice(0,10)
    year_ok=events.EventYear.astype(int).between(2016,2023)
    if not year_ok.all():raise RuntimeError("EventYear range differs from source")
    allpairs=pair.merge(events[EVENT+["date","EventYear","Hydroperiod",
                                      "AvgTemperature_C"]],on=EVENT,
                         how="left",validate="one_to_one")
    bysite=allpairs.groupby(sitekeys).size()
    byday=allpairs.groupby(sitekeys+["date"]).size()
    # Responding species are not yet known. Counting explicit taxon rows is
    # distinct from calculating their detected presence/absence.
    park_table={}
    for park,sub in per_event.groupby("ParkCode"):
        orig=parkset[str(park)]
        target=sub["has_"+CENTRAL]&sub["has_"+POSITIVE]
        withpair=sub[target]
        park_table[str(park)]={
            "site_count":int(sub.SiteLocation.nunique()),
            "recordings":int(len(sub)),
            "park_target_taxon_label_count":len(orig),
            "park_taxon_labels":sorted(orig),
            "complete_park_recordings":int(sub.complete_park_panel.sum()),
            "fraction_complete_park":float(sub.complete_park_panel.mean()),
            "complete_site_recordings":int(sub.complete_site_panel.sum()),
            "fraction_complete_site":float(sub.complete_site_panel.mean()),
            "named_pair_row_present_recordings":int(target.sum()),
            "named_pair_row_present_sites":int(withpair.SiteLocation.nunique()),
            "negative_candidate_row_present":{
                name:int((target&sub["has_"+name]).sum())
                for name in NEGATIVE}
        }
    record_byday_count=events.groupby(sitekeys+["date"]).size()
    site_status={
        str(p)+" / "+str(st):{
            "taxa_labels":len(species),
            "n_recordings":int(per_event[(per_event.ParkCode==p)&
                                          (per_event.SiteLocation==st)].shape[0])}
        for (p,st),species in siteset.items()
    }
    per_year=allpairs.groupby("EventYear").size()
    result={
       "analysis":"NPS_GLKN_recording_park_site_species_panel_source_only_v0_3",
       "contract":"exploration/NPS_GLKN_PARK_SPECIFIC_TAXON_PANEL_CONTRACT_V0_3.md",
       "source_sha256":receipt["sha256"],
       "source_bytes":receipt["n_bytes"],
       "original_taxon_rows":len(df),
       "original_recording_events":len(per_event),
       "n_distinct_park_site_locations":len(siteset),
       "taxa_labels_globally":sorted(set().union(*parkset.values())),
       "park_panels":park_table,
       "park_panel_completion_rate":float(per_event.complete_park_panel.mean()),
       "site_panel_completion_rate":float(per_event.complete_site_panel.mean()),
       "n_complete_park_panel_recordings":int(per_event.complete_park_panel.sum()),
       "n_complete_site_panel_recordings":int(per_event.complete_site_panel.sum()),
       "named_bullfrog_greenfrog_row_opportunities":{
            "recording_events":len(pair),
            "park_count":int(pair.ParkCode.nunique()),
            "park_site_count":int(pair[sitekeys].drop_duplicates().shape[0]),
            "site_days":int(len(byday)),
            "site_days_3plus_recordings":int((byday>=3).sum()),
            "site_days_6plus_recordings":int((byday>=6).sum()),
            "site_days_10plus_recordings":int((byday>=10).sum()),
            "events_in_3plus_same_site_date":int(byday[byday>=3].sum()),
            "n_frog_partner_species_rows_present_per_year":{
                str(k):int(v) for k,v in per_year.items()},
            "n_recordings_complete_park_panel":int(pair.complete_park_panel.sum()),
            "n_recordings_complete_site_panel":int(pair.complete_site_panel.sum()),
            "positive_row_pair_is_known_but_not_positive_call":True
        },
        "negative_partner_row_opportunities":{
            name:{
                "recordings":len(table),
                "site_count":int(table[sitekeys].drop_duplicates().shape[0]),
                "parks":int(table.ParkCode.nunique())
            }
            for name,table in trio.items()},
        "all_recordings_site_dates_3plus":int((record_byday_count>=3).sum()),
        "all_recordings_site_dates_6plus":int((record_byday_count>=6).sum()),
        "recording_environment":{
            "Hydroperiod_missing_frac":float(events.Hydroperiod.isna().mean()),
            "Hydroperiod_categories":[str(x) for x in sorted(
                events.Hydroperiod.dropna().unique().tolist())],
            "AvgTemperature_missing_frac":float(events.AvgTemperature_C.isna().mean()),
            "AvgTemperature_finite_frac":float(
                pd.to_numeric(events.AvgTemperature_C,errors="coerce").notna().mean()),
            "no_site_event_hydroperiod_disagreement":True},
        "park_site_taxon_panel_size_distribution":{
            str(i):sum(s["taxa_labels"]==i for s in site_status.values())
            for i in sorted(set(s["taxa_labels"] for s in site_status.values()))},
        "frozen_source_only_sample_gates":{
            "pair_1000_recording_events":len(pair)>=1000,
            "pair_at_least_20_park_site_locations":len(bysite)>=20,
            "pair_at_least_2_parks":pair.ParkCode.nunique()>=2,
            "pair_repeated_site_days_3plus_ge100":int((byday>=3).sum())>=100,
            "partner_rows_explicit_not_imputed":True,
            "source_SHA_verified":True
        },
        "occurrence_fields_read":False,
        "ManualCIV_values_read":False,
        "SurveyorDetectedStatus_values_read":False,
        "SoftwareDetectedStatus_values_read":False,
        "frozen_RC6_modified":False,
        "next_inference":"freeze outcome model only if park/site panel and named pair gates permit"
    }
    out=cfg.outdir/"nps_glkn_park_panel_source_only.json"
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("NPS_GLKN_PARK_PANEL_BEGIN",flush=True)
    print(json.dumps(result,sort_keys=True),flush=True)
    print("NPS_GLKN_PARK_PANEL_END",flush=True)

if __name__=="__main__":main()
