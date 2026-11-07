"""G8 source design and audit guards (no outcome-selected rates)."""
from __future__ import annotations

import unittest
import numpy as np
import pandas as pd

from run_g8_27rate_paired_factorial import (
    RATE_GRID, EXPECTED_ROWS, make_grid, v0_negative_control,
)
from audit_g8_27rate_paired_factorial import response_contrasts, summarize

COLUMNS = ("F_B", "S_B", "D_B", "F_fraction", "audit_H_SF",
           "audit_H_DF", "audit_H_DS", "audit_H_SD",
           "minimum_F_survival", "minimum_S_survival")


def negative_control_data():
    rows = []
    for arm in ("00", "10", "01", "11"):
        for vertex in range(8):
            v = int(vertex >= 4)
            row = dict(source_id=0, rate_id=0, context_id=0, arm=arm,
                       vertex=vertex, vegetation=v)
            for col in COLUMNS:
                row[col] = 1. + float(v) * (int(arm, 2) + 1)
            rows.append(row)
    return pd.DataFrame(rows)


def complete_toy_full():
    """Truth known before fitting: every 11 succeeds yet lowers frog abundance."""
    grid = np.stack(np.meshgrid(np.arange(256), np.arange(27),
                                np.arange(3), np.arange(4),
                                indexing="ij"), axis=-1).reshape(-1, 4)
    sid, rate, stage, arm_index = grid.T
    return pd.DataFrame(dict(
        source_id=sid, rate_id=rate, context_id=stage,
        arm=np.array(("00","10","01","11"))[arm_index],
        attack=np.array([v[0] for v in RATE_GRID])[rate],
        rho=np.array([v[1] for v in RATE_GRID])[rate],
        conversion=np.array([v[2] for v in RATE_GRID])[rate],
        accepted=arm_index == 3,
        accepted_and_floor=arm_index == 3,
        mean_log_F_B=-(arm_index == 3).astype(float),
    ))


class TestG8DesignAndAudit(unittest.TestCase):
    def test_exact_27_rate_grid(self):
        self.assertEqual(len(RATE_GRID), 27)
        self.assertEqual(len(set(RATE_GRID)), 27)
        self.assertEqual(EXPECTED_ROWS, 82944)
        self.assertEqual(RATE_GRID[0], (0.5, 0.25, 2.0))
        self.assertEqual(RATE_GRID[-1], (3.0, 0.75, 8.0))

    def test_source_backgrounds_legal_and_nuisance_paired(self):
        models, p, _ = make_grid(source_ids=(0,1), rate_ids=(0,13,26),
                                  contexts=(0,1))
        self.assertEqual(len(models), 3600)
        self.assertEqual(len(p), 48)
        self.assertEqual(len(set(p.draw_id)), 48)
        self.assertTrue(p.groupby(["source_id", "rate_id", "context_id"])
                        .arm.nunique().eq(4).all())
        self.assertTrue(p.groupby("source_id")[["strength", "refuge_order", "gate_code"]]
                        .nunique().max().max() == 1)
        self.assertTrue(p.groupby(["source_id", "rate_id", "context_id"])
                        .model_id.nunique().eq(4).all())

    def test_duplicate_or_invalid_rate_requests_rejected(self):
        with self.assertRaises(AssertionError):
            make_grid(source_ids=(0,), rate_ids=(0,0), contexts=(0,))
        with self.assertRaises(AssertionError):
            make_grid(source_ids=(0,), rate_ids=(27,), contexts=(0,))

    def test_no_vegetation_shall_not_depend_on_plant_arm(self):
        self.assertAlmostEqual(v0_negative_control(negative_control_data()), 0.0)
        broken = negative_control_data()
        broken.loc[(broken.arm == "11") & (broken.vertex == 0), "F_B"] += 0.01
        with self.assertRaises(AssertionError):
            v0_negative_control(broken)

    def test_known_paired_compatibility_and_demographic_discordance(self):
        effects = complete_toy_full()
        values = response_contrasts(effects)
        self.assertEqual(len(values), 256*27*3)
        self.assertTrue(values.compatibility.eq(1).all())
        self.assertTrue(values.factorial_compatibility.eq(1).all())
        self.assertTrue(values.viable_compatibility.eq(1).all())
        self.assertTrue(values.frog_log_cohort.eq(-1).all())
        summary = summarize(values, boot=39, seed=123)
        x = summary.set_index(["rate_id","context","metric"])
        self.assertEqual(len(summary), (27*4+1)*6)
        self.assertEqual(x.loc[("pooled_27","pooled_3","compatibility"), "mean"], 1)
        self.assertEqual(x.loc[("pooled_27","pooled_3","frog_log_cohort"), "mean"], -1)
        self.assertEqual(x.loc[("12","pooled_3","compatibility"), "pointwise_mc95_low"], 1)

    def test_incomplete_grid_fails_closed(self):
        with self.assertRaises(AssertionError):
            response_contrasts(complete_toy_full().iloc[:-1])


if __name__ == "__main__":
    unittest.main()
