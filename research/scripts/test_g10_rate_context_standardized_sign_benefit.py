"""G10 tests: direction, undefined support, exact pair standardization."""
import unittest
import numpy as np

from g10_rate_context_standardized_sign_benefit import compare


class TestG10WithinStratumStandardization(unittest.TestCase):
    @staticmethod
    def fixture(loss1=1,loss0=2):
        n1=np.array([2.,0.]);n0=np.array([2.,0.])
        z=np.array([0.,0.])
        a=({"n":n1,"loss":np.array([float(loss1),0.]),"delta":np.array([-.4,0.])},
           {"n":np.tile(n1,(3,1)),"loss":np.tile(np.array([float(loss1),0.]),(3,1)),
            "delta":np.tile(np.array([-.4,0.]),(3,1))})
        b=({"n":n0,"loss":np.array([float(loss0),0.]),"delta":np.array([-.8,0.])},
           {"n":np.tile(n0,(3,1)),"loss":np.tile(np.array([float(loss0),0.]),(3,1)),
            "delta":np.tile(np.array([-.8,0.]),(3,1))})
        return a,b

    def test_loss_standardization_sign_and_scale(self):
        a,b=self.fixture()
        x=compare(a,b,np.array([True,True]))
        self.assertEqual(x["n_supported_strata"],1)
        self.assertEqual(x["new_cases_covered"],2)
        self.assertAlmostEqual(x["p_loss_new"],.5)
        self.assertAlmostEqual(x["p_loss_comparator_standardized"],1.)
        self.assertAlmostEqual(x["adjusted_loss_difference_pp"],-50.)
        self.assertEqual(x["bootstrap_valid"],3)
        self.assertAlmostEqual(x["adjusted_log_difference"],.2)

    def test_no_supported_stratum_stops(self):
        a,b=self.fixture()
        with self.assertRaises(AssertionError):
            compare(a,b,np.array([False,True]))

    def test_zero_comparator_draw_must_not_be_inferred(self):
        a,b=self.fixture()
        b[1]["n"][0,0]=0
        x=compare(a,b,np.array([True,False]))
        self.assertEqual(x["bootstrap_valid"],2)


if __name__=="__main__":
    unittest.main()
