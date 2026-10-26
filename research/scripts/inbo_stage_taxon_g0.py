#!/usr/bin/env python3
"""Response-blind *taxon-specific* INBO two-protocol G0.1 eligibility.

The primary data are the two archived CC0 INBO 2026 DwC-A ZIPs, fetched
transiently and pinned to the previously audited content digests. The audit
NEVER reads occurrenceStatus, individualCount or measurementValue.
It does read taxon, lifeStage, surveyed event, temporal order and original
publishers' physical LocationID. Export only aggregate site/year/coverage;
raw sensitive locationIDs are not exported.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date
from io import BytesIO, TextIOWrapper
from pathlib import Path
import argparse
import csv
import hashlib
import json
import zipfile
from xml.etree import ElementTree as ET
from part2_published_source_g0 import fetch,xml_child,xml_children,norm_delim

SOURCES={
"adult_chorus":{
 "url":"https://ipt.inbo.be/archive.do?r=meetnetten-amphibia-roepkoren-occurrences",
 "sha256":"686c5a7aacc8f49e41a0642ecaa9efd8c3564304b0a4d4b027f3df2debec69fd",
 "doi":"10.15468/d4bu8j"},
"larval_census":{
 "url":"https://ipt.inbo.be/archive.do?r=meetnetten-amfibieen-larven-metamorfen-occurrences",
 "sha256":"c2cc960122ea398545edb661318160cd2b5b66a75a73dba8f7a3f61bd9c4f920",
 "doi":"10.15468/swgure"}
}
TARGETS=("Hyla arborea","Pelobates fuscus")

def part_rows(zf,node):
    location=xml_child(xml_child(node,"files"),"location")
    file=location.text.strip()
    index_to_field={int(f.attrib["index"]): f.attrib.get("term","").rsplit("/",1)[-1].rsplit("#",1)[-1]
                    for f in xml_children(node,"field")}
    coreid=xml_child(node,"coreid")
    if coreid is not None:index_to_field[int(coreid.attrib["index"])]="linkedCoreID"
    id_field=xml_child(node,"id")
    if id_field is not None:index_to_field[int(id_field.attrib["index"])]="sourceCoreID"
    delimiter=norm_delim(node.attrib.get("fieldsTerminatedBy","\\t"))
    enclosure=norm_delim(node.attrib.get("fieldsEnclosedBy",'"'))
    skip=int(node.attrib.get("ignoreHeaderLines","0"))
    with zf.open(file) as stream,TextIOWrapper(stream,encoding=node.attrib.get("encoding","utf-8-sig"),errors="replace",newline="") as fin:
        reader=csv.reader(fin,delimiter=delimiter,quotechar=enclosure if len(enclosure)==1 else '"')
        for i,record in enumerate(reader):
            if i<skip:continue
            yield {field:record[k].strip() if k<len(record) else "" for k,field in index_to_field.items()}

def get_archive(spec):
    blob,_=fetch(spec["url"])
    digest=hashlib.sha256(blob).hexdigest()
    if digest!=spec["sha256"]:raise ValueError("Pinned original DwCA checksum changed")
    with zipfile.ZipFile(BytesIO(blob)) as z:
        root=ET.fromstring(z.read("meta.xml"))
        core=next(x for x in root if x.tag.rsplit("}",1)[-1]=="core")
        extensions=[x for x in root if x.tag.rsplit("}",1)[-1]=="extension"]
        events={}
        aliases=defaultdict(set)
        years=set()
        for x in part_rows(z,core):
            eid=x.get("eventID",x.get("sourceCoreID",""))
            site=x.get("locationID","")
            dt=x.get("eventDate","")[:10]
            try: day=date.fromisoformat(dt)
            except ValueError: continue
            if not eid or not site:continue
            if eid in events:raise ValueError("Duplicate eventID in original event core")
            events[eid]=(site,day,x.get("locality","").strip())
            aliases[site].add(x.get("locality","").strip().casefold())
            years.add(day.year)
        species_coverage=defaultdict(set)
        stages=defaultdict(Counter)
        raw_taxon_labels=set()
        measures_by_type=Counter()
        occurrences=0
        for ext in extensions:
            rr=iter(part_rows(z,ext))
            first=next(rr,None)
            if first is None:continue
            cols=set(first)
            it=iter([first]+list(rr))
            if "scientificName" in cols:
                for d in it:
                    occurrences+=1
                    eid=d.get("eventID") or d.get("linkedCoreID") or ""
                    if eid not in events:continue
                    sday=events[eid]
                    sp=d.get("scientificName","").strip()
                    raw_taxon_labels.add(sp)
                    # Not reading occurrenceStatus or individualCount
                    species_coverage[sp].add((sday[0],sday[1].year,sday[1],eid))
                    stages[sp][d.get("lifeStage","").strip()]+=1
            elif "measurementType" in cols:
                for d in it:
                    t=d.get("measurementType","")
                    if t:measures_by_type[t]+=1
        return {
            "archive_sha256":digest,
            "source_events":len(events),"event_years":sorted(years),
            "unique_locations":len(aliases),"species_row_events":occurrences,
            "reported_taxon_tokens":sorted(raw_taxon_labels),
            "focal_taxon_stage_label_counts":{taxon:dict(stages[taxon]) for taxon in TARGETS},
            "physical_location_identifiers_exported":False,
            "measured_covariate_types_present":sorted(measures_by_type),
        },{
            "events":events,
            "aliases":aliases,
            "species_coverage":species_coverage
        }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    pub={};private={}
    for name,spec in SOURCES.items():
        pub[name],private[name]=get_archive(spec)
    a,b=private["adult_chorus"],private["larval_census"]
    shared=set(a["aliases"])&set(b["aliases"])
    inconsistencies=0
    within_source_name_variations=0
    for site in shared:
        aa={x for x in a["aliases"][site] if x}
        bb={x for x in b["aliases"][site] if x}
        if aa and bb and not aa.intersection(bb):inconsistencies+=1
        if len(aa)>1 or len(bb)>1:within_source_name_variations+=1
    # All rows are survey opportunity, NOT positive outcomes
    target_stats={}
    for sp in TARGETS:
        arows=a["species_coverage"].get(sp,set())
        brows=b["species_coverage"].get(sp,set())
        am=defaultdict(list);bm=defaultdict(list)
        for site,year,dt,eid in arows:am[(site,year)].append(dt)
        for site,year,dt,eid in brows:bm[(site,year)].append(dt)
        covered=set(am)&set(bm)
        chronology={p for p in covered if min(am[p])<max(bm[p])}
        sites={x[0] for x in chronology}
        times=Counter({year:sum(p[1]==year for p in chronology) for year in sorted({x[1] for x in chronology})})
        target_stats[sp]={
            "adult_annotated_species_events":len(arows),
            "larval_annotated_species_events":len(brows),
            "exact_same_site_year_taxon_coverage":len(covered),
            "chorus_event_precedes_larval_event_site_year":len(chronology),
            "distinct_shared_locationIDs_without_export":len(sites),
            "year_counts":{str(k):v for k,v in times.items()},
            "source_overlap_has_10plus_sites":len(sites)>=10,
            "source_sample_contains_10plus_eligible_location_years":len(chronology)>=10,
            "stage_presence_or_absence_NOT_OPENED":True
        }
    public_report={
      "status":"SOURCE_BLIND_TAXON_SITE_OPPORTUNITY_ONLY",
      "prior_design":"research/INBO_EXACT_LOCATION_CHORUS_LARVA_BRIDGE_G0_SPEC_2026-10-26.md",
      "sources":pub,"shared_exact_location_ID_count":len(shared),
      "conflicting_nonempty_locality_label_sites":inconsistencies,
      "within_source_alias_variation_sites":within_source_name_variations,
      "focal_taxa":target_stats,
      "no_stage_outcomes_or_egg_success_inspected":True,
      "underlying_waterbody_identity_verified":False,
      "site_identifiers_redistributed":False,
      "cross_stage_predation_supported":False,
      "readiness":"G1_FIT_NOT_AUTHORIZED_UNTIL_PHYSICAL_POND_AND_TRUE_SAMPLED_ZEROS_CHECKED"
    }
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(public_report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_FROGCS_INBO_TAXON_G0")
    print(json.dumps(public_report,indent=2,ensure_ascii=False))
    print("END_FROGCS_INBO_TAXON_G0")

if __name__=="__main__":
    main()
