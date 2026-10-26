#!/usr/bin/env python3
"""One comparable source×calendar-month×taxon×stage×method observation view.

Source-backed, no inferred pond joins. Original source site keys are kept
IN MEMORY only, then discarded; only aggregate counts and source metadata
are written. Original frozen NAAMP is never refit. GBIF 1-degree reports,
NPS annually scored stations and source literature network edges retain
separate observation SUPPORT classes in the registry, never masquerading
as co-monitored INBO ponds.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import csv
from datetime import date
import hashlib
from io import BytesIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile

from inbo_stage_taxon_g0 import SOURCES,part_rows
from part2_published_source_g0 import fetch

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"research/external/zenodo_15044115"
REGISTRY=ROOT/"research/comparable_db/SOURCE_REGISTRY_V1.json"
HUN_MD5={
 "wetland_amp_site_data.csv":"795da443249760fbc0bf30249910a4ef",
 "wetland_amp_surv_data.csv":"edcd6f12518192c01e3dbae8521c16c9",
}
FROGS=["Pelobates fuscus","Rana dalmatina","Bombina bombina","Hyla arborea",
       "Pelophylax ridibundus","Bufotes viridis","Bufo bufo"]
NEWTS=["Lissotriton vulgaris","Triturus dobrogicus"]

def require(ok,why):
    if not ok:raise ValueError(why)

def read_frozen_csv(name):
    path=DATA/name
    require(hashlib.md5(path.read_bytes()).hexdigest()==HUN_MD5[name],
            "Original Hungary source digest drift")
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def normal_stage(raw,from_chorus=False):
    if from_chorus:return "adult_call"
    x=(raw or "").strip().casefold()
    return {"adult":"adult","larva":"larva","larvae":"larva",
            "tadpole":"larva","egg":"egg","metamorph":"metamorph",
            "juvenile":"juvenile"}.get(x,"unknown")

def create_accumulator():
    return defaultdict(lambda:{"events":set(),"sites":set(),
                                "presence_events":set(),"absent_events":set(),
                                "unassessed_events":set(),
                                "rain_values":{},"emergent_values":{},
                                "depth_values":{}})

def add(group,source,year,month,taxon,stage,method,site,event_id,status,
        rain=None,emergent=None,depth=None):
    k=(source,year,month,taxon,stage,method)
    g=group[k]
    eid=(site,event_id)
    g["events"].add(eid);g["sites"].add(site)
    if status=="present":g["presence_events"].add(eid)
    elif status=="absent_explicit":g["absent_events"].add(eid)
    else:g["unassessed_events"].add(eid)
    for val,field in [(rain,"rain_values"),(emergent,"emergent_values"),(depth,"depth_values")]:
        if val is not None:g[field][eid]=float(val)

def ingest_hungary(group):
    sites=read_frozen_csv("wetland_amp_site_data.csv")
    visits=read_frozen_csv("wetland_amp_surv_data.csv")
    smap={x["site"]:x for x in sites}
    require(len(smap)==29 and len(visits)==381,
            "Hungary source counts drift")
    seen=set()
    for i,r in enumerate(visits):
        site=r["site"]
        require(site in smap,"No wetland habitat site match")
        try:time=date.fromisoformat(r["date"])
        except ValueError:raise ValueError("Invalid Hungary survey date")
        method=r["method"]
        require(method in {"acoustic","visual","dipnet","bottletrap"},
                "Unknown Hungary method")
        ev_id=r.get("surv") or f"original_row_{i+1}"
        # Some source survey_id may recur across methods. Composite with original
        # position prevents accidental cross-method event mergers.
        ev_key=f"{ev_id}:{i+1}"
        for taxon in FROGS+NEWTS:
            raw=r.get(taxon)
            require(raw is not None and raw.strip()!="",
                    "Source method reported empty species cell, not an explicit zero")
            try:n=float(raw)
            except ValueError:raise ValueError("Invalid native Hungary species score")
            require(n>=0,"Negative species observation")
            stage="adult_call" if method=="acoustic" else "method_stage_unknown"
            status="present" if n>0 else "absent_explicit"
            info=smap[site]
            add(group,"HUNGARY_2024",time.year,time.month,taxon,stage,method,site,
                ev_key,status,
                rain=r["prec"],emergent=info["cover_emerged"],depth=info["depth"])
    return {"native_sites":29,"native_visits":381,
            "country":"Hungary","years":[2024],
            "methods":["acoustic","visual","dipnet","bottletrap"],
            "stage_scope":"other survey methods did NOT distinguish larva from adult, never infer aquatic immature"}

def ingest_inbo(group,tag,source_id):
    ref=SOURCES[tag]
    binary,ctype=fetch(ref["url"])
    require(hashlib.sha256(binary).hexdigest()==ref["sha256"],
            "Original INBO DwC-A zip digest drift: "+source_id)
    with zipfile.ZipFile(BytesIO(binary)) as z:
        root=ET.fromstring(z.read("meta.xml"))
        core=next(n for n in root if n.tag.rsplit("}",1)[-1]=="core")
        extensions=[n for n in root if n.tag.rsplit("}",1)[-1]=="extension"]
        events={}
        for e in part_rows(z,core):
            eid=e.get("eventID") or e.get("sourceCoreID")
            site=e.get("locationID")
            try:dt=date.fromisoformat((e.get("eventDate") or "")[:10])
            except (ValueError,TypeError):continue
            if eid and site:
                require(eid not in events,"Duplicate original event id")
                events[eid]=(site,dt)
        observed=0;unknown=0;assessed=0
        for ext in extensions:
            rows=iter(part_rows(z,ext))
            first=next(rows,None)
            if first is None or "scientificName" not in first:continue
            for rec in [first]+list(rows):
                eid=rec.get("eventID") or rec.get("linkedCoreID")
                if eid not in events:continue
                taxon=(rec.get("scientificName") or "").strip()
                if not taxon:continue
                rawstatus=(rec.get("occurrenceStatus") or "").strip().casefold()
                status={"present":"present","absent":"absent_explicit"}.get(rawstatus,
                        "unassessed")
                if status=="unassessed":unknown+=1
                else:assessed+=1
                site,dt=events[eid]
                stage=normal_stage(rec.get("lifeStage"),tag=="adult_chorus")
                add(group,source_id,dt.year,dt.month,taxon,stage,
                    "adult_choir" if tag=="adult_chorus" else "amphibian_larval_monitor",
                    site,eid,status)
                observed+=1
    return {"original_event_rows":len(events),"original_taxon_stage_rows":observed,
            "source_status_assessed_rows":assessed,
            "source_status_unknown_rows":unknown,
            "source_sha256":ref["sha256"],"doi":ref["doi"]}

def finalize(group,registry):
    lookup={m["source_id"]:m for m in registry["source_modules"]}
    result=[]
    for k,g in sorted(group.items()):
        source,year,month,taxon,stage,method=k
        require(source in lookup,"Source not registered")
        both=g["presence_events"]&g["absent_events"]
        # Duplicate source occurrence rows can report opposite states for
        # the same taxon×stage×survey. Quarantine those AS AMBIGUOUS rather
        # than treating them as positive, negative, or dropping the source.
        present=g["presence_events"]-both
        absent=g["absent_events"]-both
        any_unknown=g["unassessed_events"]
        row={
            "source_id":source,
            "spatial_support":lookup[source]["spatial_support"],
            "year":year,"month":month,
            "taxon":taxon,"stage":stage,
            "sampling_method":method,
            "distinct_survey_events_with_taxon_stage_rows":len(g["events"]),
            "present_report_events":len(present),
            "explicit_non_detected_report_events":len(absent),
            "unassessed_or_unknown_report_events":len(any_unknown),
            "ambiguous_both_present_and_absent_source_events":len(both),
            "distinct_original_source_locations":len(g["sites"]),
            "rain_event_covariate_n":len(g["rain_values"]),
            "rain_event_sampled_mean":(sum(g["rain_values"].values())/len(g["rain_values"])
                                          if g["rain_values"] else None),
            "emergent_plant_pct_event_covariate_n":len(g["emergent_values"]),
            "emergent_plant_pct_sampled_event_mean":(
                 sum(g["emergent_values"].values())/len(g["emergent_values"])
                    if g["emergent_values"] else None),
            "depth_event_covariate_n":len(g["depth_values"]),
            "depth_sampled_event_mean":(
                 sum(g["depth_values"].values())/len(g["depth_values"])
                    if g["depth_values"] else None),
            "sampling_effort_assumed_equal_across_sources":False,
            "raw_site_keys_exported":False,
            "same_original_pond_proven_across_sources":False
        }
        result.append(row)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    reg=json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert reg["schema_version"]=="frogcs-comparable-observations/1.0"
    group=create_accumulator()
    original={
      "HUNGARY_2024":ingest_hungary(group),
      "INBO_CHORUS":ingest_inbo(group,"adult_chorus","INBO_CHORUS"),
      "INBO_LARVA":ingest_inbo(group,"larval_census","INBO_LARVA"),
    }
    rows=finalize(group,reg)
    assert any(x["source_id"]=="HUNGARY_2024" for x in rows)
    assert any(x["source_id"]=="INBO_CHORUS" for x in rows)
    assert any(x["source_id"]=="INBO_LARVA" for x in rows)
    args.out.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0])
    with (args.out/"canonical_source_stage_month_aggregates.csv").open("w",
            encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)
    bysource={}
    for src in original:
        x=[r for r in rows if r["source_id"]==src]
        bysource[src]={
          "aggregate_rows":len(x),
          "source_methods":sorted({r["sampling_method"] for r in x}),
          "stages_recorded":sorted({r["stage"] for r in x}),
          "observed_years":sorted({r["year"] for r in x}),
          "taxa_with_observed_status":len({r["taxon"] for r in x}),
          "source_original_QC":original[src],
        }
    q={
       "schema_version":reg["schema_version"],
       "created_on":"2026-10-26",
       "status":"REAL_SOURCE_STAGE_MONTH_AGGREGATES_NO_SAME_POND_CROSS_SOURCE_JOIN",
       "data_sources_in_registry":len(reg["source_modules"]),
       "source_files_ingested_as_original_records":3,
       "monthly_taxon_stage_aggregate_rows":len(rows),
       "conflicting_same_event_source_status_total":sum(r["ambiguous_both_present_and_absent_source_events"] for r in rows),
       "observed_sources":bysource,
       "source_immutable_originals":True,
       "roadside_stop_never_treated_as_an_INBO_pond":True,
       "GBIF_global_grid_has_no_actual_pond_identity":True,
       "missing_stages_or_plant_phenology_never_zero_imputed":True,
       "unobserved_permanence_or_predators_not_assumed_zero":True,
       "cross_study_call_and_predation_causal_link_identified":False,
       "all_original_site_ids_withheld":True,
       "normalization_warning":"Monthly event-report counts and stage labels are not occupancy/density or cohort survival; DO NOT pool acoustic activity levels across methods."
    }
    (args.out/"coverage_receipt.json").write_text(
        json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_COMPARABLE_DB_V1")
    print(json.dumps(q,ensure_ascii=False,indent=2))
    print("END_COMPARABLE_DB_V1")

if __name__=="__main__":
    main()
