"""Same-context tests of observed sign combinations; no parameter fitting.

Primary: source .25->2, other guild fixed at1; V0->1; F breeding index.
Adjacent ranges and completion are sensitivities. Positive S-direction means
its slope becomes more positive, not necessarily that its slope is positive.
"""
from pathlib import Path
import json
import itertools
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/joint_vegetation_20261027'


def assess(d,keys):
    rows=[]
    for context,g in d.groupby(keys,dropna=False):
        if not isinstance(context,tuple):context=(context,)
        base=dict(zip(keys,context))
        assert not g.duplicated(['vegetation','S_source','D_source']).any()
        q=g.set_index(['vegetation','S_source','D_source'])
        for (low,high),(sl,sh) in itertools.product([(.25,2.),(.25,1.),(1.,2.)],repeat=2):
            for metric in ['F_B','F_C']:
                def value(v,s,dd):return float(q.loc[(v,s,dd),metric])
                ds=[(value(v,1.,high)-value(v,1.,low))/(high-low) for v in [0.,1.]]
                ss=[(value(v,sh,1.)-value(v,sl,1.))/(sh-sl) for v in [0.,1.]]
                # Third-party contrast at each vegetation level, same range.
                sd=[((value(v,sh,high)-value(v,sh,low))-
                     (value(v,sl,high)-value(v,sl,low)))/(high-low) for v in [0.,1.]]
                d_highs=(value(1.,sh,high)-value(1.,sh,low))/(high-low)
                dv=ds[1]-ds[0];sv=ss[1]-ss[0]
                joint=dv < -1e-6 and sv > 1e-6
                rows.append(base|dict(low=low,high=high,S_low=sl,S_high=sh,metric=metric,D_slope_V0=ds[0],D_slope_V1=ds[1],
                    S_slope_V0=ss[0],S_slope_V1=ss[1],DV=dv,SV=sv,
                    SD_V0=sd[0],SD_V1=sd[1],D_highS_V1=d_highs,
                    vegetation_joint=joint,
                    all_three_directions=joint and sd[1] < -1e-6,
                    all_three_with_negative_D=joint and sd[1] < -1e-6 and d_highs < -1e-6))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(exist_ok=True);frames=[]
    for path in sorted((ROOT/'results/source_gradient_20261026').glob('*_summary.csv')):
        result=assess(pd.read_csv(path),['roles','refuge_order','f_arrival','variant'])
        result['run']=path.name.removesuffix('_summary.csv');frames.append(result)
    out=pd.concat(frames,ignore_index=True);out.to_csv(OUT/'source_contrasts.csv',index=False)
    counts=out.groupby(['run','variant','low','high','S_low','S_high','metric']).agg(
        n=('DV','size'),vegetation_joint=('vegetation_joint','sum'),
        all_three_directions=('all_three_directions','sum'),
        all_three_with_negative_D=('all_three_with_negative_D','sum')).reset_index()
    counts.to_csv(OUT/'sign_counts.csv',index=False)
    null=out[(out.run=='primary')&(out.roles==0)]
    error=float(null[['DV','SV']].abs().to_numpy().max());assert error < 1e-10
    stage=assess(pd.read_csv(ROOT/'results/stage_timing_20261026/summary.csv'),
                 ['timing','size_mode','refuge_order','reverse'])
    stage.to_csv(OUT/'timing_contrasts.csv',index=False)
    (OUT/'design.json').write_text(json.dumps(dict(classification='EXPLORATORY_SAVED_MODEL_PATTERN_CHECK',
        primary='F_B, sources .25->2, other guild fixed1, vegetation0->1; all existing contexts',
        secondary='All independent adjacent/full S and D interval combinations, F_C, timing controls; all reported',
        strict='DV<0 and SV>0; add SD at V1<0 and D slope highS V1<0 separately',
        unchanged_model=True,no_vegetation_role_null_error=error),indent=2)+'\n',encoding='utf-8')
    print(counts[(counts.metric=='F_B')&(counts.variant=='full')&(counts.S_low==.25)&(counts.S_high==2)].to_string(index=False))
    print(out[(out.run=='primary')&(out.metric=='F_B')&(out.variant=='full')&out.all_three_with_negative_D].to_string(index=False))


if __name__=='__main__':main()
