#!/usr/bin/env python3
"""v4.7 minimal NONSENSITIVE catchment x survey-night feasibility contract.

All input rows are ALREADY-AGGREGATED SOURCE-AUTHORITATIVE site-count metadata,
not species sightings, protected site IDs, raw coordinates or individual data.

Does not establish the original ledger exists, nor infer frogs' calling.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter,defaultdict
from pathlib import Path

REQUIRED=("source_night_alias","catchment","n_distinct_wetlands_completed",
          "n_completed_five_min_visits","source_version")
CATCHMENTS={"Gwydir": {"sites_total":15,"completed_visits":195},
            "Macquarie": {"sites_total":14,"completed_visits":148}}
PUBLISHED_NIGHTS=95
PUBLISHED_TOTAL_VISITS=343


def audit(raw:str)->dict:
    rd=csv.DictReader(io.StringIO(raw))
    fields=rd.fieldnames or []
    if len(fields)!=len(set(fields)) or set(fields)!=set(REQUIRED):
        raise ValueError("Only exact aggregate metadata columns are accepted, no frog response/site locations")
    rows=list(rd)
    if not rows:
        raise ValueError("No aggregate exposure observations")
    seen=set()
    nights=defaultdict(dict)
    counts=Counter()
    source_versions=set()
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Invalid/extra CSV columns")
        night=row["source_night_alias"].strip()
        catchment=row["catchment"].strip()
        version=row["source_version"].strip()
        if not night or not version or len(night)>100 or len(version)>100:
            raise ValueError("Missing source-defined night alias or version")
        if catchment not in CATCHMENTS:
            raise ValueError("Only original two named catchments allowed")
        key=(night,catchment)
        if key in seen:
            raise ValueError("Duplicate catchment-night source aggregate")
        seen.add(key)
        try:
            width=int(row["n_distinct_wetlands_completed"])
            visits=int(row["n_completed_five_min_visits"])
        except ValueError as e:
            raise ValueError("Invalid source count") from e
        if str(width)!=row["n_distinct_wetlands_completed"].strip() or str(visits)!=row["n_completed_five_min_visits"].strip():
            raise ValueError("Noncanonical integer count")
        if not 0<=width<=CATCHMENTS[catchment]["sites_total"]:
            raise ValueError("Impossible catchment-night physical-wetland width")
        if width>visits:
            raise ValueError("More distinct wetland sites than completed visits")
        if width==0 and visits!=0:
            raise ValueError("Completed visits cannot occur with zero sampled wetlands")
        if visits>0 and width==0:
            raise ValueError("Invalid source opportunity")
        nights[night][catchment]=(width,visits)
        counts[catchment]+=visits
        source_versions.add(version)
    total=sum(counts.values())
    has_repeat_visits=any(v>w for pairs in nights.values() for w,v in pairs.values())
    nights_pooled=0
    nights_within=0
    within_counts=Counter()
    catchment_opportunity=Counter()
    for night,pairs in nights.items():
        pooled=sum(width for width,_ in pairs.values())
        if pooled>=4:
            nights_pooled+=1
        if any(width>=4 for width,_ in pairs.values()):
            nights_within+=1
        for region,(width,_) in pairs.items():
            if width>=4:
                catchment_opportunity[region]+=1
            within_counts[(region,width)]+=1
    published_match=(
        len(nights)==PUBLISHED_NIGHTS and total==PUBLISHED_TOTAL_VISITS
        and all(counts[c]==t["completed_visits"] for c,t in CATCHMENTS.items())
    )
    # We cannot certify that width was compiled from authentic physical sites,
    # even when all the published aggregate margins match.
    return {
        "analysis":"ocock_catchment_night_source_aggregate_v47",
        "n_unique_source_nights":len(nights),
        "n_input_catchment_night_rows":len(rows),
        "completed_visits_by_catchment":dict(sorted(counts.items())),
        "n_total_completed_five_min_visits":total,
        "n_nights_with_4plus_wetlands_POOLED_ACROSS_CATCHMENTS":nights_pooled,
        "n_nights_with_4plus_wetlands_WITHIN_ANY_ONE_CATCHMENT":nights_within,
        "n_catchment_nights_with_4plus_wetlands":dict(sorted(catchment_opportunity.items())),
        "per_catchment_completed_width_histograms":{
            c:{str(w):v for (reg,w),v in sorted(within_counts.items()) if reg==c}
            for c in sorted(CATCHMENTS)
        },
        "source_versions_count":len(source_versions),
        "has_repeated_within_night_site_visits":has_repeat_visits,
        "published_total_margins_match":published_match,
        "status":("PUBLISHED_MARGINS_MATCH_SOURCE_AUTHENTICITY_NOT_VERIFIED"
                  if published_match else "DIFFERENT_OR_INCOMPLETE_SOURCE_FRAME"),
        "caution":"A shared date or source-night alias across Gwydir and Macquarie is not one geographically coherent acoustic route or shared rainfall treatment. Catchment-level width is necessary but not sufficient for identifying a common environmental pulse.",
        "real_frog_records_read":False,
        "original_source_provenance_verified":False,
        "species_strict_prior_chorus_history_verified":False,
        "simultaneous_rain_sound_water_event_verified":False,
        "metamorph_join_verified":False,
        "rc6_unchanged":True,
    }


def synthetic_test():
    header=",".join(REQUIRED)+"\n"
    # Complete fabricated published totals, with 2 or 3 Gwydir sites per
    # night and 0 or 2 Macquarie sites per night. It preserves all margins
    # but NO night has 4 distinct sites INSIDE one catchment.
    rows=[]
    for t in range(95):
        gw=3 if t<5 else 2  # 5*3 + 90*2 = 195
        mc=2 if t<74 else 0 # 74*2 = 148
        rows.append(f"N{t},Gwydir,{gw},{gw},SYNTHETIC")
        if mc:
            rows.append(f"N{t},Macquarie,{mc},{mc},SYNTHETIC")
    result=audit(header+"\n".join(rows)+"\n")
    assert result["published_total_margins_match"]
    assert result["n_unique_source_nights"]==95
    assert result["n_nights_with_4plus_wetlands_POOLED_ACROSS_CATCHMENTS"]==74
    assert result["n_nights_with_4plus_wetlands_WITHIN_ANY_ONE_CATCHMENT"]==0
    assert result["real_frog_records_read"] is False

    bad=[
        header+"N0,Gwydir,16,16,SYNTHETIC\n",
        header+"N0,Macquarie,15,15,SYNTHETIC\n",
        header+"N0,Gwydir,4,3,SYNTHETIC\n",
        header+"N0,Gwydir,-1,0,SYNTHETIC\n",
        header+"N0,Gwydir,0,2,SYNTHETIC\n",
        header+"N0,Gwydir,2,2,SYNTHETIC\nN0,Gwydir,2,2,SYNTHETIC\n",
        header.replace("source_version","frog_call,source_version")+
            "N0,Gwydir,2,2,CALLING,SYNTHETIC\n",
        header+"N0,UnknownRiver,2,2,SYNTHETIC\n",
        header+"N0,Gwydir,2.0,2,SYNTHETIC\n",
    ]
    for i,p in enumerate(bad):
        try:
            audit(p)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid source fixture {i} passed")
    print("PASS: 95 nights, Gwydir 195, Macquarie 148, 343 visit margins; "
          "74 pooled 4+ nights yet ZERO within-catchment 4+ nights (SYNTHETIC only)")
    print("PASS: 9 unsafe source inputs rejected, no frog outcomes or site coordinates")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--synthetic-test",action="store_true")
    p.add_argument("--authorized-aggregate-csv",type=Path)
    p.add_argument("--receipt",type=Path)
    args=p.parse_args()
    if args.synthetic_test:
        synthetic_test()
        return
    if not args.authorized_aggregate_csv or not args.receipt:
        p.error("Source-authorized aggregate CSV and receipt both required")
    contents=args.authorized_aggregate_csv.read_bytes()
    result=audit(contents.decode("utf-8-sig"))
    result["authorized_aggregate_sha256"]=hashlib.sha256(contents).hexdigest()
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "n_within_catchment_4plus":result["n_nights_with_4plus_wetlands_WITHIN_ANY_ONE_CATCHMENT"],
                      "frog_records_read":False}))


if __name__=="__main__":
    main()
