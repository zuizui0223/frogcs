#!/usr/bin/env python3
"""Original USGS 2003-08 and 2024 source identity / observation support audit.

PRE-OUTCOME DESIGN 2026-10-14: compare source-normalized Site and legacy
Site_original labels, medians of source-published WGS84 locations and
overlapping observation month/method. Does NOT inspect frog species rows
except preserving them internally as unused source columns. No coordinates,
site IDs, observers, species or exact visit dates are emitted.
No geospatial proximity alone authenticates site identity.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime
from math import radians,sin,cos,asin,sqrt
from statistics import median
from hashlib import sha256
from io import StringIO
from urllib.request import Request,urlopen
from pathlib import Path
from xml.etree import ElementTree
import csv,json

import audit_usgs_armi_history2024_public_source_gate as src

HIST_SHA="33bb028cf148a685d8af5a579786ce94bde045fa68d00f8c395713c6c06ae32b"
NEW_SHA="dafd388c7ccb79e08dbadd37a25c604473a8caf4ff5c8318532740acb56a04e4"
OUT="studies/climate_landscape/receipts/USGS_ARMI_HISTORIC_2024_SPATIAL_ID_METHOD_OVERLAP.json"

def geo_km(a,b):
    y1,x1=a;y2,x2=b
    p1,p2=radians(y1),radians(y2)
    dp=radians(y2-y1);dl=radians(x2-x1)
    h=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return 6371.0088*2*asin(min(1,sqrt(h)))

def positive_coordinates(text):
    rdr=csv.DictReader(StringIO(text))
    want={"Site","Site_original","Latitude_WGS84","Longitude_WGS84",
          "Date","Arrival_time","Observer","Method"}
    if not rdr.fieldnames or not want.issubset(rdr.fieldnames):
        raise ValueError("NO_ORIGINAL_KEY_COLUMNS")
    coords=defaultdict(list)
    aliases=defaultdict(list)
    methods=defaultdict(set)
    visits=defaultdict(set)
    method_month=defaultdict(set)
    rejected=Counter()
    n=0
    for r in rdr:
        n+=1
        if None in r:raise ValueError("ORIGINAL_CSV_EXTRA_FIELDS")
        site=r["Site"].strip()
        alias=r["Site_original"].strip()
        try:
            lat=float(r["Latitude_WGS84"]);lon=float(r["Longitude_WGS84"])
            if not -90<=lat<=90 or not -180<=lon<=180:raise ValueError()
        except ValueError:
            rejected["missing_or_invalid_coord_rows"]+=1; continue
        try:
            date=datetime.strptime(r["Date"],"%Y-%m-%d").date()
        except ValueError:
            rejected["invalid_date_rows"]+=1; continue
        if not site:rejected["blank_site"]+=1;continue
        coords[site].append((lat,lon))
        if alias:aliases[alias].append((lat,lon))
        method=r["Method"].strip()
        methods[site].add(method)
        if method in {"Ear","Microphone"}:
            method_month[site].add((method,date.month))
            visits[site].add((date,r["Observer"].strip(),r["Arrival_time"].strip(),method))
    def profile(dic):
        result={}
        within_spreads=[]
        for key,locs in dic.items():
            ys=[v[0] for v in locs];xs=[v[1] for v in locs]
            representative=(median(ys),median(xs))
            spread=max(geo_km(x,representative) for x in locs)
            result[key]=representative
            within_spreads.append(spread)
        return result,within_spreads
    srep,spread=profile(coords)
    arep,aspread=profile(aliases)
    return {
      "n_rows":n,"n_site_representative_coords":len(srep),
      "n_source_alias_representative_coords":len(arep),
      "invalid_row_counts":dict(rejected),
      "within_site_max_distance_m_minmedianmax":[
         round(min(spread)*1000,2),round(median(spread)*1000,2),round(max(spread)*1000,2)
      ] if spread else None,
      "n_site_ids_with_max_within_source_coord_spread_over_100m":
         sum(x>0.1 for x in spread),
      "n_site_ids_with_max_within_source_coord_spread_over_500m":
         sum(x>0.5 for x in spread),
      "n_site_ids_with_source_microphone_any":sum("Microphone" in v for v in methods.values()),
      "n_site_ids_with_source_ear_any":sum("Ear" in v for v in methods.values()),
      "nonidentifying_observation_rows_kept_only_in_memory":True
    },{
      "site_coords":srep,"legacy_coords":arep,
      "site_spread":{k:max(geo_km(p,v) for p in coords[k]) for k,v in srep.items()},
      "method_month":method_month,
      "visits":visits
    }

def source_codebook(item):
    # Original official XML publicly linked from USGS Data Catalog.
    u=f"https://data.usgs.gov/datacatalog/metadata/USGS.{item}.xml"
    with urlopen(Request(u,headers={"User-Agent":"frogcs-public-USGS-2003-2008-field-definition/8.2"}),timeout=40) as r:
        if r.status!=200:raise ValueError("NO_ORIGINAL_XML")
        raw=r.read(180000)
    root=ElementTree.fromstring(raw)
    wanted={"Site","Site_original","Method","Species","Number_heard","Date"}
    defs={}
    for attr in root.findall(".//attr"):
        lab="".join(attr.find("attrlabl").itertext()).strip() if attr.find("attrlabl") is not None else ""
        if lab in wanted:
            defn="".join(attr.find("attrdef").itertext()).strip() if attr.find("attrdef") is not None else ""
            if len(defn)>1250:defn=defn[:1250]
            enums=[]
            for sub in attr.findall(".//edom"):
                x=sub.find("edomv"); y=sub.find("edomvd")
                if x is not None and lab in {"Method","Number_heard","Species"}:
                    val="".join(x.itertext()).strip()
                    # Do not output taxon labels, only literal source code semantics
                    if lab!="Species":
                        enums.append({"code":val[:90],"definition":
                                      "".join(y.itertext()).strip()[:200] if y is not None else ""})
            defs[lab]={"definition":defn,"enumerations":enums[:25]}
    return {"metadata_sha256":sha256(raw).hexdigest(),
            "definitions":defs}

def id_overlap(a,b,which):
    aa=a[which];bb=b[which]
    overlap=set(aa)&set(bb)
    dist=[geo_km(aa[code],bb[code])*1000 for code in overlap]
    good={r:sum(x<=r for x in dist) for r in (10,25,50,100,250,500,1000)}
    return {"n_exact_labels":len(overlap),
            "n_with_valid_coords":len(dist),
            "between_epoch_coordinate_displacement_m_minmedianmax":
              [round(min(dist),2),round(median(dist),2),round(max(dist),2)] if dist else None,
            "n_at_or_below_distance_m":{"m"+str(k):v for k,v in good.items()},
            "n_more_than_500m_apart":sum(x>500 for x in dist),
            "cross_year_site_identity_authenticated":False}

def month_method_overlap(a,b,labels):
    shared=set(a["site_coords"])&set(b["site_coords"])
    out=Counter()
    qualifying=set()
    per_method={}
    for site in shared:
        A=a["method_month"].get(site,set())
        B=b["method_month"].get(site,set())
        common=A&B
        if common:
            out["any_exact_same_site_source_month_method"]+=1
            qualifying.add(site)
        if ("Microphone",6) in common or ("Microphone",7) in common or ("Microphone",8) in common:
            out["any_source_mic_2024_Jun_Aug_same_month"]+=1
        if any(k[0]=="Ear" for k in common):out["any_ear_same_month"]+=1
    return {"exact_site_name_cross_epoch_count":len(shared),
            "same_site_with_any_matching_method_month":out["any_exact_same_site_source_month_method"],
            "same_site_with_Microphone_and_same_Jun_Aug_month":
               out["any_source_mic_2024_Jun_Aug_same_month"],
            "same_site_with_Ear_and_same_month":out["any_ear_same_month"],
            "site_age_or_species_response_reinterpreted":False,
            "matching_a_calendar_month_does_not_equal_same_night_phenology":True}

def main():
    inputs={}
    for key,item in src.ITEMS.items():
        meta,data,found=src.public_file(item)
        if found["status"]!="UNMODIFIED_PUBLIC_CSV_OBTAINED":
            raise ValueError("REQUIRED_PUBLIC_RELEASE_NOT_SINGLE_CSV")
        expected=HIST_SHA if key=="history_2003_2008" else NEW_SHA
        if sha256(data).hexdigest()!=expected:raise ValueError("HISTORIC_SOURCE_SHA_CHANGED")
        q,loc=positive_coordinates(data.decode("utf-8-sig"))
        assert q["n_rows"]==(10189 if key=="history_2003_2008" else 1934)
        inputs[key]={"simple":q,"private":loc}
    h=inputs["history_2003_2008"]["private"]
    n=inputs["new_2024"]["private"]
    out={
      "status":"SOURCE_ONLY_ORIGINAL_USGS_CROSS_EPOCH_SPATIAL_KEY_AND_OBSERVER_METHOD_AUDIT",
      "original_historic_doi":"https://doi.org/10.5066/P1X9UBHV",
      "original_2024_doi":"https://doi.org/10.5066/P19ZCGWM",
      "official_public_release_versions":"Both ver.1.1 April 2026",
      "historic_sha256":HIST_SHA,"new2024_sha256":NEW_SHA,
      "original_source_field_definitions_historic":source_codebook(src.ITEMS["history_2003_2008"]),
      "original_source_field_definitions_2024":source_codebook(src.ITEMS["new_2024"]),
      "source_grains_only":{
          key:inputs[key]["simple"] for key in src.ITEMS
      },
      "exact_site_label_geospatial_quality":id_overlap(h,n,"site_coords"),
      "exact_historic_legacy_label_geospatial_quality":id_overlap(h,n,"legacy_coords"),
      "exact_site_month_method":month_method_overlap(h,n,set()),
      "NOTE":"Original two public datasets but exact label+coordinate proximity are not an authenticated census of ecological site histories. No frog taxa detected/not-detected opened, no occupancy trends computed.",
      "no_original_coordinates_site_names_personal_ids_exported":True,
      "historical_2024_revisit_site_crosswalk_from_custodian_verified":False,
      "new_biological_response_effect_computed":False
    }
    path=Path("studies/climate_landscape/receipts/USGS_ARMI_2003_2008_2024_SITE_KEY_GEOSPATIAL_QC.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("PUBLIC_CROSS_EPOCH_SPATIAL_SOURCE_GATE "+json.dumps(out,sort_keys=True),flush=True)
if __name__=="__main__":main()
