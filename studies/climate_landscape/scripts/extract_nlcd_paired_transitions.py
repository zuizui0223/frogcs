#!/usr/bin/env python3
"""Paired-pixel land-cover transitions from two verified USGS Annual NLCD C1.2 maps.

Unlike subtracting separately summarized land-cover shares, this compares the
SAME valid pixels between years. It distinguishes stable forest, genuine
forest conversions and reciprocal changes, and preserves missingness. Source
rasters must be independently obtained from official USGS 30-m annual NLCD.

This is entirely response-blind: it NEVER reads frog acoustic data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds
from rasterio.warp import transform
from shapely.geometry import Point, mapping

CLASS_CODES=frozenset((11,12,21,22,23,24,31,41,42,43,52,71,81,82,90,95))
FOREST=frozenset((41,42,43))
DEVELOPED=frozenset((21,22,23,24))
AGRICULTURE=frozenset((81,82))
WETLAND=frozenset((90,95))
OPEN_WATER=frozenset((11,))
MIN_PAIRED_PIXEL_COVERAGE=0.80
REQUIRED={"run_id","route_id","site_id","latitude","longitude","buffer_m","year_earlier","year_later",
          "survey_date","coordinate_qc_status","verification_source_id"}
INDEX={"year","raster_path","source_image_id","source_version"}
FORBIDDEN={"Species","CallingIndex","calling_index","chorus","CI2","CI3","frog_response"}


def _reject_response_columns(df):
    forbidden=FORBIDDEN & set(df.columns)
    if forbidden:raise ValueError(f"Acoustic outcomes not allowed in an environmental extraction: {forbidden}")


def _validate_src_pair(a,b):
    if a.count!=1 or b.count!=1:
        raise ValueError('Single thematic raster band required')
    if (a.crs!=b.crs or a.transform!=b.transform or a.width!=b.width or a.height!=b.height):
        raise ValueError('Paired NLCD rasters must have exactly the same grid and CRS')
    if a.crs is None or not a.crs.is_projected:
        raise ValueError('Use official metric projected NLCD rasters')
    if str(a.crs.linear_units).lower() not in ('metre','meter','metres','meters'):
        raise ValueError('Projected pixel units must be metres')
    crs_str=str(a.crs)
    if crs_str!='EPSG:5070' and 'albers' not in a.crs.to_wkt().lower():
        raise ValueError('Use official North American Albers Equal Area land cover grid')
    if a.res[0] <= 0 or a.res[1] <= 0:
        raise ValueError('Invalid map resolution')
    if not (25<=a.res[0]<=35 and 25<=a.res[1]<=35):
        raise ValueError('Expected official ~30 metre annual NLCD source')


def _circle_window(a,lat,lon,radius):
    x,y=transform('EPSG:4326',a.crs,[float(lon)],[float(lat)])
    x,y=x[0],y[0]
    geom=Point(x,y).buffer(int(radius),quad_segs=128)
    win=from_bounds(x-radius-35,y-radius-35,x+radius+35,y+radius+35,transform=a.transform)
    win=win.round_offsets().round_lengths()
    subtrans=a.window_transform(win)
    shape=(int(win.height),int(win.width))
    mask=geometry_mask([mapping(geom)],out_shape=shape,transform=subtrans,invert=True,all_touched=False)
    if not mask.any():raise ValueError('No pixel centers inside requested buffer')
    return win,mask


def _one_window(a,b,lon,lat,radius):
    _validate_src_pair(a,b)
    win,circle=_circle_window(a,lat,lon,radius)
    pa=a.read(1,window=win,boundless=True,fill_value=a.nodata if a.nodata is not None else 0)
    pb=b.read(1,window=win,boundless=True,fill_value=b.nodata if b.nodata is not None else 0)
    valid_a=np.isin(pa,tuple(CLASS_CODES)) & (pa!=a.nodata if a.nodata is not None else True)
    valid_b=np.isin(pb,tuple(CLASS_CODES)) & (pb!=b.nodata if b.nodata is not None else True)
    unexpected_a=pa[circle & ~valid_a & (pa!=a.nodata if a.nodata is not None else True)]
    unexpected_b=pb[circle & ~valid_b & (pb!=b.nodata if b.nodata is not None else True)]
    if len(unexpected_a) or len(unexpected_b):
        raise ValueError(f'Unexpected Annual NLCD classes: {np.unique(np.r_[unexpected_a,unexpected_b]).tolist()}')
    both=circle & valid_a & valid_b
    total=int(circle.sum()); n=int(both.sum())
    frac=n/total
    result={"buffer_m":int(radius),"total_buffer_pixels":total,"paired_valid_pixels":n,
            "paired_valid_fraction":frac,"baseline_valid_fraction":int((circle&valid_a).sum())/total,
            "later_valid_fraction":int((circle&valid_b).sum())/total,
            "validity_threshold":MIN_PAIRED_PIXEL_COVERAGE,
            "confidence_product_screened":False,
            "pixel_pair_status":"eligible" if frac>=MIN_PAIRED_PIXEL_COVERAGE else "insufficient_paired_valid_area"}
    metrics=('forest_loss','forest_gain','forest_to_developed','forest_to_agriculture',
             'forest_to_wetland','forest_to_open_water','developed_gain','developed_loss',
             'agriculture_gain','wetland_loss','wetland_gain','stable_forest',
             'unchanged_class','baseline_forest','later_forest')
    for k in metrics:
        result[k+'_fraction']=np.nan
    result['forest_balance_error']=np.nan
    if frac<MIN_PAIRED_PIXEL_COVERAGE:return result
    f0=np.isin(pa,tuple(FOREST))
    f1=np.isin(pb,tuple(FOREST))
    d0=np.isin(pa,tuple(DEVELOPED));d1=np.isin(pb,tuple(DEVELOPED))
    a0=np.isin(pa,tuple(AGRICULTURE));a1=np.isin(pb,tuple(AGRICULTURE))
    w0=np.isin(pa,tuple(WETLAND));w1=np.isin(pb,tuple(WETLAND))
    o1=np.isin(pb,tuple(OPEN_WATER))
    vals={
       'forest_loss':f0&~f1, 'forest_gain':~f0&f1,
       'forest_to_developed':f0&d1, 'forest_to_agriculture':f0&a1,
       'forest_to_wetland':f0&w1, 'forest_to_open_water':f0&o1,
       'developed_gain':~d0&d1,'developed_loss':d0&~d1,
       'agriculture_gain':~a0&a1,
       'wetland_loss':w0&~w1,'wetland_gain':~w0&w1,
       'stable_forest':f0&f1,'unchanged_class':pa==pb,
       'baseline_forest':f0,'later_forest':f1}
    for k,v in vals.items():
        result[k+'_fraction']=float((v&both).sum()/n)
    # On identical jointly-valid pixels, net forest loss must equal gross loss - gain.
    result['forest_balance_error']=float(result['baseline_forest_fraction']-result['later_forest_fraction']-
                                          result['forest_loss_fraction']+result['forest_gain_fraction'])
    if abs(result['forest_balance_error'])>1e-12:
        raise AssertionError('Forest transition mass conservation violated')
    return result


def extract(requests,index):
    _reject_response_columns(requests);_reject_response_columns(index)
    for label,df,req in (('requests',requests,REQUIRED),('raster index',index,INDEX)):
        missing=req-set(df.columns)
        if missing:raise ValueError(f'{label} missing {sorted(missing)}')
    r=requests[sorted(REQUIRED)].copy()
    i=index[sorted(INDEX)].copy()
    if r.duplicated(['run_id','route_id','site_id','buffer_m','year_earlier','year_later','survey_date']).any():
        raise ValueError('Duplicate site-time change requests')
    if i.duplicated(['year']).any():raise ValueError('Duplicate official raster-year index')
    if not i.source_version.astype(str).eq('ANNUAL_NLCD_C1_2').all():
        raise ValueError('Official Annual NLCD Collection 1.2 only')
    for c in ('year_earlier','year_later','buffer_m'):
        r[c]=pd.to_numeric(r[c],errors='raise').astype(int)
    i['year']=pd.to_numeric(i.year,errors='raise').astype(int)
    r['survey_date']=pd.to_datetime(r.survey_date,errors='raise')
    if r.survey_date.isna().any():raise ValueError('Missing survey date')
    if not r.coordinate_qc_status.eq('verified_external').all():
        raise ValueError('Physical site identity must be independently verified')
    if r.verification_source_id.astype('string').isna().any() or r.verification_source_id.astype(str).str.strip().eq('').any():
        raise ValueError('Independent station identity evidence required')
    if not r.buffer_m.isin((250,1000)).all():raise ValueError('Unexpected buffer size')
    if (r.year_earlier>=r.year_later).any() or (r.year_later>=r.survey_date.dt.year).any():
        raise ValueError('Satellite change date must strictly precede the frog survey year')
    if (r.year_earlier<1985).any() or (r.year_later>2025).any():
        raise ValueError('Annual NLCD Collection 1.2 only covers 1985–2025')
    src={int(x.year):x for x in i.itertuples(index=False)}
    missing=(set(r.year_earlier)|set(r.year_later))-set(src)
    if missing:raise ValueError(f'Official land-cover rasters missing years {sorted(missing)}')
    from contextlib import ExitStack
    out=[]
    with ExitStack() as stack:
        ras={year:stack.enter_context(rasterio.open(src[year].raster_path))
             for year in sorted(set(r.year_earlier)|set(r.year_later))}
        for x in r.itertuples(index=False):
            row=_one_window(ras[int(x.year_earlier)],ras[int(x.year_later)],
                           float(x.longitude),float(x.latitude),int(x.buffer_m))
            row.update({'run_id':str(x.run_id),'route_id':str(x.route_id),'site_id':str(x.site_id),
                        'survey_date':x.survey_date.date().isoformat(),
                        'baseline_year':int(x.year_earlier), 'comparison_year':int(x.year_later),
                        'baseline_source_id':str(src[int(x.year_earlier)].source_image_id),
                        'comparison_source_id':str(src[int(x.year_later)].source_image_id),
                        'source_version':'ANNUAL_NLCD_C1_2',
                        'coordinate_qc_status':x.coordinate_qc_status,
                        'verification_source_id':str(x.verification_source_id)})
            out.append(row)
    return pd.DataFrame(out).sort_values(['run_id','route_id','site_id','survey_date','buffer_m']).reset_index(drop=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--requests',required=True)
    p.add_argument('--raster-index',required=True)
    p.add_argument('--out',required=True)
    p.add_argument('--receipt',required=True)
    args=p.parse_args()
    raw=pd.read_csv(args.requests,dtype={'run_id':str,'route_id':str,'site_id':str,'verification_source_id':str})
    index=pd.read_csv(args.raster_index)
    result=extract(raw,index)
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(dest,index=False)
    receipt={'analysis':'annual_nlcd_c1_2_same_pixel_terrestrial_transitions_v0_1',
             'n_site_time_buffer_requests':len(result),
             'n_paired_pixel_valid_results':int(result.pixel_pair_status.eq('eligible').sum()),
             'n_insufficient_valid_results':int(result.pixel_pair_status.ne('eligible').sum()),
             'response_columns_read':False,'independent_station_verification_required':True,
             'source_version':'ANNUAL_NLCD_C1_2',
             'qa_confidence_product_evaluated':False,
             'input_sha256':{'requests':hashlib.sha256(Path(args.requests).read_bytes()).hexdigest(),
                             'rasters_index':hashlib.sha256(Path(args.raster_index).read_bytes()).hexdigest()},
             'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    rp=Path(args.receipt);rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
