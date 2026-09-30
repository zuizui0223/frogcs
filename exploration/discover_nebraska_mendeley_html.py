#!/usr/bin/env python3
import html, json, re
from pathlib import Path
import requests

PAGE="https://data.mendeley.com/datasets/p6nbn2hyz9/1"
TARGET="BorealChorusFrogCallingActivityDataset.xlsx"
OUT=Path("exploration/NEBRASKA_MENDELEY_HTML_DISCOVERY_V0_1.json")

def main():
    r=requests.get(PAGE,headers={"User-Agent":"Mozilla/5.0"},timeout=60)
    r.raise_for_status()
    txt=html.unescape(r.text)
    uuids=sorted(set(re.findall(r"(?i)[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",txt)))
    urls=sorted(set(re.findall(r"https?://[^\"'<>\\ ]+",txt)))
    candidates=[
        u for u in urls
        if any(k in u.lower() for k in ("download","public-files","file_downloaded","p6nbn2hyz9"))
    ]
    pos=txt.find(TARGET)
    near=txt[max(0,pos-2500):pos+2500] if pos>=0 else ""
    near_uuids=sorted(set(re.findall(r"(?i)[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",near)))
    near_urls=sorted(set(re.findall(r"https?://[^\"'<>\\ ]+",near)))
    out={
      "analysis":"nebraska_mendeley_html_discovery_v0_1",
      "page_status":r.status_code,
      "html_bytes":len(r.content),
      "target_filename_present":pos>=0,
      "all_uuid_count":len(uuids),
      "near_filename_uuids":near_uuids,
      "candidate_urls":candidates[:100],
      "near_filename_candidate_urls":[u for u in near_urls if "download" in u.lower() or "p6nbn2hyz9" in u.lower()][:50],
    }
    OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
