import importlib.util
from datetime import date, timedelta
from pathlib import Path
import pytest
import sys

ROOT = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('strict_scene', ROOT / 'audit_landsat_longitudinal_scene_pairs.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def src_scene(year,month,day, *, platform='LT05',pathrow='018033',lag=3):
    acquired=date(year,month,day)
    return {'scene':f'{platform}_L2SP_{pathrow}_{acquired:%Y%m%d}_02_T1',
            'acquired':acquired,'lag':lag}


def row(year,day,*,platform='LT05',pathrow='018033',lag=3):
    acquired=date(year,5,day)
    rec=src_scene(year,5,day,platform=platform,pathrow=pathrow,lag=lag)
    return {'year':year,'scenes':[rec]}


def test_same_platform_wrs_and_timing_pass():
    a=row(2003,4)
    b=row(2011,6)
    valid,best=m.eligible_scene_pair(a,b,**m.CUTOFFS['strict_season14_lag16'])
    assert valid is True
    assert best[0].startswith('LT05_') and best[1].startswith('LT05_')


def test_same_family_different_spacecraft_not_counted():
    a=row(2003,4,platform='LT04')
    b=row(2011,4,platform='LT05')
    assert not m.eligible_scene_pair(a,b,**m.CUTOFFS['broad'])[0]


def test_same_platform_wrong_wrs_pathrow_excluded():
    a=row(2003,4,pathrow='018033')
    b=row(2011,4,pathrow='018034')
    assert not m.eligible_scene_pair(a,b,**m.CUTOFFS['broad'])[0]


def test_same_platform_scene_strictly_before_survey():
    a=row(2003,4,lag=0)
    b=row(2011,4,lag=4)
    assert not m.eligible_scene_pair(a,b,**m.CUTOFFS['broad'])[0]


def test_recent_but_unequal_lag_fails_strict():
    a=row(2003,4,lag=3)
    b=row(2011,4,lag=13)
    assert m.eligible_scene_pair(a,b,**m.CUTOFFS['same_season14'])[0]
    assert not m.eligible_scene_pair(a,b,**m.CUTOFFS['strict_season14_lag16'])[0]


def test_scene_acquisition_not_equal_metadata_hard_fail():
    a=row(2003,4)
    a['scenes'][0]['acquired']=date(2003,5,5)
    with pytest.raises(ValueError,match='disagrees'):
        m.eligible_scene_pair(a,row(2011,4),**m.CUTOFFS['broad'])


def test_beyond_16day_image_lag_excluded_strict():
    a=row(2003,4,lag=18)
    b=row(2011,4,lag=18)
    assert m.eligible_scene_pair(a,b,**m.CUTOFFS['same_season14'])[0]
    assert not m.eligible_scene_pair(a,b,**m.CUTOFFS['strict_season14_lag16'])[0]


def test_unexpected_product_id_hard_fail():
    a=row(2003,4)
    a['scenes'][0]['scene']='UNKNOWN_SCENE'
    with pytest.raises(ValueError,match='Unexpected'):
        m.eligible_scene_pair(a,row(2011,4),**m.CUTOFFS['broad'])


def test_real_archive_is_consistent_and_response_not_calculated():
    archive=Path('/mnt/data/e3-ndmi-metadata-coverage-v01.zip')
    if not archive.exists():pytest.skip('Archive not bundled with GitHub tests')
    src,_=m.read_source(archive)
    out=m.run(src)
    assert out['n_source_runs']==3811
    assert out['comparison_counts']['strict_season14_lag16']['one_long_gap_per_route']['pairs']==123
    assert out['land_change_estimated'] is False
    assert out['source_is_not_outcome_independent_sample'] is True
