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
BIB = ROOT / "editorial/REFERENCES_R1_R4_P1_G6_2026-11-06.bib"
NOVELTY = ROOT / "editorial/EL_PRIMARY_LITERATURE_AND_NOVELTY_AUDIT_2026-11-09.md"
COVER = PREP / "COVER_LETTER_CD_AUTHOR_REVIEW.md"
TITLE = PREP / "TITLE_PAGE_CD_AUTHOR_REVIEW.md"
SRCFIG = ROOT / "editorial/figures"
ADMIN = [
    PREP / "COAUTHOR_REVIEW_AND_SUBMISSION_APPROVAL_REQUEST.md",
    PREP / "EL_OFFICIAL_REQUIREMENTS_AND_ARCHIVE_GATE_20261108.md",
    PREP / "NOVELTY_AND_REVIEWER_AUTHOR_CHECK.md",
    PREP / "CLAIM_EVIDENCE_REVIEWER_CHECKLIST_20261109.md",
    PREP / "DATA_CODE_DOI_ARCHIVE_PREFLIGHT_20261109.md",
]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify() -> tuple[str, str, str, int, int]:
    main = MAIN.read_text(encoding="utf-8")
    si = SI.read_text(encoding="utf-8")
    refs = REFS.read_text(encoding="utf-8")
    abs_text = main.split("## Abstract\n\n",1)[1].split("\n\n**Keywords:",1)[0]
    body = main.split("## Introduction\n",1)[1].split("## Figure legends",1)[0]
    aw, mw = len(abs_text.split()), len(body.split())
    assert 0 < aw <= 150 and 3000 <= mw <= 5000, (aw,mw)
    # All submission-section headings must describe the finding, not internal run IDs.
    assert main.count("### Frog-calling associations vary with caudates and vegetation") == 1
    assert main.count("### Salamander development reverses the demographic effect of vegetation") == 1
    assert main.count("### Rate-wide evaluation and independent structural replication") == 1
    assert "## Figure legends" in main and "## Figure captions and submission layout" not in main
    assert not re.search(r"(?m)^###\s+(?:[A-Z]\d?\.|G\d|R\d|P\d)",main)
    assert "## Evidence, reproducibility and status" not in main
    assert "author-review candidate" not in main
    assert "### B. Calls and larval records" not in main
    assert "tadpole hatching" in main and "not" in main.lower()
    assert "245 site-years; Brier gain +0.0155" in main
    assert "5.23% with calls versus 0.97% without" in main
    assert "60% to 74% at one fixed setting" in main
    assert "refuge benefits increased while odonate-support costs diminished" in main
    assert "647 canonical structures versus 712" not in main.split("## Introduction",1)[0]
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
    required_literature = [
        ("Caldwell, J. P.", "10.1007/BF00346253"),
        ("Wilbur, H. M., & Fauth", "10.1086/285038"),
        ("Klecka, J.", "10.1007/s00442-014-3007-6"),
        ("McCoy, M. W.", "10.1111/ele.12005"),
        ("Baker, R. S.", "10.1111/1365-2656.70083"),
        ("Urushihara, R.", "10.1111/fwb.70223"),
    ]
    for author, doi in required_literature:
        assert author in refs and doi in refs, (author,doi)
    ref_block = refs.split("Alford, R. A.", 1)[1].split(
        "## G7 natural-history accounts", 1)[0]
    # Count the 35 actual bibliography paragraphs, not journal footnotes.
    all_refs = "Alford, R. A." + ref_block
    entries = [p for p in all_refs.strip().split("\n\n") if p.strip()]
    assert len(entries) == 35, (len(entries), "Reference registry mismatch")
    bib_keys = re.findall(r"@\w+\{([^,]+),", BIB.read_text(encoding="utf-8"))
    assert len(bib_keys) == len(set(bib_keys)) == 35
    assert NOVELTY.is_file()
    assert (PREP / "CLAIM_EVIDENCE_REVIEWER_CHECKLIST_20261109.md").is_file()
    assert (PREP / "DATA_CODE_DOI_ARCHIVE_PREFLIGHT_20261109.md").is_file()
    assert all(s in main for s in ("Warfe & Barmuta, 2004", "McCoy et al., 2012", "Urushihara & Takatsu, 2026"))
    assert "Wilbur & Fauth, 1990" in main
    assert "Klecka & Boukal (2014)" in main
    assert "Baker et al., 2025" in main
    assert "3,890" in TITLE.read_text(encoding="utf-8")
    assert "143 words" in TITLE.read_text(encoding="utf-8")
    assert "**References:** 36" in TITLE.read_text(encoding="utf-8")
    return main, si, refs, aw, mw

