"""Illustrations selected for explaining signs; full grid remains available."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);a=p.parse_args()
    tr=pd.read_csv(a.results/'trajectories.csv.gz');pc=pd.read_csv(a.results/'reversal_contrasts.csv')
    fig,axes=plt.subplots(2,2,figsize=(12.5,9.2),layout='constrained')
    colors={'FD':'#167c9c','FSD':'#b55b28'}
    q=tr[(tr.roles==15)&(tr.vegetation==1)&(tr.rho==.5)&(tr.f_arrival==50)]
    for ax,order,title in zip(axes[0],['D','S'],['A  Refuge stronger against dragonflies','B  Refuge stronger against caudates']):
        for community in ('FD','FSD'):
            for reverse in (False,True):
                z=q[(q.community==community)&(q.refuge_order==order)&(q.reverse==reverse)].sort_values('year')
                ax.plot(z.year,z.F_B,color=colors[community],ls='-' if reverse else '--',
                        label=f'{community}; reversal {"on" if reverse else "off"}')
        ax.set(title=title,xlabel='Model year',ylabel='Frog breeding-pool index',ylim=(0,2))
        ax.grid(alpha=.15);ax.legend(frameon=False,fontsize=8)
    ax=axes[1,0]
    h=pc[(pc.community=='FSD')&(pc.vegetation==1)&(pc.rho==.5)&(pc.f_arrival==50)]
    pivot=h.pivot(index='roles',columns='refuge_order',values='delta_F_B').reindex(columns=['D','S'])
    lim=max(abs(pivot.to_numpy()).max(),.01)
    im=ax.imshow(pivot.to_numpy(),aspect='auto',cmap='RdBu',vmin=-lim,vmax=lim)
    ax.set_yticks(range(6),['No plant effect','Frog refuge','D encounter support','Caudate refuge','Emergence support','All four roles'])
    ax.set_xticks([0,1],['Stronger against D','Stronger against S'])
    for i in range(6):
        for j in range(2):ax.text(j,i,f'{pivot.iloc[i,j]:+.3f}',ha='center',va='center',fontsize=9,
                                 color='white' if abs(pivot.iloc[i,j])>lim*.65 else 'black')
    ax.set(title='C  Vegetation roles in the three-guild system (FSD)',xlabel='Frog refuge ordering (when enabled)')
    fig.colorbar(im,ax=ax,label='Change in frog index: reversal on minus off',shrink=.85)
    ax=axes[1,1]
    q=pc[(pc.roles==15)&(pc.vegetation==1)&(pc.refuge_order=='D')&(pc.f_arrival==50)]
    for community in ('FD','FSD'):
        z=q[q.community==community].sort_values('rho')
        ax.plot(z.rho,z.delta_F_B,'o-',color=colors[community],label=community)
    ax.axhline(0,color='#666666',lw=.8)
    ax.set(title='D  Feedback depends on recruitment context',xlabel='Local recruitment weight (rho)',
           ylabel='Change in frog index: reversal on minus off',xticks=[0,.5,1])
    ax.legend(frameon=False);ax.grid(alpha=.15)
    fig.suptitle('Synthetic annual feedback: a third party can reverse the benefit of stage reversal',fontsize=14)
    fig.supxlabel('F=frog, D=odonate, S=caudate. Illustrative arrival day 50; C–D: means over years 60–79.\nPanel D at rho=1: both frog trajectories approach zero. Synthetic results, not field predictions.',fontsize=9)
    fig.savefig(a.results/'multiyear_stage_network.png',dpi=180)
    fig.savefig(a.results/'multiyear_stage_network.pdf');plt.close(fig)

if __name__=='__main__':main()
