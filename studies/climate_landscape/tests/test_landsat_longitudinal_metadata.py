import importlib.util
import pathlib
import pytest

path=pathlib.Path(__file__).resolve().parents[1]/'scripts'/'audit_landsat_longitudinal_metadata.py'
spec=importlib.util.spec_from_file_location('landsat_long',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def row(name,year,day,route='VA:70001',prefix='LE07_'):
    from datetime import date,timedelta
    d=date(year,5,day)
    sc=d-timedelta(days=5)
    return {'RunID':name,'route_cluster':route,'survey_date':d.isoformat(),
      'resolved':True,'all10_one_product_candidate':True,
      'candidates':[{'item_id':prefix+'TEST_SCENE','acquisition_date':sc.isoformat(),
          'lag_days':5,'footprint_check':'polygon'}]}


def fixture(rows):
    return {'analysis':'naamp_e3_ndmi_metadata_coverage_v0_1',
      'classification':'metadata_necessary_gate_pass','NDMI_values_read':False,
      'pixel_QA_coverage_calculated':False,'frog_endpoint_calculated':False,
      'metadata_run_rows':rows}


def test_near_season_and_long_gap():
    obj=fixture([row('a',2002,11),row('b',2003,15),row('c',2008,12),row('d',2013,14)])
    result,groups=m.audit(obj)
    assert result['n_routes']==1
    assert result['groups']['adjacent_year']['pairs']==1
    assert result['groups']['exact_five_year']['pairs']==2
    assert result['groups']['one_long_gap_per_route']['pairs']==1
    assert result['groups']['early_to_late_era']['pairs']==1
    assert groups['one_long_gap_per_route'][0]['gap_years']==11
    assert groups['one_long_gap_per_route'][0]['common_sensor_season_scene_candidate']


def test_one_to_one_matching_with_many_runs_per_year():
    obj=fixture([row('a',2010,3),row('b',2010,15),row('c',2011,4),row('d',2011,16)])
    _,groups=m.audit(obj)
    x=groups['adjacent_year']
    assert len(x)==2
    assert {(p['run_earlier'],p['run_later']) for p in x} == {('a','c'),('b','d')}


def test_lag_and_future_lookahead_hard_failure():
    r=row('a',2010,11)
    r['candidates'][0]['acquisition_date']='2010-06-11'
    with pytest.raises(ValueError,match='Future/out-of-window'):
        m.audit(fixture([r]))


def test_different_sensor_not_same_sensor_match():
    obj=fixture([row('a',2004,11,prefix='LT05_'),row('b',2005,11,prefix='LE07_')])
    x,_=m.audit(obj)
    assert x['groups']['adjacent_year']['pairs']==1
    assert x['groups']['adjacent_year']['same_sensor_scene_candidate_pairs']==0


def test_same_sensor_different_scene_season_invalid():
    x=row('a',2010,11)
    y=row('b',2011,11)
    # Preadjust to the first valid date in the allowed 32-day lookup; the
    # observed survey dates are matched, but satellite seasons need not be.
    y['candidates'][0]['acquisition_date']='2011-04-10'
    y['candidates'][0]['lag_days']=31
    output,_=m.audit(fixture([x,y]))
    assert output['groups']['adjacent_year']['same_sensor_scene_candidate_pairs']==1
    assert output['groups']['adjacent_year']['same_sensor_and_scene_season_candidate_pairs']==0


def test_no_outcome_data_or_duplicate_runid():
    r=row('a',2010,11)
    with pytest.raises(ValueError,match='Duplicate'):
        m.audit(fixture([r,r]))
    f=fixture([r]);f['frog_endpoint_calculated']=True
    with pytest.raises(ValueError,match='response-blind'):
        m.audit(f)


def test_source_must_be_frozen_e3():
    f=fixture([row('a',2010,11)])
    f['classification']='not_eligible'
    with pytest.raises(ValueError,match='frozen'):
        m.audit(f)



def test_stricter_date_matching_sensitivity_falls_between_windows():
    obj=fixture([row('a',2010,11),row('b',2011,28)])
    tight,_=m.audit(obj,season_days=7)
    medium,_=m.audit(obj,season_days=14)
    broad,_=m.audit(obj,season_days=21)
    assert tight['groups']['adjacent_year']['pairs']==0
    assert medium['groups']['adjacent_year']['pairs']==0
    assert broad['groups']['adjacent_year']['pairs']==1
    with pytest.raises(ValueError,match='7/14/21'):
        m.audit(obj,season_days=30)