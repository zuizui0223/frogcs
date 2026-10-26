#!/usr/bin/env python3
"""INBO G0: exact site-year prior aquatic stages and breeding-stage timing.

No occurrenceStatus, individualCount or source response values are read.
Distinguish strictly PREVIOUS CALENDAR YEAR stage exposure opportunity from
same-year larval after-current-adult records. Stage names are not size.
Date gaps and counts are metadata: not behavioral or trophic effects.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
from datetime import date
import hashlib
from io import BytesIO
import json
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

from inbo_stage_taxon_g0 import SOURCES,part_rows
from part2_published_source_g0 import fetch
from gbif_inbo_event_g3_blind import EXPECTED,ANURA_NAMES,CAUDATA_NAMES,stage

HYLA="Hyla arborea"

def source(name):
    obj=SOURCES[name]
    blob,_=fetch(obj["url"])
    digest=hashlib.sha256(blob).hexdigest()
    if digest!=EXPECTED[name]:raise ValueError("Original INBO source digest changed")
    events={}
    cov=defaultdict(lambda:defaultdict(set))
    aliases=defaultdict(set)
    with zipfile.ZipFile(BytesIO(blob)) as z:
        root=ET.fromstring(z.read("meta.xml"))
        core=next(x for x in root if x.tag.rsplit("}",1)[-1]=="core")
        extensions=[x for x in root if x.tag.rsplit("}",1)[-1]=="extension"]
        for r in part_rows(z,core):
            eid=r.get("eventID") or r.get("sourceCoreID")
            site=r.get("locationID","")
            try: d=date.fromisoformat((r.get("eventDate") or "")[:10])
            except ValueError:continue
            if not eid or not site:continue
            if eid in events:raise ValueError("Duplicate original event")
            events[eid]=(site,d)
            aliases[site].add(r.get("locality","").strip().casefold())
        for node in extensions:
            rows=iter(part_rows(z,node))
            first=next(rows,None)
            if first is None or "scientificName" not in first:continue
            for r in [first]+list(rows):
                eid=r.get("eventID") or r.get("linkedCoreID")
                if eid not in events:continue
                sp=r.get("scientificName","").strip()
                ont=stage(r.get("lifeStage",""))
                site,d=events[eid]
                labels=[]
                if sp==HYLA and ont=="adult":labels.append("hyla_adult")
                if sp==HYLA and ont=="aquatic_immature":labels.append("hyla_larva")
                if sp in ANURA_NAMES and sp!=HYLA and ont=="aquatic_immature":labels.append("other_anuran_larva")
                if sp in CAUDATA_NAMES and ont=="aquatic_immature":labels.append("caudata_larva")
                for lab in labels:
                    cov[lab][(site,d.year)].add((eid,d))
    return {"events":events,"coverage":cov,"aliases":aliases,"source_sha256":digest}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    ac=source("adult_chorus")
    lar=source("larval_census")
    shared=set(ac["aliases"])&set(lar["aliases"])
    safe=set()
    conflicts=0
    for site in shared:
        a={x for x in ac["aliases"][site] if x}
        b={x for x in lar["aliases"][site] if x}
        if (len(a)>1 or len(b)>1 or (a and b and not a.intersection(b))):
            conflicts+=1
        else:safe.add(site)
    if conflicts:raise ValueError("Conflicting locality map")
    adult={
       (site,year):v for (site,year),v in ac["coverage"]["hyla_adult"].items()
       if site in safe
    }
    annual={}
    for guild in ("other_anuran_larva","caudata_larva","hyla_larva"):
        previous=set()
        same_year=set()
        for site,year in adult:
            if (site,year-1) in lar["coverage"][guild]:
                previous.add((site,year))
            if (site,year) in lar["coverage"][guild]:
                same_year.add((site,year))
        annual[guild]={
           "eligible_previous_year_site_years":len(previous),
           "eligible_previous_year_sites":len({s for s,y in previous}),
           "eligible_previous_year_years":sorted({y for s,y in previous}),
           "eligible_same_year_site_years":len(same_year),
           "eligible_same_year_sites":len({s for s,y in same_year}),
           "same_year_census_cannot_explain_earlier_adult_call_without_temporal_precedence":True,
        }
    joint_prev=set(adult)
    for guild in ("other_anuran_larva","caudata_larva"):
        joint_prev&={(site,year) for site,year in adult
                     if (site,year-1) in lar["coverage"][guild]}
    joint_siteyear={
         (site,year) for site,year in lar["coverage"]["hyla_larva"]
         if (site,year) in lar["coverage"]["caudata_larva"]
         and site in safe
    }
    simultaneous_events=set()
    stage_day_diff=[]
    for site,year in joint_siteyear:
        x=lar["coverage"]["hyla_larva"][(site,year)]
        y=lar["coverage"]["caudata_larva"][(site,year)]
        xe={a for a,d in x};ye={a for a,d in y}
        simultaneous_events|=xe&ye
        stage_day_diff.append(min(abs((dx-dy).days) for a,dx in x for b,dy in y))
    earliest_choir_then_larva=set()
    for (site,year),days in adult.items():
        if (site,year) not in lar["coverage"]["hyla_larva"]:continue
        if min(d for eid,d in days)<max(d for eid,d in lar["coverage"]["hyla_larva"][(site,year)]):
            earliest_choir_then_larva.add((site,year))
    out={
     "status":"SOURCE_BLIND_CROSS_TAXON_STAGE_AND_CHORUS_TIMING_G0",
     "source_DOIs":["10.15468/d4bu8j","10.15468/swgure"],
     "source_sha256":{name:obj["source_sha256"] for name,obj in
                      (("chorus",ac),("larva",lar))},
     "source_exact_locationID_overlap":len(shared),
     "locality_conflicts":conflicts,
     "hyla_choir_site_years_exact_source_sites":len(adult),
     "hyla_choir_source_sites":len({site for site,y in adult}),
     "previous_year_other_taxon_larva_sampling":annual,
     "joint_previous_year_other_anuran_and_caudata_larva_site_years":len(joint_prev),
     "same_year_hyla_and_caudata_larva_site_years":len(joint_siteyear),
     "same_year_same_census_hyla_and_caudata_larva_events":len(simultaneous_events),
     "same_year_nearest_larva_stage_recording_gap_days":{
        "n":len(stage_day_diff),
        "min":min(stage_day_diff) if stage_day_diff else None,
        "median":sorted(stage_day_diff)[len(stage_day_diff)//2] if stage_day_diff else None,
        "max":max(stage_day_diff) if stage_day_diff else None},
     "preceding_adult_call_and_later_same_taxon_larva_site_years":len(earliest_choir_then_larva),
     "independent_prior_stage_exposure_presence_or_count_inspected":False,
     "other_larvae_automatically_competitors":False,
     "caudata_larvae_automatically_predators":False,
     "ontogenetic_stage_size_similarity_measured":False,
     "real_wetland_hydroperiod_measured_for_join":False,
     "weather_or_emergent_vegetation_available_in_linked_INBO":False,
     "source_keys_exported":False,
     "next_endpoint_G1_status":"ONLY_IF_PREVIOUS_YEAR_COVERAGE_AND_SAMPLED_ZEROS_MEET_FROZEN_THRESHOLDS",
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_FROGCS_PRIOR_LARVAL_COMPETITOR_BLIND")
    print(json.dumps(out,ensure_ascii=False,indent=2))
    print("END_FROGCS_PRIOR_LARVAL_COMPETITOR_BLIND")
if __name__=="__main__":main()
