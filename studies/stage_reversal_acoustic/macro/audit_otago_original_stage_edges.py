#!/usr/bin/env python3
"""ONTO-TIME cross-ecosystem stage-network validity audit: Otago Harbour.

Read Mouritsen et al. (2011) Otago Harbour original food-web data, as
rehosted in an explicitly commit/blob-pinned GitHub repository.

A reciprocal pair in *compiled energy links* is NOT necessarily the
biological reversal of *directly observed predatory attacks*. Trematode and
acanthocephalan stage cycles must be identified, not counted as predation
direction switches. This source has BLANK LinkEvidence for all links.
"""
import argparse
import base64
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
import urllib.error

REPO="OlffLab/2024-LCED-networks"
COMMIT="3ce7d7e08ab4c2ccad7143757c98f9ddb496673f"
PREFIX="data/Otago_data/"
BLOBS={"Otago_Data_Links.csv":"d2c2765a8a798bbd72029c328302f095f97d095f",
       "Otago_Data_Nodes.csv":"9303b47b997945cd37842df5fd23879fe864d114"}
EXPECTED_BYTES={"Otago_Data_Links.csv":87692,"Otago_Data_Nodes.csv":34193}
PARASITE_GROUPS={"Trematode","Acanthocephalan"}
PARASITE_STAGES={"Parthinitae","Cercariae","Metacercariae","Cystacanth"}
RESULT=Path(__file__).resolve().parent/"results"/"OTAGO2011_ORIGINAL_STAGE_RECIPROCITY_PARASITE_CLASS_V0_1.json"
SPECIES=re.compile(r"^[a-z][a-z-]+$")

def githash(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def retrieve(name):
    path=PREFIX+name
    url=f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"ONTO-TIME-Original-Macro-Foodweb-Audit/0.2"})
        with urllib.request.urlopen(req,timeout=30) as r: raw=r.read(200_000)
    except (urllib.error.URLError,OSError):
        req=urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{path}?ref={COMMIT}",
                                   headers={"Accept":"application/vnd.github+json","User-Agent":"ONTO-TIME-Original-Macro-Foodweb-Audit/0.2"})
        with urllib.request.urlopen(req,timeout=30) as r: obj=json.load(r)
        raw=base64.b64decode(obj["content"])
    if len(raw)!=EXPECTED_BYTES[name] or githash(raw)!=BLOBS[name]:
        raise ValueError("original source identity fails closed for "+name)
    return raw

def csv_rows(content):
    with io.TextIOWrapper(io.BytesIO(content),encoding="utf-8-sig",newline="") as text:
        return list(csv.DictReader(text))

def taxon(node):
    if not node or not node.get("Genus") or not SPECIES.fullmatch(node.get("SpecificEpithet") or ""):
        return None
    return node["Genus"]+" "+node["SpecificEpithet"]

def build(links,nodes):
    index={x["NodeID"]:x for x in nodes}
    if len(index)!=len(nodes):
        raise ValueError("duplicate source node")
    by_pair=defaultdict(list)
    evidence=Counter()
    groups=Counter()
    stages=Counter()
    for node in nodes:
        groups[node["OrganismalGroup"]]+=1
        stages[node["Stage"]]+=1
    n_stage_species_edges=0
    for e in links:
        evidence[e["LinkEvidence"].strip() or "BLANK"]+=1
        pred=index.get(e["ConsumerNodeID"])
        prey=index.get(e["ResourceNodeID"])
        if pred is None or prey is None:
            raise ValueError("dangling source link")
        p=taxon(pred);q=taxon(prey)
        if not p or not q or p==q or not pred["Stage"] or not prey["Stage"]:
            continue
        n_stage_species_edges+=1
        pair="::".join(sorted([p,q]))
        by_pair[pair].append({
            "pred":p,"prey":q,"pred_stage":pred["Stage"],"prey_stage":prey["Stage"],
            "pred_group":pred["OrganismalGroup"],"prey_group":prey["OrganismalGroup"],
            "linktype":e["LinkType"],"source_link_evidence":e["LinkEvidence"] or None
        })
    candidates=[]
    for key,edges in by_pair.items():
        left,right=key.split("::")
        a=[e for e in edges if e["pred"]==left]
        b=[e for e in edges if e["pred"]==right]
        if not a or not b:
            continue
        different=any(x["pred_stage"]!=y["prey_stage"] or x["prey_stage"]!=y["pred_stage"] for x in a for y in b)
        parasite=any(e["pred_group"] in PARASITE_GROUPS or e["prey_group"] in PARASITE_GROUPS or
                     e["pred_stage"] in PARASITE_STAGES or e["prey_stage"] in PARASITE_STAGES for e in edges)
        candidates.append({
            "pair":key,"n_links":len(edges),"structural_stage_difference":different,
            "includes_parasite_source_group_or_stage":parasite,
            "distinct_group_pairs":sorted({e["pred_group"]+" / "+e["prey_group"] for e in edges}),
            "stage_edge_summaries":sorted({e["pred_stage"]+" -> "+e["prey_stage"] for e in edges}),
            "evidence_label_complete":all(e["source_link_evidence"] for e in edges)
        })
    candidates.sort(key=lambda x:x["pair"])
    staged=[x for x in candidates if x["structural_stage_difference"]]
    total={
      "n_source_nodes":len(nodes),"n_source_links":len(links),
      "source_link_evidence":dict(evidence),
      "n_species_level_stage_resolved_nonself_edges":n_stage_species_edges,
      "n_unique_species_pairs_at_least_one_direction":len(by_pair),
      "n_structural_reciprocal_species_pairs":len(candidates),
      "n_reciprocal_with_stage_difference":len(staged),
      "n_stage_difference_pairs_with_parasite":sum(x["includes_parasite_source_group_or_stage"] for x in staged),
      "n_stage_difference_pairs_without_parasite":sum(not x["includes_parasite_source_group_or_stage"] for x in staged),
      "n_nonparasite_reciprocal_pairs":sum(not x["includes_parasite_source_group_or_stage"] for x in candidates),
      "n_stage_shift_candidates_certified_direct_attack":0 if set(evidence)=={"BLANK"} else None
    }
    return total,candidates,{"node_stage_counts":dict(stages),"organismal_groups":dict(groups)}

def validate(totals,candidates,reference):
    ref=json.loads(Path(reference).read_text(encoding="utf-8"))
    assert totals==ref["totals"],"source totals differ from frozen result"
    assert candidates==ref["candidate_pairs"],"source-stage network edge identities differ"
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--reference",default=str(RESULT))
    a=p.parse_args()
    raw={k:retrieve(k) for k in BLOBS}
    summary,candidates,nodes=build(csv_rows(raw["Otago_Data_Links.csv"]),csv_rows(raw["Otago_Data_Nodes.csv"]))
    checked=validate(summary,candidates,a.reference)
    result={"status":"OTAGO_ORIGINAL_STAGE_NETWORK_EXACT_READBACK",
       "source":"Mouritsen et al. (2011) Ecology, DOI 10.1890/11-0371.1",
       "rehosted_code_repo":REPO,"pinned_commit":COMMIT,"pinned_source_blob_sha":BLOBS,
       "totals":summary,"node_summary":nodes,
       "all_stage_reverse_candidates_involve_parasite":summary["n_stage_difference_pairs_without_parasite"]==0,
       "original_source_readback_exact":checked,
       "limitation":"Stage-specific food-web energy links with blank original LinkEvidence; no source-level direct predation trials, true reversal dates, or acoustic risk events."}
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"totals":summary,"exact":checked},ensure_ascii=False))
if __name__=="__main__":
    main()
