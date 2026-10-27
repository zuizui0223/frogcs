"""First full-range dynamic-stage success per model: intervention + sensitivity."""
import json
import argparse
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import OUT,KEYS,options,contrasts


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--robust',action='store_true');args=ap.parse_args()
    prefix='robust_selected' if args.robust else 'fullrange'
    c=pd.read_csv(OUT/'stage_grid_contrasts.csv',dtype={'size_gate':str})
    base=pd.read_csv(OUT/'stage_grid_summary.csv',dtype={'size_gate':str})
    q=c[(c.metric=='F_B')&(c.size_gate=='dynamic')&c.all_three&(c.D_low==.25)&(c.D_high==2)&(c.S_low==.25)&(c.S_high==2)]
    if args.robust:
        scores=pd.read_csv(OUT/'robust_stage_scores.csv')
        q=q.merge(scores,on=['profile','timing'],validate='one_to_one')
        q=q[q.passed==q.groupby('profile').passed.transform('max')]
    selected=q.sort_values(['profile','s_arrival','d_arrival','F_duration','S_duration','D_duration']).drop_duplicates('profile')
    selected.to_csv(OUT/(prefix+'_selection.csv'),index=False)
    variants={'full':{},'no_D_eats_S':{'edge_DS':0},'no_S_eats_D':{'edge_SD':0},
              'no_S_eats_F':{'edge_SF':0},'no_D_eats_F':{'edge_DF':0},
              'no_SF_refuge':{'cover_SF':0},'no_DF_refuge':{'cover_DF':0}}
    (OUT/(prefix+'_validation_design.json')).write_text(json.dumps(dict(
        selection=('Highest robustness count among baseline full-range successes, then numeric stage tuple; exploratory selection.' if args.robust else 'First full-range dynamic-stage success sorted by profile,S arrival,D arrival,F duration,S duration,D duration; no selection by effect magnitude.'),
        interventions=variants,checks=['half_step','horizon160','rho25','rho75','conversion2','conversion8'],
        stage_grid_was_exploratory=True),indent=2)+'\n',encoding='utf-8')
    all_summaries=[];all_contrasts=[]
    for r in selected.to_dict('records'):
        q=base[(base.profile==r['profile'])&(base.timing==r['timing'])].copy()
        fields=KEYS+['roles','rho','vegetation','S_source','D_source','f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration']
        original=q[fields].reset_index(drop=True)
        des=pd.concat([original.assign(intervention=label) for label in variants],ignore_index=True)
        for label,kw in [('interventions',{}),('half_step',{'dt':.125}),('horizon160',{'years':160}),
                         ('rho25',{}),('rho75',{}),('conversion2',{'conversion':(2,2,2)}),('conversion8',{'conversion':(8,8,8)})]:
            if args.robust and label not in ('interventions','half_step','horizon160'):continue
            dd=des.copy() if label=='interventions' else original.assign(intervention='full')
            if label in ('rho25','rho75'):dd['rho']=.25 if label=='rho25' else .75
            dur=dd[['F_duration','S_duration','D_duration']].to_numpy(float)
            opt=options(r['profile'],dd.vegetation.to_numpy(),dur);opt['diagnostics']=True
            for edge in ['edge_DS','edge_SD','edge_SF','edge_DF','cover_SF','cover_DF']:
                default=opt['pathway_controls'].get(edge,1.)
                opt['pathway_controls'][edge]=np.array([variants[x].get(edge,default) for x in dd.intervention])
            kernel=dd[[k for k in DEFAULT if k in dd]+['rho']].to_dict('records')
            source=np.column_stack([np.ones(len(dd)),dd.S_source,dd.D_source])
            tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt,**kw)
            for col,g in [('F_killed_by_S','F'),('F_killed_by_D','F'),('S_killed_by_D','S'),('D_killed_by_S','D')]:
                tr[col+'_fraction']=tr[col]/tr[g+'_B']
            cols=[x for x in tr if x.startswith(('F_','S_','D_','audit_')) and x not in ('F_source','S_source','D_source')]
            tail=tr[tr.year>tr.year.max()-20]
            su=tail.groupby('scenario_id')[cols].mean().join(dd.reset_index(drop=True)).reset_index()
            su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
            for intervention,z in su.groupby('intervention'):
                cc=contrasts(z);cc['intervention']=intervention;cc['check']=label;all_contrasts.append(cc)
            su['check']=label;all_summaries.append(su)
            print('Full-range check',r['profile'],label,flush=True)
    pd.concat(all_summaries,ignore_index=True).to_csv(OUT/(prefix+'_validation_summary.csv'),index=False)
    pd.concat(all_contrasts,ignore_index=True).to_csv(OUT/(prefix+'_validation_contrasts.csv'),index=False)


if __name__=='__main__':main()
