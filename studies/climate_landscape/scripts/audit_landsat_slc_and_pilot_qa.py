#!/usr/bin/env python3
"""Real data QUALITY audit using frozen E3 STAC metadata and its pilot QA artifacts.

The upstream E3 sample was selected using frog data in another analysis, so
these are conditional engineering estimates, NOT representative coverage or a
frog-climate/ecological result. Pilot QA checks only FIRST Landsat candidate.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
from pathlib import Path
import hashlib
import json
import zipfile

from audit_landsat_longitudinal_scene_pairs import (
    read_source, eligible_scene_pair, CUTOFFS)
from audit_landsat_longitudinal_metadata import audit as longitudinal_audit, check_source

SLC_OFF = date(2003, 5, 31)
PIN_SHA='f375494c3ee4897d45729866f771521753a1a9ed070908ce4002d1db3ab599ce'


def evaluate(source:dict,qa_pilots:list[dict])->dict:
    records=check_source(source)
    lookup={r['run_id']:r for r in records}
    _,pairs=longitudinal_audit(source,season_days=21)
    comparison={}
    for category in ('one_long_gap_per_route','early_to_late_era','adjacent_year'):
        class_counts=Counter()
        included=0
        qualified=[]
        for p in pairs[category]:
            ok,selected=eligible_scene_pair(lookup[p['run_earlier']],lookup[p['run_later']],
                                    **CUTOFFS['strict_season14_lag16'])
            if not ok: continue
            included+=1
            a,b=selected
            plat=a.split('_',1)[0]
            if plat != b.split('_',1)[0]:
                raise ValueError('selected satellites differ')
            # For ETM+, distinguish pre-failure, mixed, and post-failure acquisition
            if plat=='LE07':
                early=date.fromisoformat(a.split('_')[3][:4]+'-'+a.split('_')[3][4:6]+'-'+a.split('_')[3][6:8])
                late=date.fromisoformat(b.split('_')[3][:4]+'-'+b.split('_')[3][4:6]+'-'+b.split('_')[3][6:8])
                if early<SLC_OFF and late<SLC_OFF:
                    label='LE07_both_pre_SLC_off'
                elif early>=SLC_OFF and late>=SLC_OFF:
                    label='LE07_both_post_SLC_off'
                else:
                    label='LE07_mixed_pre_post_SLC_off'
            else:
                label=plat+'_other_satellite'
            class_counts[label]+=1
            qualified.append({'route':p['route'],'year_gap':p['gap_years'],
                'platform':plat,'scene_earlier':a,'scene_later':b,'slc_class':label})
        comparison[category]={'n_metadata_eligible_pairs':included,
           'n_distinct_routes':len(set(z['route'] for z in qualified)),
           'SLC_class_counts':dict(sorted(class_counts.items())),
           'n_with_LE07_SLC_OFF_on_either_image':int(class_counts['LE07_both_post_SLC_off']+
                 class_counts['LE07_mixed_pre_post_SLC_off']),
           'n_not_using_LE07':sum(v for k,v in class_counts.items() if 'LE07' not in k)}
    pilot_records=[]
    for p in qa_pilots:
        if p.get('analysis')!='e3_ndmi_pixel_qa_pilot_v0_1' or p.get('frog_endpoint_calculated') or p.get('NDMI_computed'):
            raise ValueError('Not valid response-blind E3 quality pilot')
        pilot_records.extend(p.get('records',[]))
    if len(set(str(r['RunID']) for r in pilot_records))!=len(pilot_records):
        raise ValueError('Pilot duplicates RunID')
    quality=Counter()
    by_era={}
    for i, p in enumerate(qa_pilots):
        x=p['records']
        by_era[str(p['era_shard'])]={
            'runs':len(x),
            'n_qa_evaluated':sum(bool(r.get('qa_coverage_evaluated')) for r in x),
            'first_scene_all10_qa_pass':sum(r.get('all10_qa70_first_candidate') is True for r in x),
            'source_failed':sum(bool(r.get('error_type')) for r in x)}
        for r in x:
            if r.get('error_type'):quality['source_error']+=1
            elif r.get('qa_coverage_evaluated'):
                quality['qa_evaluated']+=1
                if r.get('all10_qa70_first_candidate') is True:quality['first_scene_all10_pass']+=1
                else:quality['first_scene_all10_fail']+=1
            else:
                quality['not_qa_evaluated']+=1
    return {'analysis':'landscape_2026_e3_slc_off_and_pilot_quality_audit_v0_1',
        'source_frog_e3_sample_outcome_informed':True,
        'actual_scenes_pixel_values_computed':False,
        'pilot_is_only_18_hash_selected_runs_first_scene_only':True,
        'site_coordinates_not_externally_verified':True,
        'frog_climate_effect_estimated':False,
        'E3_runs':len(records),
        'E3_routes':len({r['route'] for r in records}),
        'Landsat7_scan_line_corrector_failed_date':SLC_OFF.isoformat(),
        'strict_metadata_scene_pair_classification':comparison,
        'pilot_qa':{
            'n_pilot_runs':len(pilot_records),
            'n_qa_evaluated':quality['qa_evaluated'],
            'n_first_scene_all10_pass':quality['first_scene_all10_pass'],
            'n_first_scene_all10_fail':quality['first_scene_all10_fail'],
            'n_source_error':quality['source_error'],
            'n_not_evaluated_other':quality['not_qa_evaluated'],
            'by_era_shard':by_era},
        'interpretation':'Source metadata cannot confirm QA-valid change maps; pilot samples are not representative, and USGS Annual NLCD pixel transitions remain uncomputed.'}


def read_pilot(path):
    with zipfile.ZipFile(path) as z:
        names=[n for n in z.namelist() if n.endswith('.json')]
        if len(names)!=1:raise ValueError('Expected single QA pilot JSON')
        return json.loads(z.read(names[0]))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--e3-source',required=True)
    p.add_argument('--pilots',required=True,nargs='+')
    p.add_argument('--out',required=True)
    args=p.parse_args()
    source,sha=read_source(args.e3_source)
    if sha!=PIN_SHA:raise ValueError('E3 source content differs from frozen SHA256')
    pilots=[read_pilot(f) for f in args.pilots]
    result=evaluate(source,pilots)
    result['source_sha256']=sha
    result['pilot_artifact_zip_sha256']={Path(f).name:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in args.pilots}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result['strict_metadata_scene_pair_classification'],indent=2))
    print('pilot',json.dumps(result['pilot_qa'],indent=2))


if __name__=='__main__':main()
