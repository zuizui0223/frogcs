"""Behavioral checks for the frozen G7 species-composition comparison."""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from scipy.special import expit

import g7_trait_composition_bridge as g7


def small_source():
    # Deliberately retain a nontrivial site order and unrelated dataframe index.
    sites = pd.DataFrame({"site": ["b", "a", "c"]}, index=[81, 6, 39])
    values = {
        "b": {"2431978": .8, "2431993": .6, "2431951": .1,
              "2432014": .3, "5218390": .4},
        "a": {"2431978": .2, "2431993": .4, "2431951": .9,
              "2432014": .7, "5218390": .5},
        "c": {"2431978": .5, "2431993": .5, "2431951": .5,
              "2432014": .5, "5218390": .9},
    }
    names = {"2431978": "Ambystoma mavortium", "2431993": "Ambystoma tigrinum",
             "2431951": "Ambystoma maculatum", "2432014": "Ambystoma laterale",
             "5218390": "Notophthalmus viridescens"}
    rows = []
    for bg in ("uniform", "target_group"):
        sites["mean_suitability_pond_breeding_Caudata_" + bg] = [.44, .54, .58]
        for site in ("a", "c", "b"):
            for key, value in values[site].items():
                rows.append(dict(site=site, species_key=key, species=names[key],
                                 background=bg, guild="Caudata",
                                 suitability_percentile=value))
    return sites, pd.DataFrame(rows).sample(frac=1, random_state=31)


class TraitSourceTests(unittest.TestCase):
    def test_species_scores_align_by_site_identity_and_preserve_composition(self):
        sites, pred = small_source()
        d = g7.join_trait_predictors(sites, pred)
        self.assertEqual(d.site.tolist(), ["b", "a", "c"])
        np.testing.assert_allclose(d.T_uniform, [.7, .3, .5])
        np.testing.assert_allclose(d.B_uniform, [.2, .8, .5])
        np.testing.assert_allclose(d.N_uniform, [.4, .5, .9])
        np.testing.assert_allclose(d.A_uniform, [.45, .55, .5])
        np.testing.assert_allclose(d.C_uniform, [.5, -.5, 0.])
        np.testing.assert_allclose(d.A5_uniform, [.44, .54, .58])
        np.testing.assert_allclose(d.C5_uniform, [13/30, -.4, -2/15])

    def test_missing_species_cannot_change_the_group_denominator(self):
        sites, pred = small_source()
        with self.assertRaises(ValueError):
            g7.join_trait_predictors(sites, pred[pred.species_key != "5218390"])

    def test_duplicate_species_site_background_cannot_reweight_a_species(self):
        sites, pred = small_source()
        with self.assertRaises(ValueError):
            g7.join_trait_predictors(sites, pd.concat([pred, pred.iloc[[0]]]))

    def test_wrong_taxonomic_key_or_frozen_mean_fails_before_fitting(self):
        sites, pred = small_source()
        bad = pred.copy()
        bad.loc[bad.species_key == "2431978", "species"] = "Ambystoma tigrinum"
        with self.assertRaises(ValueError):
            g7.join_trait_predictors(sites, bad)
        sites.loc[81, "mean_suitability_pond_breeding_Caudata_uniform"] = .9
        with self.assertRaises(ValueError):
            g7.join_trait_predictors(sites, pred)


