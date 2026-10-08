#!/usr/bin/env python3
"""Read verified, complete source-only Daymet receipt and summarize climate state contrasts.

This is environmental description only, not a frog-response or anthropogenic
attribution analysis. Avoid treating 12 routes as a random CONUS sample.
"""
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

def summarize(obj):
    if obj.get('status')!='complete_source_screening' or obj.get('n_complete_routes')!=12:
        raise ValueError('Expected complete predeclared 12-route screening receipt')
    rows=[]
    for x in obj['routes']:
        hist=x['climate_state_by_survey_year']
        if set(hist)!={str(y) for y in range(2001,2016)}:
            raise ValueError('Incomplete prior-only climate histories')
        for y in range(2001,2016):
            r=hist[str(y)]
            rows.append(dict(state=x['state'],route_id=x['route_id'],year=y,
               prior5_temp_anom_c=float(r['prior5_tmean_anomaly_c']),
               prior5_precip_ratio=float(r['prior5_precip_ratio_to_1981_2000']),
               fullperiod_temp_slope_c_decade=float(x['descriptive_1981_2015_temp_slope_c_decade']),
               fullperiod_precip_slope_mm_decade=float(x['descriptive_1981_2015_precip_slope_mm_decade'])))
    df=pd.DataFrame(rows).sort_values(['route_id','year']).reset_index(drop=True)
    a=df[df.year==2001].set_index('route_id');b=df[df.year==2015].set_index('route_id')
    q=b[['state','prior5_temp_anom_c','prior5_precip_ratio','fullperiod_temp_slope_c_decade','fullperiod_precip_slope_mm_decade']].copy()
    q['delta_prior5_temp_2015_minus_2001_c']=b.prior5_temp_anom_c-a.prior5_temp_anom_c
    q['delta_prior5_precip_2015_minus_2001_ratio']=b.prior5_precip_ratio-a.prior5_precip_ratio
    q['temp_slope_sign_matches_prior_shift']=np.sign(q.fullperiod_temp_slope_c_decade)==np.sign(q.delta_prior5_temp_2015_minus_2001_c)
    q['precip_slope_sign_matches_prior_shift']=np.sign(q.fullperiod_precip_slope_mm_decade)==np.sign(q.delta_prior5_precip_2015_minus_2001_ratio)
    results={'analysis':'route_antecedent_climate_state_vs_retrospective_trend_v0_1',
             'n_routes':len(q),'n_route_year_states':len(df),
             'n_warming_fullperiod_slope':int((q.fullperiod_temp_slope_c_decade>0).sum()),
             'n_increasing_precip_fullperiod_slope':int((q.fullperiod_precip_slope_mm_decade>0).sum()),
             'n_warming_prior5_state_2001_to_2015':int((q.delta_prior5_temp_2015_minus_2001_c>0).sum()),
             'n_increasing_prior5_precip_state_2001_to_2015':int((q.delta_prior5_precip_2015_minus_2001_ratio>0).sum()),
             'n_precip_sign_disagreement':int((~q.precip_slope_sign_matches_prior_shift).sum()),
             'n_temp_sign_disagreement':int((~q.temp_slope_sign_matches_prior_shift).sum()),
             'median_delta_prior5_temp_c':float(q.delta_prior5_temp_2015_minus_2001_c.median()),
             'median_delta_prior5_precip_ratio':float(q.delta_prior5_precip_2015_minus_2001_ratio.median()),
             'baseline':'1981-2000','fullperiod_slope_period':'1981-2015',
             'past_only_contrasts':'1996-2000 (survey 2001) vs 2010-2014 (survey 2015)',
             'sample_inference':'fixed 12-route metadata-selected Daymet screening; not population-representative',
             'no_frog_responses_read':True,'no_causal_climate_attribution':True,
             'route_summaries':q.reset_index().to_dict(orient='records')}
    return df,results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out-dir',required=True)
    a=p.parse_args();df,res=summarize(json.load(open(a.source)))
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/'daymet_prior5_route_years.csv',index=False)
    (out/'daymet_climate_state_contrasts_v0_1.json').write_text(json.dumps(res,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in res.items() if k!='route_summaries'},indent=2))
