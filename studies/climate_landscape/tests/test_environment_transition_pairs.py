import importlib.util
from pathlib import Path
import pandas as pd
import numpy as np
import pytest
s=importlib.util.spec_from_file_location('env',Path(__file__).resolve().parents[1]/'scripts'/'build_environment_transition_pairs.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def data():
    meta=pd.DataFrame([dict(run_id=f'run{i}',route_id='VA:0701',site_id='one',
                            survey_date=dt,survey_round=2)
                       for i,dt in [(1,'2010-05-10'),(2,'2011-05-13'),(3,'2013-05-11')]])
    climate=meta.drop(columns=['survey_round']).copy()
    climate['tmean_anomaly_30d_c']=[0,2,3]
    climate['climate_shift_5y_tmean_c']=[0.4,0.7,0.9]
    climate['climate_shift_5y_precip_ratio']=[1.0,.9,.8]
    remote=meta.drop(columns=['survey_round']).copy()
    remote['coordinate_qc_status']='verified_external'
    remote['b250_water_detected_fraction_observed_12m']=[.7,.4,.2]
    remote['b250_water_detection_lower_bound_12m']=[.6,.3,.1]
    remote['b250_water_detection_upper_bound_12m']=[.8,.5,.3]
    remote['b250_forest_frac_prior_year']=[.9,.7,.5]
    remote['b250_developed_frac_prior_year']=[.05,.1,.2]
    remote['b250_water_months_observed_12m']=[10,11,12]
    return meta,climate,remote

def test_only_consecutive_comparable_year_pairs():
    a,b,c=data(); pairs,r=m.make(a,b,c)
    assert len(pairs)==1
    assert r['excluded_due_to_nonconsecutive_year']==1
    assert pairs.iloc[0].delta_b250_forest_frac_prior_year==pytest.approx(-.2)
    assert pairs.iloc[0].delta_tmean_anomaly_30d_c==pytest.approx(2)
    assert pairs.iloc[0].water_contrast_eligible

def test_different_seasons_excluded():
    a,b,c=data()
    for frame in (a,b,c):frame.loc[1,'survey_date']='2011-07-15'
    out,r=m.make(a,b,c)
    assert len(out)==0 and r['excluded_due_to_season_day_shift_over_21']==1

def test_no_pseudo_dry_for_missing_satellite_months():
    a,b,c=data()
    c.loc[1,'b250_water_detected_fraction_observed_12m']=np.nan
    c.loc[1,'b250_water_months_observed_12m']=5
    out,r=m.make(a,b,c)
    assert len(out)==1
    assert np.isnan(out.iloc[0].delta_b250_water_detected_fraction_observed_12m)
    assert not out.iloc[0].water_contrast_eligible

def test_missing_exposure_rows_fail_not_silently_inner_joined():
    a,b,c=data()
    with pytest.raises(ValueError,match='missing'):
        m.make(a,b.iloc[:-1],c)

def test_no_coords_no_inference():
    a,b,c=data()
    c['coordinate_qc_status']='pass_unverified'
    with pytest.raises(ValueError,match='unverified'):
        m.make(a,b,c)
