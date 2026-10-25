#!/usr/bin/env python3
"""Original Mouritsen et al. 2011 Otago Harbour stage-network ontology audit.

The original CSV is typed: Predation is not Macroparasitism, Trophic
Transmission, or Concomitant Predation on Symbionts. Mixed-type reciprocity
cannot be counted as a predator/prey direction switch.

Source-original 2011 network: 180 nodes, 1924 links; this GitHub mirror
is NOT a 2024 field dataset. Blank LinkEvidence cannot certify direct attacks.
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
        req=urllib.request.Request(url,headers={"User-Agent":"ONTO-TIME-Original-Foodweb-Audit/0.2"})
        with urllib.request.urlopen(req,timeout=30) as r: raw=r.read(200_000)
    except (urllib.error.URLError,OSError):
        req=urllib.request.Request(f"https://api.github.com/repos/{REPO}/contents/{path}?ref={COMMIT}",
                                   headers={"Accept":"application/vnd.github+json","User-Agent":"ONTO-TIME-Original-Foodweb-Audit/0.2"})
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

def source_stage_edges(links,nodes):
    index={x["NodeID"]:x for x in nodes}
    if len(index)!=len(nodes):
        raise ValueError("duplicate source node")
    evidence=Counter()
    categories=Counter()
    node_group=Counter(x["OrganismalGroup"] for x in nodes)
    node_stage=Counter(x["Stage"] for x in nodes)
    stage_edges=[]
    for e in links:
        evidence[e["LinkEvidence"].strip() or "BLANK"]+=1
        categories[e["LinkType"]]+=1
        a=index.get(e["ConsumerNodeID"])
        b=index.get(e["ResourceNodeID"])
        if a is None or b is None:
            raise ValueError("dangling source node")
        pred=taxon(a);prey=taxon(b)
        if not pred or not prey or pred==prey or not a["Stage"] or not b["Stage"]:
            continue
        stage_edges.append({
            "pred":pred,"prey":prey,"pred_stage":a["Stage"],"prey_stage":b["Stage"],
            "pred_group":a["OrganismalGroup"],"prey_group":b["OrganismalGroup"],
            "linktype":e["LinkType"],"source_link_evidence":e["LinkEvidence"] or None
        })
    return {
        "n_source_nodes":len(nodes),"n_source_links":len(links),
        "source_link_evidence":dict(evidence),
        "original_interaction_categories":dict(categories),
        "node_stage_counts":dict(node_stage),
        "organismal_groups":dict(node_group),
    },stage_edges

def reciprocal_scan(edges):
    """Return *structural* reciprocals only; never pretend observational proof."""
    by_pair=defaultdict(list)
    for e in edges:
        pair="::".join(sorted([e["pred"],e["prey"]]))
        by_pair[pair].append(e)
    candidates=[]
    for key,ed in by_pair.items():
        a,b=key.split("::")
        left=[e for e in ed if e["pred"]==a]
        right=[e for e in ed if e["pred"]==b]
        if not left or not right:
            continue
        diff=any(e["pred_stage"]!=f["prey_stage"] or e["prey_stage"]!=f["pred_stage"]
                 for e in left for f in right)
        parasite=any(
            e["pred_group"] in PARASITE_GROUPS or e["prey_group"] in PARASITE_GROUPS or
            e["pred_stage"] in PARASITE_STAGES or e["prey_stage"] in PARASITE_STAGES
            for e in ed
        )
        candidates.append({
           "pair":key,"n_links":len(ed),
           "structural_stage_difference":diff,
           "includes_parasite_source_group_or_stage":parasite,
           "original_link_types":sorted(set(e["linktype"] for e in ed)),
           "distinct_group_pairs":sorted({e["pred_group"]+" / "+e["prey_group"] for e in ed}),
           "stage_edge_summaries":sorted({e["pred_stage"]+" -> "+e["prey_stage"] for e in ed}),
           "evidence_label_complete":all(e["source_link_evidence"] for e in ed),
        })
    candidates.sort(key=lambda e:e["pair"])
    return {"n_stage_species_edges":len(edges),
            "n_unique_species_pairs":len(by_pair),
            "n_reciprocal_pairs":len(candidates),
            "n_stage_shift_structural_pairs":sum(e["structural_stage_difference"] for e in candidates),
            "n_stage_shift_pairs_including_parasite":
                sum(e["structural_stage_difference"] and e["includes_parasite_source_group_or_stage"] for e in candidates),
            "n_stage_shift_pairs_nonparasite":
                sum(e["structural_stage_difference"] and not e["includes_parasite_source_group_or_stage"] for e in candidates),
            "n_nonparasite_reciprocal_pairs":
                sum(not e["includes_parasite_source_group_or_stage"] for e in candidates)
           },candidates

def build(links,nodes):
    evidence,edges=source_stage_edges(links,nodes)
    mixed,pairs=reciprocal_scan(edges)
    strict,strict_pairs=reciprocal_scan([e for e in edges if e["linktype"]=="Predation"])
    nonpara,_=reciprocal_scan([e for e in edges if
                e["pred_group"] not in PARASITE_GROUPS and e["prey_group"] not in PARASITE_GROUPS])
    totals={
      "n_source_nodes":evidence["n_source_nodes"],"n_source_links":evidence["n_source_links"],
      "source_link_evidence":evidence["source_link_evidence"],
      "original_interaction_categories":evidence["original_interaction_categories"],
      "n_species_level_stage_resolved_nonself_edges_mixed_types":mixed["n_stage_species_edges"],
      "n_unique_species_pairs_mixed_types":mixed["n_unique_species_pairs"],
      "n_structural_reciprocal_species_pairs_mixed_types":mixed["n_reciprocal_pairs"],
      "n_reciprocal_stage_shift_candidates_mixed_types":mixed["n_stage_shift_structural_pairs"],
      "n_mixed_stage_shift_candidates_including_parasite":mixed["n_stage_shift_pairs_including_parasite"],
      "n_mixed_stage_shift_candidates_nonparasite":mixed["n_stage_shift_pairs_nonparasite"],
      "n_nonparasite_structural_reciprocal_pairs_mixed_types":mixed["n_nonparasite_reciprocal_pairs"],
      "n_species_level_stage_resolved_nonself_edges_predation_only":strict["n_stage_species_edges"],
      "n_unique_species_pairs_predation_only":strict["n_unique_species_pairs"],
      "n_structural_reciprocal_species_pairs_predation_only":strict["n_reciprocal_pairs"],
      "n_reciprocal_stage_shift_candidates_predation_only":strict["n_stage_shift_structural_pairs"],
      "n_nonparasite_structural_reciprocal_pairs":nonpara["n_reciprocal_pairs"],
      "n_nonparasite_stage_shift_candidates":nonpara["n_stage_shift_structural_pairs"],
      "n_certified_direct_attack_stage_switches":0 if
          set(evidence["source_link_evidence"])=={"BLANK"} else None
    }
    return totals,pairs,strict_pairs,{"node_stage_counts":evidence["node_stage_counts"],
                                     "organismal_groups":evidence["organismal_groups"]}

def validate(totals,candidates,predation_pairs,reference):
    ref=json.loads(Path(reference).read_text(encoding="utf-8"))
    assert totals==ref["totals"],"source totals differ from frozen result"
    assert {x["pair"]:x for x in candidates}=={x["pair"]:x for x in ref["mixed_interaction_type_reciprocity"]},"source mixed-type pairs differ"
    assert {x["pair"]:x for x in predation_pairs}=={x["pair"]:x for x in ref["predation_only_reciprocity"]},"source predation pairs differ"
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--reference",default=str(RESULT))
    a=p.parse_args()
    raw={name:retrieve(name) for name in BLOBS}
    totals,candidates,predation_pairs,nodes=build(csv_rows(raw["Otago_Data_Links.csv"]),
                                                  csv_rows(raw["Otago_Data_Nodes.csv"]))
    checked=validate(totals,candidates,predation_pairs,a.reference)
    result={"status":"OTAGO_ORIGINAL_TYPED_STAGE_NETWORK_EXACT_READBACK",
      "source":"Mouritsen et al. (2011) Ecology, DOI 10.1890/11-0371.1",
      "rehosted_code_repo":REPO,"pinned_commit":COMMIT,"pinned_source_blob_sha":BLOBS,
      "totals":totals,"source_node_stage_summary":nodes,
      "all_apparent_stage_shift_pairs_involve_parasite":totals["n_mixed_stage_shift_candidates_nonparasite"]==0,
      "original_source_readback_exact":checked,
      "limitation":"Typed nutrition/parasitism links, but every original LinkEvidence is blank; no directly certified stage-dependent attack reversal, exact time, or acoustic risk receiver record."}
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"totals":totals,"exact":checked},ensure_ascii=False))
if __name__=="__main__":
    main()
