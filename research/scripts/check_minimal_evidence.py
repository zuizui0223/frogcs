"""Numerical/demographic checks of both inclusion-minimal removal subsets."""
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import OUT,options,contrasts,METRICS


def main():
    passing=pd.read_csv(OUT/'minimal_passing.csv',dtype={'mask':str})
    masks=passing[passing.inclusion_minimal]['mask'].tolist()
    base=pd.read_csv(OUT/'minimal_summary.csv',dtype={'mask':str})
    fields=['profile','timing','refuge_order','attack_scale','cue','reverse','roles','rho',
            'vegetation','S_source','D_source','f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration','mask']
    edges=['edge_SF','edge_DF','edge_DS','edge_SD','cover_SF','cover_DF']
    original=base[base['mask'].isin(masks)][fields+edges].reset_index(drop=True)
    outputs=[]
    for label,kwargs in [('half_step',{'dt':.125}),('horizon160',{'years':160}),
                         ('rho25',{}),('rho75',{}),('conversion2',{'conversion':(2,2,2)}),('conversion8',{'conversion':(8,8,8)})]:
        des=original.copy()
        if label.startswith('rho'):des['rho']=.25 if label=='rho25' else .75
        opt=options('refuge_only',des.vegetation.to_numpy(),des[['F_duration','S_duration','D_duration']].to_numpy())
        for k in edges:opt['pathway_controls'][k]=des[k].to_numpy()
        kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
        source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
        tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt,**kwargs)
        tail=tr[tr.year>tr.year.max()-20]
        su=tail.groupby('scenario_id')[METRICS].mean().join(des).reset_index()
        su.to_csv(OUT/('minimal_'+label+'_summary.csv'),index=False)
        for mask,z in su.groupby('mask'):
            cc=contrasts(z);cc['mask']=mask;cc['check']=label;outputs.append(cc)
        print('Minimal check',label,flush=True)
    pd.concat(outputs,ignore_index=True).to_csv(OUT/'minimal_checks.csv',index=False)


if __name__=='__main__':main()
