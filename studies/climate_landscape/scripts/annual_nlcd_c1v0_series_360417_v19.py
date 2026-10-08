#!/usr/bin/env python3
"""Source-only Iowa 360417 complete 2001-2015 Annual NLCD C1V0 raster series.

Outcome-blind post-v1.8 exploratory expansion based on the fixed survey calendar,
not on inspecting frog species responses. Nothing here validates physical 2001-15
site identity or the newer C1V2 collection / classification confidence.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np,pandas as pd
from rasterio.io import MemoryFile
from rasterio.warp import transform as project

SCRIPTS=Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:sys.path.insert(0,str(SCRIPTS))
import arcgis_c1v0_full_aoi as source
from audit_c1v0_ecological_class_change_v18 import group_classes,classify_transition

YEARS=tuple(range(2001,2016))
ROUTE='360417'
RADII=(250,1000)
STOP_SOURCE=Path(__file__).resolve().parents[1]/'reference_routes/iowa_dnr_360417_source_only_stops_v16.csv'
STOP_SHA='8b7be934dc32aa71791b4e6c38295d25cbcebb66f2f6ab39714d41ce7b65f227'
BASELINE='Annual_NLCD_Collection_1.0_CU_C1V0'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def request_verified_year(year:int)->tuple[bytes,dict]:
    if year not in YEARS:raise ValueError('Year outside prespecified 2001–2015 source calendar')
    identity,qsha=source.source_identity_for_year(year)
    rule={'mosaicMethod':'esriMosaicByAttribute',
          'where':f'OBJECTID={identity["OBJECTID"]} AND Year={year}',
          'sortField':'Year','sortValue':year,'ascending':True}
    params={'bbox':','.join(str(z) for z in source.BBOX),'bboxSR':'5070',
            'imageSR':'5070','size':f'{source.WIDTH},{source.HEIGHT}',
            'format':'tiff','pixelType':'U8','interpolation':'RSP_NearestNeighbor',
            'mosaicRule':json.dumps(rule,separators=(',',':')),
            'renderingRule':json.dumps({'rasterFunction':'None'}),'f':'image'}
    raw,mime=source.source_request('/exportImage',params)
    if raw[:4] not in (b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+'):
        raise ValueError(f'Invalid year {year} raster response, not TIFF')
    return raw,{'dataset_name':identity['Name'],'product_version':identity['Version'],
                'object_id':identity['OBJECTID'],'query_sha256':qsha,
                'tiff_sha256':sha(raw),'bytes':len(raw),'mime_type':mime,
                'no_frog_outcome_access':True}


def prepare_series(raw_by_year:dict[int,bytes]):
    if sorted(raw_by_year)!=list(YEARS):
        raise ValueError('Incomplete annual fixed-study-calendar raster series')
    arrays={};metadata={}
    for year,raw in raw_by_year.items():
        with MemoryFile(raw) as mem:
            with mem.open() as src:
                if src.count!=1 or src.crs is None or src.crs.to_epsg()!=5070:
                    raise ValueError('Wrong categorical source band/CRS')
                if src.width!=source.WIDTH or src.height!=source.HEIGHT:
                    raise ValueError('Raster extent changed across years')
                tr=src.transform
                if (not np.allclose([tr.a,tr.b,tr.c,tr.d,tr.e,tr.f],
                    [30,0,source.BBOX[0],0,-30,source.BBOX[3]],rtol=0,atol=1e-8)):
                    raise ValueError('Raster no longer on common 30m EPSG:5070 grid')
                img=src.read(1)
                group_classes(img)  # all cells must be known Annual NLCD classes
                if src.nodata is not None and np.any(img==src.nodata):
                    raise ValueError('Nodata present in frozen AOI raster')
                arrays[year]=img
                metadata[str(year)]={'pixel_codes':sorted(map(int,np.unique(img))),
                     'n_valid_pixels':int(img.size)}
    return arrays,metadata


def fixed_site_masks(stops:pd.DataFrame)->dict[tuple[str,int],np.ndarray]:
    if not len(stops)==10 or sorted(stops.stop_number.astype(int))!=list(range(1,11)):
        raise ValueError('Incorrect ten-stop document')
    if not set(stops.site_id.astype(str))=={str(i) for i in range(7271,7281)}:
        raise ValueError('Unexpected physical SiteID mapping')
    if not stops.historical_site_verified.astype(str).str.lower().eq('false').all():
        raise ValueError('Post-study map cannot verify historical stations')
    lat=stops.latitude.astype(float).tolist();lon=stops.longitude.astype(float).tolist()
    px,py=project('EPSG:4326','EPSG:5070',lon,lat)
    rr,cc=np.indices((source.HEIGHT,source.WIDTH))
    xx=source.BBOX[0]+(cc+.5)*30
    yy=source.BBOX[3]-(rr+.5)*30
    masks={}
    for s,x,y in zip(stops.itertuples(index=False),px,py):
        for rad in RADII:
            if (x-rad<source.BBOX[0] or x+rad>source.BBOX[2] or
                y-rad<source.BBOX[1] or y+rad>source.BBOX[3]):
                raise ValueError('Buffer extends outside verified original raster crop')
            mask=(xx-x)**2+(yy-y)**2<=rad**2
            if int(mask.sum())<30:raise ValueError('Buffer does not cover enough pixels')
            masks[(str(s.site_id),rad)]=mask
    return masks


def summarize_annual(arrays:dict,stops:pd.DataFrame):
    if sorted(arrays)!=list(YEARS):raise ValueError('Annual sequence incomplete')
    masks=fixed_site_masks(stops)
    annual=[]; adjacent=[]
    for (site,rad),mask in sorted(masks.items(),key=lambda t:(t[0][1],int(t[0][0]))):
        n=int(mask.sum())
        for yr in YEARS:
            grouped=group_classes(arrays[yr])[mask]
            annual.append({'site_id':site,'stop_number':int(site)-7270,
                 'radius_m':rad,'year':yr,'nominal_pixels':n,
                 'forest_pct':float(100*(grouped==5).mean()),
                 'agriculture_pct':float(100*(grouped==8).mean()),
                 'developed_pct':float(100*(grouped==3).mean()),
                 'wetland_pct':float(100*(grouped==9).mean()),
                 'open_water_pct':float(100*(grouped==1).mean()),
                 'historic_field_station_verified':False})
        for prev,next_year in zip(YEARS[:-1],YEARS[1:]):
            before=arrays[prev];after=arrays[next_year]
            r=classify_transition(before,after,mask)
            # Conversion persisting into the following annual classification;
            # 2015 endpoint cannot be persistence-scored without future data.
            following=arrays.get(next_year+1)
            persistence=None
            if following is not None:
                beforeg=group_classes(before);afterg=group_classes(after)
                nextg=group_classes(following)
                persistence=int((mask&(beforeg!=afterg)&(afterg==nextg)).sum())
            adjacent.append({'site_id':site,'stop_number':int(site)-7270,
                  'radius_m':rad,'from_year':prev,'to_year':next_year,
                  'nominal_pixels':n,
                  'fine_class_change_pct':100*r['fine_class_changed_pixels']/n,
                  'ecological_group_change_pct':100*r['between_group_changed_pixels']/n,
                  'agriculture_81_82_swap_pixels':r['agricultural_81_82_changed_pixels'],
                  'forest_loss_pixels':r['forest_loss_pixels'],
                  'forest_gain_pixels':r['forest_gain_pixels'],
                  'forest_to_agriculture_pixels':r['forest_to_agriculture_pixels'],
                  'forest_to_developed_pixels':r['forest_to_developed_pixels'],
                  'persisted_group_change_1yr_pixels':persistence,
                  'persisted_group_change_not_observed_for_last_year':next_year==YEARS[-1]})
    return pd.DataFrame(annual),pd.DataFrame(adjacent)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-dir',required=True)
    args=p.parse_args()
    outdir=Path(args.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    stopsraw=STOP_SOURCE.read_bytes()
    if sha(stopsraw)!=STOP_SHA:raise ValueError('Station list source altered')
    stops=pd.read_csv(STOP_SOURCE,dtype={'route_id':str,'site_id':str})
    if not stops.route_id.eq(ROUTE).all():raise ValueError('Wrong route')
    summary={'analysis':'iowa360417_annual_nlcd_C1V0_2001_2015_yearly_sources_v19',
            'status':'PARTIAL_SOURCE_ONLY', 'original_collection':'C1V0_not_C1V2',
            'years_requested':list(YEARS), 'source_service':source.BASE,
            'source_station_sha256':STOP_SHA,
            'n_historic_physically_verified_stops':0,'frog_calling_outcomes_read':False,
            'classification_confidence_available':False,
            'not_preregistered_before_2004_2009_2014_readback':True,
            'years':{}}
    allraw={}
    try:
        for year in YEARS:
            raw,meta=request_verified_year(year)
            path=outdir/f'annual_c1v0_{year}_360417.tif'
            path.write_bytes(raw)
            allraw[year]=raw
            summary['years'][str(year)]=meta
            (outdir/'source_receipt.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
            print(json.dumps({'year':year,'source_tiff_sha256':meta['tiff_sha256'],'bytes':len(raw)}),flush=True)
        a,meta=prepare_series(allraw)
        per_year,between=summarize_annual(a,stops)
        per_year.to_csv(outdir/'annual_site_landcover_2001_2015.csv',index=False)
        between.to_csv(outdir/'year_to_year_site_transitions_2001_2015.csv',index=False)
        summary['year_pixel_metadata']=meta
        summary.update({'status':'COMPLETE_15_YEAR_SOURCE_ONLY_LANDCOVER',
           'n_station_buffer_annual_rows':len(per_year),'n_station_buffer_adjacent_year_rows':len(between),
           'same_30m_pixel_grid_all_years':True,'no_observed_frog_or_breeding_results':True})
        (outdir/'source_receipt.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'status':summary['status'],'n_years':len(a),'annual_rows':len(per_year),'pairs':len(between)}),flush=True)
    except Exception as e:
        summary.update({'status':'INCOMPLETE_SOURCE_COLLECTION',
             'error_type':type(e).__name__,'error_message':str(e)[:350]})
        (outdir/'source_receipt.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        raise

if __name__=='__main__':main()
