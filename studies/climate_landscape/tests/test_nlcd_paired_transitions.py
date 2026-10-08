import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer

S=Path(__file__).resolve().parents[1]/'scripts'/'extract_nlcd_paired_transitions.py'
spec=importlib.util.spec_from_file_location('nlcd_paired_transitions',S)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def fixture(tmp_path):
    x,y=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True).transform(-100,40)
    grid=from_origin(x-1500,y+1500,30,30)
    prev=np.full((100,100),41,dtype='uint8')
    cur=np.full((100,100),41,dtype='uint8')
    prev[:,50:]=22
    cur[:,:50]=22
    def save(name,array,transform=grid):
        path=tmp_path/name
        with rasterio.open(path,'w',driver='GTiff',width=100,height=100,count=1,dtype='uint8',nodata=0,
                            crs='EPSG:5070',transform=transform) as ds:
            ds.write(array,1)
        return str(path)
    one=save('2001.tif',prev);two=save('2010.tif',cur)
    requests=pd.DataFrame([{'run_id':'run1','route_id':'A','site_id':'X','latitude':40,'longitude':-100,
        'buffer_m':250,'year_earlier':2001,'year_later':2010,
        'survey_date':'2011-06-11','coordinate_qc_status':'verified_external',
        'verification_source_id':'SYNTHETIC_STATION'}])
    index=pd.DataFrame([{'year':2001,'raster_path':one,'source_image_id':'NLCD2001',
                         'source_version':'ANNUAL_NLCD_C1_2'},
                        {'year':2010,'raster_path':two,'source_image_id':'NLCD2010',
                         'source_version':'ANNUAL_NLCD_C1_2'}])
    return requests,index,prev,cur,save


def test_reciprocal_forest_development_conversions_are_not_net_change(tmp_path):
    requests,index,prev,cur,save=fixture(tmp_path)
    out=m.extract(requests,index).iloc[0]
    assert out.pixel_pair_status=='eligible'
    assert out.paired_valid_fraction==pytest.approx(1)
    assert out.forest_loss_fraction>0.4
    assert out.forest_gain_fraction>0.4
    assert out.forest_balance_error==pytest.approx(0)
    assert out.baseline_forest_fraction==pytest.approx(out.later_forest_fraction,abs=.07)
    assert out.developed_gain_fraction>0.4
    assert out.confidence_product_screened == False


def test_nodata_not_imputed_as_stable_or_water(tmp_path):
    requests,index,prev,cur,save=fixture(tmp_path)
    cur[:,:70]=0
    index.loc[index.year==2010,'raster_path']=save('2010_nodata.tif',cur)
    r=m.extract(requests,index).iloc[0]
    assert r.pixel_pair_status=='insufficient_paired_valid_area'
    assert r.paired_valid_fraction<0.80
    assert np.isnan(r.forest_loss_fraction)


def test_grid_mismatch_is_hard_error(tmp_path):
    requests,index,prev,cur,save=fixture(tmp_path)
    x,y=Transformer.from_crs('EPSG:4326','EPSG:5070',always_xy=True).transform(-100,40)
    index.loc[index.year==2010,'raster_path']=save('2010_shifted.tif',cur,from_origin(x-1470,y+1500,30,30))
    with pytest.raises(ValueError,match='exactly the same grid'):
        m.extract(requests,index)


def test_future_survey_year_imagery_is_disallowed(tmp_path):
    requests,index,*_=fixture(tmp_path)
    requests.loc[0,'survey_date']='2010-06-11'
    with pytest.raises(ValueError,match='strictly precede'):
        m.extract(requests,index)


def test_coordinate_status_must_be_independently_verified(tmp_path):
    requests,index,*_=fixture(tmp_path)
    requests.loc[0,'coordinate_qc_status']='pass_unverified'
    with pytest.raises(ValueError,match='independently verified'):
        m.extract(requests,index)


def test_prevent_response_leakage(tmp_path):
    requests,index,*_=fixture(tmp_path)
    requests['CallingIndex']=3
    with pytest.raises(ValueError,match='Acoustic outcomes not allowed'):
        m.extract(requests,index)


def test_official_version_required(tmp_path):
    requests,index,*_=fixture(tmp_path)
    index.loc[:,'source_version']='NLCD2016_EPOCH'
    with pytest.raises(ValueError,match='Official Annual NLCD Collection 1.2 only'):
        m.extract(requests,index)


def test_classification_errors_not_silently_as_nodata(tmp_path):
    requests,index,prev,cur,save=fixture(tmp_path)
    cur[:,:60]=254
    index.loc[index.year==2010,'raster_path']=save('2010_badcodes.tif',cur)
    with pytest.raises(ValueError,match='Unexpected Annual NLCD classes'):
        m.extract(requests,index)


def test_conservative_buffer_1000_is_supported(tmp_path):
    requests,index,*_=fixture(tmp_path)
    requests.loc[0,'buffer_m']=1000
    r=m.extract(requests,index).iloc[0]
    assert r.total_buffer_pixels>3000
    assert r.pixel_pair_status=='eligible'


def test_missing_index_year_hard_error(tmp_path):
    requests,index,*_=fixture(tmp_path)
    with pytest.raises(ValueError,match='missing years'):
        m.extract(requests,index.iloc[:1])
