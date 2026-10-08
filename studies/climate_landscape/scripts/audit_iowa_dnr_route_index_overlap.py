#!/usr/bin/env python3
"""Outcome-blind compatibility check for Iowa DNR route IDs and historical USGS NAAMP.

Reads an independently published CURRENT Iowa DNR map index and official
checksum-pinned 2001-2015 USGS NAAMP Runs/Stops/coordinate metadata only.
An identical six-digit code does not prove identical station locations,
map-source independence, nor historical field-site continuity.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

import pandas as pd

from build_naamp_observation_panel import SOURCE_PINS, make as make_panel
from run_public_naamp_feasibility import COORD_SHA

SOURCE_URL='https://www.iowadnr.gov/programs-services/volunteer-opportunities/wildlife-monitoring/frogs-and-toads/survey'
MIN_DOCUMENTED_SIX_DIGIT_ROUTES=20


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks=[]
        self.ignored_depth=0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ('script','style'):
            self.ignored_depth+=1

    def handle_endtag(self, tag):
        if tag.lower() in ('script','style') and self.ignored_depth:
            self.ignored_depth-=1

    def handle_data(self, data):
        if not self.ignored_depth:
            self.chunks.append(data)


def parse_index(raw: bytes):
    if len(raw)<2000:
        raise ValueError('Iowa DNR page response too short for a map index')
    doc=raw.decode('utf-8-sig',errors='strict')
    if '<html' not in doc.lower():
        raise ValueError('No HTML in Iowa DNR page response')
    parser=_VisibleText()
    parser.feed(doc)
    rendered=' '.join(parser.chunks)
    # Six-digit NAAMP-compatible codes, not short local DNR volunteer routes.
    candidates=set(re.findall(r'\bRoute\s+ID\s*(\d{6})\b',rendered,re.I))
    if len(candidates)<MIN_DOCUMENTED_SIX_DIGIT_ROUTES:
        raise ValueError(f'Iowa DNR six-digit route-map coverage too small ({len(candidates)})')
    return sorted(candidates)


def overlap(runs:pd.DataFrame,stops:pd.DataFrame,coords:pd.DataFrame,published_routes):
    documented=set(str(x).strip() for x in published_routes)
    if any(not re.fullmatch(r'\d{6}',x) for x in documented):
        raise ValueError('Malformed six-digit DNR route key')
    if len(documented)<MIN_DOCUMENTED_SIX_DIGIT_ROUTES:
        raise ValueError('Insufficient independently documented DNR routes')
    panel,cohort=make_panel(runs,stops)
    route=panel.loc[panel.state.eq('Iowa')]
    eligible=set(route.route_number.astype(str))
    allcoords=set(coords.RouteNumber.astype('string').str.strip().dropna().astype(str))
    combined=sorted(documented & eligible)
    coordinate_hits=sorted(documented & allcoords)
    perroute=(route.groupby('route_number').agg(
        n_runs=('run_id','nunique'),
        n_years=('survey_year','nunique'),
        n_site_ids=('site_id','nunique'),
        n_stop_visits=('site_id','size')))
    routes=[]
    for rid in combined:
        r=perroute.loc[rid]
        routes.append({'route_id':rid,'n_runs':int(r.n_runs),'n_years':int(r.n_years),
                       'n_site_ids':int(r.n_site_ids),'n_stop_visits':int(r.n_stop_visits),
                       'source_coordinate_route_present':rid in allcoords})
    return {
        'analysis':'iowa_dnr_present_index_vs_historic_naamp_route_key_overlap_v0_1',
        'n_published_six_digit_dnr_route_codes':len(documented),
        'n_standardized_2001_2015_iowa_naamp_routes':len(eligible),
        'n_dnr_routes_matching_all_usgs_coordinate_route_ids':len(coordinate_hits),
        'n_dnr_routes_matching_standardized_naamp_iowa_cohort':len(combined),
        'coordinate_overlap_route_ids':coordinate_hits,
        'standardized_cohort_overlap_routes':routes,
        'first_metadata_only_eligible_match':combined[0] if combined else None,
        'reference_route_360411_in_standardized_cohort':'360411' in eligible,
        'frog_counts_csv_read':False,
        'n_historical_field_sites_independently_verified':0,
        'note':'A shared route code is NOT site-level validation; current DNR index may postdate all 2001-2015 surveys and may not be the same monitoring cohort. No aquatic/landcover or frog outcome used.',
        'eligible_panel_cohort':cohort,
    }


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch_index(url=SOURCE_URL):
    if url!=SOURCE_URL:raise ValueError('Only the fixed official Iowa DNR route index is authorized')
    req=urllib.request.Request(url,headers={'User-Agent':'frogcs-naamp-route-identity-audit/1.4','Accept':'text/html'})
    with urllib.request.urlopen(req,timeout=60) as r:
        final=r.geturl()
        if not final.startswith('https://www.iowadnr.gov/'):
            raise ValueError('Iowa DNR page redirected outside its official host')
        return r.read()


def main():
    ap=argparse.ArgumentParser()
    for key in ('runs','stops','coords','out'):
        ap.add_argument('--'+key,required=True)
    ap.add_argument('--official-index-html',help='Saved exact HTML of current Iowa DNR official index; use no other host')
    args=ap.parse_args()
    pin={'Runs.csv':sha(args.runs),'Stops.csv':sha(args.stops),'Coordinates.csv':sha(args.coords)}
    if pin!={**SOURCE_PINS,'Coordinates.csv':COORD_SHA}:
        raise ValueError('USGS NAAMP metadata source hash drift')
    if args.official_index_html:
        index=Path(args.official_index_html).read_bytes()
    else:index=fetch_index()
    routes=parse_index(index)
    result=overlap(pd.read_csv(args.runs,dtype=str,keep_default_na=False),
                   pd.read_csv(args.stops,dtype=str,keep_default_na=False),
                   pd.read_csv(args.coords,dtype={'RouteNumber':str,'SiteID':str}),routes)
    result['source_sha256']={**pin,'iowa_dnr_current_index_html':hashlib.sha256(index).hexdigest()}
    result['source_url']=SOURCE_URL
    result['n_route_codes_parsed_from_current_html']=len(routes)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,default=int)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))},indent=2,sort_keys=True))


if __name__=='__main__':main()
