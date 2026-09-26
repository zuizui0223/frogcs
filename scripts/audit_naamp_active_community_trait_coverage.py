#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib.util, io, json, urllib.request
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("pulse_base",ROOT/"run_naamp_ecological_pulse.py")
base=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(base)

AMPHIBIO_URL="https://raw.githubusercontent.com/rdmpage/amphibio/c437acbc65b51b66e3dc4abd821ebe1cb06b200c/AmphiBIO_v1.csv"
AMPHIBIO_BLOB_SHA1="f98650972f3266c24962f70738799a39a8310e87"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
TRAITS=[
"Body_size_mm","Litter_size_min_n","Litter_size_max_n",
"Offspring_size_min_mm","Offspring_size_max_mm","Reproductive_output_y",
"Age_at_maturity_min_y","Age_at_maturity_max_y","Longevity_max_y"
]

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-community-trait-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def blobsha(b):
    h=hashlib.sha1();h.update(f"blob {len(b)}\0".encode());h.update(b);return h.hexdigest()

def norm(x):
    toks=str(x or "").strip().split()
    return " ".join(toks[:2]) if len(toks)>=2 else str(x or "").strip()

def traits():
    b=fetch_bytes(AMPHIBIO_URL)
    if blobsha(b)!=AMPHIBIO_BLOB_SHA1:raise SystemExit("AmphiBIO drift")
    try:t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError:t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["species_norm"]=t["Species"].map(norm)
    return t

def match(sp,t):
    idx={s:i for i,s in enumerate(t["species_norm"])}
    c=[sp]; toks=sp.split()
    if len(toks)==2 and toks[0] in ALIASES:c.append(ALIASES[toks[0]]+" "+toks[1])
    hits=[x for x in c if x in idx]
    if sp in hits:return t.iloc[idx[sp]],"exact"
    if len(hits)==1:return t.iloc[idx[hits[0]]],"alias"
    return None,None

def main():
    raw=base.load(); runs,sets=base.build_runs(raw)
    freq=Counter()
    for rid,spp in sets.items():
        if rid not in set(runs["RunID"].astype(str)):continue
        for sp in spp:freq[norm(sp)]+=1
    universe=sorted(freq)
    t=traits()
    rows=[];audit=[]
    for sp in universe:
        tr,kind=match(sp,t)
        audit.append({"naamp_species":sp,"matched":tr is not None,"match_type":kind,
                      "run_incidences":int(freq[sp]),
                      "amphibio_species":None if tr is None else str(tr["species_norm"])})
        if tr is not None:
            row={"species":sp,"run_incidences":freq[sp]}
            for c in TRAITS:row[c]=pd.to_numeric(tr.get(c,np.nan),errors="coerce")
            rows.append(row)
    d=pd.DataFrame(rows)
    report={}
    n=len(universe)
    for c in TRAITS:
        valid=np.isfinite(d[c])
        spp_complete=int(valid.sum())
        incid_complete=int(d.loc[valid,"run_incidences"].sum())
        total_incid=int(sum(freq.values()))
        x=d.loc[valid,c]
        report[c]={
          "complete_species":spp_complete,
          "fraction_unique_species":float(spp_complete/n),
          "covered_run_species_incidences":incid_complete,
          "fraction_run_species_incidences":float(incid_complete/total_incid),
          "nonzero_variance":bool(len(x)>1 and float(x.var(ddof=0))>0),
          "min":None if len(x)==0 else float(x.min()),
          "max":None if len(x)==0 else float(x.max())
        }
    panel=["Body_size_mm","Litter_size_min_n","Litter_size_max_n",
           "Offspring_size_min_mm","Offspring_size_max_mm","Reproductive_output_y"]
    complete=np.ones(len(d),dtype=bool)
    for c in panel:complete &= np.isfinite(d[c].to_numpy(float))
    panel_spp=set(d.loc[complete,"species"])
    panel_incid=sum(freq[s] for s in panel_spp)
    result={
      "analysis":"naamp_active_community_functional_trait_coverage_audit_v0_1",
      "contract":"NAAMP_ACTIVE_COMMUNITY_TRAIT_COVERAGE_AUDIT_CONTRACT_V0_1.json",
      "eligible_runs":int(len(runs)),
      "active_species_unique":int(n),
      "active_run_species_incidences":int(sum(freq.values())),
      "matched_species_unique":int(len(d)),
      "matched_fraction_unique":float(len(d)/n),
      "matched_run_species_incidences":int(sum(freq[a["naamp_species"]] for a in audit if a["matched"])),
      "trait_coverage":report,
      "candidate_six_field_panel":{
        "fields":panel,
        "complete_species":int(len(panel_spp)),
        "fraction_unique_species":float(len(panel_spp)/n),
        "fraction_run_species_incidences":float(panel_incid/sum(freq.values()))
      },
      "unmatched_species":[a for a in audit if not a["matched"]],
      "response_values_read":False,
      "response_models_fit":False
    }
    Path("NAAMP_ACTIVE_COMMUNITY_TRAIT_COVERAGE_AUDIT_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
