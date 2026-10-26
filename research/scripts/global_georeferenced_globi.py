#!/usr/bin/env python3
"""Six macro-box actual georeferenced GloBI feeding-edge records (bounded pilot).

GloBI observed record = database association with spatial coordinates;
NOT automatically direct predation observation, rate, or verified experiment.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API="https://api.globalbioticinteractions.org/interaction"
AREAS=[
    ("North_America",[-170,5,-50,83]),
    ("South_America",[-83,-56,-35,5]),
    ("Europe_Mediterranean",[-25,31,45,72]),
    ("Africa",[-20,-36,52,31]),
    ("Asia",[45,-5,180,80]),
    ("Oceania",[110,-50,180,-5]),
]
DIRECTIONS=[
    ("frog_consumes_odonate","Anura","Odonata"),
    ("odonate_consumes_frog","Odonata","Anura"),
    ("frog_consumes_salamander","Anura","Caudata"),
    ("salamander_consumes_frog","Caudata","Anura"),
    ("frog_consumes_dytiscid","Anura","Dytiscidae"),
    ("dytiscid_consumes_frog","Dytiscidae","Anura"),
    ("frog_consumes_any","Anura",None),
    ("any_consumes_frog",None,"Anura"),
]
FIELDS=[
    "source_taxon_name","source_taxon_path","source_specimen_life_stage",
    "source_specimen_occurrence_id","interaction_type",
    "target_taxon_name","target_taxon_path","target_specimen_life_stage",
    "target_specimen_occurrence_id",
    "latitude","longitude","study_citation"
]
SPECIES=re.compile(r"^[A-Z][a-z]+ [a-z][a-z-]+$")
STAGE=re.compile(
    r"egg|embryo|larv|tadpol|nymph|instar|pupa|adult|imago|young|juvenil|metamorph|fry|hatchling|subadult|post-j",
    re.I
)
BAD={"", "na", "-999", "unknown", "undefined", "unreported"}
MAX_ROWS_PER_QUERY=200


def fetch(url):
    r=Request(url,headers={"User-Agent":"FrogcsGlobalGeoAudit/0.1 (GloBI public species evidence)",
                           "Accept":"application/json"})
    with urlopen(r, timeout=45) as reply:
        return json.loads(reply.read().decode("utf8"))


def valid_stage(a):
    v=str(a or "").strip()
    return v if v.lower() not in BAD and STAGE.search(v) else ""


def parse_record(r,origin,box,label,source,target):
    x=str(r.get("source_taxon_name") or "").strip()
    y=str(r.get("target_taxon_name") or "").strip()
    if not SPECIES.fullmatch(x) or not SPECIES.fullmatch(y):
        return None
    if r.get("interaction_type") not in ("eats","preysOn"):
        return None
    if source and source not in {i.strip() for i in str(
            r.get("source_taxon_path") or "").split("|")}:
        return None
    if target and target not in {i.strip() for i in str(
            r.get("target_taxon_path") or "").split("|")}:
        return None
    try:
        lat=float(r.get("latitude"))
        lon=float(r.get("longitude"))
    except (ValueError,TypeError):
        return None
    if (not math.isfinite(lat) or not math.isfinite(lon) or
        abs(lat)>90 or abs(lon)>180 or
        (abs(lat)<.001 and abs(lon)<.001)):
        return None
    citation=str(r.get("study_citation") or "").strip()
    if not citation:
        return None
    stx=valid_stage(r.get("source_specimen_life_stage"))
    sty=valid_stage(r.get("target_specimen_life_stage"))
    id1=str(r.get("source_specimen_occurrence_id") or "").strip()
    id2=str(r.get("target_specimen_occurrence_id") or "").strip()
    key=hashlib.sha256(("\t".join([
        citation,x,y,stx,sty,
        f"{lat:.5f}",f"{lon:.5f}",id1,id2,
        ])).encode("utf8")).hexdigest()
    source_path={p.strip() for p in str(r.get("source_taxon_path") or "").split("|")}
    target_path={p.strip() for p in str(r.get("target_taxon_path") or "").split("|")}
    predator_kind=(
        "Anura" if "Anura" in source_path else
        "Caudata" if "Caudata" in source_path else
        "Odonata" if "Odonata" in source_path else
        "Dytiscidae" if "Dytiscidae" in source_path else
        "Nepomorpha" if "Nepomorpha" in source_path else
        "Actinopterygii" if "Actinopterygii" in source_path else
        "Reptilia" if "Reptilia" in source_path else
        "Aves" if "Aves" in source_path else
        "Mammalia" if "Mammalia" in source_path else "other")
    return dict(
        record_id=key[:24],box_label=origin,query_role=label,
        predator_guild=predator_kind,
        prey_is_anuran=int("Anura" in target_path),
        predator_is_anuran=int("Anura" in source_path),
        self_conspecific_feeding=int(x==y),
        predator=x,prey=y,
        predator_stage=stx,prey_stage=sty,
        predator_occurrence_id=id1,prey_occurrence_id=id2,
        latitude=lat,longitude=lon,
        interaction_type=r["interaction_type"],
        study_citation=citation, source_api_url=box,
        evidence_class="unverified_database_record",
        stage_both=int(bool(stx and sty)),
        tropical=int(abs(lat)<23.5),
        absolute_latitude_band=("tropical" if abs(lat)<23.5
                                else "temperate" if abs(lat)<66.5 else "polar")
    )


def run(folder):
    out=Path(folder);out.mkdir(parents=True,exist_ok=True)
    seen={}
    queries=[]
    fail=[]
    for name,coords in AREAS:
        for tag,src,tar in DIRECTIONS:
            params={
                "bbox":",".join(str(a) for a in coords),
                "interactionType":"eats","includeObservations":"true",
                "limit":MAX_ROWS_PER_QUERY,
                "fields":",".join(FIELDS)
            }
            if src:params["sourceTaxon"]=src
            if tar:params["targetTaxon"]=tar
            url=API+"?"+urlencode(params)
            try:
                j=fetch(url)
            except Exception as exc:
                fail.append(dict(macrobox=name,role=tag,error=str(exc)[:300]))
                continue
            cols=j.get("columns",[])
            data=j.get("data",[])
            kept=0
            for row in data:
                record=parse_record(dict(zip(cols,row)),name,url,tag,src,tar)
                if record:
                    kept+=1
                    id=record["record_id"]
                    if id not in seen:
                        seen[id]=record
            queries.append(dict(macrobox=name,role=tag,
                                url=url,returned=len(data),valid_geolocated_species_events=kept))
    if len(seen)<20:
        raise RuntimeError("Too few real georeferenced GloBI species records to proceed: "+str(len(seen)))
    records=sorted(seen.values(),key=lambda r:(r["box_label"],r["predator"],r["prey"],r["record_id"]))
    fields=list(records[0])
    with (out/"global_geolocated_associations.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(records)
    groups=[]
    for name,_ in AREAS:
        rr=[r for r in records if r["box_label"]==name]
        groups.append(dict(
            macrobox=name,rows=len(rr),
            stage_both=sum(r["stage_both"] for r in rr),
            stage_at_least_one=sum(bool(r["predator_stage"] or r["prey_stage"]) for r in rr),
            distinct_directed_binomial_edges=len(set((r["predator"],r["prey"]) for r in rr)),
            study_citations=len(set(r["study_citation"] for r in rr)),
            iNaturalist_observation_links=sum("inaturalist.org/observations/" in r["study_citation"] for r in rr),
            trophic_frogs_as_predator=sum(r["predator_is_anuran"] for r in rr),
            trophic_frogs_as_prey=sum(r["prey_is_anuran"] for r in rr),
            n_conspec_feeding=sum(r["self_conspecific_feeding"] for r in rr),
            predator_guild_counts=dict(collections.Counter(r["predator_guild"] for r in rr))
        ))
    rkeys=set((r["predator"],r["prey"]) for r in records)
    reciprocal=sorted(set(tuple(sorted((a,b))) for a,b in rkeys
                          if a!=b and (b,a) in rkeys))
    self_feeding=sorted(set(a for a,b in rkeys if a==b))
    perSource=collections.Counter(r["study_citation"] for r in records)
    rr=collections.Counter((r["predator"],r["prey"]) for r in records)
    summary={
        "date":"2026-10-25",
        "method":"Live GloBI API geolocated feeding-association records; 6 world macroboxes, 8 query roles, capped 200/query, source-deduplicated",
        "source":"https://api.globalbioticinteractions.org/interaction",
        "published_stable_recommendation":"https://doi.org/10.5281/zenodo.3950589",
        "n_successful_queries":len(queries),
        "n_failed_queries":len(fail),
        "rows_reported_before_dedup":sum(x["returned"] for x in queries),
        "eligible_before_dedup":sum(x["valid_geolocated_species_events"] for x in queries),
        "unique_geolocated_associations":len(records),
        "distinct_directed_species_pairs":len(rkeys),
        "distinct_taxa":len(set(x for r in records for x in
                               (r["predator"],r["prey"]))),
        "stage_both_labeled":sum(r["stage_both"] for r in records),
        "stage_either_labeled":sum(bool(r["predator_stage"] or r["prey_stage"]) for r in records),
        "distinct_study_citations":len(perSource),
        "reciprocal_binomial_pair_candidates":len(reciprocal),
        "conspecific_feeding_taxon_candidates":len(self_feeding),
        "conspecific_feeding_species_examples":self_feeding[:12],
        "reciprocal_pair_examples":reciprocal[:12],
        "macroboxes":groups,
        "top_source_record_share":perSource.most_common(1)[0][1]/len(records),
        "top_sources":[dict(citation=k[:220],count=v) for k,v in perSource.most_common(8)],
        "top_directed_pairs":[dict(predator=a,prey=b,count=n)
                              for (a,b),n in rr.most_common(15)],
        "query_errors":fail,
        "inferential_limits":[
            "Bounding-box API pages are not a random or exhaustive sample of global interactions.",
            "A coordinate is GloBI source record location, not verified evidence of a natural predation event or at-pond interaction intensity.",
            "Records from the same study, iNaturalist occurrence or food-web list are nonindependent; latitude effects are sampling-dependent.",
            "Macroboxes are coarse query geometries, not strictly political/ecological continents and may overlap; dedup attempted by citation and source occurrence.",
            "No global frequency of trophic stage reversal and no statistical prevalence or P-value can be reported from this subset.",
            "Macrophyte structure, rainfall, wetland hydroperiod and GBIF site records were not attached to GloBI source points.",
        ]
    }
    (out/"observed_results.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"source_queries.json").write_text(json.dumps(queries,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("BEGIN_GLOBI_GEO_OBSERVED")
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("END_GLOBI_GEO_OBSERVED")


def test():
    data=dict(source_taxon_name="Pseudacris regilla",
              source_taxon_path="Amphibia | Anura",
              source_specimen_life_stage="adult",
              source_specimen_occurrence_id="sample-101",
              interaction_type="eats",
              target_taxon_name="Anax junius",
              target_taxon_path="Insecta | Odonata",
              target_specimen_life_stage="larva",
              target_specimen_occurrence_id="sample-102",
              latitude=35.0,longitude=-115.0,study_citation="doi:test")
    a=parse_record(data,"NA","testurl","frog_consumes_odonate","Anura","Odonata")
    assert a and a["stage_both"]==1 and a["absolute_latitude_band"]=="temperate"
    assert a["predator_is_anuran"] == 1 and a["prey_is_anuran"] == 0
    assert a["predator_guild"] == "Anura"
    assert parse_record(data,"NA","testurl","frog_consumes_caudata","Anura","Caudata") is None
    data["latitude"]=0;data["longitude"]=0
    assert parse_record(data,"NA","testurl","frog_consumes_odonate","Anura","Odonata") is None
    print("SYNTHETIC_GEO_QA_PASS")


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="research/results/global_globi_geo")
    a.add_argument("--self-test",action="store_true")
    opts=a.parse_args()
    if opts.self_test:test()
    else:run(opts.out)
