"""Final bounded robustness scan of the existing dynamic-stage grid."""
import json
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import OUT,options,contrasts,METRICS


def main():
    settings={'rho25':{},'rho75':{},'conversion2':{'conversion':(2,2,2)},'conversion8':{'conversion':(8,8,8)}}
    (OUT/'robust_stage_design.json').write_text(json.dumps(dict(
        reason='First full-range representatives failed low local return or conversion; scan the already-defined stage grid under the same four sensitivity settings.',
        no_new_stage_or_rate_values=True,profiles=['refuge_only','litter_response'],checks=settings,
        selection='Require full-range F_B joint match under baseline and all four demographic checks, then first numeric stage tuple. Exploratory selection, not independent confirmation.'),indent=2)+'\n',encoding='utf-8')
    outputs=[]
    for profile in ('refuge_only','litter_response'):
        original=pd.read_csv(OUT/('stage_'+profile+'_None_summary.csv'))
        fields=['profile','timing','refuge_order','attack_scale','cue','reverse','roles','rho',
                'vegetation','S_source','D_source','f_arrival','s_arrival','d_arrival',
                'F_duration','S_duration','D_duration','size_gate']
        for label,kw in settings.items():
            des=original[fields].copy()
            if label.startswith('rho'):des['rho']=.25 if label=='rho25' else .75
            opt=options(profile,des.vegetation.to_numpy(),des[['F_duration','S_duration','D_duration']].to_numpy())
            kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
            source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
            tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt,**kw)
            tail=tr[tr.year>=60]
            su=tail.groupby('scenario_id')[METRICS].mean().join(des.reset_index(drop=True)).reset_index()
            su['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
            su.to_csv(OUT/('robust_'+profile+'_'+label+'_summary.csv'),index=False)
            cc=contrasts(su);cc['check']=label;outputs.append(cc)
            print('Robustness grid',profile,label,flush=True)
    cc=pd.concat(outputs,ignore_index=True);cc.to_csv(OUT/'robust_stage_contrasts.csv',index=False)
    base=pd.read_csv(OUT/'stage_grid_contrasts.csv',dtype={'size_gate':str})
    base=base[base.size_gate=='dynamic'].copy();base['check']='baseline'
    allc=pd.concat([base,cc],ignore_index=True)
    q=allc[(allc.metric=='F_B')&(allc.D_low==.25)&(allc.D_high==2)&(allc.S_low==.25)&(allc.S_high==2)]
    stable=q.groupby(['profile','timing']).agg(passed=('all_three','sum'),tested=('all_three','size')).reset_index()
    stable.to_csv(OUT/'robust_stage_scores.csv',index=False)
    print(stable.groupby(['profile','passed']).size().to_string(),flush=True)


if __name__=='__main__':main()
