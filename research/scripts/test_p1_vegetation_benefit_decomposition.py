"""Behavior checks for complete paired P1 decomposition, using known toy outcomes."""
from __future__ import annotations

import unittest
import numpy as np
import pandas as pd

try:
    import p1_vegetation_benefit_decomposition as analysis
except ModuleNotFoundError:
    analysis = None


def toy_effects():
    # Hand-specified arm outcomes: net effects are -1, -1, 0, +1.
    rows = []
    arms = {"LS": (10, 11, 8, 9), "LL": (10, 11, 8, 9),
            "ES": (10, 12, 9, 10), "EL": (10, 13, 9, 11)}
    for source in range(3):
        for stage, vals in arms.items():
            for arm, value in zip(("00", "10", "01", "11"), vals):
                rows.append(dict(source_id=source, stage_design=stage, arm=arm,
                                 mean_log_F_B=value + source))
    return pd.DataFrame(rows)


class PairedDecompositionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(analysis, "P1 decomposition implementation is missing")

    def test_known_opposing_paths_and_negative_interaction(self):
        d = analysis.decompose(toy_effects(), expected_sources=3)
        rows = d.set_index(["source_id", "timing"])
        np.testing.assert_allclose(rows.loc[(0, "LS"), list(analysis.TERMS)],
                                   [1, -2, 0, -1])
        np.testing.assert_allclose(rows.loc[(0, "EL"), list(analysis.TERMS)],
                                   [3, -1, -1, 1])

    def test_source_order_does_not_change_pairing(self):
        a = analysis.decompose(toy_effects(), expected_sources=3)
        b = analysis.decompose(toy_effects().sample(frac=1, random_state=9),
                               expected_sources=3)
        pd.testing.assert_frame_equal(a, b)

    def test_missing_or_duplicated_arm_is_rejected(self):
        x = toy_effects()
        with self.assertRaises(ValueError):
            analysis.decompose(x.iloc[1:], expected_sources=3)
        with self.assertRaises(ValueError):
            analysis.decompose(pd.concat([x, x.iloc[:1]]), expected_sources=3)

    def test_nonfinite_and_lost_arm_labels_are_rejected(self):
        x = toy_effects()
        x.loc[0, "mean_log_F_B"] = np.nan
        with self.assertRaises(ValueError):
            analysis.decompose(x, expected_sources=3)
        x = toy_effects()
        x["arm"] = x.arm.astype(int)
        with self.assertRaises(ValueError):
            analysis.decompose(x, expected_sources=3)

    def test_shared_resampling_preserves_decomposition_and_moderators(self):
        d = analysis.decompose(toy_effects(), expected_sources=3)
        summary, draws, labels, indices = analysis.summarize(d, n_boot=99, seed=12)
        self.assertEqual(len(summary), 32)
        self.assertEqual(indices.shape, (99, 3))
        for kind, contrast in [("timing", t) for t in analysis.TIMINGS] + [
                ("change", t) for t in analysis.CHANGES]:
            ix = [labels.index((kind, contrast, term)) for term in analysis.TERMS]
            np.testing.assert_allclose(draws[:, ix[:3]].sum(axis=1), draws[:, ix[3]])
        change = summary[(summary.kind == "change") &
                         (summary.contrast == "EL_minus_LS")].set_index("term")
        np.testing.assert_allclose(change.loc[list(analysis.TERMS), "mean"], [2, 1, -1, 2])

    def test_real_sign_reversal_is_distinct_from_a_positive_shift(self):
        d = analysis.decompose(toy_effects(), expected_sources=3)
        counts, transitions = analysis.sign_counts(d)
        self.assertTrue(counts.set_index("timing").loc["ES", "zero"] == 3)
        self.assertTrue((transitions.LS_sign == "negative").all())
        self.assertTrue((transitions.EL_sign == "positive").all())
        self.assertTrue(transitions.negative_to_positive.all())
        # A positive shift can leave the endpoint negative.
        d.loc[d.timing == "EL", "net"] = -0.5
        _, transitions = analysis.sign_counts(d)
        self.assertTrue((transitions["shift"] > 0).all())
        self.assertFalse(transitions.negative_to_positive.any())


if __name__ == "__main__":
    unittest.main()
