#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROV = ROOT / "provenance"

TEXT_SUFFIXES = {
    ".py", ".yml", ".yaml", ".md", ".json", ".txt", ".toml", ".cff", ".template"
}
SKIP_TOP = {".git", "archive"}


def classify(name: str) -> Path:
    if "_CONTRACT_" in name:
        return Path("provenance/contracts") / name
    if "_SUMMARY_" in name:
        return Path("provenance/summaries") / name
    if "_RECEIPT_" in name:
        return Path("provenance/receipts") / name
    if "_REPAIR_" in name:
        return Path("provenance/repairs") / name
    return Path("provenance/metadata") / name


def is_text_candidate(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if not rel.parts:
        return False
    if rel.parts[0] in SKIP_TOP:
        return False
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"README", "LICENSE"}


def main() -> None:
    root_json = sorted(ROOT.glob("*.json"))
    if not root_json:
        raise SystemExit("No root JSON files found; migration already applied?")

    mapping = {p.name: classify(p.name).as_posix() for p in root_json}

    for rel in mapping.values():
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)

    for p in root_json:
        target = ROOT / mapping[p.name]
        if target.exists():
            raise RuntimeError(f"target already exists: {target.relative_to(ROOT)}")
        shutil.move(str(p), str(target))

    rewritten = 0
    replacements = 0
    touched = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not is_text_candidate(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        local = 0
        for old, target in mapping.items():
            n = new.count(old)
            if n:
                new = new.replace(old, target)
                local += n
        if new != text:
            path.write_text(new, encoding="utf-8")
            rewritten += 1
            replacements += local
            touched.append(path.relative_to(ROOT).as_posix())

    readme = PROV / "README.md"
    readme.write_text(
        "# Provenance JSON\n\n"
        "Root-level JSON files are intentionally prohibited. Scientific provenance is grouped here by role.\n\n"
        "- contracts/: frozen analysis definitions and decision rules.\n"
        "- summaries/: durable compact outputs used by the manuscript, SI, README or submission audits.\n"
        "- receipts/: detailed machine-readable run outputs and audit receipts.\n"
        "- repairs/: versioned implementation or estimability repairs.\n"
        "- metadata/: claim boundaries, source identities, manifests, ledgers and other provenance metadata.\n\n"
        "Active scripts and workflows reference these paths directly. Historical release branches preserve the old root-level layout.\n",
        encoding="utf-8",
    )

    stale = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not is_text_candidate(path):
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] == "archive":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits = [old for old, target in mapping.items() if old in text and target not in text]
        if hits:
            stale[rel.as_posix()] = hits
    if stale:
        raise RuntimeError("stale root JSON references remain: " + json.dumps(stale, indent=2))

    leftovers = sorted(p.name for p in ROOT.glob("*.json"))
    if leftovers:
        raise RuntimeError(f"root JSON leftovers: {leftovers}")

    manifest = {
        "status": "PASS",
        "moved_json_files": len(mapping),
        "rewritten_text_files": rewritten,
        "reference_replacements": replacements,
        "categories": {
            "contracts": sum("/contracts/" in v for v in mapping.values()),
            "summaries": sum("/summaries/" in v for v in mapping.values()),
            "receipts": sum("/receipts/" in v for v in mapping.values()),
            "repairs": sum("/repairs/" in v for v in mapping.values()),
            "metadata": sum("/metadata/" in v for v in mapping.values()),
        },
        "mapping": mapping,
        "touched_reference_files": touched,
    }
    (PROV / "ROOT_JSON_MIGRATION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in manifest.items() if k not in {"mapping", "touched_reference_files"}}, indent=2))


if __name__ == "__main__":
    main()
