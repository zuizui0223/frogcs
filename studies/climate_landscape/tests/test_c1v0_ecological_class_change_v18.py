import importlib.util
from pathlib import Path
import numpy as np
import pytest

SOURCE=Path(__file__).resolve().parents[1]/'scripts'/'audit_c1v0_ecological_class_change_v18.py'
spec=importlib.util.spec_from_file_location('c1v0_site_audit',SOURCE)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_81_82_agriculture_subclass_not_necessarily_terrestrial_group_conversion():
    old=np.array([[81,82],[81,41]],dtype=np.uint8)
    new=np.array([[82,81],[81,82]],dtype=np.uint8)
    out=audit.classify_transition(old,new)
    assert out['fine_class_changed_pixels']==3
    assert out['between_group_changed_pixels']==1
    assert out['within_group_changed_pixels']==2
    assert out['agricultural_81_82_changed_pixels']==2
    assert out['forest_to_agriculture_pixels']==1
    assert out['forest_to_developed_pixels']==0


def test_wetland_90_to_95_and_developed_21_to_24_tracked_separately():
    old=np.array([[90,21,41,82]],dtype=np.uint8)
    new=np.array([[95,24,23,41]],dtype=np.uint8)
    r=audit.classify_transition(old,new)
    assert r['fine_class_changed_pixels']==4
    assert r['between_group_changed_pixels']==2
    assert r['within_group_changed_pixels']==2
    assert r['wetland_90_95_changed_pixels']==1
    assert r['developed_intensity_changed_pixels']==1
    assert r['forest_to_developed_pixels']==1
    assert r['forest_gain_pixels']==1


def test_real_within_group_change_stays_zero_for_exactly_same_classes():
    x=np.array([11,21,81,82,90,95],dtype=np.uint8)
    o=audit.classify_transition(x,x)
    assert o['fine_class_changed_pixels']==0
    assert o['between_group_changed_pixels']==0


def test_unknown_source_classes_and_missing_pixels_fail_closed():
    old=np.array([[81,0]],dtype=np.uint8)
    new=np.array([[81,82]],dtype=np.uint8)
    with pytest.raises(ValueError,match='Unrecognized'):
        audit.classify_transition(old,new)


def test_pixel_grid_mismatch_fail_closed():
    with pytest.raises(ValueError,match='same-grid'):
        audit.classify_transition(np.array([81]),np.array([[81]]))


def test_site_mask_selects_exactly_same_nominal_pixels():
    old=np.array([[81,41],[21,90]],dtype=np.uint8)
    new=np.array([[82,82],[24,95]],dtype=np.uint8)
    r=audit.classify_transition(old,new,np.array([[True,False],[False,False]]))
    assert r['fine_class_changed_pixels']==1
    assert r['within_group_changed_pixels']==1
    assert r['between_group_changed_pixels']==0
