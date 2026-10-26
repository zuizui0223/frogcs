"""GLAD annual open-water observations strictly before fixed NAAMP pairs.

3-km circle primary, 1-km sensitivity. All intersecting tiles, no nearest-pond
assignment. Separate area with water detections and frequency conditional on
water-positive pixels. Never call these inundation days or vegetation structure.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import defaultdict
from datetime import datetime,timezone
import hashlib
import json
import math
import shutil
import urllib.request
import time
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds,Window

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/naamp_prior_water_20261026'
CACHE=ROOT.parent/'glad_annual_cache'


def tile_keys(lon,lat,radius=3000):
    dx=radius/(111320*math.cos(math.radians(lat)));dy=radius/111320
    return [(north,west) for north in range((math.floor((lat-dy)/10)+1)*10,(math.floor((lat+dy)/10)+1)*10+1,10)
            for west in range(math.floor((lon-dx)/10)*10,math.floor((lon+dx)/10)*10+1,10)]


def circle_sums(data,transform,lon,lat,radius):
    ys=transform.f+(np.arange(data.shape[0])+.5)*transform.e
    xs=transform.c+(np.arange(data.shape[1])+.5)*transform.a
    mask=(((xs[None,:]-lon)*111320*math.cos(math.radians(lat)))**2+((ys[:,None]-lat)*111320)**2)<=radius**2
    valid=mask&(data<=100);positive=valid&(data>0)
    weights=np.broadcast_to(np.cos(np.deg2rad(ys))[:,None],data.shape)
    return dict(total_cells=int(mask.sum()),valid_cells=int(valid.sum()),unknown_codes=int((mask&(data>100)&(data!=255)).sum()),
                valid_weight=float(weights[valid].sum()),water_weight=float(weights[positive].sum()),
                water_value_sum=float((weights[valid]*data[valid]).sum()))


def fetch(north,west,year):
    tile=f'{abs(north):02d}{"N" if north>=0 else "S"}_{abs(west):03d}{"E" if west>=0 else "W"}'
    url=f'https://storage.googleapis.com/earthenginepartners-hansen/waterC2/{tile}/{year}_percent.tif'
    path=CACHE/f'{tile}_{year}.tif';receipt_path=path.with_suffix('.json')
    if path.exists() and receipt_path.exists():
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Cached file hash mismatch')
        return path,receipt
    last=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Frogcs-EcologyMacro/1.0'})
            with urllib.request.urlopen(req,timeout=120) as src:
                headers=dict(src.headers);length=int(src.headers.get('Content-Length','0'))
                if length>150_000_000:raise ValueError('Unexpected raster size')
                tmp=path.with_suffix('.part')
                with tmp.open('wb') as target:shutil.copyfileobj(src,target)
            if length and tmp.stat().st_size!=length:raise ValueError('Truncated source')
            with rasterio.open(tmp) as ds:
                if str(ds.crs)!='EPSG:4326' or ds.count!=1:raise ValueError('Unexpected raster')
                geometry=dict(shape=[ds.height,ds.width],transform=list(ds.transform),nodata=ds.nodata)
            tmp.replace(path)
            receipt=dict(url=url,year=year,tile=tile,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         etag=headers.get('ETag'),last_modified=headers.get('Last-Modified'),retrieved_utc=datetime.now(timezone.utc).isoformat(),**geometry)
            receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
            return path,receipt
        except Exception as error:
            last=error
            if attempt<2:time.sleep(1+attempt)
    raise RuntimeError(f'{url}: {last}')


def tile_job(key,records):
    north,west,year=key
    try:
        path,receipt=fetch(north,west,year)
        results=[]
        with rasterio.open(path) as src:
            for r in sorted(records,key=lambda z:z['lat'],reverse=True):
                dx=3000/(111320*math.cos(math.radians(r['lat'])));dy=3000/111320
                left=max(src.bounds.left,r['lon']-dx);right=min(src.bounds.right,r['lon']+dx)
                bottom=max(src.bounds.bottom,r['lat']-dy);top=min(src.bounds.top,r['lat']+dy)
                raw=from_bounds(left,bottom,right,top,src.transform)
                c0=max(0,math.floor(raw.col_off));r0=max(0,math.floor(raw.row_off))
                c1=min(src.width,math.ceil(raw.col_off+raw.width));r1=min(src.height,math.ceil(raw.row_off+raw.height))
                win=Window(c0,r0,c1-c0,r1-r0);data=src.read(1,window=win)
                for radius in [1000,3000]:
                    results.append(dict(site=r['site'],water_year=year,radius_m=radius,
                                        **circle_sums(data,src.window_transform(win),r['lon'],r['lat'],radius)))
        return dict(status='ok',receipt=receipt,rows=results,key=key)
    except Exception as error:return dict(status='error',key=key,error=str(error),rows=[])


def main():
    OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    base=ROOT/'research/results/naamp_three_guild_occurrence/full_naamp_history'
    p=pd.read_csv(base/'matched_strong_silent_history.csv')
    v=pd.read_csv(base/'naamp_completed_site_surveys.csv.gz')
    env=pd.read_csv(ROOT/'research/results/interaction_species_sdm_20261026/naamp_site_environment.csv.gz')
    ends=pd.concat([p[['run','chosen_site']].rename(columns={'chosen_site':'site'}),p[['run','silent_site']].rename(columns={'silent_site':'site'})])
    points=ends.merge(v[['run','site','year']],on=['run','site'],validate='many_to_one').merge(env[['site','lat','lon']],on='site',validate='many_to_one')
    points['water_year']=points.year-1
    points=points[['site','lat','lon','water_year']].drop_duplicates(['site','water_year'])
    assert len(p)==4040 and len(points)==6293
    jobs=defaultdict(list);expected={}
    for r in points.to_dict('records'):
        keys=tile_keys(r['lon'],r['lat']);expected[(r['site'],r['water_year'])]=len(keys)
        for north,west in keys:jobs[(north,west,r['water_year'])].append(r)
    print('planned',len(points),'site-years;',len(jobs),'tile-years',flush=True)
    receipts=[];allrows=[];failures=[]
    with rasterio.Env(GDAL_CACHEMAX=256_000_000):
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending={pool.submit(tile_job,k,rs):k for k,rs in jobs.items()}
            for number,future in enumerate(as_completed(pending),1):
                result=future.result()
                if result['status']=='ok':receipts.append(result['receipt']);allrows.extend(result['rows'])
                else:failures.append({k:z for k,z in result.items() if k!='rows'})
                (OUT/'progress.json').write_text(json.dumps(dict(completed=number,total=len(jobs),successful=len(receipts),failures=failures)),encoding='utf-8')
                print('tile',number,'/',len(jobs),result['key'],result['status'],flush=True)
    rows=pd.DataFrame(allrows)
    columns=['total_cells','valid_cells','unknown_codes','valid_weight','water_weight','water_value_sum']
    agg=rows.groupby(['site','water_year','radius_m'])[columns].sum()
    agg['tiles_read']=rows.groupby(['site','water_year','radius_m']).size()
    agg=agg.reset_index();agg['tiles_expected']=[expected[(r.site,r.water_year)] for r in agg.itertuples()]
    agg['complete']=agg.tiles_read==agg.tiles_expected
    agg['valid_fraction']=agg.valid_cells/agg.total_cells
    agg['mean_water_frequency']=agg.water_value_sum/agg.valid_weight
    agg['water_positive_area_fraction']=agg.water_weight/agg.valid_weight
    agg['frequency_on_water_positive_pixels']=agg.water_value_sum/agg.water_weight.replace(0,np.nan)
    for c in ['mean_water_frequency','water_positive_area_fraction','frequency_on_water_positive_pixels']:
        agg.loc[~agg.complete|agg.valid_fraction.lt(.9)|agg.unknown_codes.gt(0),c]=np.nan
    agg.to_csv(OUT/'prior_year_site_water_context.csv.gz',index=False)
    pd.DataFrame(receipts).sort_values(['tile','year']).to_csv(OUT/'source_receipts.csv',index=False)
    meta=dict(pair_source_sha256=hashlib.sha256((base/'matched_strong_silent_history.csv').read_bytes()).hexdigest(),
              source='GLAD surface water dynamics Collection 2 annual water percent',
              source_docs='https://storage.googleapis.com/earthenginepartners-hansen/waterC2/download.html',
              sites_years=len(points),planned_tile_years=len(jobs),successful_tile_years=len(receipts),failures=failures,
              downloaded_bytes=sum(r['bytes'] for r in receipts),water_years=[int(points.water_year.min()),int(points.water_year.max())],
              main_radius_m=3000,sensitivity_radius_m=1000,min_valid_fraction=.9,
              missing_conditional_frequency='No water-positive pixels is undefined, not zero persistence',
              semantics='Percent of classified land/water observations that are water; not inundation days or actual breeding pond hydroperiod',
              reference='Pickens et al. 2020, doi:10.1016/j.rse.2020.111792')
    (OUT/'observed_results.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print(json.dumps(meta,indent=2),flush=True)


if __name__=='__main__':main()
