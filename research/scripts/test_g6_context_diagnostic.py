"""Behavior tests for fixed-prediction G6 context diagnostics.

The fixtures are artificial; no original frog outcomes or G6 results are read.
"""
import math
import unittest

import numpy as np
import pandas as pd

try:
    from g6_context_diagnostic import analyze_contexts
except ModuleNotFoundError as exc:
    if exc.name != "g6_context_diagnostic":
        raise
    analyze_contexts = None


# Deliberately independent of the production module's candidate registry.
MODEL_NAMES = (
    "env_add", "env_all", "flex_add", "flex_all",
    "flex_prior_00", "flex_prior_11",
)


def paired_rows(records):
    """Duplicate an explicitly specified site fixture into the two SDM designs."""
    rows = []
    for background in ("uniform", "target_group"):
        for record in records:
            row = {
                "background": background,
                "caudata_tertile": 0,
                "odonata_tertile": 0,
                **{model: 0.5 for model in MODEL_NAMES},
                **record,
            }
            rows.append(row)
    return pd.DataFrame(rows)


def tiny_fixture():
    # Unequal visits make a site-mean implementation observably wrong.
    return paired_rows([
        dict(site="a", route="r0", spatial_block="b0", V=0,
             n_completed=1, k_strong=1, flex_prior_11=0.8),
        dict(site="b", route="r1", spatial_block="b1", V=1,
             n_completed=3, k_strong=0, flex_prior_11=0.2),
    ])


