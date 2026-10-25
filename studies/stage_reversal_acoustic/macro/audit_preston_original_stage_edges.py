#!/usr/bin/env python3
"""Original Preston 2012 Quick Pond stage-resolved trophic network audit.

Read raw source files from the pinned public GloBI GitHub import at one commit.
Respect original LinkEvidence (observed/inferred/modelled) and stage labels.
Pure standard library, outputs only evidence classifications and aggregates.
No species-level reciprocal *candidate* is elevated to direct ontogenetic
switch without observed evidence for both trophic directions.
"""
import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.request
import urllib.error
import base64

REPO="globalbioticinteractions/preston2012"
COMMIT="10676b041317d933f16c089b819f6669da42396b"
SOURCE_SHA={
 "Quick_Pond_Links.csv":"98c45c7a2081976f0a4c31db3c6646686b8277fa",
 "Quick_Pond_Nodes.csv":"201dc6ace08a26d4d07825f6bae6a295bd735adc"
}
EXPECTED_FILE_BYTES={"Quick_Pond_Links.csv":151964,"Quick_Pond_Nodes.csv":33833}
ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"results"/"PRESTON2012_ORIGINAL_STAGE_RECIPROCITY_EVIDENCE_TIER_V0_1.json"
NAME_RE=re.compile(r"^[a-z][a-z-]+$")

def git_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def download_original(filename):
    url=f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{filename}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={
            "User-Agent":"ONTO-TIME-Original-Foodweb-Audit/1.0"}),timeout=30) as resp:
            raw=resp.read(1_000_000)
    except (urllib.error.URLError,OSError):
        # GitHub REST public raw bytes encoded in source API as base64.
        request=urllib.request.Request(
           f"https://api.github.com/repos/{REPO}/contents/{filename}?ref={COMMIT}",
           headers={"User-Agent":"ONTO-TIME-Original-Foodweb-Audit/1.0",
                    "Accept":"application/vnd.github+json"})
        with urllib.request.urlopen(request,timeout=35) as resp:
            payload=json.load(resp)
        raw=base64.b64decode(payload["content"])
    if len(raw)!=EXPECTED_FILE_BYTES[filename] or git_sha(raw)!=SOURCE_SHA[filename]:
        raise ValueError("Original foodweb Git source blob changed: "+filename)
    return raw

def parse_csv(original):
    text=io.TextIOWrapper(io.BytesIO(original),encoding="utf-8-sig",newline="")
    return list(csv.DictReader(text))

def label(node):
    if not node or not node.get("Genus") or not NAME_RE.fullmatch(node.get("SpecificEpithet","")):
        return None
    return node["Genus"]+" "+node["SpecificEpithet"]

def build(links,nodes):
    n={x["NodeID"]:x for x in nodes}
    groups=defaultdict(list)
    stage_edges=0
    pred=[x for x in links if x["LinkType"]=="predation"]
    for edge in pred:
        a=n.get(edge["ConsumerNodeID"])
        b=n.get(edge["ResourceNodeID"])
        p=label(a);q=label(b)
        if not p or not q or p==q or not a.get("Stage") or not b.get("Stage"):
            continue
        stage_edges+=1
        row={"predator":p,"predator_stage":a["Stage"],"prey":q,
             "prey_stage":b["Stage"],"evidence":edge["LinkEvidence"],
             "source_link_node_id_pair":[a["NodeID"],b["NodeID"]],
             "source_notes":edge["LinkEvidenceNotes"]}
        groups["::".join(sorted([p,q]))].append(row)
    recips=[]
    for key,edges in groups.items():
        left,right=key.split("::")
        x=[e for e in edges if e["predator"]==left]
        y=[e for e in edges if e["predator"]==right]
        if not x or not y:
            continue
        observed_both=any(e["evidence"]=="observed" for e in x) and any(e["evidence"]=="observed" for e in y)
        observed_switch=any(
            e["evidence"]=="observed" and z["evidence"]=="observed" and (
            e["predator_stage"]!=z["prey_stage"] or e["prey_stage"]!=z["predator_stage"])
            for e in x for z in y)
        recips.append({"species_pair":key,"n_edges":len(edges),
              "n_edges_observed":sum(e["evidence"]=="observed" for e in edges),
              "both_directions_observed":observed_both,
              "both_observed_with_stage_transition":observed_switch,
              "edges":edges})
    recips.sort(key=lambda e:e["species_pair"])
    return {"n_pond_nodes":len(nodes),"n_all_link_rows":len(links),
           "all_link_evidence":dict(Counter(x["LinkEvidence"] for x in links)),
           "n_predation_link_rows":len(pred),
           "predation_link_evidence":dict(Counter(x["LinkEvidence"] for x in pred)),
           "n_stage_and_species_resolved_nonself_predation_edges":stage_edges,
           "n_unique_species_pairs_any_one_direction":len(groups),
           "n_named_species_pairs_with_links_in_both_directions":len(recips),
           "n_reciprocal_species_pairs_both_directions_source_class_observed":
             sum(v["both_directions_observed"] for v in recips),
           "n_reciprocal_pairs_with_both_source_class_observed_and_stage_change":
             sum(v["both_observed_with_stage_transition"] for v in recips)},recips

def validate(total,candidates,receipt):
    old=json.loads(Path(receipt).read_text(encoding="utf-8"))
    assert total==old["totals"], "Source-original denominator or evidence-tier changed"
    ref={x["species_pair"]:x for x in old["reciprocity"]}
    assert {x["species_pair"] for x in candidates}==set(ref), "Reciprocal source pair set changed"
    for x in candidates:
        y=ref[x["species_pair"]]
        assert x["n_edges"]==y["n_edges"] and x["n_edges_observed"]==y["n_edges_observed"],"Evidence tier changed"
        assert x["both_directions_observed"]==y["both_directions_observed"],"Observed direction changed"
        assert x["both_observed_with_stage_transition"]==y["both_observed_with_stage_transition"],"Stage transition classification changed"
        f=lambda es:sorted(json.dumps(e,sort_keys=True) for e in es)
        assert f(x["edges"])==f(y["edges"]), "Original link-stage data changed"
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--reference",default=str(RESULT))
    a=p.parse_args()
    originals={key:download_original(key) for key in SOURCE_SHA}
    totals,candidates=build(parse_csv(originals["Quick_Pond_Links.csv"]),
                            parse_csv(originals["Quick_Pond_Nodes.csv"]))
    checked=validate(totals,candidates,a.reference)
    out={"status":"PINNED_ORIGINAL_SOURCE_STAGE_RECIPROCITY_MATCH",
         "original_sources":REPO+"@"+COMMIT,
         "source_sha":SOURCE_SHA,
         "totals":totals,
         "reciprocal_pairs":candidates,
         "exact_source_readback":checked,
         "claim_ceiling":"No observed-to-observed ontogenetic reversal in this original compiled food web; a source-tagged observation is not an individually dated attack trial."}
    Path(a.out).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"totals":totals,"exact_source_readback":checked},indent=2))

if __name__=="__main__":
    main()
