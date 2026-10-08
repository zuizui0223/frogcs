#!/usr/bin/env python3
"""Check Sarker et al. 2022 published Table-2 EXPOSURES, no frog outcomes.

This source-only audit inventories the site/flow windows with zero *reported*
local 24-h rainfall before and after water arrival. It is NOT a new biological
effect test and does not read the paper's frog responses.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path("studies/climate_landscape")
DATA=ROOT/"reference_routes/GWYDIR_SARKER_2022_SIX_SITE_EXPOSURE_TABLE2_V39.csv"
OUT=ROOT/"receipts/GWYDIR_SARKER_RAIN_WATER_DECOUPLING_SOURCE_AUDIT_V39.json"
ALLOWED={
    "site_id","site_name","site_type","hydroperiod_class",
    "rain_before_mm","rain_after_mm","min_temp_before_c","min_temp_after_c",
    "recording_before","recording_after","post_nights_reported","exposure_only",
}
EXPECTED=["ALLB","CARC","CMBD","GINW","GNDR","TYRL"]
def audit():
    raw=DATA.read_bytes()
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(rows)!=6:
        raise ValueError("Published Table-2 site count mismatch")
    if not rows or set(rows[0])!=ALLOWED or len(rows[0])!=len(ALLOWED):
        raise ValueError("Wrong source-only header shape")
    if sorted(x["site_id"] for x in rows)!=EXPECTED:
        raise ValueError("Published six sites mismatch")
    if any(x.get("exposure_only")!="true" for x in rows):
        raise ValueError("All rows must be source-only exposures")
    if any(x["hydroperiod_class"] not in ("Permanent","Temporary") for x in rows):
        raise ValueError("Missing site environment")
    for row in rows:
        for f in ("rain_before_mm","rain_after_mm","min_temp_before_c","min_temp_after_c"):
            float(row[f])
        nights=int(row["post_nights_reported"])
        if nights not in (3,4):raise ValueError("Invalid observed-night metadata")
    zero_both=sorted(x["site_id"] for x in rows if float(x["rain_before_mm"])==0 and float(x["rain_after_mm"])==0)
    if zero_both!=["ALLB","GNDR"]:
        raise ValueError("Source Table-2 no-rain flow-arrival pair changed")
    rain_groups=Counter()
    for x in rows:
        p,q=float(x["rain_before_mm"]),float(x["rain_after_mm"])
        group=("zero_both" if p==0 and q==0 else
               "zero_before_some_after" if p==0 and q>0 else
               "rain_before_zero_after" if p>0 and q==0 else "other")
        rain_groups[group]+=1
    if dict(rain_groups)!={"zero_both":2,"zero_before_some_after":3,"rain_before_zero_after":1}:
        raise ValueError("Rainfall strata no longer match original published table")
    rec={
        "audit":"sarker_2022_gwydir_published_table2_exposure_only_v39",
        "publication_doi":"10.1016/j.ecolind.2022.109640",
        "data_source":"published Table 2 transcribed exposure fields, not original response data",
        "input_sha256":hashlib.sha256(raw).hexdigest(),
        "n_acoustic_sites_in_paper":6,
        "local_rain_stratum_counts":dict(rain_groups),
        "no_reported_rain_both_flow_windows":zero_both,
        "n_sites_post_flow_one_night_missing":sum(x["post_nights_reported"]=="3" for x in rows),
        "caveat":"zero reported local rainfall != randomized water, no sound cue, or a causal effect; flow sounds and temperature/time remain confounded",
        "frog_outcomes_read":False,
        "biological_effect_estimated":False,
        "rc6_unchanged":True,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(rec,sort_keys=True))
if __name__=="__main__":
    audit()
