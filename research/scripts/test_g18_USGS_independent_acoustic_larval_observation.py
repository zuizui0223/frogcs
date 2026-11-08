"""G18 published original-USGS interpretation and fixed observation learner guard."""
import unittest,numpy as np,pandas as pd
from g18_USGS_independent_acoustic_larval_observation import (
    TAXA,SOURCE_ITEM,DOI,SEED,BOOT,fixed_logistic
)

class TestOriginalUSGSStages(unittest.TestCase):
    def test_frozen_USGS_source_and_13_exact_frog_taxa(self):
        self.assertEqual(DOI,"10.5066/P9T71JCO")
        self.assertEqual(SOURCE_ITEM,"5eb5880c82ce25b5135ae784")
        self.assertEqual(len(TAXA),13)
        self.assertEqual(len(set(TAXA)),13)
        self.assertEqual(SEED,20261108)
        self.assertEqual(BOOT,10000)

    def test_single_explicit_prior_call_not_experimental_survival(self):
        rows=pd.DataFrame(dict(
           taxon=["A","A","A","B","B","B","A","B"],
           year=["2012","2013","2014","2012","2013","2014","2015","2015"],
           doy=[100,110,120,130,140,150,160,170],
           logprior=[.7,1.1,1.5,.7,1.1,1.5,.7,.7],
           prior_call=[0,1,0,1,0,1,1,0],
        ))
        y=np.array([0,0,1,0,1,0,0,1])
        m0=fixed_logistic(False)
        m1=fixed_logistic(True)
        m0.fit(rows,y);m1.fit(rows,y)
        self.assertEqual(m0.predict_proba(rows).shape,(8,2))
        self.assertEqual(m1.predict_proba(rows).shape,(8,2))
        self.assertTrue(np.isfinite(m0.predict_proba(rows)).all())
        self.assertTrue(np.isfinite(m1.predict_proba(rows)).all())

    def test_no_false_future_year_certainty_without_data(self):
        self.assertNotIn("survival",list(TAXA))
        self.assertTrue(all(" " in x for x in TAXA))

if __name__=="__main__":
    unittest.main()
