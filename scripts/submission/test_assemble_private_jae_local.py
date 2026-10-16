#!/usr/bin/env python3
"""Synthetic-only local JAE author-page safety; no real author metadata."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"/"submission"))
import assemble_private_jae_local as app


def payload():
    files={}
    for name in sorted(app.REQUIRED):
        if name=="submission_files/Manuscript.md":
            b=("# "+app.JOURNAL_TITLE+"\n\nNo personal details are present.\n").encode()
        elif name.endswith(".png"):
            b=b"\x89PNG\r\n\x1a\n"+b"x"*31000
        else:
            b=b"TEST_INPUT_PLACEHOLDER"
        files[name]=b
    return files


def make_zip(p,files):
    sums={name:hashlib.sha256(value).hexdigest() for name,value in sorted(files.items())}
    with ZipFile(p,"w",compression=ZIP_DEFLATED) as z:
        for name,data in files.items():
            z.writestr(name,data)
        z.writestr("SHA256SUMS.json",json.dumps(sums))
    return hashlib.sha256(p.read_bytes()).hexdigest()


class LocalSubmissionSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="jae-qa-outside-repo-")
        self.addCleanup(self.temp.cleanup)
        self.d=Path(self.temp.name)
        self.archive=self.d/"anon.zip"
        self.filedata=payload()
        self.sha=make_zip(self.archive,self.filedata)
        self.meta=self.d/"synthetic_metadata.yml"
        shutil.copyfile(ROOT/"submission"/"test_metadata.fixture.yml",self.meta)

    def test_fixture_can_be_packaged_without_public_upload(self):
        out=self.d/"identifying-private.zip"
        receipt=app.build(self.archive,self.sha,self.meta,out)
        self.assertTrue(out.is_file())
        self.assertEqual(receipt["status"],"PASS")
        self.assertTrue(receipt["no_public_upload"])
        self.assertLessEqual(receipt["combined_word_count"],8500)
        self.assertEqual(stat.S_IMODE(out.stat().st_mode),0o600)
        with ZipFile(out) as z:
            self.assertIn("submission_files/Title_Page.docx",z.namelist())
            self.assertIn("submission_files/Title_Page.md",z.namelist())
            self.assertIn("private/JAE_PORTAL_FIELDS.json",z.namelist())
            self.assertEqual(z.read("submission_files/Manuscript.md"),
                             self.filedata["submission_files/Manuscript.md"])
            portal=json.loads(z.read("private/JAE_PORTAL_FIELDS.json"))
            self.assertEqual(portal["authors"],["Test Author"])
            self.assertIn("Test Author",z.read("submission_files/Title_Page.md").decode())

    def test_bad_zip_digest_is_blocked(self):
        with self.assertRaisesRegex(ValueError,"SHA256"):
            app.build(self.archive,"0"*64,self.meta,self.d/"no.zip")

    def test_tampered_inner_manifest_is_blocked(self):
        altered=dict(self.filedata)
        altered["submission_files/Manuscript.docx"]=b"DIFFERENT"
        # Tamper the content but keep the manifest of original files.
        with ZipFile(self.archive,"w") as z:
            for key,b in altered.items():
                z.writestr(key,b)
            z.writestr("SHA256SUMS.json",json.dumps({
                key:hashlib.sha256(b).hexdigest() for key,b in self.filedata.items()}))
        new_sha=hashlib.sha256(self.archive.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError,"corrupted internal"):
            app.build(self.archive,new_sha,self.meta,self.d/"no.zip")

    def test_real_data_paths_inside_public_repo_are_forbidden(self):
        with self.assertRaisesRegex(ValueError,"outside the public"):
            app.outside_public_repo(ROOT/"submission"/"metadata.template.yml","Private metadata")
        with self.assertRaisesRegex(ValueError,"outside the public"):
            app.outside_public_repo(ROOT/"build"/"private.zip","Identifying ZIP")

    def test_metadata_must_have_actual_approvals(self):
        text=self.meta.read_text().replace("all_authors_approve_submission: true",
                                           "all_authors_approve_submission: false")
        self.meta.write_text(text)
        with self.assertRaises(SystemExit):
            app.build(self.archive,self.sha,self.meta,self.d/"no.zip")

    def test_no_silent_private_zip_overwrite(self):
        output=self.d/"already.zip"
        output.write_bytes(b"existing")
        with self.assertRaisesRegex(ValueError,"exists"):
            app.build(self.archive,self.sha,self.meta,output)
        self.assertEqual(output.read_bytes(),b"existing")

    def test_product_metadata_mismatch_fail_closed(self):
        s=self.meta.read_text().replace("Journal of Animal Ecology",
                                        "Unknown Journal",1)
        self.meta.write_text(s)
        with self.assertRaisesRegex(ValueError,"journal/title"):
            app.build(self.archive,self.sha,self.meta,self.d/"no.zip")


if __name__=="__main__":
    unittest.main()
