#!/usr/bin/env python3
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"

files=sorted(p for p in SCRIPTS.glob("*.py") if p.name not in {
    "migrate_script_layout.py","migrate_submission_json.py"
})
mapping={}
for p in files:
    if p.name.startswith("run_naamp_"):
        dest=Path("scripts/naamp")/p.name
    elif p.name.startswith("run_frogid_") or p.name=="run_crosscontinental_active_depth.py":
        dest=Path("scripts/frogid")/p.name
    elif p.name.startswith("audit_"):
        dest=Path("scripts/qa")/p.name
    else:
        dest=Path("scripts/submission")/p.name
    mapping[f"scripts/{p.name}"]=dest.as_posix()

for target in mapping.values():
    (ROOT/target).parent.mkdir(parents=True,exist_ok=True)

for old,target in mapping.items():
    src=ROOT/old
    dst=ROOT/target
    text=src.read_text(encoding="utf-8")
    # Files moved one directory deeper need repo-root calculations adjusted.
    if target.startswith("scripts/qa/") or target.startswith("scripts/submission/"):
        text=text.replace("Path(__file__).resolve().parents[1]","Path(__file__).resolve().parents[2]")
        text=text.replace("Path(__file__).resolve().parent.parent","Path(__file__).resolve().parents[2]")
    # These QA scripts use ROOT specifically as the script directory containing NAAMP runners.
    if Path(old).name in {
        "audit_naamp_observer_schema.py",
        "audit_dry_dry_background_estimability.py",
        "audit_naamp_active_community_trait_coverage.py",
    }:
        text=text.replace(
            "ROOT = Path(__file__).resolve().parent",
            'ROOT = Path(__file__).resolve().parents[1] / "naamp"'
        ).replace(
            "ROOT=Path(__file__).resolve().parent",
            'ROOT=Path(__file__).resolve().parents[1]/"naamp"'
        )
    dst.write_text(text,encoding="utf-8")
    src.unlink()

# Rewrite explicit scripts/<file> references in all active non-workflow text surfaces.
replacements=0
touched=[]
for base in [ROOT/"scripts",ROOT/"submission",ROOT/"provenance",ROOT/"README.md"]:
    paths=[base] if base.is_file() else list(base.rglob("*"))
    for p in paths:
        if not p.is_file() or p.suffix.lower() not in {".py",".md",".json",".yml",".yaml",".txt",".cff"}:
            continue
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
            replacements+=n; touched.append(str(p.relative_to(ROOT)))

manifest={
    "status":"PASS","moved_scripts":len(mapping),
    "categories":{
        "naamp":sum(v.startswith("scripts/naamp/") for v in mapping.values()),
        "frogid":sum(v.startswith("scripts/frogid/") for v in mapping.values()),
        "qa":sum(v.startswith("scripts/qa/") for v in mapping.values()),
        "submission":sum(v.startswith("scripts/submission/") for v in mapping.values()),
    },
    "reference_replacements":replacements,
    "mapping":mapping,"touched":touched
}
(ROOT/"provenance"/"SCRIPT_LAYOUT_MIGRATION_MANIFEST.json").write_text(
    json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"
)
print(json.dumps({k:v for k,v in manifest.items() if k not in {"mapping","touched"}},indent=2))
