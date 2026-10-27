"""Unfitted timing controls; constants remove size dependence, not predation."""
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from multiyear_stage_network import simulate_years

OUT=Path(__file__).resolve().parents[1]/'results/stage_timing_20261026'
CONTEXTS={'baseline':((50,0,35),(45,70,60)),
          'same_start':((20,20,20),(45,70,60)),
          'same_exit':((50,25,35),(45,70,60)),
          'no_triple_overlap':((75,0,35),(45,70,60)),
          'equal_duration':((50,0,35),(60,60,60)),
          'fully_aligned':((20,20,20),(60,60,60))}
KEYS=['timing','size_mode','vegetation','refuge_order','reverse']
METRICS=['F_B','F_C','S_B','D_B','F_killed_by_S','F_killed_by_D','D_killed_by_S','S_killed_by_D','D_killed_by_F']


def main():
    OUT.mkdir(parents=True,exist_ok=True);summaries=[];overlaps=[]
    for timing,(arr,dur) in CONTEXTS.items():
        ends=np.array(arr)+dur
        overlaps.append(dict(timing=timing,F_arrival=arr[0],S_arrival=arr[1],D_arrival=arr[2],
            F_exit=ends[0],S_exit=ends[1],D_exit=ends[2],
            triple_days=max(0,min(ends)-max(arr)),
            FS_days=max(0,min(ends[:2])-max(arr[:2])),
            FD_days=max(0,min(ends[[0,2]])-max(arr[0],arr[2])),
            SD_days=max(0,min(ends[1:])-max(arr[1:])),
            reverse_days=max(0,min(120,ends[2]+5)-max(ends[0],ends[2]))))
    pd.DataFrame(overlaps).to_csv(OUT/'potential_overlap_days.csv',index=False)
    for durations in [(45,70,60),(60,60,60)]:
        for size_mode,gate in [('dynamic',None),('constant25',.25),('constant50',.5),('constant75',.75)]:
            rows=[]
            for timing,(arr,dur) in CONTEXTS.items():
                if dur!=durations:continue
                for v,order,reverse,s,d in itertools.product([0.,1.],['S','D'],[False,True],[.25,1.,2.],[.25,1.,2.]):
                    rows.append(dict(timing=timing,size_mode=size_mode,vegetation=v,refuge_order=order,
                        reverse=reverse,S_source=s,D_source=d,f_arrival=arr[0],s_arrival=arr[1],d_arrival=arr[2],
                        roles=15,attack_scale=1.5,cue=3.,rho=.5))
            design=pd.DataFrame(rows)
            kernel=design.drop(columns=['timing','size_mode','S_source','D_source']).to_dict('records')
            sources=np.column_stack([np.ones(len(design)),design.S_source,design.D_source])
            tr=simulate_years(kernel,source_cohorts=sources,seasonal_options={'stage_durations':durations,'size_gate':gate})
            label=('original_duration_' if durations==(45,70,60) else 'equal_duration_')+size_mode
            tr[['scenario_id','year']+METRICS].to_csv(OUT/(label+'_trajectory.csv.gz'),index=False,
                                                   compression={'method':'gzip','mtime':0})
            tail=tr[tr.year>=60]
            summary=tail.groupby('scenario_id')[METRICS].mean().join(design).reset_index()
            summary['F_B_sd']=tail.groupby('scenario_id').F_B.std(ddof=0).to_numpy()
            summary['batch']=label;summaries.append(summary)
            print('Completed',label,len(design),flush=True)
    q=pd.concat(summaries,ignore_index=True);q.to_csv(OUT/'summary.csv',index=False)
    output=[]
    for dl,dh in [(.25,2.),(.25,1.),(1.,2.)]:
        k=KEYS+['S_source']
        a=q[q.D_source==dl].set_index(k)[['F_B','F_C']].sort_index()
        b=q[q.D_source==dh].set_index(k)[['F_B','F_C']].sort_index()
        assert a.index.equals(b.index) and a.index.is_unique
        slope=((b-a)/(dh-dl)).add_prefix('slope_').reset_index()
        z=slope[slope.S_source==.25].merge(slope[slope.S_source==2],on=KEYS,suffixes=('_lowS','_highS'))
        z['change']=z.slope_F_B_highS-z.slope_F_B_lowS
        z['joint_negative']=(z.change < -1e-6)&(z.slope_F_B_highS < -1e-6)
        z['D_low']=dl;z['D_high']=dh;output.append(z)
    out=pd.concat(output,ignore_index=True);out.to_csv(OUT/'joint_signs.csv',index=False)
    before=out[~out.reverse].set_index([k for k in KEYS if k!='reverse']+['D_low','D_high'])
    after=out[out.reverse].set_index([k for k in KEYS if k!='reverse']+['D_low','D_high'])
    delta=(after[['change','slope_F_B_lowS','slope_F_B_highS']]-before[['change','slope_F_B_lowS','slope_F_B_highS']]).add_prefix('reverse_effect_')
    delta.to_csv(OUT/'reverse_modification.csv')
    (OUT/'design.json').write_text(json.dumps(dict(classification='SYNTHETIC_EXPLORATORY',contexts=CONTEXTS,
        scenarios=len(q),years=80,window=20,constant_gate_caveat='Changes mean attack rates as well as removes size dependence; three levels tested',
        missing='No calibration to stage observations, no emergence survival or field calling fit'),indent=2)+'\n',encoding='utf-8')
    print(out[(out.D_low==1)&(out.vegetation==1)&(out.refuge_order=='S')&out.reverse][['timing','size_mode','change','joint_negative']].to_string(index=False))


if __name__=='__main__':main()
