import unittest
import numpy as np
import pandas as pd
import tempfile
import json,hashlib
from unittest.mock import patch
from pathlib import Path
from refuge_response_20261029 import factor
from stage_refuge_generality_20261029 import simulate
from stage_handling_factorial_20261029 import simulate as original

class GeneralityTests(unittest.TestCase):
 def test_cache_rejects_changed_demography_and_output(self):
  from run_refuge_generality import simulate_design,computation_provenance,DEMOGRAPHY
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'cached.csv.gz';de=pd.DataFrame({'foo':[1]});de.to_csv(path,index=False)
   path.with_suffix('.gz.json').write_text(json.dumps(dict(computation=computation_provenance(.25),output_sha256=hashlib.sha256(path.read_bytes()).hexdigest())))
   pd.testing.assert_frame_equal(simulate_design(de,.25,path),de)
   with patch.dict(DEMOGRAPHY,{'initial_scale':999}):
    with self.assertRaisesRegex(ValueError,'provenance'):simulate_design(de,.25,path)
   pd.DataFrame({'foo':[2]}).to_csv(path,index=False)
   with self.assertRaisesRegex(ValueError,'provenance'):simulate_design(de,.25,path)
 def test_cache_without_code_provenance_is_rejected(self):
  from run_refuge_generality import simulate_design
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'cached.csv.gz';de=pd.DataFrame({'foo':[1]});de.to_csv(path,index=False)
   with self.assertRaisesRegex(ValueError,'provenance'):
    simulate_design(de,.25,path)
 def test_normalized_at_one(self):
  for family in ['constant','II','III','mixed','steep']:
   for k in [.5,1,2]:np.testing.assert_allclose(factor(np.ones(3),np.array([0,.5,1]),family,k),1.)
 def test_replay_old_kernel(self):
  p=[dict(cue=0,vegetation=v) for v in [0,.5,1]]
  pd.testing.assert_frame_equal(simulate(p,functional_response='litter',diagnostics=True),original(p,functional_response='litter',diagnostics=True),check_exact=True)
 def test_mixed_replays_old_factor(self):
  p=[dict(cue=0,vegetation=v) for v in [0,.5,1]]
  pd.testing.assert_frame_equal(simulate(p,response_family='mixed',diagnostics=True),original(p,functional_response='litter',diagnostics=True),check_exact=True)
 def test_absent_S_has_no_DS_edge_effect(self):
  p=[dict(community='FD',cue=0,vegetation=v) for v in [0,1]]
  a=simulate(p,response_family='III',pathway_controls={'edge_DS':0})
  b=simulate(p,response_family='III',pathway_controls={'edge_DS':1})
  pd.testing.assert_frame_equal(a,b,check_exact=True)
 def test_other_scales_conserve_cohorts(self):
  a=simulate([dict(cue=0,vegetation=1)],response_family='steep',response_scale=2,refuge_strength=.5).iloc[0]
  for g in 'FSD':self.assertAlmostEqual(a[g+'_dead']+a[g+'_survived'],1)

if __name__=='__main__':unittest.main()
