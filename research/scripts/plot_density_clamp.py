from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'research/results/density_clamp_20261029'
F=ROOT/'research/manuscript/working_20261029/figures'

def main():
 a=pd.read_csv(P/'bridge_dt025_contrasts.csv',dtype={'arm':str})
 a=a[(a.context=='original')&(a.arm=='1000')&(a.path=='H_total')&(a.contrast=='OS')&(a['at']==1)].set_index(['initial_policy','clamp'])
 order=[('inherited_F',False),('inherited_F',True),('common_F',False),('common_F',True)]
 vals=[a.loc[x,'value'] for x in order]
 fig,axes=plt.subplots(1,2,figsize=(12,5.8))
 axes[0].bar(range(4),vals,color=['#2166ac','#67a9cf','#b2182b','#ef8a62']);axes[0].axhline(0,color='gray')
 axes[0].set(xticks=range(4),xticklabels=['Inherited F\nDeclines','Inherited F\nMaintained','Common F\nDeclines','Common F\nMaintained'],ylabel='Caudate × dragonfly contrast in total frog hazard',title='A. Annual-start F differences matter\nReference stage, FF handling, high vegetation')
 axes[0].set_ylim(-.0033,.0039)
 for i,y in enumerate(vals):axes[0].annotate(f'{y:+.5f}',(i,y),xytext=(0,5 if y>0 else -14),textcoords='offset points',ha='center',fontsize=9)
 b=pd.read_csv(P/'dt025_direct_mediator_predictions.csv',dtype={'arm':str});b=b[(b.context=='original')&(b.family=='mixed')&(b.arm=='1000')&(b.F0==3)&(b.S0==2)&(b.D0==2)]
 colors=['#2166ac','#b2182b'];roles=['F_from_S','F_and_S_refuge'];paths=['audit_H_SF','audit_H_DS'];x=np.arange(2)
 for i,role in enumerate(roles):
  v=[b[(b.role==role)&(b.path==path)].ratio.iloc[0] for path in paths]
  axes[1].bar(x+(i-.5)*.3,v,width=.3,color=colors[i],label=['Protect F','Protect F and S'][i])
 axes[1].axhline(1,color='gray',ls='--');axes[1].set(xticks=x,xticklabels=['S eats F','D eats S'],ylim=(0,1.15),ylabel='High / low vegetation hazard',title='B. Measure the salamander pathway\nAll three densities maintained');axes[1].legend(loc='lower right')
 fig.text(.5,.02,'F = frog, S = salamander, D = dragonfly. Synthetic interventions; not acoustic rank fits.\nA: all 20 actual yearly starts replayed; S/D starts retained; no annual re-equilibration. B: predictions from assigned refuge functions.',ha='center',fontsize=9)
 fig.tight_layout(rect=[0,.1,1,1]);fig.savefig(F/'figS3_density_clamp.png',dpi=180);fig.savefig(F/'figS3_density_clamp.svg')
 svg=F/'figS3_density_clamp.svg';svg.write_text('\n'.join(x.rstrip() for x in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
 files=[P/'bridge_dt025_contrasts.csv',P/'dt025_direct_mediator_predictions.csv',Path(__file__)]
 (F/'density_clamp_sources.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')

if __name__=='__main__':main()
