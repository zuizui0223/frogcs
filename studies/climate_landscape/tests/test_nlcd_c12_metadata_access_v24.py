import importlib.util,sys,json
from pathlib import Path
import pytest
f=Path(__file__).resolve().parents[1]/'scripts'/'audit_official_nlcd_c12_metadata_access_v24.py'
spec=importlib.util.spec_from_file_location('catalog',f)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

def test_known_assets_are_only_references_not_verified_pixels():
    assert set(a.GEE_ID)=={'land_cover','confidence'}
    assert all(p.startswith('projects/sat-io/') for p in a.GEE_ID.values())
def test_untrusted_host_redirect_is_fixed_to_original():
    assert a.HOSTS['mrlc']=={'www.mrlc.gov','mrlc.gov'}
    assert a.LIMIT<=2_500_000

def test_parse_synthetic_current_official_data_list():
    text=b'<html><title>Data</title>Annual NLCD Collection 1 Version 2 (1.2) 2012 <a href="/download/foo">Download</a></html>'
    r=a.extract('mrlc',text)
    assert r['mentions_C1V2']
    assert r['year_2012_mentioned']
    assert r['public_links'][0]['label']=='Download'
def test_sciencebase_has_children_without_embedded_listing_is_not_an_inventory():
    r=a.extract('usgs_archive',json.dumps({
         'id':'655ceb8ad34ee4b6e05cc51a','title':'Annual NLCD',
         'hasChildren':True,'files':[]}).encode())
    assert r['hasChildren'] is True
    assert r['available_inline_files']==[]
def test_catalog_missing_version_is_not_validated():
    r=a.extract('mrlc',b'<html><title>Unknown</title>2025 2012</html>')
    assert not r['mentions_C1V2']
