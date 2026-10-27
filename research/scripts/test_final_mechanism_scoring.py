import unittest
import numpy as np
import pandas as pd
from final_mechanism_common import CELLS,score,catalog
from naamp_vegetation_network_associations import fit
from naamp_remote_vegetation_network import standardized_rank
from run_evidence_constrained import contrasts
class FinalScoring(unittest.TestCase):
 def test_rank_model_matches_macro_implementation(self):
  a=np.array(CELLS);v,s,d=a.T
  y=4-.3*d+.2*s-.1*s*d-.2*v*d+.3*v*s
  q=pd.DataFrame(dict(model_id=0,block_id=0,vegetation=v,S_source=s,D_source=d,F_B=y,F_fraction=np.exp(-d),audit_H_SF=0.,audit_H_DF=d,minimum_F_survival=np.exp(-d),minimum_S_survival=.2,F_B_sd=0.))
  got=score(q).iloc[0];expected=fit(d,s,standardized_rank(v),y,np.zeros(18),False)
  np.testing.assert_allclose([got.rank_DS,got.rank_DV,got.rank_SV,got.rank_DSV],expected[[3,4,5,6]],atol=1e-12)
 def test_catalog_unique_and_excludes_unverified_cue(self):
  q=catalog();self.assertEqual(len(q),3600);self.assertFalse(q.duplicated(q.columns.drop('model_id').tolist()).any());self.assertTrue(set(q.behavior)<= {'none','cue_SF','risk_refuge'})
if __name__=='__main__':unittest.main()
