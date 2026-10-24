import unittest
from run_exact_k_environment import (
    JRC_SHA,PRIOR_ALPHA,PRIOR_BETA,MIN_PRIMARY_EVENTS,
    MIN_PRIMARY_ROUTES,MIN_SECONDARY_EVENTS,MIN_SECONDARY_ROUTES,
    MIN_SECONDARY_SPREAD_FRACTION
)
from exact_k_model import N_STOPS,N_FOLDS,LAMBDA

class PreOutcomeGuards(unittest.TestCase):
    def test_locked_acoustic_and_source_gates(self):
        self.assertEqual(N_STOPS,10)
        self.assertEqual(N_FOLDS,5)
        self.assertEqual(LAMBDA,1.)
        self.assertEqual((PRIOR_ALPHA,PRIOR_BETA),(.5,.5))
        self.assertEqual((MIN_PRIMARY_EVENTS,MIN_PRIMARY_ROUTES),(200,50))
        self.assertEqual((MIN_SECONDARY_EVENTS,MIN_SECONDARY_ROUTES),(100,30))
        self.assertEqual(MIN_SECONDARY_SPREAD_FRACTION,.10)
        self.assertEqual(JRC_SHA,"bd291a4f42a9768a4dfc2d92c68050344bde4e5b2bbb0a923a1218399e96f81b")

if __name__=="__main__":unittest.main()
