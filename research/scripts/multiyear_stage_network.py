"""Synthetic annual feedback around the unchanged seasonal trophic hazards."""
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT, simulate

DEMOGRAPHY=dict(survival=(.4,.5,0.),conversion=(4.,4.,4.),juvenile=(.8,.8,.8),
                delays=(2,2,1),capacity=1.,initial_scale=1.)

def simulate_years(scenarios,years=80,dt=.25,source_cohorts=None,**demography):
    if set(demography)-set(DEMOGRAPHY):raise ValueError('Unknown demography')
    cfg={**DEMOGRAPHY,**demography}
    if not isinstance(years,int) or years<1:raise ValueError('Positive integer years required')
    arrays={k:np.asarray(cfg[k],dtype=float) for k in ('survival','conversion','juvenile','delays')}
    for k,a in arrays.items():
        if a.shape!=(3,) or not np.isfinite(a).all() or (a<0).any():raise ValueError('Invalid '+k)
    if (arrays['survival']>=1).any() or (arrays['juvenile']>1).any():raise ValueError('Invalid survival')
    if (arrays['delays']<1).any() or (arrays['delays']%1!=0).any():raise ValueError('Invalid delay')
    if not np.isfinite(cfg['capacity']) or cfg['capacity']<=0:raise ValueError('Invalid capacity')
    if not np.isfinite(cfg['initial_scale']) or cfg['initial_scale']<0:raise ValueError('Invalid initial scale')
    if not scenarios:raise ValueError('No scenarios')
    rho=np.array([r.get('rho',.5) for r in scenarios],float)[:,None]
    if not np.isfinite(rho).all() or (rho<0).any() or (rho>1).any():raise ValueError('Invalid local return')
    kernel=[{k:v for k,v in r.items() if k!='rho'}for r in scenarios]
    params=pd.DataFrame([{**DEFAULT,**r,'rho':float(rho[i,0])} for i,r in enumerate(kernel)])
    present=np.array([[1,int(r.community in ('FS','FSD')),int(r.community in ('FD','FSD'))]
                      for r in params.itertuples()],float)
    B=present*cfg['initial_scale'];s=arrays['survival'];b=arrays['conversion'];j=arrays['juvenile']
    m=arrays['delays'].astype(int);K=cfg['capacity']
    source=present if source_cohorts is None else np.asarray(source_cohorts,dtype=float)
    if source.shape!=present.shape or not np.isfinite(source).all() or (source<0).any():
        raise ValueError('Sources must be finite nonnegative n-by-3 F/S/D values')
    if ((present==0)&(source!=0)).any():raise ValueError('Source supplied for absent guild')
    if source_cohorts is not None:
        for k,g in enumerate('FSD'):params[g+'_source']=source[:,k]
    immigrant=(1-rho)*(1-s)*source
    upper=np.maximum(B,(rho*b*K+immigrant)/(1-s))
    completed=[];frames=[]
    for year in range(years):
        season=simulate(kernel,dt=dt,initial_cohorts=B)
        C=season[[g+'_completed' for g in 'FSD']].to_numpy(float)
        completed.append(C)
        due=np.zeros_like(B)
        for k in range(3):
            origin=year+1-m[k]
            if origin>=0:due[:,k]=completed[origin][:,k]
        local=rho*b*j**(m-1)*due/(1+due/K)
        next_B=s*B+local+immigrant
        if not np.isfinite(next_B).all() or (next_B<0).any() or (next_B>upper+1e-10).any():
            raise AssertionError('Invalid/unbounded annual population')
        frame=params.copy();frame.insert(0,'scenario_id',np.arange(len(params)));frame['year']=year
        for k,g in enumerate('FSD'):
            frame[g+'_B']=B[:,k];frame[g+'_C']=C[:,k]
            frame[g+'_fraction']=np.divide(C[:,k],B[:,k],out=np.full(len(B),np.nan),where=B[:,k]>0)
            frame[g+'_local']=local[:,k];frame[g+'_immigrant']=immigrant[:,k]
            frame[g+'_next_B']=next_B[:,k]
        for col in ('F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S','D_killed_by_F'):
            frame[col]=season[col].to_numpy()
        frames.append(frame);B=next_B
    return pd.concat(frames,ignore_index=True)

def scenario_grid():
    names=['community','roles','vegetation','refuge_order','f_arrival','rho','reverse']
    values=[['FD','FSD'],[0,1,2,4,8,15],[0.,1.],['S','D'],[10.,30.,50.],[0.,.5,1.],[False,True]]
    return [{**dict(zip(names,v)),'attack_scale':1.5,'cue':3.}for v in itertools.product(*values)]

def summarize(trajectory,window=20):
    last=int(trajectory.year.max());tail=trajectory[trajectory.year>last-window]
    keys=['scenario_id']+list(DEFAULT)+['rho']
    metrics=[g+s for g in 'FSD' for s in ('_B','_C','_fraction')]
    out=tail.groupby(keys,dropna=False)[metrics].mean().reset_index()
    variability=tail.groupby('scenario_id')[[g+'_B'for g in 'FSD']].std(ddof=0).add_suffix('_sd')
    out=out.merge(variability,on='scenario_id',validate='one_to_one')
    out['window_years']=min(window,last+1)
    return out

