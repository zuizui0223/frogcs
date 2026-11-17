"""Annual native 30-m grid, WGS84 geodesic 3-km discs, cell-centre counts."""
from pathlib import Path
import argparse, json, hashlib, tempfile, zipfile, shutil
import requests
import numpy as np
import pandas as pd
import rasterio
from pyproj import Geod, Transformer
from rasterio.features import geometry_mask, geometry_window

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "research/results"
def cohort():
    sites = pd.read_csv(RESULTS / "naamp_remote_vegetation_20261026/primary_site_landscape_context.csv.gz")
    visits = pd.read_csv(RESULTS / "naamp_three_guild_occurrence/full_naamp_history/naamp_completed_site_surveys.csv.gz")
    visits = visits[visits.site.isin(sites.site) & visits.timeout.eq(0)]
    groups = visits.groupby(["site","year"]).agg(visits=("strong","size"), strong=("strong","sum")).reset_index()
    totals = groups.groupby("site").sum().loc[sites.site]
    np.testing.assert_array_equal(totals.visits, sites.n_visits)
    np.testing.assert_allclose(totals.strong/totals.visits, sites.strong_rate)
    assert (len(sites),len(groups),len(visits)) == (4248,26489,63180)
    return groups.merge(sites[["site","lon","lat"]],on="site",validate="many_to_one")

def extract(year,out):
    obs = cohort().query("year == @year").copy()
    name = f"Annual_NLCD_LndCov_{year}_CU_C1V1"
    url = f"https://www.mrlc.gov/downloads/sciweb1/shared/mrlc/data-bundles/{name}.zip"
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        digest=hashlib.sha256()
        with requests.get(url,stream=True,timeout=(30,180)) as r:
            r.raise_for_status()
            with (tmp/"source.zip").open("wb") as f:
                for data in r.iter_content(4*1024**2):
                    f.write(data);digest.update(data)
        with zipfile.ZipFile(tmp/"source.zip") as z:
            tif=next(n for n in z.namelist() if Path(n).name==name+".tif")
            with z.open(tif) as src,(tmp/"land.tif").open("wb") as dst:
                shutil.copyfileobj(src,dst,4*1024**2)
        with rasterio.open(tmp/"land.tif") as r:
            assert r.res==(30,30)
            project=Transformer.from_crs(4326,r.crs,always_xy=True)
            geo=Geod(ellps="WGS84")
            az=np.arange(360)
            rows=[]
            for a in obs.itertuples():
                lon,lat,_=geo.fwd(np.full(360,a.lon),np.full(360,a.lat),az,np.full(360,3000.))
                x,y=project.transform(lon,lat)
                ring=list(zip(x,y));shape={"type":"Polygon","coordinates":[ring+[ring[0]]]}
                w=geometry_window(r,[shape])
                keep=geometry_mask([shape],out_shape=(int(w.height),int(w.width)),transform=r.window_transform(w),invert=True)
                values=r.read(1,window=w)[keep]
                valid=values[np.isin(values,[11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95])]
                assert len(valid)>0 and 30700<len(values)<32000
                rows.append((a.site,year,a.visits,a.strong,len(values),len(valid),(valid==95).sum(),(valid==90).sum()))
            pd.DataFrame(rows,columns=["site","year","visits","strong","circle_cells","valid_cells","herb_cells","woody_cells"]).to_csv(out/f"{year}.csv",index=False)
            (out/f"{year}.json").write_text(json.dumps(dict(year=year,url=url,sha256=digest.hexdigest(),crs=r.crs.to_string(),res=r.res,nodata=r.nodata,n=len(rows)),indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("year",type=int);p.add_argument("output",type=Path)
    a=p.parse_args();extract(a.year,a.output)
