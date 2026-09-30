#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, io, json, re, urllib.request, zipfile
from collections import Counter
from pathlib import Path

PARENT="5b3e4033e4b060350a0ef7dd"
CALLING="5b3e4054e4b060350a0ef7e3"
WATER="5b3e4093e4b060350a0ef7f6"
OUT=Path("exploration/STCROIX_DIRECT_HYDROLOGY_ELIGIBILITY_RECEIPT_V0_1.json")


def get_json(item):
    url=f"https://www.sciencebase.gov/catalog/item/{item}?format=json"
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-stcroix-audit/0.1","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-stcroix-audit/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def parse_csv_bytes(name,b):
    txt=None
    for enc in ("utf-8-sig","utf-8","cp1252"):
        try:
            txt=b.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    if txt is None:
        return None
    rows=list(csv.DictReader(io.StringIO(txt)))
    cols=list(rows[0]) if rows else []
    return rows,cols


def summarize_rows(rows,cols):
    low={c:c.lower() for c in cols}
    date_cols=[c for c in cols if any(k in low[c] for k in ("date","day"))]
    site_cols=[c for c in cols if any(k in low[c] for k in ("site","wetland","station","location"))]
    call_cols=[c for c in cols if any(k in low[c] for k in ("integrand","calling","call_activity","sound","intensity"))]
    depth_cols=[c for c in cols if any(k in low[c] for k in ("depth","water_level","waterlevel"))]
    year_cols=[c for c in cols if "year" in low[c]]

    def vals(c):
        return [(r.get(c) or "").strip() for r in rows]

    card={c:len(set(v for v in vals(c) if v)) for c in cols}
    candidate_samples={
        c:list(dict.fromkeys(v for v in vals(c) if v))[:12]
        for c in date_cols+site_cols+year_cols
    }

    numeric={}
    for c in call_cols+depth_cols:
        arr=[]
        for v in vals(c):
            try:
                x=float(v)
                if x==x:
                    arr.append(x)
            except Exception:
                pass
        numeric[c]={
            "n_numeric":len(arr),
            "n_zero":sum(x==0 for x in arr),
            "n_positive":sum(x>0 for x in arr),
            "n_negative":sum(x<0 for x in arr),
        }

    return {
        "n_rows":len(rows),
        "columns":cols,
        "candidate_date_columns":date_cols,
        "candidate_site_columns":site_cols,
        "candidate_year_columns":year_cols,
        "candidate_call_columns":call_cols,
        "candidate_depth_columns":depth_cols,
        "cardinality":card,
        "candidate_samples":candidate_samples,
        "numeric_candidate_counts":numeric,
    }


def inspect_item(item_id):
    obj=get_json(item_id)
    result={
        "item_id":item_id,
        "title":obj.get("title"),
        "files":[],
    }
    for f in obj.get("files") or []:
        name=f.get("name") or ""
        url=file_url(f)
        rec={
            "name":name,
            "contentType":f.get("contentType"),
            "size":f.get("size"),
            "url_present":bool(url),
        }
        if not url:
            result["files"].append(rec)
            continue
        b=get_bytes(url)
        rec["bytes"]=len(b)
        rec["sha256"]=hashlib.sha256(b).hexdigest()
        low=name.lower()
        if low.endswith(".csv"):
            parsed=parse_csv_bytes(name,b)
            if parsed:
                rec["table"]=summarize_rows(*parsed)
        elif low.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                members=[]
                for n in z.namelist():
                    rr={"name":n,"bytes":z.getinfo(n).file_size}
                    if n.lower().endswith(".csv"):
                        parsed=parse_csv_bytes(n,z.read(n))
                        if parsed:
                            rr["table"]=summarize_rows(*parsed)
                    members.append(rr)
                rec["archive_members"]=members
        result["files"].append(rec)
    return result


def table_summaries(item):
    out=[]
    for f in item["files"]:
        if "table" in f:
            out.append({"container":f["name"],**f["table"]})
        for m in f.get("archive_members") or []:
            if "table" in m:
                out.append({"container":f["name"],"member":m["name"],**m["table"]})
    return out


def main():
    parent=get_json(PARENT)
    calling=inspect_item(CALLING)
    water=inspect_item(WATER)
    ct=table_summaries(calling)
    wt=table_summaries(water)

    calling_schema_candidates=[
        x for x in ct
        if x["candidate_date_columns"] and x["candidate_call_columns"]
    ]
    water_schema_candidates=[
        x for x in wt
        if x["candidate_date_columns"] and x["candidate_depth_columns"]
    ]

    # Do not choose among multiple candidate files using response values.
    unique_calling_schema=(len(calling_schema_candidates)==1)
    unique_water_schema=(len(water_schema_candidates)==1)

    zero_represented=False
    if unique_calling_schema:
        x=calling_schema_candidates[0]
        zero_represented=any(
            rec.get("n_zero",0)>0
            for rec in x["numeric_candidate_counts"].values()
        )

    result={
        "analysis":"stcroix_direct_hydrology_eligibility_v0_1",
        "contract":"exploration/STCROIX_DIRECT_HYDROLOGY_ELIGIBILITY_CONTRACT_V0_1.json",
        "parent":{
            "item_id":PARENT,
            "title":parent.get("title"),
            "files":[{
                "name":f.get("name"),"size":f.get("size"),"contentType":f.get("contentType")
            } for f in (parent.get("files") or [])],
        },
        "calling_item":calling,
        "water_depth_item":water,
        "schema_gate":{
            "calling_candidate_tables":len(calling_schema_candidates),
            "water_candidate_tables":len(water_schema_candidates),
            "unique_calling_schema":unique_calling_schema,
            "unique_water_schema":unique_water_schema,
            "calling_zero_values_represented":zero_represented,
        },
        "overlap_gate_read":False,
        "response_relationship_read":False,
    }

    # Only inspect date/site overlap after schemas are unique. This is still an
    # eligibility property; no calling-water association is computed.
    if unique_calling_schema and unique_water_schema:
        c=calling_schema_candidates[0]
        w=water_schema_candidates[0]
        result["schema_gate"]["calling_selected_schema"]={
            "container":c.get("container"),"member":c.get("member"),
            "date_columns":c["candidate_date_columns"],
            "site_columns":c["candidate_site_columns"],
            "call_columns":c["candidate_call_columns"],
            "n_rows":c["n_rows"],
        }
        result["schema_gate"]["water_selected_schema"]={
            "container":w.get("container"),"member":w.get("member"),
            "date_columns":w["candidate_date_columns"],
            "site_columns":w["candidate_site_columns"],
            "depth_columns":w["candidate_depth_columns"],
            "n_rows":w["n_rows"],
        }
        result["overlap_gate_read"]=True
        result["eligibility_status"]="schema_eligible_pending_exact_date_join_audit"
    else:
        result["eligibility_status"]="not_eligible_due_to_nonunique_or_missing_schema"

    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
