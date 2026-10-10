#!/usr/bin/env python3
"""v5.5 official MDMS vs frog SamplePoint EXACT candidate label join only.

Freeze: V5_5_MDMS_SAMPLE_POINT_SOURCE_CROSSWALK_CONTRACT.md.
Takes public CEWH GeoJSON, and a 2-column public frog CKAN projection, compares
two candidate keys NAME and SAMO_ID separately. No coordinates or individual
site values/names are output, written or embedded in logs. An exact NAME match
alone does NOT verify independent ecological wetland unit identity.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

BASE="https://data.gov.au/data/api/3/action/"
MDMS_RESOURCE="35b2b6d7-2557-49c9-bcc0-af98d17cb49a"
FROG_RESOURCE="70f3b7c9-990b-4770-b306-57c4e7cdac61"
ALLOWED_HOSTS={"data.gov.au","www.data.gov.au"}

def norm(x):
    return " ".join(unicodedata.normalize("NFKC",str(x or "")).split()).casefold()

def get(url,limit):
    u=urllib.parse.urlparse(url)
    if u.scheme!="https" or u.hostname not in ALLOWED_HOSTS:
        raise ValueError("untrusted government URL")
    req=urllib.request.Request(url,headers={"Accept":"application/json",
          "User-Agent":"frogcs-cewh-mdms-frog-label-only-coverage-v55"})
    with urllib.request.urlopen(req,timeout=40) as r:
        after=urllib.parse.urlparse(r.geturl())
        if after.scheme!="https" or after.hostname not in ALLOWED_HOSTS:
            raise ValueError("unexpected redirect")
        b=r.read(limit+1)
        if r.status!=200 or len(b)>limit:
            raise ValueError("too much source data")
    return json.loads(b.decode("utf-8-sig")),sha256(b).hexdigest()

def source(meta):
    if meta.get("success") is not True:
        raise ValueError("source metadata not valid")
    d=meta.get("result") or {}
    if d.get("id")!=MDMS_RESOURCE or str(d.get("format","")).lower()!="geojson":
        raise ValueError("wrong MDMS resource")
    url=str(d.get("url") or "")
    q=urllib.parse.urlparse(url)
    if q.scheme!="https" or q.hostname not in ALLOWED_HOSTS:
        raise ValueError("bad MDMS URL hostname")
    return url

def audit(mdms,frog):
    features=mdms.get("features")
    if mdms.get("type")!="FeatureCollection" or not isinstance(features,list):
        raise ValueError("not source feature collection")
    if frog.get("success") is not True:
        raise ValueError("frog source invalid")
    o=frog.get("result") or {}
    rec=o.get("records")
    if not isinstance(rec,list) or len(rec)!=o.get("total") or len(rec)>2000:
        raise ValueError("not complete limited frog samplepoint coverage")
    frog_fields={x.get("id") for x in o.get("fields",[]) if isinstance(x,dict)}
    if frog_fields!={"Program","SamplePoint"}:
        raise ValueError("frog source must not contain any animal or coordinate fields")
    for f in features:
        if not isinstance(f,dict) or f.get("type")!="Feature" or not isinstance(f.get("properties"),dict):
            raise ValueError("invalid MDMS feature")
        if any(z not in f["properties"] for z in ("NAME","SAMO_ID")):
            raise ValueError("missing candidate MDMS keys")

    lookup={}
    for field in ("NAME","SAMO_ID"):
        maps=defaultdict(set)
        for i,f in enumerate(features):
            value=norm(f["properties"].get(field))
            if value:maps[value].add(i)
        lookup[field]=maps
    frog_sites=defaultdict(set)
    for row in rec:
        if not isinstance(row,dict) or set(row)-{"Program","SamplePoint","_id"}:
            raise ValueError("unapproved frog row fields")
        prog=str(row.get("Program") or "").strip()
        sample=norm(row.get("SamplePoint"))
        if prog and sample:
            frog_sites[prog].add(sample)
    result={"status":"OFFICIAL_MDMS_CANDIDATE_LABEL_OVERLAP_EVALUATED",
            "mdms_feature_count":len(features),
            "frog_source_row_count":len(rec),
            "frog_source_unique_samplepoint_count_by_program":{
                p:len(s) for p,s in sorted(frog_sites.items())},
            "join_is_exact_normalized_string_NOT_physical_wetland_verification":True,
            "no_coordinate_or_individual_site_id_printed_or_saved":True,
            "no_frog_response_values_accessed":True,
            "rc6_main_unchanged":True,"key_tests":{}}
    for field,m in lookup.items():
        region={}
        for program,samples in sorted(frog_sites.items()):
            uniquely={x for x in samples if x in m and len(m[x])==1}
            ambiguous={x for x in samples if x in m and len(m[x])>1}
            region[program]={
               "frog_unique_samplepoint_labels":len(samples),
               "exact_label_one_MDMS_feature":len(uniquely),
               "exact_label_2plus_MDMS_features_AMBIGUOUS":len(ambiguous),
               "frog_source_names_no_exact_MDMS_key_match":len(samples-uniquely-ambiguous)}
        result["key_tests"][field]={
           "mdms_nonempty_distinct_normalized_keys":len(m),
           "mdms_duplicate_label_key_groups":sum(len(ids)>1 for ids in m.values()),
           "mdms_features_under_duplicate_keys":sum(len(ids) for ids in m.values() if len(ids)>1),
           "per_frog_program_source_key_match":region}
    # Additional pre-declared GEOMETRY-ONLY ecological unit diagnostic:
    # Exact point-location collisions are checked IN MEMORY only and never
    # expose site IDs, coordinates, point clusters, reversibly hashed positions.
    official_name=lookup["NAME"]
    site_geometry_checks={}
    for program, samples in sorted(frog_sites.items()):
        feature_indices=[
            next(iter(official_name[label]))
            for label in samples if label in official_name and len(official_name[label])==1
        ]
        coord_fingerprints=Counter()
        geometry_types=Counter()
        missing_geometries=0
        categories=defaultdict(set)
        attribute_nonmissing=Counter()
        for index in feature_indices:
            feat=features[index]
            geom=feat.get("geometry")
            if not isinstance(geom,dict):
                missing_geometries+=1
                geometry_types["NULL"]+=1
                continue
            typ=str(geom.get("type") or "UNKNOWN")
            geometry_types[typ]+=1
            # Only exact equality; never compute distances or reveal values.
            if typ=="Point" and isinstance(geom.get("coordinates"),list) and len(geom["coordinates"])>=2:
                coords=geom["coordinates"]
                if all(isinstance(n,(int,float)) for n in coords[:2]):
                    coord_fingerprints[(coords[0],coords[1])]+=1
            for tag in ("POINT_CATE","PROGRAM"):
                v=str(feat["properties"].get(tag) or "").strip()
                if v:
                    categories[tag].add(norm(v))
                    attribute_nonmissing[tag]+=1
        site_geometry_checks[program]={
            "n_source_samplepoint_labels_with_unique_MDMS_NAME_match":len(feature_indices),
            "n_unique_exact_Point_coordinate_pairs_IN_MEMORY_ONLY":len(coord_fingerprints),
            "n_coordinate_pairs_shared_by_2plus_MDMS_source_labels":sum(n>1 for n in coord_fingerprints.values()),
            "n_labels_on_repeated_exact_coordinates":sum(n for n in coord_fingerprints.values() if n>1),
            "geometry_type_counts":dict(sorted(geometry_types.items())),
            "n_missing_geometries":missing_geometries,
            "attribute_number_distinct_VALUES_WITHOUT_VALUES":{
                 tag:len(categories[tag]) for tag in ("POINT_CATE","PROGRAM")},
            "attribute_nonmissing_feature_counts":dict(sorted(attribute_nonmissing.items())),
            "exact_unique_coordinates_not_independent_wetland_proof":True
        }
    result["matched_MDMS_exact_point_geometry_collision_QC_by_frog_program"]=site_geometry_checks
    flat=[k for s in frog_sites.values() for k in s]
    result["sum_unique_site_labels_per_program"]=len(flat)
    result["n_distinct_site_labels_across_ALL_three_frog_programs"]=len(set(flat))
    # Catch exact geometry collisions also ACROSS the three programmes, not
    # only within each programme's sample-name frame.
    globally=Counter()
    for name in set(flat):
        if name in official_name and len(official_name[name])==1:
            feat=features[next(iter(official_name[name]))]
            geo=feat.get("geometry")
            if isinstance(geo,dict) and geo.get("type")=="Point":
                values=geo.get("coordinates")
                if isinstance(values,list) and len(values)>=2 and all(
                    isinstance(q,(int,float)) for q in values[:2]):
                    globally[(values[0],values[1])]+=1
    result["n_unique_exact_MDMS_Point_coordinates_ALL_programs"]=len(globally)
    result["n_coordinate_collision_groups_between_ANY_source_programs"]=sum(v>1 for v in globally.values())
    return result

def self_test():
    features=[{"type":"Feature","geometry":{"type":"Point","coordinates":[100,35]},
        "properties":{"NAME":"River A","SAMO_ID":"9"}},
       {"type":"Feature","geometry":{"type":"Point","coordinates":[100,35]},
        "properties":{"NAME":"River A","SAMO_ID":"10"}},
       {"type":"Feature","geometry":{"type":"Point","coordinates":[101,36]},
        "properties":{"NAME":"River B","SAMO_ID":"11"}}]
    f={"success":True,"result":{"total":2,"fields":[{"id":"Program"},{"id":"SamplePoint"}],
        "records":[{"Program":"X","SamplePoint":" River  A "},
                   {"Program":"X","SamplePoint":"River B"}]}}
    z=audit({"type":"FeatureCollection","features":features},f)
    assert z["key_tests"]["NAME"]["per_frog_program_source_key_match"]["X"][
         "exact_label_2plus_MDMS_features_AMBIGUOUS"]==1
    assert z["key_tests"]["NAME"]["per_frog_program_source_key_match"]["X"][
         "exact_label_one_MDMS_feature"]==1
    assert z["matched_MDMS_exact_point_geometry_collision_QC_by_frog_program"]["X"]["n_coordinate_pairs_shared_by_2plus_MDMS_source_labels"]==0
    assert z["matched_MDMS_exact_point_geometry_collision_QC_by_frog_program"]["X"]["n_unique_exact_Point_coordinate_pairs_IN_MEMORY_ONLY"]==1
    assert "River A" not in json.dumps(z)
    assert "[100, 35]" not in json.dumps(z) and "[101, 36]" not in json.dumps(z)
    f["result"]["fields"].append({"id":"Latitude"})
    try:audit({"type":"FeatureCollection","features":features},f)
    except ValueError:pass
    else:raise AssertionError("geocoded unapproved source accepted")
    print("PASS: exact source-label join, MDMS duplicate cardinality and no site-identity disclosure")

def main():
    self_test()
    receipt={"status":"SOURCE_NOT_AVAILABLE",
       "source_MDMS_resource_id":MDMS_RESOURCE,
       "frog_source_resource_id":FROG_RESOURCE,
       "source_contract":"studies/climate_landscape/V5_5_MDMS_SAMPLE_POINT_SOURCE_CROSSWALK_CONTRACT.md"}
    try:
        meta,_=get(BASE+"resource_show?"+urllib.parse.urlencode({"id":MDMS_RESOURCE}),400000)
        url=source(meta)
        geo,hash_mdms=get(url,1_200_000)
        frog,hash_frog=get(BASE+"datastore_search?"+urllib.parse.urlencode({
            "resource_id":FROG_RESOURCE,"limit":1000,"fields":"Program,SamplePoint"}),800000)
        receipt.update(audit(geo,frog))
        receipt["mdms_full_document_sha256"]=hash_mdms
        receipt["frog_2field_projected_response_sha256"]=hash_frog
    except urllib.error.HTTPError as e:
        receipt.update(status="HTTP_SOURCE_UNAVAILABLE",http_code=e.code)
    except (urllib.error.URLError,TimeoutError) as e:
        receipt.update(status="NETWORK_SOURCE_UNAVAILABLE",error_type=type(e).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        receipt.update(status="SOURCE_JOIN_FAILED_CLOSED",error_type=type(e).__name__,
                       error=str(e)[:150])
    dest=Path("studies/climate_landscape/receipts/MDMS_FROG_EXACT_NAME_CANDIDATE_MATCH_V55.json")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
