import pandas as pd
from compare_vegetation_functions import OUT,run
from audit_response_scales import compare
j=pd.read_csv(OUT/'joint_success.csv');parts=[];selected=[]
for func,g in j[j.all_scales].groupby('function'):
 su=pd.read_csv(OUT/(func+'_summary.csv'))
 meta=su[su.timing.isin(g.timing)][['timing','s_arrival','d_arrival','S_duration','D_duration']].drop_duplicates().sort_values(['s_arrival','d_arrival','S_duration','D_duration'])
 name=meta.iloc[0].timing
 des=su[su.timing==name].copy()
 # Remove computed response columns before joining a new simulation.
 fields=['function','protect_F','protect_S','protect_D','emergence','timing','f_arrival','s_arrival','d_arrival','F_duration','S_duration','D_duration','vegetation','S_source','D_source','refuge_order','attack_scale','cue','reverse','roles','rho']
 parts.append(des[fields]);selected.append(dict(function=func,timing=name,selection='First numeric stage tuple among baseline passing configurations; exploratory not independent'))
pd.DataFrame(selected).to_csv(OUT/'numerical_selection.csv',index=False)
des=pd.concat(parts,ignore_index=True);rows=[]
for name,kw in [('half_step',{'dt':.125}),('horizon160',{'years':160})]:
 su,err=run(des,**kw);su.to_csv(OUT/('selected_'+name+'_summary.csv'),index=False)
 for func,g in su.groupby('function'):rows+=compare(g,dict(function=func,timing=g.timing.iloc[0],check=name))
 print('Selected numerical',name,len(parts),'functions',err,flush=True)
x=pd.DataFrame(rows);x.to_csv(OUT/'selected_numerical_checks.csv',index=False)
print(x[(x.D_low==.25)&x.metric.isin(['F_B','log_F_B','log_F_fraction','negative_H'])].groupby(['function','check']).all_three.all().to_string(),flush=True)
