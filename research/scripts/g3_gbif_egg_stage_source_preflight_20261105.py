"""Response-blind G3 preflight: explicit GBIF amphibian egg-stage report coverage.

This phase does NOT download occurrences, estimate breeding onset, merge
NAAMP outcomes, or test the ecological vegetation×salamander-lead hypothesis.
Use original frozen 15 frog and 5 pond Caudata taxa plus two non-pond controls.
GBIF occurrence metadata = observation reporting, not breeding phenology.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE="https://api.gbif.org/v1/occurrence/search"
ORIGINAL_MAIN_SHA="5e2f0a87c639df373fa2700b29403d2ab417a1cc"
YEARS="2010,2025"
COUNTRY="US"
POND_CA=(
    "Ambystoma maculatum","Ambystoma mavortium","Ambystoma tigrinum",
    "Ambystoma laterale","Notophthalmus viridescens"
)
NONPOND_CA=("Plethodon cinereus","Eurycea longicauda")
EGG_LABELS=frozenset({"egg","eggs","ovum","ova"})
MIN_EGG_PER_SPECIES=50
MIN_FROG_EGG_SPECIES=5
MIN_POND_EGG_SPECIES=3
MIN_TOTAL_EGGS=300


def must(cond,message):
    if not bool(cond):
        raise AssertionError(message)


def source_taxa(manifest):
    data=list(csv.DictReader(Path(manifest).open(encoding="utf-8",newline="")))
    original={}
    for row in data:
        species=row["species"].strip()
        k=int(row["species_key"])
        guild=row["guild"]
        if row["background"] not in ("uniform","target_group"):
            raise AssertionError("Unexpected non-source SDM background")
        if guild not in ("Anura","Caudata","Odonata"):
            raise AssertionError("Original taxon guild drift")
        current=(k,guild)
        if species in original and original[species]!=current:
            raise AssertionError("Source GBIF species identity conflicts between backgrounds")
        original[species]=current
    counts={g:sum(role==g for _,role in original.values()) for g in ("Anura","Caudata","Odonata")}
    must(counts=={"Anura":15,"Caudata":7,"Odonata":6},
         "Original frozen 28-source-taxon inventory changed")
    must(set(POND_CA).issubset(original) and set(NONPOND_CA).issubset(original),
         "Original five pond vs two nonpond caudate roles missing")
    must(all(original[name][1]=="Caudata" for name in POND_CA+NONPOND_CA),
         "Pond breeding guild was not source-derived")
    rows=[]
    for species,(key,guild) in sorted(original.items()):
        if guild=="Anura":
            role="frog_original_15"
        elif species in POND_CA:
            role="pond_caudata_original_5"
        elif species in NONPOND_CA:
            role="nonpond_caudata_control_2"
        else:
            continue
        rows.append(dict(species=species,gbif_species_key=key,guild=guild,role=role))
    must(len(rows)==22 and
         sum(r["role"]=="frog_original_15" for r in rows)==15 and
         sum(r["role"]=="pond_caudata_original_5" for r in rows)==5 and
         sum(r["role"]=="nonpond_caudata_control_2" for r in rows)==2,
         "Predeclared G3 original eligible guild inventory changed")
    return rows


def facet_params(key,field="lifeStage"):
    # Official occurrence search with source-frozen year and country filters.
    return dict(taxonKey=int(key),country=COUNTRY,year=YEARS,
                hasCoordinate="true",hasGeospatialIssue="false",
                occurrenceStatus="PRESENT",facet=field,
                facetLimit=200,limit=0)


def get_facet(key,field="lifeStage",sleep_fn=time.sleep):
    params=facet_params(key,field=field)
    url=BASE+"?"+urllib.parse.urlencode(params)
    err=""
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"frogcs-G3-egg-stage-G0/2026-11-05 (source metadata feasibility)"
            })
            with urllib.request.urlopen(req,timeout=25) as handle:
                payload=json.loads(handle.read().decode("utf-8"))
            if not isinstance(payload,dict) or not isinstance(payload.get("count"),int):
                raise ValueError("Missing GBIF occurrence count")
            return dict(status="SUCCESS",total=payload["count"],facets=payload.get("facets",[]),
                        url=url,query=params,error="")
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,
                json.JSONDecodeError,ValueError,OSError) as e:
            err=str(e)[:400]
            if isinstance(e,urllib.error.HTTPError) and e.code in (400,401,403):
                return dict(status="UNSUPPORTED_OR_UNAUTHORIZED",total=None,
                            facets=None,url=url,query=params,error=err)
            if attempt<2:
                sleep_fn(1+attempt)
    return dict(status="API_ERROR_UNVERIFIED",total=None,facets=None,
                url=url,query=params,error=err)


def raw_facet_counts(reply,field):
    must(reply["status"]=="SUCCESS","Raw stage labels cannot be counted on source API error")
    results=[]
    for facet in reply["facets"]:
        name=str(facet.get("field","")).replace("_","").lower()
        if name!=field.lower().replace("_",""):
            continue
        for entry in facet.get("counts",[]):
            label=str(entry.get("name") or "").strip()
            count=int(entry.get("count",0))
            must(count>=0,"Negative source lifeStage occurrence count")
            results.append((label,count))
    return results


def explicit_egg(label):
    # Accept only unambiguous literal stage names, no substring matching.
    return re.sub(r"\s+"," ",str(label).strip().lower()) in EGG_LABELS


def extract_one(row):
    response=get_facet(row["gbif_species_key"])
    result=dict(**row,status=response["status"],
        gbif_total_US_2010_2025=response["total"],
        raw_lifestage_facet_labels=0,
        explicit_egg_stage_reports=None,
        adult_lifestage_reports=None,
        larval_lifestage_reports=None,
        source_url=response["url"],
        api_error=response["error"])
    details=[]
    if response["status"]!="SUCCESS":
        return result,details
    counts=raw_facet_counts(response,"lifeStage")
    egg=sum(n for label,n in counts if explicit_egg(label))
    adult=sum(n for label,n in counts if label.lower().strip() in ("adult","imago"))
    larval=sum(n for label,n in counts
               if label.lower().strip() in ("larva","larvae","tadpole","nymph"))
    result.update(raw_lifestage_facet_labels=len(counts),
                  explicit_egg_stage_reports=int(egg),
                  adult_lifestage_reports=int(adult),
                  larval_lifestage_reports=int(larval),
                  lifeStage_facet_exposed=bool(counts))
    details=[dict(role=row["role"],species=row["species"],gbif_species_key=row["gbif_species_key"],
                  raw_lifeStage_label=label,reported_count=n,
                  counted_as_explicit_egg=explicit_egg(label))
             for label,n in counts]
    return result,details


def gate(rows):
    if len(rows)!=22:
        raise AssertionError("G3 original source species inventory incomplete")
    if any(r["status"]!="SUCCESS" for r in rows):
        return dict(status="UNKNOWN_API_OR_SOURCE_INCOMPLETE",
            missing_source_taxa=[r["species"] for r in rows if r["status"]!="SUCCESS"],
            field_test_allowed=False)
    frog=[r for r in rows if r["role"]=="frog_original_15"]
    pond=[r for r in rows if r["role"]=="pond_caudata_original_5"]
    must(len(frog)==15 and len(pond)==5,"Original source guild role count changed")
    fg=sum(r["explicit_egg_stage_reports"]>=MIN_EGG_PER_SPECIES for r in frog)
    pg=sum(r["explicit_egg_stage_reports"]>=MIN_EGG_PER_SPECIES for r in pond)
    fe=sum(r["explicit_egg_stage_reports"] for r in frog)
    pe=sum(r["explicit_egg_stage_reports"] for r in pond)
    qualified=bool(fg>=MIN_FROG_EGG_SPECIES and pg>=MIN_POND_EGG_SPECIES
                   and fe>=MIN_TOTAL_EGGS and pe>=MIN_TOTAL_EGGS)
    return dict(
        status="G0_COUNTRY_STAGE_FACET_MINIMUM_PASSED_NEEDS_DATE_EFFORT_G1"
               if qualified else "G0_NOT_QUALIFIED_INSUFFICIENT_EXPLICIT_EGG_STAGE",
        field_test_allowed=False,
        next_phase_response_blind_date_effort_inventory_allowed=qualified,
        frog_original_species=15,pond_original_species=5,
        frog_species_at_least_50_egg_reports=int(fg),
        pond_species_at_least_50_egg_reports=int(pg),
        frog_explicit_egg_report_total=int(fe),
        pond_explicit_egg_report_total=int(pe),
        threshold_min_frog_species=MIN_FROG_EGG_SPECIES,
        threshold_min_pond_species=MIN_POND_EGG_SPECIES,
        threshold_each_species_explicit_egg_records=MIN_EGG_PER_SPECIES,
        threshold_each_guild_total=MIN_TOTAL_EGGS,
        report_count_not_breeding_onset=True
    )


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-manifest",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    taxa=source_taxa(a.source_manifest)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        output=list(pool.map(extract_one,taxa))
    rows=[a for a,b in output]
    labels=[v for a,b in output for v in b]
    conclusion=gate(rows)
    # The optional reproductiveCondition facet is an API capability check,
    # not a source-defined egg count and not a field data eligibility gate.
    checks=[]
    for role in ("frog_original_15","pond_caudata_original_5"):
        group=next(r for r in taxa if r["role"]==role)
        x=get_facet(group["gbif_species_key"],field="reproductiveCondition")
        checks.append(dict(taxon=group["species"],role=role,
                           status=x["status"],label_count=(
                              len(raw_facet_counts(x,"reproductiveCondition"))
                              if x["status"]=="SUCCESS" else None),
                           api_error=x["error"],url=x["url"],
                           field_not_eligibility_evidence=True))
    a.out.mkdir(parents=True,exist_ok=True)
    def save_csv(filename,data,fields):
        with (a.out/filename).open("w",encoding="utf-8",newline="") as fh:
            w=csv.DictWriter(fh,fieldnames=fields)
            w.writeheader()
            w.writerows(data)
    save_csv("original_22_taxon_lifestage_coverage.csv",rows,
             sorted(set().union(*(set(item) for item in rows))))
    save_csv("raw_gbif_lifestage_facet_labels.csv",labels,
             ["role","species","gbif_species_key","raw_lifeStage_label",
              "reported_count","counted_as_explicit_egg"])
    save_csv("optional_reproduction_facet_ability.csv",checks,list(checks[0]))
    receipt=dict(
        source_main_sha=ORIGINAL_MAIN_SHA,
        original_species_manifest_path=str(a.source_manifest),
        original_species_manifest_sha256=hashlib.sha256(a.source_manifest.read_bytes()).hexdigest(),
        checked_utc=datetime.now(timezone.utc).isoformat(),
        source="GBIF occurrence SEARCH facets, original US 2010-2025",
        exact_G0_filters=facet_params(taxa[0]["gbif_species_key"]),
        g0_result=conclusion,original_taxa_queried=22,
        source_API_failures=sum(r["status"]!="SUCCESS" for r in rows),
        original_raw_labels_examined=len(labels),
        source_taxonomy_outcome_selected=False,
        early_spring_adult_records_accepted_as_breeding=False,
        original_event_dates_downloaded=False,
        regional_breeding_lead_computed=False,
        field_vegetation_x_priority_regression_run=False,
        no_original_R1_R4_outcome_modified=True,
        note="Country-level stage reporting only. G1 exact dates/effort/site remains mandatory if G0 passes."
    )
    (a.out/"G3_GBIF_POND_BREEDING_G0_SOURCE_RECEIPT.json").write_text(
         json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("G3_GBIF_EGG_STAGE_G0_RESPONSE_BLIND_SOURCE_COMPLETE",json.dumps({
       "original_taxa_queried":len(rows), "result":conclusion,
       "errors":receipt["source_API_failures"],
       "raw_labels":len(labels)}),flush=True)
    for r in rows:
        print("TAXON_STAGE",json.dumps({
            k:r[k] for k in ("role","species","gbif_total_US_2010_2025",
                             "explicit_egg_stage_reports","raw_lifestage_facet_labels",
                             "status")}),flush=True)


if __name__=="__main__":
    main()
