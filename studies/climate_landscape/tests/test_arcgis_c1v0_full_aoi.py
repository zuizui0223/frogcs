import importlib.util
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('aoi',ROOT/'arcgis_c1v0_full_aoi.py')
aoi=importlib.util.module_from_spec(spec);spec.loader.exec_module(aoi)

def stations():
    return pd.DataFrame([{'route_id':'360417','site_id':f'{7271+i}','stop_number':i+1,
             'latitude':41.486301-i*.0099,'longitude':-93.790497-i*.002,
             'historical_site_verified':False} for i in range(10)])

def test_year_id_must_be_versioned(monkeypatch):
    monkeypatch.setattr(aoi,'source_request',lambda p,q,limit=4_000_000: (b'{"features":[{"attributes":{"Year":2004,"OBJECTID":1,"Name":"Annual_NLCD_LndCov_2004_CU_C1V2","Version":"1.2"}}]}','application/json'))
    with pytest.raises(ValueError,match='Collection 1.0'):
        aoi.source_identity_for_year(2004)

def test_reject_unexpected_class_values(tmp_path):
    import rasterio
    shape=(aoi.HEIGHT,aoi.WIDTH)
    p=tmp_path/'bad.tif'
    with rasterio.open(p,'w',driver='GTiff',width=shape[1],height=shape[0],
              count=1,dtype='uint8',crs='EPSG:5070',
              transform=from_origin(aoi.BBOX[0],aoi.BBOX[3],30,30)) as dst:
        dst.write(np.full(shape,33,dtype='uint8'),1)
    with pytest.raises(ValueError,match='Unexpected raw thematic codes'):
        aoi.inspect(p)

def test_same_pixel_transition_and_balance():
    sites=stations()
    # One synthetic location near AOI center so both radii fit. Repeat for 10 stops.
    from rasterio.warp import transform
    from pyproj import Transformer
    x=(aoi.BBOX[0]+aoi.BBOX[2])/2;y=(aoi.BBOX[1]+aoi.BBOX[3])/2
    lon,lat=Transformer.from_crs('EPSG:5070','EPSG:4326',always_xy=True).transform(x,y)
    sites['latitude']=lat;sites['longitude']=lon
    im=np.full((aoi.HEIGHT,aoi.WIDTH),41,dtype='uint8')
    new=im.copy();new[100:140,60:80]=21
    valid=np.ones_like(im,dtype=bool)
    result=aoi.summarize_layers({2004:(im,valid),2014:(new,valid)},sites)
    assert len(result)==20
    assert all(z['pairs']['2004_2014']['forest_mass_balance_verified'] for z in result)
    assert result[0]['pairs']['2004_2014']['passes_80pct']

def test_buffer_coverage_is_fail_closed():
    s=stations()
    s['latitude']=41.486301;s['longitude']=-93.790497
    s.loc[0,'latitude']=0
    im=np.full((aoi.HEIGHT,aoi.WIDTH),41,dtype='uint8')
    with pytest.raises(ValueError,match='buffer truncated'):
        aoi.summarize_layers({2004:(im,im==41),2014:(im,im==41)},s)
