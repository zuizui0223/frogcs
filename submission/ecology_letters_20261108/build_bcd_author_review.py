"""B/C/D Ecology Letters author-review docx + 3 reviewed figure candidates.
No biological model fit, parameter search or new data analysis.
"""
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
from build_editorial_bundle import make_main,to_docx

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"submission/ecology_letters_20261108/_bcd_review_bundle"
SRC=ROOT/"editorial"
MAIN=SRC/"MAIN_TEXT_BCD_ECOLOGY_LETTERS_2026-11-08.md"
SI=SRC/"SUPPLEMENTARY_METHODS_AND_EVIDENCE_R1_R4_2026-11-05.md"
REFS=SRC/"REFERENCES_R1_R4_P1_G6_2026-11-06.md"
COVER=ROOT/"submission/ecology_letters_20261108/COVER_LETTER_BCD_AUTHOR_REVIEW.md"
TITLE=ROOT/"submission/ecology_letters_20261108/TITLE_PAGE_BCD_AUTHOR_REVIEW.md"
PREP=ROOT/"submission/ecology_letters_20261108"
ADMIN=[
    PREP/"COAUTHOR_REVIEW_AND_SUBMISSION_APPROVAL_REQUEST.md",
    PREP/"EL_OFFICIAL_REQUIREMENTS_AND_ARCHIVE_GATE_20261108.md",
    PREP/"NOVELTY_AND_REVIEWER_AUTHOR_CHECK.md",
]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def extract_counts(main):
    words=main.split("## Abstract\n\n",1)[1].split("\n\n**Keywords:",1)[0].split()
    body=main.split("## Introduction\n",1)[1].split("## Figure captions",1)[0]
    return len(words),len(body.split())

def check():
    main=MAIN.read_text();si=SI.read_text();r=REFS.read_text()
    aw,mw=extract_counts(main)
    assert aw<=150 and 3000<=mw<=5000,("Word count",aw,mw)
    # All three evidence functions must be present and non-causal
    assert main.count("### B. Calls and larval records")==1
    assert main.count("### C. The continental acoustic association")==1
    assert main.count("### D1.")==1 and main.count("### D4.")==1
    assert main.count("### R4.")==0 and "R4" in si
    assert "Supplementary Methods S21." in si and "Supplementary Methods S22." in si
    for token in ["245", "93", "5.38-fold", "−0.166", "−0.087","794 (3.97%)",
                  "2.705", "2.754", "124", "0.1163", "0.1864"]:
        assert token in main,token
    science_body=main.split("## Evidence, reproducibility and status",1)[0]
    assert "29/30" not in science_body and "29/59" not in science_body and "φ=+0.262" not in science_body
    assert "not" in main.lower() and "field" in main.lower()
    assert "Garretson, A." in r and "Zurell, D." in r
    assert all(f"Supplementary Methods S{i}." in si for i in range(1,23))
    return main,si,r,aw,mw

def build():
    main,si,refs,aw,mw=check()
    OUT.mkdir(parents=True,exist_ok=True)
    scientific=re.sub(r"(?m)^\*\*B→C→D Letter editorial review candidate[^\n]*\n+","",main)
    review=make_main(scientific,refs)
    (OUT/"Letter_BCD_MAIN_AUTHOR_REVIEW.md").write_text(review,encoding="utf-8")
    (OUT/"Letter_BCD_SI_S1_S22_AUTHOR_REVIEW.md").write_text(si,encoding="utf-8")
    (OUT/"Letter_BCD_Cover_AUTHOR_REVIEW.md").write_text(COVER.read_text(),encoding="utf-8")
    (OUT/"TITLE_PAGE_BCD_AUTHOR_REVIEW.md").write_text(TITLE.read_text(),encoding="utf-8")
    for file in ADMIN:
        shutil.copyfile(file,OUT/file.name)
    for base in ["Letter_BCD_MAIN_AUTHOR_REVIEW","Letter_BCD_SI_S1_S22_AUTHOR_REVIEW",
                 "Letter_BCD_Cover_AUTHOR_REVIEW","TITLE_PAGE_BCD_AUTHOR_REVIEW"]:
        to_docx(OUT/(base+".md"),OUT/(base+".docx"))
    figdir=OUT/"figures"
    subprocess.run([sys.executable,str(ROOT/"research/scripts/build_bcd_editorial_figures_20261108.py"),
                    "--out",str(figdir)],cwd=ROOT,check=True)
    assert (figdir/"Figure1_BC_StageAndContinentalContext_EDITORIAL.png").stat().st_size>100000
    assert (figdir/"Figure3_D_RateAndDevelopment_EDITORIAL.png").stat().st_size>100000
    assert len(list(figdir.glob("Figure*.png")))==3
    (OUT/"README_AUTHOR_REVIEW_NOT_SUBMITTED.txt").write_text(
        "R5 frozen research + B/C/D scientific narrative. B=independent biological premises; "
        "C=continental acoustic association; D=controlled stage-structured model.\n"
        "Main 3 FIGURES are EDITORIAL CANDIDATES requiring author layout/accessibility approval; "
        "R4 original Figure4 moves to SI S5. No new analysis was performed for these displays.\n"
        "Mohonk 29/30 and 29/59 counts and INBO phi=+0.262 have NOT been source verified; "
        "not included as manuscript numbers. INBO future-year prediction failure retained.\n"
        "MANUSCRIPT NOT SUBMITTED. Coauthor order/contact/approval, archive DOI and rights pending.\n",
        encoding="utf-8"
    )
    source=[MAIN,SI,REFS,COVER,TITLE,*ADMIN]
    receipt={
        "status":"BCD_AUTHOR_REVIEW_COMPLETE_NOT_SUBMITTED",
        "article_type":"Ecology Letters Letter",
        "abstract_words":aw,"main_body_words":mw,
        "main_figure_candidates":3,
        "supplementary_sections":22,
        "original_44_science_claims_rerun":False,
        "original_science_retained_from":"R1–R5/G1–G18/P1 previously audited source",
        "new_biological_simulations":0,
        "mohonk_29_30_source_verified":False,
        "mohonk_29_59_source_verified":False,
        "inbo_phi_0262_source_verified":False,
        "coauthor_approval":False,
        "archive_doi_verified":False,
        "journal_submitted":False,
        "source_sha256":{str(p.relative_to(ROOT)):sha(p) for p in source},
        "deliverables_sha256":{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob("*") if p.is_file()},
    }
    (OUT/"BCD_SOURCE_AND_MANUSCRIPT_QA.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("BCD_AUTHOR_REVIEW_PACKAGE_SUCCESS",json.dumps({
        "main_body_words":mw,"abstract_words":aw,"SI":22,"main_figures":3,
        "simulation_recomputed":0,"journal_submitted":False
    }),flush=True)

if __name__=="__main__":build()
