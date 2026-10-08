"""Independent synthetic regression checks for descriptive NLCD source audit."""
from __future__ import annotations
import hashlib,importlib.util,io,json,sys,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

CODE=Path(__file__).resolve().parents[1]/'scripts'/'audit_nlcd_geolocation_sensitivity_v18.py'
spec=importlib.util.spec_from_file_location('geoqa',CODE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ROOT=Path(__file__).resolve().parents[1]
STATIONS=ROOT/'reference_routes'/'iowa_dnr_360417_source_only_stops_v16.csv'


def make_archive(path,source_version=None,delta=False):
    v=source_version or mod.EXPECTED_VERSION
    receipt={'source_version':v,
        'status':'all_three_years_raw_C1V0_pixels_available_environment_only',
        'frog_counts_read':False,
        'original_station_table_sha256':mod.sha(STATIONS.read_bytes()),
        'study_bbox_epsg5070':list(mod.EXPECTED_BBOX),'years':{}}
    arrs={}
    for year in mod.YEARS:
        arr=np.full((409,170),41,dtype=np.uint8)
        if delta and year==2014:
            arr[:]=82
        with MemoryFile() as mem:
            with mem.open(driver='GTiff',count=1,dtype='uint8',width=170,height=409,
                          transform=from_origin(mod.EXPECTED_BBOX[0],mod.EXPECTED_BBOX[3],30,30),
                          crs='EPSG:5070') as ds:
                ds.write(arr,1)
            raw=mem.read()
        arrs[year]=raw
        receipt['years'][str(year)]={'data_sha256':mod.sha(raw),
          'catalog':{'catalog_source_name':f'Annual_NLCD_LndCov_{year}_CU_C1V0'}}
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('receipt.json',json.dumps(receipt))
        for yr,raw in arrs.items():
            z.writestr(f'arcgis_nlcd_C1V0_{yr}_iowa_360417.tif',raw)
    return arrs


def test_exact_displacement_schedule_and_numerical_norm():
    assert mod.SHIFTS_M==(0,6,15,30)
    assert mod.offsets(0)==[(0.,0.)]
    for radius in (6,15,30):
        o=mod.offsets(radius)
        assert len(o)==8
        assert all((dx*dx+dy*dy)**.5==pytest.approx(radius) for dx,dy in o)


def test_reject_wrong_raster_version_even_with_correct_pixel_categories(tmp_path):
    path=tmp_path/'a.zip'
    make_archive(path,source_version='Annual_NLCD_Collection_1.2_CU_C1V2')
    with pytest.raises(ValueError,match='Source version'):
        mod.read_archive(path)


def test_detect_modified_source_raster_byte_hash(tmp_path):
    path=tmp_path/'a.zip';make_archive(path)
    with zipfile.ZipFile(path) as z:
        raw={name:z.read(name) for name in z.namelist()}
    key=next(k for k in raw if '2014' in k)
    raw[key]=raw[key][:-4]+b'fail'
    with zipfile.ZipFile(path,'w') as z:
        for name,data in raw.items():z.writestr(name,data)
    with pytest.raises(ValueError,match='hash mismatch'):
        mod.read_archive(path)


def test_source_only_synthetic_three_year_change_and_250m_buffer(tmp_path):
    p=tmp_path/'source.zip'; make_archive(p,delta=True)
    arrs,tr,receipt=mod.read_archive(p)
    stations=mod.site_coordinates(STATIONS,receipt['original_station_table_sha256'])
    samples=mod.spatial_values(arrs,stations,tr)
    assert len(samples)==10*2*25
    assert samples['valid_2004'].eq(1).all()
    assert samples['valid_2014'].eq(1).all()
    first=samples[(samples.stop_number==10)&(samples.radius_m==250)&(samples.shift_m==0)].iloc[0]
    assert first.forest_2004_pct==pytest.approx(100)
    assert first.forest_2014_pct==pytest.approx(0)
    assert first.forest_to_agri_2004_2014==first.nominal_pixels
    assert first.net_forest_delta_2004_2014_pp==pytest.approx(-100)
    agg=mod.summarize_sensitivity(samples)
    assert len(agg)==20
    assert agg.all_negative_30m.all()


def test_station_source_is_explicitly_unverified(tmp_path):
    source=STATIONS.read_bytes();bad=tmp_path/'stations.csv'
    bad.write_bytes(source.replace(b'false',b'true'))
    with pytest.raises(ValueError,match='SHA'):
        mod.site_coordinates(bad,mod.sha(source))
    with pytest.raises(ValueError,match='not the frozen'):
        mod.site_coordinates(bad,mod.sha(bad.read_bytes()))


def test_missing_2009_fails_without_inventing_middle_year(tmp_path):
    p=tmp_path/'source.zip';make_archive(p)
    with zipfile.ZipFile(p) as z:raw={name:z.read(name) for name in z.namelist() if '2009' not in name}
    with zipfile.ZipFile(p,'w') as z:
        for name,b in raw.items():z.writestr(name,b)
    with pytest.raises(ValueError,match='Ambiguous original TIFF'):
        mod.read_archive(p)


def test_summary_never_labels_exactly_zero_as_negative():
    a=pd.DataFrame({'stop_number':[1]*25,'radius_m':[250]*25,'shift_m':[0]+[6]*8+[15]*8+[30]*8,
                    'site_id':['s']*25,'forest_2004_pct':[1.0]*25,
                    'forest_2009_pct':[1.0]*25,'forest_2014_pct':[1.0]*25,
                    'net_forest_delta_2004_2014_pp':[0.]*25,
                    'changed_2004_2014':[0]*25,'forest_loss_2004_2014':[0]*25,
                    'forest_gain_2004_2014':[0]*25,'forest_to_agri_2004_2014':[0]*25,
                    'forest_to_developed_2004_2014':[0]*25})
    y=mod.summarize_sensitivity(a).iloc[0]
    assert y.all_zero_30m and not y.all_negative_30m
