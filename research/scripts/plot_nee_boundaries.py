"""Publication-style source-backed sensitivity and mechanism figures."""
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nee_context_robustness import ROOT
from nee_boundaries import hill_elasticity
R=ROOT/'research/results/nee_boundaries_20261029';OUT=ROOT/'research/manuscript/working_20261029/figures'
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def save(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight');p=OUT/(name+'.svg');fig.savefig(p,bbox_inches='tight');plt.close(fig);p.write_text('\n'.join(x.rstrip() for x in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
def main():
 a=pd.read_csv(R/'joint_refit_coefficients.csv');a=a[a.replicate>0];assert a.groupby(['background','term']).size().eq(49).all()
 fig,axes=plt.subplots(1,3,figsize=(12,4.2),layout='constrained')
 for ax,t in zip(axes,['OS','OV','SV']):
  for j,(bg,col) in enumerate([('uniform','#0072B2'),('target_group','#D55E00')]):
   q=a[(a.background==bg)&(a.term==t)].sort_values('replicate');jitter=np.linspace(-.14,.14,len(q));ax.scatter(j+jitter,q.beta,s=18,alpha=.65,color=col);ax.hlines(q.beta.median(),j-.22,j+.22,color='black',lw=2)
  ax.axhline(0,color='.6',lw=1);ax.set_xticks([0,1],['Uniform','Target group']);ax.set_title(t);ax.set_ylabel('Rank coefficient');ax.set_xlim(-.5,1.5)
 fig.suptitle('5 | Joint SDM and site-block refitting: 49 stability draws, not confidence intervals')
 save(fig,'fig5_joint_uncertainty')
 a=pd.read_csv(R/'dt025_OS_paths.csv',dtype={'arm':str});null=pd.read_csv(R/'network_null_all_physical_contrasts.csv',dtype={'arm':str})
 fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained');ax=axes[0];f=np.linspace(.1,4,300)
 for c,label,col in [(0,'No alternative-prey handling','#0072B2'),(1,'Alternative-prey load = 1','#D55E00'),(3,'Alternative-prey load = 3','#009E73')]:ax.plot(f,hill_elasticity(f,1,2,c),label=label,color=col)
 ax.axhline(0,color='.6',lw=1);ax.set_xlabel('Frog density / assumed response scale');ax.set_ylabel('Elasticity of individual D-path hazard');ax.set_title('A | High-vegetation local boundary');ax.legend(fontsize=8,frameon=False);ax.text(.02,.02,'Below zero: frog depletion increases hazard',transform=ax.transAxes,fontsize=8)
 ax=axes[1];q=a[(a.context=='original')&(a.V==1)].set_index('arm');arms=['0000','1000','0100','1111'];x=np.arange(4)
 for offset,field,label,color in [(-.22,'F_state','F-density contribution','#0072B2'),(0,'D_state','D-density contribution','#009E73'),(.22,'S_path','S-path compensation','#D55E00')]:ax.bar(x+offset,q.loc[arms,field],width=.22,label=label,color=color)
 ax.plot(x,q.loc[arms,'total'],'ko',label='Net OS');ax.axhline(0,color='.6',lw=1);ax.set_xticks(x,['None','F saturation','D time','Full shared'],rotation=25,ha='right');ax.set_ylabel('Cumulative-hazard OS contrast');ax.set_title('B | Amplification minus compensation');ax.legend(fontsize=8,frameon=False)
 ax=axes[2];q=null[(null.tag=='dt025')&(null.context=='original')&(null.arm=='1000')&(null.path=='H_total')&(null.contrast=='OV')];models=['independent_predators','no_DS','no_SD','network']
 for offset,at,col in [(-.18,.25,'#56B4E9'),(.18,2.,'#E69F00')]:
  vals=q[q['at']==at].set_index('model').loc[models,'value'];ax.bar(np.arange(4)+offset,vals,.36,color=col,label='Low S supply' if at==.25 else 'High S supply')
 ax.axhline(0,color='.6',lw=1);ax.set_xticks(range(4),['Neither edge','No D → S','No S → D','Both edges'],rotation=25,ha='right');ax.set_ylabel('Cumulative-hazard OV contrast');ax.set_title('C | Which predator edge changes V effect?');ax.legend(fontsize=8,frameon=False)
 fig.suptitle('6 | Synthetic model diagnostics; local boundary is not a field mechanism test')
 save(fig,'fig6_amplification_boundary')
 paths=[R/p for p in ['joint_refit_coefficients.csv','dt025_OS_paths.csv','network_null_all_physical_contrasts.csv']]
 (OUT/'boundary_sources.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
if __name__=='__main__':main()
