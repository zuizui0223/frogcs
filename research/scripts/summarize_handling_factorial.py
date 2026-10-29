"""Report all paired factorial effects without choosing an estimand afterward."""
import pandas as pd
from run_handling_factorial import OUT,ANCHORS


def read(name):return pd.read_csv(OUT/name,dtype={'arm':str})


def main():
    a=read('primary_rank_coefficients.csv');h=read('primary_hazard_coefficients.csv')
    rows=[]
    for dataset,table,groupcols in [('rank',a,['background']),('hazard',h,['background','path'])]:
        for keys,g in table.groupby(groupcols):
            keys=keys if isinstance(keys,tuple) else (keys,)
            meta=dict(zip(groupcols,keys));g=g.set_index('arm')
            for arm in g.index:
                for j,flag in enumerate(['FF','FD','DF','DD']):
                    if arm[j]!='0':continue
                    target=arm[:j]+'1'+arm[j+1:]
                    for term in ['OS','OV','SV','OSV']:
                        rows.append(dict(dataset=dataset,**meta,from_arm=arm,to_arm=target,added=flag,term=term,delta=g.loc[target,term]-g.loc[arm,term]))
    pd.DataFrame(rows).to_csv(OUT/'all_paired_factorial_effects.csv',index=False)
    half=read('half_step_rank_coefficients.csv');j=half.merge(a,on=['arm','background'],suffixes=('_half','_primary'))
    for t in ['OS','OV','SV','OSV']:j['delta_'+t]=j[t+'_half']-j[t+'_primary']
    j.to_csv(OUT/'numerical_rank_check.csv',index=False)
    print('Numerical differences:',j[['delta_OS','delta_OV','delta_SV']].abs().max().to_dict())
    p=read('dense21_physical_contrasts.csv')
    print(p[(p.contrast=='OS')&(p['at']==1)].pivot(index=['arm','label'],columns='path',values='value').to_string())
    c=read('dense21_corner_mortality.csv')
    print(c[(c.vegetation==1)&(c.S_source==2)&(c.D_source==2)][['arm','F_B','F_fraction','F_killed_by_S','F_killed_by_D','D_killed_by_S','audit_H_SF','audit_H_DF']].to_string(index=False))
    h=read('dense21_hazard_coefficients.csv')
    print(h[(h.background=='uniform')&(h.path=='H_total')].to_string(index=False))
    print(a.groupby('background')[['rank_signs','all_three_intervals','physical_corner_signs']].sum().to_string())


if __name__=='__main__':main()
