"""Read-only recomputation from saved final mechanism cells; no simulations."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parents[2]/'final_mechanism_20261027'
OUT=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'research/scripts'))
from final_mechanism_common import score
scores=pd.read_csv(P/'validation_scores.csv')
scores=scores[(scores.model_id==1479)&(scores.block_id>=0)]
scores=pd.concat([scores,pd.read_csv(P/'reduced_validation_scores.csv')],ignore_index=True)
assert len(scores)==48
inputs=[P/'validation_scores.csv',P/'reduced_validation_scores.csv',P/'validation_design.json']
cells=[]
for block in range(24):
    f=P/f'validation_{block}_none_1_cells.csv.gz';inputs.append(f)
    d=pd.read_csv(f);cells.append(d[d.model_id==1479])
for f in [P/'reduced_None_cells.csv.gz',P/'reduced_0.5_cells.csv.gz']:
    inputs.append(f);cells.append(pd.read_csv(f))
cells=pd.concat(cells,ignore_index=True)
assert len(cells)==48*18
constraints=[];paths=[];ranges=[]
for (mid,bid),d in cells.groupby(['model_id','block_id']):
    d=d.sort_values(['vegetation','S_source','D_source']).reset_index(drop=True)
    replay=score(d).iloc[0];saved=scores[(scores.model_id==mid)&(scores.block_id==bid)].iloc[0]
    for k in ['rank_DS','rank_DV','rank_SV','rank_DSV','F_B_DV','F_B_SV','F_B_SD','log_F_survival_SD']:
        np.testing.assert_allclose(replay[k],saved[k],atol=1e-10,rtol=1e-10)
    rec=dict(model_id=mid,block_id=bid,floor_avoiding=bool(saved.floor_avoiding),conditional_pass=bool(saved.conditional_pass),macro_form_pass=bool(saved.macro_form_pass),joint_pass=bool(saved.joint_pass),min_F=saved.min_F,min_S=saved.min_S)
    responses={'F_B':d.F_B.to_numpy(),'log_F_B':np.log(d.F_B.to_numpy()),'log_F_survival':np.log(d.F_fraction.to_numpy()),'negative_H':-d.audit_H_SF.to_numpy()-d.audit_H_DF.to_numpy()}
    for name,val in responses.items():
        a=val.reshape(2,3,3);ds=(a[:,:,2]-a[:,:,0])/1.75;ss=(a[:,2,1]-a[:,0,1])/1.75
        values={'DV':ds[1,1]-ds[0,1],'SV':ss[1]-ss[0],'SD':ds[1,2]-ds[1,0],'D_harm_highV_highS':ds[1,2]}
        for k,v in values.items():
            rec[name+'_'+k]=v;rec[name+'_'+k+'_ok']=bool(v>1e-6 if k=='SV' else v< -1e-6)
    for term in ['DS','DV','SV']:
        v=saved['rank_'+term];rec['rank_'+term]=v;rec['rank_'+term+'_ok']=bool(v>1e-6 if term=='SV' else v< -1e-6)
    constraints.append(rec)
    for v,q in d.groupby('vegetation'):
        arr={k:q[k].to_numpy().reshape(3,3) for k in ['audit_H_SF','audit_H_DF','F_B','F_fraction','S_B','D_B']}
        changes={k:x[:,-1]-x[:,0] for k,x in arr.items()}
        x={k:z[-1]-z[0] for k,z in changes.items()}
        paths.append(dict(model_id=mid,block_id=bid,vegetation=v,DD_HSF=x['audit_H_SF'],DD_HDF=x['audit_H_DF'],DD_H_total=x['audit_H_SF']+x['audit_H_DF'],DD_F_B=x['F_B'],DD_F_fraction=x['F_fraction'],SF_offset_fraction=(-x['audit_H_SF']/x['audit_H_DF'] if x['audit_H_DF']>0 else np.nan),min_F_B=q.F_B.min(),max_F_B=q.F_B.max(),min_S_B=q.S_B.min(),max_S_B=q.S_B.max(),min_D_B=q.D_B.min(),max_D_B=q.D_B.max()))
    for response,values in responses.items():
        arr=values.reshape(2,3,3)
        for v in [0,1]:
            row_changes=arr[v,:,-1]-arr[v,:,0]
            ranges.append(dict(model_id=mid,block_id=bid,response=response,vegetation=v,D_effect_Slow=row_changes[0],D_effect_Smid=row_changes[1],D_effect_Shigh=row_changes[2],interaction_high_minus_low=row_changes[2]-row_changes[0]))
c=pd.DataFrame(constraints).sort_values(['model_id','block_id']);c.to_csv(OUT/'criterion_audit.csv',index=False)
pd.DataFrame(paths).to_csv(OUT/'hazard_path_audit.csv',index=False)
pd.DataFrame(ranges).to_csv(OUT/'conditional_effects.csv',index=False)
counts=[]
for mid,g in c.groupby('model_id'):
    for col in ['conditional_pass','macro_form_pass','joint_pass','floor_avoiding']+[x for x in c if x.endswith('_ok')]:
        counts.append(dict(model_id=mid,criterion=col,pass_count=int(g[col].sum()),total=len(g)))
pd.DataFrame(counts).to_csv(OUT/'criterion_counts.csv',index=False)
blocks=pd.DataFrame(json.loads((P/'validation_design.json').read_text())['blocks']);blocks=blocks[blocks.block_id>=0]
c.merge(blocks,on='block_id',validate='many_to_one').to_csv(OUT/'criteria_with_context.csv',index=False)
receipt=dict(replayed_model_contexts=48,existing_cells=864,new_simulations=0,inputs=[dict(path=f.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in inputs])
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(pd.DataFrame(counts).to_string(index=False))
print(pd.DataFrame(paths).query('model_id==1479 and block_id==13').to_string(index=False))

# Recompute scale/resolution diagnostics on the already saved leader grid.
from scipy.stats import rankdata
f=P/'winner_rank_cells.csv.gz';grid=pd.read_csv(f);inputs.append(f);scale_rows=[]
def z(a):
    a=np.asarray(a);return (a-a.mean())/a.std()
for levels,g in grid.groupby('levels'):
    D=z(rankdata(g.D_source));S=z(rankdata(g.S_source));V=z(g.vegetation)
    x=np.column_stack([D,S,V,D*S,D*V,S*V,D*S*V])
    np.testing.assert_allclose(x.T@x/len(g),np.eye(7),atol=1e-12)
    for outcome,raw in {'F_B':g.F_B,'log_F_B':np.log(g.F_B),'negative_H':-g.audit_H_DF-g.audit_H_SF}.items():
        for transform in ['standardized_value','standardized_rank']:
            y=z(raw if transform=='standardized_value' else rankdata(raw));b=np.linalg.lstsq(x,y,rcond=None)[0]
            rec=dict(levels=levels,outcome=outcome,transform=transform,rows=len(g),DS_lowV=b[3]-b[6],DS_highV=b[3]+b[6],R2=float(np.mean((x@b)**2)),DS_variance_share=b[3]**2,threeway_variance_share=b[6]**2,all_interaction_variance_share=float(np.sum(b[3:]**2)),main_effect_variance_share=float(np.sum(b[:3]**2)))
            rec.update(dict(zip(['D','S','V','DS','DV','SV','DSV'],b)));scale_rows.append(rec)
pd.DataFrame(scale_rows).to_csv(OUT/'grid_scale_diagnostics.csv',index=False)
receipt['inputs']=[dict(path=f.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in inputs]
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
