#!/usr/bin/env python3
"""v5.5 government MDMS sample-point resource: SOURCE METADATA ONLY.

Reads official CKAN resource_show output and reports ONLY URL host, file format,
declared byte size, update timestamp and public file provenance. No geometry,
site ID, protected location or any fauna record is requested.
"""
from __future__ import annotations
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API="https://data.gov.au/data/api/3/action/resource_show"
ID="35b2b6d7-2557-49c9-bcc0-af98d17cb49a"

def inspect(obj):
    if not isinstance(obj,dict) or obj.get("success") is not True:
        raise ValueError("not a successful CKAN resource metadata receipt")
    x=obj.get("result")
    if not isinstance(x,dict) or x.get("id")!=ID:
        raise ValueError("resource identity mismatch")
    location=urllib.parse.urlparse(str(x.get("url") or ""))
    # URLs are NOT opened by this script; never authorize arbitrary redirects.
    return {
      "resource_id":ID,"package_id":x.get("package_id"),
      "resource_name":str(x.get("name") or "")[:130],
      "resource_format":x.get("format"),
      "declared_bytes":x.get("size"),
      "url_hostname":location.hostname,
      "url_https":location.scheme=="https",
      "ckan_mimetype":x.get("mimetype"),
      "last_modified":x.get("last_modified") or x.get("created"),
      "resource_is_public_document_not_verified_site_crosswalk":True,
      "no_geojson_download_or_coordinates_requested":True,
      "no_frog_records_accessed":True,
      "rc6_unchanged":True,
      "status":"OFFICIAL_MDMS_SOURCE_METADATA_OK"
    }

def self_test():
    x={"success":True,"result":{"id":ID,"url":"https://data.gov.au/example.geojson",
      "size":1024,"format":"GeoJSON"}}
    y=inspect(x)
    assert y["url_hostname"]=="data.gov.au"
    assert y["declared_bytes"]==1024
    for bad in ({"success":False,"result":x["result"]},
                {"success":True,"result":dict(x["result"],id="wrong")}):
        try:inspect(bad)
        except ValueError:pass
        else:raise AssertionError("bad official resource accepted")
    print("PASS: official CKAN resource ID/metadata validation; no sensitive data")

def main():
    self_test()
    q=API+"?"+urllib.parse.urlencode({"id":ID})
    z={"status":"OFFICIAL_SOURCE_UNAVAILABLE","official_dataset":
      "https://data.gov.au/data/dataset/mdms-monitoring-locations",
      "resource_id":ID,"no_geojson_or_fauna_records_read":True,
      "rc6_unchanged":True}
    try:
        request=urllib.request.Request(q,headers={"Accept":"application/json",
          "User-Agent":"frogcs-official-mdms-source-metadata-v55"})
        with urllib.request.urlopen(request,timeout=35) as response:
            content=response.read(400001)
            if response.status!=200 or len(content)>400000:
                raise ValueError("unbounded metadata response")
        z.update(inspect(json.loads(content.decode("utf-8"))))
    except urllib.error.HTTPError as exc:
        z.update(status="HTTP_SOURCE_UNAVAILABLE",http_status=exc.code)
    except (urllib.error.URLError,TimeoutError) as exc:
        z.update(status="NETWORK_SOURCE_UNAVAILABLE",error_type=type(exc).__name__)
    except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        z.update(status="SOURCE_METADATA_FAILED_CLOSED",error_type=type(exc).__name__,
                 error_text=str(exc)[:150])
    path=Path("studies/climate_landscape/receipts/MDMS_SOURCE_METADATA_V55.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(z,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(z,sort_keys=True))

if __name__=="__main__":
    main()
