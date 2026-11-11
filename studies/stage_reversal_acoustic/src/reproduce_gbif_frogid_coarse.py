#!/usr/bin/env python3
"""Verify GBIF/FrogID source event coverage without redistributing sensitive point records.

DESCRIPTIVE SOURCE AUDIT ONLY. No species absence, predator-switch time, or
acoustic warning/causal effect is identified by this dataset.
"""
import argparse
import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

DATASET="47c9fee2-619a-481c-a114-386bc4748256"
URL="https://api.gbif.org/v1/occurrence/search"
DATES="2018-09-04,2019-04-09"
BOX={"decimalLatitude":"-33.25,-32.55","decimalLongitude":"151.2,152.0"}
FOCAL_TAXON_KEY=10595763  # GBIF accepted synonym Ranoidea aurea (source Litoria aurea)
COMPARE_KEYS=("week_start","species_rows","unique_recording_events",
              "records_with_event_id","focal_positive_recording_events")


def week_start(text):
    d=dt.date.fromisoformat(text[:10])
    return (d-dt.timedelta(days=d.weekday())).isoformat()


def aggregate(records):
    grouped=defaultdict(lambda:{"rows":0,"identified_rows":0,"events":set(),"focal":set()})
    for a in records:
        if a.get("datasetKey")!=DATASET:
            raise ValueError("not FrogID source dataset")
        when=a.get("eventDate","")[:10]
        if not when or not ("2018-09-04" <= when <= "2019-04-09"):
            raise ValueError("eventDate outside frozen window")
        wk=week_start(when)
        g=grouped[wk]
        g["rows"]+=1
        eid=a.get("eventID")
        if eid is not None and str(eid).strip():
            g["identified_rows"]+=1
            g["events"].add(str(eid))
        if int(a.get("acceptedTaxonKey") or -1)==FOCAL_TAXON_KEY:
            if not eid:
                raise ValueError("focal eventID absent; cannot deduplicate")
            g["focal"].add(str(eid))
    start=dt.date(2018,9,3)
    output=[]
    for i in range(32):
        week=(start+dt.timedelta(weeks=i)).isoformat()
        g=grouped[week]
        output.append({"week_start":week,"species_rows":g["rows"],
                       "records_with_event_id":g["identified_rows"],
                       "unique_recording_events":len(g["events"]),
                       "focal_positive_recording_events":len(g["focal"])})
    return output


def fetch_page(offset,limit=300):
    parameters={"datasetKey":DATASET,"eventDate":DATES,**BOX,"limit":limit,"offset":offset}
    address=URL+"?"+urllib.parse.urlencode(parameters)
    request=urllib.request.Request(address,headers={
        "User-Agent":"StageAcousticOriginalDataVerification/0.1",
        "Accept":"application/json"})
    last=None
    for delay in (0,2,6):
        if delay:time.sleep(delay)
        try:
            with urllib.request.urlopen(request,timeout=35) as response:
                result=json.load(response)
            if not isinstance(result.get("count"),int) or not isinstance(result.get("results"),list):
                raise ValueError("malformed original API response")
            return result
        except (urllib.error.URLError,TimeoutError,ValueError,ConnectionError) as exc:
            last=exc
    raise RuntimeError("source API unavailable; no biological conclusion: "+str(last))


def retrieve_source():
    rows=[]; expected=None;offset=0
    while expected is None or offset<expected:
        source=fetch_page(offset)
        expected=source["count"]
        batch=source["results"]
        if not batch or expected>100000:
            raise ValueError("source pagination invalid or exceeds declared narrow scope")
        rows.extend(batch)
        offset+=len(batch)
    if len(rows)!=expected:
        raise ValueError("source row count changed during pagination")
    return aggregate(rows)


def validate(observed,receipt):
    frozen=receipt["weekly_source_aggregate"]
    if len(observed)!=len(frozen):
        raise ValueError("non-32-week source")
    diffs=[]
    for a,b in zip(observed,frozen):
        for key in COMPARE_KEYS:
            if a.get(key)!=b.get(key):
                diffs.append({"week":a["week_start"],"field":key,
                              "source":a.get(key),"frozen":b.get(key)})
    return {
      "status":"ORIGINAL_GBIF_AGGREGATE_MATCH" if not diffs else "SOURCE_VERSION_DRIFT",
      "matched_frozen_2026_10_25_readback":not diffs,
      "source_dataset":"FrogID (GBIF dataset 47c9fee2-619a-481c-a114-386bc4748256)",
      "scope":"2018-09-04..2019-04-09; coarse geoprivacy-safe Newcastle macro region",
      "species_rows":sum(z["species_rows"] for z in observed),
      "recordings_with_eventID":sum(z["unique_recording_events"] for z in observed),
      "rows_missing_eventID":sum(z["species_rows"]-z["records_with_event_id"] for z in observed),
      "focal_species_positive_recordings":sum(z["focal_positive_recording_events"] for z in observed),
      "differences":diffs[:10],
      "scope_limit":"Only acoustic-positive source records; cannot infer precise wetland overlap, alarm or independent seasonal predictive validity."
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--receipt",default=str(Path(__file__).resolve().parents[1]/"results"/"FROGID_ANAX_COARSE_WEEKLY_REAL_2018_2019_V1.json"))
    parser.add_argument("--out",required=True)
    parser.add_argument("--strict",action="store_true")
    args=parser.parse_args()
    frozen=json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    verified=validate(retrieve_source(),frozen)
    Path(args.out).write_text(json.dumps(verified,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(verified,indent=2))
    if args.strict and verified["status"]!="ORIGINAL_GBIF_AGGREGATE_MATCH":
        raise SystemExit("SOURCE_VERSION_DRIFT_NOT_VALIDATED")


if __name__=="__main__":
    main()
