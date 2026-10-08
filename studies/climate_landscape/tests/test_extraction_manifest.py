import importlib.util
from pathlib import Path
import pandas as pd
import pytest
sp=importlib.util.spec_from_file_location("manifest",Path(__file__).resolve().parents[1]/"scripts"/"build_extraction_manifest.py")
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)


def setup():
    e=pd.DataFrame([{"run_id":"run1","route_id":"route1","site_id":"s1","survey_date":"2010-06-15"},
                    {"run_id":"run2","route_id":"route1","site_id":"s1","survey_date":"2010-07-16"}])
    l=pd.DataFrame([{"route_id":"route1","site_id":"s1","latitude":43.0,"longitude":-89.0,
                     "coordinate_qc_status":"verified_external","verification_source_id":"actual_map_2026"}])
    return e,l


def test_months_years_are_prior_and_deduplicated():
    e,l=setup();s,m,y=mod.make(e,l)
    assert len(s)==2
    assert m.year.max()==2010 and m.query("year==2010").month.max()==6
    assert len(m)==26 # 13 unique months x two buffers
    assert set(y.year)=={2004,2009} and len(y)==4
    assert all(s.coordinate_qc_status=="verified_external")


def test_ledger_geometry_only_fails():
    e,l=setup();l.loc[0,'coordinate_qc_status']='pass_unverified'
    with pytest.raises(ValueError,match="non-verified"):mod.make(e,l)


def test_missing_station_fails():
    e,l=setup();e.loc[1,'site_id']='other'
    with pytest.raises(ValueError,match="not externally verified"):mod.make(e,l)


def test_duplicate_ledger_location_fails():
    e,l=setup();l=pd.concat([l,l],ignore_index=True)
    with pytest.raises(ValueError,match="duplicate coordinate"):mod.make(e,l)
