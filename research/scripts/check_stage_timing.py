"""Reproduce the limited half-step checks reported with the timing controls."""
import json
import numpy as np
import pandas as pd
from multiyear_stage_network import simulate_years
from run_stage_timing import OUT,CONTEXTS


def main():
    saved=pd.read_csv(OUT/'summary.csv');results=[]
    for timing,mode,gate in [('fully_aligned','dynamic',None),
                            ('no_triple_overlap','dynamic',None),('baseline','constant50',.5)]:
        arr,dur=CONTEXTS[timing]
        d=saved[(saved.timing==timing)&(saved.size_mode==mode)&(saved.vegetation==1)&(saved.refuge_order=='S')].copy()
        kernel=d[['vegetation','refuge_order','reverse','f_arrival','s_arrival','d_arrival','roles','attack_scale','cue','rho']].to_dict('records')
        src=np.column_stack([np.ones(len(d)),d.S_source,d.D_source])
        tr=simulate_years(kernel,dt=.125,source_cohorts=src,
                          seasonal_options={'stage_durations':dur,'size_gate':gate})
        values=tr[tr.year>=60].groupby('scenario_id').F_B.mean().to_numpy()
        error=float(np.max(abs(values-d.F_B.to_numpy())))
        frame=d[['S_source','D_source','reverse']].copy();frame['F_B']=values
        slope=frame[frame.D_source==2].set_index(['S_source','reverse']).F_B-frame[frame.D_source==1].set_index(['S_source','reverse']).F_B
        change=slope.loc[2]-slope.loc[.25]
        results.append(dict(timing=timing,size_mode=mode,max_F_B_error=error,
                            modifier_off=float(change.loc[False]),modifier_on=float(change.loc[True])))
        print(results[-1],flush=True)
    (OUT/'numerical_checks.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
