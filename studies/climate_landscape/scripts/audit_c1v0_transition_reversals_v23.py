#!/usr/bin/env python3
"""Response-blind temporal-persistence QC for pinned 2001-2015 C1V0 Iowa 360417.

Class changes and one-year reversals describe a map product, not verified
physical land conversion. No NAAMP frog outcomes, site history, or C1V2 pixels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from rasterio.io import MemoryFile

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from annual_nlcd_c1v0_series_360417_v19 import YEARS,STOP_SHA,STOP_SOURCE,fixed_site_masks
from audit_c1v0_ecological_class_change_v18 import group_classes


def read_source(archive:Path):
    arr={}
    with ZipFile(archive) as z:
        receipt=json.loads(z.read('source_receipt.json'))
        if receipt.get('status')!='COMPLETE_15_YEAR_SOURCE_ONLY_LANDCOVER':
            raise ValueError('Original 15-year source receipt incomplete')
        if receipt.get('original_collection')!='C1V0_not_C1V2':
            raise ValueError('Wrong Annual NLCD product collection')
        if receipt.get('source_station_sha256')!=STOP_SHA:
            raise ValueError('Site source SHA mismatch')
        for year in YEARS:
            name=f'annual_c1v0_{year}_360417.tif'
            data=z.read(name)
            if hashlib.sha256(data).hexdigest()!=receipt['years'][str(year)]['tiff_sha256']:
                raise ValueError('Source SHA mismatch for year '+str(year))
            with MemoryFile(data) as mf:
                with mf.open() as src:
                    if (src.count!=1 or src.crs is None or src.crs.to_epsg()!=5070 or
                        src.shape!=(409,170) or any(abs(a-b)>1e-9 for a,b in zip(src.res,(30,30)))):
                        raise ValueError('Raster grid not frozen source')
                    raw=src.read(1)
                    if src.nodata is not None and np.any(raw==src.nodata):
                        raise ValueError('No-data pixels in original source')
                    arr[year]=group_classes(raw)
    if hashlib.sha256(STOP_SOURCE.read_bytes()).hexdigest()!=STOP_SHA:
        raise ValueError('Frozen station coordinate file drifted')
    return arr,pd.read_csv(STOP_SOURCE,dtype={'route_id':str,'site_id':str}),receipt


def classify_three(before:np.ndarray,current:np.ndarray,following:np.ndarray,mask:np.ndarray)->dict:
    if before.shape!=current.shape or before.shape!=following.shape or before.shape!=mask.shape:
        raise ValueError('Array shape/geometry mismatch')
    if mask.dtype!=bool:
        raise ValueError('Mask must be boolean')
    if not mask.any():raise ValueError('Empty buffer')
    for x in (before,current,following):
        if not np.isin(x,np.arange(1,10)).all():
            raise ValueError('Not a classified land-cover group')
    change=mask&(before!=current)
    revert=change&(following==before)
    persisted=change&(following==current)
    three=change&(following!=before)&(following!=current)
    loss=mask&(before==5)&(current!=5)
    forest_revert=loss&(following==5)
    forest_persist=loss&(following!=5)
    count=lambda x:int(x.sum())
    if count(revert)+count(persisted)+count(three)!=count(change):
        raise AssertionError('Changed pixels not fully partitioned')
    if count(forest_revert)+count(forest_persist)!=count(loss):
        raise AssertionError('Forest loss must partition into next-year states')
    return {'n_nominal_pixels':count(mask),'functional_group_changed_pixels':count(change),
            'one_year_reversed_group_pixels':count(revert),
            'following_year_same_new_group_pixels':count(persisted),
            'third_group_next_year_pixels':count(three),
            'forest_group_loss_pixels':count(loss),
            'forest_loss_reverted_next_year_pixels':count(forest_revert),
            'forest_loss_persisted_nonforest_next_year_pixels':count(forest_persist)}


def audit(arr:dict,stops:pd.DataFrame):
    if sorted(arr)!=list(YEARS):raise ValueError('All exact years required')
    if not all(v.shape==arr[2001].shape for v in arr.values()):
        raise ValueError('Source pixels not aligned')
    masks=fixed_site_masks(stops)
    rows=[]
    for (site,radius),mask in sorted(masks.items()):
        for year in YEARS[1:-1]:
            row=classify_three(arr[year-1],arr[year],arr[year+1],mask)
            rows.append({'route_id':'360417','site_id':site,'buffer_m':radius,
                'from_year':year-1,'to_year':year,'followup_year':year+1,
                'field_site_historically_verified':False,
                'nlcd_collection':'C1V0_not_C1V2',**row})
    x=pd.DataFrame(rows).sort_values(['buffer_m','to_year','site_id']).reset_index(drop=True)
    summary={}
    fields=['functional_group_changed_pixels','one_year_reversed_group_pixels',
      'following_year_same_new_group_pixels','third_group_next_year_pixels',
      'forest_group_loss_pixels','forest_loss_reverted_next_year_pixels',
      'forest_loss_persisted_nonforest_next_year_pixels']
    for radius,g in x.groupby('buffer_m'):
        total={k:int(g[k].sum()) for k in fields}
        total['fraction_group_changes_reverted_after_one_year']=(
            total['one_year_reversed_group_pixels']/total['functional_group_changed_pixels']
            if total['functional_group_changed_pixels'] else None)
        total['fraction_forest_loss_reverted_after_one_year']=(
            total['forest_loss_reverted_next_year_pixels']/total['forest_group_loss_pixels']
            if total['forest_group_loss_pixels'] else None)
        grouped=g.groupby('to_year')[fields].sum().astype(int).reset_index()
        total['by_transition_year']=grouped.to_dict(orient='records')
        total['number_of_distinct_sites']=int(g.site_id.nunique())
        summary[str(radius)]=total
    return x,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True)
    p.add_argument('--output-dir',required=True)
    args=p.parse_args()
    images,stops,source=read_source(Path(args.archive))
    result,summary=audit(images,stops)
    path=Path(args.output_dir);path.mkdir(parents=True,exist_ok=True)
    result.to_csv(path/'per_site_year_group_stability.csv',index=False)
    receipt={'analysis':'annual_nlcd_C1V0_2001_2015_one_year_reversal_vs_persistence_v2_3',
      'study':'Iowa route 360417 map classification noise vs persistence, not frog biology',
      'route_id':'360417','source_zip_sha256':hashlib.sha256(Path(args.archive).read_bytes()).hexdigest(),
      'source_collection':'C1V0 not C1.2','n_frog_outcomes_opened':0,
      'n_independently_verified_historical_sites':0,
      'not_an_independent_confirmatory_selection':True,
      'n_site_buffer_year_transition_records':len(result),
      'study_radii':[250,1000],
      'last_transition_included_for_followup':'2013_to_2014_followed_in_2015',
      'last_transition_excluded_for_followup':'2014_to_2015, no 2016 source',
      'overlapping_one_km_buffers_not_independent_area':True,
      'summary':summary}
    (path/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'n_rows':len(result),'summary':{k:{x:v for x,v in y.items() if x!='by_transition_year'} for k,y in summary.items()}},sort_keys=True,indent=2))

if __name__=='__main__':main()
