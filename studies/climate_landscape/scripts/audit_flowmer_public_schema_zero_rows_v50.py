#!/usr/bin/env python3
"""v5.0 OFFICIAL Australian Flow-MER frog CSV metadata gateway (zero rows).

This requests CKAN DataStore with limit=0. Only field definitions, total
(if provided), and source availability status are retained. Any accidental
rows in response cause a fail-closed status; NO species/coordinates are shown,
persisted, counted by taxon, or used for ecology. No auth required.
"""
from __future__ import annotations
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE="https://data.gov.au/data/api/3/action/datastore_search"
RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
MAX_JSON=1_000_000
KNOWN={"Program","samplePoint","sampleDate","sampleDateStart","sampleDateEnd",
       "speciesCode","speciesName","CPUEAdults","callingEvidence","CPUETadpoles",
       "vegCommunity","Latitude","Longitude"}

def check_result(payload):
    if not isinstance(payload,dict) or payload.get("success") is not True:
        raise ValueError("CKAN datastore did not return success")
    result=payload.get("result")
    if not isinstance(result,dict):
        raise ValueError("invalid result")
    records=result.get("records")
    if records is None or not isinstance(records,list):
        raise ValueError("missing records list; cannot attest zero-row scope")
    if records:
        raise ValueError("NONZERO_ROWS_RETURNED; refuse all response values")
    fields=result.get("fields")
    if not isinstance(fields,list) or len(fields)>200:
        raise ValueError("unexpected field metadata")
    parsed=[]
    for f in fields:
        if not isinstance(f,dict) or not isinstance(f.get("id"),str):
            raise ValueError("malformed field record")
        parsed.append({"name":f["id"][:100],"schema_type":str(f.get("type",""))[:100]})
    if not parsed:
        raise ValueError("field list empty")
    names={x["name"] for x in parsed}
    return {"n_columns":len(parsed),"field_names_and_types":parsed,
            "declared_total_rows":result.get("total"),
            "expected_published_variable_names_present":
              {k:(k in names) for k in sorted(KNOWN)},
            "data_records_returned":0}

def self_test():
    fields=[{"id":c,"type":"text"} for c in sorted(KNOWN)]
    x={"success":True,"result":{"fields":fields,"records":[],"total":777}}
    q=check_result(x)
    assert q["n_columns"]==len(KNOWN)
    assert q["declared_total_rows"]==777
    for invalid in (
        {"success":False,"result":{"fields":fields,"records":[]}},
        {"success":True,"result":{"fields":fields,"records":[{"speciesName":"BLOCK"}]}},
        {"success":True,"result":{"fields":[],"records":[]}},
        {"success":True,"result":{"fields":fields}},
    ):
        try:check_result(invalid)
        except ValueError:pass
        else:raise AssertionError("unsafe CKAN source response accepted")
    print("PASS: zero-row CKAN source-field metadata and fail-closed unexpected data protection")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        self_test()
        return
    params=urllib.parse.urlencode({"resource_id":RESOURCE,"limit":0})
    url=BASE+"?"+params
    receipt={
        "audit":"flow_mer_2014_2022_frog_official_ckan_metadata_zero_rows_v50",
        "official_landing_page":"https://data.gov.au/data/dataset/flow-mer-frog-abundance",
        "resource_id":RESOURCE,
        "endpoint":url,
        "date_range_as_published":"2014-07-01 to 2022-06-30",
        "published_regions":["Gwydir","Murrumbidgee","Lachlan 2015"],
        "endpoint_scope":"CKAN datastore_search, limit=0; schema metadata only",
        "status":"NOT_CHECKED",
        "frog_data_analyzed":False,
        "raw_species_values_saved":False,
        "raw_coordinates_saved":False,
        "original_ocock_survey_opportunities_verified":False,
        "original_ocock_survey_join_verified":False,
        "rc6_main_unchanged":True
    }
    try:
        req=urllib.request.Request(url,headers={"Accept":"application/json",
             "User-Agent":"frogcs-FlowMER-zero-record-metadata/5.0"})
        with urllib.request.urlopen(req,timeout=35) as response:
            data=response.read(MAX_JSON+1)
            if response.status!=200 or len(data)>MAX_JSON:
                raise ValueError("unexpected status or too-large JSON metadata")
        obj=json.loads(data.decode("utf-8"))
        receipt.update(check_result(obj))
        receipt["status"]="PUBLIC_ZERO_ROW_SCHEMA_AVAILABLE"
    except urllib.error.HTTPError as exc:
        receipt.update(status="HTTP_BLOCKED",http_code=exc.code)
    except (urllib.error.URLError,TimeoutError) as exc:
        receipt.update(status="NETWORK_UNAVAILABLE",error_type=type(exc).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        receipt.update(status="NO_SAFE_ZERO_ROW_SCHEMA",error_type=type(exc).__name__,
                       error_detail=str(exc)[:180])
    out=Path("studies/climate_landscape/receipts/FLOW_MER_FROG_PUBLIC_CKAN_ZERO_ROW_SCHEMA_V50.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":receipt["status"],
       "n_columns":receipt.get("n_columns"),"http_code":receipt.get("http_code"),
       "published_fields_confirmed":receipt.get("expected_published_variable_names_present"),
       "frog_data_analyzed":False},sort_keys=True))

if __name__=="__main__":
    main()
