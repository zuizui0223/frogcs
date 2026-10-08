import importlib.util
from pathlib import Path

import pandas as pd
import pytest

src = Path(__file__).resolve().parents[1]/"scripts"/"build_climate_features.py"
spec = importlib.util.spec_from_file_location("build_climate_features",src)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

@pytest.fixture
def inputs():
    dates = pd.date_range("1981-01-01", "2005-12-31", freq="D")
    daily = pd.DataFrame({"route_id":"route1", "site_id":"site1", "date":dates,
                          "tmin_c":10.0, "tmax_c":20.0, "precip_mm":2.0})
    surveys = pd.DataFrame({"run_id":["run1"],"route_id":["route1"],"site_id":["site1"],
                            "survey_date":["2003-06-15"],"coordinate_qc_status":["verified_external"]})
    return surveys,daily

def test_reference_and_daily_metrics(inputs):
    surveys,daily=inputs
    result=mod.build_features(surveys,daily).iloc[0]
    assert result["climate_shift_5y_tmean_c"] == pytest.approx(0)
    assert result["climate_shift_5y_precip_ratio"] == pytest.approx(1,abs=0.006)
    assert result["tmean_anomaly_7d_c"] == pytest.approx(0)
    assert result["precip_anomaly_30d_mm"] == pytest.approx(0)
    assert result["precip_sum_90d_mm"] == pytest.approx(180)
    assert result["days_lt1mm_rain_30d"] == 0

def test_future_weather_not_used(inputs):
    surveys,daily=inputs
    a=mod.build_features(surveys,daily)
    daily.loc[daily.date>=pd.Timestamp("2003-06-15"), "precip_mm"] = 100
    daily.loc[daily.date>=pd.Timestamp("2003-06-15"), "tmin_c"] = 40
    daily.loc[daily.date>=pd.Timestamp("2003-06-15"), "tmax_c"] = 50
    b=mod.build_features(surveys,daily)
    pd.testing.assert_frame_equal(a,b)

def test_unverified_coordinates_fail_closed(inputs):
    surveys,daily=inputs
    surveys.loc[0,"coordinate_qc_status"]="unverified"
    with pytest.raises(ValueError, match="verified"):
        mod.build_features(surveys,daily)

def test_missing_daily_prior_fails_closed(inputs):
    surveys,daily=inputs
    daily=daily[daily.date!=pd.Timestamp("2003-06-12")]
    with pytest.raises(ValueError, match="missing prior"):
        mod.build_features(surveys,daily)

def test_duplicate_meteorology_rejected(inputs):
    surveys,daily=inputs
    daily=pd.concat([daily,daily.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        mod.build_features(surveys,daily)

def test_climatology_rejects_insufficient_baseline(inputs):
    surveys,daily=inputs
    daily=daily[daily.date.dt.year>=1999]
    with pytest.raises(ValueError, match="insufficient"):
        mod.build_features(surveys,daily)
