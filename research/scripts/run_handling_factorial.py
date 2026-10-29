"""Four directed handling controls; fixed rank analysis plus physical hazards."""
import argparse
import hashlib
import itertools
import json
import numpy as np
import pandas as pd
from handling_annual_summary_20261029 import summarize_years
from stage_handling_factorial_20261029 import simulate
from common_scale_comparison import weighted_core,features,transform
from separate_mechanism_observation import empirical_weights
from nee_context_robustness import ROOT,load

OUT=ROOT/'research/results/handling_factorial_20261029'
ANCHORS=['0000','1000','0100','1100','1111']
LABELS={'0000':'none','1000':'F_saturation_only','0100':'D_time_on_F_only','1100':'both_F_paths','1111':'full_shared'}


def evaluate(ids,levels,dt,tag,annual=True,initial_state=None):
    rows=[]
    for arm in ids:
        for v,s,d in itertools.product([0.,1.],np.linspace(.25,2.,levels),np.linspace(.25,2.,levels)):
            rows.append(dict(arm=arm,FF=int(arm[0]),FD=int(arm[1]),DF=int(arm[2]),DD=int(arm[3]),vegetation=v,S_source=s,D_source=d))
    de=pd.DataFrame(rows);path=OUT/f'{tag}_cells.csv.gz'
    if path.exists():
        su=pd.read_csv(path,dtype={'arm':str})
        pd.testing.assert_frame_equal(su[de.columns],de,check_dtype=False)
        return su
    params=[dict(community='FSD',roles=15,refuge_order='D',vegetation=r.vegetation,f_arrival=20.,s_arrival=20.,d_arrival=0.,attack_scale=.5,cue=0.,reverse=False,rho=.75) for r in de.itertuples()]
    controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,cue_SD=0.)
    opts=dict(pathway_controls=controls,stage_durations=(45,80,40),functional_response='litter',s_handling_matrix=de[['FF','FD','DF','DD']].to_numpy(float))
    source=np.column_stack([np.ones(len(de)),de.S_source,de.D_source])
    if initial_state is not None:
        pd.testing.assert_frame_equal(initial_state[de.columns].reset_index(drop=True),de,check_dtype=False)
        source=initial_state[['F_B','S_B','D_B']].to_numpy(float)
    if annual:su=summarize_years(params,years=80,window=20,dt=dt,source_cohorts=source,seasonal_options=opts,conversion=4.)
    else:
        su=simulate([{k:v for k,v in p.items() if k!='rho'} for p in params],dt=dt,initial_cohorts=source,diagnostics=True,**opts)
        su=su[['F_killed_by_S','F_killed_by_D','S_killed_by_D','D_killed_by_S','audit_H_DF','audit_H_SF','F_completed']].copy()
        su['F_B']=source[:,0];su['F_fraction']=su.F_completed/source[:,0];su['minimum_F_survival']=su.F_fraction
    result=pd.concat([de,su],axis=1)
    result.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
    print('Finished',tag,len(result),flush=True)
    return result


def physical_contrasts(g):
    rows=[]
    g=g.set_index(['vegetation','S_source','D_source'])
    for path in ['audit_H_DF','audit_H_SF','H_total']:
        z=g[path]
        for v in [0.,1.]:
            value=z.loc[(v,2.,2.)]-z.loc[(v,2.,.25)]-z.loc[(v,.25,2.)]+z.loc[(v,.25,.25)]
            rows.append(dict(path=path,contrast='OS',at=v,value=value))
        for s in [.25,2.]:
            value=z.loc[(1.,s,2.)]-z.loc[(1.,s,.25)]-z.loc[(0.,s,2.)]+z.loc[(0.,s,.25)]
            rows.append(dict(path=path,contrast='OV',at=s,value=value))
        for d in [.25,2.]:
            value=z.loc[(1.,2.,d)]-z.loc[(1.,.25,d)]-z.loc[(0.,2.,d)]+z.loc[(0.,.25,d)]
            rows.append(dict(path=path,contrast='SV',at=d,value=value))
    return rows


