#!/usr/bin/env python3
"""Outcome-blind, source-pinned re-audit of Iowa 360417 Annual NLCD C1V0.

Separates 16-class changes from changes between ecological land-cover groups.
No NAAMP Counts.csv, breeding response, or 2001-2015 field-site verification.

Exact source: original archive from successful GitHub Actions run 37754405051,
artifact 11539925980, original C1V0 years 2004, 2009, 2014.  DO NOT mix
collections and DO NOT upgrade source label to Collection 1.2.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from rasterio.io import MemoryFile
from rasterio.warp import transform as project

YEARS = (2004, 2009, 2014)
PAIRS = ((2004, 2009), (2009, 2014), (2004, 2014))
ROUTE = '360417'
RADII = (250, 1000)
RASTER_PREFIX = 'arcgis_nlcd_C1V0_'
AUTHORITATIVE_SHA = {
    2004: '8384900d2afb3afb63624bb5a2368cf3a2b6dde98d737e0fb6cc9bbf544b7290',
    2009: 'e6207792fa973d97aaab49bfe226e71175ae4e8815ede11832d7b8301f34b0ad',
    2014: 'dc776e204f7f2ee7de9ff2817b58c8ac86f7ed6e44ab320c1733ba1f6c4694c0',
}
STOP_CSV_SHA = '8b7be934dc32aa71791b4e6c38295d25cbcebb66f2f6ab39714d41ce7b65f227'
SOURCE_ARTIFACT = 'https://github.com/zuizui0223/frogcs/actions/runs/37754405051/artifacts/11539925980'
# Group IDs: 1 water, 2 snow/ice, 3 developed, 4 barren, 5 forest,
# 6 shrub, 7 grass, 8 agriculture, 9 wetlands.
NLCD_TO_GROUP = {
    11: 1, 12: 2,
    21: 3, 22: 3, 23: 3, 24: 3,
    31: 4, 41: 5, 42: 5, 43: 5,
    52: 6, 71: 7, 81: 8, 82: 8, 90: 9, 95: 9,
}
GROUP_NAME = {
    1:'open_water',2:'ice_snow',3:'developed',4:'barren',5:'forest',
    6:'shrub',7:'grass',8:'agriculture',9:'wetland',
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def group_classes(a: np.ndarray) -> np.ndarray:
    if not set(np.unique(a).astype(int)).issubset(NLCD_TO_GROUP):
        raise ValueError('Unrecognized NLCD classes or nondisclosed missing pixels')
    ans = np.zeros(a.shape, dtype=np.uint8)
    for code, group in NLCD_TO_GROUP.items():
        ans[a == code] = group
    return ans


def classify_transition(old: np.ndarray, new: np.ndarray,
                        within: np.ndarray | None = None) -> dict:
    if old.shape != new.shape:
        raise ValueError('Yearly pixel arrays are not same-grid aligned')
    if within is None:
        within = np.ones(old.shape, dtype=bool)
    if within.shape != old.shape:
        raise ValueError('Site mask is not aligned with raster')
    before = group_classes(old)
    after = group_classes(new)
    fine = within & (old != new)
    ecogroup = within & (before != after)
    within_group = within & (old != new) & (before == after)
    agricultural = within & (((old == 81) & (new == 82)) |
                             ((old == 82) & (new == 81)))
    developed = within & np.isin(old, (21,22,23,24)) & np.isin(new,(21,22,23,24)) & (old != new)
    wetland = within & (((old == 90) & (new == 95)) | ((old == 95) & (new == 90)))
    forest_old = before == 5
    forest_new = after == 5
    values = {
        'valid_pixels': int(within.sum()),
        'fine_class_changed_pixels': int(fine.sum()),
        'between_group_changed_pixels': int(ecogroup.sum()),
        'within_group_changed_pixels': int(within_group.sum()),
        'agricultural_81_82_changed_pixels': int(agricultural.sum()),
        'developed_intensity_changed_pixels': int(developed.sum()),
        'wetland_90_95_changed_pixels': int(wetland.sum()),
        'forest_loss_pixels': int((within & forest_old & ~forest_new).sum()),
        'forest_gain_pixels': int((within & ~forest_old & forest_new).sum()),
        'forest_to_developed_pixels': int((within & forest_old & (after == 3)).sum()),
        'forest_to_agriculture_pixels': int((within & forest_old & (after == 8)).sum()),
    }
    if values['fine_class_changed_pixels'] != (values['between_group_changed_pixels'] + values['within_group_changed_pixels']):
        raise AssertionError('Partition of class changes failed')
    if values['within_group_changed_pixels'] != (values['agricultural_81_82_changed_pixels']+
      values['developed_intensity_changed_pixels']+values['wetland_90_95_changed_pixels']+
      int((within & (old != new) & (before == after) & ~agricultural & ~developed & ~wetland).sum())):
        raise AssertionError('Within-group change categories inconsistent')
    return values


def read_original_artifact(z: ZipFile):
    if 'receipt.json' not in z.namelist():
        raise ValueError('Original source receipt missing')
    orig = json.loads(z.read('receipt.json'))
    if orig.get('source_version') != 'Annual_NLCD_Collection_1.0_CU_C1V0' or orig.get('status') != 'all_three_years_raw_C1V0_pixels_available_environment_only':
        raise ValueError('Wrong collection, incomplete source, or noncategorical original')
    data = {}
    ref_transform = None
    ref_shape = None
    for year in YEARS:
        name = f'{RASTER_PREFIX}{year}_iowa_360417.tif'
        raw = z.read(name)
        if sha256(raw) != AUTHORITATIVE_SHA[year] or sha256(raw) != orig['years'][str(year)]['data_sha256']:
            raise ValueError('Original raster bytes drifted from source provenance')
        with MemoryFile(raw) as mem:
            with mem.open() as src:
                if src.count != 1 or src.crs is None or src.crs.to_epsg() != 5070:
                    raise ValueError('Unexpected categorical raster projection/band count')
                if not np.allclose(src.res, (30,30), rtol=0,atol=1e-7):
                    raise ValueError('Not 30m raster')
                a = src.read(1).copy()
                group_classes(a)  # validates every pixel; rejects missing/unknown classes
                if ref_shape is None:
                    ref_shape = a.shape; ref_transform = src.transform
                elif ref_shape != a.shape or not np.allclose(tuple(ref_transform)[:6], tuple(src.transform)[:6], rtol=0, atol=1e-9):
                    raise ValueError('Raster grid drift across years')
                if src.nodata is not None and np.any(a==src.nodata):
                    raise ValueError('Unresolved nodata pixels, cannot infer change')
                data[year] = a
    return orig, data, ref_transform


def site_summary(data: dict, affine, stations: pd.DataFrame):
    if sorted(data) != list(YEARS):
        raise ValueError('All prespecified years required')
    if set(stations.site_id.astype(str)) != {str(i) for i in range(7271, 7281)} or len(stations)!=10:
        raise ValueError('Unexpected station set')
    if not stations.historical_site_verified.astype(str).str.lower().eq('false').all():
        raise ValueError('Do not silently label post-study-map sites historically verified')
    rr,cc=np.indices(data[2004].shape)
    xx=affine.c+(cc+.5)*affine.a
    yy=affine.f+(rr+.5)*affine.e
    coords_x,coords_y=project('EPSG:4326','EPSG:5070',stations.longitude.to_list(),stations.latitude.to_list())
    rows=[]
    for s,x,y in zip(stations.itertuples(index=False),coords_x,coords_y):
        for radius in RADII:
            inside=(xx-x)**2+(yy-y)**2<=radius**2
            pixels=int(inside.sum())
            if pixels < 30:
                raise ValueError('Site too close to raster edge or outside requested extent')
            rec={'site_id':str(s.site_id),'stop_number':int(s.stop_number),
                 'radius_m':radius,'circle_pixels':pixels}
            for year in YEARS:
                grouped=group_classes(data[year]); annual=grouped[inside]
                for group,name in GROUP_NAME.items():
                    rec[f'{year}_{name}_pct']=float(100*(annual==group).mean())
            for old,new in PAIRS:
                metrics=classify_transition(data[old],data[new],inside)
                key=f'{old}_{new}'
                for name,value in metrics.items():
                    if name != 'valid_pixels':
                        rec[f'{key}_{name}']=value
                rec[f'{key}_fine_change_pct']=100*metrics['fine_class_changed_pixels']/pixels
                rec[f'{key}_between_group_change_pct']=100*metrics['between_group_changed_pixels']/pixels
                rec[f'{key}_within_group_change_pct']=100*metrics['within_group_changed_pixels']/pixels
            rows.append(rec)
    return pd.DataFrame(rows).sort_values(['radius_m','stop_number']).reset_index(drop=True)


def make_report(path: Path, stops_path: Path):
    if sha256(stops_path.read_bytes()) != STOP_CSV_SHA:
        raise ValueError('Historical-map coordinate list drift')
    stops=pd.read_csv(stops_path,dtype={'route_id':str,'site_id':str})
    if len(stops)!=10 or not stops.route_id.eq(ROUTE).all():
        raise ValueError('Source-only AOI identity drift')
    with ZipFile(path) as z:
        receipt, rasters, transform=read_original_artifact(z)
    df=site_summary(rasters, transform, stops)
    levels={}
    for radius,g in df.groupby('radius_m'):
        k=f'2004_2014'
        fine=f'{k}_fine_change_pct';between=f'{k}_between_group_change_pct'
        levels[str(radius)]={
          'n_sites':len(g),
          'mean_fine_change_pct_equal_site':float(g[fine].mean()),
          'mean_between_group_change_pct_equal_site':float(g[between].mean()),
          'n_sites_any_forest_loss':int(g[f'{k}_forest_loss_pixels'].gt(0).sum()),
          'n_sites_any_forest_to_developed':int(g[f'{k}_forest_to_developed_pixels'].gt(0).sum()),
          'n_sites_any_forest_to_agriculture':int(g[f'{k}_forest_to_agriculture_pixels'].gt(0).sum()),
          'n_sites_any_between_group_change':int(g[f'{k}_between_group_changed_pixels'].gt(0).sum()),
          'source_pixels_nominally_valid':bool(g.circle_pixels.ge(30).all()),
          'overlapping_buffers_not_independent':True,
        }
    report={
      'analysis':'iowa_360417_C1V0_functional_land_cover_reaudit_v18',
      'source_name':'Annual_NLCD_Collection_1.0_CU_C1V0',
      'not_collection_1_2':True,
      'year_source_shas':{str(y):AUTHORITATIVE_SHA[y] for y in YEARS},
      'original_action_artifact':SOURCE_ARTIFACT,
      'original_archive_sha256':sha256(path.read_bytes()),
      'original_stop_source_sha256':sha256(stops_path.read_bytes()),
      'study_route':ROUTE,
      'years':YEARS,
      'nominal_buffer_m':RADII,
      'coarse_class_dictionary':GROUP_NAME,
      'results_by_radius':levels,
      'n_historical_physical_sites_independently_field_verified':0,
      'frog_counts_or_acoustic_outcomes_read':False,
      'interpretation':'Environment-only categorical landcover screening; mapping classes and original station identities require independent confirmation before frog response analysis',
      'site_rows':df.to_dict(orient='records'),
    }
    return report,df


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--artifact',required=True)
    parser.add_argument('--source-stops',required=True)
    parser.add_argument('--out-json',required=True)
    parser.add_argument('--out-csv',required=True)
    a=parser.parse_args()
    result,table=make_report(Path(a.artifact),Path(a.source_stops))
    dest=Path(a.out_json);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    csv=Path(a.out_csv);csv.parent.mkdir(parents=True,exist_ok=True)
    table.to_csv(csv,index=False)
    print(json.dumps({k:v for k,v in result.items() if k!='site_rows'},sort_keys=True,indent=2))

if __name__=='__main__':main()
