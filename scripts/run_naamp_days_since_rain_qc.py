#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, math, re, urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

ITEM_ID="583dc314e4b0d1899f9dea8d"
ITEM_URL=f"https://www.sciencebase.gov/catalog/item/{ITEM_ID}?format=json"
PIN="ec6b314fe4cd8ec8c048a973e576c8810ea12b21c739c1140e3a12123c611730"
SENTINELS=[-9999,-999,-99,-9,99,999,9999]

def get_json(url):
    q=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-rain-qc/0.1","Accept":"application/json"})
    with urllib.request.urlopen(q,timeout=60) as r:
        return json.loads(r.read().decode())

def get_bytes(url):
    q=urllib.request.Request(url,headers={"User-Agent":"frog-naamp-rain-qc/0.1"})
    with urllib.request.urlopen(q,timeout=120) as r:
        return r.read()

def year(x):
    m=re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)",str(x or ""))
    return int(m.group(1)) if m else None

def main():
    item=get_json(ITEM_URL)
    f=next(x for x in item.get("files",[]) if (x.get("name") or "")=="Runs.csv")
    b=get_bytes(f.get("downloadUri") or f.get("url") or f.get("uri"))
    sha=hashlib.sha256(b).hexdigest()
    if sha!=PIN:
        raise RuntimeError(f"Runs.csv hash drift {sha}")

    rows=list(csv.DictReader(io.StringIO(b.decode("utf-8-sig"))))
    tokens=[]
    numeric=[]
    eligible=[]
    nonnumeric=Counter()

    for r in rows:
        y=year(r.get("SurveyYear")) or year(r.get("SurveyDate"))
        if y is None or not 2001<=y<=2015 or (r.get("UnifiedProtocol") or "").strip()!="1":
            continue
        raw=(r.get("DaysSinceRain") or "").strip()
        tokens.append(raw)
        if not raw:
            nonnumeric["blank"]+=1
            continue
        try:
            v=float(raw)
        except Exception:
            nonnumeric[raw]+=1
            continue
        if not math.isfinite(v):
            nonnumeric[raw]+=1
            continue
        numeric.append(v)
        if v>=0:
            eligible.append(v)

    a=np.asarray(numeric,float)
    e=np.asarray(eligible,float)
    quantiles={str(q):float(np.quantile(e,q)) for q in [0,0.001,0.01,0.05,0.25,0.5,0.75,0.95,0.99,0.999,1]} if len(e) else {}
    exact=Counter(float(x) for x in numeric)

    result={
      "analysis":"naamp_days_since_rain_qc_v0_1",
      "contract":"NAAMP_DAYS_SINCE_RAIN_QC_CONTRACT_V0_1.json",
      "runs_sha256":sha,
      "eligible_protocol_rows":len(tokens),
      "numeric_rows":len(numeric),
      "nonnegative_rows":len(eligible),
      "negative_rows":int(np.sum(a<0)) if len(a) else 0,
      "nonnumeric_or_blank":dict(sorted(nonnumeric.items())),
      "predeclared_sentinel_counts":{str(x):int(exact.get(float(x),0)) for x in SENTINELS},
      "nonnegative_quantiles_days":quantiles,
      "extreme_counts":{f"ge_{x}":int(np.sum(e>=x)) for x in [30,60,90,99]} if len(e) else {},
      "top_nonnegative_values": [
          {"value":v,"count":c}
          for v,c in Counter(float(x) for x in eligible).most_common(25)
      ],
      "integer_valued_fraction":float(np.mean(np.isclose(e,np.round(e)))) if len(e) else None,
      "outcome_values_read":False,
      "model_change_authorized":False
    }
    Path("frog_naamp_days_since_rain_qc_v0_1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
