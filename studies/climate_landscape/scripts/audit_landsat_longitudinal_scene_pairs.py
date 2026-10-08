#!/usr/bin/env python3
"""Real E3 *metadata only* longitudinal scene-pair comparability diagnostics.

The source was assembled from the earlier frog-outcome-informed E3 analysis
subset. This script itself does not read frog responses; results therefore
must not be called an outcome-independent sampling frame or a validated
site-level land-cover change sample. No imagery pixels or cloud QA are read.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import zipfile

from audit_landsat_longitudinal_metadata import audit, check_source, season_day

SCENE = re.compile(r'^(LT04|LT05|LE07|LC08|LC09)_L2(?:SP|SR)_(\d{6})_(\d{8})_\d{2}_(?:T1|T2|RT)$')
CUTOFFS = {"broad": dict(image_season_days=21, max_image_lag=32, max_lag_difference=32),
           "same_season14": dict(image_season_days=14, max_image_lag=32, max_lag_difference=32),
           "strict_season14_lag16": dict(image_season_days=14, max_image_lag=16, max_lag_difference=7)}
GROUPS = ("adjacent_year", "exact_five_year", "one_long_gap_per_route", "early_to_late_era")


def scene_meta(row: dict) -> dict:
    m = SCENE.fullmatch(str(row['scene']))
    if not m:
        raise ValueError(f'Unexpected Landsat C2 L2 identifier: {row["scene"]}')
    parsed = date.fromisoformat(f'{m.group(3)[:4]}-{m.group(3)[4:6]}-{m.group(3)[6:8]}')
    if parsed != row['acquired']:
        raise ValueError('Scene ID acquisition date disagrees with source metadata')
    if row['lag'] < 0 or row['lag'] > 32:
        raise ValueError('Imagery must not postdate survey and must be within lookback')
    return {"platform": m.group(1), "pathrow": m.group(2),
            "scene_id": row['scene'], "date": parsed,
            "season_day":season_day(parsed), "lag":row['lag']}


def eligible_scene_pair(a: dict, b: dict, *, image_season_days: int,
                        max_image_lag: int, max_lag_difference: int) -> tuple[bool, tuple | None]:
    """Fixed metadata-only gate: same spacecraft/WRS, 1+ days prior, similar season/lag.

    Return a deterministic selected scene pair purely by date/identifier.
    Never use actual image QA or frog outcomes to select this metadata pair.
    """
    if not all(isinstance(x,int) and x>=0 for x in
               (image_season_days,max_image_lag,max_lag_difference)):
        raise ValueError('Bad fixed comparison tolerance')
    x = [scene_meta(s) for s in a['scenes']]
    y = [scene_meta(s) for s in b['scenes']]
    options=[]
    for s in x:
        for t in y:
            if s['platform'] != t['platform'] or s['pathrow'] != t['pathrow']:
                continue
            if not 1 <= s['lag'] <= max_image_lag or not 1 <= t['lag'] <= max_image_lag:
                continue
            image_shift = abs(s['season_day']-t['season_day'])
            lag_shift = abs(s['lag']-t['lag'])
            if image_shift > image_season_days or lag_shift > max_lag_difference:
                continue
            # Deterministic, outcome- and QA-independent ranking.
            options.append((image_shift,lag_shift,max(s['lag'],t['lag']),
                            s['scene_id'],t['scene_id']))
    if not options:
        return False, None
    best=min(options)
    return True, (best[3],best[4])


def _summarize(nested:dict[str,list[dict]]) -> dict:
    def stat(ps):
        states=Counter(p['route'].split(':',1)[0] for p in ps)
        platforms=Counter(p['scene_earlier'].split('_',1)[0] for p in ps)
        return {'pairs':len(ps), 'routes':len({p['route'] for p in ps}),
                'states':len(states), 'pairs_by_state':dict(sorted(states.items())),
                'pairs_by_satellite_platform':dict(sorted(platforms.items()))}
    return {name:stat(ps) for name,ps in nested.items()}


def run(source:dict) -> dict:
    rows=check_source(source)
    lookup={r['run_id']:r for r in rows}
    base, pairs=audit(source, season_days=21)
    result={
      'analysis':'frog_climate_strict_interannual_landsat_scene_pair_gate_v0_1',
      'source_analysis':source['analysis'],
      'source_is_selected_frog_e3_subset':True,
      'source_is_not_outcome_independent_sample':True,
      'this_analysis_reads_frog_response':False,
      'this_analysis_reads_landsat_pixels':False,
      'station_positions_independently_validated':False,
      'scene_pixel_qa_verified':False,
      'land_change_estimated':False,
      'acoustic_or_climate_effect_estimated':False,
      'n_source_runs':len(rows), 'n_routes':base['n_routes'],
      'source_population':'previous selected E3 2,916-principal-pair universe; not 7,848 full eligible runs',
      'comparators':{},'comparison_counts':{}
    }
    for tier,config in CUTOFFS.items():
        selected={g:[] for g in GROUPS}
        for group in GROUPS:
            for p in pairs[group]:
                eligible,picked=eligible_scene_pair(lookup[p['run_earlier']],lookup[p['run_later']],**config)
                if eligible:
                    selected[group].append({'route':p['route'],
                             'run_earlier':p['run_earlier'],'run_later':p['run_later'],
                             'year_gap':p['gap_years'],
                             'scene_earlier':picked[0],'scene_later':picked[1]})
        result['comparators'][tier]=config
        result['comparison_counts'][tier]=_summarize(selected)
    result['base_pairs']= {g:{'pairs':len(pairs[g]),'routes':len({p['route'] for p in pairs[g]})} for g in GROUPS}
    result['fixed_choice_bias_note']=(
      'The one_long_gap_per_route record was selected by maximum year gap before scene gate. '
      'These numbers are lower bounds for routes with ANY eligible scene pair, not route-optimized upper bounds.')
    return result


def read_source(path):
    path=Path(path)
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as z:
            names=[x for x in z.namelist() if x.endswith('E3_NDMI_METADATA_COVERAGE_V0_1.json')]
            if len(names)!=1:raise ValueError('Exactly one frozen metadata JSON required')
            blob=z.read(names[0])
    else:
        blob=path.read_bytes()
    return json.loads(blob),hashlib.sha256(blob).hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    src,sha=read_source(args.source)
    out=run(src)
    out['source_sha256']=sha
    pth=Path(args.output);pth.parent.mkdir(parents=True,exist_ok=True)
    pth.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(out['comparison_counts'],indent=2))

if __name__=='__main__':main()
