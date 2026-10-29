import unittest
import numpy as np
from separate_mechanism_observation import components


class ObservationComponentsTests(unittest.TestCase):
    def test_nested_event_factorization(self):
        r=components([0,.2,.8],[.1,.5,1.])
        np.testing.assert_allclose(r[:,2],[0,.4,.8])
        np.testing.assert_allclose(r[:,0],r[:,1]*r[:,2])

    def test_zero_or_non_nested_rejected(self):
        for strong,any_call in [([0],[0]),([.6],[.5])]:
            with self.assertRaises(ValueError):components(strong,any_call)


if __name__=='__main__':unittest.main()
