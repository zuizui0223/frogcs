#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]
TITLE="Rainfall-associated expansion of frog active communities is more boundary-biased than uniform activation predicts"

# ---------- repository structure ----------
CURRENT_ROOT_FILES={
    "README.md","MANUSCRIPT_JAE_V1_3.md",
    "SUPPORTING_INFORMATION_JAE_RC11_V0_1.md","JAE_TITLE_PAGE_V0_8.template.md",
}
CURRENT_ROOT_DIRS={".github","figures_ecology_v1_0","figures_ecology_v1_2","provenance","scripts","submission"}
CURRENT_SUBMISSION_FILES={"CITATION.cff.template","COVER_LETTER_JAE_V0_13.md","SUBMISSION_METADATA_TEMPLATE_V0_7.yml"}
SCRIPT_LAYOUT={"naamp":11,"frogid":1,"qa":2,"submission":2}
CURRENT_WORKFLOWS={"reproduce_current_results.yml","submission_pipeline.yml"}
CURRENT_PROVENANCE_FILES={
    "CURRENT_ANALYSIS_SPECIFICATIONS.json",
    "receipts/README.md",
    "submission/RC11_STORY_FREEZE_V0_1.json",
    "summaries/CROSSCONTINENTAL_ACTIVE_DEPTH_SUMMARY_V0_1.json",
    "summaries/NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_SUMMARY_V0_1.json",
    "summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json",
    "summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json",
    "summaries/NAAMP_SORENSEN_EQUIVALENCE_SUMMARY_V0_1.json",
    "summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json",
}

root_files={p.name for p in ROOT.iterdir() if p.is_file()}
root_dirs={p.name for p in ROOT.iterdir() if p.is_dir() and p.name!=".git"}
assert root_files==CURRENT_ROOT_FILES,{"unexpected_root_files":sorted(root_files-CURRENT_ROOT_FILES),"missing":sorted(CURRENT_ROOT_FILES-root_files)}
assert root_dirs==CURRENT_ROOT_DIRS,{"unexpected_root_dirs":sorted(root_dirs-CURRENT_ROOT_DIRS),"missing":sorted(CURRENT_ROOT_DIRS-root_dirs)}
assert not list(ROOT.glob("*.json"))

submission=ROOT/"submission"
submission_files={p.name for p in submission.iterdir() if p.is_file()}
assert submission_files==CURRENT_SUBMISSION_FILES,{"unexpected_submission_files":sorted(submission_files-CURRENT_SUBMISSION_FILES),"missing":sorted(CURRENT_SUBMISSION_FILES-submission_files)}

scripts=ROOT/"scripts"
assert not list(scripts.glob("*.py"))
assert {p.name for p in scripts.iterdir() if p.is_dir()}==set(SCRIPT_LAYOUT)
for name,expected in SCRIPT_LAYOUT.items():
    got=len(list((scripts/name).glob("*.py")))
    assert got==expected,(name,got,expected)

active_workflows=ROOT/".github/workflows"
active_names={p.name for p in active_workflows.glob("*.yml")}
assert active_names==CURRENT_WORKFLOWS,{"unexpected_workflows":sorted(active_names-CURRENT_WORKFLOWS),"missing":sorted(CURRENT_WORKFLOWS-active_names)}

prov=ROOT/"provenance"
spec_bundle=json.loads((prov/"CURRENT_ANALYSIS_SPECIFICATIONS.json").read_text(encoding="utf-8"))
EXPECTED_SPEC_KEYS={
    "CROSSCONTINENTAL_ACTIVE_DEPTH_CONTRACT_V0_1",
    "FROGID_TIMEZONE_REPAIR_CONTRACT_V0_1",
    "NAAMP_DETECTION_QUALITY_ROBUSTNESS_CONTRACT_V0_1",
    "NAAMP_ECOLOGICAL_PULSE_CONTRACT_V0_1",
    "NAAMP_GEOGRAPHIC_GENERALITY_AUDIT_CONTRACT_V0_1",
    "NAAMP_METACOMMUNITY_ALPHA_BETA_GAMMA_CONTRACT_V0_1",
    "NAAMP_PERSISTENCE_PRESERVING_NULL_CONTRACT_V0_1",
    "NAAMP_PROTOCOL_WINDOW_SENSITIVITY_CONTRACT_V0_1",
    "NAAMP_SAME_OBSERVER_ROBUSTNESS_CONTRACT_V0_1",
    "NAAMP_SORENSEN_EQUIVALENCE_CONTRACT_V0_1",
    "NAAMP_SPATIAL_TAXONOMIC_ACTIVATION_CONTRACT_V0_1",
    "NAAMP_UNIFORM_ACTIVATION_NULL_CONTRACT_V0_1",
    "NAAMP_WITHIN_ACTIVE_DEPTH_CONTRACT_V0_1",
    "NAAMP_UNIFORM_ACTIVATION_NULL_REPAIR_V0_1_1",
    "RC10_SCOPE_UNFREEZE_V0_1",
    "RC10_STORY_DECISION_TREE_V0_1",
    "RC8_CROSSCONTINENTAL_DEPTH_UNFREEZE_V0_1",
}
assert set(spec_bundle["items"])==EXPECTED_SPEC_KEYS