class FixedPredictionContextTests(unittest.TestCase):
    def analyze(self, frame, **kwargs):
        self.assertTrue(
            callable(analyze_contexts),
            "G6 analyze_contexts is not implemented yet",
        )
        return analyze_contexts(frame, **kwargs)

    def test_visit_weighted_calibration_and_proper_scores(self):
        # Catches replacing the visit-weighted average with a site average,
        # treating k/n as one Bernoulli event, or reversing the residual sign.
        data = tiny_fixture()
        original = data.copy(deep=True)
        result = self.analyze(data, bootstrap=8, seed=7)
        row = result["scores"].query(
            "background == 'uniform' and partition == 'all' "
            "and candidate == 'flex_prior_11'"
        ).iloc[0]
        self.assertEqual(row.sites, 2)
        self.assertEqual(row.visits, 4)
        self.assertEqual(row.strong_events, 1)
        self.assertAlmostEqual(row.observed_rate, 0.25, places=14)
        self.assertAlmostEqual(row.predicted_rate, 0.35, places=14)
        self.assertAlmostEqual(row.residual, -0.10, places=14)
        self.assertAlmostEqual(row.nll_per_visit, -math.log(0.8), places=14)
        self.assertAlmostEqual(row.brier_per_visit, 0.04, places=14)
        pd.testing.assert_frame_equal(data, original)

    def test_every_partition_reconstructs_the_original_global_gain(self):
        # Catches normalizing cell contributions by cell visits or averaging
        # cells equally, which would overstate the one-visit stratum.
        result = self.analyze(tiny_fixture(), bootstrap=8, seed=7)
        gain = math.log(1.6)  # log(0.8 / 0.5), independently derived.
        g = result["gains"]
        for background in ("uniform", "target_group"):
            for baseline in ("flex_add", "flex_prior_00", "flex_all", "env_add"):
                rows = g[(g.background == background) & (g.baseline == baseline)]
                for partition in ("all", "V", "V_S", "V_S_O"):
                    selected = rows[rows.partition == partition]
                    self.assertAlmostEqual(
                        selected.full_total_weighted_contribution.sum(), gain, places=13,
                    )
                v0 = rows[rows.stratum == "V0"].iloc[0]
                v1 = rows[rows.stratum == "V1"].iloc[0]
                self.assertAlmostEqual(v0.gain_per_visit, gain, places=13)
                self.assertAlmostEqual(v1.gain_per_visit, gain, places=13)
                self.assertAlmostEqual(v0.full_total_weighted_contribution, gain / 4, places=13)
                self.assertAlmostEqual(v1.full_total_weighted_contribution, 3 * gain / 4, places=13)

    def test_empty_and_unsupported_strata_are_retained_without_intervals(self):
        # Catches silently dropping empty or rare source cells and presenting
        # a conditional interval as if a cell had passed the support rule.
        result = self.analyze(tiny_fixture(), bootstrap=8, seed=7)
        self.assertEqual(set(result), {"scores", "gains", "heterogeneity", "support"})
        self.assertEqual(len(result["support"]), 54)
        self.assertEqual(len(result["scores"]), 324)
        self.assertEqual(len(result["gains"]), 216)
        self.assertEqual(len(result["heterogeneity"]), 8)
        empty = result["support"].query(
            "background == 'uniform' and stratum == 'V0_S2_O2'"
        ).iloc[0]
        self.assertEqual((empty.sites, empty.routes, empty.blocks, empty.visits), (0, 0, 0, 0))
        self.assertFalse(empty.supported)
        empty_gain = result["gains"].query(
            "background == 'uniform' and stratum == 'V0_S2_O2' "
            "and baseline == 'flex_add'"
        ).iloc[0]
        self.assertTrue(math.isnan(empty_gain.gain_per_visit))
        self.assertEqual(empty_gain.full_total_weighted_contribution, 0.0)
        self.assertEqual(empty_gain.invalid_gain_draws, 8)
        self.assertEqual(empty_gain.invalid_contribution_draws, 0)
        self.assertTrue(result["gains"].gain_ci_low.isna().all())
        self.assertTrue(result["gains"].contribution_ci_high.isna().all())

    def test_paired_block_draws_count_absent_cells_and_use_one_shared_draw(self):
        # For two blocks, seed 7 gives eight multinomial counts:
        # (1,1),(2,0),(2,0),(0,2),(1,1),(2,0),(0,2),(2,0).
        # These literal counts catch independent resampling of V0/V1 or
        # backgrounds and silent deletion of zero-denominator replicates.
        result = self.analyze(tiny_fixture(), bootstrap=8, seed=7)
        for background in ("uniform", "target_group"):
            rows = result["gains"].query(
                "background == @background and baseline == 'flex_add' and partition == 'V'"
            ).set_index("stratum")
            self.assertEqual(int(rows.loc["V0", "invalid_gain_draws"]), 2)
            self.assertEqual(int(rows.loc["V1", "invalid_gain_draws"]), 4)
            heterogeneity = result["heterogeneity"].query(
                "background == @background and baseline == 'flex_add'"
            ).iloc[0]
            self.assertEqual(heterogeneity.invalid_draws, 6)
            self.assertAlmostEqual(heterogeneity.difference_v1_minus_v0, 0.0, places=14)

    def test_identical_predictions_have_exactly_zero_gains_and_supported_intervals(self):
        # Catches subtraction/order/aggregation bugs without deriving expected
        # answers from the same scoring helper as the implementation.
        records = []
        for i in range(48):
            records.append(dict(
                site=f"s{i:02d}", route=f"r{i // 4:02d}",
                spatial_block=f"b{i // 12}", V=i % 2,
                caudata_tertile=(i // 2) % 3,
                odonata_tertile=(i // 6) % 3,
                n_completed=10, k_strong=i % 11,
            ))
        result = self.analyze(paired_rows(records), bootstrap=32, seed=7)
        gains = result["gains"]
        present = gains[gains.visits > 0]
        self.assertTrue((present.gain_per_visit == 0.0).all())
        self.assertTrue((gains.full_total_weighted_contribution == 0.0).all())
        supported = gains[gains.supported]
        self.assertEqual(set(supported.partition), {"all", "V"})
        self.assertTrue((supported.gain_ci_low == 0.0).all())
        self.assertTrue((supported.gain_ci_high == 0.0).all())
        self.assertTrue((supported.contribution_ci_low == 0.0).all())
        self.assertTrue((supported.contribution_ci_high == 0.0).all())
        h = result["heterogeneity"]
        self.assertTrue(h.supported_v0.all() and h.supported_v1.all())
        self.assertTrue((h.difference_v1_minus_v0 == 0.0).all())
        self.assertTrue((h.ci_low == 0.0).all() and (h.ci_high == 0.0).all())

    def test_rejects_duplicate_unpaired_and_inconsistent_background_metadata(self):
        # Catches pooling duplicates, silently inner-joining backgrounds, or
        # comparing different observed visits under different SDM designs.
        base = tiny_fixture()
        duplicate = pd.concat([base, base.iloc[[0]]], ignore_index=True)
        unpaired = base.drop(index=2).reset_index(drop=True)
        unknown = base.copy()
        unknown.loc[unknown.background == "target_group", "background"] = "other"
        inconsistent = base.copy()
        inconsistent.loc[2, "n_completed"] = 2
        for label, bad in (
            ("duplicate", duplicate), ("unpaired", unpaired),
            ("unknown background", unknown), ("metadata", inconsistent),
        ):
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    self.analyze(bad, bootstrap=8, seed=7)

    def test_rejects_invalid_counts_probabilities_and_predictor_labels(self):
        # Catches clipping invalid source predictions or accepting fractional
        # visits and out-of-range bins as ordinary field observations.
        changes = (
            ("n_completed", 0), ("n_completed", 1.5),
            ("k_strong", 2), ("k_strong", -1), ("k_strong", 0.5),
            ("env_all", 0.0), ("env_all", 1.0),
            ("flex_prior_11", np.nan), ("V", 2),
            ("caudata_tertile", 3), ("odonata_tertile", -1),
            ("route", None),
        )
        for column, value in changes:
            with self.subTest(column=column, value=value):
                frame = tiny_fixture().astype({"n_completed": float, "k_strong": float})
                frame.loc[0, column] = value
                with self.assertRaises(ValueError):
                    self.analyze(frame, bootstrap=8, seed=7)
        with self.assertRaises(ValueError):
            self.analyze(tiny_fixture(), bootstrap=0, seed=7)


if __name__ == "__main__":
    unittest.main()
