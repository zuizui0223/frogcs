"""Matched response-scale audit; no parameter reselection or tuning."""
from pathlib import Path
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT,simulate
from run_evidence_constrained import options
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/evidence_constrained_20261027'
OUT=ROOT/'results/response_scale_audit_20261027'

def compare(q,identity):
    x=q.set_index(['vegetation','S_source','D_source'])
    if len(x)!=18 or not x.index.is_unique:raise ValueError('Incomplete matched cells')
    rows=[]
    for metric in ['F_B','log_F_B','F_fraction','log_F_fraction','negative_H']:
        if metric not in x:continue
        for dl,dh in [(.25,2.),(1.,2.)]:
            ds=lambda v,s:(x.loc[(v,s,dh),metric]-x.loc[(v,s,dl),metric])/(dh-dl)
            ss=lambda v:(x.loc[(v,2.,1.),metric]-x.loc[(v,.25,1.),metric])/1.75
            dv=ds(1,1)-ds(0,1);sv=ss(1)-ss(0);sd=ds(1,2)-ds(1,.25)
            rows.append(dict(**identity,metric=metric,D_low=dl,DV=dv,SV=sv,SD=sd,D_highS=ds(1,2),all_three=dv<-1e-6 and sv>1e-6 and sd<-1e-6 and ds(1,2)<-1e-6))
    return rows

def transform(q):
    q=q.copy()
    if (q[['F_B','F_fraction']]<=0).any().any():raise ValueError('Log undefined; no pseudocount permitted')
    q['log_F_B']=np.log(q.F_B);q['log_F_fraction']=np.log(q.F_fraction)
    return q

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    q=transform(pd.read_csv(BASE/'minimal_summary.csv',dtype={'mask':str}))
    opt=options('refuge_only',q.vegetation.to_numpy(),q[['F_duration','S_duration','D_duration']].to_numpy())
    for k in ['edge_SF','edge_DF','edge_DS','edge_SD','cover_SF','cover_DF']:opt['pathway_controls'][k]=q[k].to_numpy()
    y=simulate(q[[k for k in DEFAULT if k in q]].to_dict('records'),initial_cohorts=q[['F_B','S_B','D_B']].to_numpy(),diagnostics=True,**opt)
    for k in ['audit_H_SF','audit_H_DF','audit_H_SD']:q[k]=y[k].to_numpy()
    q['negative_H']=-q.audit_H_SF-q.audit_H_DF
    err=np.max(abs(y.F_completed.to_numpy()/q.F_B-q.F_fraction))
    if err>1e-8:raise AssertionError(f'Mean-state replay not exact: {err}')
    if not np.allclose(q.negative_H,q.log_F_fraction,rtol=0,atol=1e-8):raise AssertionError('Hazard identity failed')
    q.to_csv(OUT/'minimal_diagnostics.csv',index=False)
    rows=[]
    for mask,z in q.groupby('mask'):rows+=compare(z,dict(mask=mask))
    cs=pd.DataFrame(rows);cs.to_csv(OUT/'minimal_scale_contrasts.csv',index=False)
    print('Selected and deletion controls: full range')
    print(cs[(cs['mask'].isin(['110110','110010','010110','111111']))&(cs.D_low==.25)].to_string(index=False))
    print('All 64 masks, full range counts',cs[cs.D_low==.25].groupby('metric').all_three.sum().to_dict())
    # Exhaustively discovered scale-consistent candidate; no rate tuning.
    from multiyear_stage_network import simulate_years
    cand=q[q['mask']=='111110'].copy().reset_index(drop=True)
    controls=options('refuge_only',cand.vegetation.to_numpy(),cand[['F_duration','S_duration','D_duration']].to_numpy())
    for k in ['edge_SF','edge_DF','edge_DS','edge_SD','cover_SF','cover_DF']:controls['pathway_controls'][k]=cand[k].to_numpy()
    controls['diagnostics']=True
    source=np.column_stack([np.ones(len(cand)),cand.S_source,cand.D_source])
    sensitivity=[]
    for label,kwargs in {'half_step':{'dt':.125},'horizon160':{'years':160},'rho25':{},'rho75':{},'conversion2':{'conversion':(2,2,2)},'conversion8':{'conversion':(8,8,8)}}.items():
        des=cand.copy()
        if label.startswith('rho'):des['rho']=float(label[3:])/100
        kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
        tr=simulate_years(kernel,source_cohorts=source,seasonal_options=controls,**kwargs)
        tail=tr[tr.year>tr.year.max()-20].copy()
        tail['negative_H']=-tail.audit_H_SF-tail.audit_H_DF
        if not np.allclose(np.log(tail.F_fraction),tail.negative_H,rtol=0,atol=1e-10):raise AssertionError('Seasonal hazard identity failed')
        av=tail.groupby('scenario_id')[['F_B','F_fraction','negative_H']].mean()
        av=transform(av.join(des[['vegetation','S_source','D_source']]))
        av.to_csv(OUT/('candidate_'+label+'_summary.csv'),index=False)
        sensitivity+=compare(av,dict(mask='111110',check=label))
    sensitivity=pd.DataFrame(sensitivity);sensitivity.to_csv(OUT/'candidate_sensitivity.csv',index=False)
    print(sensitivity[(sensitivity.D_low==.25)&sensitivity.metric.isin(['F_B','log_F_fraction','negative_H'])].to_string(index=False))
    # Broader original dynamic stage configurations, unchanged attack scales.
    z=transform(pd.read_csv(BASE/'stage_grid_summary.csv',low_memory=False))
    z=z[z.timing.str.endswith('gateNone')]
    rows=[]
    for (profile,timing),g in z.groupby(['profile','timing']):rows+=compare(g,dict(profile=profile,timing=timing))
    st=pd.DataFrame(rows);st.to_csv(OUT/'dynamic_stage_scale_contrasts.csv',index=False)
    count=st[st.D_low==.25].groupby(['profile','metric']).all_three.agg(['sum','count'])
    count.to_csv(OUT/'dynamic_stage_counts.csv');print(count.to_string());print('Replay error',err)

if __name__=='__main__':main()

