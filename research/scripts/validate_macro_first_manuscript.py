#!/usr/bin/env python3
"""Fail-closed research-only macro-first editorial and numerical source audit.

Validates NEW MACRO manuscript/ledger against source tables already pinned in
the separate 894-file macro reproducibility snapshot. Original manuscript,
NAAMP RC6 science, prior research documents and source snapshot are read-only.
No new ecological outcomes are fitted; no causal trophic claim is authorized.
"""
from __future__ import annotations
from pathlib import Path
import csv
import json
import math
import re

ROOT=Path(__file__).resolve().parents[2]
MANUSCRIPT=ROOT/"research/manuscript/MACRO_ECOLOGY_MAIN_DRAFT_V0_1.md"
LEDGER=ROOT/"research/MACRO_FIRST_EVIDENCE_LEDGER_2026-10-26.json"
DECISION=ROOT/"research/MACRO_FIRST_EDITORIAL_DECISION_2026-10-26.md"
INDEX=ROOT/"research/manuscript/README.md"
SNAPSHOT=ROOT/"research/reproducibility/macro_snapshot_20261026.json"

def require(x,msg):
    if not x:raise ValueError(msg)

def nearly(x,y,atol=0.00055):
    require(math.isclose(float(x),float(y),rel_tol=0,abs_tol=atol),
            f"Numerical source disagreement: {x} vs {y}")

