"""Refine every local intervention equally, without selecting favorable cases."""
import itertools
import hashlib
import json
import numpy as np
import pandas as pd
from final_mechanism_common import evaluate
from diagnose_model_contexts import OPT
from separate_mechanism_observation import OUT,SOURCE,empirical_weights
from common_scale_comparison import weighted_core
from nee_context_robustness import ROOT, load


def main():
    d=load();records=[]
    for gate in [None,.5]:
        src=pd.read_csv(SOURCE/f'counterfactual_{gate}_cells.csv.gz')
        rows=[]
        for _,g in src.groupby(['model_id','block_id']):
            first=g.iloc[0].to_dict()
            for v,s,o in itertools.product([0.,1.],np.linspace(.25,2.,9),np.linspace(.25,2.,9)):
                rows.append({**first,'vegetation':v,'S_source':s,'D_source':o})
        de=pd.DataFrame(rows)
        # Remove saved outputs; evaluate returns these anew.
        de=de.drop(columns=[c for c in de if c.startswith('audit_') or c in ['F_B','S_B','D_B','F_fraction','S_fraction','D_fraction','F_B_sd','minimum_F_survival','minimum_S_survival']])
        path=OUT/f'dense9_{gate}_cells.csv.gz'
        if path.exists():
            su=pd.read_csv(path)
            np.testing.assert_array_equal(su[['model_id','block_id','vegetation','S_source','D_source']],de[['model_id','block_id','vegetation','S_source','D_source']])
        else:
            su=evaluate(de,years=80,window=20,dt=.25,size_gate=gate,**{k:de['batch_'+k].to_numpy() for k in OPT if k!='size_gate'})
            su.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
        for (mid,bid),g in su.groupby(['model_id','block_id']):
            g=g.sort_values(['vegetation','S_source','D_source'])
            for bg in ['uniform','target_group']:
                r=weighted_core(g.D_source.to_numpy(),g.S_source.to_numpy(),g.vegetation.to_numpy(),g.F_B.to_numpy(),empirical_weights(d,bg,9),'rank','rank')
                records.append(dict(model_id=mid,block_id=bid,background=bg,simultaneous_signs=bool(r['OS']<0 and r['OV']<0 and r['SV']>0),**r))
        print('Dense grid complete',gate,len(su),flush=True)
    result=pd.DataFrame(records)
    result.to_csv(OUT/'dense9_coefficients.csv',index=False)
    old=pd.read_csv(OUT/'fixed_scale_interventions.csv')
    result=result.merge(old[old.check=='local'][['model_id','block_id','background','intervention']],on=['model_id','block_id','background'],validate='one_to_one')
    macro=pd.read_csv(ROOT/'research/results/scale_comparison_20261029/macro_common_estimators.csv')
    macro=macro[(macro.vegetation=='binary')&(macro.x_transform=='rank')&(macro.y_transform=='rank')&(macro.adjustment=='space')&(macro['mode']=='pooled')]
    result['all_three_intervals']=True
    for bg in ['uniform','target_group']:
        for term in ['OS','OV','SV']:
            q=macro[(macro.background==bg)&(macro.term==term)].iloc[0]
            result.loc[result.background==bg,'all_three_intervals'] &= result.loc[result.background==bg,term].between(q.low,q.high)
    result.to_csv(OUT/'dense9_labelled_comparison.csv',index=False)
    paths=[OUT/f'dense9_{gate}_cells.csv.gz' for gate in [None,.5]]
    (OUT/'dense9_receipt.json').write_text(json.dumps(dict(contexts=54,cells=8748,levels=9,years=80,window=20,dt=.25,
        purpose='Equal refinement of all fixed local interventions; no winner selection',
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')


if __name__=='__main__':main()
