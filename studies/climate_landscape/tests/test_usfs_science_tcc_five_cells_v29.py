import importlib.util,sys,json
from pathlib import Path
import numpy as np,pandas as pd,pytest
HERE=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location("tcc",HERE/"extract_usfs_science_tcc_at_five_nlcd_cells_v29.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_catalog_original_2025_6_source_one_row_per_year(monkeypatch):
    def fake(base,endpoint,params,max_bytes=1000000):
        year=int(params["where"].split(" <= ")[1].split(" ")[0])
        name="Science_TCC" if "Science_" in base else "NLCD_TCC"
        return json.dumps({"features":[{"attributes":{
            "beginyear":year,"endyear":year,
            "name":f"{m.EXPECTED_NAME_PREFIX[name]}{year}0101_{year}1231",
            "objectid":145 if name=="Science_TCC" else 66,
            "dataset_name":"Science TCC CONUS"}}]}).encode()
    monkeypatch.setattr(m,"request",fake)
    for year in m.YEARS:
        for product in m.BASES:
            row,checksum=m.get_catalog(product,year)
            assert row["beginyear"]==row["endyear"]==year
            assert len(checksum)==64

def test_version_drift_hard_fails(monkeypatch):
    monkeypatch.setattr(m,"request",lambda *args,**kw:
      json.dumps({"features":[{"attributes":{
          "beginyear":2011,"endyear":2011,"name":"wrong_C1V0_image",
          "objectid":145}}]}).encode())
    with pytest.raises(ValueError,match="original year/catalog drift"):
        m.get_catalog("Science_TCC",2011)

def test_frozen_population_not_a_statistically_independent_confirmation():
    assert m.YEARS==(2011,2012,2013)
    assert m.TARGETS=={"360104":("6613",3,3),"360412":("7247",7,2)}
    assert set(m.BASES)=={"Science_TCC","NLCD_TCC"}

def test_loss_cell_negative_and_positive_canopy_delta_both_retained():
    import pyproj
    lon,lat=-93.5,42
    x,y=pyproj.Transformer.from_crs(4326,5070,always_xy=True).transform(lon,lat)
    west=30*int(np.floor((x-300)/30))
    north=30*int(np.ceil((y+300)/30))
    bbox=(west,north-600,west+600,north)
    width=height=20
    col=int(np.floor((x-west)/30));row=int(np.floor((north-y)/30))
    old=np.full((20,20),82,dtype=np.uint8)
    new=old.copy();old[row,col]=41
    good=np.ones((20,20),dtype=bool)
    # Science: target forest loss in categorical layer, but modelled canopy can rise.
    a=np.full((20,20),60,dtype=np.uint8);b=np.full((20,20),55,dtype=np.uint8)
    c=np.full((20,20),51,dtype=np.uint8)
    a[row,col]=17;b[row,col]=20;c[row,col]=22
    source={"Science_TCC":{2011:(a,good,{}),2012:(b,good,{}),2013:(c,good,{})},
            "NLCD_TCC":{2011:(a,good,{}),2012:(b,good,{}),2013:(c,good,{})}}
    station=pd.DataFrame([{"site_id":"6613","route_id":"360104",
        "stop_number":3,"latitude":lat,"longitude":lon}])
    out=m.summarize_site(station,bbox,(old,good,bbox),(new,good,bbox),source,1)
    assert out["USFS_annual_tree_canopy_comparison"]["Science_TCC"]["loss_cell_delta_2011_2013_pct_points"]==[5]
    assert out["USFS_annual_tree_canopy_comparison"]["Science_TCC"]["loss_cells_with_declining_canopy_2011_2013"]==0
    assert not out["historical_field_site_verified"]