def summarize(cells,levels,tag,d,annual=True):
    cells=cells.copy();cells['H_total']=cells.audit_H_DF+cells.audit_H_SF
    macro=pd.read_csv(ROOT/'research/results/scale_comparison_20261029/macro_common_estimators.csv')
    macro=macro[(macro.vegetation=='binary')&(macro.x_transform=='rank')&(macro.y_transform=='rank')&(macro.adjustment=='space')&(macro['mode']=='pooled')]
    coeff=[];contrasts=[];corners=[];hfits=[]
    for arm,g in cells.groupby('arm'):
        g=g.sort_values(['vegetation','S_source','D_source'])
        cs=physical_contrasts(g)
        for r in cs:contrasts.append(dict(arm=arm,label=LABELS.get(arm,arm),**r))
        total=[r for r in cs if r['path']=='H_total']
        physical_pass=all(r['value']>0 if r['contrast']!='SV' else r['value']<0 for r in total)
        corner=g[g.S_source.isin([.25,2.])&g.D_source.isin([.25,2.])]
        corners.append(corner)
        if not annual:continue
        for bg in ['uniform','target_group']:
            w=empirical_weights(d,bg,levels)
            r=weighted_core(g.D_source.to_numpy(),g.S_source.to_numpy(),g.vegetation.to_numpy(),g.F_B.to_numpy(),w,'rank','rank')
            q=macro[macro.background==bg].set_index('term')
            coeff.append(dict(arm=arm,label=LABELS.get(arm,arm),background=bg,rank_signs=bool(r['OS']<0 and r['OV']<0 and r['SV']>0),all_three_intervals=all(q.loc[t,'low']<=r[t]<=q.loc[t,'high'] for t in ['OS','OV','SV']),physical_corner_signs=physical_pass,**r))
            # Fixed supplementary outcome in physical cumulative-hazard units.
            keep=w>0;ww=w[keep];sw=np.sqrt(ww)
            x=features(*[transform(g[k].to_numpy()[keep],ww,'rank') for k in ['D_source','S_source','vegetation']]);x=np.column_stack([x,np.ones(len(x))])
            for name in ['audit_H_DF','audit_H_SF','H_total']:
                beta=np.linalg.lstsq(x*sw[:,None],g[name].to_numpy()[keep]*sw,rcond=None)[0]
                hfits.append(dict(arm=arm,background=bg,path=name,OS=beta[3],OV=beta[4],SV=beta[5],OSV=beta[6]))
    pd.DataFrame(contrasts).to_csv(OUT/f'{tag}_physical_contrasts.csv',index=False)
    pd.concat(corners).to_csv(OUT/f'{tag}_corner_mortality.csv',index=False)
    if annual:
        pd.DataFrame(coeff).to_csv(OUT/f'{tag}_rank_coefficients.csv',index=False)
        pd.DataFrame(hfits).to_csv(OUT/f'{tag}_hazard_coefficients.csv',index=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checks',action='store_true');args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);d=load()
    if args.checks:
        for tag,levels,dt in [('dense21',21,.25),('half_step',9,.125)]:
            cells=evaluate(ANCHORS,levels,dt,tag);summarize(cells,levels,tag,d)
    else:
        arms=[''.join(map(str,b)) for b in itertools.product([0,1],repeat=4)]
        cells=evaluate(arms,9,.25,'primary');summarize(cells,9,'primary',d)
        one=evaluate(arms,9,.125,'one_season',annual=False);summarize(one,9,'one_season',d,annual=False)
        matched=evaluate(arms,9,.25,'state_matched_season',annual=False,initial_state=cells)
        summarize(matched,9,'state_matched_season',d,annual=False)
        np.testing.assert_allclose(matched[['audit_H_DF','audit_H_SF']],cells[['audit_H_DF','audit_H_SF']],atol=1e-6)
        old=pd.read_csv(ROOT/'research/results/literature_extension_20261029/primary_0_dynamic_cells.csv.gz')
        for arm,case in [('0000',0),('1111',10)]:
            a=cells[cells.arm==arm].sort_values(['vegetation','S_source','D_source'])
            b=old[old['case']==case].sort_values(['vegetation','S_source','D_source'])
            np.testing.assert_allclose(a[['F_B','audit_H_DF','audit_H_SF']],b[['F_B','audit_H_DF','audit_H_SF']],atol=1e-12)
        (OUT/'receipt.json').write_text(json.dumps(dict(primary_arms=16,primary_cells=len(cells),rank_scale_fixed=True,previous_baseline_and_full_replayed=True,calling_map_fitted=False,
            interpretation='Directed handling ablations are diagnostic, not all physically complete feeding laws',
            hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'research/scripts/stage_handling_factorial_20261029.py',ROOT/'research/scripts/handling_annual_summary_20261029.py']}),indent=2)+'\n')


if __name__=='__main__':main()
