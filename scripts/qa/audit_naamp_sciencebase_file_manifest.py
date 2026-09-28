#!/usr/bin/env python3
import json, urllib.request
from pathlib import Path

ITEM="https://www.sciencebase.gov/catalog/item/583dc314e4b0d1899f9dea8d?format=json"
req=urllib.request.Request(ITEM,headers={"User-Agent":"frogcs-source-manifest-audit/0.1","Accept":"application/json"})
with urllib.request.urlopen(req,timeout=60) as r:
    obj=json.loads(r.read().decode("utf-8"))
rows=[]
for f in obj.get("files") or []:
    rows.append({
      "name":f.get("name"),
      "contentType":f.get("contentType"),
      "size":f.get("size"),
      "downloadUri":f.get("downloadUri")
    })
out={"analysis":"naamp_sciencebase_file_manifest_audit_v0_1","n_files":len(rows),"files":rows}
Path("NAAMP_SCIENCEBASE_FILE_MANIFEST_AUDIT_V0_1.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
