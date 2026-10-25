#!/usr/bin/env python3
"""Worldwide GBIF developmental-stage observation facets for GloBI trophic pairs.

Pure public API; species-level GloBI partner matching is pinned upstream.
GBIF stage reporting is not stage abundance, predator/prey contact or a
documented local developmental trophic reversal. Country geographic coverage
is a feasibility screen only; future bulk 1° grid + wetlands needed.
"""
import argparse
import collections
import concurrent.futures
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE="https://api.gbif.org/v1/occurrence/search"
SOURCE_DATE="2026-10-25"
FIELD_REP={"adult":"Adult","egg":"Egg","larva":"Larva",
           "nymph":"Nymph","juvenile":"Juvenile"}
GLOBI_TO_BIN={
    "adult":"adult","imago":"adult","post-juvenile adult stage":"adult",
    "larval":"aquatic_immature","larva":"aquatic_immature",
    "nymph":"aquatic_immature","tadpole":"aquatic_immature",
    "egg":"egg","embryo":"egg","young":"juvenile",
    "juvenile":"juvenile","subadult":"juvenile",
    "immature":"juvenile","pupa":"aquatic_immature"
}
GBIF_TO_BIN={
    "Adult":"adult","Imago":"adult",
    "Larva":"aquatic_immature","Nymph":"aquatic_immature",
    "Tadpole":"aquatic_immature","Pupa":"aquatic_immature",
    "Egg":"egg","Juvenile":"juvenile","Subadult":"juvenile",
    "Young":"juvenile","Immature":"juvenile"
}


def api(key, **params):
    params=dict(taxonKey=int(key),hasCoordinate="true",
                hasGeospatialIssue="false",year="2010,2026",
                occurrenceStatus="PRESENT",limit=0,
                facetLimit=250,**params)
    url=BASE+"?"+urllib.parse.urlencode(params)
    err=""
    for i in range(3):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"FrogcsGlobalStage/0.1 (GBIF stage metadata research)"})
            with urllib.request.urlopen(req,timeout=30) as f:
                return json.loads(f.read().decode("utf8"))
        except Exception as e:
            err=str(e)
            time.sleep(.7*(i+1))
    raise RuntimeError(f"GBIF stage query failed for {key}: {err}")


def summary_raw(row):
    try:
        r=api(row["gbif_taxon_key"],facet="lifeStage")
        cats={}
        for f in r.get("facets",[]):
            if f.get("field","").upper()=="LIFE_STAGE":
                cats={x["name"]:int(x["count"]) for x in f.get("counts",[])}
        valid={cat:sum(n for label,n in cats.items()
                       if GBIF_TO_BIN.get(label)==cat)
               for cat in set(GBIF_TO_BIN.values())}
        return {"taxon":row["taxon"],"taxon_key":int(row["gbif_taxon_key"]),
                "gbif_total_valid_coord_records":int(r.get("count",0)),
                "gbif_raw_stage_labels":cats,"canonical_counts":valid,
                "staged_records":sum(valid.values()),"status":"ok"}
    except Exception as e:
        return {"taxon":row["taxon"],"status":"error","error":str(e)[:300]}


def countries_by_stage(job,lookup):
    name,stage_cat=job
    species=lookup[name]
    key=species["taxon_key"]
    cats=species["gbif_raw_stage_labels"]
    labels=sorted(label for label in cats if
                  GBIF_TO_BIN.get(label)==stage_cat and cats[label]>=1)
    raw={}
    errors=[]
    for label in labels:
        try:
            d=api(key,facet="country",lifeStage=label)
        except Exception as e:
            errors.append(str(e)[:300])
            continue
        for f in d.get("facets",[]):
            if f.get("field","").upper()=="COUNTRY":
                for x in f.get("counts",[]):
                    country=x.get("name","")
                    if re.fullmatch("[A-Z]{2}",country):
                        raw[country]=raw.get(country,0)+int(x["count"])
    return (job,{"counts":raw,"raw_labels_used":labels,"errors":errors})


def load_csv(path):
    with Path(path).open(encoding="utf8",newline="") as f:
        return list(csv.DictReader(f))


