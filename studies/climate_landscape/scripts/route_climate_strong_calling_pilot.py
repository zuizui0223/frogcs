#!/usr/bin/env python3
"""Prospectively specified, exploratory route-scale NAAMP climate-acoustic pilot.

Uses an independently source-selected set of 12 routes and strictly previous
5-year Daymet route-scale climate exposure. No fine-site satellite inference;
no demographic/occupancy or anthropogenic climate attribution.

Main outcome: number among ten non-skipped sampled stops with at least one
CallingIndex >= 2 record. Both models use the same surveyed runs and same
2011-2015 test period; H0 uses route, visit round, season, air temperature,
rain recency, H1 adds past-only climate history. Ridge penalty fixed a priori.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from build_daymet_survey_exposure_panel import combine, sha256
from build_naamp_observation_panel import SOURCE_PINS

COUNTS_SHA='60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086'
RIDGE=1.0
N_STOPS=10
EARLY_END=2010
LATE_START=2011
TRAIN_MIN=30
TEST_MIN=20
MIN_ROUTE_TRAIN=3
MIN_ROUTE_TEST=2


def build_outcome(runs,stops,counts,exposures):
    for cols,name,d in [({'RunID','DaysSinceRain','SurveyDate','RunNumber'},'runs',runs),
                        ({'RunID','StopNumber','SkippedStop','AirTemp'},'stops',stops),
                        ({'RunID','StopNumber','CallingIndex'},'counts',counts)]:
        missing=cols-set(d.columns)
        if missing:raise ValueError(f'{name} missing required columns: {sorted(missing)}')
    if exposures.duplicated('run_id').any():raise ValueError('climate exposure duplicated RunID')
    r=runs.set_index('RunID')
    if r.index.duplicated().any():raise ValueError('duplicate source RunID')
    eligible=exposures[['run_id','route_id','survey_date','survey_year','survey_round',
        'prior5_tmean_anomaly_c','prior5_precip_ratio_to_1981_2000']].copy()
    eligible['run_id']=eligible.run_id.astype(str)
    x=eligible.join(r[['DaysSinceRain','SurveyDate','RunNumber','TempScale']],on='run_id',how='left',validate='one_to_one')
    if x[['DaysSinceRain','SurveyDate','RunNumber','TempScale']].isna().any().any():
        raise ValueError('missing source runs')
    source_dates=pd.to_datetime(x.SurveyDate,errors='coerce')
    if source_dates.isna().any():raise ValueError('Unparseable survey dates')
    if not (source_dates.dt.date.astype(str).to_numpy()==x.survey_date.astype(str).to_numpy()).all():
        raise ValueError('survey dates disagree with Daymet selected run panel')
    if not (x.RunNumber.astype(int).to_numpy()==x.survey_round.astype(int).to_numpy()).all():
        raise ValueError('run round disagrees')
    x['rain_recency']=pd.to_numeric(x.DaysSinceRain,errors='coerce')
    if (~np.isfinite(x.rain_recency) | ~x.rain_recency.between(0,180)).any():
        raise ValueError('invalid rain recency')
    sites=stops[stops.RunID.isin(set(x.run_id))].copy()
    sites=sites[sites.SkippedStop.astype(str).str.strip().eq('0')]
    if sites.duplicated(['RunID','StopNumber']).any():
        raise ValueError('duplicated stop for sampled run')
    counts_site=sites.groupby('RunID').StopNumber.nunique()
    if not counts_site.reindex(x.run_id).eq(N_STOPS).all():
        raise ValueError('not exactly ten stops for every sampled run')
    sites['temperature']=pd.to_numeric(sites.AirTemp,errors='coerce')
    scale=x.set_index('run_id').TempScale.to_dict()
    sites['temp_c']=np.where(sites.RunID.map(scale).eq('F'),(sites.temperature-32)*5/9,sites.temperature)
    if (~sites.RunID.map(scale).isin(['C','F'])).any():raise ValueError('Unknown temperature scale')
    if sites.temp_c.groupby(sites.RunID).count().reindex(x.run_id).min()<8:
        raise ValueError('insufficient stop temperature coverage')
    temp=sites.groupby('RunID').temp_c.mean()
    x['temp_c']=x.run_id.map(temp)
    if (~np.isfinite(x.temp_c) | ~x.temp_c.between(-10,45)).any():raise ValueError('invalid temperatures')
    counts=counts[counts.RunID.isin(set(x.run_id))].copy()
    counts.CallingIndex=counts.CallingIndex.astype(str).str.strip()
    if (~counts.CallingIndex.isin(['1','2','3'])).any():raise ValueError('unexpected positive CI code')
    allowed=sites[['RunID','StopNumber']]
    checked=counts.merge(allowed,on=['RunID','StopNumber'],how='left',indicator=True,validate='many_to_one')
    if not checked._merge.eq('both').all():raise ValueError('positive calls outside surveyed stops')
    strong=checked[checked.CallingIndex.isin(['2','3'])]
    k=strong.groupby('RunID').StopNumber.nunique()
    x['strong_stops']=x.run_id.map(k).fillna(0).astype(int)
    if (~x.strong_stops.between(0,N_STOPS)).any():raise ValueError('bad strong stops')
    x['doy']=source_dates.dt.dayofyear
    x['season_sin']=np.sin(2*np.pi*x.doy/365.25)
    x['season_cos']=np.cos(2*np.pi*x.doy/365.25)
    x['log_days_since_rain']=np.log1p(x.rain_recency)
    x['log_prior_precip']=np.log(x.prior5_precip_ratio_to_1981_2000)
    if (~np.isfinite(x.log_prior_precip)).any():raise ValueError('invalid prior climate')
    return x.sort_values(['route_id','survey_year','run_id']).reset_index(drop=True)


def design(train,test,add_climate):
    # Never learn preprocessing from future rows.
    continuous=['temp_c','log_days_since_rain','season_sin','season_cos']
    if add_climate:continuous+=['prior5_tmean_anomaly_c','log_prior_precip']
    train_cols=[np.ones(len(train))];test_cols=[np.ones(len(test))];labels=['intercept']
    routes=sorted(train.route_id.unique());rounds=[2,3,4]
    for route in routes[1:]:
        train_cols.append(train.route_id.eq(route).astype(float).to_numpy())
        test_cols.append(test.route_id.eq(route).astype(float).to_numpy())
        labels.append('route_'+route)
    for roundno in rounds:
        train_cols.append(train.survey_round.eq(roundno).astype(float).to_numpy())
        test_cols.append(test.survey_round.eq(roundno).astype(float).to_numpy())
        labels.append('round_'+str(roundno))
    for col in continuous:
        mu=float(train[col].mean());sd=float(train[col].std(ddof=0));sd=max(sd,0.05 if col=='prior5_tmean_anomaly_c' else 1e-6)
        train_cols.append(((train[col]-mu)/sd).to_numpy(dtype=float))
        test_cols.append(((test[col]-mu)/sd).to_numpy(dtype=float))
        labels.append(col)
    return np.column_stack(train_cols),np.column_stack(test_cols),labels


def fit_predict(X,Y,n=10,ridge=RIDGE):
    # Fitted only on train, penalty does not include intercept.
    X=np.asarray(X,dtype=float);Y=np.asarray(Y,dtype=float)
    if (~np.isfinite(X)).any() or (~np.isfinite(Y)).any() or not np.all((Y>=0)&(Y<=n)):
        raise ValueError('invalid predictors or response')
    penalty=np.ones(X.shape[1]);penalty[0]=0
    def objective(beta):
        eta=X@beta
        loss=np.sum(n*np.logaddexp(0,eta)-Y*eta)+0.5*ridge*np.sum(penalty*beta**2)
        grad=X.T@(n*expit(eta)-Y)+ridge*penalty*beta
        return loss,grad
    r=minimize(objective,np.zeros(X.shape[1]),jac=True,method='L-BFGS-B',
               options={'maxiter':1500,'ftol':1e-12})
    if not r.success:raise RuntimeError(f'Fit failed: {r.message}')
    return r.x


def loss_by_row(y,p):
    p=np.clip(np.asarray(p,dtype=float),1e-8,1-1e-8)
    y=np.asarray(y,dtype=float)
    return -(y*np.log(p)+(N_STOPS-y)*np.log1p(-p))/N_STOPS


def audit_and_fit(x):
    counts=x.groupby(['route_id','survey_year']).size().reset_index(name='n_runs')
    train=x[x.survey_year<=EARLY_END].copy()
    test=x[x.survey_year>=LATE_START].copy()
    train_routes=train.groupby('route_id').size()
    test_routes=test.groupby('route_id').size()
    usable=sorted(set(train_routes[train_routes>=MIN_ROUTE_TRAIN].index)&
                  set(test_routes[test_routes>=MIN_ROUTE_TEST].index))
    train=train[train.route_id.isin(usable)].copy()
    test=test[test.route_id.isin(usable)].copy()
    status={'n_runs_total':int(len(x)),'n_routes_total':int(x.route_id.nunique()),
            'n_route_years':int(len(counts)),
            'n_routes_both_eras_sufficient':len(usable),
            'n_training_runs':int(len(train)),'n_heldout_runs':int(len(test)),
            'min_train_runs':TRAIN_MIN,'min_test_runs':TEST_MIN,
            'time_cutoff_training_last_year':EARLY_END,'heldout_first_year':LATE_START,
            'independent_site_coordinates_verified':False,
            'site_level_landscape_effects_computed':False,
            'endpoint':'number_of_10_stops_with_at_least_one_CI2_or_CI3',
            'claims':'exploratory prediction in fixed 12 route screen, not causal climate or abundance'}
    if len(train)<TRAIN_MIN or len(test)<TEST_MIN or len(usable)<5:
        status['classification']='INSUFFICIENT_TEMPORAL_HOLDOUT_COVERAGE'
        return status,None
    if train.strong_stops.nunique()<=1:
        status['classification']='NO_TRAIN_RESPONSE_VARIATION'
        return status,None
    outputs=[]
    for add in (False,True):
        a,b,features=design(train,test,add)
        beta=fit_predict(a,train.strong_stops.to_numpy())
        p=expit(b@beta)
        outputs.append(pd.DataFrame({'run_id':test.run_id.to_numpy(),
              'route_id':test.route_id.to_numpy(),'survey_year':test.survey_year.to_numpy(),
              'strong_stops':test.strong_stops.to_numpy(),
              ('logloss_extended' if add else 'logloss_baseline'):loss_by_row(test.strong_stops.to_numpy(),p)}))
    pred=outputs[0].merge(outputs[1],on=['run_id','route_id','survey_year','strong_stops'],validate='one_to_one')
    pred['improvement']=pred.logloss_baseline-pred.logloss_extended
    by_route=pred.groupby('route_id').agg(n=('run_id','size'),gain=('improvement','mean')).reset_index()
    status.update({'classification':'COMPLETED_EXPLORATORY_TEMPORAL_HOLDOUT',
      'mean_heldout_baseline_logloss':float(pred.logloss_baseline.mean()),
      'mean_heldout_extended_logloss':float(pred.logloss_extended.mean()),
      'mean_heldout_gain_positive_better':float(pred.improvement.mean()),
      'mean_route_equal_weight_gain_positive_better':float(by_route.gain.mean()),
      'routes_with_positive_gain':int((by_route.gain>0).sum()),
      'routes_with_negative_gain':int((by_route.gain<0).sum()),
      'n_strong_stop_visits_train':int(train.strong_stops.sum()),
      'n_strong_stop_visits_test':int(test.strong_stops.sum())})
    return status,by_route


def main():
    ap=argparse.ArgumentParser()
    for name in ('sample','climate_receipt','runs','stops','counts','out'):
        ap.add_argument('--'+name.replace('_','-'),required=True)
    z=ap.parse_args()
    hashes={'Runs.csv':sha256(z.runs),'Stops.csv':sha256(z.stops),
            'Counts.csv':sha256(z.counts)}
    if hashes!={**SOURCE_PINS,'Counts.csv':COUNTS_SHA}:
        raise ValueError('Original USGS NAAMP source digest mismatch')
    sample=json.loads(Path(z.sample).read_text())
    climate=json.loads(Path(z.climate_receipt).read_text())
    if climate.get('sample_source_sha256')!=sha256(z.sample):
        raise ValueError('Daymet receipt not tied to sampled routes')
    runs=pd.read_csv(z.runs,dtype=str,keep_default_na=False)
    stops=pd.read_csv(z.stops,dtype=str,keep_default_na=False)
    exposed,meta=combine(sample,climate,runs,stops)
    counts=pd.read_csv(z.counts,dtype=str,keep_default_na=False)
    data=build_outcome(runs,stops,counts,exposed)
    report,by_route=audit_and_fit(data)
    report.update({'source_sha256':hashes,'daymet_sample_sha256':sha256(z.sample),
       'daymet_climate_receipt_sha256':sha256(z.climate_receipt),
       'no_testing_data_used_for_feature_scaling':True,
       'models':'fixed_ridge_binomial_route_round_season_temp_rain_vs_plus_past5_climate',
       'ridge_penalty':RIDGE,'n_stops_per_run':N_STOPS,
       'source_sample_preselected_without_frog_counts':True,
       'not_pre_registered_before_prior_frog_inspection_in_repository':True,
       'geographically_or_temporally_generalizable':False,
       'endpoint_is_calling_only_not_breeding_success':True,
       'route_equal_weight_gains':[] if by_route is None else by_route.to_dict(orient='records')})
    path=Path(z.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if not isinstance(v,(dict,list))},sort_keys=True,indent=2))

if __name__=='__main__':main()
