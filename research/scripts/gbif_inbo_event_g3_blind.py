#!/usr/bin/env python3
"""GBIF G0.B: sampling-event cross-stage *opportunity* only, INBO original DwC-A.

Only original eventID, locationID, eventDate, samplingProtocol,
scientificName and literal lifeStage labels, and the existence (not values)
of individualCount/occurrenceStatus and measurementType/Unit are read.
Never read abundance, actual presence/absence, prey survival, diet outcome,
or any global G1/G2 response index. No event IDs or locality keys exported.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import date
import hashlib
from io import BytesIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile

from inbo_stage_taxon_g0 import SOURCES,part_rows
from part2_published_source_g0 import fetch

EXPECTED={
 "adult_chorus":"686c5a7aacc8f49e41a0642ecaa9efd8c3564304b0a4d4b027f3df2debec69fd",
 "larval_census":"c2cc960122ea398545edb661318160cd2b5b66a75a73dba8f7a3f61bd9c4f920",
}
SOURCE_GUILDS={
 "frog":"Anura",
 "possible_amphibian_predator":"Caudata",
}
ANURA_NAMES={
 "Bufo bufo","Hyla arborea","Pelobates fuscus",
 "Pelophylax esculenta synklepton","Pelophylax lessonae",
 "Pelophylax ridibundus","Rana arvalis","Rana temporaria",
}
CAUDATA_NAMES={
 "Ichthyosaura alpestris","Lissotriton helveticus","Lissotriton spec.",
 "Lissotriton vulgaris","Triturus cristatus",
}

def stage(raw):
    x=(raw or "").strip().lower()
    if x in {"larva","larvae","larval","tadpole","nymph"}:return "aquatic_immature"
    if x in {"adult","imago"}:return "adult"
    if x in {"egg","eggs"}:return "egg"
    if x in {"metamorph","metamorphosed"}:return "metamorph"
    return "other_or_unverified"

def taxon(t):
    if t in ANURA_NAMES:return "Anura"
    if t in CAUDATA_NAMES:return "Caudata"
    return "ambiguous_or_other"

def get(name):
    spec=SOURCES[name]
    binary,_=fetch(spec["url"])
    sha=hashlib.sha256(binary).hexdigest()
    assert sha==EXPECTED[name], "Source DWCA zip SHA changed"
    with zipfile.ZipFile(BytesIO(binary)) as z:
        root=ET.fromstring(z.read("meta.xml"))
        core=next(x for x in root if x.tag.rsplit("}",1)[-1]=="core")
        exts=[x for x in root if x.tag.rsplit("}",1)[-1]=="extension"]
        events={}
        by_site_year=defaultdict(set)
        for r in part_rows(z,core):
            eventid=r.get("eventID") or r.get("sourceCoreID")
            site=r.get("locationID","")
            timestamp=r.get("eventDate","")
            try:year=date.fromisoformat(timestamp[:10]).year
            except (ValueError,TypeError):continue
            if not site or not eventid:continue
            assert eventid not in events,"source event identifier duplicate"
            events[eventid]=(site,year,r.get("samplingProtocol",""))
            by_site_year[(site,year)].add(eventid)

        stage_by_event=defaultdict(set)
        taxon_stage_rows=Counter()
        event_species=defaultdict(set)
        metatypes=Counter()
        has_occ_columns=[]
        countrows=Counter()
        for node in exts:
            rows=iter(part_rows(z,node))
            first=next(rows,None)
            if first is None:continue
            headers=set(first)
            if "scientificName" in headers:
                has_occ_columns.append({
                    "explicit_occurrenceStatus_field":"occurrenceStatus" in headers,
                    "individualCount_field":"individualCount" in headers,
                    "lifeStage_field":"lifeStage" in headers,
                })
                def observe(r):
                    eid=r.get("eventID") or r.get("linkedCoreID")
                    if eid not in events:return
                    sp=r.get("scientificName","").strip()
                    st=stage(r.get("lifeStage",""))
                    cl=taxon(sp)
                    countrows[(cl,st)]+=1
                    taxon_stage_rows[(sp,st)]+=1
                    stage_by_event[eid].add((cl,st))
                    event_species[eid].add(sp)
                observe(first)
                for r in rows:observe(r)
            elif "measurementType" in headers:
                def measure(r):
                    k=r.get("measurementType","").strip().lower()
                    if k:metatypes[k]+=1
                measure(first)
                for r in rows:measure(r)

    both=[]
    larvae=[];caudata=[]
    allsiteyears=set()
    key_guild=defaultdict(set)
    for eid,stages in stage_by_event.items():
        site,year,protocol=events[eid]
        if ("Anura","aquatic_immature") in stages:
            larvae.append(eid)
            key_guild["frog_larva"].add((site,year))
        if ("Caudata","aquatic_immature") in stages:
            caudata.append(eid)
            key_guild["salamander_larva"].add((site,year))
        if ("Anura","aquatic_immature") in stages and ("Caudata","aquatic_immature") in stages:
            both.append(eid)
            allsiteyears.add((site,year))
    repeated_sites=len({
       site for site in {site for site,year in by_site_year}
       if sum(1 for s,y in by_site_year if s==site)>=2
    })
    return {
      "source_doi":spec["doi"], "source_sha256":sha,
      "event_count":len(events),"distinct_source_location_id":len({e[0] for e in events.values()}),
      "site_years":len(by_site_year),"distinct_sites_with_2plus_years":repeated_sites,
      "occurrence_field_presence":has_occ_columns,
      "distinct_frog_larva_annotated_events":len(larvae),
      "distinct_salamander_larva_annotated_events":len(caudata),
      "same_event_annotated_both_frog_and_salamander_larva":len(both),
      "same_source_site_years_with_both_larval_stage_annotations":len(allsiteyears),
      "frog_larva_site_years":len(key_guild["frog_larva"]),
      "salamander_larva_site_years":len(key_guild["salamander_larva"]),
      "stage_annotated_record_counts":{f"{c}|{s}":n for (c,s),n in sorted(countrows.items())},
      "source_taxon_stage_label_counts":{f"{c}|{s}":n for (c,s),n in sorted(taxon_stage_rows.items())},
      "measurement_type_coverage_record_count":dict(sorted(metatypes.items())),
      "nonpredator_ephemeroptera_chironomidae_assessed_by_protocol":False,
      "source_pond_identity_externally_verified":False,
      "same_event_predator_prey_abundance_count_read":False,
      "reported_anura_vs_caudata_diet_relationship_verified":False,
      "all_raw_site_keys_kept_private":True
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    report={
        "project":"frogcs",
        "status":"GBIF_SAMPLING_EVENT_G3_SOURCE_OPPORTUNITY_ONLY",
        "protocol":"research/GBIF_GLOBAL_STAGE_EVENT_BLIND_G0_PROTOCOL_2026-10-26.md",
        "sources":{name:get(name) for name in ("adult_chorus","larval_census")},
        "event_cross_guild_count_quality_sufficient":False,
        "has_source_assessed_nonpredatory_benthos_control":False,
        "G3_same_event_predator_prey_negative_control_test_eligible":False,
        "neither_predation_nor_true_zero_inferred":True,
        "source_coverage_only":True,
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BEGIN_INBO_GBIF_EVENT_G3_G0")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print("END_INBO_GBIF_EVENT_G3_G0")
if __name__=="__main__":
    main()
