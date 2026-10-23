import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'scripts'/'probe_public_nlcd_stac.py'
sp=importlib.util.spec_from_file_location('nlcd_stac_probe',p)
s=importlib.util.module_from_spec(sp)
sp.loader.exec_module(s)
class TestNLCDStac(unittest.TestCase):
    def test_historical_not_final_version(self):
        self.assertIn('C1V1',s.ITEM)
        self.assertNotIn('C1V2',s.ITEM)
    def test_refuse_full_raster_response(self):
        from email.message import Message
        class R:
            status=200
            headers=Message()
            def __enter__(self): return self
            def __exit__(self,*exc): pass
            def read(self,*args): raise AssertionError('unexpected raster download')
        with patch.object(s.urllib.request,'urlopen',return_value=R()):
            r=s.small_range('https://invalid.example/thing.tif')
        self.assertEqual(r['bytes_read'],0)
        self.assertEqual(r['status'],200)
if __name__=='__main__': unittest.main()
