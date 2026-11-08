#!/usr/bin/env python3
"""Build author-review copies from pinned scientific manuscripts. NO scientific analyses."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT / "submission" / "ecology_letters_20261108"
OUT = SUB / "_review_bundle"
ED = ROOT / "editorial"
MAIN = ED / "MAIN_TEXT_R1_R4_SUBMISSION_CANDIDATE_2026-11-05.md"
SUPP = ED / "SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md"
REFS = ED / "REFERENCES_R1_R4_P1_G6_2026-11-06.md"
COVER = SUB / "COVER_LETTER_AUTHOR_REVIEW.md"
FIGS = [
    "Figure1_Observed_ThirdGuild_AcousticAssociation.png",
    "Figure2_InteractionSignature_VsFrogAbundance.png",
    "Figure3_Arrival_Duration_P1_PureMechanism.png",
    "Figure4_GenuineFinitePopulation_R4.png",
]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_source() -> tuple[str, str, str]:
    main = MAIN.read_text(encoding="utf-8")
    supp = SUPP.read_text(encoding="utf-8")
    refs = REFS.read_text(encoding="utf-8")
    required = {
        "g13_structure_main": "647 canonical IDs" in main and "p=0.0002" in main,
        "g18_independent_observation_main": "In independent USGS surveys" in main,
        "g12_prior_in_supp": "Supplementary Methods S14." in supp,
        "g13_structure_in_supp": "Supplementary Methods S15." in supp,
        "g14_g17_limits_in_supp": all(f"Supplementary Methods S{i}." in supp for i in range(16, 20)),
        "g18_stage_in_supp": "Supplementary Methods S20." in supp,
        "g17_failure_preserved": "G17's original replay gate failed" in main,
        "rate_mismatch_positive": "+2.71" in main and "−0.040" in main,
        "developmental_benefit_positive": "+0.116" in main,
    }
    if not all(required.values()):
        raise RuntimeError("Frozen result markers failed: " + json.dumps(required))
    return main, supp, refs

def make_main(main: str, refs: str) -> str:
    # Remove author-side statuses/source-audit appendix, never change results.
    main = re.sub(r"(?m)^\*\*Submission main-text candidate[^\n]*\n+", "", main)
    main = main.split("## Evidence, reproducibility and status", 1)[0].rstrip()
    main = main.replace("## Figure captions and submission layout", "## Figure legends")
    entries = refs.split("Alford, R. A.", 1)[1].split("## G7 natural-history accounts", 1)[0]
    entries = "Alford, R. A." + entries
    entries = re.sub(
        r"(Takahashi, M\. K\., & Parris, M\. J\. \(2008\)\.[^\n]*?\]\(https://doi\.org/10\.1007/s00442-008-1125-8\)\.)[^\n]*",
        r"\1", entries,
    )
    entries = entries.strip()
    usgs = (
        "Glorioso, B. M., & Waddle, H. (2025). *Data from time-constrained visual "
        "encounter surveys and acoustic surveys for amphibians and reptiles in "
        "the Atchafalaya Basin conducted from 2008 through 2016*. "
        "U.S. Geological Survey data release. https://doi.org/10.5066/P9T71JCO."
    )
    # A required DOI is still missing: keep a conspicuous stop marker in the author review copy.
    access = (
        "## Data and code availability — ACTION REQUIRED BEFORE SUBMISSION\n\n"
        "The primary NAAMP data release is DOI:10.5066/F7G44NG0; the independent "
        "USGS G18 source is DOI:10.5066/P9T71JCO. Project-specific derived "
        "data, code, model outputs and metadata require a permanent, accessible "
        "archive. **[INSERT VERIFIED STUDY ARCHIVAL DOI AND RIGHTS-CLEARED "
        "FILE MANIFEST BEFORE JOURNAL UPLOAD]**. A public GitHub branch and "
        "original USGS source DOIs alone do not satisfy the project archive requirement.\n"
    )
    return main + "\n\n" + access + "\n## References\n\n" + entries + "\n\n" + usgs + "\n"

def make_supplement(supp: str) -> str:
    """Preserve all scientific SI S1–S20; omit only author-side status notes."""
    supp = re.sub(r"(?m)^\*\*Source-preserving integrated draft[^\n]*\n+", "", supp)
    supp = re.sub(r"(?m)^\*\*Remaining author decisions:\*\*[^\n]*\n?", "", supp)
    return supp

def to_docx(md: Path, dest: Path) -> None:
    subprocess.run(
        ["pandoc", str(md), "--from=markdown", "--to=docx",
         "--standalone", "--output", str(dest)],
        cwd=ROOT, check=True,
    )
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    doc = Document(dest)
    base = doc.styles["Normal"]
    base.font.name = "Times New Roman"
    base.font.size = Pt(12)
    base.paragraph_format.line_spacing = 2.0
    base.paragraph_format.space_after = Pt(4)
    for style_name in ["Body Text", "List Paragraph", "Caption"]:
        if style_name in doc.styles:
            doc.styles[style_name].font.name = "Times New Roman"
            doc.styles[style_name].font.size = Pt(12)
            doc.styles[style_name].paragraph_format.line_spacing = 2.0
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing = 2.0
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing = 2.0
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        foot = section.footer.paragraphs[0]
        foot.alignment = 2
        foot.add_run("Page ")
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), "PAGE")
        foot._p.append(field)
    doc.save(dest)

def main() -> None:
    main_src, supp_src, refs = check_source()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "Letter_MAIN_AUTHOR_REVIEW.md").write_text(make_main(main_src, refs), encoding="utf-8")
    (OUT / "Letter_SI_AUTHOR_REVIEW.md").write_text(make_supplement(supp_src), encoding="utf-8")
    (OUT / "Cover_Letter_AUTHOR_REVIEW.md").write_text(
        COVER.read_text(encoding="utf-8"), encoding="utf-8")
    for stem in ["Letter_MAIN", "Letter_SI", "Cover_Letter"]:
        src = OUT / (stem + "_AUTHOR_REVIEW.md")
        to_docx(src, OUT / (stem + "_AUTHOR_REVIEW.docx"))
    for fig in FIGS:
        shutil.copyfile(ED / "figures" / fig, OUT / fig)
    (OUT / "READ_ME_FIRST_NOT_SUBMITTED.txt").write_text(
        "Ecology Letters submission preparation / frozen 2026-11-08.\n"
        "AUTHOR REVIEW COPY, NOT JOURNAL-SUBMITTED OR ARCHIVAL DOI-COMPLETE.\n"
        "No scientific model or original numerical output was rerun here.\n"
        "Do not upload until: all coauthors approve; title page/corresponding author and "
        "reviewer data are verified; project data/code archive DOI is entered; "
        "third-party rights/licensing cleared; all figure sizes and captions approved.\n"
        "See ../SCIENCE_FREEZE_AND_HANDOFF.md in the GitHub branch.\n",
        encoding="utf-8",
    )
    sources = [MAIN, SUPP, REFS, COVER] + [ED / "figures" / f for f in FIGS]
    manifest = {
        "journal": "Ecology Letters",
        "article_type": "Letter",
        "source_base_commit": "e6f6b941ff75e008658bdff0910868eb03e44673",
        "current_build_commit": os.getenv("GITHUB_SHA", "not-set"),
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in sources},
        "bundle_sha256": {p.name: sha256(p) for p in sorted(OUT.iterdir()) if p.is_file()},
        "scientific_simulations_executed": 0,
        "journal_submitted": False,
        "author_approval_complete": False,
        "project_archive_doi_verified": False,
        "status": "AUTHOR_REVIEW_ONLY",
    }
    (OUT / "freeze_bundle_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("EDITORIAL_PACKAGE_BUILT", len(manifest["bundle_sha256"]), "review-only files")
    print("MAIN_SOURCE_CHARS", len(main_src), "SI_SOURCE_CHARS", len(supp_src))
    print("NO_NEW_SCIENTIFIC_ANALYSES")

if __name__ == "__main__":
    main()
