#!/usr/bin/env python3
"""v6.2 bounded official Flow-MER package metadata and zero-record schema QA."""
from __future__ import annotations
from pathlib import Path
import json
import urllib.error
import urllib.parse
import urllib.request

HOST = "data.flow-mer.org.au"
API = f"https://{HOST}/api/3/action/"
PACKAGES = (
    "flow-mer-frog-abundance",
    "basin-flow-gauges-matched-to-monitoring-sample-points",
    "data-standards",
)

def read_api(action: str, params: dict, size: int = 1_500_000) -> dict:
    if action not in {"package_show", "datastore_search"}:
        raise ValueError("UNAPPROVED_API_ACTION")
    url = API + action + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "frogcs-independent-source-schema-only-v62"
    })
    with urllib.request.urlopen(request, timeout=35) as response:
        final = urllib.parse.urlparse(response.geturl())
        if final.scheme != "https" or final.hostname != HOST:
            raise ValueError("UNTRUSTED_API_REDIRECT")
        data = response.read(size + 1)
        if response.status != 200 or len(data) > size:
            raise ValueError("UNEXPECTED_API_SIZE_OR_STATUS")
    obj = json.loads(data.decode("utf-8-sig"))
    if not isinstance(obj, dict) or obj.get("success") is not True or not isinstance(obj.get("result"), dict):
        raise ValueError("SOURCE_RESPONSE_NOT_SUCCESS")
    return obj["result"]

def text_limit(v, limit=200):
    return str(v or "")[:limit]

def safe_package(src: dict, expected_slug: str) -> dict:
    if str(src.get("name")) != expected_slug:
        raise ValueError("SOURCE_PACKAGE_SLUG_MISMATCH")
    rs = src.get("resources")
    if not isinstance(rs, list) or len(rs) > 150:
        raise ValueError("INVALID_RESOURCE_LIST")
    entry = {
        "package_slug": expected_slug,
        "id": text_limit(src.get("id"), 70),
        "title": text_limit(src.get("title"), 180),
        "metadata_created": text_limit(src.get("metadata_created"), 60),
        "metadata_modified": text_limit(src.get("metadata_modified"), 60),
        "license_id": text_limit(src.get("license_id"), 100),
        "description_char_count": len(str(src.get("notes") or "")),
        "resource_count": len(rs),
        "resource_metadata": [],
        "animal_observation_values_read": False,
    }
    for z in rs:
        resource_id = str(z.get("id", ""))
        if not resource_id or len(resource_id) > 100:
            raise ValueError("BAD_RESOURCE_ID")
        original_url = str(z.get("url") or "")
        parsed = urllib.parse.urlparse(original_url)
        entry["resource_metadata"].append({
            "id": resource_id,
            "format": text_limit(z.get("format"), 35),
            "size_bytes_declared": z.get("size") if type(z.get("size")) is int else None,
            "last_modified": text_limit(z.get("last_modified"), 70),
            "datastore_active": z.get("datastore_active") is True,
            "mimetype": text_limit(z.get("mimetype"), 90),
            "resource_url_host_only": (parsed.hostname or "")[:120],
        })
    return entry

def validate_datastore_schema(r: dict) -> dict:
    if r.get("records") != []:
        raise ValueError("NONZERO_SOURCE_RECORDS_RETURNED_FAIL_CLOSED")
    fields = r.get("fields")
    if not isinstance(fields, list):
        raise ValueError("MISSING_DATASTORE_SCHEMA")
    names = []
    for field in fields:
        if not isinstance(field, dict):
            raise ValueError("INVALID_FIELD_METADATA")
        name = str(field.get("id") or "")
        if not name or len(name) > 128:
            raise ValueError("INVALID_FIELD_NAME")
        names.append({"column": name, "type": str(field.get("type") or "")[:70]})
    return {"server_reported_total": r.get("total") if type(r.get("total")) is int else None,
            "field_names_and_types_only": names, "records_returned": 0}

def tests():
    fake = {"name":"flow-mer-frog-abundance","id":"x","title":"Flow-MER Frog Abundance 2014-2024",
            "resources":[{"id":"abc","format":"CSV","url":"https://host.example/protected-site-string.csv","datastore_active":True}]}
    row = safe_package(fake,"flow-mer-frog-abundance")
    assert row["resource_metadata"][0]["resource_url_host_only"]=="host.example"
    assert "protected-site-string" not in json.dumps(row)
    assert validate_datastore_schema({"records":[],"fields":[{"id":"SampleDate","type":"timestamp"}],"total":1})["records_returned"]==0
    try:
        validate_datastore_schema({"records":[{"speciesCode":"SENSITIVE"}],"fields":[]})
    except ValueError as ex:
        assert str(ex)=="NONZERO_SOURCE_RECORDS_RETURNED_FAIL_CLOSED"
    else:raise AssertionError("Records in datastore metadata response accepted")
    print("PASS: metadata-only field allowlist and source-record leakage guard")

def main():
    tests()
    payload={"status":"SOURCE_METADATA_ATTEMPTED","official_portal":"https://data.flow-mer.org.au/",
             "source_results":[],"no_animal_rows_or_locations_accessed":True,
             "RC6_scientific_package_changed":False}
    for package in PACKAGES:
        result={"requested_package_slug":package,"status":"SOURCE_NOT_VERIFIED"}
        try:
            src=read_api("package_show",{"id":package})
            result.update(safe_package(src,package))
            result["status"]="PACKAGE_METADATA_VERIFIED"
            for z in result["resource_metadata"]:
                if z["datastore_active"]:
                    try:
                        schema=read_api("datastore_search",{"resource_id":z["id"],"limit":0})
                        z["zero_record_schema"]=validate_datastore_schema(schema)
                    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
                        z["zero_record_schema_status"]="UNAVAILABLE_OR_FAIL_CLOSED"
                        z["schema_error_type"]=type(exc).__name__
        except urllib.error.HTTPError as exc:
            result.update(status="HTTP_SOURCE_UNAVAILABLE",code=exc.code)
        except (urllib.error.URLError,TimeoutError) as exc:
            result.update(status="NETWORK_SOURCE_UNAVAILABLE",error_type=type(exc).__name__)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
            result.update(status="PACKAGE_METADATA_FAILED_CLOSED",error_type=type(exc).__name__)
        payload["source_results"].append(result)
    dst=Path("studies/climate_landscape/receipts/FLOWMER_PUBLIC_REGISTRY_METADATA_ONLY_V62.json")
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,sort_keys=True))

if __name__ == "__main__":
    main()
