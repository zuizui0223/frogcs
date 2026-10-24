import unittest
import hashlib
import io
import zipfile
from ecology.dryad_takahashi.fetch_original_experiment import extract_original,validated

class DryadOriginalChecksum(unittest.TestCase):
    def test_reject_invented_lab_data(self):
        self.assertFalse(validated(b"Predation,Layers,Success\nhigh,Yes,1"))
    def test_reject_html_auth_as_data(self):
        self.assertIsNone(extract_original(b"<!DOCTYPE html><h1>Sign in</h1>"))
    def test_reject_lookalike_in_zip(self):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w") as z:z.writestr("Hatch_w.csv",b"Wrong header\n")
        self.assertIsNone(extract_original(buf.getvalue()))

if __name__=="__main__":unittest.main()
