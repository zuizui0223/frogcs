#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd

AMPHIBIO_URL="https://raw.githubusercontent.com/rdmpage/amphibio/c437acbc65b51b66e3dc4abd821ebe1cb06b200c/AmphiBIO_v1.csv"
AMPHIBIO_BLOB_SHA1="f98650972f3266c24962f70738799a39a8310e87"
ALIASES={"Hyla":"Dryophytes","Dryophytes":"Hyla","Lithobates":"Rana","Rana":"Lithobates"}
EXPECTED_N=29
FROZEN_SPECIES=[
"Gastrophryne carolinensis","Pseudacris crucifer","Hyla squirella","Hyla chrysoscelis",
"Lithobates catesbeianus","Lithobates palustris","Hyla femoralis","Pseudacris maculata",
"Hyla cinerea","Pseudacris ocularis","Scaphiopus holbrookii","Lithobates sphenocephalus",
"Anaxyrus terrestris","Lithobates clamitans","Pseudacris feriarum","Hyla versicolor",
"Pseudacris kalmi","Acris crepitans","Hyla chrysoscelis/versicolor",
"Pseudacris maculata/triseriata","Acris gryllus","Acris crepitans/gryllus",
"Lithobates virgatipes","Lithobates pipiens","Lithobates sylvaticus","Anaxyrus fowleri",
"Anaxyrus americanus","Pseudacris nigrita","Hyla gratiosa"
]
BINARY=["Fos","Ter","Aqu","Arb","Diu","Noc","Crepu","Dir","Lar","Viv"]
CONT=[
"Body_size_mm","Body_mass_g","Age_at_maturity_min_y","Age_at_maturity_max_y",
"Longevity_max_y","Litter_size_min_n","Litter_size_max_n","Reproductive_output_y",
"Offspring_size_min_mm","Offspring_size_max_mm"
]

def fetch_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-functional-trait-audit/0.1"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def git_blob_sha1(b):
    h=hashlib.sha1(); h.update(f"blob {len(b)}\0".encode()); h.update(b); return h.hexdigest()

def norm(x):
    toks=str(x or "").strip().split()
    return " ".join(toks[:2]) if len(toks)>=2 else str(x or "").strip()

def species_universe():
    if len(FROZEN_SPECIES)!=EXPECTED_N or len(set(FROZEN_SPECIES))!=EXPECTED_N:
        raise SystemExit("frozen species universe malformed")
    return [norm(x) for x in FROZEN_SPECIES]

def load_traits():
    b=fetch_bytes(AMPHIBIO_URL)
    if git_blob_sha1(b)!=AMPHIBIO_BLOB_SHA1: raise SystemExit("AmphiBIO drift")
    try: t=pd.read_csv(io.BytesIO(b),encoding="utf-8")
    except UnicodeDecodeError: t=pd.read_csv(io.BytesIO(b),encoding="cp1252")
    t["species_norm"]=t["Species"].map(norm)
    return t

def match(sp,t):
    idx={s:i for i,s in enumerate(t["species_norm"])}
    cands=[sp]
    toks=sp.split()
    if len(toks)==2 and toks[0] in ALIASES:
        cands.append(ALIASES[toks[0]]+" "+toks[1])
    hits=[c for c in cands if c in idx]
    if sp in hits: return t.iloc[idx[sp]],"exact"
    if len(hits)==1: return t.iloc[idx[hits[0]]],"alias"
    return None,None

def asnum(s):
    return pd.to_numeric(s,errors="coerce")

def main():
    spp=species_universe(); t=load_traits()
    matched=[]; audit=[]
    for sp in spp:
        tr,kind=match(sp,t)
        audit.append({"naamp_species":sp,"matched":tr is not None,"match_type":kind,
                      "amphibio_species":None if tr is None else str(tr["species_norm"])})
        if tr is not None:
            row={"species":sp}
            for c in BINARY+CONT: row[c]=tr.get(c,np.nan)
            matched.append(row)
    d=pd.DataFrame(matched)
    report={}
    for c in BINARY:
        x=asnum(d[c]); valid=x[x.isin([0,1])]
        counts={str(int(k)):int(v) for k,v in valid.value_counts().sort_index().items()}
        eligible=len(valid)>=18 and all(counts.get(str(k),0)>=3 for k in (0,1))
        report[c]={"type":"binary","complete":int(len(valid)),"missing":int(EXPECTED_N-len(valid)),
                   "level_counts":counts,"eligible":bool(eligible)}
    for c in CONT:
        x=asnum(d[c]); valid=x[np.isfinite(x)]
        eligible=len(valid)>=18 and float(valid.var(ddof=0))>0
        report[c]={"type":"continuous","complete":int(len(valid)),"missing":int(EXPECTED_N-len(valid)),
                   "min":None if len(valid)==0 else float(valid.min()),
                   "max":None if len(valid)==0 else float(valid.max()),
                   "sd":None if len(valid)<2 else float(valid.std(ddof=0)),
                   "eligible":bool(eligible)}
    result={
      "analysis":"amphibio_functional_trait_coverage_audit_v0_1",
      "contract":"AMPHIBIO_FUNCTIONAL_TRAIT_COVERAGE_AUDIT_CONTRACT_V0_1.json",
      "species_universe_provenance":{
        "source_workflow_run":36123858918,
        "rule":"29 response-eligible species from frozen species-pulse workflow; copied literally after repository summary was found to omit non-significant species"
      },
      "matched_species":int(len(d)),
      "unmatched_species":[a["naamp_species"] for a in audit if not a["matched"]],
      "taxonomy_audit":audit,
      "trait_coverage":report,
      "eligible_binary_traits":[c for c in BINARY if report[c]["eligible"]],
      "eligible_continuous_traits":[c for c in CONT if report[c]["eligible"]],
      "response_values_read":False,
      "response_trait_models_fit":False
    }
    Path("AMPHIBIO_FUNCTIONAL_TRAIT_COVERAGE_AUDIT_RECEIPT_V0_1.json").write_text(
      json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__": main()
