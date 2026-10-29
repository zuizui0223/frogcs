"""Paired pathway diagnosis and fixed-unit-cohort stage checks."""
import numpy as np
import pandas as pd
from run_literature_extension import OUT,CONTEXTS
from stage_network_extension_20261029 import simulate


def stage_check():
    rows=[]
    controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,cue_SD=0.)
    for ctx in CONTEXTS:
        for handling in [0.,1.]:
            for mode in ['dynamic','frozen']:
                for reverse in [False,True]:
                    params=dict(community='FSD',roles=15,refuge_order='D',vegetation=1.,f_arrival=20.,s_arrival=ctx['sa'],d_arrival=ctx['da'],attack_scale=.5,cue=0.,reverse=reverse)
                    r=simulate([params],dt=.125,stage_durations=(45,80,ctx['dduration']),pathway_controls=controls,functional_response='litter',handling_s=handling,handling_d=handling,sd_size_mode=mode,s_growth=ctx['sg'],d_growth=ctx['dg'],diagnostics=True,extension_diagnostics=True).iloc[0]
                    rows.append(dict(context=ctx['context'],shared_both=handling,mode=mode,frog_reverse=reverse,**{k:r[k] for k in ['audit_DS_dominant_days','audit_SD_dominant_days','audit_both_alive_days','F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S','D_killed_by_F','F_completed']}))
    pd.DataFrame(rows).to_csv(OUT/'unit_cohort_stage_diagnostic.csv',index=False)


def main():
    stage_check()
    a=pd.read_csv(OUT/'primary_coefficients.csv')
    terms=['OS','OV','SV','OSV']
    base=a[a.family=='baseline'][['context','risk','edge','background']+terms].rename(columns={t:'baseline_'+t for t in terms})
    paired=a.merge(base,on=['context','risk','edge','background'],validate='many_to_one')
    for t in terms:paired['added_'+t]=paired[t]-paired['baseline_'+t]
    paired.to_csv(OUT/'paired_mechanism_effects.csv',index=False)
    frozen=a[a.edge=='frozen'][['context','family','hs','hd','risk','background']+terms].rename(columns={t:'frozen_'+t for t in terms})
    dyn=a[a.edge=='dynamic'].merge(frozen,on=['context','family','hs','hd','risk','background'],validate='one_to_one')
    for t in terms:dyn['dynamic_minus_frozen_'+t]=dyn[t]-dyn['frozen_'+t]
    dyn.to_csv(OUT/'paired_size_dynamics.csv',index=False)
    c=pd.read_csv(OUT/'primary_corner_mortality.csv');rows=[]
    for (case,v),g in c.groupby(['case','vegetation']):
        g=g.set_index(['S_source','D_source']);row=dict(case=case,vegetation=v)
        for term in ['audit_H_DF','audit_H_SF']:
            z=g[term];row[term+'_DiD']=z.loc[(2.,2.)]-z.loc[(2.,.25)]-z.loc[(.25,2.)]+z.loc[(.25,.25)]
        row['net_H_DiD']=row['audit_H_DF_DiD']+row['audit_H_SF_DiD']
        row['min_F_survival']=g.minimum_F_survival.min();rows.append(row)
    pd.DataFrame(rows).to_csv(OUT/'hazard_pathway_contrasts.csv',index=False)
    half=pd.read_csv(OUT/'half_step_coefficients.csv')
    check=half.merge(a,on=['case','background'],suffixes=('_half','_primary'),validate='one_to_one')
    for t in terms:check['delta_'+t]=check[t+'_half']-check[t+'_primary']
    check.to_csv(OUT/'numerical_check.csv',index=False)


if __name__=='__main__':main()
