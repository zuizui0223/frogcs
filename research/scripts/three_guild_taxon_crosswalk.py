"""Exact GBIF accepted-species identity for the observed GloBI guild endpoints."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CLASSES={'Anura':'Amphibia','Caudata':'Amphibia','Odonata':'Insecta'}


def validate_match(d,guild):
    if d.get('matchType')!='EXACT':raise ValueError('NONEXACT_'+str(d.get('matchType')))
    if d.get('rank')!='SPECIES':raise ValueError('NOT_SPECIES_'+str(d.get('rank')))
    if d.get('status') not in ('ACCEPTED','SYNONYM'):raise ValueError('UNSUPPORTED_STATUS_'+str(d.get('status')))
    if d.get('order')!=guild or d.get('class')!=CLASSES[guild]:raise ValueError('GUILD_OR_CLASS_MISMATCH')
    key=d.get('acceptedUsageKey') if d['status']=='SYNONYM' else d.get('usageKey')
    if not isinstance(key,int):raise ValueError('NO_ACCEPTED_KEY')
    return key


def validate_accepted(d,key,guild):
    if d.get('key')!=key or d.get('rank')!='SPECIES' or d.get('taxonomicStatus')!='ACCEPTED':
        raise ValueError('ACCEPTED_ENDPOINT_IDENTITY_MISMATCH')
    if d.get('order')!=guild or d.get('class')!=CLASSES[guild]:raise ValueError('ACCEPTED_ENDPOINT_GUILD_MISMATCH')
    if not d.get('canonicalName'):raise ValueError('NO_CANONICAL_ACCEPTED_NAME')
    return d['canonicalName']


def fetch(url,directory,label,cache_dirs=()):
    path=directory/(label+'.json')
    if path.exists():
        previous=json.loads(path.read_text(encoding='utf8'))
        if previous.get('status')=='SUCCESS' and previous.get('url')==url:
            return previous,True
    for cachedir in cache_dirs:
        candidate=Path(cachedir)/(label+'.json')
        if candidate.exists():
            previous=json.loads(candidate.read_text(encoding='utf8'))
            if previous.get('status')=='SUCCESS' and previous.get('url')==url:
                path.write_text(json.dumps(previous,indent=2)+'\n',encoding='utf8')
                return previous,True
    time.sleep(.4)
    rec={'url':url,'queried_at_utc':datetime.now(timezone.utc).isoformat()}
    try:
        req=Request(url,headers={'User-Agent':'frogcs-exact-guild-crosswalk/1.0','Accept':'application/json'})
        with urlopen(req,timeout=35) as f:raw=f.read()
        d=json.loads(raw)
        if not isinstance(d,dict):raise ValueError('Not a JSON object')
        rec.update(status='SUCCESS',response_sha256=hashlib.sha256(raw).hexdigest(),response=d)
    except Exception as exc:
        rec.update(status='REQUEST_FAILED',error=type(exc).__name__+': '+str(exc))
    path.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
    return rec,False


def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--edges',type=Path);g.add_argument('--naamp-surveys',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    dirname='taxonomy_naamp' if a.naamp_surveys else 'taxonomy'
    rawdir=a.out/dirname;rawdir.mkdir(exist_ok=True)
    names=defaultdict(set);skipped=Counter();source_counts=Counter()
    source=a.naamp_surveys or a.edges
    if a.naamp_surveys:
        with gzip.open(source,'rt',encoding='utf8',newline='') as f:
            for r in csv.DictReader(f):
                for name in set(r['source_taxa'].split('|')):
                    name=name.strip()
                    if not name:continue
                    source_counts[name]+=1
                    if re.fullmatch(r'[A-Z][a-z]+ [a-z][a-z-]+',name):names[name].add('Anura')
                    else:skipped[name]+=1
    else:
        with source.open(encoding='utf8',newline='') as f:
            for r in csv.DictReader(f):
                names[r['source_taxon_name']].add(r['source_guild'])
                names[r['target_taxon_name']].add(r['target_guild'])
    records=[];cache_hits=0;fetches=0
    for i,(name,guilds) in enumerate(sorted(names.items()),1):
        row={'source_name':name,'expected_guilds':sorted(guilds),'status':'UNRESOLVED'}
        if a.naamp_surveys:row['naamp_name']=name
        else:row.update(globi_name=name,globi_guilds=sorted(guilds))
        if len(guilds)!=1 or next(iter(guilds)) not in CLASSES:
            row['reason']='AMBIGUOUS_GUILD';records.append(row);continue
        guild=next(iter(guilds));row['expected_order']=guild
        q={'name':name,'verbose':'true','kingdom':'Animalia','class':CLASSES[guild],'order':guild}
        url='https://api.gbif.org/v1/species/match?'+urlencode(q)
        label='match_'+hashlib.sha256(name.encode()).hexdigest()[:16]
        rec,cache=fetch(url,rawdir,label,[a.out/'taxonomy']);cache_hits+=int(cache);fetches+=int(not cache)
        row['match_receipt']=dirname+'/'+label+'.json'
        if rec['status']!='SUCCESS':row.update(status='REQUEST_FAILED',reason=rec['error'])
        else:
            d=rec['response']
            row.update({k:d.get(k) for k in ['usageKey','acceptedUsageKey','canonicalName','confidence','matchType','rank','alternatives']})
            row['matched_taxonomic_status']=d.get('status')
            try:
                key=validate_match(d,guild)
                if d['status']=='ACCEPTED':canonical=d['canonicalName']
                else:
                    accepted_url='https://api.gbif.org/v1/species/'+str(key)
                    accepted_label='accepted_'+str(key)
                    acc,cache=fetch(accepted_url,rawdir,accepted_label,[a.out/'taxonomy']);cache_hits+=int(cache);fetches+=int(not cache)
                    row['accepted_receipt']=dirname+'/'+accepted_label+'.json'
                    if acc['status']!='SUCCESS':raise ValueError('ACCEPTED_ENDPOINT_REQUEST_FAILED: '+acc.get('error',''))
                    canonical=validate_accepted(acc['response'],key,guild)
                row.update(status='EXACT_ACCEPTED_SPECIES_BRIDGE',accepted_key=key,accepted_canonical_name=canonical)
            except (ValueError,KeyError) as exc:row.update(reason=str(exc))
        records.append(row)
        print(i,len(names),name,row['status'],row.get('reason',''),flush=True)
    summary=dict(date_utc=datetime.now(timezone.utc).isoformat(),source_file=str(source),
                 source_file_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),n_names=len(names),
                 source_kind='NAAMP_COMPLETED_SURVEY_SOURCE_TAXA' if a.naamp_surveys else 'GLOBI_SPECIES_EDGES',
                 skipped_non_binomial_labels=dict(skipped),source_survey_name_counts=dict(source_counts),
                 status_counts=dict(Counter(r['status'] for r in records)),
                 accepted_unique_keys=len({r['accepted_key'] for r in records if r['status']=='EXACT_ACCEPTED_SPECIES_BRIDGE'}),
                 names=records,cache_hits=cache_hits,http_requests=fetches,strict_exact_only=True,
                 rank_order_class_checked=True,fuzzy_or_higher_rank_forced=False,unresolved_is_not_species_absence=True,
                 no_local_occurrence_or_interaction_inference=True)
    filename='naamp_taxon_crosswalk.json' if a.naamp_surveys else 'taxon_crosswalk.json'
    (a.out/filename).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
    print(summary['status_counts'],flush=True)


if __name__=='__main__':main()