def normalized_globi_stage(v):
    raw=str(v or "").strip().lower()
    if raw in GLOBI_TO_BIN:
        return GLOBI_TO_BIN[raw]
    if "adult" in raw and "post" in raw:return "adult"
    if any(word in raw for word in ["larv","tadpol","nymph"]):
        return "aquatic_immature"
    if "juvenil" in raw or "young" in raw:return "juvenile"
    if "egg" in raw:return "egg"
    if "adult" in raw:return "adult"
    return ""


def write_csv(path,rows,columns):
    with Path(path).open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader();w.writerows(rows)


def run(a):
    taxa_rows=[r for r in load_csv(a.taxa)
               if r.get("layer")=="trophic" and r.get("status")=="accepted"]
    edges=[r for r in load_csv(a.edges)
           if r.get("any_both_stage_labeled")=="1"]
    if len(taxa_rows)<15 or not edges:
        raise RuntimeError("GloBI taxon & actual paired stage evidence missing")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        summaries=list(ex.map(summary_raw,taxa_rows))
    sm={r["taxon"]:r for r in summaries if r["status"]=="ok"}
    staged_pairs=[]
    for p in edges:
        try: patterns=json.loads(p.get("paired_stage_patterns") or "[]")
        except Exception: patterns=[]
        for raw_pred,raw_prey in patterns:
            pred=normalized_globi_stage(raw_pred)
            prey=normalized_globi_stage(raw_prey)
            if not pred or not prey or p["predator"] not in sm or p["prey"] not in sm:
                continue
            staged_pairs.append({
                "predator":p["predator"],"prey":p["prey"],
                "predator_stage":pred,"prey_stage":prey,
                "original_predator_stage":raw_pred,
                "original_prey_stage":raw_prey,
                "source":p["example_source"],
                "predator_guild":p["predator_guild"],
                "prey_guild":p["prey_guild"],
            })
    demands=sorted({(p["predator"],p["predator_stage"]) for p in staged_pairs} |
                   {(p["prey"],p["prey_stage"]) for p in staged_pairs})
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        observations=dict(pool.map(lambda job:countries_by_stage(job,sm),
                                   demands))
    pair_rows=[]
    for r in staged_pairs:
        left=observations[(r["predator"],r["predator_stage"])]["counts"]
        right=observations[(r["prey"],r["prey_stage"])]["counts"]
        paired={c for c in left if left.get(c,0)>=1 and right.get(c,0)>=1}
        paired5={c for c in left if left.get(c,0)>=5 and right.get(c,0)>=5}
        pair_rows.append({
            **r,"countries_stage_co_report_min1":len(paired),
            "countries_stage_co_report_min5":len(paired5),
            "example_co_report_countries":";".join(sorted(paired)[:12]),
            "inference":"GBIF_STAGE_COUNTRY_CO_REPORT_ONLY"
        })
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"species_lifestage_coverage.csv",[
        {
            "taxon":r["taxon"],"gbif_specieskey":r.get("taxon_key",""),
            "status":r["status"],"gbif_records":r.get("gbif_total_valid_coord_records",""),
            "stage_labeled_records":r.get("staged_records",""),
            "adult":r.get("canonical_counts",{}).get("adult",0),
            "aquatic_immature":r.get("canonical_counts",{}).get("aquatic_immature",0),
            "egg":r.get("canonical_counts",{}).get("egg",0),
            "juvenile":r.get("canonical_counts",{}).get("juvenile",0),
            "error":r.get("error","")
        } for r in summaries],
        ["taxon","gbif_specieskey","status","gbif_records",
         "stage_labeled_records","adult","aquatic_immature","egg",
         "juvenile","error"])
    write_csv(out/"gloBI_species_stage_country_potential.csv",pair_rows,[
        "predator","prey","predator_guild","prey_guild",
        "predator_stage","prey_stage","original_predator_stage",
        "original_prey_stage","countries_stage_co_report_min1",
        "countries_stage_co_report_min5","example_co_report_countries",
        "source","inference"])
    write_csv(out/"country_stage_cells.csv",[
        dict(taxon=s,stage_class=stage,country=country,
             records=int(n),qualifier="GBIF_REPORTED_STAGE_NOT_ACTUAL_INTERACTION")
        for ((s,stage),d) in observations.items()
        for country,n in d["counts"].items()],
        ["taxon","stage_class","country","records","qualifier"])
    totals=sum(r.get("gbif_total_valid_coord_records",0) for r in summaries)
    labeled=sum(r.get("staged_records",0) for r in summaries)
    summary={
        "date":SOURCE_DATE,
        "source":"GBIF occurrence SEARCH facet=lifeStage and country conditioned on exact lifeStage; GloBI source linked species pairs",
        "staging":"GloBI joint life-stage pattern must exist; species names matched in prior GBIF pilot",
        "taxa_queried":len(taxa_rows),
        "taxa_with_lifestage_facet":sum(r.get("staged_records",0)>0 for r in summaries),
        "taxa_with_adults_and_aquatic_immatures":sum(
            r.get("canonical_counts",{}).get("adult",0)>=5 and
            r.get("canonical_counts",{}).get("aquatic_immature",0)>=5
            for r in summaries),
        "total_occurrence_records_among_taxa":totals,
        "raw_lifestage_annotation_records_among_taxa":labeled,
        "raw_lifestage_record_annotation_ratio":
            labeled/totals if totals else None,
        "gloBI_staged_trophic_links":len(edges),
        "retained_joint_predator_prey_stage_patterns":len(pair_rows),
        "distinct_staged_trophic_species_pairs":len(set(
            (p["predator"],p["prey"]) for p in pair_rows)),
        "taxon_stage_country_queries":len(demands),
        "stage_country_pair_with_overlap_min1":sum(
            p["countries_stage_co_report_min1"]>0 for p in pair_rows),
        "stage_country_pair_with_overlap_min5":sum(
            p["countries_stage_co_report_min5"]>0 for p in pair_rows),
        "stage_pairs_examples":sorted(pair_rows,key=lambda p:
            (-p["countries_stage_co_report_min1"],
             p["predator"],p["prey"]))[:14],
        "largest_lifestage_sample_taxa":sorted(
            [dict(taxon=r["taxon"],staged=r["staged_records"],
                  adult=r["canonical_counts"].get("adult",0),
                  aquatic=r["canonical_counts"].get("aquatic_immature",0),
                  egg=r["canonical_counts"].get("egg",0))
             for r in summaries if r["status"]=="ok"],
            key=lambda v:-v["staged"])[:10],
        "failures":[r for r in summaries if r["status"]=="error"],
        "stage_country_query_errors":[{"species":n,"stage":k,"errors":v["errors"]}
                                    for (n,k),v in observations.items()
                                    if v.get("errors")],
        "interpretation_boundaries":[
            "Missing lifeStage record fields in GBIF DO NOT mean no immatures or adults in nature.",
            "GBIF lifeStage vocabulary and GloBI stage terms were loosely normalized; no actual developmental timing was measured.",
            "GBIF stage observations are not prey/predator overlap at a pond or synchronized in calendar year.",
            "Country stage co-reporting does not establish ontogenetic feeding reversal, direction dominance, or any predation rate.",
            "GloBI documented pair stages were preserved jointly, not cross-combined into unsupported pairs.",
            "GBIF data are biased by species, survey method, geography and observer; these are data availability results only.",
            "Global wetland macrophyte structure, local rainfall, freshwater fish and frog chorus history remain unjoined."
        ],
    }
    (out/"observed_results.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BEGIN_GBIF_GLOBAL_STAGE_BRIDGE_RESULTS")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("END_GBIF_GLOBAL_STAGE_BRIDGE_RESULTS")


def selftest():
    assert normalized_globi_stage("post-juvenile adult stage")=="adult"
    assert normalized_globi_stage("larval")=="aquatic_immature"
    assert normalized_globi_stage("-999")==""
    assert normalized_globi_stage("Egg")=="egg"
    print("SYNTHETIC_STAGE_BRIDGE_QA_PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--taxa",default="research/results/global_globi_gbif/gbif_species_match_audit.csv")
    p.add_argument("--edges",default="research/results/global_globi_gbif/selected_trophic_pairs.csv")
    p.add_argument("--out",default="research/results/global_globi_gbif/stage_bridge")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:selftest()
    else:run(a)
