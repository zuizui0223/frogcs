"""Source-table figures for the current working manuscript; no new fitting."""
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator,FormatStrFormatter
from nee_context_robustness import ROOT

OUT=ROOT/'research/manuscript/working_20261029/figures'
RES=ROOT/'research/results'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
SOURCES=[]


def read(path,**kwargs):
    p=RES/path;SOURCES.append(p);return pd.read_csv(p,**kwargs)


def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight')
    svg=OUT/(name+'.svg')
    fig.savefig(svg,bbox_inches='tight');plt.close(fig)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    a=read('nee_crossfit_20261029/coefficients.csv')
    fig,axes=plt.subplots(2,3,figsize=(11,6),layout='constrained')
    names=['Linear adjustment','Spatial CF: trees20','Spatial CF: trees60'];kinds=['full_linear','trees_20','trees_60']
    for row,bg in enumerate(['uniform','target_group']):
        for col,t in enumerate(['OS','OV','SV']):
            ax=axes[row,col]
            for i,(kind,color) in enumerate(zip(kinds,['#555555','#0072B2','#D55E00'])):
                q=a[(a.background==bg)&(a.nuisance==kind)&(a['mode']=='pooled')&(a.term==t)].iloc[0]
                ax.errorbar(q.beta,2-i,xerr=[[q.beta-q.low],[q.high-q.beta]],fmt='o',color=color,capsize=3)
            ax.axvline(0,color='.7',lw=1);ax.set_yticks([2,1,0],names if col==0 else ['']*3);ax.set_ylim(-.6,2.6)
            ax.set_title(bg.replace('_',' ')+' | '+t);ax.set_xlabel('Rank coefficient (95% interval)')
            ax.xaxis.set_major_locator(MaxNLocator(4));ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    fig.suptitle('1 | Shared-environment sensitivity; 4,248 listening sites')
    save(fig,'fig1_environment')
    a=read('mechanism_observation_20261029/calling_component_coefficients.csv')
    fig,axes=plt.subplots(2,2,figsize=(10,6),layout='constrained')
    outcomes=['strong_rate','any_call_rate','strong_given_call'];labels=['Strong-call frequency','Any-call frequency','Strong given a call']
    for row,mode in enumerate(['pooled','within']):
        for col,t in enumerate(['OS','OV']):
            ax=axes[row,col]
            for i,outcome in enumerate(outcomes):
                q=a[(a.background=='uniform')&(a['mode']==mode)&(a.term==t)&(a.outcome==outcome)].iloc[0]
                ax.errorbar(q.beta,2-i,xerr=[[q.beta-q.low],[q.high-q.beta]],fmt='o',color=['#555555','#0072B2','#D55E00'][i],capsize=3)
            ax.axvline(0,color='.7',lw=1);ax.set_yticks([2,1,0],labels if col==0 else ['']*3);ax.set_ylim(-.6,2.6);ax.set_title(mode+' | '+t);ax.set_xlabel('Rank coefficient (95% spatial interval)')
            ax.xaxis.set_major_locator(MaxNLocator(4));ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    fig.suptitle('2 | Observed calling components; same 4,182 sites, uniform background')
    save(fig,'fig2_calling_components')
    a=read('handling_factorial_20261029/dense21_rank_coefficients.csv',dtype={'arm':str})
    h=read('handling_factorial_20261029/dense21_physical_contrasts.csv',dtype={'arm':str})
    m=read('scale_comparison_20261029/macro_common_estimators.csv')
    m=m[(m.background=='uniform')&(m.vegetation=='binary')&(m.x_transform=='rank')&(m.y_transform=='rank')&(m.adjustment=='space')&(m['mode']=='pooled')].set_index('term')
    arms=['0000','1000','0100','1100','1111'];labels=['None','F saturation','D time','Both F paths','Full shared']
    fig,axes=plt.subplots(2,2,figsize=(11,7.5),layout='constrained')
    for ax,t in zip(axes.flat,['OS','OV','SV']):
        vals=[a[(a.background=='uniform')&(a.arm==arm)][t].iloc[0] for arm in arms]+[m.loc[t,'beta']]
        ax.bar(np.arange(6),vals,color=['#999999','#0072B2','#D55E00','#009E73','#CC79A7','#333333'])
        ax.errorbar(5,vals[-1],yerr=[[vals[-1]-m.loc[t,'low']],[m.loc[t,'high']-vals[-1]]],fmt='none',color='black',capsize=4)
        ax.axhline(0,color='.6',lw=1);ax.set_xticks(range(6),labels+['Macro'],rotation=25,ha='right');ax.set_title(t+' | rank coefficient');ax.set_ylabel('Standardized rank coefficient')
    ax=axes[1,1]
    for shift,v,color in [(-.18,0.,'#56B4E9'),(.18,1.,'#E69F00')]:
        vals=[h[(h.arm==arm)&(h.path=='H_total')&(h.contrast=='OS')&(h['at']==v)].value.iloc[0] for arm in arms]
        ax.bar(np.arange(5)+shift,vals,.36,label='Low V' if v==0 else 'High V',color=color)
    ax.axhline(0,color='.6',lw=1);ax.set_xticks(range(5),labels,rotation=25,ha='right');ax.set_title('OS | physical hazard contrast');ax.set_ylabel('Cumulative hazard difference of differences');ax.legend(frameon=False)
    fig.suptitle('3 | Saturation and cross-prey handling: rank patterns versus physical hazards')
    save(fig,'fig3_handling')
    a=read('literature_extension_20261029/paired_size_dynamics.csv')
    a=a[(a.background=='uniform')&(a.family=='shared_both')&(~a.risk)]
    ctx=['D_first_S_overtakes','S_first_D_overtakes']
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for shift,col,color,label in [(-.18,'frozen_OS','#999999','Initial hierarchy fixed'),(.18,'OS','#0072B2','Size hierarchy changes')]:
        vals=[a[a.context==c][col].iloc[0] for c in ctx];ax.bar(np.arange(2)+shift,vals,.36,color=color,label=label)
    ax.axhline(0,color='.6',lw=1);ax.set_xticks([0,1],['Dragonfly first; salamander overtakes','Salamander first; dragonfly overtakes']);ax.set_ylabel('Modeled OS rank coefficient');ax.legend(frameon=False);ax.set_title('4 | The order of size reversal changes the third-guild association')
    save(fig,'fig4_stage_order')
    (OUT/'sources.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},indent=2)+'\n')


if __name__=='__main__':main()
