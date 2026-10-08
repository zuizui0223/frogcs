import importlib.util, sys
from pathlib import Path
import numpy as np, pandas as pd, pytest
scripts=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(scripts))
spec=importlib.util.spec_from_file_location('acousticpilot',scripts/'route_climate_strong_calling_pilot.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture():
    routes=['R'+str(i) for i in range(6)]
    runs=[];stops=[];calls=[];exposures=[]
    for route in routes:
      for year in range(2001,2016):
       for roundno in (1,2):
        rid=f'{route}-{year}-{roundno}'
        datestr=f'05/{10+roundno:02d}/{year}'
        runs.append(dict(RunID=rid,SurveyDate=datestr,RunNumber=str(roundno),DaysSinceRain='3',TempScale='C'))
        ex=dict(run_id=rid,route_id=route, survey_year=year,survey_round=roundno,
                 survey_date=f'{year}-05-{10+roundno:02d}',
                 prior5_tmean_anomaly_c=.02*(year-2001),
                 prior5_precip_ratio_to_1981_2000=1+.01*(year-2001))
        exposures.append(ex)
        for st in range(1,11):
         stops.append(dict(RunID=rid,StopNumber=str(st),SkippedStop='0',AirTemp='15'))
         if st<=int((year-2001)*.27)+roundno:
          calls.append(dict(RunID=rid,StopNumber=str(st),CallingIndex='2'))
    return (pd.DataFrame(runs),pd.DataFrame(stops),pd.DataFrame(calls),pd.DataFrame(exposures))

def test_exact_strong_stop_endpoint():
    run,stop,call,ex=fixture()
    y=m.build_outcome(run,stop,call,ex)
    r=y[(y.route_id=='R1')&(y.survey_year==2001)&(y.survey_round==1)].iloc[0]
    assert r.strong_stops==1
    extra=pd.DataFrame([{'RunID':r.run_id,'StopNumber':'1','CallingIndex':'3'}])
    y2=m.build_outcome(run,stop,pd.concat([call,extra],ignore_index=True),ex)
    assert int(y2[(y2.route_id=='R1')&(y2.survey_year==2001)&(y2.survey_round==1)].iloc[0].strong_stops)==1

def test_rejects_counts_outside_survey():
    run,stop,call,ex=fixture()
    call.loc[0,'StopNumber']='19'
    with pytest.raises(ValueError,match='outside surveyed stops'):m.build_outcome(run,stop,call,ex)

def test_holdout_never_uses_test_for_train_scaling():
    run,stop,call,ex=fixture()
    y=m.build_outcome(run,stop,call,ex)
    train=y[y.survey_year<=2010].copy();test=y[y.survey_year>=2011].copy()
    a,b,cols=m.design(train,test,True)
    test['temp_c']=1e6
    c,d,cols2=m.design(train,test,True)
    assert cols==cols2
    np.testing.assert_allclose(a,c)
    assert not np.allclose(b,d)

def test_baseline_vs_climate_both_fit():
    run,stop,call,ex=fixture()
    y=m.build_outcome(run,stop,call,ex)
    r,by=m.audit_and_fit(y)
    assert r['classification']=='COMPLETED_EXPLORATORY_TEMPORAL_HOLDOUT'
    assert r['n_training_runs']==6*10*2
    assert r['n_heldout_runs']==6*5*2
    assert np.isfinite(r['mean_heldout_gain_positive_better'])
    assert len(by)==6

def test_fail_closed_without_temporal_test():
    run,stop,call,ex=fixture()
    y=m.build_outcome(run,stop,call,ex)
    r,by=m.audit_and_fit(y[y.survey_year<=2010])
    assert r['classification']=='INSUFFICIENT_TEMPORAL_HOLDOUT_COVERAGE'
    assert by is None
