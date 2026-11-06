"""The source join must not duplicate, mismatch or silently drop field sites."""
import importlib.util
import unittest

import numpy as np
import pandas as pd


CANDIDATES = ("env_add", "env_all", "flex_add", "flex_all", "flex_prior_00", "flex_prior_11")


def source_fixture():
    predictions, classes = [], []
    sites = pd.DataFrame({
        "site": ["a", "b"], "strong_rate": [0.25, 0.8],
        "flooded_3000m_mean": [0.0, 2.0],
        "mean_suitability_Odonata_uniform": [0.1, 0.9],
        "mean_suitability_Odonata_target_group": [0.3, 0.7],
    })
    for bg in ("uniform", "target_group"):
        for site, route, block, fold, n, k, v, s, o in (
            ("a", "r1", "b1", 0, 4, 1, 0, 0, 2),
            ("b", "r2", "b2", 1, 10, 8, 1, 2, 0),
        ):
            classes.append(dict(site=site, background=bg, route=route,
                                spatial_block=block, vegetation=v,
                                caudata_tertile=s, odonata_tertile=o,
                                n_completed=n, n_strong=k))
            for candidate in CANDIDATES:
                predictions.append(dict(site=site, background=bg, route=route,
                                        spatial_block=block, fold=fold,
                                        candidate=candidate, n_completed=n,
                                        k_strong=k, predicted=0.4 if site == "a" else 0.7))
    return pd.DataFrame(predictions), pd.DataFrame(classes), sites


class OriginalSourceJoinTests(unittest.TestCase):
    def implementation(self):
        spec = importlib.util.find_spec("run_g6_observation_context_diagnostic")
        self.assertIsNotNone(spec, "The source-safe G6 joining implementation is missing")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_preserves_each_site_once_and_keeps_observed_and_predicted_distinct(self):
        # A duplicated join or substituting the prediction for the response must fail.
        module = self.implementation()
        p, c, s = source_fixture()
        result = module.build_wide(p, c, s).sort_values(["background", "site"])
        self.assertEqual(len(result), 4)
        self.assertFalse(result.duplicated(["background", "site"]).any())
        np.testing.assert_allclose(result.observed_rate, [0.25, 0.8, 0.25, 0.8])
        np.testing.assert_allclose(result.flex_prior_11, [0.4, 0.7, 0.4, 0.7])
        self.assertEqual(result.groupby("background").n_completed.sum().tolist(), [14, 14])

    def test_rejects_duplicate_source_probability_instead_of_averaging(self):
        module = self.implementation()
        p, c, s = source_fixture()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            module.build_wide(pd.concat([p, p.iloc[[0]]], ignore_index=True), c, s)

    def test_rejects_missing_candidate_site_instead_of_inner_joining_it_away(self):
        module = self.implementation()
        p, c, s = source_fixture()
        with self.assertRaisesRegex(ValueError, "candidate|complete"):
            module.build_wide(p.iloc[1:], c, s)

    def test_rejects_source_visit_or_route_mismatch(self):
        module = self.implementation()
        for column, replacement in (("n_completed", 5), ("route", "wrong-route")):
            p, c, s = source_fixture()
            c.loc[0, column] = replacement
            with self.subTest(column=column), self.assertRaisesRegex(ValueError, "mismatch"):
                module.build_wide(p, c, s)

    def test_rejects_nonfinite_probability_and_conflicting_fold(self):
        module = self.implementation()
        p, c, s = source_fixture()
        p.loc[0, "predicted"] = np.nan
        with self.assertRaisesRegex(ValueError, "probability"):
            module.build_wide(p, c, s)
        p, c, s = source_fixture()
        p.loc[0, "fold"] = 3
        with self.assertRaisesRegex(ValueError, "metadata|fold"):
            module.build_wide(p, c, s)


if __name__ == "__main__":
    unittest.main()
