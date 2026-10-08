import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sp=importlib.util.spec_from_file_location("rs",Path(__file__).resolve().parents[1]/"scripts"/"build_remote_sensing_features.py")
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)


def data():
    e=pd.DataFrame([{"run_id":"run1","route_id":"r1","site_id":"s1","survey_date":"2011-07-18", "coordinate_qc_status":"verified_external"}])
    m=[]; land=[]
    for b in (250,1000):
        for mo in pd.period_range("2010-07", "2011-07",freq="M"):
            m.append({"route_id":"r1","site_id":"s1","buffer_m":b,"year":mo.year,"month":mo.month,
                      "water_area_m2":20, "nonwater_area_m2":80,"nodata_area_m2":0,
                      "source_image_id":f"JRC/GSW1_4/MonthlyHistory/{mo.year:04d}_{mo.month:02d}","source_version":"JRC_GSW1_4"})
        for year in (2005,2010,2011):
            land.append({"route_id":"r1","site_id":"s1","buffer_m":b,"year":year,
                          "forest_area_m2":400 if year==2005 else 300,"agriculture_area_m2":100,"developed_area_m2":100 if year==2005 else 200,"wetland_area_m2":100,"openwater_area_m2":100,
                          "other_area_m2":200,"nodata_area_m2":0,"source_image_id":f"USGS/{year}","source_version":"ANNUAL_NLCD_C1_2"})
    return e,pd.DataFrame(m),pd.DataFrame(land)


def test_uses_last_completed_month_and_previous_annual():
    e,m,l=data();x=mod.build(e,m,l).iloc[0]
    assert x.last_eligible_water_month=='2011-06'
    assert x.landcover_antecedent_year==2010
    assert x.b250_water_frac_last_completed_month==pytest.approx(0.2)
    assert x.b250_water_persistence_12m_frac==pytest.approx(0.2)
    assert x.b250_forest_frac_prior_year==pytest.approx(0.3)
    assert x.b250_forest_change_prior5y_frac==pytest.approx(-0.1)
    assert '2010' in x.b250_nlcd_last_source_image_id


def test_images_dated_after_survey_do_not_leak():
    e,m,l=data();x=mod.build(e,m,l)
    m.loc[m.year.eq(2011)&m.month.eq(7),'water_area_m2']=100
    l.loc[l.year.eq(2011),'forest_area_m2']=1000
    y=mod.build(e,m,l)
    pd.testing.assert_frame_equal(x,y)


def test_no_data_is_missing_not_dry():
    e,m,l=data()
    m.loc[m.year.eq(2011)&m.month.eq(6),['water_area_m2','nonwater_area_m2','nodata_area_m2']]=[0,0,100]
    x=mod.build(e,m,l).iloc[0]
    assert np.isnan(x.b250_water_frac_last_completed_month)
    assert x.b250_water_months_observed_12m==11
    assert x.b250_water_persistence_12m_frac==pytest.approx(0.2)
    assert x.jrc_nodata_is_dry==False


def test_insufficient_observed_months_is_missing():
    e,m,l=data()
    q=m.month.isin([8,9,10,11,12,1,2,3,4,5])
    m.loc[q,['water_area_m2','nonwater_area_m2','nodata_area_m2']]=[0,0,100]
    x=mod.build(e,m,l).iloc[0]
    assert np.isnan(x.b250_water_persistence_12m_frac)


def test_unverified_sites_refused():
    e,m,l=data();e.loc[0,'coordinate_qc_status']='pass_unverified'
    with pytest.raises(ValueError,match='unverified'):mod.build(e,m,l)


def test_duplicate_month_refused():
    e,m,l=data();m=pd.concat([m,m.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match='duplicate'):mod.build(e,m,l)


def test_wrong_product_version_refused():
    e,m,l=data();l['source_version']='NLCD_2011'
    with pytest.raises(ValueError,match='Collection 1.2'):mod.build(e,m,l)


def test_missing_annual_not_assumed_unchanged():
    e,m,l=data();l=l[l.year!=2010]
    x=mod.build(e,m,l).iloc[0]
    assert np.isnan(x.b250_forest_frac_prior_year)
    assert np.isnan(x.b250_forest_change_prior5y_frac)


def test_source_image_month_mismatch_rejected():
    e,m,l=data();m.loc[0,"source_image_id"]="JRC/GSW1_4/MonthlyHistory/2020_01"
    with pytest.raises(ValueError,match="source_image_id"):
        mod.build(e,m,l)
