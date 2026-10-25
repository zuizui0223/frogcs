#!/usr/bin/env python3
"""Original Hechinger (2011) 3-estuary source-stage ontology audit.

This deliberately distinguishes (i) trophic link class,
(ii) true species-binomial vs open morphospecies label,
(iii) adult bivalve consuming another bivalve larva, and
(iv) independently observed attacks (not measured here).

Original 2011 ecology Metaweb: link-site presence flags for three estuaries,
not 3 independent attack experiments or a 2024 dataset. The original paper
states many free-living consumer-resource links were estimated/projected.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.error
import urllib.request
import base64

ORIGINAL="globalbioticinteractions/hechinger2011"
COMMIT="28e6836db3fe18d17e029187971d94e9af8bf9d1"
FILE_SHA={
    "Metaweb_Links.txt":"7defe6a366a2efb8fe738df8f51671d41328cce7",
    "Metaweb_Nodes.txt":"7d4fc3a6707fb72fd90b0b146209e0f5b86851f6"
}
SITES=("CSM","EPB","BSQ")
PARASITES={"trematode","cestode","acanthocephalan","nematode",
           "monogenean","gregarine","microsporidian","parasite"}
PARASITE_STAGES={"parthenitae","cercaria","metacercaria","plerocercoid",
                 "procercoid","cystacanth"}
ROOT=Path(__file__).resolve().parent
FROZEN=ROOT/"results"/"HECHINGER2011_THREE_ESTUARY_ORIGINAL_TYPED_STAGE_V0_1.json"

def git_blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def original_bytes(filename):
    url=f"https://raw.githubusercontent.com/{ORIGINAL}/{COMMIT}/{filename}"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"ONTO-TIME-Original-Stage-Network-Replay/0.1"})
        with urllib.request.urlopen(req,timeout=40) as response:
            raw=response.read(2_000_000)
    except (urllib.error.URLError,OSError):
        url=f"https://api.github.com/repos/{ORIGINAL}/contents/{filename}?ref={COMMIT}"
        req=urllib.request.Request(url,headers={"Accept":"application/vnd.github+json",
                                                "User-Agent":"ONTO-TIME-Original-Stage-Network-Replay/0.1"})
        with urllib.request.urlopen(req,timeout=40) as response:
            value=json.load(response)
        raw=base64.b64decode(value["content"])
    if git_blob_sha(raw)!=FILE_SHA[filename]:
        raise ValueError("source Git blob SHA drift for "+filename)
    return raw

def read_rows(original):
    with io.TextIOWrapper(io.BytesIO(original),encoding="utf-8-sig",newline="") as text:
        return list(csv.DictReader(text,delimiter="\t"))

def taxon(node,broad=False):
    if node is None:
        return None
    genus=node.get("Genus","")
    epi=node.get("SpecificEpithet","")
    if not re.fullmatch(r"[A-Z][a-z-]+",genus):
        return None
    if not re.fullmatch(r"[a-z][a-z-]+",epi):
        if not (broad and re.fullmatch(r"[A-Za-z][A-Za-z-]*",epi)):
            return None
    return genus+" "+epi

def stage_edges(site_links,node_by_id,broad=False):
    edges=[]
    for link in site_links:
        a=node_by_id.get(link["ConsumerNodeID"])
        b=node_by_id.get(link["ResourceNodeID"])
        if a is None or b is None:
            raise ValueError("dangling original site-stage node")
        pred=taxon(a,broad=broad)
        prey=taxon(b,broad=broad)
        if not pred or not prey or pred==prey or not a["Stage"] or not b["Stage"]:
            continue
        pg=a["OrganismalGroup"].lower()
        rg=b["OrganismalGroup"].lower()
        ps=a["Stage"].lower()
        rs=b["Stage"].lower()
        edges.append({
            "pred":pred,"prey":prey,"ps":ps,"rs":rs,
            "pg":pg,"rg":rg,"type":link["LinkType"].lower(),
            "par":pg in PARASITES or rg in PARASITES or
                  ps in PARASITE_STAGES or rs in PARASITE_STAGES,
        })
    return edges

def reciprocal(edges):
    pairs=defaultdict(list)
    for edge in edges:
        key="::".join(sorted([edge["pred"],edge["prey"]]))
        pairs[key].append(edge)
    both=[]
    for pair,arr in pairs.items():
        a,b=pair.split("::")
        left=[z for z in arr if z["pred"]==a]
        right=[z for z in arr if z["pred"]==b]
        if not left or not right:
            continue
        switched=any(x["ps"]!=y["rs"] or x["rs"]!=y["ps"]
                     for x in left for y in right)
        both.append({
            "pair":pair,"changed":switched,
            "parasite":any(x["par"] for x in arr),
            "double_bivalve_adult_consumes_heterospecific_larva":
                all(x["pg"]=="bivalve" and x["rg"]=="bivalve" and
                    x["ps"]=="adult" and x["rs"]=="larva" for x in arr)
        })
    return {
        "n_edges":len(edges),
        "n_unique_pairs":len(pairs),
        "n_reciprocal":len(both),
        "n_changed":sum(x["changed"] for x in both),
        "n_changed_parasite":sum(x["changed"] and x["parasite"] for x in both),
        "n_changed_nonparasite":sum(x["changed"] and not x["parasite"] for x in both),
    },both

def process(nodes,links):
    site_output={}
    if len(nodes)!=919 or len(links)!=11270:
        raise ValueError("unexpected original source dimensions")
    for link in links:
        if link["PresentAtAnyEstuary"] not in ("0","1"):
            raise ValueError("original site summary flag invalid")
        visible=any(link["PresentAt"+site]=="1" for site in SITES)
        if visible!=(link["PresentAtAnyEstuary"]=="1"):
            raise ValueError("metaweb row present-any flag inconsistent")
    for site in SITES:
        site_nodes=[x for x in nodes if x["System"]==site]
        index={x["NodeID"]:x for x in site_nodes}
        if len(index)!=len(site_nodes):
            raise ValueError("duplicate site node id")
        rows=[x for x in links if x["PresentAt"+site]=="1"]
        strict=stage_edges(rows,index)
        wide=stage_edges(rows,index,broad=True)
        all_stat,_=reciprocal(strict)
        broad_stat,_=reciprocal(wide)
        pred_stat,pred_pairs=reciprocal([x for x in strict if x["type"]=="predation"])
        motif=[x for x in pred_pairs if x["changed"]]
        taxa=sorted(set(t for x in motif for t in x["pair"].split("::")))
        site_output[site]={
            "site_nodes":len(site_nodes),
            "site_present_links":len(rows),
            "stage_species_edges_all_classes":all_stat["n_edges"],
            "structural_reciprocal_all_classes":all_stat["n_reciprocal"],
            "stage_shift_all_classes_strict_species":all_stat["n_changed"],
            "stage_shift_all_classes_including_parasite":all_stat["n_changed_parasite"],
            "stage_shift_all_classes_nonparasite":all_stat["n_changed_nonparasite"],
            "stage_shift_all_classes_with_morphospecies_placeholder":broad_stat["n_changed"],
            "morphospecies_placeholder_extra_candidate_pairs":broad_stat["n_changed"]-all_stat["n_changed"],
            "predation_only":{
                "stage_species_edges":pred_stat["n_edges"],
                "unique_pairs":pred_stat["n_unique_pairs"],
                "structural_reciprocal_pairs":pred_stat["n_reciprocal"],
                "stage_shift_candidate_pairs":pred_stat["n_changed"]
            },
            "bivalve_motif":{
                "n_pairs":len(motif),
                "n_double_adult_to_other_species_larva":sum(
                   x["double_bivalve_adult_consumes_heterospecific_larva"] for x in motif),
                "species":taxa,
                "pair_names":sorted(x["pair"] for x in motif)
            },
            "site_link_type_counts":dict(sorted(Counter(x["LinkType"] for x in rows).items()))
        }
    meta={
        "n_meta_links":len(links),"n_nodes_site_rows":len(nodes),
        "n_global_distinct_node_ids":len({x["NodeID"] for x in nodes}),
        "n_present_any_site":sum(x["PresentAtAnyEstuary"]=="1" for x in links),
        "n_present_no_site":sum(x["PresentAtAnyEstuary"]=="0" for x in links),
        "n_site_presence_links":sum(site_output[x]["site_present_links"] for x in SITES)
    }
    total={
        "stage_shift_strict_species_all_classes":sum(site_output[x]["stage_shift_all_classes_strict_species"] for x in SITES),
        "stage_shift_with_morphospecies_placeholders":sum(site_output[x]["stage_shift_all_classes_with_morphospecies_placeholder"] for x in SITES),
        "non_species_placeholder_excess":sum(site_output[x]["morphospecies_placeholder_extra_candidate_pairs"] for x in SITES),
        "strict_predation_stage_shift_site_pairs":sum(site_output[x]["predation_only"]["stage_shift_candidate_pairs"] for x in SITES),
        "bivalve_module_site_pairs":sum(site_output[x]["bivalve_motif"]["n_double_adult_to_other_species_larva"] for x in SITES)
    }
    return meta,total,site_output

def validate(result,reference):
    source=json.loads(Path(reference).read_text(encoding="utf-8"))
    if result["meta"]!=source["meta"] or result["totals"]!=source["totals"]:
        raise ValueError("original source dimensions or common macro endpoint drift")
    for site in SITES:
        if result["sites"][site]!=source["sites"][site]:
            raise ValueError("site original source prediction changed: "+site)
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    parser.add_argument("--reference",default=str(FROZEN))
    args=parser.parse_args()
    links=read_rows(original_bytes("Metaweb_Links.txt"))
    nodes=read_rows(original_bytes("Metaweb_Nodes.txt"))
    meta,totals,sites=process(nodes,links)
    report={"status":"ORIGINAL_HECHINGER_3_ESTUARY_TYPED_STAGE_EXACT_REPLAY",
            "source_repo":ORIGINAL,"commit":COMMIT,
            "original_git_blob_sha":FILE_SHA,
            "meta":meta,"totals":totals,"sites":sites}
    report["exact_source_readback"]=validate(report,args.reference)
    Path(args.out).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("status","meta","totals","exact_source_readback")},
                     ensure_ascii=False))
if __name__=="__main__":
    main()
