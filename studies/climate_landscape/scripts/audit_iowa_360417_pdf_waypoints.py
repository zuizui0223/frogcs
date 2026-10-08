#!/usr/bin/env python3
"""Frozen 360417 original-USGS-vs-Iowa-DNR coordinate crosscheck.

NO Counts.csv / land pixels. Published 2021 PDF cannot demonstrate historical
(2001-2015) station continuity, even when the numerical coordinates agree.
"""
from __future__ import annotations
import argparse,hashlib,json,re,urllib.parse,urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import fitz
from audit_coordinates import audit as geometry_audit,km
from build_naamp_observation_panel import make as observation_panel,SOURCE_PINS
from run_public_naamp_feasibility import COORD_SHA

ROUTE='360417'
STATE='Iowa'
URL='https://www.iowadnr.gov/media/1999/download?inline='
PDF_SHA='74c37c9ed7c3aaccd0a3eb3a0f6ab3834d404313380b8819987f2822add1c1b0'
THRESHOLD_M=(100.0,250.0)
COORD_ROW=re.compile(r'^\s*(10|[1-9])\s+\d+(?:\.\d+)?\s+(Warren|Madison)\s+(4[01]\.\d{4,})\s+(-9[0-7]\.\d{4,})(?:\s|$)')

def waypoint_table_from_pages(pages:list[str])->pd.DataFrame:
    rows=[]
    for pn,page in enumerate(pages,1):
        for ln,line in enumerate(page.splitlines(),1):
            m=COORD_ROW.match(line.strip())
            if m:
                rows.append({'stop_no':int(m.group(1)), 'county':m.group(2),
                     'latitude':float(m.group(3)),'longitude':float(m.group(4)),
                     'source_page':pn,'source_line':ln})
    x=pd.DataFrame(rows)
    if (len(x)!=10 or sorted(x.stop_no.tolist())!=list(range(1,11)) or
        x.stop_no.duplicated().any() or not x.latitude.between(40,44).all() or
        not x.longitude.between(-97,-89).all()):
        raise ValueError('No unambiguous 10-stop coordinate table; do not map guesses')
    return x.sort_values('stop_no').reset_index(drop=True)

