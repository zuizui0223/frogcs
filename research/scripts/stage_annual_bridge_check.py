"""Conditional linear renewal bridge, NOT a fitted coupled population model.

N[t+1] = adult_survival*N[t] + retained_recruitment*C*N[t+1-delay].
C is the existing single-season completion fraction, held fixed. Recruitment
bundles fecundity, terrestrial survival and local return, with arbitrary units.
Holding C fixed deliberately exposes what an annual link alone cannot explain.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

def growth(completion, retention, delay, survival=.5):
    if not 0 <= completion <= 1 or not 0 <= retention <= 1:
        raise ValueError('Completion and retention must be fractions')
    if delay not in (1,2,3) or not 0 <= survival <= 1:
        raise ValueError('Invalid delay or survival')
    matrix=np.zeros((delay,delay))
    matrix[0,0]=survival
    matrix[0,-1]+=retention*completion
    for k in range(1,delay): matrix[k,k-1]=1
    return float(np.max(np.abs(np.linalg.eigvals(matrix))))

def run(root):
    tables={name:pd.read_csv(root/file) for name,file in
            [('reverse','all_scenarios.csv.gz'),('no_reverse','no_reverse.csv.gz')]}
    parameters=['scenario_id','community','roles','refuge_order','f_arrival','s_arrival',
                'd_arrival','attack_scale','cue','vegetation']
    tables['no_reverse']=tables['reverse'][parameters].merge(tables['no_reverse'],
                                      on='scenario_id',validate='one_to_one')
    selected={}
    for name,d in tables.items():
        selected[name]=d[(d.community=='FSD')&(d.roles==15)&(d.refuge_order=='S')&
                         (d.f_arrival==30)&(d.s_arrival==0)&(d.d_arrival==35)&
                         (d.attack_scale==1.5)&(d.cue==3)].set_index('vegetation')
        assert len(selected[name])==2
    rows=[]
    for v in (0.,1.):
        for guild in ('F','S','D'):
            for delay in (1,3):
                for retention in (0.,.25,1.):
                    c={name:float(d.loc[v,guild+'_completed']) for name,d in selected.items()}
                    g={name:growth(value,retention,delay) for name,value in c.items()}
                    rows.append(dict(vegetation=v,guild=guild,delay=delay,retention=retention,
                                     completion=c,growth=g,difference=g['reverse']-g['no_reverse']))
    assert max(abs(r['difference']) for r in rows if r['guild']=='F')<1e-12
    assert max(abs(r['difference']) for r in rows if r['retention']==0)<1e-12
    assert all(r['difference']<=1e-12 for r in rows if r['guild']=='D')
    return {'status':'CONDITIONAL_LINEAR_BRIDGE_ONLY',
            'empirical_parameters':False,'density_feedback':False,'calling_observation_model':False,
            'interpretation':'Adding a recruitment delay alone cannot turn the current stage-reversal effect into a frog population effect; future dragonfly density must feed back into seasonal hazards.',
            'results':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,default=Path('research/results/stage_vegetation_network_20261026'))
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(run(a.source),indent=2)+'\n',encoding='utf-8')
