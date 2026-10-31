"""Synthetic structure-type aggregation invariants; not empirical ecological claims.

Test all 12 nuisance settings, 3 sources, 8 genuine-rate labels, paired
reversal identical source de-duplication, danger neutral vs controls, and
the balanced baseline/shared-handling comparison without one noisy setting
being counted as an independent study.
"""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from summarize_pom_structural_types import (
    CONTEXTS,HANDLING,NOISE,N_SENS,N_TYPES,
    common_structure,join_all,type_conditional_scores,type_overall,
    handling_comparison,reversal_contrasts,expanded_frozen_type_comparison,
    matched_danger_comparison,read_sources,
)
from r2_calibrated_directional_pom import BACKGROUNDS,MODES
from pattern_oriented_archive132 import DESIGN as DESIGN_PATH


def synthetic_alias_and_scores():
    design=pd.read_csv(DESIGN_PATH)
    common=design[design.context.isin(CONTEXTS)&
                  design.family.isin(HANDLING)&
                  design.edge.isin(("dynamic","frog_reverse"))]
    assert len(common)==24
    source_rows=[]
    def source_for(family,case,draw=-1,hypothesis="frozen"):
        r=design.set_index("case").loc[case]
        # In this synthetic fixture all reversal ON and OFF output the same
        # frozen F_B model, while all other response variants remain distinct.
        if r.edge=="frog_reverse":
            possible=design[(design.context==r.context)&
                            (design.family==r.family)&
                            (design.risk==r.risk)&
                            (design.edge=="dynamic")]
            src=int(possible.case.iloc[0])
        else:src=int(case)
        if family=="frozen132":return f"case_{src:03d}"
        if family=="realrate192":return f"d{draw:02d}_case_{src:03d}"
        return f"{hypothesis}_case_{src:03d}"
    for case in design.case:
        source_rows.append(dict(family="frozen132",
                         model_label=f"case_{case:03d}",
                         case=f"case_{case:03d}",rate_draw=-1,
                         hypothesis="frozen",source_group=source_for("frozen132",case)))
    for draw in range(8):
        for case in common.case:
            source_rows.append(dict(family="realrate192",
                           model_label=f"d{draw:02d}_case_{case:03d}",
                           case=f"case_{case:03d}",rate_draw=draw,
                           hypothesis="process_rate",
                           source_group=source_for("realrate192",case,draw=draw)))
    for hypo in ("neutral","moderate","strong"):
        for case in common.case:
            source_rows.append(dict(family="facilitation72",
                           model_label=f"{hypo}_case_{case:03d}",
                           case=f"case_{case:03d}",rate_draw=-1,
                           hypothesis=hypo,
                           source_group=source_for("facilitation72",case,hypothesis=hypo)))
    alias=pd.DataFrame(source_rows)
    alias["case_numeric"]=alias.case.str.slice(-3).astype(int)
    alias=alias.merge(
        design[["case","context","family","risk","edge","hs","hd"]].rename(
            columns={"case":"case_numeric","family":"handling"}),
        on="case_numeric",how="left",validate="many_to_one")
    score=[]
    for fam,group in alias.groupby(["family","source_group"]):
        family,source=fam
        design_row=group.iloc[0]
        for noise in NOISE:
            for background in BACKGROUNDS:
                for mode in MODES:
                    # Baseline->shared_both is always +.06 here; no observed
                    # source result need match this artificial fixture.
                    shape=.25+(.06 if design_row.handling=="shared_both" else 0)
                    shape+=(.008 if design_row.context=="original" else -.003)
                    shape+=(.002 if design_row.risk else 0)
                    shape+=(.006 if noise=="naamp_residual_icc_2degree" else 0)
                    shape+=(.003 if background=="uniform" else 0)
                    shape+=(.004 if mode=="log_signal" else 0)
                    shape+=(.006 if design_row.hypothesis=="moderate" else
                            -.01 if design_row.hypothesis=="strong" else 0)
                    score.append(dict(family=family,source_group=source,
                                      noise_type=noise,background=background,mode=mode,
                                      calibration_status="MATCHED_R2",
                                      soft_joint_agreement=shape,
                                      modal_complete_frequency=shape/4,
                                      modal_complete_count=round(128*shape/4)))
    return pd.DataFrame(score),alias


class StructureLevelPOMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scores,aliases=synthetic_alias_and_scores()
        cls.score=scores
        cls.alias=aliases
        cls.joined=join_all(scores,aliases)
        cls.common=common_structure(cls.joined)

    def test_three_families_are_balanced_without_double_counting_reversal(self):
        base,bydraw,distinct=type_conditional_scores(self.common)
        self.assertEqual(len(base),3*N_SENS*N_TYPES)
        self.assertEqual(len(distinct[distinct.family=="frozen132"]),
                         12*N_SENS)
        self.assertEqual(len(distinct[distinct.family=="realrate192"]),
                         12*8*N_SENS)
        self.assertEqual(len(distinct[distinct.family=="facilitation72"]),
                         12*N_SENS)
        self.assertEqual(base.groupby("family").n_rate_draws.min().to_dict(),
                         {"frozen132":1,"realrate192":8,"facilitation72":1})
        self.assertTrue(base.source_groups_per_draw.eq(1).all())
        summary=type_overall(base)
        self.assertEqual(len(summary),3*N_TYPES)
        self.assertTrue(summary.n_conditions.eq(N_SENS).all())
        self.assertTrue(summary.mean_rank_percentile.between(0,1).all())

    def test_shared_both_is_synthetic_winner_in_all_72_paired_conditions(self):
        per,_,_=type_conditional_scores(self.common)
        matching,totals,by_context=handling_comparison(per)
        self.assertEqual(len(matching),3*72)
        self.assertTrue(np.allclose(matching.delta_soft,.06))
        self.assertEqual(len(totals),3)
        self.assertTrue(totals.n_shared_better.eq(72).all())
        self.assertTrue(totals.n_baseline_better.eq(0).all())
        self.assertTrue(by_context.n_timing_risk_pairs.eq(6).all())

    def test_reversal_same_fB_does_not_inflate_votes_or_create_nonzero_effects(self):
        pair,total=reversal_contrasts(self.joined)
        self.assertEqual(len(total),3)
        self.assertEqual(len(pair),12*12 + 12*8*12 + 12*3*12)
        self.assertTrue(pair.source_identical.all())
        self.assertTrue(np.allclose(pair.delta_reversal_soft,0))
        self.assertTrue(total.fraction_identical_sources.eq(1).all())

    def test_old_frozen_extra_cases_reported_but_not_primary(self):
        extra,alltypes=expanded_frozen_type_comparison(self.joined)
        self.assertEqual(extra.background.nunique(),2)
        self.assertIn("shared_both_sensitivity",set(alltypes.handling))
        self.assertIn("frozen",set(alltypes.edge))
        self.assertIn("no_DS",set(alltypes.edge))
        self.assertIn("no_SD",set(alltypes.edge))
        self.assertTrue(alltypes.n_contexts.eq(N_SENS).all())

    def test_hazard_vs_neutral_is_paired_on_exact_case(self):
        pairs,summary=matched_danger_comparison(self.joined)
        self.assertEqual(len(pairs),24*12*2)
        self.assertEqual(len(summary),4)
        self.assertTrue(np.allclose(pairs[pairs.hypothesis=="moderate"].gain_soft,.006))
        self.assertTrue(np.allclose(pairs[pairs.hypothesis=="strong"].gain_soft,-.01))
        self.assertTrue(summary.n_paired_contexts.eq(12*12).all())

    def test_no_unsupported_case_can_enter_primary_type_selection(self):
        wrong=self.joined[self.joined.family=="frozen132"].copy()
        wrong=wrong[wrong.case_numeric!=30]
        with self.assertRaises(AssertionError):
            common_structure(wrong)
        corrupted=self.joined.iloc[:-1].copy()
        with self.assertRaises(AssertionError):
            common_structure(corrupted)


if __name__=="__main__":
    unittest.main()
