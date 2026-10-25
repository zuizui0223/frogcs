#!/usr/bin/env python3
"""Source-only body-mass assumptions behind Hechinger 2011 bivalve motifs.

One assigned size for every larval bivalve in two original estuaries is
a *documented approximation*, not an independent larval mass measurement,
and adult/larval body-size contrast does not establish an observed attack.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import statistics
import audit_hechinger_original_three_estuaries as source

BASE=Path(__file__).resolve().parent
STAGE=BASE/"results"/"HECHINGER2011_THREE_ESTUARY_ORIGINAL_TYPED_STAGE_V0_1.json"
FROZEN=BASE/"results"/"HECHINGER2011_BIVALVE_MOTIF_STAGE_BODYMASS_SOURCE_AUDIT_V0_1.json"

def compute(nodes,links,stage_snapshot):
    out={}
    for site in ("CSM","EPB"):
        site_nodes={n["NodeID"]:n for n in nodes if n["System"]==site}
        pairs=set(stage_snapshot["sites"][site]["bivalve_motif"]["pair_names"])
        items=[]
        for edge in links:
            if edge["PresentAt"+site]!="1" or edge["LinkType"].lower()!="predation":
                continue
            a=site_nodes.get(edge["ConsumerNodeID"])
            b=site_nodes.get(edge["ResourceNodeID"])
            if a is None or b is None:
                raise ValueError("unmapped bivalve source stage nodes")
            p=source.taxon(a)
            q=source.taxon(b)
            if not p or not q or p==q or "::".join(sorted([p,q])) not in pairs:
                continue
            if not (a["Stage"].lower()=="adult" and b["Stage"].lower()=="larva"
                    and a["OrganismalGroup"].lower()=="bivalve"
                    and b["OrganismalGroup"].lower()=="bivalve"):
                raise ValueError("source's typed reciprocal motif is no longer all adult→larva")
            try:
                adult=float(a["BodySize(g)"])
                larva=float(b["BodySize(g)"])
            except (ValueError,TypeError) as err:
                raise ValueError("source node body size absent for pinned motif") from err
            if adult<=0 or larva<=0 or not math.isfinite(adult/larva):
                raise ValueError("invalid positive mass from source")
            items.append({"pair":"::".join(sorted([p,q])),"adult":adult,
                          "larva":larva,"ratio":adult/larva,
                          "adult_method":a["BodySizeEstimation"],
                          "larva_method":b["BodySizeEstimation"]})
        counts=Counter(e["pair"] for e in items)
        if any(counts[pair]!=2 for pair in pairs):
            raise ValueError("a source stage-pair does not have exactly two opposite directions")
        rs=sorted(x["ratio"] for x in items)
        masses=sorted(set(x["larva"] for x in items))
        out[site]={
            "n_stage_motif_directed_links":len(items),
            "n_bilateral_species_pairs":len(pairs),
            "n_distinct_adult_mass_values":len({e["adult"] for e in items}),
            "n_distinct_larval_mass_values":len(masses),
            "larval_mass_values_g":masses,
            "larval_mass_estimation_methods":sorted({e["larva_method"] for e in items}),
            "adult_mass_estimation_methods":sorted({e["adult_method"] for e in items}),
            "median_log10_mass_ratio":round(math.log10(statistics.median(rs)),6),
            "min_log10_mass_ratio":round(math.log10(rs[0]),6),
            "max_log10_mass_ratio":round(math.log10(rs[-1]),6),
            "note":"Mass ratios describe source-assigned node sizes; shared larval size is an approximation, not independently measured for each link or proof of predation."
        }
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    original=json.loads(STAGE.read_text(encoding="utf-8"))
    reference=json.loads(FROZEN.read_text(encoding="utf-8"))
    nodes=source.read_rows(source.original_bytes("Metaweb_Nodes.txt"))
    links=source.read_rows(source.original_bytes("Metaweb_Links.txt"))
    totals=compute(nodes,links,original)
    if totals!=reference["sites"]:
        raise ValueError("Original pinned bivalve mass assumption changed")
    report={"status":"ORIGINAL_SOURCE_BIVALVE_MASS_APPROXIMATION_VERIFIED",
            "source_commit":source.COMMIT,"sites":totals,
            "unchanged_source_reference":True,
            "interpretation":"High adult/larva mass ratio is based in part on a single approximate larval mass used for all recorded larval stages; does not demonstrate observed predation ability."}
    Path(args.out).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],
                      "shared_larval_mass_g":totals["CSM"]["larval_mass_values_g"][0],
                      "n_directed_original_predation_class_motifs":sum(t["n_stage_motif_directed_links"] for t in totals.values()),
                      "source_exact":True}))
if __name__=="__main__":
    main()
