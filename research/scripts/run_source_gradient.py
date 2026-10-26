"""Unfitted independent external supply gradients and pathway ablations."""
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from multiyear_stage_network import simulate_years

OUT=Path(__file__).resolve().parents[1]/'results/source_gradient_20261026'
KEYS=['roles','vegetation','refuge_order','f_arrival','variant']
METRICS=['F_B','F_C','S_B','D_B','F_killed_by_S','F_killed_by_D','D_killed_by_F']


def grid(roles=(0,15,14,13,11,7)):
    variants={'full':{},'no_reverse':{'reverse':False},'no_cue':{'cue':0.},
              'no_intraguild':{'intraguild':False},
              'independent':{'intraguild':False,'cue':0.}}
    rows=[]
    for role,v,order,arrival,variant,s,d in itertools.product(
            roles,[0.,1.],['S','D'],[10.,30.,50.],variants,[.25,1.,2.],[.25,1.,2.]):
        rows.append(dict(roles=role,vegetation=v,refuge_order=order,f_arrival=arrival,
                         variant=variant,S_source=s,D_source=d,
                         attack_scale=1.5,cue=3.,rho=.5,reverse=True,intraguild=True)|variants[variant])
    return pd.DataFrame(rows)


def contrasts(summary):
    q=summary.copy()
    for c in ['F_B','F_C']:q['log_'+c]=np.log(q[c])
    metrics=METRICS+['log_F_B','log_F_C']
    key=KEYS+['S_source']
    low=q[q.D_source==.25].set_index(key)[metrics].sort_index()
    high=q[q.D_source==2].set_index(key)[metrics].sort_index()
    assert low.index.equals(high.index) and low.index.is_unique
    slopes=((high-low)/1.75).add_prefix('slope_').reset_index()
    low=slopes[slopes.S_source==.25].set_index(KEYS).drop(columns='S_source').sort_index()
    high=slopes[slopes.S_source==2].set_index(KEYS).drop(columns='S_source').sort_index()
    assert low.index.equals(high.index) and low.index.is_unique
    return slopes,(high-low).add_prefix('S_change_').reset_index()


def run(label,design,**kwargs):
    design=design.copy()
    if 'rho' in kwargs:design['rho']=kwargs.pop('rho')
    kernel=design.drop(columns=['variant','S_source','D_source']).to_dict('records')
    sources=np.column_stack([np.ones(len(design)),design.S_source,design.D_source])
    tr=simulate_years(kernel,source_cohorts=sources,**kwargs)
    last=tr.year.max();tail=tr[tr.year>last-20]
    su=tail.groupby('scenario_id')[METRICS].mean().join(design).reset_index()
    su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
    slopes,changes=contrasts(su)
    su.to_csv(OUT/(label+'_summary.csv'),index=False)
    slopes.to_csv(OUT/(label+'_D_slopes.csv'),index=False)
    changes.to_csv(OUT/(label+'_S_modification.csv'),index=False)
    tr[['scenario_id','year']+METRICS].to_csv(OUT/(label+'_trajectory.csv.gz'),index=False,
                                            compression={'method':'gzip','mtime':0})
    print('Completed',label,len(design),flush=True)
    return su,changes


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    full=grid();base,changes=run('primary',full)
    small=grid((15,))
    runs={'half_step':{'dt':.125},'horizon160':{'years':160},
          'rho25':{'rho':.25},'rho75':{'rho':.75},
          'conversion2':{'conversion':(2,2,2)},'conversion8':{'conversion':(8,8,8)},
          'delay111':{'delays':(1,1,1)},'delay332':{'delays':(3,3,2)}}
    counts=[];numerics={}
    def count(label,df):
        for variant,d in df.groupby('variant'):
            for metric in ['S_change_slope_F_B','S_change_slope_log_F_B','S_change_slope_F_C']:
                counts.append(dict(run=label,variant=variant,metric=metric,n=len(d),
                                   negative=int((d[metric]<-1e-6).sum()),
                                   positive=int((d[metric]>1e-6).sum()),
                                   minimum=float(d[metric].min()),maximum=float(d[metric].max())))
    count('primary',changes)
    reference=base[base.roles==15].sort_values(KEYS+['S_source','D_source'])
    for label,kwargs in runs.items():
        su,ch=run(label,small,**kwargs);count(label,ch)
        if label in ['half_step','horizon160']:
            q=su.sort_values(KEYS+['S_source','D_source'])
            numerics[label+'_max_F_B_difference']=float(np.max(np.abs(q.F_B.to_numpy()-reference.F_B.to_numpy())))
            original=changes[changes.roles==15].sort_values(KEYS)
            alt=ch.sort_values(KEYS)
            numerics[label+'_negative_sign_disagreements']=int(np.sum(
                (original.S_change_slope_F_B.to_numpy() < -1e-6)!=
                (alt.S_change_slope_F_B.to_numpy() < -1e-6)))
    pd.DataFrame(counts).to_csv(OUT/'sign_counts.csv',index=False)
    report={'classification':'SYNTHETIC_NOT_EMPIRICAL','primary_scenarios':len(full),
            'primary_years':80,'window_years':20,'source_grid':[.25,1.,2.],
            'F_source':1,'primary_rho':.5,'sensitivity_scope':'all vegetation roles only, all variants and contexts',
            'numerics':numerics,'calling_predicted':False,'equilibrium_assumed':False}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
