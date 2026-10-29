"""Known prey-depletion null: remove S-D predation, retain shared prey and nonlinearity."""
import json
import numpy as np
import pandas as pd
from nee_context_robustness import ROOT
from handling_annual_summary_20261029 import summarize_years
OUT=ROOT/'research/results/nee_boundaries_20261029'

def main():
 reference=pd.read_csv(OUT/'dt025_annual.csv.gz',dtype={'arm':str});de=reference[['context','sa','da','dduration','sg','dg','arm','vegetation','S_source','D_source']]
 rows=[]
 for dt,tag,edge in [(dt,tag,e) for dt,tag in [(.25,'dt025'),(.125,'dt0125')] for e in ['neither','no_DS','no_SD']]:
  params=[dict(community='FSD',roles=15,refuge_order='D',vegetation=r.vegetation,f_arrival=20.,s_arrival=float(r.sa),d_arrival=float(r.da),attack_scale=.5,cue=0.,reverse=False,rho=.75) for r in de.itertuples()]
  controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,cue_SD=0.,edge_SD=float(edge=='no_DS'),edge_DS=float(edge=='no_SD'))
  opts=dict(pathway_controls=controls,stage_durations=np.column_stack([np.full(len(de),45.),np.full(len(de),80.),de.dduration]),functional_response='litter',s_handling_matrix=np.array([[int(i) for i in a] for a in de.arm]),s_growth=de.sg.to_numpy(),d_growth=de.dg.to_numpy())
  source=np.column_stack([np.ones(len(de)),de.S_source,de.D_source]);suffix='independent_predator' if edge=='neither' else edge;path=OUT/(tag+'_'+suffix+'_cells.csv.gz')
  if path.exists():
   a=pd.read_csv(path,dtype={'arm':str});pd.testing.assert_frame_equal(a[de.columns],de,check_dtype=False)
  else:
   su=summarize_years(params,years=80,window=20,dt=dt,source_cohorts=source,seasonal_options=opts,conversion=4.);a=pd.concat([de,su],axis=1);a.to_csv(path,index=False,compression={'method':'gzip','mtime':0})
  for (ctx,arm,v),g in a.groupby(['context','arm','vegetation']):
   g=g.set_index(['S_source','D_source']);q={}
   for field in ['audit_H_DF','audit_H_SF']:
    z=g[field];q[field]=z.loc[(2.,2.)]-z.loc[(2.,.25)]-z.loc[(.25,2.)]+z.loc[(.25,.25)]
   rows.append(dict(dt=dt,edge=edge,context=ctx,arm=arm,V=v,D_path=q['audit_H_DF'],S_path=q['audit_H_SF'],total=sum(q.values())))
  print('edge control done',dt,edge,flush=True)
 pd.DataFrame(rows).to_csv(OUT/'independent_predator_OS.csv',index=False)
 (OUT/'independent_predator_receipt.json').write_text(json.dumps(dict(intervention='both, DS-only, SD-only removals; cue=0, reverse=false; retain F response, S FF saturation and annual demography',meaning='baseline shared-prey depletion null, not absence of all indirect interaction'),indent=2)+'\n')
if __name__=='__main__':main()
