import unittest
import numpy as np
import pandas as pd
from stage_vegetation_network import simulate
from run_evidence_constrained import contrasts


class EvidenceMechanisms(unittest.TestCase):
    def test_defaults_retain_legacy(self):
        rows=[{'vegetation':v,'f_arrival':50} for v in (0,1)]
        a=simulate(rows)
        b=simulate(rows,functional_response=None,behavioral_refuge=False,emergence_delay=0)
        pd.testing.assert_frame_equal(a,b,check_exact=True)

    def test_behavioral_refuge_requires_dragonfly(self):
        row={'community':'FS','vegetation':1,'refuge_order':'S','f_arrival':50}
        a=simulate([row],behavioral_refuge=True).iloc[0]
        b=simulate([{**row,'vegetation':0}]).iloc[0]
        self.assertEqual(a.F_completed,b.F_completed)

    def test_response_switch_is_neutral_at_density_scale(self):
        # One predation step then drying; check analytic II/III mortality.
        for f in (.1,1.,10.):
            rows=[dict(community='FD',roles=0,vegetation=v,f_arrival=0,d_arrival=0,water=1)
                  for v in (0,1)]
            r=simulate(rows,dt=1,size_gate=.5,initial_cohorts=[[f,0,1]]*2,functional_response='litter')
            responses=np.array([2/(1+f),2*f/(1+f*f)])
            np.testing.assert_allclose(r.F_killed_by_D,f*(1-np.exp(-.025*.5*responses)),atol=1e-12)
            if f==1:self.assertEqual(r.iloc[0].F_killed_by_D,r.iloc[1].F_killed_by_D)

    def test_vector_delay_shifts_completion_boundary(self):
        rows=[{'d_arrival':60,'attack_scale':0,'reverse':False}]*2
        r=simulate(rows,emergence_delay=[0,5])
        # Neither finishes emergence before day120; delayed cohort dries at120.
        self.assertEqual(r.iloc[0].D_dry,0)
        self.assertEqual(r.iloc[1].D_dry,1)

    def test_delays_and_response_validation(self):
        for kw in ({'functional_response':'unknown'},{'emergence_delay':-.5},
                   {'emergence_delay':[0,5]},{'emergence_delay':.1}):
            with self.assertRaises(ValueError):simulate([{}],**kw)

    def test_new_mechanisms_keep_mass_and_hazard_identity(self):
        r=simulate([{'vegetation':0,'f_arrival':50},{'vegetation':1,'f_arrival':50}],
                   functional_response='litter',behavioral_refuge=True,
                   emergence_delay=[0,5],diagnostics=True)
        for g in 'FSD':np.testing.assert_allclose(r[g+'_survived']+r[g+'_dead'],1,atol=1e-12)
        np.testing.assert_allclose(r.F_completed,np.exp(-r.audit_H_SF-r.audit_H_DF),atol=1e-12)

    def test_vector_stage_durations_match_individual_runs(self):
        rows=[dict(f_arrival=20,s_arrival=0,d_arrival=40),dict(f_arrival=20,s_arrival=40,d_arrival=0)]
        durations=[(45,80,60),(75,40,70)]
        batched=simulate(rows,stage_durations=durations)
        single=pd.concat([simulate([r],stage_durations=d) for r,d in zip(rows,durations)],ignore_index=True)
        pd.testing.assert_frame_equal(batched,single,check_exact=True)

    def test_contrasts_recover_known_interactions_and_reject_missing_cells(self):
        rows=[]
        for v in (0.,1.):
            for s in (.25,1.,2.):
                for d in (.25,1.,2.):
                    value=10-d+s-v*d+v*s-.1*s*d
                    rows.append(dict(profile='test',timing='test',refuge_order='S',attack_scale=1.,
                        cue=0.,reverse=False,vegetation=v,S_source=s,D_source=d,F_B=value,F_C=value))
        q=pd.DataFrame(rows);a=contrasts(q);b=contrasts(q.sample(frac=1,random_state=2))
        pd.testing.assert_frame_equal(a,b)
        r=a[(a.metric=='F_B')&(a.D_low==1)&(a.D_high==2)&(a.S_low==.25)&(a.S_high==2)].iloc[0]
        self.assertAlmostEqual(r.DV,-1)
        self.assertAlmostEqual(r.SV,1)
        self.assertAlmostEqual(r.SD,-.175)
        self.assertTrue(r.all_three)
        with self.assertRaises(ValueError):contrasts(q.iloc[:-1])


if __name__=='__main__':unittest.main()