def build():
    main, si, refs, aw, mw = verify()
    OUT.mkdir(parents=True, exist_ok=True)
    # The S4/S5 evidence-to-assumption table cites the full source-verified
    # registry. Retain these cited papers in the manuscript reference list;
    # the separate USGS G18 dataset citation is appended by make_main.
    review_main = make_main(
        re.sub(r"(?m)^\*\*C \(observation\) → D \(mechanism\) author-review candidate[^\n]*\n+",
               "",main),refs)
    final_reference_text = review_main.split("\n## References\n\n",1)[1]
    assert len([r for r in final_reference_text.strip().split("\n\n") if r.strip()]) == 36
    supplementary_sources = [
        "g6_observation_context_20261106/G6_field_mechanism_context_diagnostic.png",
        "g7_trait_composition_20261106/G7_trait_composition_bridge.png",
        "p1_vegetation_benefit_20261106/P1_vegetation_benefit_decomposition.png",
        "g8_27rate_paired_20261107/audited/G8_27rate_pattern_vs_population.png",
    ]
    review_links = {
        MAIN.name: "Letter_CD_MAIN_AUTHOR_REVIEW.md",
        "figures/Figure1_Observed_ThirdGuild_AcousticAssociation.png": "figures/Figure1_C_ContinentalAcousticAssociations_ORIGINAL.png",
        "figures/Figure2_InteractionSignature_VsFrogAbundance.png": "figures/Figure2_D_VegetationMechanism_ORIGINAL.png",
        "figures/Figure4_GenuineFinitePopulation_R4.png": "figures/Supplementary_Figure_S5_R4_ORIGINAL.png",
    }
    for index, source in enumerate(supplementary_sources, start=1):
        destination = OUT / "figures" / f"Supplementary_Figure_S{index}.png"
        destination.parent.mkdir(exist_ok=True)
        original = ROOT / "research/results" / source
        shutil.copyfile(original, destination)
        assert sha(original) == sha(destination)
        review_links[f"../research/results/{source}"] = f"figures/{destination.name}"
    datasets = {
        "naamp_species_sensitivity_20261109": [
            ("figS6_species.png", "figures/Supplementary_Figure_S6.png"),
            *[(name, f"tables/{name}") for name in ("interaction_results.csv", "species_support.csv", "detected_route_sensitivity.csv")],
        ],
        "public_larval_overlap_20261109": [
            (name, f"tables/{name}") for name in ("reviewed_paired_vouchers.csv", "usgs_brookshire_crosswalk.csv")
        ],
        "frog_arrival_20261109": [
            ("arrival_comparison.png", "figures/Supplementary_Figure_S8.png"),
            *[(name, f"tables/frog_arrival_{name}") for name in ("summary.csv", "paired_change_from_baseline.csv", "validation.json")],
        ],
        "naamp_shared_site_pair_20261109": [
            ("shared_sites_and_season.png", "figures/Supplementary_Figure_S7.png"),
            *[(name, f"tables/{name}") for name in ("monthly.csv", "timing.csv", "paired_coefficients.csv")],
        ],
    }
    for dataset, assets in datasets.items():
        for name, relative in assets:
            original = ROOT / "research/results" / dataset / name
            destination = OUT / relative
            destination.parent.mkdir(exist_ok=True)
            shutil.copyfile(original, destination)
            assert sha(original) == sha(destination)
            review_links[f"../research/results/{dataset}/{name}"] = relative
    for original_link, package_link in review_links.items():
        assert f"({original_link})" in si
        si = si.replace(f"({original_link})", f"({package_link})")
    prose = {
        "Letter_CD_MAIN_AUTHOR_REVIEW.md":review_main,
        "Letter_CD_SI_S1_S22_AUTHOR_REVIEW.md":si,
        "Letter_CD_COVER_AUTHOR_REVIEW.md":COVER.read_text(encoding="utf-8"),
        "TITLE_PAGE_CD_AUTHOR_REVIEW.md":TITLE.read_text(encoding="utf-8"),
    }
    for file, contents in prose.items():
        (OUT/file).write_text(contents, encoding="utf-8")
        to_docx(OUT/file, OUT/Path(file).with_suffix(".docx").name)
    for file in ADMIN:
        shutil.copyfile(file, OUT/file.name)
    shutil.copyfile(NOVELTY, OUT / "PRIMARY_LITERATURE_NOVELTY_AUDIT_20261109.md")
    shutil.copyfile(BIB, OUT / "VERIFIED_REFERENCES_20261109.bib")

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
    for figure_link in re.findall(r"\]\((figures/[^)]+\.png)\)", si):
        assert (OUT / figure_link).is_file(), figure_link
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
    files=[MAIN,SI,REFS,BIB,NOVELTY,COVER,TITLE]+ADMIN
    receipt={
        "status":"CD_MACRO_MECHANISM_AUTHOR_REVIEW_ONLY",
        "abstract_words":aw,"scientific_main_words":mw,
        "supplementary_figures":8,"main_figures":3,"SI_sections":22,
        "literature_registry_entries":35,
        "main_manuscript_references_including_USGS_builder":36,
        "research_audit_only_reference_entries":0,
        "primary_literature_audit_included":True,
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
        "bundle_sha256":{str(f.relative_to(OUT)):sha(f) for f in OUT.rglob("*") if f.is_file() and f.name not in {"CD_AUTHOR_REVIEW_SOURCE_QA.json", "ORIGINAL_44_CLAIM_QA.json"}},
    }
    (OUT/"CD_AUTHOR_REVIEW_SOURCE_QA.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CD_AUTHOR_REVIEW_PACKAGE_PASS",json.dumps({
        "main_words":mw,"abstract_words":aw,"main_figures":3,
        "SI_sections":22,"no_new_science":True,"not_submitted":True
    }))

if __name__ == "__main__":
    build()
