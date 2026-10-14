#!/usr/bin/env python3
"""Synthetic-only checks for exact-k site-configuration probabilities."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "exact_k_placement_kernel_v0_1.py"
spec = importlib.util.spec_from_file_location("exact_k", SCRIPT)
kernel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kernel)

def example(k=(1, 3), soil=0.0, guild=0, shift=0):
    observed = [int(i in k) for i in range(10)]
    forest = [0.1 + 0.08 * ((i + 2 * shift) % 10) for i in range(10)]
    history = [int((i + shift) % 3 == 0) for i in range(10)]
    conn = [
        [float(abs(i - j) == 1 and ((i + shift) % 2 == 0))
         for j in range(10)]
        for i in range(10)
    ]
    for i in range(10):
        for j in range(i + 1, 10):
            conn[i][j] = conn[j][i] = max(conn[i][j], conn[j][i])
    return {"q": [0.14 + 0.025 * i for i in range(10)],
            "observed": observed, "history": history, "forest": forest,
            "soil_change_z": soil, "guild": guild, "connection": conn,
            "response_state": "CI_ge_1", "q_response_state": "CI_ge_1",
            "connection_source": "synthetic"}

class ConditionalSiteTests(unittest.TestCase):
    def setUp(self):
        self.zero = np.zeros(len(kernel.FEATURE_NAMES), dtype=float)

    def test_exact_k_normalization_and_null_bernoulli_weights(self):
        data = example(k=(1, 7))
        choices, probs, matched = kernel.event_pmf(data, self.zero)
        self.assertEqual(len(choices), 45)
        self.assertAlmostEqual(float(probs.sum()), 1.0, places=12)
        q = np.array(data["q"])
        expected = np.prod(q[choices] / (1 - q[choices]), axis=1)
        expected /= expected.sum()
        np.testing.assert_allclose(probs, expected, rtol=1e-12)
        self.assertEqual(tuple(choices[matched]), (1, 7))

    def test_hydric_state_only_enters_conditional_placement_through_site_contrast(self):
        wetter = example(k=(0,), soil=2.0)
        drier = example(k=(0,), soil=-2.0)
        beta = self.zero.copy()
        beta[kernel.FEATURE_NAMES.index("soil_by_history")] = 1.0
        s_w, p_w, _ = kernel.event_pmf(wetter, beta)
        s_d, p_d, _ = kernel.event_pmf(drier, beta)
        self.assertGreater(sum(p_w[i] for i, row in enumerate(s_w)
                               if wetter["history"][int(row[0])]),
                           sum(p_d[i] for i, row in enumerate(s_d)
                               if drier["history"][int(row[0])]))
        # If every site has the same history flag, this term cancels at fixed k.
        wetter["history"] = [1] * 10
        s1, p1, _ = kernel.event_pmf(wetter, beta)
        _, p0, _ = kernel.event_pmf(wetter, self.zero)
        np.testing.assert_allclose(p1, p0, atol=1e-12)

    def test_connection_parameter_needs_two_or_more_active_sites(self):
        event = example(k=(0,), soil=0)
        beta = self.zero.copy()
        beta[kernel.FEATURE_NAMES.index("connected_forest_pairs")] = 3.0
        _, p0, _ = kernel.event_pmf(event, self.zero)
        _, p1, _ = kernel.event_pmf(event, beta)
        np.testing.assert_allclose(p1, p0, atol=1e-12)
        event["observed"] = [int(i in (0, 1)) for i in range(10)]
        _, p2, _ = kernel.event_pmf(event, beta)
        _, pbase, _ = kernel.event_pmf(event, self.zero)
        self.assertGreater(float(np.max(p2 - pbase)), 0)

    def test_fail_closed_on_threshold_conflict_and_fake_connection(self):
        event = example()
        event["q_response_state"] = "CI_ge_2"
        with self.assertRaisesRegex(ValueError, "must match"):
            kernel.event_design(event)
        event["q_response_state"] = "CI_ge_1"
        event["connection_source"] = "geometric_proximity_is_forest"
        with self.assertRaisesRegex(ValueError, "independently classified"):
            kernel.event_design(event)

    def test_fail_closed_on_noninformative_all_or_no_sites(self):
        for observed in ([0] * 10, [1] * 10):
            event = example()
            event["observed"] = observed
            with self.assertRaisesRegex(ValueError, "no conditional placement information"):
                kernel.event_design(event)

    def test_training_fit_and_heldout_score_are_synthetic_only(self):
        events = []
        for t in range(24):
            chosen = ((t + 1) % 10, (t + 4) % 10, (t + 7) % 10)
            e = example(k=chosen, soil=float((t % 5) - 2),
                        guild=t % 2, shift=t % 10)
            events.append(e)
        model = kernel.fit_train_only(events[:18], kernel.FEATURE_NAMES, ridge=1.0)
        self.assertEqual(model["rank"], 5)
        self.assertEqual(model["n_training_events"], 18)
        heldout = kernel.heldout_comparison(events[18:], model["beta"])
        self.assertEqual(heldout["n_heldout_events"], 6)
        self.assertTrue(np.isfinite(heldout["mean_logscore_gain_per_event"]))
        self.assertFalse(heldout["independent_confirmation"])

    def test_collinear_predictors_blocked(self):
        e = example()
        e["history"] = [1] * 10
        with self.assertRaisesRegex(ValueError, "unidentifiable"):
            kernel.fit_train_only([e],
                                  ["extra_history", "soil_by_history"], ridge=1.0)

    def test_log_probability_stable_under_large_effect(self):
        e = example(k=(0, 3))
        b = self.zero.copy()
        b[0] = 500.0
        # Scoring remains finite even if normalized raw probabilities underflow.
        value = kernel.event_logprob(e, b)
        self.assertTrue(np.isfinite(value))
        self.assertLessEqual(value, 0.0)

if __name__ == "__main__":
    unittest.main()
