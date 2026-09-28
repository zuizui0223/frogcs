#!/usr/bin/env python3
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUB=ROOT/"submission"
DEST=ROOT/"provenance"/"submission"
DEST.mkdir(parents=True,exist_ok=True)

files=sorted(p for p in SUB.glob("*.json") if p.name!="ZENODO_METADATA_TEMPLATE.json")
mapping={f"submission/{p.name}":f"provenance/submission/{p.name}" for p in files}

for p in files:
    target=DEST/p.name
    if target.exists(): raise RuntimeError(target)
    shutil.move(str(p),str(target))

rewrites=0
touched=[]
for base in [ROOT/"scripts", ROOT/"submission", ROOT/"provenance", ROOT/"README.md"]:
    paths=[base] if base.is_file() else list(base.rglob("*"))
    for p in paths:
        if not p.is_file() or p.suffix.lower() not in {".py",".md",".json",".yml",".yaml",".txt",".cff"}: continue
        try: text=p.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        new=text
        n=0
        for old,target in mapping.items():
            k=new.count(old)
            if k:
                new=new.replace(old,target); n+=k
        if new!=text:
            p.write_text(new,encoding="utf-8")
            rewrites+=n; touched.append(str(p.relative_to(ROOT)))

manifest={"status":"PASS","moved":len(mapping),"mapping":mapping,"reference_replacements":rewrites,"touched":touched}
(DEST/"SUBMISSION_JSON_MIGRATION_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in manifest.items() if k not in {"mapping","touched"}},indent=2))