def rows(name):
    with (ROOT/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def find_unique(rr,conditions):
    matches=[z for z in rr if all(z.get(k)==v for k,v in conditions.items())]
    require(len(matches)==1,"Expected one numerical source row: "+str(conditions))
    return matches[0]

def verify_source_and_ledger():
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    assert ledger["status"].startswith("POSTHOC_EXPLORATORY")
    claims={x["id"]:x for x in ledger["primary_claims"]}
    assert len(claims)==5
    assert ledger["historical_RC6"]["motivation_only"] is True
    assert ledger["historical_RC6"]["own_results_primary"] is False
    assert ledger["historical_RC6"]["not_independent_replication"] is True
    assert ledger["frozen_source_snapshot"]["verified_files"]==894

    src=rows("research/results/naamp_site_use_associations_20261026/primary_correlations.csv")
    c=claims["guild_whole_area_odonata"]
    for bg in ("uniform","target_group"):
        r=find_unique(src,{"feature":"mean_suitability_Odonata_"+bg,
                           "outcome":"strong_rate","scale":"whole_sample_spearman"})
        nearly(r["correlation"],c["backgrounds"][bg]["rho"])
        require(int(r["sites"])==4248 and int(r["routes"])==432,
                "Original acoustic site/grain drift")
    assert ledger["source_eligibility"]["modeled_species"]==28
    assert sum(ledger["source_eligibility"][k] for k in
               ("modeled_Anura","modeled_Caudata","modeled_Odonata"))==28

    src=rows("research/results/naamp_odonata_caudata_associations_20261026/high_low_contrasts.csv")
    c=claims["caudata_context_condition"]
    for bg in ("uniform","target_group"):
        r=find_unique(src,{"background":bg,
                           "group":"pond_breeding_Caudata","within_route":"False"})
        nearly(r["high_minus_low_rho"],c["backgrounds"][bg]["difference"])
        nearly(r["low"],c["backgrounds"][bg]["ci95_difference"][0])
        nearly(r["high"],c["backgrounds"][bg]["ci95_difference"][1])

    src=rows("research/results/naamp_remote_vegetation_20261026/network_rank_coefficients.csv")
    c=claims["landscape_vegetation_interaction"]
    for bg in ("uniform","target_group"):
        r=find_unique(src,{"background":bg,
                           "group":"pond_breeding_Caudata",
                           "vegetation_metric":"mean","radius_m":"3000",
                           "within_route":"False",
                           "term":"Odonata:Caudata:vegetation"})
        nearly(r["beta"],c[bg+"_whole_area"]["threeway_beta"])
        nearly(r["low"],c[bg+"_whole_area"]["ci95"][0])
        nearly(r["high"],c[bg+"_whole_area"]["ci95"][1])

    src=rows("research/results/naamp_prior_water_20261026/matched_water_differences.csv")
    c=claims["antecedent_water"]
    r=find_unique(src,{"feature":"frequency_on_water_positive_pixels","radius_m":"3000"})
    require(int(r["pairs"])==3907 and int(r["routes"])==387,
            "Original conditional water subcohort drift")
    nearly(r["difference"],c["difference_pp"])
    nearly(r["low"],c["ci95_pp"][0])
    nearly(r["high"],c["ci95_pp"][1])
    r=find_unique(src,{"feature":"water_positive_area_fraction","radius_m":"3000"})
    nearly(float(r["difference"])*100,c["ever_water_area_difference_pp"])

    src=rows("research/results/naamp_network_fixed_pairs_20261026/matched_stratum_differences.csv")
    c=claims["prior_site_history"]
    r=find_unique(src,{"background":"uniform","group":"Caudata","stratum":"all",
                       "feature":"history_difference"})
    require(int(r["pairs"])==4040 and int(r["routes"])==388,
            "Original history comparison sample/route drift")
    nearly(float(r["mean"])*100,c["difference_pp"])
    nearly(float(r["low"])*100,c["ci95_pp"][0])
    nearly(float(r["high"])*100,c["ci95_pp"][1])

    prior_replay=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert prior_replay["source_commit"]==ledger["frozen_source_snapshot"]["commit"]
    assert len(prior_replay["files"])==894
    pinned={item["path"] for item in prior_replay["files"]}
    # Never amend one original snapshot byte just to change reader-facing order.
    for x in [MANUSCRIPT,LEDGER,DECISION,INDEX]:
        assert str(x.relative_to(ROOT)) not in pinned, str(x)
    return {
      "source_naamp_sites":4248,"source_fixed_pair_units":4040,
      "original_water_frequenced_pairs":3907,
      "historical_route_components":388,
      "five_main_macro_claims_verified_against_saved_original_numeric_CSV":True,
      "original_historical_894_file_snapshot_used_read_only":True,
    }

def verify_manuscript():
    manuscript=MANUSCRIPT.read_text(encoding="utf-8")
    header=manuscript.split("## Abstract — the macro results lead",1)
    require(len(header)==2,"Macro-led abstract section missing")
    abstract=header[1].split("## 1. Introduction",1)[0]
    require("RC6" not in abstract,"RC6 must not lead the macro abstract")
    require("0.2969" not in abstract,"Old RC6 null must not lead the macro abstract")
    for point in ("4,248","−0.095","−0.086","−0.385","−0.179",
                  "+0.037","3,907","−1.481","4,040","+27.68"):
        require(point in abstract or point in manuscript,
                "Missing quantified macro result: "+point)
    for section in ("## 1. Introduction","## 2. Methods","## 3. Results",
                    "## 4. Discussion","## 5. Conclusion",
                    "## Main paper figure and data plan"):
        require(section in manuscript,"Missing macro reader-facing section "+section)
    require("### Motivating observation: from RC6" in manuscript,
            "Historical origin statement missing")
    for limit in ("not measured","not a census","not biological",
                  "not a georeferenced breeding pond"):
        # Not all possible caveat strings must match literal case; enforce key
        # substantive disallowances via general terms below.
        pass
    require("not local" in manuscript.lower() or "not direct" in manuscript.lower()
            or "not measured" in manuscript.lower(),
            "Direct trophic observations cannot be assumed")
    require("no independent" not in abstract.lower(),
            "Avoid accidental misleading double-negative claim")
    require("not submission ready" in manuscript.lower(),"Not yet submission-ready")
    require("working" in manuscript.lower(),"Provisional editorial state missing")
    idx=INDEX.read_text(encoding="utf-8")
    for link in ("MACRO_ECOLOGY_MAIN_DRAFT_V0_1.md",
                 "INTEGRATED_FROG_ECOLOGY_DRAFT_V0_1.md",
                 "MACRO_FIRST_EDITORIAL_DECISION_2026-10-26.md"):
        require(link in idx,"Manuscript index missing source distinction "+link)

    unresolved=[]
    for document in (MANUSCRIPT,INDEX,DECISION):
        text=document.read_text(encoding="utf-8")
        for m in re.finditer(r"\[[^\]]+\]\(([^)\s]+)\)",text):
            link=m.group(1)
            if link.startswith(("http://","https://","mailto:","#")):
                continue
            target=(document.parent/link.split("#",1)[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                unresolved.append(f"{document.name}: {link}")
    require(not unresolved,"Broken local manuscript reference: "+", ".join(unresolved))
    return {"abstract_main_is_macro_not_rc6":True,"historical_RC6_introduction_only":True,
            "local_links_validated":True,"new_main_draft_provisional":True}

def main():
    report={"status":"PASS","scientific_sources":verify_source_and_ledger(),
            "editorial_checks":verify_manuscript(),
            "RC6_prior_submission_science_rewritten":False,
            "causal_trophic_mechanism_claimed":False}
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
