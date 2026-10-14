#!/usr/bin/env python3
"""Public USGS historic 2003–08 x 2024 original survey feasibility, SOURCE BLIND.

Pre-response goal (2026-10-14): compare exact official source site identifiers,
effort/event units, observer/method/timing support and source dictionary, WITHOUT
examining frog species response frequencies or claiming recolonization. Both
official public CC0 releases are independently verified; do not print sites,
observers, species names, coordinates or raw source rows.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
from io import StringIO
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
import csv,json

ITEMS={
    "history_2003_2008":"68015203d4be0263cab1091b",
    "new_2024":"68016413d4be0263cab109a8",
}
PIN_2024="dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4"
OUTPUT="studies/climate_landscape/receipts/USGS_ARMI_PUBLIC_2003_2008_2024_SOURCE_LINK_GATE.json"
CAP=18000000

def allowed(u):
    p=urlsplit(u)
    host=(p.hostname or "").lower()
    return p.scheme=="https" and (host=="www.sciencebase.gov"
                   or host.endswith(".sciencebase.gov")
                   or host.endswith(".amazonaws.com"))

def pull(u,cap):
    if not allowed(u):raise ValueError("DISALLOWED_EXTERNAL_HOST")
    with urlopen(Request(u,headers={
        "User-Agent":"frogcs-open-USGS-historic-versus-new-source-grain/8.1",
        "Accept":"application/json,text/csv"}),timeout=55) as res:
        if res.status!=200 or not allowed(res.geturl()):raise ValueError("NOT_PUBLIC_200_SOURCE")
        r=res.read(cap+1)
    if not r or len(r)>cap:raise ValueError("EMPTY_OR_LARGE_RESPONSE")
    return r

def public_file(item_id):
    meta=json.loads(pull(f"https://www.sciencebase.gov/catalog/item/{item_id}?format=json",1500000))
    if meta.get("id")!=item_id:raise ValueError("ID_MISMATCH")
    entries=[]
    for f in (meta.get("files") or []):
        name=str(f.get("name",""))
        entries.append({"file_ext":name.rsplit(".",1)[-1].lower() if "." in name else "",
                        "name":name[:190],"size":f.get("size"),
                        "media_type":str(f.get("contentType",""))[:80]})
    csv_files=[f for f in (meta.get("files") or [])
               if str(f.get("name","")).lower().endswith(".csv")
                  and f.get("size") and 0<f["size"]<CAP]
    if len(csv_files)!=1:
        return meta,None,{"status":"NOT_EXACTLY_ONE_PUBLIC_CSV",
             "n_csv_candidates":len(csv_files),"file_metadata":entries}
    f=csv_files[0]
    url=str(f.get("downloadUri",""))
    data=pull(url,CAP)
    if len(data)!=f["size"]:raise ValueError("CSV_DECLARED_SIZE_MISMATCH")
    return meta,data,{"status":"UNMODIFIED_PUBLIC_CSV_OBTAINED",
                      "file_metadata":entries,
                      "data_basename":str(f["name"])[:200],
                      "data_bytes":len(data),"sha256":sha256(data).hexdigest()}

def profile_csv(data:bytes):
    text=data.decode("utf-8-sig")
    rdr=csv.DictReader(StringIO(text))
    cols=rdr.fieldnames
    if not cols or len(cols)!=len(set(cols)) or len(cols)>250:
        raise ValueError("BAD_SOURCE_CSV_HEADER")
    candidates={
        "site":[x for x in cols if x.casefold() in ("site","siteid","site_id")],
        "old_id":[x for x in cols if x.casefold() in ("site_original","siteoriginal","site_original_id")],
        "date":[x for x in cols if x.casefold() in ("date","surveydate","sampledate")],
        "observer":[x for x in cols if x.casefold() in ("observer","observerid","observer_id")],
        "method":[x for x in cols if x.casefold() in ("method","survey_method","surveymethod")],
        "clock":[x for x in cols if x.casefold() in ("arrival_time","arrivaltime","time","start_time")],
        "species":[x for x in cols if x.casefold() in ("species","speciesname","scientific_name")],
        "count":[x for x in cols if x.casefold() in ("number_heard","numberheard","count")],
    }
    exact_map={k:v[0] for k,v in candidates.items() if len(v)==1}
    n=0
    groups=defaultdict(set);site_dates=defaultdict(set)
    named_site=set(); original=set();months=Counter();years=Counter()
    combos=Counter();singletons=Counter()
    by_observer=defaultdict(set); by_method=Counter(); by_clock=Counter()
    for row in rdr:
        n+=1
        if n>450000 or None in row:raise ValueError("SOURCE_ROW_GRAIN_FAILURE")
        site=str(row.get(exact_map.get("site",""),"") or "").strip()
        old=str(row.get(exact_map.get("old_id",""),"") or "").strip()
        date=str(row.get(exact_map.get("date",""),"") or "").strip()
        person=str(row.get(exact_map.get("observer",""),"") or "").strip()
        method=str(row.get(exact_map.get("method",""),"") or "").strip()
        clock=str(row.get(exact_map.get("clock",""),"") or "").strip()
        if site: named_site.add(site)
        if old:original.add(old)
        if site and date:site_dates[site].add(date)
        if date:
            dt=None
            for fmt in ("%Y-%m-%d","%m/%d/%Y","%Y/%m/%d"):
                try:dt=datetime.strptime(date,fmt).date();break
                except ValueError:pass
            if dt:years[dt.year]+=1; months[dt.month]+=1
        if site and date and person:
            key=(site,date,person)
            groups[key].add((method,clock))
            by_observer[(site,date)].add(person)
        if method:by_method[method]+=1
        if clock:by_clock[clock]+=1
    site_day_pairs={(s,d) for s,dd in site_dates.items() for d in dd}
    repeated=sum(len(ds)>=2 for ds in site_dates.values())
    site_date_with_both=sum(len(obs)>1 for obs in by_observer.values())
    return {
        "n_source_lines":n,"field_names_only":cols,
        "inferred_exact_key_column_names_only":exact_map,
        "n_distinct_public_original_site_ids":len(named_site),
        "n_distinct_public_original_historical_alias_ids":len(original),
        "n_distinct_source_site_day_keys":len(site_day_pairs),
        "n_distinct_source_site_day_observer_keys":len(groups),
        "n_sites_with_two_or_more_recorded_survey_dates":repeated,
        "n_site_days_with_multiple_observers":site_date_with_both,
        "n_observer_source_keys_with_internally_multiple_method_or_times":
             sum(len(x)>1 for x in groups.values()),
        "observed_year_counts_source_species_rows":dict(sorted(years.items())),
        "source_month_counts_source_species_rows":dict(sorted(months.items())),
        "observer_method_counts_source_rows":dict(sorted(by_method.items())),
        "n_original_observer_codes":len({o for (_,d,o) in groups}),
        "non_site_date_values_exported":True,
        "n_original_lat_long_extracted_to_output":0,
        "n_ecological_species_response_values_computed":0,
    },{"site":named_site,"original":original,
       "site_day_pairs":site_day_pairs,"site_day_map":site_dates}

def tests():
    mock="Site,Site_original,Date,Observer,Method,Arrival_time,Species\nA,S1,2024-06-01,O1,Ear,20:12,Frog1\nA,S1,2024-06-01,O2,Microphone,20:14,Frog2\nA,S1,2024-07-01,O1,Ear,20:00,None\n"
    p,raw=profile_csv(mock.encode())
    assert p["n_source_site_day_observer_keys"]==3
    assert p["n_site_days_with_multiple_observers"]==1
    assert p["n_sites_with_two_or_more_recorded_survey_dates"]==1
    assert "S1" not in json.dumps(p) and "Frog1" not in json.dumps(p)
    print("PASS: strict source header, site/observer/date grain and no source identifiers or frog taxa emitted")

def main():
    tests()
    record={"record_type":"historical_versus_2024_USGS_source_identity_AND_replicate_grain",
            "status":"METADATA_PREFLIGHT",
            "checked_utc":datetime.now(timezone.utc).isoformat(),
            "data_product":"USGS 2003-08 Midwest ARMI vs 2024 Midwest ARMI v1.1 Apr 2026",
            "no_frog_species_outcome_fitted":True,
            "no_sensitive_location_or_observer_ids_redistributed":True,
            "sources":{}}
    raw_id={}
    for key,item in ITEMS.items():
        obj,data,meta=public_file(item)
        rec={"source_item_id":item,"source_title":obj.get("title"),
             "source_rights_available":bool(obj.get("rights")),
             **meta}
        if data:
            if key=="new_2024" and meta["sha256"]!=PIN_2024:
                raise ValueError("KNOWN_2024_SOURCE_HASH_MISMATCH")
            p,ids=profile_csv(data)
            rec["profile"]=p
            raw_id[key]=ids
            if key=="new_2024" and (p["n_source_lines"]!=1934 or p["n_distinct_public_original_site_ids"]!=343):
                raise ValueError("KNOWN_2024_SCOPE_CHANGED")
        record["sources"][key]=rec
    if len(raw_id)==2:
        old=raw_id["history_2003_2008"];new=raw_id["new_2024"]
        record["exact_site_identifier_intersection_aggregate_only"]={
          "exact_Site_match_count":len(old["site"]&new["site"]),
          "exact_Site_original_match_count":len(old["original"]&new["original"]),
          "old_Site_to_new_Site_original_exact_cross":len(old["site"]&new["original"]),
          "old_Site_original_to_new_Site_exact_cross":len(old["original"]&new["site"]),
          "n_old_source_site_aliases":len(old["site"]),
          "n_new_source_site_aliases":len(new["site"]),
          "source_crosswalk_certified":False,
          "comparison_warning":"Source-label intersection is not date-effective physical station crosswalk or observed historical occupancy; no fuzzy/spatial matching attempted"
        }
        record["status"]="BOTH_PUBLIC_RELEASES_FULLY_READ_SOURCE_GRAIN_ONLY"
    else:
        record["status"]="ONE_OR_BOTH_ORIGINAL_PUBLIC_CSV_UNAVAILABLE"
    p=Path(OUTPUT);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print("PUBLIC_ARMI_HISTORICAL_GATE "+json.dumps(record,sort_keys=True),flush=True)

if __name__=="__main__":main()