def paired(summary):
    keys=[k for k in DEFAULT if k!='reverse']+['rho']
    metrics=[g+s for g in 'FSD' for s in ('_B','_C','_fraction')]
    a=summary[~summary.reverse].set_index(keys)[metrics]
    b=summary[summary.reverse].set_index(keys)[metrics]
    if not a.index.is_unique or not b.index.is_unique:raise ValueError('Duplicate reversal context')
    if not a.index.equals(b.index):
        a=a.sort_index();b=b.sort_index()
    if not a.index.equals(b.index):raise ValueError('Unmatched reversal pairs')
    out=(b-a).add_prefix('delta_').reset_index()
    return out

def modifier_contrasts(pairs,column,low,high):
    keys=[k for k in DEFAULT if k not in ('reverse',column)]+['rho']
    metrics=[c for c in pairs if c.startswith('delta_')]
    a=pairs[pairs[column]==low].set_index(keys)[metrics].sort_index()
    b=pairs[pairs[column]==high].set_index(keys)[metrics].sort_index()
    if not a.index.is_unique or not b.index.is_unique or not a.index.equals(b.index):
        raise ValueError('Invalid modifier pairing')
    return (b-a).add_prefix('change_').reset_index()

def categories(values):
    return {'negative':int((values<-.005).sum()),'near_zero':int((values.abs()<=.005).sum()),
            'positive':int((values>.005).sum())}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    grid=scenario_grid();trajectory=simulate_years(grid)
    summary=summarize(trajectory);pairs=paired(summary)
    trajectory.to_csv(a.out/'trajectories.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    summary.to_csv(a.out/'last20_summary.csv',index=False);pairs.to_csv(a.out/'reversal_contrasts.csv',index=False)
    modifier_contrasts(pairs,'community','FD','FSD').to_csv(a.out/'third_party_modification.csv',index=False)
    modifier_contrasts(pairs,'vegetation',0,1).to_csv(a.out/'vegetation_modification.csv',index=False)
    print('Primary grid complete',len(grid),flush=True)
    subset=[r for r in grid if r['roles']==15]
    alternatives={'base':{},'short_delay':{'delays':(1,1,1)},'long_delay':{'delays':(3,3,2)},
                  'low_conversion':{'conversion':(2,2,2)},'high_conversion':{'conversion':(8,8,8)},
                  'low_juvenile_survival':{'juvenile':(.5,.5,.5)},'full_juvenile_survival':{'juvenile':(1,1,1)},
                  'no_adult_carryover':{'survival':(0,0,0)},'initial_low':{'initial_scale':.25},
                  'initial_high':{'initial_scale':2.},'horizon160':{'years':160},'half_step':{'dt':.125},
                  'no_cue':{}}
    sensitivity=[];summaries={}
    for label,kwargs in alternatives.items():
        scenarios=[{**r,'cue':0.}for r in subset] if label=='no_cue' else subset
        tr=simulate_years(scenarios,**kwargs);su=summarize(tr);summaries[label]=su
        pc=paired(su);pc.insert(0,'variant',label);sensitivity.append(pc)
        su.to_csv(a.out/(label+'_summary.csv'),index=False)
        tr.to_csv(a.out/(label+'_trajectories.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
        print('Sensitivity complete',label,flush=True)
    sensitivity=pd.concat(sensitivity,ignore_index=True)
    sensitivity.to_csv(a.out/'sensitivity_contrasts.csv',index=False)
    numeric=[g+s for g in 'FSD' for s in ('_B','_C')]
    fine_error=float(np.max(np.abs(summaries['base'][numeric].to_numpy()-summaries['half_step'][numeric].to_numpy())))
    reports={}
    for (community,rho),d in pairs.groupby(['community','rho']):
        reports[f'{community}|rho={rho}']={'F_B':categories(d.delta_F_B),'F_C':categories(d.delta_F_C),
                                          'delta_F_B_range':[float(d.delta_F_B.min()),float(d.delta_F_B.max())]}
    result={'classification':'SYNTHETIC_COUPLED_ANNUAL_FEEDBACK_NOT_EMPIRICAL','scenarios':len(grid),
            'years':80,'summary_last_years':20,'demography':DEMOGRAPHY,
            'counts_by_community_return':reports,'half_step_max_abs_mean_density_difference':fine_error,
            'half_step_scope':'all-role subset only','sensitivity_variants':list(alternatives),
            'equilibrium_assumed':False,'calling_predicted':False,
            'local_return_zero_max_F_effect':float(pairs[pairs.rho==0].delta_F_B.abs().max())}
    if result['local_return_zero_max_F_effect']>1e-12:raise AssertionError('Fixed input control failed')
    (a.out/'synthetic_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
