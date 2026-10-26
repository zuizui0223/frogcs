"""Reuse pinned EarthEnv rasters for landscape context around acoustic sites.

Main radius 3 km, sensitivity 1 km. Cell-centre circular buffers, cosine area
weights, missing values retained. This does not reconstruct pond architecture.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import urllib.request
import shutil
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds, Window

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_remote_vegetation_20261026'
CACHE=ROOT.parent/'earthenv_cache'
BANDS={6:'herbaceous',8:'flooded',12:'water'}


def circular_summary(data,transform,lon,lat,radius):
    dx=radius/(111320*math.cos(math.radians(lat)));dy=radius/111320
    raw=from_bounds(lon-dx,lat-dy,lon+dx,lat+dy,transform)
    c0=max(0,math.floor(raw.col_off));c1=min(data.shape[1],math.ceil(raw.col_off+raw.width))
    r0=max(0,math.floor(raw.row_off));r1=min(data.shape[0],math.ceil(raw.row_off+raw.height))
    cols=np.arange(c0,c1);rows=np.arange(r0,r1)
    xs=transform.c+(cols+.5)*transform.a;ys=transform.f+(rows+.5)*transform.e
    distances=((xs[None,:]-lon)*111320*math.cos(math.radians(lat)))**2+((ys[:,None]-lat)*111320)**2
    inside=distances<=radius**2
    values=data[r0:r1,c0:c1]
    valid=inside&(values<=100)
    n=int(valid.sum()); total=int(inside.sum())
    if n==0:return dict(mean=None,sd=None,positive_fraction=None,valid_cells=0,total_cells=total)
    weights=np.broadcast_to(np.cos(np.deg2rad(ys))[:,None],values.shape)[valid]
    vals=values[valid].astype(float);mean=np.average(vals,weights=weights)
    return dict(mean=float(mean),sd=float(np.sqrt(np.average((vals-mean)**2,weights=weights))),
                positive_fraction=float(np.average(vals>0,weights=weights)),valid_cells=n,total_cells=total)


def fetch(item):
    band,pin=item;dest=CACHE/f'earthenv_{band}.tif'
    if not dest.exists():
        request=urllib.request.Request(pin['url'],headers={'User-Agent':'Frogcs-EcologyMacro/1.0'})
        temp=dest.with_suffix('.part')
        with urllib.request.urlopen(request,timeout=120) as src, temp.open('wb') as target:
            shutil.copyfileobj(src,target)
        temp.replace(dest)
    sha=hashlib.sha256(dest.read_bytes()).hexdigest()
    if sha!=pin['sha256']:raise ValueError('Source hash drift: '+str(band))
    return dict(band=band,url=pin['url'],sha256=sha,bytes=dest.stat().st_size)


def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    pins=json.loads((ROOT/'research/results/earthenv_wetland_1deg/observed_results.json').read_text(encoding='utf-8'))['download_receipts']
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipts=list(pool.map(fetch,[(k,pins[str(k)]) for k in BANDS]))
    sites=pd.read_csv(ROOT/'research/results/interaction_species_sdm_20261026/naamp_site_environment.csv.gz')[['site','lat','lon']]
    assert sites.site.is_unique
    result=sites.copy();raster_meta=[]
    for band,name in BANDS.items():
        with rasterio.open(CACHE/f'earthenv_{band}.tif') as src:
            raw=from_bounds(sites.lon.min()-.1,sites.lat.min()-.1,sites.lon.max()+.1,sites.lat.max()+.1,src.transform)
            win=Window(math.floor(raw.col_off),math.floor(raw.row_off),math.ceil(raw.width)+2,math.ceil(raw.height)+2)
            data=src.read(1,window=win);transform=src.window_transform(win)
            raster_meta.append(dict(band=band,crs=str(src.crs),source_transform=list(src.transform),
                                    source_shape=[src.height,src.width],regional_shape=list(data.shape),nodata=src.nodata))
            # Replay existing point sample before changing spatial support.
            if name in ('flooded','water'):
                vals=np.array([x[0] for x in src.sample(zip(sites.lon,sites.lat))])
                saved=pd.read_csv(ROOT/'research/results/interaction_species_sdm_20261026/naamp_site_environment.csv.gz')[name].to_numpy()
                assert np.array_equal(vals.astype(float),saved)
        for radius in [1000,3000]:
            rows=[circular_summary(data,transform,s.lon,s.lat,radius) for s in sites.itertuples()]
            for measure in rows[0]:
                result[f'{name}_{radius}m_{measure}']=[r[measure] for r in rows]
        print('sampled',name,len(sites),flush=True)
    result.to_csv(OUT/'site_landscape_context.csv.gz',index=False)
    primary=pd.read_csv(ROOT/'research/results/naamp_site_use_associations_20261026/primary_site_characteristics.csv.gz')
    joined=primary.merge(result.drop(columns=['lat','lon']),on='site',validate='one_to_one')
    joined.to_csv(OUT/'primary_site_landscape_context.csv.gz',index=False)
    summary=[]
    for band in BANDS.values():
        for radius in [1000,3000]:
            name=f'{band}_{radius}m_mean';valid=joined[name].notna();positive=joined[name]>0
            summary.append(dict(band=band,radius_m=radius,sites=len(joined),valid_sites=int(valid.sum()),
                                positive_sites=int(positive.sum()),positive_routes=int(joined.loc[positive,'route'].nunique()),
                                median=float(joined[name].median()),q90=float(joined[name].quantile(.9))))
    pd.DataFrame(summary).to_csv(OUT/'coverage.csv',index=False)
    metadata=dict(dataset='EarthEnv full v1, Tuanmu & Jetz 2014, CC BY-NC 4.0',receipts=receipts,raster_metadata=raster_meta,
                  main_radius_m=3000,sensitivity_radius_m=1000,total_sites=len(sites),primary_sites=len(joined),
                  interpretation='Landscape context of consensus prevalence; not actual pond stem density, refuge use or current vegetation',
                  time='Static composite of historical input products, not a strict annual prior-history covariate',
                  extraction='Cell centres within approximate metric circle; cosine-latitude area weighting; values 0..100 valid; 255 missing',
                  point_replay='Exact agreement with previously saved flooded/open-water point samples')
    (OUT/'observed_results.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(pd.DataFrame(summary).to_string(index=False))


if __name__=='__main__':main()
