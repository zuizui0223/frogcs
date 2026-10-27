"""Check accounting, numerical sensitivity and generate inspectable mechanism tables."""
import json
import numpy as np
import pandas as pd
from run_pathway_audit import OUT


def main():
    su=pd.read_csv(OUT/'primary_summary.csv')
    tr=pd.read_csv(OUT/'primary_trajectories.csv.gz')
    audit={}
    deaths={'F':['F_killed_by_S','F_killed_by_D','F_dry'],
            'S':['S_killed_by_D','S_dry'],
            'D':['D_killed_by_S','D_killed_by_F','D_failure','D_dry']}
    for g,cols in deaths.items():
        err=float((tr[g+'_B']-tr[g+'_C']-tr[cols].sum(axis=1)).abs().max())
        audit[g+'_max_mass_balance_error']=err
        if err>1e-10:raise AssertionError('Mass balance: '+g)
    err=float((tr.F_fraction-np.exp(-tr.audit_H_SF-tr.audit_H_DF)).abs().max())
    audit['max_frog_survival_hazard_identity_error']=err
    if err>1e-11:raise AssertionError('F survival/hazard identity')
    base=su[su.variant=='full'].copy()
    cols=['vegetation','S_source','D_source','F_B','S_B','D_B','F_C','F_fraction',
          'F_killed_by_S','F_killed_by_D','D_killed_by_S','S_killed_by_D',
          'F_killed_by_S_fraction','F_killed_by_D_fraction','D_killed_by_S_fraction',
          'S_killed_by_D_fraction','audit_H_SF','audit_H_DF','audit_H_SD',
          'audit_S_days_Dwindow','audit_S_active_Dwindow','D_C','D_local','F_local','F_immigrant']
    base[cols].to_csv(OUT/'baseline_flux_table.csv',index=False)
    rows=[]
    for v in (0.,1.):
        for d in (1.,2.):
            q=base[(base.vegetation==v)&(base.D_source==d)].set_index('S_source')
            lo,hi=q.loc[.25],q.loc[2.]
            # These are competing-risk accounting contrasts, not isolated mediated effects.
            rows.append(dict(vegetation=v,D_source=d,
                F_B_benefit=hi.F_B-lo.F_B,F_C_benefit=hi.F_C-lo.F_C,
                F_survival_benefit=hi.F_fraction-lo.F_fraction,
                added_S_mortality_fraction=hi.F_killed_by_S_fraction-lo.F_killed_by_S_fraction,
                avoided_D_mortality_fraction=lo.F_killed_by_D_fraction-hi.F_killed_by_D_fraction,
                log_survival_benefit=(lo.audit_H_SF+lo.audit_H_DF)-(hi.audit_H_SF+hi.audit_H_DF),
                F_local_benefit=hi.F_local-lo.F_local))
    benefit=pd.DataFrame(rows)
    if not np.allclose(benefit.F_survival_benefit,
                       benefit.avoided_D_mortality_fraction-benefit.added_S_mortality_fraction,atol=1e-12):
        raise AssertionError('Mortality fraction contrast identity')
    benefit.to_csv(OUT/'benefit_accounting.csv',index=False)
    c=pd.read_csv(OUT/'primary_contrasts.csv');local=c[c.D_low==1]
    selected=local[local.variant.eq('full')|local.variant.str.startswith('no_')]
    selected.to_csv(OUT/'single_pathway_interventions.csv',index=False)
    for label in ('half_step','horizon160'):
        fine=pd.read_csv(OUT/(label+'_contrasts.csv'))
        z=c.merge(fine,on=['variant','D_low','D_high'],suffixes=('_base','_check'),validate='one_to_one')
        audit[label+'_joint_sign_disagreements']=int((z.all_three_base!=z.all_three_check).sum())
        audit[label+'_max_SD_difference']=float((z.SD_base-z.SD_check).abs().max())
        chosen=z[z.D_low==1]
        chosen.to_csv(OUT/(label+'_comparison.csv'),index=False)
    # No vegetation means all vegetation-only interventions are inert.
    keys=['S_source','D_source'];metrics=['F_B','S_B','D_B','F_C','S_C','D_C']
    ref=base[base.vegetation==0].set_index(keys)[metrics].sort_index()
    errors=[]
    for label,q in su[(su.vegetation==0)&su.variant.str.startswith('veg_')].groupby('variant'):
        errors.append(float((q.set_index(keys)[metrics].sort_index()-ref).abs().max().max()))
    audit['vegetation_zero_max_intervention_effect']=max(errors)
    if max(errors)>1e-12:raise AssertionError('Vegetation-zero control')
    audit['predator_factorial_matching']=local[local.variant.str.startswith('pred_')&local.all_three].variant.tolist()
    audit['vegetation_factorial_matching']=local[local.variant.str.startswith('veg_')&local.all_three].variant.tolist()
    audit['scope']='Selected synthetic context only. No identified NAAMP mechanism; no empirical animal counts.'
    (OUT/'accounting_validation.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,indent=2))
    print(benefit.round(6).to_string(index=False))


if __name__=='__main__':main()
