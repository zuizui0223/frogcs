"""Inventory regional GBIF candidates and independent GloBI evidence before SDM selection."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from reliable_source_json import ReliableJSON
from broad_species_sdm import ORDERS, QUERY, ROOT, write_csv, write_json

REGION = dict(country='US',hasCoordinate='true',hasGeospatialIssue='false',occurrenceStatus='PRESENT',
              decimalLatitude='24,50',decimalLongitude='-101,-65')
BASIS = ['HUMAN_OBSERVATION','OBSERVATION','PRESERVED_SPECIMEN','MACHINE_OBSERVATION',
         'MATERIAL_SAMPLE','MATERIAL_CITATION','OCCURRENCE']


def query(client, params):
    return client.get('https://api.gbif.org/v1/occurrence/search?'+urlencode(params,doseq=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cache',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    client=ReliableJSON(args.cache/'json',interval=.5)
    facets, receipts, names={},[],{}
    for guild,key in ORDERS.items():
        scopes={'regional_all_dates':{**REGION,'basisOfRecord':BASIS},
                'regional_historical_strict':{**REGION,'year':'1980,2015','coordinateUncertaintyInMeters':'0,1000','basisOfRecord':BASIS},
                'broad_historical_strict':{**QUERY,'basisOfRecord':BASIS}}
        for scope,params in scopes.items():
            obj=query(client,{**params,'taxonKey':key,'limit':0,'facet':'speciesKey','facetLimit':1000})
            fc=obj['facets'][0]['counts']
            if len(fc)>=1000:
                raise ValueError('Facet limit reached; paginate instead of truncating')
            facets[(guild,scope)]={x['name']:x['count'] for x in fc}
            receipt=dict(guild=guild,scope=scope,query=params,count=obj['count'],species=len(fc))
            receipts.append(receipt)
            write_json(args.out/f'facet_{guild}_{scope}.json',obj)
        # Bulk accepted taxonomy, without restricting names to the original 205 species.
        offset=0
        while True:
            params=dict(highertaxonKey=key,rank='SPECIES',status='ACCEPTED',limit=1000,offset=offset)
            obj=client.get('https://api.gbif.org/v1/species/search?'+urlencode(params))
            for r in obj['results']:
                names[str(r['key'])]=dict(species=r.get('canonicalName') or r.get('scientificName'),
                                         family=r.get('family',''),genus=r.get('genus',''),taxonomic_status=r.get('taxonomicStatus',''))
            if obj['endOfRecords']:
                break
            offset+=len(obj['results'])
            if offset>30000:
                raise ValueError('Unexpected taxonomy pagination')
        print('inventoried',guild,len(facets[(guild,'regional_all_dates')]),flush=True)
    source=ROOT/'research/results/three_guild_globi_live'
    crosswalk=json.loads((source/'taxon_crosswalk.json').read_text())['names']
    bridge={r['globi_name']:str(r['accepted_key']) for r in crosswalk if r['status']=='EXACT_ACCEPTED_SPECIES_BRIDGE'}
    evidence=defaultdict(list)
    with open(source/'direction_normalized_species_edges.csv',encoding='utf8',newline='') as f:
        edges=list(csv.DictReader(f))
    regional_keys=set().union(*(set(facets[(g,'regional_all_dates')]) for g in ORDERS))
    regional_edges=[]
    for edge in edges:
        a,b=bridge.get(edge['source_taxon_name']),bridge.get(edge['target_taxon_name'])
        if not a or not b:
            continue
        for k in (a,b):
            evidence[k].append(edge)
        if a in regional_keys and b in regional_keys:
            regional_edges.append({**edge,'source_species_key':a,'target_species_key':b})
    connected={k for e in regional_edges for k in (e['source_species_key'],e['target_species_key'])}
    rows=[]
    for guild in ORDERS:
        for key,count in sorted(facets[(guild,'regional_all_dates')].items()):
            if key not in names:
                obj=client.get('https://api.gbif.org/v1/species/'+key)
                names[key]=dict(species=obj.get('canonicalName') or obj.get('scientificName'),family=obj.get('family',''),
                                genus=obj.get('genus',''),taxonomic_status=obj.get('taxonomicStatus',''))
            history=facets[(guild,'regional_historical_strict')].get(key,0)
            broad=facets[(guild,'broad_historical_strict')].get(key,0)
            types=Counter(e['interaction_type'] for e in evidence[key])
            rows.append(dict(guild=guild,species_key=key,**names[key],regional_all_dates_count=count,
                             regional_historical_strict_count=history,broad_historical_strict_count=broad,
                             globi_any_mapped_evidence=bool(evidence[key]),globi_edge_both_species_regional=key in connected,
                             globi_relation_types='|'.join(sorted(types)),
                             trophic_evidence=any(x in types for x in ('eats','preysOn','eatenBy','preyedUponBy')),
                             model_status='candidate_needs_spatial_support' if broad>=100 else 'historical_strict_records_insufficient',
                             selected_for_interaction_sdm=key in connected and broad>=100))
    write_csv(args.out/'gbif_regional_species_inventory.csv',rows)
    write_csv(args.out/'globi_regionally_supported_edges.csv',regional_edges)
    # GloBI taxa lacking regional occurrence evidence remain unconfirmed, never absent.
    missing=[]
    for r in crosswalk:
        key=str(r.get('accepted_key',''))
        if key and key not in regional_keys:
            missing.append(dict(globi_name=r['globi_name'],accepted_species_key=key,
                                status='no_regional_record_in_this_query_not_absence',taxonomy_status=r['status']))
    write_csv(args.out/'globi_region_unconfirmed.csv',missing)
    summary=dict(date_utc=datetime.now(timezone.utc).isoformat(),regional_scope=REGION,facets=receipts,
                 regional_species_by_guild=dict(Counter(r['guild'] for r in rows)),
                 globi_regionally_connected_species_by_guild=dict(Counter(r['guild'] for r in rows if r['globi_edge_both_species_regional'])),
                 eligible_interaction_sdm_species_by_guild=dict(Counter(r['guild'] for r in rows if r['selected_for_interaction_sdm'])),
                 regionally_supported_globi_relations=len(regional_edges),
                 independent_checklist_reconciliation='pending; occurrence inventory is not an exhaustive regional checklist',
                 source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                (source/'taxon_crosswalk.json',source/'direction_normalized_species_edges.csv')})
    write_json(args.out/'gbif_globi_inventory_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('facets','source_sha256')},indent=2))


if __name__=='__main__':
    main()
