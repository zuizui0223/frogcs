#!/usr/bin/env python3
"""Read only official Annual NLCD raw pixels for the 360417 source-only environmental pilot.

This does not use NAAMP calling data or verify historical fixed-station continuity.
Failures (wrong source, WCS response, projection, year, code) fail closed.
"""
from __future__ import annotations
import argparse, hashlib, json, urllib.parse, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform as project

ROOT = Path(__file__).resolve().parents[1]
STOPS = ROOT / 'reference_routes/iowa_dnr_360417_source_only_stops_v16.csv'
BASE_URL = 'https://dmsdata.cr.usgs.gov/geoserver/mrlc_Land-Cover-Native_conus_year_data/wcs'
COVERAGE = 'mrlc_Land-Cover-Native_conus_year_data:Land-Cover-Native_conus_year_data'
YEARS = (2004, 2009, 2014)
BBOX = (179220, 2044410, 184320, 2056680)
CLASSES = {11, 12, 21, 22, 23, 24, 31, 41, 42, 43, 52, 71, 81, 82, 90, 95}
FOREST = {41, 42, 43}; DEVELOPED = {21, 22, 23, 24}; AGRICULTURE = {81, 82}
WETLAND = {90, 95}; WATER = {11}
MAX_BYTES = 6_000_000


def get_coverage(year):
    if year not in YEARS:
        raise ValueError('Year not frozen')
    params = {
        'service': 'WCS', 'version': '1.0.0', 'request': 'GetCoverage',
        'coverage': COVERAGE, 'CRS': 'EPSG:5070',
        'BBOX': ','.join(map(str, BBOX)),
        'time': f'{year}-01-01T00:00:00.000Z', 'format': 'image/geotiff',
        'resx': '30', 'resy': '30',
    }
    url = BASE_URL + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'frogcs-nlcd-direct-source-1.6',
                                                'Accept': 'image/tiff, image/geotiff'})
    with urllib.request.urlopen(req, timeout=155) as response:
        data = response.read(MAX_BYTES + 1)
        host = urllib.parse.urlparse(response.geturl()).hostname
        content_type = response.headers.get('Content-Type', '')
    if host != 'dmsdata.cr.usgs.gov' or len(data) > MAX_BYTES:
        raise ValueError('Unexpected source host or overlarge response')
    if data[:4] not in (b'II*\x00', b'MM\x00*', b'II+\x00', b'MM\x00+'):
        raise ValueError('Official WCS response not GeoTIFF; starts ' + data[:180].decode('utf8', 'replace'))
    return data, {'http_content_type': content_type, 'requested_time': params['time'],
                  'host': host, 'request_path': urllib.parse.urlparse(url).path}


def inspect_tif(path):
    with rasterio.open(path) as src:
        if src.count != 1 or src.crs is None or src.crs.to_epsg() != 5070:
            raise ValueError('Not a single-band EPSG:5070 categorical source raster')
        if not all(abs(v - 30) < 0.1 for v in src.res):
            raise ValueError('Not 30m native source pixels')
        if abs(src.transform.b) > 1e-9 or abs(src.transform.d) > 1e-9:
            raise ValueError('Rotated raster cannot be compared without preregistered resampling')
        image = src.read(1)
        valid = np.ones_like(image, dtype=bool) if src.nodata is None else image != src.nodata
        codes = set(map(int, np.unique(image[valid])))
        if not codes or not codes.issubset(CLASSES):
            raise ValueError('WCS did not return raw Annual NLCD classes: ' + str(sorted(codes)))
        counts = {str(int(c)): int(n) for c, n in zip(*np.unique(image[valid], return_counts=True))}
        record = {'crs': str(src.crs), 'shape': list(image.shape),
                  'transform': list(src.transform)[:6], 'nodata': src.nodata,
                  'pixel_codes': sorted(codes), 'histogram': counts, 'bands': src.count,
                  'valid_pixel_fraction': float(valid.mean())}
        return image, src.transform, valid, record


