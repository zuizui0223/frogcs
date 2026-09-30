#!/usr/bin/env python3
from __future__ import annotations

import csv, io, json, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

CALLING="5b3e4054e4b060350a0ef7e3"
WATER="5b3e4093e4b060350a0ef7f6"
SITE="SC4DAI2"
OUT=Path("exploration/STCROIX_DIRECT_HYDROLOGY_JOIN_AUDIT_V0_1.json")


def get_json(item):
    req=urllib.request.Request(
        f"https://www.sciencebase.gov/catalog/item/{item}?format=json",
        headers={"User-Agent":"frogcs-stcroix-join-audit/0.1","Accept":"application/json"}
    )
    with urllib.request.urlopen(req,timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-stcroix-join-audit/0.1"})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()


def file_url(f):
    return f.get("downloadUri") or f.get("url") or f.get("uri")


def exact_csv(item_id,name):
    obj=get_json(item_id)
    hits=[f for f in obj.get("files") or [] if (f.get("name") or "")==name]
    if len(hits)!=1:
        raise RuntimeError(f"expected one exact file {name}, found {len(hits)}")
    b=get_bytes(file_url(hits[0]))
    rows=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    return rows


def parse_date(x):
    s=str(x or "").strip()
    for fmt in ("%m/%d/%Y","%m/%d/%y","%Y-%m-%d"):
        try:
            return datetime.strptime(s,fmt).date()
        except ValueError:
            pass
    raise RuntimeError(f"unparseable date {s!r}")


def num(x):
    try:
        v=float(str(x or "").strip())
        return v if v==v else None
    except Exception:
        return None


def main():
    calling=exact_csv(CALLING,"Daily Calling activity Pcrucifer SC4DAI2 2008to2012.csv")
    water=exact_csv(WATER,"Median daily water depths.csv")
    call_col=[c for c in calling[0] if "integrand" in c.lower()]
    if len(call_col)!=1:
        raise RuntimeError(f"calling column ambiguity: {call_col}")
    call_col=call_col[0]
    depth_col="Median water depth (m)"
    if depth_col not in water[0]:
        raise RuntimeError("water-depth column missing")

    sites=sorted({str(r.get("Site") or "").strip() for r in water if str(r.get("Site") or "").strip()})
    exact_present=SITE in sites
    water_site=[r for r in water if str(r.get("Site") or "").strip()==SITE]

    c_by={}
    c_dups=0
    for r in calling:
        d=parse_date(r["Date"])
        v=num(r[call_col])
        if v is None:
            continue
        if d in c_by:
            c_dups+=1
        c_by[d]=v

    w_by={}
    w_dups=0
    for r in water_site:
        d=parse_date(r["Date"])
        v=num(r[depth_col])
        if v is None:
            continue
        if d in w_by:
            w_dups+=1
        w_by[d]=v

    overlap=sorted(set(c_by)&set(w_by))
    years=Counter(d.year for d in overlap)
    call_zero=sum(c_by[d]==0 for d in overlap)
    depth_zero=sum(w_by[d]==0 for d in overlap)
    both_zero=sum(c_by[d]==0 and w_by[d]==0 for d in overlap)
    call_positive_depth_zero=sum(c_by[d]>0 and w_by[d]==0 for d in overlap)

    # Eligibility only: no correlation/regression or outcome-conditioned selection.
    gate=bool(
        exact_present
        and c_dups==0 and w_dups==0
        and len(overlap)>=100
        and len(years)>=3
        and call_zero>0
    )

    out={
      "analysis":"stcroix_direct_hydrology_join_audit_v0_1",
      "parent_contract":"exploration/STCROIX_DIRECT_HYDROLOGY_ELIGIBILITY_CONTRACT_V0_1.json",
      "site":SITE,
      "water_site_exact_match_present":exact_present,
      "water_site_values":sites,
      "calling_rows_numeric":len(c_by),
      "water_rows_numeric_at_site":len(w_by),
      "duplicate_calling_dates":c_dups,
      "duplicate_water_dates":w_dups,
      "overlap":{
        "n_dates":len(overlap),
        "years":{str(k):int(v) for k,v in sorted(years.items())},
        "n_years":len(years),
        "first_date":overlap[0].isoformat() if overlap else None,
        "last_date":overlap[-1].isoformat() if overlap else None,
        "calling_zero_days":int(call_zero),
        "water_zero_days":int(depth_zero),
        "both_zero_days":int(both_zero),
        "calling_positive_water_zero_days":int(call_positive_depth_zero)
      },
      "eligibility_gate_pass":gate,
      "relationship_endpoint_read":False,
      "interpretation_boundary":{
        "exact_siteid_required":True,
        "no_alias_mapping_used":True,
        "correlation_or_regression_computed":False
      }
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
