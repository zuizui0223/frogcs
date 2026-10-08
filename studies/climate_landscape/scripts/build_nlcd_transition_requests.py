#!/usr/bin/env python3
"""Convert verified survey dates into a frozen prior-year NLCD change manifest.

Forest/impervious change is computed between calendar years (survey−6) and
(survey−1), guaranteeing that both years precede an observed frog survey.
The manifest is response-blind and does not certify any station coordinates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

NEEDED={"run_id","route_id","site_id","latitude","longitude",
        "survey_date","coordinate_qc_status","verification_source_id"}


def make(surveys):
    missing=NEEDED-set(surveys.columns)
    if missing:raise ValueError(f'Missing fields: {sorted(missing)}')
    if {'CallingIndex','Species','chorus','frog_response'} & set(surveys.columns):
        raise ValueError('Outcome data must not be mixed with satellite extraction requests')
    a=surveys[sorted(NEEDED)].copy()
    a.survey_date=pd.to_datetime(a.survey_date,errors='raise')
    if a.survey_date.isna().any():raise ValueError('Missing survey dates')
    if not a.coordinate_qc_status.eq('verified_external').all():
        raise ValueError('Independent physical station verification required')
    if a.verification_source_id.astype('string').isna().any() or a.verification_source_id.astype(str).str.strip().eq('').any():
        raise ValueError('Missing independent station evidence ID')
    if a.duplicated(['run_id','route_id','site_id']).any():
        raise ValueError('Duplicate physical survey events')
    if not a.survey_date.dt.year.between(2001,2015).all():
        raise ValueError('Study surveys are restricted to the NAAMP 2001–2015 era')
    records=[]
    for r in a.itertuples(index=False):
        for buffer in (250,1000):
            records.append(dict(run_id=str(r.run_id),route_id=str(r.route_id),site_id=str(r.site_id),
                latitude=float(r.latitude),longitude=float(r.longitude),
                survey_date=pd.Timestamp(r.survey_date).date().isoformat(),
                year_earlier=int(r.survey_date.year-6),year_later=int(r.survey_date.year-1),
                coordinate_qc_status='verified_external',
                verification_source_id=str(r.verification_source_id),buffer_m=buffer))
    return pd.DataFrame(records).sort_values(['run_id','route_id','site_id','buffer_m']).reset_index(drop=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--verified-surveys',required=True)
    p.add_argument('--out',required=True)
    args=p.parse_args()
    rows=make(pd.read_csv(args.verified_surveys,dtype={k:str for k in
         ('run_id','route_id','site_id','verification_source_id')}))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    rows.to_csv(out,index=False)
    result=dict(analysis='frozen_antecedent_nlcd_transition_requests_v0_1',
                input_sha256=hashlib.sha256(Path(args.verified_surveys).read_bytes()).hexdigest(),
                output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                requests=int(len(rows)),n_survey_site_events=int(len(rows)/2),
                response_columns_read=False)
    out.with_suffix('.receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
