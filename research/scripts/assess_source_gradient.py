"""Joint signs and dose-range sensitivity, with a paper-ready diagnostic plot."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_source_gradient import OUT,KEYS


def assess(summary):
    rows=[]
    for dl,dh in [(.25,2.),(.25,1.),(1.,2.)]:
        for metric in ['F_B','F_C']:
            key=KEYS+['S_source']
            a=summary[summary.D_source==dl].set_index(key)[metric].sort_index()
            b=summary[summary.D_source==dh].set_index(key)[metric].sort_index()
            slope=((b-a)/(dh-dl)).rename('slope').reset_index()
            q=slope[slope.S_source==.25].merge(slope[slope.S_source==2.],on=KEYS,suffixes=('_lowS','_highS'))
            q['change']=q.slope_highS-q.slope_lowS
            q['joint_negative']=(q.change < -1e-6)&(q.slope_highS < -1e-6)
            q['negative_modifier']=q.change < -1e-6
            q['both_negative']=(q.slope_lowS < -1e-6)&q.joint_negative
            q['metric']=metric;q['D_low']=dl;q['D_high']=dh
            rows.append(q)
    return pd.concat(rows,ignore_index=True)


def main():
    allrows=[]
    for p in sorted(OUT.glob('*_summary.csv')):
        q=assess(pd.read_csv(p));q['run']=p.name.removesuffix('_summary.csv');allrows.append(q)
    q=pd.concat(allrows,ignore_index=True)
    q.to_csv(OUT/'joint_signs_all_ranges.csv',index=False)
    counts=q.groupby(['run','variant','metric','D_low','D_high']).agg(
        n=('change','size'),negative_modifier=('negative_modifier','sum'),
        joint_negative=('joint_negative','sum'),both_negative=('both_negative','sum')).reset_index()
    counts.to_csv(OUT/'joint_sign_counts.csv',index=False)
    su=pd.read_csv(OUT/'primary_summary.csv')
    fig,axes=plt.subplots(2,2,figsize=(11.5,9),layout='constrained');axes=axes.ravel()
    example=su[(su.roles==15)&(su.vegetation==1)&(su.refuge_order=='D')&(su.f_arrival==30)&(su.variant=='full')]
    for s,d in example.groupby('S_source'):
        d=d.sort_values('D_source');axes[0].plot(d.D_source,d.F_B,'o-',label=f'S source = {s:g}')
    axes[0].set(xlabel='External D source (normalized)',ylabel='Mean F breeding index (last 20 years)',
                title='A  Positive benefit becomes smaller')
    axes[0].legend(frameon=False);axes[0].set_ylim(bottom=0)
    main=q[(q.run=='primary')&(q.variant=='full')&(q.metric=='F_B')&(q.D_low==.25)&(q.D_high==2.)]
    for v,d in main.groupby('vegetation'):
        axes[1].scatter(d.slope_lowS,d.slope_highS,s=40,alpha=.65,label=f'Vegetation = {v:g}')
    bounds=np.r_[main.slope_lowS,main.slope_highS];lo=bounds.min()-.03;hi=bounds.max()+.03
    axes[1].plot([lo,hi],[lo,hi],'--',color='grey',linewidth=1)
    axes[1].axhline(0,color='grey',linewidth=.8);axes[1].axvline(0,color='grey',linewidth=.8)
    axes[1].set(xlim=(lo,hi),ylim=(lo,hi),xlabel='D-source slope at low S source',
                ylabel='D-source slope at high S source',title='B  Whole range (D 0.25 to 2): no joint match')
    axes[1].legend(frameon=False,loc='upper left')
    example=su[(su.roles==15)&(su.vegetation==1)&(su.refuge_order=='S')&(su.f_arrival==50)&(su.variant=='full')]
    for s,d in example.groupby('S_source'):
        d=d.sort_values('D_source');axes[2].plot(d.D_source,d.F_B,'o-',label=f'S source = {s:g}')
    axes[2].axvspan(1,2,color='grey',alpha=.1)
    axes[2].set(xlabel='External D source (normalized)',ylabel='Mean F breeding index (last 20 years)',
                title='C  Exploratory candidate in upper range (shaded)')
    axes[2].set_ylim(bottom=0);axes[2].legend(frameon=False)
    ab=q[(q.run=='primary')&(q.metric=='F_B')&(q.D_low==1)&(q.roles==15)&(q.vegetation==1)&(q.refuge_order=='S')&(q.f_arrival==50)]
    order=['full','no_reverse','no_cue','no_intraguild','independent']
    ab=ab.set_index('variant').loc[order]
    labels=['Full','No reverse predation','No cue suppression','No intraguild predation','Neither cue nor intraguild']
    axes[3].barh(labels,ab.change,color=['#0072B2' if x<0 else '#D55E00' for x in ab.change])
    axes[3].axvline(0,color='grey',linewidth=1);axes[3].invert_yaxis()
    axes[3].set(xlabel='High-S minus low-S D slope (D 1 to 2)',title='D  Reverse predation is not required here')
    fig.suptitle('Synthetic annual feedback: whole-range test and exploratory local mechanism',fontsize=13)
    fig.savefig(OUT/'source_gradient_diagnostic.png',dpi=180)
    fig.savefig(OUT/'source_gradient_diagnostic.pdf')
    print(counts[(counts.variant=='full')&(counts.metric=='F_B')].to_string(index=False))


if __name__=='__main__':main()