class StatisticalBehaviorTests(unittest.TestCase):
    def test_composition_uses_raw_difference_sd_and_excludes_redundant_total(self):
        d = pd.DataFrame(dict(V=[0., 1., 0., 1.], lat=[31., 33., 35., 37.],
                              lon=[-95., -94., -91., -89.]))
        d["A_uniform"] = [.3, .4, .5, .5]
        d["C_uniform"] = [0., .1, .2, .9]
        d["N_uniform"] = [.3, .4, .7, .5]
        d["mean_suitability_Odonata_uniform"] = [.1, .2, .3, .4]
        d["mean_suitability_pond_breeding_Caudata_uniform"] = [.3, .4, .5, .6]
        for name in g7.SURVEY + g7.ENV:
            d[name] = [1., 2., 4., 8.]
        first = g7.build_design(d, "uniform")
        # Raw contrast mean = .3; population variance = .125. Rank scaling
        # would instead produce equally spaced scores and fails this check.
        expected_c = np.array([-.3, -.2, -.1, .6])/np.sqrt(.125)
        np.testing.assert_allclose(first.base[:, first.base_names.index("C")], expected_c)
        np.testing.assert_allclose(first.full[:, -1], [0., -.2/np.sqrt(.125), 0., .6/np.sqrt(.125)])
        d["mean_suitability_pond_breeding_Caudata_uniform"] = [1., 0., 1., 0.]
        second = g7.build_design(d, "uniform")
        np.testing.assert_array_equal(first.full, second.full)

    def test_known_positive_and_negative_moderators_are_not_sign_constrained(self):
        c = np.tile(np.linspace(-1.6, 1.6, 80), 2)
        v = np.repeat([0., 1.], 80)
        x = np.column_stack((c, v, v*c))
        n = np.full(len(c), 200)
        for theta in (1.2, -1.2):
            with self.subTest(theta=theta):
                k = np.rint(n*expit(-.25 + .4*c - .3*v + theta*c*v)).astype(int)
                fit = g7.fit_binomial(x, k, n)
                self.assertTrue(fit.converged)
                self.assertAlmostEqual(fit.coefficients[-1], theta, delta=.08)
                self.assertTrue(np.all((fit.predict(x) > 0) & (fit.predict(x) < 1)))

    def test_returned_coefficients_are_in_original_feature_units(self):
        x = np.linspace(-100, 100, 151)[:, None]
        n = np.full(151, 500)
        k = np.rint(n*expit(.2 + .03*x[:, 0])).astype(int)
        fit = g7.fit_binomial(x, k, n, ridge=0.)
        self.assertTrue(fit.converged)
        self.assertAlmostEqual(fit.coefficients[0], .2, delta=.01)
        self.assertAlmostEqual(fit.coefficients[1], .03, delta=.0001)

    def test_cluster_multiplicity_fit_equals_duplicated_whole_clusters(self):
        x = np.column_stack((np.linspace(-1.5, 1.5, 12), np.tile([0., 1.], 6)))
        n = np.full(12, 40)
        k = np.rint(n*expit(-.2 + .5*x[:, 0] - .3*x[:, 1])).astype(int)
        weights = np.repeat([2, 0, 1], 4)
        scale = g7.numerical_scaling(x)
        weighted = g7.fit_binomial(x, k, n, multiplicity=weights, scaling=scale)
        index = np.repeat(np.arange(len(x)), weights)
        repeated = g7.fit_binomial(x[index], k[index], n[index], scaling=scale)
        self.assertTrue(weighted.converged and repeated.converged)
        np.testing.assert_allclose(weighted.coefficients, repeated.coefficients, atol=1e-9)

    def test_bootstrap_resamples_blocks_and_keeps_all_rows_in_each_block(self):
        labels, code, counts = g7.block_multiplicities(np.array(["c", "a", "a", "b", "c"]), 23, 12)
        self.assertEqual(labels.tolist(), ["a", "b", "c"])
        self.assertTrue(np.all(counts.sum(axis=1) == 3))
        weights = counts[:, code]
        np.testing.assert_array_equal(weights[:, 1], weights[:, 2])
        np.testing.assert_array_equal(weights[:, 0], weights[:, 4])
        self.assertTrue(np.any(weights == 0) and np.any(weights > 1))

    def test_paired_scores_align_sites_and_weight_by_completed_visits(self):
        null = pd.DataFrame(dict(site=["s1", "s2", "s3"], spatial_block=["A", "A", "B"],
                                 k=[5, 10, 90], n=[10, 20, 90], predicted=[.5, .5, .5]))
        full = null.copy()
        full.loc[2, "predicted"] = .75
        counts = np.array([[2, 0], [0, 2], [1, 1]])
        result = g7.paired_holdout_gain(null, full.iloc[[2, 0, 1]], np.array(["A", "B"]), counts)
        self.assertAlmostEqual(result["gain_nll_per_survey"], .75*np.log(1.5), places=12)
        self.assertEqual(result["n_surveys"], 120)
        self.assertAlmostEqual(result["bootstrap_95_low"], .05*.75*np.log(1.5), places=12)
        self.assertAlmostEqual(result["bootstrap_95_high"], .95*np.log(1.5)+.05*.75*np.log(1.5), places=12)
        with self.assertRaises(ValueError):
            g7.paired_holdout_gain(null, full.iloc[:2], np.array(["A", "B"]), counts)
        mismatched = full.copy()
        mismatched.loc[0, "n"] = 11
        with self.assertRaises(ValueError):
            g7.paired_holdout_gain(null, mismatched, np.array(["A", "B"]), counts)

    def test_residual_information_detects_a_saturated_moderator(self):
        base = np.array([[-1.], [-1.], [1.], [1.]])
        self.assertLess(g7.residual_information_ratio(base, 2*base[:, 0]), 1e-12)
        self.assertAlmostEqual(g7.residual_information_ratio(base, np.array([-1., 1., -1., 1.])), 1., places=12)

    def test_route_or_geographic_block_cannot_cross_folds(self):
        d = pd.DataFrame(dict(site=np.arange(10), route=np.repeat(np.arange(5), 2),
                              spatial_block=np.repeat(list("ABCDE"), 2)))
        folds = np.repeat(np.arange(5), 2)
        g7.validate_folds(d, folds)
        leaking = folds.copy()
        leaking[0] = 1
        with self.assertRaises(ValueError):
            g7.validate_folds(d, leaking)

    def test_a_held_out_regions_outcomes_cannot_change_its_predictions(self):
        c = np.tile(np.linspace(-1.5, 1.5, 20), 5)
        v = np.tile(np.repeat([0., 1.], 10), 5)
        n = np.full(100, 30)
        k = np.rint(n*expit(-.2 + .3*c -.2*v + .8*v*c)).astype(int)
        folds = np.repeat(np.arange(5), 20)
        d = pd.DataFrame(dict(site=["s"+str(i) for i in range(100)], route=folds,
                              spatial_block=folds.astype(str), V=v, k=k, n=n))
        design = g7.Design(np.column_stack((c, v)), np.column_stack((c, v, c*v)),
                           ("C", "V"), ("C", "V", "VC"), [])
        fits = {("uniform", "primary"): design}
        first, _ = g7.heldout_predictions(d, fits, folds)
        changed = d.copy()
        changed.loc[folds == 0, "k"] = n[folds == 0]-k[folds == 0]
        second, _ = g7.heldout_predictions(changed, fits, folds)
        a = first[(first.fold == 0) & (first.candidate == "full")].set_index("site")
        b = second[(second.fold == 0) & (second.candidate == "full")].set_index("site")
        np.testing.assert_allclose(a.predicted, b.reindex(a.index).predicted, atol=1e-12)

    def test_corrupted_source_bytes_are_rejected(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/"source.txt"
            source.write_bytes(b"abc")
            expected = {"example": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}
            g7.verify_source_hashes({"example": source}, expected=expected)
            source.write_bytes(b"abc\n")
            with self.assertRaises(ValueError):
                g7.verify_source_hashes({"example": source}, expected=expected)

    def test_positive_coefficients_cannot_override_support_or_convergence_gates(self):
        design = g7.Design(np.zeros((3, 1)), np.zeros((3, 2)), ("V",), ("V", "VC"), [])
        point = g7.BinomialFit(np.array([0., 0., 1.]), np.array([0., 0., 1.]), True, 2, 0., 1.)
        key = ("uniform", "primary")
        draws = pd.DataFrame(dict(background=["uniform"]*999, variant=["primary"]*999,
                                  converged=[True]*989+[False]*10,
                                  theta=np.ones(999), vegetation_coefficient=np.zeros(999)))
        summary = g7.summarize_coefficients({key: point}, draws, {key: design}, {key: True}, 999)
        self.assertFalse(summary.positive_association_qualified.iloc[0])
        self.assertEqual(summary.n_valid_bootstrap.iloc[0], 989)
        draws.loc[989, "converged"] = True
        supported = g7.summarize_coefficients({key: point}, draws, {key: design}, {key: True}, 999)
        self.assertTrue(supported.positive_association_qualified.iloc[0])
        unsupported = g7.summarize_coefficients({key: point}, draws, {key: design}, {key: False}, 999)
        self.assertFalse(unsupported.positive_association_qualified.iloc[0])


if __name__ == "__main__":
    unittest.main()
