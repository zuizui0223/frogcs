import importlib.util,sys
from pathlib import Path
import numpy as np,pandas as pd,pytest
src=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(src))
spec=importlib.util.spec_from_file_location("seven",src/"screen_seven_iowa_nlcd_c1v0_v22.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sites():
    return pd.DataFrame([{"route_id":"360104","site_id":str(i),
        "stop_number":i,"latitude":42.0+i/5000,
        "longitude":-93.5-i/5000} for i in range(1,11)])
def test_forest_transition_persistence():
    pts=sites();box,w,h=m.shared_grid(pts);shape=h,w
    a=np.full(shape,41,dtype=np.uint8);b=np.full(shape,82,dtype=np.uint8)
    valid=np.ones(shape,dtype=bool)
    out=m.analyze(pts,{2011:(a,valid),2012:(b,valid),2013:(b,valid)},box)
    assert len(out)==20
    for row in out:
        assert row["passes_80pct"]
        c=row["2011_to_2012_transition"]
        assert c["forest_loss_pixels"]==row["n_nominal_pixels"]
        assert c["forest_to_agriculture_pixels"]==row["n_nominal_pixels"]
        assert c["2012_loss_class_persists_2013_pixels"]==row["n_nominal_pixels"]
        assert not row["historic_station_independently_confirmed"]
def test_missing_imagery_is_not_zero_change():
    pts=sites();box,w,h=m.shared_grid(pts);shape=h,w
    a=np.full(shape,41,dtype=np.uint8);b=np.full(shape,82,dtype=np.uint8)
    good=np.ones(shape,dtype=bool);missing=np.zeros(shape,dtype=bool)
    out=m.analyze(pts,{2011:(a,good),2012:(b,missing),2013:(b,good)},box)
    assert len(out)==20
    assert all(not row["passes_80pct"] for row in out)
    assert all(row["2011_to_2012_transition"]["forest_loss_pixels"] is None for row in out)
def test_broad_location_or_incomplete_years_fails():
    pts=sites();pts.loc[pts.stop_number==10,"longitude"]=-88
    with pytest.raises(ValueError,match="too broad"):m.shared_grid(pts)
    pts=sites();box,w,h=m.shared_grid(pts)
    with pytest.raises(ValueError,match="Incomplete raster years"):
        m.analyze(pts,{2011:(np.zeros((h,w),dtype=np.uint8),np.ones((h,w),dtype=bool))},box)
def test_population_and_years_precommitted():
    assert m.ROUTES==("360104","360110","360125","360213","360219","360316","360412")
    assert m.YEARS==(2011,2012,2013)
    assert "360109" not in m.ROUTES and "360417" not in m.ROUTES
