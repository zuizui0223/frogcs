"""All 64 combinations of existing four feeding edges and two refuge edges.

No new parameter values: removal-only test at the robust selected stage.
"""
import itertools
import json
import numpy as np
import pandas as pd
from stage_vegetation_network import DEFAULT
from multiyear_stage_network import simulate_years
from run_evidence_constrained import OUT,options,contrasts,METRICS


def main():
    su=pd.read_csv(OUT/'robust_selected_validation_summary.csv')
    q=su[(su.profile=='refuge_only')&(su.check=='interventions')&(su.intervention=='full')]
    fields=['profile','timing','refuge_order','attack_scale','cue','reverse','roles','rho',
            'vegetation','S_source','D_source','f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration']
    edges=['edge_SF','edge_DF','edge_DS','edge_SD','cover_SF','cover_DF']
    frames=[]
    for mask in itertools.product([0.,1.],repeat=6):
        frame=q[fields].copy();frame['mask']=''.join(str(int(v)) for v in mask)
        for k,v in zip(edges,mask):frame[k]=v
        frames.append(frame)
    des=pd.concat(frames,ignore_index=True)
    (OUT/'minimal_design.json').write_text(json.dumps(dict(edges=edges,
        selection='Previously selected robust refuge-only stage; removal-only full factorial, no added rates',
        rule='A passing subset is inclusion-minimal if no strict passing subset exists; no prevalence interpretation'),indent=2)+'\n',encoding='utf-8')
    opt=options('refuge_only',des.vegetation.to_numpy(),des[['F_duration','S_duration','D_duration']].to_numpy())
    for k in edges:opt['pathway_controls'][k]=des[k].to_numpy()
    kernel=des[[k for k in DEFAULT if k in des]+['rho']].to_dict('records')
    source=np.column_stack([np.ones(len(des)),des.S_source,des.D_source])
    tr=simulate_years(kernel,source_cohorts=source,seasonal_options=opt)
    summary=tr[tr.year>=60].groupby('scenario_id')[METRICS].mean().join(des).reset_index()
    output=[]
    for mask,z in summary.groupby('mask'):
        cc=contrasts(z);cc['mask']=mask;output.append(cc)
    cs=pd.concat(output,ignore_index=True)
    summary.to_csv(OUT/'minimal_summary.csv',index=False);cs.to_csv(OUT/'minimal_contrasts.csv',index=False)
    full=cs[(cs.metric=='F_B')&(cs.D_low==.25)&(cs.D_high==2)&(cs.S_low==.25)&(cs.S_high==2)]
    passing=full[full.all_three].copy()
    sets={mask:{k for k,v in zip(edges,mask) if v=='1'} for mask in passing['mask']}
    passing['inclusion_minimal']=[not any(other<sets[m] for other in sets.values()) for m in passing['mask']]
    passing.to_csv(OUT/'minimal_passing.csv',index=False)
    print(passing[['mask','DV','SV','SD','all_three','inclusion_minimal']].to_string(index=False),flush=True)


if __name__=='__main__':main()
