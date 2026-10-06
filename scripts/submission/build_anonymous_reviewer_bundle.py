#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

IDENTITY_PATTERNS=[
    re.compile(r"zuizui0223",re.I),
    re.compile(r"rachelzhang",re.I),
    re.compile(r"zhang\s+ruiqi",re.I),
    re.compile(r"rachelzhang0223@gmail\.com",re.I),
    re.compile(r"[A-Z]:\\Users\\zuizui",re.I),
    re.compile(r"/Users/[^/]*rachel",re.I),
]

TEXT_SUFFIXES={".py",".json",".md",".txt",".yml",".yaml",".csv"}

def add_path(paths:set[str], value):
    if isinstance(value,str) and value:
        paths.add(value)

def collect_paths(spec:dict)->set[str]:
    paths={
        "provenance/CURRENT_RESULTS.json",
        "provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json",
        "revision/PULSE_TEMPLATE_FIGURE_DATA_V0_1.json",
        "revision/FIGURE_REBUILD_SPEC_V0_3.md",
        "revision/build_pulse_template_figures.py",
    }

    for section in ("primary_analysis_chain","supporting_information_diagnostics"):
        for item in spec.get(section,[]) or []:
            for key in ("contract","receipt","script","qc"):
                add_path(paths,item.get(key))
            prefix=item.get("path_prefix")
            if prefix:
                p=ROOT/prefix
                if p.exists():
                    for child in p.rglob("*.py"):
                        paths.add(str(child.relative_to(ROOT)))

    chain=spec.get("post_reopening_exploratory_chain",{}) or {}
    for item in chain.get("analyses",[]) or []:
        for key in ("contract","receipt","script","qc"):
            add_path(paths,item.get(key))

    audits=spec.get("numerical_audits",{}) or {}
    for item in audits.values():
        if isinstance(item,dict):
            for key in ("contract","receipt","script","qc"):
                add_path(paths,item.get(key))

    public_scale=spec.get("public_scale_validation",{}) or {}
    for item in public_scale.values():
        if isinstance(item,dict):
            for key in ("contract","receipt","script","qc"):
                add_path(paths,item.get(key))
        elif isinstance(item,str) and (item.endswith(".md") or item.endswith(".json") or item.endswith(".py")):
            add_path(paths,item)

    return paths

def text_identity_hits(path:Path)->list[str]:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    text=path.read_text(encoding="utf-8",errors="ignore")
    return [p.pattern for p in IDENTITY_PATTERNS if p.search(text)]

def deterministic_zip(staging:Path, output:Path):
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(staging.rglob("*")):
            if not p.is_file():
                continue
            rel=p.relative_to(staging).as_posix()
            info=zipfile.ZipInfo(rel,date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644 << 16
            z.writestr(info,p.read_bytes())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="build/Reviewer_Code.zip")
    ap.add_argument("--staging",default="build/anonymous-reviewer-code")
    args=ap.parse_args()

    spec=json.loads((ROOT/"provenance/CURRENT_ANALYSIS_SPECIFICATIONS.json").read_text(encoding="utf-8"))
    selected=collect_paths(spec)

    staging=ROOT/args.staging
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    copied=[]
    missing=[]
    for rel in sorted(selected):
        src=ROOT/rel
        if not src.exists() or not src.is_file():
            missing.append(rel)
            continue
        dst=staging/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        copied.append(rel)

    readme=staging/"README_FOR_REVIEW.md"
    readme.write_text(
        "# Anonymous reviewer code package\n\n"
        "This package contains the analysis scripts, frozen analysis specifications, "
        "selected result receipts and deterministic figure inputs supporting the manuscript "
        "“Rainfall-associated frog chorus activation is concentrated within taxa across multiple sites.”\n\n"
        "Raw third-party source datasets are not redistributed. Source data are available from:\n\n"
        "- North American Amphibian Monitoring Program: DOI 10.5066/F7G44NG0\n"
        "- FrogID dataset description/data citation: DOI 10.3897/zookeys.912.38253\n\n"
        "Historical internal filenames are retained where needed for reproducibility; they do not encode author identity. "
        "The final public code and derived-analysis archive will be deposited in a permanent repository after peer review.\n",
        encoding="utf-8",
    )

    hits=[]
    for p in staging.rglob("*"):
        if p.is_file():
            bad=text_identity_hits(p)
            if bad:
                hits.append({"path":str(p.relative_to(staging)),"patterns":bad})
    if hits:
        raise SystemExit("identity tokens detected in reviewer bundle: "+json.dumps(hits,indent=2))

    output=ROOT/args.output
    deterministic_zip(staging,output)

    # Re-open archive and verify file names/content again.
    with zipfile.ZipFile(output) as z:
        names=z.namelist()
        name_blob="\n".join(names)
        for pattern in IDENTITY_PATTERNS:
            if pattern.search(name_blob):
                raise SystemExit(f"identity token in archive filenames: {pattern.pattern}")
        for name in names:
            suffix=Path(name).suffix.lower()
            if suffix not in TEXT_SUFFIXES:
                continue
            text=z.read(name).decode("utf-8",errors="ignore")
            for pattern in IDENTITY_PATTERNS:
                if pattern.search(text):
                    raise SystemExit(f"identity token in archive content {name}: {pattern.pattern}")

    print(json.dumps({
        "status":"PASS",
        "output":str(output.relative_to(ROOT)),
        "files":len(copied)+1,
        "optional_missing_records":missing,
        "identity_hits":0,
    },indent=2))

if __name__=="__main__":
    main()
