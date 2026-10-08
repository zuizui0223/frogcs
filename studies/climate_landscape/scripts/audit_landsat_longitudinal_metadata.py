#!/usr/bin/env python3
"""Outcome-blind Landsat interannual scene availability audit for independent NAAMP study.

Source: frozen Earth-engine-free Microsoft Planetary Computer Landsat STAC
metadata artifact E3_NDMI_METADATA_COVERAGE_V0_1.json. No pixel values, frogs,
observer outcomes, or site-specific habitat variables are accessed.

IMPORTANT: route-level scene footprint does not verify physical station identity
or determine whether cloud-masked pixels support long-term land-cover analysis.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import zipfile
from pathlib import Path

SEASON_TOLERANCE_DAYS = 21
MAX_LOOKBACK_DAYS = 32
LONG_GAP_YEARS = 5
EARLY = range(2001, 2006)
LATE = range(2011, 2016)


def season_day(date: dt.date) -> int:
    """Comparable calendar-month/day index using non-leap 2001 (Feb 29 -> Feb 28)."""
    if date.month == 2 and date.day == 29:
        return (dt.date(2001, 2, 28) - dt.date(2001, 1, 1)).days
    return (dt.date(2001, date.month, date.day) - dt.date(2001, 1, 1)).days


def sensor(item_id: str) -> str:
    if item_id.startswith(('LT04_', 'LT05_')):
        return 'TM'
    if item_id.startswith('LE07_'):
        return 'ETM+'
    if item_id.startswith(('LC08_', 'LC09_')):
        return 'OLI'
    raise ValueError(f'unsupported sensor in scene {item_id}')


def check_source(obj: dict) -> list[dict]:
    expected = 'naamp_e3_ndmi_metadata_coverage_v0_1'
    if obj.get('analysis') != expected or obj.get('classification') != 'metadata_necessary_gate_pass':
        raise ValueError('Not frozen E3 metadata-necessary-gate-pass data')
    if obj.get('NDMI_values_read') or obj.get('pixel_QA_coverage_calculated') or obj.get('frog_endpoint_calculated'):
        raise ValueError('Requested response-blind metadata must not include pixel/outcome analyses')
    rows = obj.get('metadata_run_rows')
    if not isinstance(rows, list) or not rows:
        raise ValueError('No metadata rows')
    seen = set()
    out = []
    for row in rows:
        rid = str(row['RunID']).strip()
        route = str(row['route_cluster']).strip()
        if not rid or rid in seen or not route or ':' not in route:
            raise ValueError('Duplicate RunID or invalid route identity')
        seen.add(rid)
        date = dt.date.fromisoformat(row['survey_date'])
        if not 2001 <= date.year <= 2015:
            raise ValueError('Survey outside predeclared 2001–2015 period')
        if not row.get('resolved') or not row.get('all10_one_product_candidate'):
            raise ValueError('A metadata run lacks resolved common scene')
        cand = []
        for c in row.get('candidates', []):
            acquired = dt.date.fromisoformat(c['acquisition_date'])
            scene = str(c['item_id'])
            lag = (date - acquired).days
            if lag != int(c['lag_days']) or not 0 <= lag <= MAX_LOOKBACK_DAYS:
                raise ValueError('Future/out-of-window or mislabeled satellite scene')
            if c['footprint_check'] != 'polygon':
                raise ValueError('Require verified polygon footprint for longitudinal audit')
            cand.append({'scene': scene, 'acquired': acquired, 'sensor': sensor(scene), 'lag':lag})
        if not cand:
            raise ValueError('No valid source scene candidate')
        out.append({'run_id': rid, 'route': route, 'survey':date,
                    'year':date.year, 'season_day':season_day(date), 'scenes':cand})
    return out


def pair_possible_scene_match(a: dict, b: dict, season_days: int = SEASON_TOLERANCE_DAYS) -> tuple[bool, bool]:
    """Any common-sensor scene pair with near-matched calendar season?

    True means metadata-only scene candidates; NOT common pixel QA or NDMI.
    """
    same_sensor = False
    same_sensor_same_season = False
    for x in a['scenes']:
        for y in b['scenes']:
            if x['sensor'] == y['sensor']:
                same_sensor = True
                if abs(season_day(x['acquired']) - season_day(y['acquired'])) <= season_days:
                    same_sensor_same_season = True
    return same_sensor, same_sensor_same_season


def pair_dict(a: dict, b: dict, season_days: int = SEASON_TOLERANCE_DAYS) -> dict:
    assert a['route'] == b['route'] and a['year'] < b['year']
    both, comparable = pair_possible_scene_match(a, b, season_days)
    return {'route':a['route'], 'run_earlier':a['run_id'], 'run_later':b['run_id'],
            'year_earlier':a['year'], 'year_later':b['year'],
            'gap_years':b['year']-a['year'],
            'survey_season_shift_days':abs(a['season_day']-b['season_day']),
            'common_sensor_candidate':both,
            'common_sensor_season_scene_candidate':comparable,
            'n_scenes_earlier':len(a['scenes']), 'n_scenes_later':len(b['scenes'])}


def pairs_by_group(group: list[dict], y1: int, y2: int, season_days: int = SEASON_TOLERANCE_DAYS) -> list[dict]:
    """Greedy closest-season one-to-one within an exact pair of route-years."""
    a = [r for r in group if r['year'] == y1]
    b = [r for r in group if r['year'] == y2]
    options = [(abs(x['season_day']-y['season_day']), x['run_id'], y['run_id'], x, y)
               for x in a for y in b if abs(x['season_day']-y['season_day']) <= season_days]
    seen_a, seen_b = set(), set()
    matches = []
    for _, _, _, x, y in sorted(options):
        if x['run_id'] not in seen_a and y['run_id'] not in seen_b:
            matches.append(pair_dict(x,y,season_days))
            seen_a.add(x['run_id'])
            seen_b.add(y['run_id'])
    return matches


def longest_pair(group: list[dict], *, min_gap=LONG_GAP_YEARS, cross_era=False, season_days=SEASON_TOLERANCE_DAYS) -> dict | None:
    """Choose exactly one long-period comparison per route, outcome-blind."""
    possible = [(x,y) for x in group for y in group
                if x['year'] < y['year']
                and y['year']-x['year'] >= min_gap
                and (not cross_era or (x['year'] in EARLY and y['year'] in LATE))
                and abs(x['season_day']-y['season_day']) <= season_days]
    if not possible: return None
    x,y = sorted(possible, key=lambda p:(-(p[1]['year']-p[0]['year']),
                        abs(p[0]['season_day']-p[1]['season_day']),p[0]['run_id'],p[1]['run_id']))[0]
    return pair_dict(x,y,season_days)


def audit(obj:dict, *, season_days: int = SEASON_TOLERANCE_DAYS) -> tuple[dict,dict[str,list[dict]]]:
    if season_days not in (7, 14, 21):
        raise ValueError("Season tolerance must be preregistered 7/14/21-day sensitivity")
    rows = check_source(obj)
    byroute = collections.defaultdict(list)
    for r in rows: byroute[r['route']].append(r)
    annual, gap5, long_gap, across = [], [], [], []
    for route, group in sorted(byroute.items()):
        years = sorted({r['year'] for r in group})
        for y in years:
            if y+1 in years: annual += pairs_by_group(group,y,y+1,season_days)
            if y+5 in years: gap5 += pairs_by_group(group,y,y+5,season_days)
        one = longest_pair(group,season_days=season_days)
        if one is not None: long_gap.append(one)
        one = longest_pair(group,min_gap=6,cross_era=True,season_days=season_days)
        if one is not None: across.append(one)
    collections_out = {'adjacent_year':annual,'exact_five_year':gap5,
                       'one_long_gap_per_route':long_gap,'early_to_late_era':across}
    summary = {}
    for k,pairs in collections_out.items():
        summary[k] = {'pairs':len(pairs),
                      'routes':len({p['route'] for p in pairs}),
                      'same_sensor_scene_candidate_pairs':sum(p['common_sensor_candidate'] for p in pairs),
                      'same_sensor_and_scene_season_candidate_pairs':sum(p['common_sensor_season_scene_candidate'] for p in pairs),
                      'year_gap_median':sorted(p['gap_years'] for p in pairs)[len(pairs)//2] if pairs else None}
    routespans=[max(r['year'] for r in group)-min(r['year'] for r in group) for group in byroute.values()]
    result = {'analysis':'e3_landsat_longitudinal_metadata_feasibility_v0_1',
              'input_analysis':obj['analysis'],
              'scientific_status':'metadata_only_no_pixel_or_frog_response',
              'population_scope':'frozen E3 principal-pair subset, not all 7,848 NAAMP runs',
              'n_survey_runs':len(rows),'n_routes':len(byroute),
              'n_routes_at_least_two_survey_years':sum(len({r['year'] for r in g})>=2 for g in byroute.values()),
              'n_routes_span_at_least_five_years':sum(s>=5 for s in routespans),
              'n_routes_span_at_least_eight_years':sum(s>=8 for s in routespans),
              'n_routes_with_full_scene_candidate':len({r['route'] for r in rows}),
              'image_lookback_days':MAX_LOOKBACK_DAYS,
              'survey_date_season_tolerance_days':season_days,
              'scene_acquisition_same_season_tolerance_days':season_days,
              'groups':summary,
              'QA_pixel_validity_checked':False,
              'physical_site_continuity_across_years_verified':False,
              'cross_sensor_harmonisation_performed':False,
              'climate_or_biology_effect_estimated':False,
              'note':'Potential route-year satellite coverage only: requires independent site verification, QA-complete pixels and frozen climate-response analysis.'}
    return result, collections_out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-json',help='E3_NDMI_METADATA_COVERAGE_V0_1.json source')
    ap.add_argument('--source-zip',help='GitHub Actions artifact containing source JSON')
    ap.add_argument('--out-receipt',required=True)
    ap.add_argument('--out-pairs',help='Optional JSON of metadata-only run pair identities')
    args=ap.parse_args()
    if bool(args.source_json) == bool(args.source_zip):
        raise ValueError('Provide exactly one metadata source path')
    if args.source_json:
        source=Path(args.source_json).read_bytes()
    else:
        with zipfile.ZipFile(args.source_zip) as z:
            names=[name for name in z.namelist() if name.endswith('E3_NDMI_METADATA_COVERAGE_V0_1.json')]
            if len(names)!=1: raise ValueError('source ZIP lacks unique expected receipt')
            source=z.read(names[0])
    obj=json.loads(source)
    output, groups = audit(obj,season_days=21)
    output["season_sensitivity"]={str(days):audit(obj,season_days=days)[0]["groups"] for days in (7,14,21)}
    output['input_json_sha256']=hashlib.sha256(source).hexdigest()
    target=Path(args.out_receipt);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    if args.out_pairs:
        path=Path(args.out_pairs);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(groups,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=='__main__':main()