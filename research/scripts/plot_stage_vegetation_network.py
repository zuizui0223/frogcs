"""Fixed illustrations from the complete synthetic grid, not fitted predictions."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--results',type=Path,required=True);a=ap.parse_args()
    d=pd.read_csv(a.results/'all_scenarios.csv.gz')
    m=pd.read_csv(a.results/'vegetation_modification.csv')
    nr=pd.read_csv(a.results/'no_reverse.csv.gz').set_index('scenario_id')
    # Prespecified illustration: strong attacks, cues, S-first/D-late; no sign-based selection.
    choose="refuge_order=='S' and s_arrival==0 and d_arrival==35 and attack_scale==1.5 and cue==3"
    z=d.query(choose+' and roles==15')
    fig,axes=plt.subplots(2,2,figsize=(12,9),layout='constrained')
    colors={'FS':'#c17c24','FD':'#3b82b5','FSD':'#7960a9'}
    for v,ax in zip([0,1],axes[0]):
        for c in colors:
            q=z[(z.vegetation==v)&(z.community==c)].sort_values('f_arrival')
            ax.plot(q.f_arrival-10,q.F_completed,'o-',label=c,color=colors[c])
        ax.set(title=f'{"A" if v==0 else "B"}  Frog completion; vegetation={v}',
               xlabel='Frog arrival delay (model days)',ylabel='Surviving fraction of initial frog cohort',ylim=(0,1))
        ax.legend(title='Groups present',frameon=False)
        ax.grid(alpha=.2)
    ax=axes[1,0]
    q=m.query(choose).pivot(index='roles',columns='f_arrival',values='vegetation_change_D_effect_with_S')
    lim=max(float(np.abs(q.to_numpy()).max()),.01)
    im=ax.imshow(q.to_numpy(),aspect='auto',cmap='RdBu',vmin=-lim,vmax=lim)
    labels=[]
    for r in q.index:
        labels.append('None' if r==0 else '+'.join(s for bit,s in [(1,'F refuge'),(2,'D support'),(4,'S refuge'),(8,'Emergence')] if r&bit))
    ax.set_yticks(range(len(q)),labels,fontsize=7)
    ax.set_xticks(range(len(q.columns)),[int(x-10) for x in q.columns])
    ax.set(title='C  Vegetation changes the effect of adding D',xlabel='Frog arrival delay (model days)')
    fig.colorbar(im,ax=ax,label='Change in frog survival contrast (V=1 minus V=0)',shrink=.9)
    ax=axes[1,1]
    for v,color in [(0,'#666666'),(1,'#228b66')]:
        q=z[(z.vegetation==v)&(z.community=='FSD')].sort_values('f_arrival')
        ax.plot(q.f_arrival-10,q.D_completed,'o-',color=color,label=f'V={v}, reverse edge on')
        ax.plot(q.f_arrival-10,nr.loc[q.scenario_id,'D_completed'].to_numpy(),'s--',color=color,label=f'V={v}, reverse edge off')
    ax.set(title='D  Stage reversal constrains odonate completion',xlabel='Frog arrival delay (model days)',
           ylabel='Surviving fraction reaching adult D',ylim=(0,1))
    ax.legend(fontsize=8,frameon=False);ax.grid(alpha=.2)
    fig.suptitle('Synthetic stage-dependent constraints: vegetation pathways and third-party effects',fontsize=14)
    fig.savefig(a.results/'stage_vegetation_network.png',dpi=180)
    fig.savefig(a.results/'stage_vegetation_network.pdf')
    plt.close(fig)


if __name__=='__main__':main()
