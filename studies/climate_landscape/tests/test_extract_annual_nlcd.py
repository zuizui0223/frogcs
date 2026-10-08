import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer
sp=importlib.util.spec_from_file_location("nlcd",Path(__file__).resolve().parents[1]/"scripts"/"extract_annual_nlcd.py")
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)


def geotiff(tmp_path,year,forest=True,fill=41):
    cx,cy=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform(-100,40)
    trans=from_origin(cx-1500,cy+1500,30,30)
    data=np.full((100,100),fill,dtype=np.uint8)
    data[46:54,46:54]=11
    if not forest:
        data[20:80,20:80]=22
    p=tmp_path/f"annual_{year}.tif"
    with rasterio.open(p,"w",driver="GTiff",height=100,width=100,count=1,dtype="uint8",crs="EPSG:5070",transform=trans,nodata=0) as ds:ds.write(data,1)
    return p


def test_actual_raster_pixels_projected_by_site(tmp_path):
    p=geotiff(tmp_path,2010)
    with rasterio.open(p) as src:
        s=mod.extract_one(src,-100,40,250)
        assert s['forest_area_m2']>0 and s['openwater_area_m2']>0
        assert s['nodata_area_m2']==0
        assert s['raster_pixel_area_m2']==pytest.approx(900)
        assert s['sampled_pixels']>0


def test_nodata_is_not_forest_or_water(tmp_path):
    p=geotiff(tmp_path,2010)
    with rasterio.open(p,'r+') as ds:
        a=ds.read(1);a[45:55,45:55]=0;ds.write(a,1)
    with rasterio.open(p) as ds:s=mod.extract_one(ds,-100,40,250)
    assert s['nodata_area_m2']>0
    assert s['openwater_area_m2']==0


def test_missing_raster_year_hard_fails(tmp_path):
    p=geotiff(tmp_path,2010)
    req=pd.DataFrame([dict(route_id="r1",site_id="s1",longitude=-100,latitude=40,buffer_m=250,year=2011)])
    idx=pd.DataFrame([dict(year=2010,raster_path=str(p),source_version="ANNUAL_NLCD_C1_2",source_image_id="test")])
    with pytest.raises(ValueError,match="year missing"):mod.extract(req,idx)


def test_wrong_dataset_version_fails(tmp_path):
    p=geotiff(tmp_path,2010)
    req=pd.DataFrame([dict(route_id="r1",site_id="s1",longitude=-100,latitude=40,buffer_m=250,year=2010)])
    idx=pd.DataFrame([dict(year=2010,raster_path=str(p),source_version="epoch_NLCD",source_image_id="test")])
    with pytest.raises(ValueError,match="unsupported"):mod.extract(req,idx)
