"""Accepted-key literature edges over records, never local observed interactions."""
import argparse,csv,gzip,hashlib,json,itertools
from collections import Counter,defaultdict
from pathlib import Path
from naamp_three_guild_occurrence import writecsv

def readcsv(p):
    opener=gzip.open if str(p).endswith('.gz') else open
    with opener(p,'rt',encoding='utf8') as f:return list(csv.DictReader(f))

def source_sets(records,members,radius=25,accuracy='strict'):
    sets=defaultdict(set)
    for m in members:
        r=records[m['id']]
        if r['quality']=='exclude' or (accuracy=='strict' and r['quality']!='strict') or float(m['distance_km'])>radius:continue
        sets[r['species_key']].add((m['center'],int(r['year']),int(r['month']) if r['month'] else None))
    return sets

def edge_overlap(a,b):
    return dict(both_species_reported=bool(a and b),shared_centers=len({x[0] for x in a}&{x[0] for x in b}),
                shared_center_years=len({x[:2] for x in a}&{x[:2] for x in b}),
                shared_center_year_months=len({x for x in a if x[2] is not None}&{x for x in b if x[2] is not None}))

def main():
    p=argparse.ArgumentParser();p.add_argument('--occurrence',type=Path,required=True);p.add_argument('--globi',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    records={r['id']:r for r in readcsv(a.occurrence/'occurrences.csv.gz')};members=readcsv(a.occurrence/'neighborhood_membership.csv.gz')
    queries=json.loads((a.occurrence/'queries.json').read_text(encoding='utf8'))
    complete={q['center'] for q in queries if all(z['status']=='COMPLETE' for z in queries if z['center']==q['center'])}
    members=[r for r in members if r['center'] in complete]
    cross=json.loads((a.globi/'taxon_crosswalk.json').read_text(encoding='utf8'))
    good={r['globi_name']:r for r in cross['names'] if r['status']=='EXACT_ACCEPTED_SPECIES_BRIDGE'}
    alias={name:str(r['accepted_key']) for name,r in good.items()}
    alias.update({r['accepted_canonical_name']:str(r['accepted_key']) for r in good.values()})
    naamp_cross=json.loads((a.globi/'naamp_taxon_crosswalk.json').read_text(encoding='utf8'))
    alias.update({r['naamp_name']:str(r['accepted_key']) for r in naamp_cross['names'] if r['status']=='EXACT_ACCEPTED_SPECIES_BRIDGE'})
    original=readcsv(a.globi/'direction_normalized_species_edges.csv');edges=[];unresolved=[]
    for r in original:
        x,y=r['source_taxon_name'],r['target_taxon_name']
        if x not in good or y not in good:unresolved.append(r);continue
        edges.append(dict(r,source_key=str(good[x]['accepted_key']),target_key=str(good[y]['accepted_key'])))
    variants=[]
    for radius,accuracy in itertools.product((5,25),('strict','strict_plus_unknown')):
        sets=source_sets(records,members,radius,accuracy);rows=[]
        for e in edges:rows.append(dict(e,**edge_overlap(sets[e['source_key']],sets[e['target_key']])))
        writecsv(a.out/f'literature_edge_occurrence_overlap_{radius}km_{accuracy}.csv',rows)
        variants.append(dict(radius_km=radius,accuracy=accuracy,eligible_resolved_edges=len(rows),both_species_anywhere=sum(r['both_species_reported'] for r in rows),
            any_shared_center=sum(r['shared_centers']>0 for r in rows),any_shared_center_year=sum(r['shared_center_years']>0 for r in rows),
            any_shared_center_year_month=sum(r['shared_center_year_months']>0 for r in rows),
            shared_month_edges_by_relation=dict(Counter(r['interaction_type'] for r in rows if r['shared_center_year_months']>0))))
    calls=readcsv(a.occurrence/'naamp_completed_site_surveys.csv.gz');supports=[];unmapped=Counter();mapped=Counter()
    for accuracy in ('strict','strict_plus_unknown'):
      sets=source_sets(records,members,25,accuracy)
      for r in calls:
        if r['site'] not in complete:continue
        native=set(filter(None,r['source_taxa'].split('|')));keys={alias[x] for x in native if x in alias}
        if accuracy=='strict':unmapped.update(native-set(alias));mapped.update(native&set(alias))
        cy=(r['site'],int(r['year']));cym=(*cy,int(r['month']))
        for e in edges:
            src,tgt=e['source_key'],e['target_key']
            other=tgt if src in keys else src if tgt in keys else None
            if other is None:continue
            year=any(x[:2]==cy for x in sets[other]);month=cym in sets[other]
            if not year:continue
            supports.append(dict(accuracy=accuracy,site=r['site'],run=r['run'],date=r['date'],strong=r['strong'],
                source=e['source_taxon_name'],target=e['target_taxon_name'],interaction=e['interaction_type'],
                counterpart_record_same_year=year,counterpart_record_same_month=month,citations=e['citation_strings_json']))
    writecsv(a.out/'naamp_call_literature_counterpart_record_support.csv',supports)
    paths=[a.occurrence/'occurrences.csv.gz',a.occurrence/'neighborhood_membership.csv.gz',a.globi/'taxon_crosswalk.json',a.globi/'naamp_taxon_crosswalk.json',a.globi/'direction_normalized_species_edges.csv']
    result=dict(source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
       literature_name_edges=len(original),accepted_key_edges=len(edges),unresolved_name_edges=len(unresolved),variants=variants,
       naamp_species_names_mapped=dict(mapped),naamp_species_names_unresolved=dict(unmapped),naamp_taxonomic_bridge_scope=naamp_cross['status_counts'],
       naamp_record_support_sensitivity=[dict(accuracy=acc,source_edge_support_rows=sum(r['accuracy']==acc for r in supports),
         visits_same_year=len({r['run']+'|'+r['site'] for r in supports if r['accuracy']==acc}),
         visits_same_month=len({r['run']+'|'+r['site'] for r in supports if r['accuracy']==acc and r['counterpart_record_same_month']})) for acc in ('strict','strict_plus_unknown')],
       no_local_interaction_observed=True,life_stage_not_required=True,
       limits=['literature relations are not local realized edges','ecologicallyRelatedTo is not proof of competition',
               'unknown/missing edge not absence','NAAMP complex labels not forced to species; species bridge is source-eligible cohort, not every raw NAAMP label',
               'spatial and temporal reporting, not simultaneous pond contact','no observation-effort correction'])
    (a.out/'observed_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('accepted_key_edges','variants','naamp_record_support_sensitivity')},indent=2))

if __name__=='__main__':main()
