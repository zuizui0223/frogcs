import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

src=Path(__file__).resolve().parents[1]/"scripts"/"build_climate_trend_diagnostics.py"
spec=importlib.util.spec_from_file_location("trends",src)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

@pytest.fixture
def data():
    days=pd.date_range("1981-01-01", "2015-12-31")
    years=days.year.to_numpy()
    ydiff=years-1981
    return pd.DataFrame({"route_id":"r1","site_id":"s1","date":days,
                         "coordinate_qc_status":"verified_external",
                         "tmin_c":0.0 + 0.02*ydiff,
                         "tmax_c":10.0 + 0.02*ydiff,
                         "precip_mm":2.0 + 0.0001*ydiff})

def test_descriptive_trend(data):
    r=mod.summarize(data).iloc[0]
    assert r.warming_c_decade==pytest.approx(0.2)
    assert r.n_valid_years==35
    assert r.annual_precip_change_mm_decade == pytest.approx(0.365, abs=0.06)
    assert r.trend_status=="descriptive_only"

def test_does_not_claim_trend_from_few_years(data):
    data=data[data.date.dt.year>=2000]
    r=mod.summarize(data).iloc[0]
    assert r.trend_status=="insufficient_years"
    assert np.isnan(r.warming_c_decade)

def test_rejects_unverified(data):
    data["coordinate_qc_status"]="unverified"
    with pytest.raises(ValueError,match="unverified"):
        mod.summarize(data)
