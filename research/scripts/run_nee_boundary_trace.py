"""Exact D-path state attribution at fixed annual model states, not causal mediation."""
import itertools,json
import numpy as np
import pandas as pd
from nee_context_robustness import ROOT
from nee_boundaries import hazard,elasticities,shapley_state
from stage_boundary_trace_20261029 import simulate
from boundary_annual_trace_20261029 import summarize_years
from run_literature_extension import CONTEXTS
OUT=ROOT/'research/results/nee_boundaries_20261029'
ARMS=['0000','1000','0100','1100','1111']

def run(dt,tag):
 rows=[]
 for ctx,arm,v,s,d in itertools.product(CONTEXTS,ARMS,[0.,1.],[.25,2.],[.25,2.]):rows.append(dict(**ctx,arm=arm,vegetation=v,S_source=s,D_source=d))
 de=pd.DataFrame(rows);params=[dict(community='FSD',roles=15,refuge_order='D',vegetation=r.vegetation,f_arrival=20.,s_arrival=float(r.sa),d_arrival=float(r.da),attack_scale=.5,cue=0.,reverse=False,rho=.75) for r in de.itertuples()]
 controls=dict(cover_SF=1.,cover_DF=0.,cover_DS=0.,cover_SD=0.,support_DF=0.,support_DS=0.,emerge_survival=0.,emerge_exposure=0.,cue_SD=0.)
 opts=dict(pathway_controls=controls,stage_durations=np.column_stack([np.full(len(de),45.),np.full(len(de),80.),de.dduration]),functional_response='litter',s_handling_matrix=np.array([[int(i) for i in a] for a in de.arm]),s_growth=de.sg.to_numpy(),d_growth=de.dg.to_numpy())
 source=np.column_stack([np.ones(len(de)),de.S_source,de.D_source]);path=OUT/(tag+'_annual.csv.gz')
 statepath=OUT/(tag+'_annual_states.npy')
 if path.exists() and statepath.exists():
  annual=pd.read_csv(path,dtype={'arm':str});yearstates=np.load(statepath);pd.testing.assert_frame_equal(annual[de.columns],de,check_dtype=False);assert yearstates.shape==(20,len(de),3)
 else:
  history=[]
  a=summarize_years(params,years=80,window=20,dt=dt,source_cohorts=source,seasonal_options=opts,conversion=4.,state_observer=lambda year,state:history.append(state))
  annual=pd.concat([de,a],axis=1);annual.to_csv(path,index=False,compression={'method':'gzip','mtime':0});yearstates=np.array(history);np.save(statepath,yearstates)
 # Replay all twenty actual yearly states, never substitute their mean in nonlinear dynamics.
 n=len(de);years=len(yearstates);tr=[]
 tiled={k:(np.tile(val,(years,1)) if isinstance(val,np.ndarray) and val.ndim==2 else np.tile(val,years) if isinstance(val,np.ndarray) else val) for k,val in opts.items()}
 replay=simulate([{k:v for k,v in p.items() if k!='rho'} for p in params]*years,dt=dt,initial_cohorts=yearstates.reshape(-1,3),diagnostics=True,observer=lambda t,q:tr.append((t,q)),**tiled)
 np.testing.assert_allclose(replay[['audit_H_DF','audit_H_SF']].to_numpy().reshape(years,n,2).mean(axis=0),annual[['audit_H_DF','audit_H_SF']],atol=1e-10)
 # All these S-handling arms leave D handling at zero. Formula extension c>0 tested separately.
 out=[];local=[]
 for (ctx,arm,v,d),g in de.groupby(['context','arm','vegetation','D_source']):
  lo0=g[g.S_source==.25].index[0];hi0=g[g.S_source==2.].index[0];lo=lo0+np.arange(years)*n;hi=hi0+np.arange(years)*n;parts=np.zeros(3);exact=0.;sf=0.;weighted_negative=0.;weight=0.
  for t,q in tr:
   if not q['fw'][lo].any():continue
   l=np.column_stack([q['F'][lo],q['D'][lo],q['S'][lo]]);h=np.column_stack([q['F'][hi],q['D'][hi],q['S'][hi]])
   a=.025*.5*q['gdf'][lo];cc=0.
   np.testing.assert_allclose(a*hazard(*l.T,v,cc),q['hdf'][lo],atol=1e-12)
   np.testing.assert_allclose(a*hazard(*h.T,v,cc),q['hdf'][hi],atol=1e-12)
   parts+=dt*(a[:,None]*shapley_state(l,h,v,cc)).mean(axis=0);exact+=dt*(q['hdf'][hi]-q['hdf'][lo]).mean();sf+=dt*(q['hsf'][hi]-q['hsf'][lo]).mean()
   for idx,src in [(lo,.25),(hi,2.)]:
    ok=q['F'][idx]>0
    if ok.any():
     ef,_=elasticities(q['F'][idx][ok],q['S'][idx][ok],v,cc);w=dt*q['hdf'][idx][ok]/years;weighted_negative+=np.sum(w*(ef<0));weight+=w.sum()
     if tag=='dt025':local.append(dict(context=ctx,arm=arm,V=v,D_source=d,S_source=src,day=t,F=q['F'][idx].mean(),D=q['D'][idx].mean(),S=q['S'][idx].mean(),E_F=ef.mean(),D_hazard=q['hdf'][idx].mean()))
  np.testing.assert_allclose(parts.sum(),exact,atol=1e-11)
  out.append(dict(context=ctx,arm=arm,V=v,D_source=d,F_state=parts[0],D_state=parts[1],S_handling_state=parts[2],D_path=exact,S_path=sf,total=exact+sf,depletion_amplifying_hazard_share=weighted_negative/weight if weight else np.nan))
 out=pd.DataFrame(out);out.to_csv(OUT/(tag+'_S_effect_paths.csv'),index=False)
 contrasts=[]
 for (ctx,arm,v),g in out.groupby(['context','arm','V']):
  g=g.set_index('D_source');cols=['F_state','D_state','S_handling_state','D_path','S_path','total'];diff=g.loc[2.,cols]-g.loc[.25,cols]
  contrasts.append(dict(context=ctx,arm=arm,V=v,**{k:diff[k] for k in ['F_state','D_state','S_handling_state','D_path','S_path','total']}))
 pd.DataFrame(contrasts).to_csv(OUT/(tag+'_OS_paths.csv'),index=False)
 if local:pd.DataFrame(local).to_csv(OUT/'local_density_boundaries.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 print('trace done',tag,len(annual),flush=True)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 for dt,tag in [(.25,'dt025'),(.125,'dt0125')]:run(dt,tag)
 a=pd.read_csv(OUT/'dt025_OS_paths.csv',dtype={'arm':str});b=pd.read_csv(OUT/'dt0125_OS_paths.csv',dtype={'arm':str})
 pd.testing.assert_frame_equal(a[['context','arm','V']],b[['context','arm','V']])
 delta=a[['D_path','S_path','total']]-b[['D_path','S_path','total']]
 (OUT/'boundary_receipt.json').write_text(json.dumps(dict(max_half_step_difference=delta.abs().max().to_dict(),annual_state_replay_tolerance=1e-10,all_twenty_year_states_replayed=True,exact_path_identity=True,contribution_type='symmetric algebraic state attribution, not intervention mediation',D_handling_in_traced_arms=0,local_derivative_not_total_OS=True),indent=2)+'\n')
if __name__=='__main__':main()
