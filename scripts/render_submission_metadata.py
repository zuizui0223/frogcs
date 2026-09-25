#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

PLACEHOLDER = re.compile(r"\[[A-Z][^\]]*\]")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
ORCID_RE = re.compile(r"^(?:https://orcid\.org/)?\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")

KEYWORDS = [
    "acoustic community",
    "anurans",
    "ecoacoustics",
    "environmental cue",
    "rainfall",
    "temporal niche",
    "synchrony",
    "weather",
]

DESCRIPTION = (
    "Reproducibility package for a Journal of Animal Ecology Research Article testing whether "
    "recent rainfall is associated with greater short-window multispecies frog co-calling across "
    "independent North American and Australian acoustic monitoring systems. The archive contains "
    "the anonymized scientific manuscript, frozen analysis contracts, result receipts, deterministic "
    "figure-generation code and analysis scripts. Raw third-party datasets are not redistributed."
)

def load(path: Path) -> dict:
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise SystemExit("metadata root must be a mapping")
    return obj

def placeholder_paths(value, prefix=""):
    out=[]
    if isinstance(value, dict):
        for k,v in value.items():
            out.extend(placeholder_paths(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(value, list):
        for i,v in enumerate(value):
            out.extend(placeholder_paths(v, f"{prefix}[{i}]"))
    elif isinstance(value, str) and PLACEHOLDER.search(value):
        out.append(prefix)
    return out

def require(condition: bool, message: str):
    if not condition:
        raise SystemExit(message)

def author_name(a: dict) -> str:
    return a.get("display_name") or f"{a['given_names']} {a['family_names']}".strip()

def affiliation_text(aid: str, affiliations: dict) -> str:
    a=affiliations[aid]
    bits=[a.get("department",""), a.get("institution",""), a.get("city",""), a.get("country","")]
    return ", ".join(x for x in bits if x)

def validate(m: dict, strict: bool) -> dict:
    authors=m.get("authors") or []
    require(authors, "at least one author is required")
    orders=[a.get("order") for a in authors]
    require(orders == list(range(1,len(authors)+1)), f"author order must be contiguous from 1: {orders}")

    affiliations=m.get("affiliations") or {}
    require(affiliations, "at least one affiliation is required")
    for a in authors:
        require(a.get("given_names"), f"author {a.get('order')} given_names missing")
        require(a.get("family_names"), f"author {a.get('order')} family_names missing")
        require(a.get("affiliation_ids"), f"author {a.get('order')} affiliation_ids missing")
        for aid in a["affiliation_ids"]:
            require(aid in affiliations, f"unknown affiliation id {aid!r}")
        orcid=(a.get("orcid") or "").strip()
        if orcid:
            require(bool(ORCID_RE.fullmatch(orcid)), f"invalid ORCID for author {a.get('order')}: {orcid}")

    ca=m.get("corresponding_author") or {}
    require(ca.get("author_order") in orders, "corresponding_author.author_order must identify an author")

    repo=m.get("repository") or {}
    doi=(repo.get("archive_doi") or "").strip()
    if doi:
        doi=re.sub(r"^https?://doi\.org/","",doi,flags=re.I)
        require(bool(DOI_RE.fullmatch(doi)), f"invalid archive DOI: {doi}")
        repo["archive_doi"]=doi

    approvals=m.get("approvals") or {}
    if strict:
        placeholders=placeholder_paths(m)
        require(not placeholders, "unresolved placeholders: " + ", ".join(placeholders))
        require(bool(ca.get("email")), "corresponding author email required")
        require("@" in ca.get("email",""), "corresponding author email is invalid")
        require(bool(ca.get("postal_address")), "corresponding author postal address required")
        require(bool(repo.get("license")), "repository license required")
        require(bool(repo.get("archive_doi")), "archive DOI required")
        require(bool(m.get("statement_on_inclusion")), "statement_on_inclusion required for JAE submission")
        for k in ("all_authors_approve_submission","all_entitled_authors_included","not_under_consideration_elsewhere"):
            require(approvals.get(k) is True, f"approval must be true: {k}")

    return m

def render_title_page(m: dict) -> str:
    authors=m["authors"]; aff=m["affiliations"]; ca=m["corresponding_author"]
    author_line=", ".join(author_name(a) for a in authors)
    aff_lines=[]
    for aid in sorted(aff):
        aff_lines.append(f"**{aid}:** {affiliation_text(aid, aff)}")
    corr=next(a for a in authors if a["order"]==ca["author_order"])

    funding=m.get("funding") or []
    funding_lines=[]
    for f in funding:
        if f.get("funder")=="None":
            funding_lines.append("None.")
        else:
            grant=f.get("grant_number") or ""
            funding_lines.append(f"- {f.get('funder')}" + (f" — {grant}" if grant else ""))

    credits=[]
    for a in authors:
        roles=", ".join(a.get("credit_roles") or [])
        credits.append(f"- **{author_name(a)}:** {roles}")

    return "\n".join([
        "# Journal of Animal Ecology title page",
        "",
        f"**Manuscript title:** {m['manuscript']['title']}",
        "",
        f"**Authors:** {author_line}",
        "",
        "**Affiliations:**",
        *aff_lines,
        "",
        f"**Corresponding author:** {author_name(corr)}; {ca.get('postal_address','')}; {ca.get('email','')}",
        "",
        "## Acknowledgements",
        "",
        str(m.get("acknowledgements","")),
        "",
        "## Funding",
        "",
        *funding_lines,
        "",
        "## Conflict of Interest",
        "",
        str(m.get("conflict_of_interest","")),
        "",
        "## Author Contributions",
        "",
        *credits,
        "",
        "## Statement on Inclusion",
        "",
        str(m.get("statement_on_inclusion","")),
        "",
        "## Approval",
        "",
        f"- all authors approve the submitted version: {m['approvals'].get('all_authors_approve_submission')}",
        f"- all entitled authors are included: {m['approvals'].get('all_entitled_authors_included')}",
        f"- manuscript is not under consideration elsewhere: {m['approvals'].get('not_under_consideration_elsewhere')}",
        "",
    ])

def render_zenodo(m: dict) -> dict:
    creators=[]
    for a in m["authors"]:
        aff="; ".join(affiliation_text(x,m["affiliations"]) for x in a["affiliation_ids"])
        c={"name": f"{a['family_names']}, {a['given_names']}", "affiliation": aff}
        if a.get("orcid"):
            c["orcid"]=a["orcid"].replace("https://orcid.org/","")
        creators.append(c)
    repo=m["repository"]
    return {
        "title": m["manuscript"]["title"],
        "upload_type": "software",
        "description": DESCRIPTION,
        "creators": creators,
        "keywords": KEYWORDS,
        "license": repo.get("license",""),
        "related_identifiers": [
            {"identifier": repo["url"], "relation": "isSupplementTo", "scheme": "url"},
            *[
                {"identifier": x["doi"], "relation": "references", "scheme": "doi"}
                for x in m.get("source_data",[])
            ],
        ],
        "notes": "Raw third-party source datasets are not redistributed in this archive.",
    }

def render_cff(m: dict) -> dict:
    authors=[]
    for a in m["authors"]:
        x={"family-names": a["family_names"], "given-names": a["given_names"]}
        if a.get("orcid"):
            val=a["orcid"]
            x["orcid"]=val if val.startswith("http") else "https://orcid.org/"+val
        authors.append(x)
    repo=m["repository"]
    return {
        "cff-version": "1.2.0",
        "message": "If you use this reproducibility package, please cite the associated article and archived release.",
        "title": m["manuscript"]["title"],
        "type": "software",
        "authors": authors,
        "repository-code": repo["url"],
        "doi": repo.get("archive_doi",""),
        "license": repo.get("license",""),
        "keywords": KEYWORDS,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--metadata", required=True)
    p.add_argument("--outdir", default="build/submission-metadata")
    p.add_argument("--strict", action="store_true")
    args=p.parse_args()

    m=validate(load(Path(args.metadata)), args.strict)
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)

    (out/"JAE_TITLE_PAGE_FINAL.md").write_text(render_title_page(m),encoding="utf-8")
    (out/"ZENODO_METADATA_FINAL.json").write_text(json.dumps(render_zenodo(m),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"CITATION.cff").write_text(yaml.safe_dump(render_cff(m),sort_keys=False,allow_unicode=True),encoding="utf-8")

    portal = {
        "article_type": m["manuscript"]["article_type"],
        "title": m["manuscript"]["title"],
        "authors": [author_name(a) for a in m["authors"]],
        "corresponding_author_order": m["corresponding_author"]["author_order"],
        "conflict_of_interest": m.get("conflict_of_interest",""),
        "statement_on_inclusion": m.get("statement_on_inclusion",""),
        "data_archive_doi": m["repository"].get("archive_doi",""),
        "repository_license": m["repository"].get("license",""),
        "all_authors_approve_submission": m["approvals"].get("all_authors_approve_submission"),
        "all_entitled_authors_included": m["approvals"].get("all_entitled_authors_included"),
        "not_under_consideration_elsewhere": m["approvals"].get("not_under_consideration_elsewhere"),
        "ethics_and_permits": m.get("ethics_and_permits",{}),
    }
    (out/"JAE_PORTAL_FIELDS.json").write_text(json.dumps(portal,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    validation={
        "strict": args.strict,
        "authors": len(m["authors"]),
        "affiliations": len(m["affiliations"]),
        "archive_doi_present": bool(m["repository"].get("archive_doi")),
        "placeholders_remaining": placeholder_paths(m),
        "approvals": m.get("approvals",{}),
        "status": "PASS",
    }
    (out/"SUBMISSION_METADATA_VALIDATION.json").write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")
    print(validation)

if __name__=="__main__":
    main()
