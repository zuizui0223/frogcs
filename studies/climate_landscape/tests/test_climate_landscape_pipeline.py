"""Synthetic-only climate × JRC × official NLCD pixel processing contract tests.

Run from the repository root with:
  pytest -q studies/climate_landscape/tests
No real frog responses are read by these tests.
"""
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
    p=ROOT/"scripts"/(name+".py")
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


coordinate=load("audit_coordinates")
manifest=load("build_extraction_manifest")
raster=load("extract_annual_nlcd")
satellite=load("build_remote_sensing_features")
climate=load("build_climate_features")
trends=load("build_climate_trend_diagnostics")


def synthetic_events():
    ev=pd.DataFrame([dict(run_id="run1",route_id="r1",
                           site_id="s1",survey_date="2011-07-18")])
    ledger=pd.DataFrame([dict(route_id="r1",site_id="s1",
                              latitude=40.0,longitude=-100.0,
                              coordinate_qc_status="verified_external",
                              verification_source_id="SYNTHETIC_ONLY")])
    return ev,ledger


def test_geometry_never_auto_verifies():
    raw=pd.DataFrame([["r1","s1",40,-100],["r1","s2",40.01,-100.01],
                      ["r1","s3",40.02,100]],
                     columns=["RouteNumber","SiteID","lat","lon"])
    a,r=coordinate.audit(raw)
    assert r["coordinates_independently_verified"]==0
    assert a.query("site_id=='s3'").iloc[0].geometry_qc_status=="failed_domain"
    assert (a.coordinate_qc_status=="UNVERIFIED_DO_NOT_EXTRACT").all()


def test_manifest_uses_completed_images_only():
    ev,ledger=synthetic_events()
    resolved,months,years=manifest.make(ev,ledger)
    assert len(resolved)==1
    assert months.year.max()==2011
    assert months.query("year==2011").month.max()==6
    assert set(years.year)=={2005,2010}
    ledger.coordinate_qc_status="pass_unverified"
    with pytest.raises(ValueError,match="non-verified"):
        manifest.make(ev,ledger)


def test_full_synthetic_pipeline(tmp_path):
    ev,ledger=synthetic_events()
    verified,months,years=manifest.make(ev,ledger)
    cx,cy=Transformer.from_crs("EPSG:4326","EPSG:5070",
                               always_xy=True).transform(-100,40)
    indexed=[]
    for year in years.year.unique():
        color=41 if year==2010 else 22
        band=np.full((100,100),color,dtype=np.uint8)
        tif=tmp_path/f"{year}.tif"
        with rasterio.open(tif,"w",driver="GTiff",
                           width=100,height=100,count=1,dtype="uint8",
                           crs="EPSG:5070",
                           transform=from_origin(cx-1500,cy+1500,30,30),
                           nodata=0) as ds:
            ds.write(band,1)
        indexed.append(dict(year=year,raster_path=str(tif),
                            source_image_id=f"SYNTH_NLCD_{year}",
                            source_version="ANNUAL_NLCD_C1_2"))
    land=raster.extract(years,pd.DataFrame(indexed))
    water=months.copy()
    water["water_area_m2"]=2000
    water["nonwater_area_m2"]=8000
    water["nodata_area_m2"]=0
    water["source_image_id"]=water.apply(lambda r:f"JRC/GSW1_4/MonthlyHistory/{int(r.year):04d}_{int(r.month):02d}",axis=1)
    water["source_version"]="JRC_GSW1_4"
    sat=satellite.build(verified,water,land)
    assert sat.iloc[0].b250_forest_change_prior5y_frac==pytest.approx(1)
    assert sat.iloc[0].b250_water_frac_last_completed_month==pytest.approx(.2)
    daily=pd.DataFrame({"route_id":"r1","site_id":"s1",
                        "date":pd.date_range("1981-01-01","2011-07-19")})
    daily["tmin_c"]=10
    daily["tmax_c"]=20
    daily["precip_mm"]=2
    d=climate.build_features(verified,daily)
    merged=sat.merge(d,on=["run_id","route_id","site_id","survey_date",
                           "coordinate_qc_status"],validate="one_to_one")
    assert len(merged)==1
    assert merged.iloc[0].climate_shift_5y_tmean_c==pytest.approx(0)
    assert merged.iloc[0].survey_day_weather_used==False
    assert merged.iloc[0].current_survey_year_landcover_used==False


def test_missing_month_is_not_dry():
    ev,ledger=synthetic_events()
    verified,months,years=manifest.make(ev,ledger)
    water=months.copy()
    water["water_area_m2"]=2
    water["nonwater_area_m2"]=8
    water["nodata_area_m2"]=0
    water["source_image_id"]=water.apply(lambda r:f"JRC/GSW1_4/MonthlyHistory/{int(r.year):04d}_{int(r.month):02d}",axis=1)
    water["source_version"]="JRC_GSW1_4"
    water.loc[(water.year==2011)&(water.month==6),
              ["water_area_m2","nonwater_area_m2","nodata_area_m2"]]=[0,0,10]
    land=years.copy()
    for key in ("forest","agriculture","developed","wetland","openwater","other","nodata"):
        land[key+"_area_m2"]=10
    land["source_image_id"]="SYNTH_NLCD"
    land["source_version"]="ANNUAL_NLCD_C1_2"
    x=satellite.build(verified,water,land).iloc[0]
    assert np.isnan(x.b250_water_frac_last_completed_month)
    assert x.b250_water_months_observed_12m==11


def test_future_weather_cannot_enter_short_windows():
    ev,ledger=synthetic_events()
    verified,_,_=manifest.make(ev,ledger)
    daily=pd.DataFrame({"route_id":"r1","site_id":"s1",
                        "date":pd.date_range("1981-01-01","2011-07-19")})
    daily["tmin_c"]=10
    daily["tmax_c"]=20
    daily["precip_mm"]=2
    a=climate.build_features(verified,daily)
    daily.loc[daily.date>=pd.Timestamp("2011-07-18"),"precip_mm"]=999
    b=climate.build_features(verified,daily)
    pd.testing.assert_frame_equal(a,b)
