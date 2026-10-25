#!/usr/bin/env python3
"""Live global GloBI occurrence-level food-web × GBIF country facets.

Scope: exploratory GLOBAL occurrence-opportunity map, NOT observed predation,
frog chorus ecology, realized competition, eDNA state or vegetation causality.
Use the stable GloBI release and authenticated GBIF download for final inference.
Designed to run on public GitHub Actions in <20min with finite API limits.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import csv
import hashlib
import json
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GLOBI = "https://api.globalbioticinteractions.org/interaction"
GBIF = "https://api.gbif.org/v1"
DATE = "2026-10-25"
GUILDS = [
    ("Anura", "Odonata"), ("Odonata", "Anura"),
    ("Anura", "Caudata"), ("Caudata", "Anura"),
    ("Anura", "Dytiscidae"), ("Dytiscidae", "Anura"),
    ("Anura", "Nepomorpha"), ("Nepomorpha", "Anura"),
    ("Anura", "Actinopterygii"), ("Actinopterygii", "Anura"),
    ("Anura", "Decapoda"), ("Decapoda", "Anura"),
    ("Caudata", "Odonata"), ("Odonata", "Caudata"),
    ("Caudata", "Dytiscidae"), ("Dytiscidae", "Caudata"),
    ("Odonata", "Actinopterygii"), ("Actinopterygii", "Odonata"),
]
PLANT_SPECIES = [
    "Phragmites australis", "Typha latifolia", "Typha angustifolia",
    "Schoenoplectus lacustris", "Schoenoplectus tabernaemontani",
    "Bolboschoenus maritimus", "Eleocharis palustris"
]
GLOBI_FIELDS = [
    "source_taxon_name", "source_taxon_path", "source_specimen_life_stage",
    "interaction_type", "target_taxon_name", "target_taxon_path",
    "target_specimen_life_stage", "study_citation",
]
PAT_BIN = re.compile(r"^[A-Z][a-z]+ [a-z][a-z-]+$")
KNOWN_STAGE = re.compile(
    r"egg|embryo|larv|tadpol|nymph|instar|pupa|adult|imago|"
    r"young|juvenil|metamorph|fry|fingerling|hatchling|subadult|post-j",
    re.I
)
BAD_STAGE = {"", "na", "n/a", "unknown", "-999", "none", "unreported"}
COUNTRY_MIN = 5
COUNTRY_STRICT = 20
MAX_SPECIES = 120
MAX_EDGES = 105
MAX_PER_DIRECTION = 12
MAX_SOURCE_EDGE = 8


def req_json(url, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "FrogcsGlobalMacro/0.1 (source-cited noncommercial scientific audit)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=32) as ans:
                return json.loads(ans.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError,
                TimeoutError, ValueError) as exc:
            last = str(exc)
            if i < retries-1:
                time.sleep(min(1.6*(i+1), 5))
    raise RuntimeError(f"Source request failed: {url}; last error {last}")


def form(base, **kwargs):
    return base + "?" + urllib.parse.urlencode(kwargs)


def stage(raw):
    r = str(raw or "").strip()
    if r.lower() in BAD_STAGE:
        return ""
    return r if KNOWN_STAGE.search(r) else ""


def binomial(name):
    return bool(PAT_BIN.fullmatch(str(name or "").strip()))


def in_guild(taxon_path, guild):
    """GloBI taxonomic path uses explicit | delimiter."""
    return guild in {part.strip() for part in str(taxon_path or "").split("|")}


def analyze_guild_record(raw, guild_source, guild_target):
    if not isinstance(raw, list) or len(raw) != len(GLOBI_FIELDS):
        return None
    rec = dict(zip(GLOBI_FIELDS, raw))
    if rec["interaction_type"] not in {"eats", "preysOn"}:
        return None
    src = str(rec["source_taxon_name"] or "").strip()
    tar = str(rec["target_taxon_name"] or "").strip()
    if not binomial(src) or not binomial(tar) or src == tar:
        return None
    if not in_guild(rec["source_taxon_path"], guild_source):
        return None
    if not in_guild(rec["target_taxon_path"], guild_target):
        return None
    cite = str(rec["study_citation"] or "").strip()
    if not cite:
        return None
    return dict(
        predator=src, prey=tar, predator_guild=guild_source,
        prey_guild=guild_target,
        predator_stage=stage(rec["source_specimen_life_stage"]),
        prey_stage=stage(rec["target_specimen_life_stage"]),
        cite=cite,
    )


def fetch_globi(max_per_page=200, second_page=False):
    all_edges = {}
    receipt = []
    for gi, (src, tar) in enumerate(GUILDS):
        for offset in ([0, max_per_page] if second_page else [0]):
            url = form(GLOBI,
                       sourceTaxon=src, targetTaxon=tar,
                       interactionType="eats", includeObservations="true",
                       fields=",".join(GLOBI_FIELDS),
                       limit=max_per_page, offset=offset)
            try:
                result = req_json(url)
            except RuntimeError as exc:
                receipt.append({
                    "direction": f"{src}->{tar}", "offset": offset,
                    "error": str(exc)[:290],
                })
                continue
            cols = result.get("columns", [])
            rows = result.get("data", [])
            if not isinstance(rows, list):
                rows = []
            kept = 0
            for raw in rows:
                rec = dict(zip(cols, raw))
                record = analyze_guild_record(
                    [rec.get(key) for key in GLOBI_FIELDS], src, tar)
                if not record:
                    continue
                kept += 1
                key = (record["predator"], record["prey"], src, tar)
                pair = all_edges.setdefault(key, dict(
                    predator=key[0], prey=key[1],
                    predator_guild=src, prey_guild=tar,
                    studies=set(), stages=set(),
                    observed_rows=0))
                pair["observed_rows"] += 1
                pair["studies"].add(record["cite"])
                if record["predator_stage"] or record["prey_stage"]:
                    pair["stages"].add((record["predator_stage"],
                                        record["prey_stage"]))
            receipt.append(dict(direction=f"{src}->{tar}", url=url,
                                offset=offset, returned=len(rows), eligible=kept))
            if len(rows) < max_per_page:
                break
    return all_edges, receipt


def select_edges(edges):
    """Selection before GBIF geography, balanced across directional guilds."""
    by_dir = collections.defaultdict(list)
    for p in edges.values():
        by_dir[(p["predator_guild"], p["prey_guild"])].append(p)
    for group in by_dir.values():
        group.sort(key=lambda p: (
            -min(len(p["studies"]), 4),
            -int(any(a and b for a,b in p["stages"])),
            -int(bool(p["stages"])),
            p["predator"], p["prey"]))
    species = set()
    chosen = []
    per_dir = collections.Counter()
    per_study = collections.Counter()
    ix = {k:0 for k in by_dir}
    while len(chosen) < MAX_EDGES:
        changed = False
        for guild in GUILDS:
            if per_dir[guild] >= MAX_PER_DIRECTION:
                continue
            group = by_dir.get(guild, [])
            while ix.get(guild, 0) < len(group):
                p = group[ix[guild]]
                ix[guild] += 1
                new_species = {p["predator"],p["prey"]} - species
                if len(species)+len(new_species) > MAX_SPECIES:
                    continue
                primary_study=sorted(p["studies"])[0]
                if per_study[primary_study] >= MAX_SOURCE_EDGE:
                    continue
                chosen.append(p)
                species.update(new_species)
                per_study[primary_study] += 1
                per_dir[guild] += 1
                changed = True
                break
        if not changed:
            break
    return chosen, per_dir, per_study


def get_gbif(name):
    try:
        matching = req_json(form(
            GBIF+"/species/match", name=name, strict="true"))
        if (matching.get("rank") != "SPECIES" or
                matching.get("matchType") != "EXACT" or
                int(matching.get("confidence",0)) < 90 or
                not matching.get("speciesKey")):
            return dict(query_name=name, status="unmatched_or_ambiguous",
                        match=matching)
        key = int(matching["speciesKey"])
        url = form(GBIF+"/occurrence/search",
                   taxonKey=key, limit=0, facet="country", facetLimit=250,
                   hasCoordinate="true", hasGeospatialIssue="false",
                   year="2010,2026", occurrenceStatus="PRESENT")
        result = req_json(url)
        facets = result.get("facets", [])
        countries = {}
        for facet in facets:
            if str(facet.get("field","")).upper() == "COUNTRY":
                countries = {a["name"]:int(a["count"])
                             for a in facet.get("counts",[])
                             if re.fullmatch(r"[A-Z]{2}",str(a.get("name","")))}
        return dict(
            query_name=name, status="accepted",
            taxon_key=key, accepted_name=matching.get("species",""),
            match_type=matching.get("matchType"),
            status_accepted=matching.get("status"),
            confidence=int(matching.get("confidence",0)),
            taxonomic_order=matching.get("order", ""),
            n_occurrences=int(result.get("count",0)),
            n_countries_all=len(countries),
            country_counts=countries,
            gbif_query=url)
    except Exception as exc:
        return dict(query_name=name, status="source_error",
                    error=str(exc)[:290])


def normalized_presence(taxon, threshold):
    if taxon is None or taxon.get("status")!="accepted":
        return set()
    return {k for k,v in taxon.get("country_counts",{}).items()
            if v>=threshold}


def make_country_summary(edges, taxa, plants):
    rows = []
    all_countries=set()
    for entity in list(taxa.values()) + list(plants.values()):
        all_countries.update(entity.get("country_counts",{}))
    for country in sorted(all_countries):
        supported = []
        low_stage = 0
        pred = set(); prey=set(); frogs=set()
        for p in edges:
            a=taxa.get(p["predator"],{})
            b=taxa.get(p["prey"],{})
            if (country in normalized_presence(a,COUNTRY_MIN)
                    and country in normalized_presence(b,COUNTRY_MIN)):
                supported.append(p)
                pred.add(p["predator"]); prey.add(p["prey"])
                if p["predator_guild"]=="Anura":
                    frogs.add(p["predator"])
                if p["prey_guild"]=="Anura":
                    frogs.add(p["prey"])
                if any(a and b for a,b in p["stages"]):
                    low_stage += 1
        plants_here = [
            name for name,obj in plants.items()
            if country in normalized_presence(obj,COUNTRY_MIN)]
        rows.append(dict(
            country=country,
            documented_link_opportunities=len(supported),
            documented_stage_specific_opportunities=low_stage,
            unique_predator_species=len(pred), unique_prey_species=len(prey),
            unique_frog_species=len(frogs),
            emergent_proxy_species_reported=len(plants_here),
            has_plant_proxy=int(bool(plants_here)),
            qualifier="GBIF_COUNTRY_CO_REPORTING_ONLY",
        ))
    return rows


def write_csv(dest, rows, cols):
    with open(dest,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run(output_dir, second_page=False):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    edges, receipts=fetch_globi(second_page=second_page)
    if len(edges)<10:
        raise ValueError(f"GloBI directional query insufficient: {len(edges)}")
    selected,per_dir,per_study=select_edges(edges)
    if len(selected)<10:
        raise ValueError(f"GloBI balanced selection insufficient: {len(selected)}")
    species = sorted({sp for p in selected for sp in
                      [p["predator"],p["prey"]]})
    allnames=species+PLANT_SPECIES
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(get_gbif, allnames))
    taxonmap={r["query_name"]:r for r in records}
    taxon={s:taxonmap[s] for s in species}
    plants={s:taxonmap[s] for s in PLANT_SPECIES}
    accepted = [p for p in selected if
                taxon[p["predator"]]["status"]=="accepted" and
                taxon[p["prey"]]["status"]=="accepted"]
    pairrows=[]
    for p in accepted:
        predator=taxon[p["predator"]]
        prey=taxon[p["prey"]]
        pc=normalized_presence(predator,COUNTRY_MIN)
        qc=normalized_presence(prey,COUNTRY_MIN)
        overlap=pc & qc
        strict=(normalized_presence(predator,COUNTRY_STRICT)
                & normalized_presence(prey,COUNTRY_STRICT))
        p_stages=sorted(p["stages"])
        pairrows.append(dict(
            predator=p["predator"],prey=p["prey"],
            predator_guild=p["predator_guild"],
            prey_guild=p["prey_guild"],
            predator_gbif_taxon_key=predator["taxon_key"],
            prey_gbif_taxon_key=prey["taxon_key"],
            n_gbif_countries_predator=len(pc),
            n_gbif_countries_prey=len(qc),
            n_gbif_countries_both=len(overlap),
            n_gbif_countries_both_min20=len(strict),
            any_both_stage_labeled=int(any(a and b for a,b in p_stages)),
            paired_stage_patterns=json.dumps(p_stages, ensure_ascii=False),
            source_stages="; ".join(sorted({a for a,b in p_stages if a})),
            target_stages="; ".join(sorted({b for a,b in p_stages if b})),
            distinct_original_citations=len(p["studies"]),
            example_source=sorted(p["studies"])[0][:400],
            source_record_count=p["observed_rows"],
            classification="COUNTRY_CO_REPORTED_POTENTIAL_NOT_OBSERVED_INTERACTION",
        ))
    countryrows=make_country_summary(accepted,taxon,plants)
    taxa_out=[]
    for x in records:
        taxa_out.append(dict(
            taxon=x["query_name"],layer="plant_proxy"
            if x["query_name"] in PLANT_SPECIES else "trophic",
            status=x["status"],
            gbif_taxon_key=x.get("taxon_key",""),
            reported_total_georeferenced_present_records=x.get("n_occurrences",""),
            gbif_countries_any=x.get("n_countries_all",""),
            gbif_countries_min5=len(normalized_presence(x,COUNTRY_MIN)),
            gbif_countries_min20=len(normalized_presence(x,COUNTRY_STRICT)),
            gbif_match=x.get("accepted_name",""),
            error=x.get("error",""),
            gbif_api_url=x.get("gbif_query",""),
        ))
    write_csv(out/"global_country_coverage.csv",countryrows,[
        "country","documented_link_opportunities",
        "documented_stage_specific_opportunities",
        "unique_predator_species","unique_prey_species","unique_frog_species",
        "emergent_proxy_species_reported","has_plant_proxy","qualifier"])
    write_csv(out/"selected_trophic_pairs.csv",pairrows,[
        "predator","prey","predator_guild","prey_guild",
        "predator_gbif_taxon_key","prey_gbif_taxon_key",
        "n_gbif_countries_predator","n_gbif_countries_prey",
        "n_gbif_countries_both","n_gbif_countries_both_min20",
        "any_both_stage_labeled","paired_stage_patterns",
        "source_stages","target_stages",
        "distinct_original_citations","example_source","source_record_count",
        "classification"])
    write_csv(out/"gbif_species_match_audit.csv",taxa_out,[
        "taxon","layer","status","gbif_taxon_key",
        "reported_total_georeferenced_present_records",
        "gbif_countries_any","gbif_countries_min5","gbif_countries_min20",
        "gbif_match","error","gbif_api_url"])
    reciprocal=set((p["predator"],p["prey"]) for p in accepted)
    reciprocal_pairs=set(tuple(sorted((a,b)))
                         for a,b in reciprocal if (b,a) in reciprocal)
    rowcounts=sum(x.get("returned",0) for x in receipts)
    eligible_rows=sum(x.get("eligible",0) for x in receipts)
    summary=dict(
        program="GloBI × GBIF global geographic interaction OPPORTUNITY pilot",
        query_date=DATE,
        inference="descriptive_nonrepresentative_API_pilot",
        globi_source="Live GloBI API (NOT pinned complete stable release)",
        globi_stable_release="https://doi.org/10.5281/zenodo.3950589",
        gbif_source="https://api.gbif.org/v1, current live taxon/match and country facet",
        gbif_query_filter={
            "hasCoordinate":True,"hasGeospatialIssue":False,
            "year":"2010-2026","occurrenceStatus":"PRESENT",
            "country_min_records":COUNTRY_MIN,
            "sensitivity_country_min_records":COUNTRY_STRICT
        },
        globi_queries=len(receipts),globi_direction_groups=len(GUILDS),
        globi_downloaded_rows=rowcounts,globi_eligible_rows=eligible_rows,
        globi_unique_directed_species_edges=len(edges),
        selected_edges_pre_geography=len(selected),
        selected_taxa_pre_geography=len(species),
        selected_sources=len(per_study),
        selected_directions={f"{a}->{b}":n for (a,b),n in per_dir.items()},
        gbif_taxa_requested=len(allnames),
        gbif_trophic_taxa_accepted=sum(x["status"]=="accepted"
                                        for x in taxon.values()),
        gbif_trophic_taxa_unresolved=sum(x["status"]!="accepted"
                                          for x in taxon.values()),
        gbif_plants_accepted=sum(x["status"]=="accepted"
                                 for x in plants.values()),
        eligible_pairs_with_gbif_matches=len(accepted),
        pairs_with_country_overlap_min5=sum(x["n_gbif_countries_both"]>0
                                             for x in pairrows),
        pairs_with_country_overlap_min20=sum(x["n_gbif_countries_both_min20"]>0
                                              for x in pairrows),
        reciprocal_named_pair_candidates=len(reciprocal_pairs),
        stage_both_labeled_pair_candidates=sum(x["any_both_stage_labeled"]
                                               for x in pairrows),
        n_countries_any_gbif=sum(
            any(x["country_counts"].get(country,0)>0
                for x in records if x.get("status")=="accepted")
            for country in {a for x in records
                           for a in x.get("country_counts",{})}),
        countries_with_potential_links=sum(
            row["documented_link_opportunities"]>0 for row in countryrows),
        countries_with_plant_proxies=sum(
            row["emergent_proxy_species_reported"]>0 for row in countryrows),
        top_countries=sorted(countryrows,
            key=lambda row:(-row["documented_link_opportunities"],row["country"]))[:16],
        top_pairs=sorted(pairrows,
            key=lambda row:(-row["n_gbif_countries_both"],
                            -row["distinct_original_citations"],
                            row["predator"],row["prey"]))[:14],
        methodological_warnings=[
            "Global GBIF reporting across a country is not local co-occurrence, predation or native range.",
            "Species and plant report opportunities are biased by GBIF access, duplicate sightings and citizen science.",
            "GloBI API first pages are selected nonrandomly; not a global prevalence, frequency or statistically representative interaction sample.",
            "GloBI original sources may be inferred food-web links, not independently observed attacks.",
            "Species-stage information in GloBI concerns documented feeding-edge stages, not GBIF occurrence life stages.",
            "Country plant presence is NOT wetland emergent-cover area or local structural complexity.",
            "No rain, pond hydroperiod, local frog chorus or methylation-eDNA was joined at country level.",
            "Species not matched to exact GBIF species excluded before spatial metric; full records need DOI-versioned GloBI and GBIF bulk download.",
            "No null-model P value or causal wetland result is provided from these opportunity counts."
        ],
        download_errors=[q for q in receipts if "error" in q]
    )
    (out/"observed_results.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"source_query_receipt.json").write_text(
        json.dumps(receipts,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_GLOBAL_GLOBI_GBIF_RESULTS")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("END_GLOBAL_GLOBI_GBIF_RESULTS")
    return summary


def selftest():
    x=dict(source_taxon_name="Pseudacris regilla",
           source_taxon_path="root | Animalia | Amphibia | Anura | Pseudacris",
           source_specimen_life_stage="adult",interaction_type="eats",
           target_taxon_name="Anax junius",
           target_taxon_path="root | Animalia | Insecta | Odonata | Anax",
           target_specimen_life_stage="larval",
           study_citation="One published source")
    rec=analyze_guild_record([x[f] for f in GLOBI_FIELDS],"Anura","Odonata")
    assert rec and rec["predator_stage"]=="adult" and rec["prey_stage"]=="larval"
    assert not analyze_guild_record([x[f] for f in GLOBI_FIELDS],
                                    "Anura","Caudata")
    assert not stage("-999") and not binomial("Anax") and binomial("Anax junius")
    counts={"US":30,"CA":6,"MX":1}
    assert normalized_presence({"status":"accepted","country_counts":counts},5)=={"US","CA"}
    sample=[dict(predator="Pseudacris regilla",prey="Anax junius",
                 predator_guild="Anura",prey_guild="Odonata",
                 stages={("adult","larval")})]
    t={"Pseudacris regilla":{"status":"accepted","country_counts":{"US":30,"CA":6}},
       "Anax junius":{"status":"accepted","country_counts":{"US":20,"MX":4}}}
    plant={"Phragmites australis":{
        "status":"accepted","country_counts":{"US":100}}}
    result=make_country_summary(sample,t,plant)
    us=[r for r in result if r["country"]=="US"][0]
    assert us["documented_link_opportunities"]==1
    assert us["emergent_proxy_species_reported"]==1
    ca=[r for r in result if r["country"]=="CA"][0]
    assert ca["documented_link_opportunities"]==0
    print(json.dumps({"synthetic_only":True,"status":"PASS",
                      "tested":"life stage, binomial/taxon path, country co-report"}))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="research/results/global_globi_gbif")
    ap.add_argument("--second-page",action="store_true")
    ap.add_argument("--self-test",action="store_true")
    aa=ap.parse_args()
    if aa.self_test:selftest()
    else:run(aa.out,aa.second_page)
