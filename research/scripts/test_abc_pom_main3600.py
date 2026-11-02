"""Tests of joint-prior structure sampling and exact factorial sign logic."""
import unittest
import numpy as np

from abc_pom_main3600 import accepted_signs, corner_contrasts, draw_prior, run_subset
from final_mechanism_common import catalog


class ABCPOMJointTest(unittest.TestCase):
    def test_known_factorial(self):
        z = np.zeros((1, 2, 2, 2))
        for v in range(2):
            for s in range(2):
                for d in range(2):
                    z[0, v, s, d] = -2*s*d - 2*v*d + 2*v*s + v*s*d
        result = corner_contrasts(z)
        np.testing.assert_allclose(result, [[-1.5, -1.5, 2.5, 1.0]], atol=1e-12)
        self.assertTrue(accepted_signs(result)[0])

    def test_null_signs_rejected(self):
        z = np.zeros((3, 2, 2, 2))
        self.assertFalse(accepted_signs(corner_contrasts(z)).any())

    def test_seed_shard_invariance(self):
        m = catalog()
        a = draw_prior(80, seed=11, models=m)
        b = draw_prior(80, seed=11, models=m)
        self.assertTrue(a.equals(b))
        ids = np.concatenate([a[a.draw_id % 7 == i].draw_id.to_numpy() for i in range(7)])
        self.assertEqual(sorted(ids.tolist()), list(range(80)))
        self.assertEqual(m.model_id.nunique(), 3600)

    def test_actual_kernel_integration_smoke(self):
        # Two genuine deterministic short-horizon runs; NOT scientific ABC estimates.
        m = catalog()
        p = draw_prior(4, seed=33, models=m).iloc[:2].copy()
        result = run_subset(p, m, years=2, window=1, dt=1.0, chunk=2)
        self.assertEqual(result.draw_id.tolist(), p.draw_id.tolist())
        self.assertEqual(len(result), 2)
        self.assertTrue(np.isfinite(result[["log_OS", "log_OV", "log_SV", "log_OSV"]]).all().all())
        self.assertTrue((result.min_F >= 0).all())
        self.assertTrue((result.min_F <= 1).all())


if __name__ == "__main__":
    unittest.main()