def compare_original(runs,stops,coords,waypoints):
    panel,cohort=observation_panel(runs,stops)
    chosen=panel[(panel.state==STATE)&(panel.route_number==ROUTE)].copy()
    if chosen.empty:
        raise ValueError('Route not in published NAAMP standardized history')
    chosen['stop_no']=pd.to_numeric(chosen.stop_number,errors='raise').astype(int)
    if not chosen.stop_no.between(1,10).all():
        raise ValueError('Stop numbers not 1 to 10')
    counts=chosen.groupby('stop_no').site_id.nunique()
    reverse=chosen.groupby('site_id').stop_no.nunique()
    if len(counts)!=10:
        raise ValueError('Historic route does not have all 10 stop numbers')
    bad=set(counts[counts.ne(1)].index)
    bad|=set(chosen.loc[chosen.site_id.isin(reverse[reverse.ne(1)].index),'stop_no'])
    good=chosen[~chosen.stop_no.isin(bad)].drop_duplicates(['stop_no','site_id'])[['stop_no','site_id']]
    if good.stop_no.duplicated().any():raise ValueError('Inconsistent historical stop identity')
    geo,gsummary=geometry_audit(coords)
    geo=geo[geo.route_id.eq(ROUTE)][['site_id','latitude','longitude','geometry_qc_status']]
    if geo.site_id.duplicated().any():raise ValueError('Duplicate USGS SiteID')
    merged=waypoints.merge(good,on='stop_no',how='left',validate='one_to_one')
    merged=merged.merge(geo,on='site_id',how='left',validate='one_to_one',suffixes=('_dnr','_usgs'))
    detail=[]
    for q in merged.itertuples(index=False):
        valid=(pd.notna(q.site_id) and pd.notna(q.latitude_usgs) and
               q.geometry_qc_status=='pass_unverified')
        distance=(float(km(q.latitude_dnr,q.longitude_dnr,
                   q.latitude_usgs,q.longitude_usgs)*1000) if valid else None)
        detail.append({'stop_no':int(q.stop_no),
          'historical_site_id':str(q.site_id) if pd.notna(q.site_id) else None,
          'dnr_latitude':float(q.latitude_dnr),
          'dnr_longitude':float(q.longitude_dnr),
          'usgs_latitude':float(q.latitude_usgs) if pd.notna(q.latitude_usgs) else None,
          'usgs_longitude':float(q.longitude_usgs) if pd.notna(q.longitude_usgs) else None,
          'usgs_geometry_qc':str(q.geometry_qc_status) if pd.notna(q.geometry_qc_status) else 'missing',
          'distance_m':distance,
          'within_100m':bool(distance is not None and distance<=100.0),
          'within_250m':bool(distance is not None and distance<=250.0)})
    d=[z['distance_m'] for z in detail if z['distance_m'] is not None]
    return {'analysis':'iowa_360417_original_usgs_state_map_coordinate_agreement_v1_5',
       'study_period':'2001-2015',
       'comparison_map_created_after_study':True,
       'n_source_eligible_runs':int(chosen.run_id.nunique()),
       'n_source_eligible_years':int(chosen.survey_year.nunique()),
       'n_historic_stop_positions_with_ambiguous_siteid':len(bad),
       'n_dnr_map_stops':len(waypoints),
       'n_comparable_coordinate_stops':len(d),
       'n_within_100m':sum(x['within_100m'] for x in detail),
       'n_within_250m':sum(x['within_250m'] for x in detail),
       'median_distance_m':float(np.median(d)) if d else None,
       'max_distance_m':float(np.max(d)) if d else None,
       'n_historical_field_sites_independently_verified':0,
       'did_not_use_frog_counts':True,'did_not_use_satellite_landcover_pixels':True,
       'status':'MAP_VS_ARCHIVE_COORDINATE_AGREEMENT_ONLY' if d else 'NO_COMPARABLE_COORDINATES',
       'site_rows':detail,
       'interpretation':'Published contemporary map and archived coordinates may share source; no historical field continuity shown.'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fetch_pdf():
    req=urllib.request.Request(URL,headers={'User-Agent':'frogcs-iowa-crosscheck-2026/1.5','Accept':'application/pdf'})
    with urllib.request.urlopen(req,timeout=90) as response:
        u=urllib.parse.urlparse(response.geturl())
        if u.scheme!='https' or u.hostname not in ('www.iowadnr.gov','iowadnr.gov'):
            raise ValueError('State PDF redirected off original official host')
        payload=response.read(12_000_001)
    if hashlib.sha256(payload).hexdigest()!=PDF_SHA or not payload.startswith(b'%PDF-'):
        raise ValueError('Official PDF hash mismatch; do not silently change reference')
    return payload

def main():
    ap=argparse.ArgumentParser()
    for name in ('runs','stops','coords','out'):
        ap.add_argument('--'+name,required=True)
    ap.add_argument('--image-dir',default=None)
    a=ap.parse_args()
    dig={'Runs.csv':sha(a.runs),'Stops.csv':sha(a.stops),'Coordinates.csv':sha(a.coords)}
    if dig!={**SOURCE_PINS,'Coordinates.csv':COORD_SHA}:
        raise ValueError('Original USGS NAAMP files differ from pinned source digests')
    pdf=fetch_pdf()
    with fitz.open(stream=pdf,filetype='pdf') as f:
        pages=[p.get_text('text',sort=True) for p in f]
        if a.image_dir:
            outimg=Path(a.image_dir);outimg.mkdir(parents=True,exist_ok=True)
            for i in (3,4):
                if i<len(f):
                    f[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False).save(outimg/f'iowa_360417_pdf_page_{i+1}.png')
    waypoints=waypoint_table_from_pages(pages)
    record=compare_original(pd.read_csv(a.runs,dtype=str,keep_default_na=False),
           pd.read_csv(a.stops,dtype=str,keep_default_na=False),
           pd.read_csv(a.coords,dtype={'RouteNumber':str,'SiteID':str}),waypoints)
    record.update({'source_sha256':{**dig,'iowa_dnr_pdf':PDF_SHA},
                   'official_dnr_document_url':URL,'pdf_page_count':len(pages),
                   'coordinate_table_pages':sorted(set(int(v) for v in waypoints.source_page))})
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k!='site_rows'},indent=2,sort_keys=True))

if __name__=='__main__':main()