prov_files={p.relative_to(prov).as_posix() for p in prov.rglob("*") if p.is_file()}
assert prov_files==CURRENT_PROVENANCE_FILES,{"unexpected_provenance":sorted(prov_files-CURRENT_PROVENANCE_FILES),"missing":sorted(CURRENT_PROVENANCE_FILES-prov_files)}

required=[
    ROOT/"scripts/qa/audit_current_submission.py",
    ROOT/"scripts/qa/audit_naamp_sciencebase_file_manifest.py",
    ROOT/"scripts/submission/build_jae_anonymous_docx.py",
    ROOT/"scripts/submission/render_submission_metadata.py",
    prov/"submission/RC11_STORY_FREEZE_V0_1.json",
]
for p in required: assert p.exists(),f"missing current file: {p.relative_to(ROOT)}"

# Historical flat paths must not return.
legacy={}
legacy_patterns=[
    re.compile(r'(?<![A-Za-z0-9_./-])scripts/(?:run_|audit_|build_|render_|finalize_)[A-Za-z0-9_.-]+\.py'),
    re.compile(r'(?<![A-Za-z0-9_./-])submission/RC[0-9][A-Za-z0-9_.-]*\.json'),
]
for base in [scripts,active_workflows,submission,ROOT/"README.md"]:
    paths=[base] if base.is_file() else list(base.rglob("*"))
    for p in paths:
        if p.resolve()==Path(__file__).resolve():
            continue
        if not p.is_file() or p.suffix.lower() not in {".py",".yml",".yaml",".md",".json",".txt",".cff"}: continue
        text=p.read_text(encoding="utf-8")
        hits=sorted({m.group(0) for pat in legacy_patterns for m in pat.finditer(text)})
        if hits: legacy[str(p.relative_to(ROOT))]=hits
assert not legacy,legacy

missing_refs={}
for wf in active_workflows.glob("*.yml"):
    text=wf.read_text(encoding="utf-8")
    refs=set(re.findall(r'(scripts/[A-Za-z0-9_./-]+\.py)',text))
    refs.update(re.findall(r'(provenance/[A-Za-z0-9_./-]+\.json)',text))
    refs.update(re.findall(r'(figures_ecology_v[0-9_]+/[A-Za-z0-9_./-]+\.svg)',text))
    bad=sorted(ref for ref in refs if "/receipts/" not in ref and not (ROOT/ref).exists())
    if bad: missing_refs[wf.name]=bad
assert not missing_refs,missing_refs

bare_pat=re.compile(r'(?<![/A-Za-z0-9_.-])([A-Z][A-Z0-9_]*(?:CONTRACT|SUMMARY|RECEIPT|REPAIR)[A-Z0-9_]*\.json)')
bare={}
for base in [scripts,active_workflows]:
    for p in base.rglob("*"):
        if p.resolve()==Path(__file__).resolve():
            continue
        if not p.is_file() or p.suffix.lower() not in {".py",".yml",".yaml"}: continue
        hits=sorted(set(bare_pat.findall(p.read_text(encoding="utf-8"))))
        if hits: bare[str(p.relative_to(ROOT))]=hits
assert not bare,bare

# ---------- current scientific package ----------
m=(ROOT/"MANUSCRIPT_JAE_V1_3.md").read_text(encoding="utf-8")
si=(ROOT/"SUPPORTING_INFORMATION_JAE_RC11_V0_1.md").read_text(encoding="utf-8")
cl=(submission/"COVER_LETTER_JAE_V0_13.md").read_text(encoding="utf-8")
title_page=(ROOT/"JAE_TITLE_PAGE_V0_8.template.md").read_text(encoding="utf-8")
meta=(submission/"SUBMISSION_METADATA_TEMPLATE_V0_7.yml").read_text(encoding="utf-8")
citation=(submission/"CITATION.cff.template").read_text(encoding="utf-8")
readme=(ROOT/"README.md").read_text(encoding="utf-8")
fig2=(ROOT/"figures_ecology_v1_2/FIGURE_2_ALLOCATION_NULLS_V0_1.svg").read_text(encoding="utf-8")
fig3=(ROOT/"figures_ecology_v1_2/FIGURE_3_CROSS_DATASET_DEPTH_V0_1.svg").read_text(encoding="utf-8")

