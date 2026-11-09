from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]/'results/frog_arrival_20261109'
d=pd.read_csv(p/'summary.csv')
fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1.2,1]})
ax=axes[0]
for name,color,style,label in [('EL','#084c61','-','Early / long'),('LL','#bb4d00','-','Late / long'),('ES','#479d9c','--','Early / short'),('LS','#ca8b49','--','Late / short')]:
    x=d.query("metric=='mean_log_F' and contrast=='net' and s_offset==0 and d_offset==0 and stage==@name")
    ax.plot(x.f_offset,x['mean'],style,color=color,marker='o',ms=4,label=label)
ax.axhline(0,color='#777',lw=.7);ax.set(xlabel='Delay in tadpole arrival (days)',ylabel='Change in mean log frog cohort',title='A   Predator calendars held fixed')
ax.legend(title='Salamander arrival / duration',fontsize=8,frameon=False)
ax=axes[1]
for i,(component,col,label) in enumerate([('refuge','#23836d','Shelter only'),('support','#c36a37','Odonate support only'),('net','#282b32','Both functions')]):
    a=d.query("metric=='mean_log_F' and f_offset==78 and stage=='EL' and contrast==@component").set_index(['s_offset','d_offset']).loc[[(0,0),(78,0),(0,78),(78,78)]]
    ax.bar(np.arange(4)+(i-1)*.22,a['mean'],width=.21,color=col,label=label)
ax.axhline(0,color='#777',lw=.7);ax.set_xticks(range(4),['Neither','Salamander','Odonate','Both']);ax.set(xlabel='Predator calendar also delayed by 78 days',title='B   Late tadpoles, early / long salamander regime')
ax.legend(frameon=False,fontsize=8);fig.tight_layout();fig.savefig(p/'arrival_comparison.png',dpi=180)
