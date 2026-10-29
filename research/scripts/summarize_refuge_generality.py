"""Summarize every fixed condition; physical signs are not macro rank fits."""
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/results/refuge_generality_20261029'
TOL=1e-9

def main():
 receipt=json.loads((OUT/'simulation_receipt.json').read_text())
 assert receipt['primary_cells']==6480 and receipt['secondary_cells']==1440
 checks={}
 for label in ['primary','scale']:
  keys=['context','family','role','K','refuge_strength','arm','DS_edge','path','contrast','at']
  a=pd.read_csv(OUT/(label+'_dt025_contrasts.csv'),dtype={'arm':str})
  b=pd.read_csv(OUT/(label+'_dt0125_contrasts.csv'),dtype={'arm':str})
  z=a.merge(b,on=keys,suffixes=('_a','_b'),validate='one_to_one')
  assert len(z)==len(a)==len(b) and np.isfinite(z[['value_a','value_b']]).all().all()
  z['absolute_difference']=abs(z.value_a-z.value_b)
  z['sign_stable']=np.sign(z.value_a.where(abs(z.value_a)>TOL,0))==np.sign(z.value_b.where(abs(z.value_b)>TOL,0))
  z.to_csv(OUT/(label+'_timestep_comparison.csv'),index=False)
  h=z[(z.path=='H_total')&~((z.contrast=='OV')&(z['at']==0))].copy()
  h['direction025']=np.where(h.contrast=='SV',-h.value_a,h.value_a)>TOL
  h['direction0125']=np.where(h.contrast=='SV',-h.value_b,h.value_b)>TOL
  config=keys[:7]
  joint=h.groupby(config).agg(n_contrasts=('direction025','size'),all_directions025=('direction025','all'),all_directions0125=('direction0125','all')).reset_index()
  assert (joint.n_contrasts==6).all()
  joint['both_timesteps']=joint.all_directions025 & joint.all_directions0125
  joint.to_csv(OUT/(label+'_joint_physical_directions.csv'),index=False)
  totals=joint.groupby(['role','family','DS_edge']).agg(success=('both_timesteps','sum'),conditions=('both_timesteps','size')).reset_index()
  totals.to_csv(OUT/(label+'_direction_counts.csv'),index=False)
  checks[label]=dict(contrasts=len(z),sign_changes=int((~z.sign_stable).sum()),max_absolute_difference=float(z.absolute_difference.max()),hazard_sign_changes=int((~h.sign_stable).sum()),joint_pass025=int(joint.all_directions025.sum()),joint_pass0125=int(joint.all_directions0125.sum()),joint_both=int(joint.both_timesteps.sum()),conditions=len(joint))
 # Exact old-reference replay for the matching settings, not just signs.
 for tag in ['dt025','dt0125']:
  old=pd.read_csv(ROOT/'research/results/nee_boundaries_20261029'/f'{tag}_annual.csv.gz',dtype={'arm':str}).rename(columns={'vegetation':'V'})
  old.arm=old.arm.str.zfill(4)
  new=pd.read_csv(OUT/f'primary_{tag}_original_cells.csv.gz',dtype={'arm':str})
  new=new[(new.family=='mixed')&(new.role=='F_from_S')&(new.DS_edge==1)&(new.S_source>0)]
  key=['context','arm','V','S_source','D_source']
  j=new.merge(old,on=key,suffixes=('_new','_old'),validate='one_to_one')
  assert len(j)==16
  fields=['F_B','S_B','D_B','audit_H_SF','audit_H_DF','F_killed_by_S','F_killed_by_D','S_killed_by_D']
  delta=max(float(abs(j[k+'_new']-j[k+'_old']).max()) for k in fields)
  assert delta<1e-10,delta
  checks[tag+'_baseline_replay_max_error']=delta
 # Descriptive source audit only: extracted plotted points are not all 126 trials.
 ext=OUT/'external_hossie2010';d=pd.read_csv(ext/'hossie2010_compiled.csv')
 assert len(d)==91 and (d.Time==24).all() and ((d.NE>=0)&(d.NE<=d.N0)).all()
 d['loss_fraction']=d.NE/d.N0
 d.groupby(['ID','N0']).loss_fraction.agg(['size','min','max']).reset_index().to_csv(OUT/'external_loss_point_ranges.csv',index=False)
 checks['external_compiled_points']=91
 checks['external_original_trials']=126
 checks['external_refit_performed']=False
 (OUT/'generality_validation.json').write_text(json.dumps(checks,indent=2)+'\n')
 files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='generality_manifest.json')
 (OUT/'generality_manifest.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
 print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