freeze=json.loads((prov/"submission/RC11_STORY_FREEZE_V0_1.json").read_text(encoding="utf-8"))
obs=json.loads((prov/"summaries/NAAMP_SAME_OBSERVER_ROBUSTNESS_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
pers=json.loads((prov/"summaries/NAAMP_PERSISTENCE_PRESERVING_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
uniform=json.loads((prov/"summaries/NAAMP_UNIFORM_ACTIVATION_NULL_SUMMARY_V0_1.json").read_text(encoding="utf-8"))

assert m.startswith("# "+TITLE)
for surface in (cl,title_page,meta,citation): assert TITLE in surface
assert freeze["status"]=="frozen_for_submission"
assert freeze["scientific_story_changed_from_rc10"] is False
assert freeze["reserved_revision_analysis"]["species_specific_activation_null"]["status"]=="not_run"
assert freeze["reserved_revision_analysis"]["species_specific_activation_null"]["authorized_pre_submission"] is False

assert obs["prefrozen_classification"]=="observer_robust"
assert obs["coverage"]["same_observer_pairs"]==3152
assert obs["coverage"]["same_observer_routes"]==500
assert obs["coverage"]["same_observer_unique_observers"]==542
assert obs["observed_matrix"]["boundary_crossing_share"] > obs["uniform_null"]["kappa_2"]["ci95"][1]
assert obs["observed_matrix"]["boundary_crossing_share"] > obs["persistence_preserving_null"]["anchor_0_75"]["ci95"][1]
for v in obs["headline_models"].values(): assert v["ci95"][0] > 0
assert pers["decision"]=="strong_rejection_under_persistence_anchoring"
assert uniform["decision"]=="strong_rejection_of_uniform_activation"

assert not re.search(r"\bRC\d+\b",m+"\n"+si)
assert "readback" not in (m+"\n"+si).lower()
for x in [
    "β = 0.384","β = 0.0794","0.2859","92.0% observed","80.9%","77.9%",
    "3,152 same-observer pairs","cross-dataset consistency","not as a replication claim",
    "a null allowing species-specific shifts","not a unique causal pathway",
]:
    assert x.lower() in m.lower(),x
for x in ["### Same-observer sensitivity","3,152 of 4,236 pairs (74.4%)","500 routes and 542 observer identifiers","80.3%","79.1%","observer robust"]:
    assert x.lower() in si.lower(),x
for x in ["Persistence null","Observed 92.0%","Anchor a=.90"]: assert x in fig2
for x in ["Cross-dataset consistency only","NAAMP","FrogID"]: assert x in fig3

forbidden=[
    "worldwide universality is demonstrated","same effect size across continents",
    "identical mechanism across continents","rainfall caused","species-specific heterogeneity is excluded",
]
for surface,name in [(m,"manuscript"),(si,"supporting_information"),(cl,"cover")]:
    for x in forbidden:
        if x.lower() in surface.lower(): raise SystemExit(f"{name} overclaim: {x}")

# ---------- JAE formatting / anonymity ----------
WORD_RE=re.compile(r"\b[\wÀ-ÖØ-öø-ÿĀ-ž’'–—+./×βρκΔ≥≤%-]+\b",re.UNICODE)
wc=lambda s:len(WORD_RE.findall(s))
am=re.search(r"## Abstract\s*(.*?)\n## Keywords",m,re.S)
km=re.search(r"## Keywords\s*(.*?)\n## Introduction",m,re.S)
rm=re.search(r"## References\s*(.*?)\n## Figure legends",m,re.S)
assert am and km and rm
abstract=am.group(1)
keywords=[x.strip() for x in km.group(1).strip().split(";") if x.strip()]
refs=[x.strip() for x in re.split(r"\n\s*\n",rm.group(1).strip()) if x.strip()]
key=lambda x:x.split(",",1)[0].casefold()

assert wc(m)+wc(title_page)<=8500
assert wc(abstract)<=350
assert len(re.findall(r"(?m)^\d+\. ",abstract))==5
assert len(keywords)<=8 and keywords==sorted(keywords,key=str.casefold)
assert refs==sorted(refs,key=key)
assert all(x in m for x in ["(Fig. 1)","(Fig. 2)","(Fig. 3)","## Data Availability"])
for x in ["10.5066/F7G44NG0","10.3897/zookeys.912.38253","10.6084/m9.figshare.4644424.v5"]: assert x in m
assert "involved no new animal capture, handling or field sampling" in m
assert wc(cl)<=500
assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",m+"\n"+si)
assert "https://github.com/" not in m+si

print(json.dumps({
    "status":"PASS",
    "root_files":len(root_files),
    "submission_files":len(submission_files),
    "workflows":len(active_names),
    "active_scripts":len(list(scripts.rglob("*.py"))),
    "provenance_files":len(prov_files),
    "manuscript_words":wc(m),
    "title_words":wc(title_page),
    "combined_proxy_words":wc(m)+wc(title_page),
    "abstract_words":wc(abstract),
    "cover_words":wc(cl),
    "references":len(refs),
    "same_observer_pairs":obs["coverage"]["same_observer_pairs"],
    "same_observer_classification":obs["prefrozen_classification"],
    "species_specific_null":"reserved_not_run",
},indent=2,sort_keys=True))
