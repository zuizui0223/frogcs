"""Reconcile independent regional checklists before selecting GloBI-linked species."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode

from reliable_source_json import ReliableJSON
from broad_species_sdm import write_csv, write_json, ROOT


def read(path):
    with open(path,encoding='utf8',newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cache',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    client=ReliableJSON(a.cache/'json',interval=.5)
    known={}
    for p in (a.cache/'json').glob('*.json'):
        obj=json.loads(p.read_text())
        for r in obj.get('results',[]):
            if r.get('rank')=='SPECIES' and r.get('taxonomicStatus')=='ACCEPTED' and r.get('canonicalName'):
                known[r['canonicalName']]=r
    check=read(a.out/'armi_eastern_state_union_candidates.csv')
    check += [r for r in read(a.out/'checklist_candidates.csv') if r['source'].startswith('DSA_')]
    mapped=[]
    for row in check:
        name=row['scientific_name']
        expected='Odonata' if row['source'].startswith('DSA_') else row['order']
        if name in known and known[name].get('order')==expected:
            r=known[name]
            key=r['key']; status='EXACT_ACCEPTED_NAME'
        elif name.endswith(' sp.'):
            key=''; status='PROVISIONAL_NAME'
        else:
            r=client.get('https://api.gbif.org/v1/species/match?'+urlencode(dict(name=name,strict='true',kingdom='Animalia')))
            if r.get('matchType')=='EXACT' and r.get('rank')=='SPECIES' and r.get('order')==expected:
                key=r.get('acceptedUsageKey') or r['usageKey']; status='EXACT_ACCEPTED_OR_SYNONYM'
            else:
                key=''; status='UNRESOLVED'
        mapped.append(dict(source=row['source'],scientific_name=name,accepted_species_key=str(key),
                           accepted_name=r.get('canonicalName','') if key else '',guild=expected,status=status,
                           range_text=row['range_text'],scope=row['scope']))
    write_csv(a.out/'checklist_taxon_crosswalk.csv',mapped)
    supported={r['accepted_species_key'] for r in mapped if r['accepted_species_key']}
    original=read(a.out/'gbif_regional_species_inventory.csv')
    for r in original:
        r['independent_checklist_support']=r['species_key'] in supported
        r['distribution_review']=('checklist_and_regional_record' if r['species_key'] in supported
                                  else 'GBIF_only_requires_distribution_review')
        # Zero old precise records is not absence: it is kept in the review table.
    confirmed={r['species_key'] for r in original if r['independent_checklist_support']}
    edges=read(a.out/'globi_regionally_supported_edges.csv')
    verified=[e for e in edges if e['source_species_key'] in confirmed and e['target_species_key'] in confirmed]
    connected={k for e in verified for k in (e['source_species_key'],e['target_species_key'])}
    # A named focal species remains useful even when its counterpart was only
    # identified to genus/order. Do not discard it through a two-binomial filter.
    aliases={r['species']:r['species_key'] for r in original}
    aliases.update({r['scientific_name']:r['accepted_species_key'] for r in mapped if r['accepted_species_key']})
    globi=ROOT/'research/results/three_guild_globi_live'
    bridge=json.loads((globi/'taxon_crosswalk.json').read_text())['names']
    aliases.update({r['globi_name']:str(r['accepted_key']) for r in bridge if r['status']=='EXACT_ACCEPTED_SPECIES_BRIDGE'})
    higher=[]
    for edge in read(globi/'normalized_source_rows.csv'):
        if edge['qualification']!='not_two_binomial_form_names':
            continue
        for role in ('source','target'):
            name=edge[role+'_taxon_name'].strip()
            key=aliases.get(name)
            if re.fullmatch(r'[A-Z][a-z]+ [a-z][a-z-]+',name) and key in confirmed:
                higher.append(dict(focal_species_name=name,focal_species_key=key,focal_role=role,
                                   counterpart_name=edge[('target' if role=='source' else 'source')+'_taxon_name'],
                                   source_taxon_name=edge['source_taxon_name'],target_taxon_name=edge['target_taxon_name'],
                                   interaction_type=edge['interaction_type'],study_citation=edge['study_citation'],
                                   source_stage=edge['source_specimen_life_stage'],target_stage=edge['target_specimen_life_stage'],
                                   receipt=edge['receipt'],evidence_tier='named_focal_species_counterpart_not_resolved_to_species'))
    higher_keys={r['focal_species_key'] for r in higher}
    write_csv(a.out/'higher_taxon_counterpart_evidence.csv',higher)
    for r in original:
        r['evidence_tier']=('regional_species_pair' if r['species_key'] in connected else
                            'named_species_higher_taxon_counterpart' if r['species_key'] in higher_keys else 'outside_interaction_pool')
        r['selected_for_interaction_sdm']=r['species_key'] in (connected|higher_keys) and int(r['broad_historical_strict_count'])>0
        r['selection_reason']=('regional_checklist_plus_globi_evidence' if r['selected_for_interaction_sdm'] else
                               'regional_distribution_review_pending' if r['species_key'] not in supported else
                               'outside_confirmed_interaction_model_pool')
    write_csv(a.out/'reviewed_species_inventory.csv',original)
    write_csv(a.out/'reviewed_interaction_model_pool.csv',[r for r in original if r['selected_for_interaction_sdm']])
    write_csv(a.out/'reviewed_globi_edges.csv',verified)
    regional_ids={r['species_key'] for r in original}
    write_csv(a.out/'checklist_not_in_regional_query.csv',[r for r in mapped if r['accepted_species_key'] not in regional_ids])
    summary=dict(independent_checklist_rows=len(mapped),checklist_mapping_status=dict(Counter(r['status'] for r in mapped)),
                 original_regional_candidate_rows=len(original),
                 candidates_without_independent_support=sum(not r['independent_checklist_support'] for r in original),
                 interaction_model_species_by_guild=dict(Counter(r['guild'] for r in original if r['selected_for_interaction_sdm'])),
                 interaction_model_evidence_tiers=dict(Counter(r['evidence_tier'] for r in original if r['selected_for_interaction_sdm'])),
                 verified_named_globi_relations=len(verified),
                 relation_types=dict(Counter(e['interaction_type'] for e in verified)),
                 limitations=['ARMI state union broader than focal box; DSA checklist covers Canada and continental US',
                              'Checklist support plus GBIF regional records is candidate evidence, not verified presence in a particular pond',
                              'Unmatched checklist names and GBIF-only candidates remain review items, not absences',
                              'GloBI evidence is literature/database-level, not an interaction observed at NAAMP sites'])
    write_json(a.out/'reviewed_pool_summary.json',summary)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
