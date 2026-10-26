"""Bounded, paginated GloBI guild edges; stage is optional, no local interaction inference."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GUILDS = ('Anura','Caudata','Odonata')
FIELDS = ['source_taxon_name','source_taxon_path','source_specimen_life_stage','interaction_type',
          'target_taxon_name','target_taxon_path','target_specimen_life_stage','study_citation']
BINOMIAL = re.compile(r'^[A-Z][a-z]+ [a-z][a-z-]+$')
INVERSE = {'eatenBy':'eats','preyedUponBy':'preysOn','hasHost':'hostOf'}
SYMMETRIC = {'interactsWith','coOccursWith','ecologicallyRelatedTo'}


def directed_identity(source,target,relation):
    if relation in INVERSE:
        return target,source,INVERSE[relation]
    if relation in SYMMETRIC:
        source,target=sorted([source,target])
    return source,target,relation


def qualify(row, source, target):
    if source not in {x.strip() for x in str(row['source_taxon_path'] or '').split('|')}:
        return 'source_guild_unverified'
    if target not in {x.strip() for x in str(row['target_taxon_path'] or '').split('|')}:
        return 'target_guild_unverified'
    if not all(BINOMIAL.fullmatch(str(row[k] or '')) for k in ['source_taxon_name','target_taxon_name']):
        return 'not_two_binomial_form_names'
    if not row['interaction_type']:
        return 'missing_interaction_type'
    return 'eligible_named_edge'


def page(url, out, label):
    rec = {'url':url,'queried_at_utc':datetime.now(timezone.utc).isoformat()}
    try:
        req = Request(url,headers={'User-Agent':'FrogcsGlobalMacro/0.1 (source-cited noncommercial scientific audit)',
                                   'Accept':'application/json'})
        with urlopen(req,timeout=40) as f: raw=f.read()
        d=json.loads(raw)
        rec.update(status='SUCCESS',response_sha256=hashlib.sha256(raw).hexdigest(),response=d)
        if d.get('columns')!=FIELDS or not isinstance(d.get('data'),list) or any(
                not isinstance(r,list) or len(r)!=len(FIELDS) for r in d.get('data',[])):
            rec.update(status='SCHEMA_FAILED')
    except Exception as exc:
        rec.update(status='REQUEST_FAILED',error=type(exc).__name__+': '+str(exc))
    (out/(label+'.json')).write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
    time.sleep(1)
    return rec


def write_csv(path,rows,fields):
    with path.open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--page-size',type=int,default=1000);p.add_argument('--max-pages',type=int,default=10)
    a=p.parse_args()
    if not 1<=a.page_size<=1000 or not 1<=a.max_pages<=10:raise ValueError('Explicit modest retrieval caps exceeded')
    a.out.mkdir(parents=True,exist_ok=True); rawdir=a.out/'raw';rawdir.mkdir(exist_ok=True)
    allrows=[];receipts=[];fingerprints=set()
    for source,target in itertools.permutations(GUILDS,2):
        label=source+'_to_'+target
        info=dict(source_guild=source,target_guild=target,pages=[],returned_rows=0,exhausted=False,
                  capped=False,failed=False,repeated_page=False)
        for i in range(a.max_pages):
            q=dict(sourceTaxon=source,targetTaxon=target,includeObservations='true',fields=','.join(FIELDS),
                   limit=a.page_size,offset=i*a.page_size)
            name=label+'_page'+str(i)
            rec=page('https://api.globalbioticinteractions.org/interaction?'+urlencode(q),rawdir,name)
            info['pages'].append(dict(receipt='raw/'+name+'.json',status=rec['status'],offset=i*a.page_size))
            if rec['status']!='SUCCESS':
                info['failed']=True;break
            values=rec['response']['data'];info['returned_rows']+=len(values)
            pagekey=(label,hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest())
            if values and pagekey in fingerprints:
                info['repeated_page']=True;info['failed']=True;break
            fingerprints.add(pagekey)
            for row in values:
                r=dict(zip(FIELDS,row));r.update(query_source_guild=source,query_target_guild=target,
                                                qualification=qualify(r,source,target),receipt='raw/'+name+'.json')
                allrows.append(r)
            print(name,len(values),flush=True)
            if len(values)<a.page_size:
                info['exhausted']=True;break
        if not info['exhausted'] and not info['failed']:info['capped']=True
        receipts.append(info)
    edgegroups=defaultdict(list)
    for r in allrows:
        if r['qualification']=='eligible_named_edge':
            edgegroups[(r['source_taxon_name'],r['target_taxon_name'],r['interaction_type'])].append(r)
    edges=[]
    for (source,target,relation),group in sorted(edgegroups.items()):
        cites=sorted({r['study_citation'] for r in group if r['study_citation']})
        stages=sorted({(r['source_specimen_life_stage'] or '',r['target_specimen_life_stage'] or '') for r in group})
        unique_fields={tuple(r[k] for k in FIELDS) for r in group}
        edges.append(dict(source_taxon_name=source,target_taxon_name=target,interaction_type=relation,
                          source_guild=group[0]['query_source_guild'],target_guild=group[0]['query_target_guild'],
                          retrieved_rows=len(group),distinct_returned_field_rows=len(unique_fields),
                          distinct_citation_strings=len(cites),citation_strings_json=json.dumps(cites),
                          optional_stage_pairs_json=json.dumps(stages),
                          receipts_json=json.dumps(sorted({r['receipt'] for r in group})),
                          naming_status='BINOMIAL_FORM_GUILD_VERIFIED_NOT_ACCEPTED_SPECIES_KEY_MATCHED'))
    write_csv(a.out/'normalized_source_rows.csv',allrows,FIELDS+['query_source_guild','query_target_guild','qualification','receipt'])
    edgefields=['source_taxon_name','target_taxon_name','interaction_type','source_guild','target_guild','retrieved_rows',
                'distinct_returned_field_rows','distinct_citation_strings','citation_strings_json','optional_stage_pairs_json',
                'receipts_json','naming_status']
    write_csv(a.out/'species_edges.csv',edges,edgefields)
    direction_groups=defaultdict(list)
    for r in edges:
        direction_groups[directed_identity(r['source_taxon_name'],r['target_taxon_name'],r['interaction_type'])].append(r)
    direction_edges=[]
    for (source,target,relation),group in sorted(direction_groups.items()):
        citations=sorted({c for r in group for c in json.loads(r['citation_strings_json'])})
        direction_edges.append(dict(source_taxon_name=source,target_taxon_name=target,interaction_type=relation,
                                    query_orientation_edges=len(group),distinct_citation_strings=len(citations),
                                    citation_strings_json=json.dumps(citations),
                                    original_relations_json=json.dumps(sorted({r['interaction_type'] for r in group})),
                                    original_edge_keys_json=json.dumps([[r['source_taxon_name'],r['target_taxon_name'],r['interaction_type']] for r in group])))
    write_csv(a.out/'direction_normalized_species_edges.csv',direction_edges,
              ['source_taxon_name','target_taxon_name','interaction_type','query_orientation_edges',
               'distinct_citation_strings','citation_strings_json','original_relations_json','original_edge_keys_json'])
    summary=dict(date_utc=datetime.now(timezone.utc).isoformat(),query_directions=receipts,
                 page_size=a.page_size,max_pages_per_direction=a.max_pages,
                 status='COMPLETE_BOUNDED_LIVE_QUERY' if all(r['exhausted'] for r in receipts) else 'CAPPED_OR_FAILED_EXPLICITLY',
                 returned_rows=len(allrows),qualification_counts=dict(Counter(r['qualification'] for r in allrows)),
                 species_name_relation_edges=len(edges),source_taxon_names=len({r['source_taxon_name'] for r in edges}),
                 direction_normalized_species_edges=len(direction_edges),
                 inverse_and_symmetric_query_edges_not_independent=True,
                 target_taxon_names=len({r['target_taxon_name'] for r in edges}),
                 interaction_type_counts_rows=dict(Counter(r['interaction_type'] for r in allrows)),
                 life_stage_required=False,interaction_type_filter=None,source_citation_required=False,
                 source_citation_missing_rows=sum(not r['study_citation'] for r in allrows),
                 no_gbif_or_naamp_site_time_join_yet=True,missing_edge_is_not_absence=True,
                 multiple_rows_not_independent_observations=True,live_api_not_stable_release=True,
                 exhausted_means_pagination_end_not_global_biological_completeness=True,
                 api_documentation='https://github.com/globalbioticinteractions/globalbioticinteractions/wiki/API')
    (a.out/'observed_results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    print(summary['status'],summary['returned_rows'],summary['species_name_relation_edges'],flush=True)
    if any(r['failed'] for r in receipts):raise SystemExit(4)


if __name__=='__main__':main()
