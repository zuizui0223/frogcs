#!/usr/bin/env python3
"""Build JAE identifying title-page materials LOCALLY from a verified anonymous ZIP.

Never sends personal metadata to GitHub, a cloud API, or stdout. Treat the
resulting ZIP as confidential: it is not encrypted and must never be uploaded
to the public GitHub Actions artifact store.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "submission"))
import render_submission_metadata as metadata_renderer

REQUIRED = {
    "submission_files/Manuscript.md",
    "submission_files/Manuscript.docx",
    "submission_files/Supporting_Information.md",
    "submission_files/Supporting_Information.docx",
    "submission_files/Cover_Letter.md",
    "submission_files/Reviewer_Code.zip",
    *(f"submission_files/Figure{i}.png" for i in range(1, 6)),
}
JOURNAL_TITLE = "Rainfall-associated frog chorus activation is concentrated within taxa across multiple sites"
JOURNAL = "Journal of Animal Ecology"


def outside_public_repo(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError(f"{label} must be outside the public GitHub repository")
    return resolved


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_anonymous_zip(path: Path, expected_hash: str) -> dict[str, bytes]:
    if len(expected_hash) != 64 or any(c not in "0123456789abcdef" for c in expected_hash.lower()):
        raise ValueError("an explicit 64-character source ZIP SHA256 is required")
    raw = path.read_bytes()
    if checksum(raw) != expected_hash.lower():
        raise ValueError("anonymous ZIP SHA256 does not equal the previously verified receipt")
    with ZipFile(io.BytesIO(raw)) as archive:
        members = archive.namelist()
        if len(members) != len(set(members)) or any(
            m.startswith("/") or ".." in Path(m).parts for m in members
        ):
            raise ValueError("ZIP contains ambiguous names or unsafe paths")
        if "SHA256SUMS.json" not in members:
            raise ValueError("anonymous ZIP has no SHA256SUMS.json")
        audit = json.loads(archive.read("SHA256SUMS.json"))
        if not isinstance(audit, dict) or set(audit) != set(members)-{"SHA256SUMS.json"}:
            raise ValueError("anonymous ZIP members differ from its manifest")
        files = {name: archive.read(name) for name in members if name != "SHA256SUMS.json"}
        if any(checksum(files[name]) != expected for name, expected in audit.items()):
            raise ValueError("anonymous ZIP has a corrupted internal source file")
        if not REQUIRED.issubset(files):
            raise ValueError("anonymous ZIP is missing a required JAE submission file")
        if any(len(files[f"submission_files/Figure{i}.png"]) < 30000 for i in range(1, 6)):
            raise ValueError("anonymous ZIP contains an unexpectedly small figure")
        return files


def build(anonymous_zip: Path, expected_hash: str, metadata_path: Path, output: Path) -> dict:
    outside_public_repo(metadata_path, "Private metadata")
    out = outside_public_repo(output, "Identifying output ZIP")
    if out.exists():
        raise ValueError("output ZIP exists; avoid silently overwriting a private submission")
    if not metadata_path.is_file():
        raise ValueError("private metadata YAML is missing")
    if not anonymous_zip.is_file():
        raise ValueError("anonymous scientific ZIP is missing")
    source_files = verify_anonymous_zip(anonymous_zip, expected_hash)
    obj = metadata_renderer.validate(
        metadata_renderer.load(metadata_path), strict=True, stage="initial"
    )
    if obj.get("manuscript", {}).get("title") != JOURNAL_TITLE or \
       obj["manuscript"].get("target_journal") != JOURNAL or \
       obj["manuscript"].get("article_type") != "Research Article":
        raise ValueError("private metadata journal/title/article type disagrees with frozen source")

    manuscript = source_files["submission_files/Manuscript.md"].decode("utf8")
    if manuscript.splitlines()[0].strip() != "# " + JOURNAL_TITLE:
        raise ValueError("anonymous manuscript title differs from frozen paper")
    title_text = metadata_renderer.render_title_page(obj)
    main_words = len(manuscript.split())
    title_words = len(title_text.split())
    combined = main_words + title_words
    if combined > 8500:
        raise ValueError(f"combined manuscript plus private title-page word count {combined} exceeds 8500")

    # Private intermediate data remain under a temp directory and are deleted
    # on success or error. No metadata values are written to public Actions logs.
    with tempfile.TemporaryDirectory(prefix="jae-private-local-") as tmp:
        tmproot = Path(tmp)
        title_md = tmproot / "Title_Page.md"
        title_docx = tmproot / "Title_Page.docx"
        title_md.write_text(title_text, encoding="utf8")
        render_script = ROOT / "scripts" / "submission" / "build_jae_anonymous_docx.py"
        proc = subprocess.run(
            [sys.executable, str(render_script), "--source", str(title_md),
             "--output", str(title_docx)],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if proc.returncode or not title_docx.is_file():
            raise RuntimeError("failed to generate private identifying title-page DOCX")

        additions = {
            "submission_files/Title_Page.md": title_md.read_bytes(),
            "submission_files/Title_Page.docx": title_docx.read_bytes(),
            "private/JAE_PORTAL_FIELDS.json": (
                json.dumps({
                    "title": obj["manuscript"]["title"],
                    "article_type": obj["manuscript"]["article_type"],
                    "authors": [metadata_renderer.author_name(a) for a in obj["authors"]],
                    "corresponding_author_order": obj["corresponding_author"]["author_order"],
                    "funding": obj.get("funding", []),
                    "acknowledgements": obj.get("acknowledgements", ""),
                    "conflict_of_interest": obj.get("conflict_of_interest", ""),
                    "statement_on_inclusion": obj.get("statement_on_inclusion", ""),
                    "approvals": obj.get("approvals", {}),
                    "original_anonymous_zip_sha256": expected_hash.lower(),
                }, ensure_ascii=False, indent=2) + "\n"
            ).encode("utf8"),
        }
        if set(additions) & set(source_files):
            raise ValueError("unexpected title-page collision in anonymous scientific ZIP")
        all_files = {**source_files, **additions}
        digest = {k: checksum(v) for k, v in sorted(all_files.items())}
        out.parent.mkdir(parents=True, exist_ok=True)
        old_umask = os.umask(0o077)
        try:
            with ZipFile(out, mode="x", compression=ZIP_DEFLATED, compresslevel=6) as dest:
                for name, data in sorted(all_files.items()):
                    dest.writestr(name, data)
                dest.writestr("SHA256SUMS.json",json.dumps(digest,indent=2,sort_keys=True)+"\n")
            os.chmod(out, 0o600)
        finally:
            os.umask(old_umask)
        with ZipFile(out) as zipcheck:
            if set(zipcheck.namelist()) != set(digest)|{"SHA256SUMS.json"} or \
               any(checksum(zipcheck.read(k)) != v for k,v in digest.items()):
                out.unlink(missing_ok=True)
                raise ValueError("private output ZIP failed integrity verification")
    return {"status": "PASS", "combined_word_count": combined,
            "manuscript_words": main_words,"private_title_page_words": title_words,
            "files": len(all_files), "output_zip_sha256": checksum(out.read_bytes()),
            "no_public_upload": True}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--anonymous-zip", type=Path, required=True)
    p.add_argument("--expected-zip-sha256", required=True)
    p.add_argument("--private-metadata", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = build(args.anonymous_zip,args.expected_zip_sha256,
                   args.private_metadata,args.output)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
