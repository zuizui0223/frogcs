#!/usr/bin/env python3
"""v6.3 source-provenance fix: canonical university/ARDC slug; metadata only."""
from __future__ import annotations
import json
from pathlib import Path
from urllib import request, parse, error

HOST = "data.flow-mer.org.au"
PACKAGE = "flow-mer-frogs"
URI = f"https://{HOST}/api/3/action/package_show?" + parse.urlencode({"id": PACKAGE})

def safe_metadata(payload):
    if payload.get("success") is not True or not isinstance(payload.get("result"), dict):
        raise ValueError("UNEXPECTED_PACKAGE_RESPONSE")
    p=payload["result"]
    if p.get("name") != PACKAGE:
        raise ValueError("PACKAGE_SLUG_NOT_VERIFIED")
    resources=p.get("resources")
    if not isinstance(resources,list) or len(resources)>150:
        raise ValueError("UNEXPECTED_RESOURCES")
    def tiny(x,n=160):return str(x or "")[:n]
    return {
      "title":tiny(p.get("title")),
      "canonical_slug":PACKAGE,
      "metadata_created":tiny(p.get("metadata_created")),
      "metadata_modified":tiny(p.get("metadata_modified")),
      "license_id":tiny(p.get("license_id")),
      "resources":[{"id":tiny(z.get("id"),90),
                    "format":tiny(z.get("format"),50),
                    "datastore_active":z.get("datastore_active") is True}
                   for z in resources if isinstance(z,dict)],
      "records_read":0
    }

def checks():
    z={"success":True,"result":{"name":PACKAGE,"title":"Sample frog registry",
                                      "resources":[{"id":"dummy","format":"CSV","url":"https://host/sensitive_location.csv"}]}}
    q=safe_metadata(z)
    assert q["records_read"]==0 and "sensitive_location" not in json.dumps(q)
    try:safe_metadata({"success":True,"result":{"name":"wrong","resources":[]}})
    except ValueError as e:assert str(e)=="PACKAGE_SLUG_NOT_VERIFIED"
    else:raise AssertionError("incorrect slug accepted")
    print("PASS: canonical-slug and no-source-row synthetic metadata checks")

def main():
    checks()
    receipt={
      "canonical_slug":PACKAGE,
      "source_registry":"Charles Sturt University / Australian Research Data Commons",
      "status":"METADATA_SOURCE_UNAVAILABLE",
      "no_animal_records_or_site_values_accessed":True,
      "no_raw_audio_accessed":True,
      "submitted_rc6_unchanged":True
    }
    try:
        req=request.Request(URI,headers={"Accept":"application/json","User-Agent":"frogcs-official-registry-metadata-v63"})
        with request.urlopen(req,timeout=30) as response:
            final=parse.urlparse(response.geturl())
            if final.scheme!="https" or final.hostname !=HOST:
                raise ValueError("UNTRUSTED_SOURCE_REDIRECT")
            b=response.read(1_500_001)
            if response.status!=200 or len(b)>1_500_000:
                raise ValueError("UNEXPECTED_RESPONSE_STATUS_OR_SIZE")
        receipt["verified_metadata"]=safe_metadata(json.loads(b.decode("utf-8-sig")))
        receipt["status"]="PACKAGE_METADATA_VERIFIED_ONLY"
    except error.HTTPError as e:
        receipt["http_status"]=e.code
        receipt["status"]=f"CORRECT_PACKAGE_API_{e.code}_METADATA_NOT_RETRIEVED"
    except (error.URLError,TimeoutError) as e:
        receipt["status"]="NETWORK_SOURCE_UNAVAILABLE"
        receipt["error_type"]=type(e).__name__
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        receipt["status"]="SOURCE_FAILED_CLOSED"
        receipt["error_type"]=type(e).__name__
    p=Path("studies/climate_landscape/receipts/FLOWMER_CORRECT_FROGS_PACKAGE_METADATA_V63.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    main()
