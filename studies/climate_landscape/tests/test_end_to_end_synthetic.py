"""Synthetic image-pixel extraction -> exposure join; never a NAAMP outcome result."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]

def load(name):
    sp=importlib.util.spec_from_file_location(name,ROOT/"scripts"/(name+".py"))
    mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod

manifest=load('build_extraction_manifest')
annual=load('extract_annual_nlcd')
exposure=load('build_remote_sensing_features')
climate=load('build_climate_features')


def test_30m_landcover_plus_monthly_water_plus_prior_climate(tmp_path):
    e=pd.DataFrame([dict(run_id='example1',route_id='synthetic',site_id='p1',survey_date='2011-07-18')])
    l=pd.DataFrame([dict(route_id='synthetic',site_id='p1',latitude=40,longitude=-100,
                         coordinate_qc_status='verified_external',verification_source_id='synthetic_fixture_not_real')])
    verified,months,years=manifest.make(e,l)
    assert len(months)==24 and len(years)==4
    cx,cy=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True).transform(-100,40)
    rows=[]
    for y in years.year.unique():
        data=np.full((100,100),41 if y==2010 else 22,dtype=np.uint8)
        path=tmp_path/f'{y}.tif'
        with rasterio.open(path,'w',driver='GTiff',width=100,height=100,count=1,
                  crs='EPSG:5070',transform=from_origin(cx-1500,cy+1500,30,30),
                  dtype='uint8',nodata=0) as tif:tif.write(data,1)
        rows.append(dict(year=y,raster_path=str(path),source_image_id=f'SYNTH_NLCD_{y}',source_version='ANNUAL_NLCD_C1_2'))
    from_raster=annual.extract(years,pd.DataFrame(rows))
    mock_jrc=months.copy()
    mock_jrc['water_area_m2']=2000
    mock_jrc['nonwater_area_m2']=8000
    mock_jrc['nodata_area_m2']=0
    mock_jrc['source_image_id']=mock_jrc.apply(
        lambda r:f"JRC/GSW1_4/MonthlyHistory/{int(r.year):04d}_{int(r.month):02d}",axis=1)
    mock_jrc['source_version']='JRC_GSW1_4'
    rs=exposure.build(verified,mock_jrc,from_raster)
    assert len(rs)==1 and rs.iloc[0].b250_forest_change_prior5y_frac==pytest.approx(1)
    assert rs.iloc[0].b250_water_frac_last_completed_month==pytest.approx(.2)
    daily=pd.DataFrame(dict(route_id='synthetic',site_id='p1',date=pd.date_range('1981-01-01','2011-07-19')))
    daily['tmin_c']=10;daily['tmax_c']=20;daily['precip_mm']=2
    cl=climate.build_features(verified,daily)
    both=rs.merge(cl,on=['run_id','route_id','site_id','survey_date','coordinate_qc_status'],validate='one_to_one')
    assert len(both)==1
    assert both.iloc[0].climate_shift_5y_tmean_c==pytest.approx(0)
    assert both.iloc[0].survey_day_weather_used==False
    assert both.iloc[0].current_survey_year_landcover_used==False
