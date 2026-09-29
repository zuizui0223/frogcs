#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"exploration"/"NPS_SECN_REPLICATION_ELIGIBILITY_RECEIPT_V0_1.json"
URLS={
    "classifications":"https://irma.nps.gov/DataStore/DownloadFile/713859?Reference=2307457",
    "equipment_failures":"https://irma.nps.gov/DataStore/DownloadFile/713861?Reference=2307457",
    "metadata":"https://irma.nps.gov/DataStore/DownloadFile/713862?Reference=2307457",
}
ZERO_PAT=re.compile(r"\b(no\s*(frog|anuran|call|detection)|none detected|silence|silent|absent|absence)\b",re.I)


def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"frogcs-nps-secn-audit/0.1","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()


def decode(b):
    for enc in ("utf-8-sig","utf-8","latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    raise RuntimeError("unable to decode text")


def csv_report(b):
    text=decode(b)
    rows=list(csv.DictReader(io.StringIO(text)))
    cols=list(rows[0].keys()) if rows else []
    candidate_cols=[
        c for c in cols if any(tok in c.lower() for tok in (
            "record","audio","file","site","location","park","station","point",
            "date","time","species","tax","class","call","detect","presence",
            "absence","effort","sample","visit","night","year"
        ))
    ]
    sample_values={}
    for c in candidate_cols:
        seen=[]
        for r in rows:
            v=(r.get(c) or "").strip()
            if v and v not in seen:
                seen.append(v)
            if len(seen)>=20:
                break
        sample_values[c]=seen

    zero_like=[]
    blank_taxon_rows=0
    tax_cols=[c for c in cols if any(tok in c.lower() for tok in ("species","taxon","scientific","common","class"))]
    for i,r in enumerate(rows):
        joined=" | ".join((r.get(c) or "") for c in cols)
        if ZERO_PAT.search(joined):
            if len(zero_like)<25:
                zero_like.append({"row":i+2,"values":{c:r.get(c) for c in candidate_cols}})
        if tax_cols and all(not (r.get(c) or "").strip() for c in tax_cols):
            blank_taxon_rows+=1

    # Cardinalities for plausible recording/site/date keys.
    cardinality={}
    for c in candidate_cols:
        vals=[(r.get(c) or "").strip() for r in rows]
        non=[v for v in vals if v]
        cardinality[c]={
            "nonempty":len(non),
            "unique":len(set(non)),
        }

    return {
        "n_rows":len(rows),
        "columns":cols,
        "candidate_columns":candidate_cols,
        "candidate_sample_values":sample_values,
        "candidate_cardinality":cardinality,
        "zero_like_rows_count":sum(1 for r in rows if ZERO_PAT.search(" | ".join((r.get(c) or "") for c in cols))),
        "zero_like_examples":zero_like,
        "taxon_candidate_columns":tax_cols,
        "blank_taxon_rows":blank_taxon_rows,
    }


def metadata_report(b):
    text=decode(b)
    root=ET.fromstring(text)
    attrs=[]
    for node in root.iter():
        if node.tag.split("}")[-1]=="attribute":
            name=None
            definition=None
            for ch in node.iter():
                tag=ch.tag.split("}")[-1]
                if tag=="attributeName" and ch.text:
                    name=ch.text.strip()
                elif tag=="attributeDefinition" and ch.text:
                    definition=ch.text.strip()
            if name:
                attrs.append({"name":name,"definition":definition})
    interesting=[
        a for a in attrs
        if any(tok in ((a["name"] or "")+" "+(a["definition"] or "")).lower()
               for tok in ("record","audio","site","location","date","time","species","class",
                           "call","detect","absence","failure","equipment","effort","sample"))
    ]
    return {
        "n_attribute_definitions":len(attrs),
        "interesting_attribute_definitions":interesting,
    }


def main():
    blobs={k:fetch(u) for k,u in URLS.items()}
    class_rep=csv_report(blobs["classifications"])
    fail_rep=csv_report(blobs["equipment_failures"])
    meta_rep=metadata_report(blobs["metadata"])

    explicit_zero=bool(class_rep["zero_like_rows_count"]>0 or class_rep["blank_taxon_rows"]>0)
    result={
        "analysis":"nps_secn_replication_eligibility_v0_1",
        "contract":"exploration/MECHANISM_UNIVERSALITY_CONTRACT_V0_1.json#nps_secn_replication_eligibility",
        "source":{
            k:{"url":URLS[k],"sha256":hashlib.sha256(blobs[k]).hexdigest(),"bytes":len(blobs[k])}
            for k in blobs
        },
        "classifications":class_rep,
        "equipment_failures":fail_rep,
        "metadata":meta_rep,
        "screen":{
            "explicit_zero_or_blank_taxon_rows_present":explicit_zero,
            "automatic_matrix_eligibility":False,
            "reason":"Schema audit only. Matrix eligibility requires proof that reviewed/sampled recordings with zero anuran detections are represented, or a complete effort frame can be reconstructed after equipment failures."
        }
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
