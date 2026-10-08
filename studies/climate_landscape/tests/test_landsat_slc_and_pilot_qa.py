from __future__ import annotations
import importlib.util
from datetime import date,timedelta
from pathlib import Path
import pytest
import sys

S=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(S))
sp=importlib.util.spec_from_file_location('audit_slc',S/'audit_landsat_slc_and_pilot_qa.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)


def candidate(acq,platform='LE07'):
    date_=date.fromisoformat(acq)
    return {'item_id':f'{platform}_L2SP_018033_{date_:%Y%m%d}_02_T1',
       'lag_days':3,'footprint_check':'polygon','acquisition_date':acq}


def row(run_id,acq,platform='LE07'):
    d=(date.fromisoformat(acq)+timedelta(days=3)).isoformat()
    return {'RunID':run_id,'route_cluster':'Virginia:1515',
        'survey_date':d,'resolved':True,'all10_one_product_candidate':True,
        'candidates':[candidate(acq,platform)]}


def source(early='2002-05-01',late='2008-05-01',platform='LE07'):
    return {'analysis':'naamp_e3_ndmi_metadata_coverage_v0_1',
       'classification':'metadata_necessary_gate_pass',
       'NDMI_values_read':False,'pixel_QA_coverage_calculated':False,
       'frog_endpoint_calculated':False,
       'metadata_run_rows':[row('early',early,platform),row('late',late,platform)]}


def pilot(run_ids=('early','late')):
    return {'analysis':'e3_ndmi_pixel_qa_pilot_v0_1',
      'frog_endpoint_calculated':False,'NDMI_computed':False,'era_shard':1,
      'records':[{'RunID':r,'qa_coverage_evaluated':True,
                  'all10_qa70_first_candidate':r=='early'} for r in run_ids]}


def test_mixed_scanline_failure_pair():
    d=m.evaluate(source(),[pilot()])
    assert d['strict_metadata_scene_pair_classification']['one_long_gap_per_route']['SLC_class_counts']=={
      'LE07_mixed_pre_post_SLC_off':1}
    assert d['pilot_qa']['n_first_scene_all10_pass']==1
    assert d['pilot_qa']['n_qa_evaluated']==2
    assert not d['frog_climate_effect_estimated']


def test_both_post_slc_off():
    d=m.evaluate(source('2004-05-01','2010-05-01'),[pilot()])
    assert d['strict_metadata_scene_pair_classification']['one_long_gap_per_route']['SLC_class_counts']=={
      'LE07_both_post_SLC_off':1}


def test_other_satellite_does_not_receive_scandate_failure():
    d=m.evaluate(source(platform='LT05'),[pilot()])
    assert d['strict_metadata_scene_pair_classification']['one_long_gap_per_route']['n_not_using_LE07']==1


def test_pilot_duplicate_ids_are_invalid():
    with pytest.raises(ValueError,match='duplicates'):
        m.evaluate(source(),[pilot(('early','early'))])


def test_unapproved_qa_product_rejected():
    bad=pilot();bad['NDMI_computed']=True
    with pytest.raises(ValueError,match='Not valid'):
        m.evaluate(source(),[bad])
