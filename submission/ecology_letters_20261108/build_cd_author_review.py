"""Prepare Ecology Letters C-macro/D-mechanism author-review documents; no new science."""
from __future__ import annotations
import hashlib, json, re, shutil, sys
from pathlib import Path

from build_editorial_bundle import make_main, to_docx

ROOT = Path(__file__).resolve().parents[2]
PREP = ROOT / "submission/ecology_letters_20261108"
OUT = PREP / "_cd_review_bundle"
MAIN = ROOT / "editorial/MAIN_TEXT_CD_ECOLOGY_LETTERS_2026-11-09.md"
SI = ROOT / "editorial/SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md"
REFS = ROOT / "editorial/REFERENCES_R1_R4_P1_G6_2026-11-06.md"
COVER = PREP / "COVER_LETTER_CD_AUTHOR_REVIEW.md"
TITLE = PREP / "TITLE_PAGE_CD_AUTHOR_REVIEW.md"
SRCFIG = ROOT / "editorial/figures"
ADMIN = [
    PREP / "COAUTHOR_REVIEW_AND_SUBMISSION_APPROVAL_REQUEST.md",
    PREP / "EL_OFFICIAL_REQUIREMENTS_AND_ARCHIVE_GATE_20261108.md",
    PREP / "NOVELTY_AND_REVIEWER_AUTHOR_CHECK.md",
]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify() -> tuple[str, str, str, int, int]:
    main = MAIN.read_text(encoding="utf-8")
    si = SI.read_text(encoding="utf-8")
    refs = REFS.read_text(encoding="utf-8")
    abs_text = main.split("## Abstract\n\n",1)[1].split("\n\n**Keywords:",1)[0]
    body = main.split("## Introduction\n",1)[1].split("## Figure captions",1)[0]
    aw, mw = len(abs_text.split()), len(body.split())
    assert 0 < aw <= 150 and 3000 <= mw <= 5000, (aw,mw)
    assert main.count("### C. The continental acoustic association") == 1
    assert main.count("### D1.") == 1 and main.count("### D4.") == 1
    assert main.count("### B. Calls and larval records") == 0
    assert "tadpole hatching" in main and "not" in main.lower()
    assert "Supplementary Methods S20 and S22" in main and "S20, S22" in main
    assert "S21" in main and "Supplementary Methods S21." in si
    for token in ["−0.166", "−0.087", "794 (3.97%)",
                  "2.705", "2.754", "124", "0.1163", "0.1864"]:
        assert token in main, token
    scientific = main.split("## Evidence, reproducibility and status",1)[0]
    assert "29/30" not in scientific and "29/59" not in scientific
    assert "φ=+0.262" not in scientific
    assert "Observed egg deposition" not in scientific
    assert all(f"Supplementary Methods S{i}." in si for i in range(1,23))
    assert "## Supplementary Methods S22. Auxiliary biological premise" in si
    assert "Garretson, A." in refs and "Zurell, D." in refs
    return main, si, refs, aw, mw

def build():
    main, si, refs, aw, mw = verify()
    OUT.mkdir(parents=True, exist_ok=True)
    review_main = make_main(
        re.sub(r"(?m)^\*\*C \(observation\) → D \(mechanism\) author-review candidate[^\n]*\n+",
               "",main),refs)
    prose = {
        "Letter_CD_MAIN_AUTHOR_REVIEW.md":review_main,
        "Letter_CD_SI_S1_S22_AUTHOR_REVIEW.md":si,
        "Letter_CD_COVER_AUTHOR_REVIEW.md":COVER.read_text(encoding="utf-8"),
        "TITLE_PAGE_CD_AUTHOR_REVIEW.md":TITLE.read_text(encoding="utf-8"),
    }
    for file, contents in prose.items():
        (OUT/file).write_text(contents, encoding="utf-8")
        to_docx(OUT/file, OUT/(file[:-3]+"docx"))
    for file in ADMIN:
        shutil.copyfile(file, OUT/file.name)

    figs=OUT/"figures"
    figs.mkdir(parents=True,exist_ok=True)
    originalC=SRCFIG/"Figure1_Observed_ThirdGuild_AcousticAssociation.png"
    originalD=SRCFIG/"Figure2_InteractionSignature_VsFrogAbundance.png"
    originalR4=SRCFIG/"Figure4_GenuineFinitePopulation_R4.png"
    shutil.copyfile(originalC,figs/"Figure1_C_ContinentalAcousticAssociations_ORIGINAL.png")
    shutil.copyfile(originalD,figs/"Figure2_D_VegetationMechanism_ORIGINAL.png")
    shutil.copyfile(originalR4,figs/"Supplementary_Figure_S5_R4_ORIGINAL.png")

    # Figure 3 is a publication layout of previously audited G8/G11/P1 values.
    sys.path.insert(0,str(ROOT/"research/scripts"))
    from build_bcd_editorial_figures_20261108 import figure3
    figure3(figs)
    assert len(list(figs.glob("Figure*.png")))==3
    assert sha(originalC)==sha(figs/"Figure1_C_ContinentalAcousticAssociations_ORIGINAL.png")
    assert sha(originalD)==sha(figs/"Figure2_D_VegetationMechanism_ORIGINAL.png")
    assert sha(originalR4)==sha(figs/"Supplementary_Figure_S5_R4_ORIGINAL.png")

    (OUT/"README_NOT_SUBMITTED.txt").write_text(
        "C = continental adult frog calling associations (not tadpole birth).\n"
        "D = hypothetical food-web mechanisms and within-model population effects.\n"
        "Independent INBO and USGS call/larva associations are SI-only premises "
        "(S20, S22); temporal transfer is not robust.\n"
        "Calling is NOT hatching, counted new tadpoles, recruitment or larval survival. "
        "No observed same-year trophic causality claimed.\n"
        "Mohonk 29/30 and 29/59 and INBO phi=0.262 not original-source verified. "
        "R4 and R5 remain in SI.\n"
        "Awaiting all coauthors' explicit approval, permissions and actual project DOI. "
        "Never treated as journal submission.\n",
        encoding="utf-8")
    files=[MAIN,SI,REFS,COVER,TITLE]+ADMIN
    receipt={
        "status":"CD_MACRO_MECHANISM_AUTHOR_REVIEW_ONLY",
        "abstract_words":aw,"scientific_main_words":mw,
        "main_figures":3,"SI_sections":22,
        "original_main_figure_1_and_2_bytes_unchanged":True,
        "original_R4_supplementary_figure_bytes_unchanged":True,
        "stage_B_sources_in_SI_only":True,
        "tadpole_birth_directly_observed_from_calls":False,
        "inbo_phi_0262_source_verified":False,
        "mohonk_29_30_29_59_source_verified":False,
        "mechanism_identified_in_field":False,
        "original_scientific_simulations_rerun":0,
        "coauthor_approval":False,"project_archive_doi_verified":False,
        "journal_submitted":False,
        "source_sha256":{str(f.relative_to(ROOT)):sha(f) for f in files},
        "bundle_sha256":{str(f.relative_to(OUT)):sha(f) for f in OUT.rglob("*") if f.is_file()},
    }
    (OUT/"CD_AUTHOR_REVIEW_SOURCE_QA.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CD_AUTHOR_REVIEW_PACKAGE_PASS",json.dumps({
        "main_words":mw,"abstract_words":aw,"main_figures":3,
        "SI_sections":22,"no_new_science":True,"not_submitted":True
    }))

if __name__ == "__main__":
    build()
