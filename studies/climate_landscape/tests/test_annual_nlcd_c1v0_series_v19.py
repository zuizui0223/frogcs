import importlib.util
from pathlib import Path
import numpy as np,pandas as pd,pytest
from rasterio.warp import transform as project
ROOT=Path(__file__).resolve().parents[1]/'scripts'
spec=importlib.util.spec_from_file_location('annseries',ROOT/'annual_nlcd_c1v0_series_360417_v19.py')
series=importlib.util.module_from_spec(spec);spec.loader.exec_module(series)


def test_years_fixed_to_observational_calendar():
    assert series.YEARS==tuple(range(2001,2016))
    with pytest.raises(ValueError,match='outside prespecified'):
        series.request_verified_year(2020)


def test_missing_years_fail_closed():
    with pytest.raises(ValueError,match='incomplete|Incomplete'):
        series.prepare_series({2004:b'fake'})


def sites_at_center():
    midx=sum((series.source.BBOX[0],series.source.BBOX[2]))/2
    midy=sum((series.source.BBOX[1],series.source.BBOX[3]))/2
    from pyproj import Transformer
    lon,lat=Transformer.from_crs('EPSG:5070','EPSG:4326',always_xy=True).transform(midx,midy)
    return pd.DataFrame([{'route_id':'360417','stop_number':i+1,'site_id':str(7271+i),
         'latitude':lat,'longitude':lon,'historical_site_verified':False} for i in range(10)])


def test_yearly_outputs_are_300_and_280_without_frog_responses():
    data={y:np.full((series.source.HEIGHT,series.source.WIDTH),41,dtype=np.uint8) for y in series.YEARS}
    # Ecological group conversion deliberately introduced in 2009, and
    # held after 2009; does not imply physical habitat change.
    for y in series.YEARS:
        if y>=2009:
            data[y][200,80]=82
    annual,between=series.summarize_annual(data,sites_at_center())
    assert len(annual)==300
    assert len(between)==280
    s=between[(between.site_id=='7271')&(between.radius_m==250)&(between.to_year==2009)].iloc[0]
    assert s.forest_to_agriculture_pixels==1
    assert s.persisted_group_change_1yr_pixels==1
    assert not s.persisted_group_change_not_observed_for_last_year
    last=between[(between.site_id=='7271')&(between.to_year==2015)].iloc[0]
    assert pd.isna(last.persisted_group_change_1yr_pixels)


def test_post_2015_map_is_never_field_verification():
    p=sites_at_center()
    p.loc[0,'historical_site_verified']=True
    with pytest.raises(ValueError,match='cannot verify'):
        series.fixed_site_masks(p)
