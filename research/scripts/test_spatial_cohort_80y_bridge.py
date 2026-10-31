"""Source and movement invariants for the PR146/147 common-kernel bridge."""
import unittest

import numpy as np

from spatial_cohort_80y_bridge import (
    pilot_cube, replay_gate, ring_mix, spatial_annual_recurrence
)


def tiny_cube():
    cube = pilot_cube(1)
    return cube[
        cube.context.eq("original")
        & cube.plant_model.eq("SF1_DF0_DS0_L1")
        & cube.reverse_on.eq(0)
    ].copy()


class SpatialCohortBridgeTests(unittest.TestCase):

    def test_conservative_ring_transfer(self):
        x = np.array([
            [[2., 0., 1.], [1., 3., 0.], [0., 0., 2.], [4., 2., 1.]],
            [[0., 2., 3.], [3., 0., 1.], [1., 1., 2.], [0., 4., 0.]],
        ])
        y = ring_mix(x, [0., .2, .8])
        np.testing.assert_allclose(y.sum(axis=1), x.sum(axis=1), atol=1e-12)
        self.assertTrue(np.all(y >= 0))
        np.testing.assert_array_equal(y[:, :, 0], x[:, :, 0])
        np.testing.assert_array_equal(ring_mix(x, [0, 0, 0]), x)

    def test_movement_input_fail_closed(self):
        with self.assertRaises(ValueError):
            ring_mix(np.ones((2, 4, 3)), [-.1, 0, 0])
        with self.assertRaises(ValueError):
            ring_mix(np.ones((2, 4, 3)), [1.1, 0, 0])
        with self.assertRaises(ValueError):
            ring_mix(np.ones((2, 1, 3)), [0, 0, 0])

    def test_no_movement_exactly_replays_pr146(self):
        errors = replay_gate(tiny_cube(), years=4, window=2, dt=.25)
        self.assertLess(errors["F_B"], 1e-8)
        self.assertLess(errors["F_fraction"], 1e-8)
        self.assertLess(errors["F_B_sd"], 1e-7)

    def test_homogeneous_transport_is_identity(self):
        cube = tiny_cube()
        no_move = spatial_annual_recurrence(
            cube, mode="off", landscape="homogeneous",
            years=4, window=2, dt=.25
        ).sort_values("vertex")
        both_move = spatial_annual_recurrence(
            cube, mode="both", transfer=.22, landscape="homogeneous",
            years=4, window=2, dt=.25
        ).sort_values("vertex")
        for var in ("F_B", "F_fraction", "F_B_sd"):
            np.testing.assert_allclose(no_move[var], both_move[var],
                                       rtol=0, atol=1e-10)
        np.testing.assert_allclose(both_move.effective_patches_F, 8, atol=1e-8)

    def test_mosaic_valid_source_native_readouts(self):
        cube = tiny_cube()
        for mode in ("off", "recruits", "carryover", "both"):
            p = spatial_annual_recurrence(
                cube, mode=mode, transfer=.15, landscape="mosaic",
                years=4, window=2, dt=.25
            )
            self.assertEqual(len(p), 8)
            self.assertTrue((p.F_B > 0).all())
            self.assertTrue(p.F_fraction.between(0, 1).all())
            self.assertTrue(p.effective_patches_F.between(1, 8+1e-8).all())
            self.assertTrue((p.min_patch_F_B <= p.max_patch_F_B).all())


if __name__ == "__main__":
    unittest.main()
