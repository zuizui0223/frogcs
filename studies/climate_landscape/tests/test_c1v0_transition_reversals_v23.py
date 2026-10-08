import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_c1v0_transition_reversals_v23 import classify_three

def test_full_partition_reversal_persistence_and_third_category():
    before=np.array([[5,5,5,5],[8,8,8,8]],dtype=np.uint8)
    during=np.array([[8,8,8,5],[5,5,8,8]],dtype=np.uint8)
    after=np.array([[5,8,3,5],[8,5,8,8]],dtype=np.uint8)
    mask=np.ones((2,4),dtype=bool)
    rec=classify_three(before,during,after,mask)
    assert rec['functional_group_changed_pixels']==5
    assert rec['one_year_reversed_group_pixels']==2
    assert rec['following_year_same_new_group_pixels']==2
    assert rec['third_group_next_year_pixels']==1
    assert rec['forest_group_loss_pixels']==3
    assert rec['forest_loss_reverted_next_year_pixels']==1
    assert rec['forest_loss_persisted_nonforest_next_year_pixels']==2

def test_source_mismatch_and_invalid_mask_fail():
    x=np.ones((2,2),dtype=np.uint8)
    with pytest.raises(ValueError,match='Array shape'):
        classify_three(x,x,np.ones((2,3),dtype=np.uint8),np.ones((2,2),dtype=bool))
    with pytest.raises(ValueError,match='classified'):
        classify_three(x,x,np.full((2,2),10,dtype=np.uint8),np.ones((2,2),dtype=bool))
    with pytest.raises(ValueError,match='boolean'):
        classify_three(x,x,x,np.ones((2,2),dtype=np.uint8))
