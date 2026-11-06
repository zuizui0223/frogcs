"""Behavioral checks for a retrospective, fixed-prediction R1 rank diagnostic."""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

try:
    import g6_rank_pattern_diagnostic as diagnostic
except ModuleNotFoundError:
    diagnostic = None


CANDIDATES = (
    "env_add", "env_all", "flex_add", "flex_all", "flex_prior_00", "flex_prior_11"
)


def fixture() -> pd.DataFrame:
    """Each V/S group has exactly 20 sites, 5 routes, 4 blocks and 200 visits."""
    rows = []
    for vegetation in (0, 1):
        for s_group in (0, 2):
            for i in range(20):
                x = i / 19
                observed = .1 + .8 * x if s_group == 0 else .9 - .8 * x
                row = dict(
                    background="uniform", site=f"{vegetation}-{s_group}-{i}",
                    route=f"r-{vegetation}-{s_group}-{i % 5}",
                    spatial_block=f"b{i % 4}", V=vegetation,
                    caudata_tertile=s_group, odonata_suitability=x,
                    observed_rate=observed, n_completed=10,
                )
                row.update({name: observed for name in CANDIDATES})
                row["env_add"] = 1 - observed
                rows.append(row)
    return pd.DataFrame(rows)


class RankPatternDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(
            diagnostic,
            "G6 rank-pattern production module is absent; implement the fixed-prediction diagnostic",
        )

    def test_frequency_weighted_tied_ranks_match_literal_cluster_duplication(self):
        # A bug using unweighted ranks would fail the second and third draws.
        x = np.array([0., 0., 1., 2.])
        y = np.array([1., 0., 1., 0.])
        weights = np.array([[1, 1, 1, 1], [2, 1, 3, 1], [0, 2, 1, 4]])
        expected = [
            spearmanr(np.repeat(x, w), np.repeat(y, w)).statistic for w in weights
        ]
        actual = diagnostic._weighted_spearman(x, y, weights)
        np.testing.assert_allclose(actual, expected, atol=1e-14, rtol=0)

    def test_same_operator_retains_known_high_minus_low_and_paired_discrepancy(self):
        # A reversed high-minus-low sign or model/observed pairing fails here.
        data = fixture()
        before = data.copy(deep=True)
        result = diagnostic.summarize_rank_patterns(data, bootstrap=31, seed=42)
        self.assertEqual(len(result), 21)
        obs = result.query("subset == 'all' and response == 'observed_rate'").iloc[0]
        pred = result.query("subset == 'all' and response == 'env_add'").iloc[0]
        self.assertAlmostEqual(obs.rho_low, 1.)
        self.assertAlmostEqual(obs.rho_high, -1.)
        self.assertAlmostEqual(obs.contrast_high_minus_low, -2.)
        self.assertAlmostEqual(pred.contrast_high_minus_low, 2.)
        self.assertAlmostEqual(pred.predicted_minus_observed, 4.)
        self.assertAlmostEqual(pred.discrepancy_ci_low, 4.)
        self.assertAlmostEqual(pred.discrepancy_ci_high, 4.)
        self.assertTrue(result.supported.all())
        self.assertTrue(result.bootstrap_invalid.eq(0).all())
        pd.testing.assert_frame_equal(data, before)

    def test_whole_background_block_resampling_matches_raw_paired_reconstruction(self):
        # Sampling only blocks present in a selected group would fail this test.
        data = fixture()
        for i, row in data.iterrows():
            number = int(row.site.split("-")[-1])
            data.loc[i, "env_all"] = (
                .5 + .4 * np.sin(number) if row.caudata_tertile == 0
                else ((number * 7) % 20) / 20
            )
        middle = data.iloc[:5].copy()
        middle["site"] = [f"middle-{i}" for i in range(len(middle))]
        middle["spatial_block"] = "b4"
        middle["caudata_tertile"] = 1
        data = pd.concat([data, middle], ignore_index=True)
        blocks = sorted(data.spatial_block.unique())
        draws = np.random.default_rng(17).integers(0, len(blocks), size=(71, len(blocks)))
        discrepancies = []
        for draw in draws:
            repeated = pd.concat([data[data.spatial_block.eq(blocks[i])] for i in draw])
            repeated = repeated[repeated.V.eq(1)]
            low = repeated[repeated.caudata_tertile.eq(0)]
            high = repeated[repeated.caudata_tertile.eq(2)]
            observed = (
                spearmanr(high.odonata_suitability, high.observed_rate).statistic
                - spearmanr(low.odonata_suitability, low.observed_rate).statistic
            )
            predicted = (
                spearmanr(high.odonata_suitability, high.env_all).statistic
                - spearmanr(low.odonata_suitability, low.env_all).statistic
            )
            discrepancies.append(predicted - observed)
        expected = np.quantile(discrepancies, [.025, .975])
        result = diagnostic.summarize_rank_patterns(data, bootstrap=71, seed=17)
        selected = result.query("subset == 'V1' and response == 'env_all'").iloc[0]
        np.testing.assert_allclose(
            [selected.discrepancy_ci_low, selected.discrepancy_ci_high],
            expected, atol=1e-13, rtol=0,
        )
        self.assertEqual(selected.source_blocks, 5)

    def test_sparse_groups_are_retained_without_an_interval(self):
        # Lowering the prespecified site/visit support limits would fail here.
        data = fixture()
        data = data[~data.site.isin(["1-0-18", "1-0-19"])].copy()
        result = diagnostic.summarize_rank_patterns(data, bootstrap=19, seed=4)
        v1 = result[result.subset.eq("V1")]
        self.assertEqual(len(v1), 7)
        self.assertFalse(v1.supported.any())
        self.assertTrue(v1.low_sites.eq(18).all())
        self.assertTrue(v1.low_visits.eq(180).all())
        self.assertTrue(v1.contrast_ci_low.isna().all())
        self.assertTrue(v1.discrepancy_ci_low.isna().all())
        self.assertTrue(np.isfinite(v1.contrast_high_minus_low).all())

    def test_degenerate_correlations_are_missing_and_bootstrap_failures_counted(self):
        # Substituting zero for an undefined correlation would fail here.
        data = fixture()
        data["odonata_suitability"] = .5
        result = diagnostic.summarize_rank_patterns(data, bootstrap=13, seed=9)
        self.assertTrue(result.supported.all())
        self.assertTrue(result.contrast_high_minus_low.isna().all())
        self.assertTrue(result.predicted_minus_observed.isna().all())
        self.assertTrue(result.bootstrap_invalid.eq(13).all())
        self.assertTrue(result.discrepancy_bootstrap_invalid.eq(13).all())
        self.assertTrue(result.contrast_ci_low.isna().all())

    def test_missing_high_group_preserves_all_requested_rows(self):
        data = fixture().query("not (V == 1 and caudata_tertile == 2)").copy()
        result = diagnostic.summarize_rank_patterns(data, bootstrap=11, seed=8)
        v1 = result[result.subset.eq("V1")]
        self.assertEqual(len(v1), 7)
        self.assertTrue(v1.high_sites.eq(0).all())
        self.assertFalse(v1.supported.any())
        self.assertTrue(v1.rho_high.isna().all())
        self.assertTrue(v1.contrast_high_minus_low.isna().all())

    def test_duplicate_site_background_is_rejected_instead_of_pseudoreplicated(self):
        data = fixture()
        duplicated = pd.concat([data, data.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "unique"):
            diagnostic.summarize_rank_patterns(duplicated, bootstrap=3)

    def test_invalid_probabilities_and_visits_are_rejected(self):
        for column, value in (("env_all", 1.1), ("observed_rate", np.nan), ("n_completed", 0)):
            with self.subTest(column=column):
                data = fixture()
                data.loc[0, column] = value
                with self.assertRaises(ValueError):
                    diagnostic.summarize_rank_patterns(data, bootstrap=3)


if __name__ == "__main__":
    unittest.main()
