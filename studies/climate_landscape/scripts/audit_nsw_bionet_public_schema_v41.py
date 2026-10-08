#!/usr/bin/env python3
"""v4.1 NSW BioNet public OData metadata-only survey-data availability gate.

Reads ONLY the official service document and OData $metadata; does not fetch
species sightings, animal locations, dates, counts or raw frog outcomes.
A schema field name is not evidence that historic survey values exist.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT="https://data.bionet.nsw.gov.au/biosvcapp/odata"
TARGETS=(
    "SpeciesSightings_CoreDataExtended",
    "SpeciesSightings_AdditionalMeasurementsOrFacts",
    "SpeciesSightings_CoreData",
)
CAP_BYTES=3_000_000
NS="{http://docs.oasis-open.org/odata/ns/edm}"

def service_summary(raw):
    obj=json.loads(raw.decode("utf-8"))
    values=obj.get("value")
    if not isinstance(values,list):
        raise ValueError("official OData service document has no entity set list")
    names=sorted(str(x.get("name","")) for x in values if isinstance(x,dict))
    if not names or any(not n or len(n)>150 for n in names):
        raise ValueError("invalid entity list")
    return {"n_public_entity_sets":len(names),
            "target_entity_sets_present":{name:name in names for name in TARGETS},
            "separate_SystematicFaunaSurvey_entity_set":any("SystematicFauna" in name for name in names)}

def schema_summary(xml_bytes):
    root=ET.fromstring(xml_bytes)
    schema_types={}
    for schema in root.iter(NS+"Schema"):
        namespace=schema.attrib.get("Namespace","")
        for entity in schema.findall(NS+"EntityType"):
            name=entity.attrib.get("Name","")
            if name:
                schema_types[namespace+"."+name]=sorted(
                    x.attrib.get("Name","")
                    for x in entity.findall(NS+"Property")
                    if x.attrib.get("Name"))
    sets={}
    for entityset in root.iter(NS+"EntitySet"):
        name=entityset.attrib.get("Name","")
        if name in TARGETS:
            typ=entityset.attrib.get("EntityType","")
            sets[name]={"entity_type":typ,
                        "n_properties":len(schema_types.get(typ,[])),
                        "property_names":schema_types.get(typ,[])}
    return {"target_schema_fields":sets,
            "schema_note":"field names only, not non-missing values or row counts"}

def get_public_metadata(url, kind):
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!="https" or parsed.netloc!="data.bionet.nsw.gov.au":
        raise ValueError("URL not whitelisted NSW BioNet metadata source")
    req=urllib.request.Request(url,headers={
        "Accept":"application/json" if kind=="service" else "application/xml",
        "User-Agent":"frogcs-public-metadata-only-audit/4.1"})
    with urllib.request.urlopen(req,timeout=30) as res:
        body=res.read(CAP_BYTES+1)
        if res.status!=200 or len(body)>CAP_BYTES:
            raise ValueError("Unexpected metadata status/length")
        return body

def self_test():
    sample=json.dumps({"value":[{"name":TARGETS[0]},{"name":TARGETS[1]}]}).encode()
    summary=service_summary(sample)
    assert summary["target_entity_sets_present"][TARGETS[0]]
    assert not summary["target_entity_sets_present"][TARGETS[2]]
    xml=(f'<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">'
         f'<edmx:DataServices><Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="M">'
         f'<EntityType Name="Sightings"><Key><PropertyRef Name="observationID"/></Key>'
         f'<Property Name="observationID" Type="Edm.String"/>'
         f'<Property Name="eventDate" Type="Edm.Date"/></EntityType>'
         f'<EntityContainer Name="C"><EntitySet Name="{TARGETS[0]}" EntityType="M.Sightings"/>'
         f'</EntityContainer></Schema></edmx:DataServices></edmx:Edmx>').encode()
    r=schema_summary(xml)
    assert r["target_schema_fields"][TARGETS[0]]["property_names"]==["eventDate","observationID"]
    try:
        service_summary(b'{"value":"notalist"}')
    except ValueError:
        pass
    else:
        raise AssertionError("invalid entity schema accepted")
    print("PASS: synthetic public service and XML metadata gates; no species observations")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--receipt",default="studies/climate_landscape/receipts/NSW_BIONET_ODATA_PUBLIC_SCHEMA_V41.json")
    a=ap.parse_args()
    if a.self_test:
        self_test()
        return
    result={
        "audit":"nsw_bionet_official_odata_schema_only_v41",
        "source_service_document":ROOT,
        "source_schema_document":ROOT+"/$metadata",
        "publication":"Ocock et al. 2024; frog survey sightings available via BioNet, ancillary data on request",
        "read_scope":"entity names and property names only",
        "data_endpoint_authenticated":False,
        "fauna_records_downloaded":False,
        "species_sightings_read":False,
        "frog_call_values_read":False,
        "hydrology_values_read":False,
        "rc6_unchanged":True,
    }
    for key,url,parser in (
        ("service",ROOT,service_summary),
        ("schema",ROOT+"/$metadata",schema_summary),
    ):
        try:
            raw=get_public_metadata(url,key)
            result[key+"_status"]="PUBLIC_METADATA_OK"
            result[key+"_summary"]=parser(raw)
        except urllib.error.HTTPError as ex:
            result[key+"_status"]="SOURCE_HTTP_ERROR"
            result[key+"_http_code"]=ex.code
        except (urllib.error.URLError,TimeoutError) as ex:
            result[key+"_status"]="NETWORK_UNAVAILABLE"
            result[key+"_error_type"]=type(ex).__name__
        except (ValueError,ET.ParseError,json.JSONDecodeError) as ex:
            result[key+"_status"]="SOURCE_SCHEMA_UNEXPECTED"
            result[key+"_error_type"]=type(ex).__name__
    path=Path(a.receipt)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "service_status":result.get("service_status"),
        "schema_status":result.get("schema_status"),
        "target_entities":result.get("service_summary",{}).get("target_entity_sets_present"),
        "target_schema_field_counts":{k:v.get("n_properties") for k,v
            in result.get("schema_summary",{}).get("target_schema_fields",{}).items()},
        "frog_call_values_read":False,
    },sort_keys=True))

if __name__=="__main__":
    main()
