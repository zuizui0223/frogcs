"""Demographic sensitivity on preselected candidates; no refitting."""
import numpy as np
import pandas as pd
from run_evidence_constrained import OUT,TIMINGS,simulate_design,contrasts,KEYS,grid


def main():
    base=pd.read_csv(OUT/'summary.csv');selected=pd.read_csv(OUT/'sensitivity_selection.csv')
    outputs=[]
    for r in selected[selected.profile.isin(['refuge_only','litter_response'])].to_dict('records'):
        mask=np.ones(len(base),bool)
        for k in KEYS:mask&=base[k]==r[k]
        des=base.loc[mask,list(grid(r['profile'],TIMINGS[r['timing']][1]).columns)].reset_index(drop=True)
        for label,kw in [('rho25',{}),('rho75',{}),('conversion2',{'conversion':(2,2,2)}),
                         ('conversion8',{'conversion':(8,8,8)}),('delay111',{'delays':(1,1,1)}),
                         ('delay332',{'delays':(3,3,2)})]:
            dd=des.copy()
            if label.startswith('rho'):dd['rho']=.25 if label=='rho25' else .75
            su=simulate_design(dd,TIMINGS[r['timing']][1],**kw)
            cc=contrasts(su);cc['check']=label;outputs.append(cc)
            su.to_csv(OUT/(r['profile']+'_'+label+'_summary.csv'),index=False)
            print('Demography',r['profile'],label,flush=True)
    pd.concat(outputs,ignore_index=True).to_csv(OUT/'demographic_contrasts.csv',index=False)


if __name__=='__main__':main()
