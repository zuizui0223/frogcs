"""Directed intervention on deterministic first refuge-only local success."""
import json
import argparse
import numpy as np
import pandas as pd
from run_evidence_constrained import OUT,TIMINGS,options,contrasts
from multiyear_stage_network import simulate_years


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--profile',default='refuge_only',choices=['refuge_only','litter_response']);args=ap.parse_args()
    prefix='candidate_' if args.profile=='refuge_only' else 'litter_candidate_'
    files=[OUT/(args.profile+'_'+str(d)+'_summary.csv') for d in (45,60)]
    su=pd.concat([pd.read_csv(p) for p in files])
    c=contrasts(su)
    keys=['profile','timing','refuge_order','attack_scale','cue','reverse']
    candidates=c[(c.metric=='F_B')&c.all_three&(c.D_low==1)&(c.D_high==2)&(c.S_low==.25)&(c.S_high==2)]
    r=candidates.sort_values(keys).iloc[0]
    mask=np.ones(len(su),bool)
    for k in keys:mask&=su[k]==r[k]
    cols=['profile','timing','refuge_order','attack_scale','cue','reverse','vegetation',
          'S_source','D_source','f_arrival','s_arrival','d_arrival','roles','rho']
    des=su.loc[mask,cols].reset_index(drop=True)
    variants={'full':{},'no_D_eats_S':{'edge_DS':0},'no_S_eats_D':{'edge_SD':0},
              'no_S_eats_F':{'edge_SF':0},'no_D_eats_F':{'edge_DF':0},
              'no_SF_refuge':{'cover_SF':0},'no_DF_refuge':{'cover_DF':0}}
    summaries=[];signs=[]
    for label,extra in variants.items():
        opt=options(args.profile,des.vegetation.to_numpy(),TIMINGS[r.timing][1])
        opt['pathway_controls'].update(extra);opt['diagnostics']=True
        kernel=des.drop(columns=['profile','timing','S_source','D_source']).to_dict('records')
        source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
        tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt)
        for col,g in [('F_killed_by_S','F'),('F_killed_by_D','F'),('S_killed_by_D','S'),('D_killed_by_S','D')]:
            tr[col+'_fraction']=tr[col]/tr[g+'_B']
        metrics=[x for x in tr if x.startswith(('F_','S_','D_','audit_')) and x not in ('F_source','S_source','D_source')]
        summary=tr[tr.year>=60].groupby('scenario_id')[metrics].mean().join(des).reset_index()
        cc=contrasts(summary);cc['intervention']=label;signs.append(cc)
        summary['intervention']=label;summaries.append(summary)
        tr.to_csv(OUT/(prefix+label+'_trajectory.csv.gz'),index=False,compression={'method':'gzip','mtime':0})
        print('Audited candidate',label,flush=True)
    pd.concat(summaries,ignore_index=True).to_csv(OUT/(prefix+'pathway_summary.csv'),index=False)
    pd.concat(signs,ignore_index=True).to_csv(OUT/(prefix+'pathway_contrasts.csv'),index=False)
    (OUT/(prefix+'selection.json')).write_text(json.dumps(r.to_dict(),indent=2,default=str)+'\n',encoding='utf-8')


if __name__=='__main__':main()
