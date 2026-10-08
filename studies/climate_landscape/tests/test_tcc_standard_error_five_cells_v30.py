import importlib.util,sys
from pathlib import Path
import numpy as np
import pytest
root=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location("se",root/"audit_usfs_tcc_standard_error_five_cells_v30.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_uint16_unscale_and_mask():
    a=np.array([[0,1234,4500,65534,65535]],dtype=np.uint16)
    result,valid=m.validate_standard_error(a)
    assert result[0,0]==0
    assert result[0,1]==pytest.approx(12.34)
    assert result[0,2]==pytest.approx(45)
    assert valid.tolist()==[[True,True,True,False,False]]
    assert np.isnan(result[0,3]) and np.isnan(result[0,4])

def test_uint8_or_impossible_values_are_rejected():
    with pytest.raises(ValueError,match="U16"):
        m.validate_standard_error(np.array([100],dtype=np.uint8))
    with pytest.raises(ValueError,match="Implausible"):
        m.validate_standard_error(np.array([12001],dtype=np.uint16))

def test_change_screen_no_p_values_or_independence_assumption():
    row=m.compare_annual_se({2011:35,2012:8,2013:6},
      {2011:8,2012:7,2013:7})
    assert row["canopy_delta_2011_2013_pp"]==-29
    assert row["sum_marginal_SE_2011_2013"]==15
    assert row["diff_exceeds_sum_SE_2011_2013"]
    assert row["not_a_calibrated_uncertainty_interval"]
    assert "p_value" not in row

def test_small_change_not_robustly_larger_than_marginal_SE_sum():
    row=m.compare_annual_se({2011:3,2012:2,2013:3},
      {2011:10,2012:8,2013:11})
    assert row["canopy_delta_2011_2013_pp"]==0
    assert not row["diff_exceeds_sum_SE_2011_2013"]
    with pytest.raises(ValueError,match="Missing"):
      m.compare_annual_se({2011:3,2012:2,2013:3},
                           {2011:10,2012:float("nan"),2013:11})

def test_exact_population_frozen():
    assert m.YEARS==(2011,2012,2013)
    assert m.TARGETS=={"360104":("6613",3,3),"360412":("7247",7,2)}