def summarize_pixels(layers, stations):
    if sorted(layers) != list(YEARS):
        raise ValueError('Not all three years available')
    base_shape = layers[2004][0].shape
    base_transform = np.array(list(layers[2004][1])[:6])
    for yr in YEARS[1:]:
        if layers[yr][0].shape != base_shape or not np.allclose(
            list(layers[yr][1])[:6], base_transform, atol=1e-8, rtol=0
        ):
            raise ValueError('Rasters are not precisely same-pixel aligned')
    rows, cols = np.indices(base_shape)
    aff = layers[2004][1]
    xx = aff.c + (cols + .5) * aff.a
    yy = aff.f + (rows + .5) * aff.e
    cx, cy = project('EPSG:4326', 'EPSG:5070',
                     stations.longitude.to_list(), stations.latitude.to_list())
    out = []
    for station, x, y in zip(stations.itertuples(index=False), cx, cy):
        for radius in (250, 1000):
            disk = ((xx-x)**2+(yy-y)**2) <= radius**2
            available = int(disk.sum())
            if available < 30:
                raise ValueError('Site falls outside or is too small for the requested grid')
            result = {'route_id': '360417', 'site_id': str(station.site_id),
                      'stop_number': int(station.stop_number), 'radius_m': radius,
                      'circle_pixels': available, 'physical_station_history_verified': False,
                      'years': {}, 'transitions': {}}
            for year in YEARS:
                arr, _, good, _ = layers[year]
                usable = disk & good
                n = int(usable.sum())
                denom = max(n, 1)
                result['years'][str(year)] = {
                    'valid_pixels': n, 'valid_fraction': n/available,
                    'forest_frac_valid': float((np.isin(arr, list(FOREST)) & usable).sum()/denom) if n else None,
                    'developed_frac_valid': float((np.isin(arr, list(DEVELOPED)) & usable).sum()/denom) if n else None,
                    'agriculture_frac_valid': float((np.isin(arr, list(AGRICULTURE)) & usable).sum()/denom) if n else None,
                    'wetland_frac_valid': float((np.isin(arr, list(WETLAND)) & usable).sum()/denom) if n else None,
                }
            for early, late in ((2004,2009),(2009,2014),(2004,2014)):
                prev, _, pval, _ = layers[early]
                new, _, nval, _ = layers[late]
                pair = disk & pval & nval
                npair = int(pair.sum())
                trans = {'pairwise_valid_pixels': npair,
                         'pairwise_valid_fraction': npair/available,
                         'passes_80percent_coverage': bool(npair >= 0.8*available)}
                if trans['passes_80percent_coverage']:
                    f0 = np.isin(prev, list(FOREST))
                    f1 = np.isin(new, list(FOREST))
                    trans.update({
                        'changed_category_pixels': int((pair & (prev!=new)).sum()),
                        'forest_loss_pixels': int((pair & f0 & ~f1).sum()),
                        'forest_gain_pixels': int((pair & ~f0 & f1).sum()),
                        'forest_to_developed_pixels': int((pair & f0 & np.isin(new, list(DEVELOPED))).sum()),
                        'forest_to_agriculture_pixels': int((pair & f0 & np.isin(new, list(AGRICULTURE))).sum()),
                    })
                result['transitions'][f'{early}_{late}'] = trans
            out.append(result)
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args()
    root=Path(args.output_dir);root.mkdir(parents=True,exist_ok=True)
    stations=pd.read_csv(STOPS,dtype={'route_id':str,'site_id':str})
    if len(stations)!=10 or sorted(stations.stop_number.to_list())!=list(range(1,11)) or \
       stations.historical_site_verified.astype(str).str.lower().ne('false').any():
        raise ValueError('Source-only 10-stop list not frozen')
    receipt = {'analysis':'iowa360417_official_annual_nlcd_WCS_pilot_v16',
               'status':'SOURCE_EXTRACTION_NOT_COMPLETE',
               'official_WCS_service':BASE_URL,'coverage':COVERAGE,
               'requested_years':list(YEARS),'bbox_epsg5070':list(BBOX),
               'source_station_table_sha256':hashlib.sha256(STOPS.read_bytes()).hexdigest(),
               'field_verified_historical_2001_2015_stops':0,
               'frog_calling_data_read':False,'collection_1_2_version_verified':False,
               'year_sources':{}}
    saved = {}
    for year in YEARS:
        try:
            raw, http=get_coverage(year)
            path=root/f'annual_nlcd_source_{year}_360417.tif'
            path.write_bytes(raw)
            image, transform, good, meta=inspect_tif(path)
            saved[year]=(image,transform,good,meta)
            receipt['year_sources'][str(year)]={'sha256':hashlib.sha256(raw).hexdigest(),
                'bytes':len(raw),'http':http,'raster':meta}
            print(json.dumps({'year':year,'image_bytes':len(raw),'pixel_codes':meta['pixel_codes']}),flush=True)
        except Exception as error:
            receipt['status']='WCS_SOURCE_FAILURE_OR_INVALID_RASTER'
            receipt['failed_year']=year
            receipt['failure_type']=type(error).__name__
            receipt['failure_details']=str(error)[:400]
            (root/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
            raise
    receipt['site_radii']=summarize_pixels(saved,stations)
    receipt['status']='THREE_YEAR_RAW_NLCD_LAND_COVER_PIXELS_READY_SOURCE_ONLY'
    (root/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':receipt['status'],'source_only_site_buffer_rows':len(receipt['site_radii'])}),flush=True)

if __name__=='__main__':main()
