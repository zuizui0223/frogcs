"""G18 response-blind source-eligibility unit checks; no outcome data."""
import unittest,io,zipfile,csv
from g18_usgs_atchafalaya_original_source_preflight import (
    ITEM,DOI,MAX_FILE,parse_sbjson,original_file_manifest,member_headers
)
import json

class TestG18USGSPreflight(unittest.TestCase):
    def test_source_identity_without_substitute(self):
        self.assertEqual(DOI,"10.5066/P9T71JCO")
        self.assertEqual(ITEM,"5eb5880c82ce25b5135ae784")
        self.assertGreater(MAX_FILE,10_000)
        self.assertIsNone(parse_sbjson(json.dumps({"id":"WRONG"}).encode()))
        self.assertIsNotNone(parse_sbjson(json.dumps({"id":ITEM,"files":[]}).encode()))
        self.assertIsNone(parse_sbjson(b"<html>access denied</html>"))

    def test_original_file_manifest_does_not_open_response(self):
        info={"id":ITEM,"files":[
            {"name":"sites.csv","size":39,"contentType":"text/csv","downloadUri":"https://example.org/a"},
            {"name":"readme.pdf","size":150,"contentType":"application/pdf"}
        ]}
        o=original_file_manifest(info)
        self.assertEqual(len(o),2)
        self.assertTrue(o[0]["qualifying_file"])
        self.assertFalse(o[1]["qualifying_file"])

    def test_zip_header_only(self):
        bio=io.BytesIO()
        with zipfile.ZipFile(bio,"w") as z:
            z.writestr("survey.csv","sample_id,site_id,species,count\n1,A,Frog,99\n")
        r=member_headers("survey.zip",bio.getvalue())
        self.assertEqual(len(r),1)
        self.assertEqual(r[0]["header"],["sample_id","site_id","species","count"])
        self.assertNotIn("99",str(r))

if __name__=="__main__":
    unittest.main()
