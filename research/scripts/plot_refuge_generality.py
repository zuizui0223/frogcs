"""Supplementary fixed-grid and observational comparison; no fitted causal arrows."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'research/results/refuge_generality_20261029'
F=ROOT/'research/manuscript/working_20261029/figures'

def main():
 a=pd.read_csv(P/'primary_joint_physical_directions.csv');a=a[a.DS_edge==1]
 roles=['no_direct_function','F_from_S','F_from_D','F_both','S_from_D','D_from_S','D_attack_support','D_emergence_support','F_and_S_refuge']
 labels=['No direct pathway','Protect F from S','Protect F from D','Protect F from both','Protect S from D','Protect D from S','Support D attack','Support D emergence','Protect F and S']
 families=['constant','II','III','mixed','steep']
 z=a.groupby(['role','family']).both_timesteps.sum().unstack().reindex(index=roles,columns=families)
 fig,ax=plt.subplots(figsize=(8.5,5.5));ax.imshow(z,vmin=0,vmax=6,cmap='Blues',aspect='auto')
 for i in range(len(roles)):
  for j in range(5):ax.text(j,i,f'{int(z.iloc[i,j])}/6',ha='center',va='center',color='black')
 ax.set(xticks=range(5),xticklabels=['Constant','Type II','Type III','II / III','II / steep III'],yticks=range(9),yticklabels=labels,title='Joint hazard directions: 18 / 270 configurations\nEach cell: 3 stage contexts × 2 S handling forms')
 fig.text(.5,.015,'OS > 0 and OV > 0; SV < 0 at both endpoints, stable at both timesteps.\nF=frog, S=salamander, D=dragonfly. D→S retained. All passes: reference stage. Not a calling-rank fit.',ha='center',fontsize=9)
 fig.tight_layout(rect=[0,.08,1,1])
 for ext in ['png','svg']:fig.savefig(F/f'figS1_refuge_generality.{ext}',dpi=180)
 plt.close(fig)
 a=pd.read_csv(P/'macro_conditional_OV.csv');a=a[a.contrast=='high_minus_low']
 fig,ax=plt.subplots(figsize=(8.5,4.5));y=np.arange(len(a))
 ax.errorbar(a.beta,y,xerr=np.vstack([a.beta-a.low,a.high-a.beta]),fmt='o',capsize=4,color='#2166ac')
 ax.axvline(0,color='gray',ls='--');ax.set(yticks=y,yticklabels=[f'{x.background}: {x.adjustment}' for x in a.itertuples()],xlabel='OV at high S − OV at low S (rank-regression contrast)',title='Does the vegetation × dragonfly association differ by salamander context?')
 fig.text(.5,.02,'Same 4,248 sites; S quartiles; 999 spatial resamples.\nTrees intervals condition on fixed nuisance fits. Low suitability is not salamander absence.',ha='center',fontsize=9)
 fig.tight_layout(rect=[0,.12,1,1])
 for ext in ['png','svg']:fig.savefig(F/f'figS2_refuge_prediction.{ext}',dpi=180)
 plt.close(fig)

if __name__=='__main__':
 main()
 for path in F.glob('figS*_refuge_*.svg'):
  path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
