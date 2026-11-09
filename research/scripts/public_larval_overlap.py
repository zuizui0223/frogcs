from pathlib import Path
import argparse, json, re, time
from concurrent.futures import ThreadPoolExecutor
import requests
API='https://api.gbif.org/v1/occurrence/search'
FROGS={2427618:'Acris gryllus',2428182:'Pseudacris crucifer'}
def request(params):
    for i in range(5):
        try:
            response=requests.get(API,params=params,timeout=60);response.raise_for_status();return response.json()
        except requests.RequestException:
            if i==4:raise
            time.sleep(2**i)
def download(path,params):
    if not path.exists():
        records=[]
        while True:
            result=request({**params,'limit':300,'offset':len(records)})
            records.extend(result['results'])
            if result['endOfRecords']:break
            if not result['results']:raise ValueError('Incomplete page')
        path.write_text(json.dumps(records),encoding='utf8')
    return json.loads(path.read_text(encoding='utf8'))
def day(z):
    s=z.get('eventDate','')
    return s[:10] if re.fullmatch(r'\d{4}-\d\d-\d\d(?:T[^/]*)?',s) else ''
def positive(z):
    return z.get('occurrenceStatus')=='PRESENT' and z.get('individualCount')!=0 and day(z)
def collect(cache):
    cache.mkdir(exist_ok=True,parents=True)
    frogs={}
    for key in FROGS:
        for stage in ['Larva','Tadpole']:
            for z in download(cache/f'{key}-{stage}.json',dict(country='US',taxonKey=key,lifeStage=stage)):
                if positive(z):frogs[z['key']]=z
    dates=sorted(set(map(day,frogs.values())))
    jobs=[(k,stage,dates[i:i+6]) for k,stage in [(953,'Larva'),(789,'Larva'),(789,'Nymph')] for i in range(0,len(dates),6)]
    def one(job):
        key,stage,days=job
        file=cache/f'{key}-{stage}-{"_".join(days)}.json'
        rows=download(file,dict(country='US',taxonKey=key,lifeStage=stage,eventDate=days,occurrenceStatus='PRESENT'))
        return [z for z in rows if positive(z) and day(z) in days]
    pred={}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for rows in pool.map(one,jobs):
            pred.update({z['key']:z for z in rows})
    return list(frogs.values()),list(pred.values())
def audit(cache,out):
    import csv, hashlib, math
    from collections import Counter, defaultdict
    import pandas as pd
    out.mkdir(exist_ok=True,parents=True)
    frogs,predators=collect(cache)
    records={z['key']:z for z in frogs+predators}
    known_waterbodies=[
        (1143472616,1143472646),(1143472554,1143472595),
        (1319726388,1322837534),(1322513737,1318420671),
        (786078102,786078105),(1320659349,1318152294),
        (785442869,785442157),(785442870,785442158),
        (1039485994,1039465827),(1919926674,1919926670),
        (1919926674,1919926679),(1919926674,1919926664),
        (3321344260,3321343722),(2269099198,2269099392),
        (786082140,786082135),(786082140,786082138),
        (786082186,786082164),(786082186,786082167),
        (786082004,786081998)]
    registry={}
    rows=[]
    for fk,pk in known_waterbodies:
        x,y=records[fk],records[pk]
        assert x['datasetKey']==y['datasetKey'] and x['stateProvince']==y['stateProvince']
        assert x['locality']==y['locality'] and x['locality'] and day(x)==day(y)
        assert positive(x) and positive(y) and y['order']=='Caudata'
        assert x['basisOfRecord']==y['basisOfRecord']=='PRESERVED_SPECIMEN'
        assert y['lifeStage'].lower()=='larva' and x['lifeStage'].lower() in ('larva','tadpole')
        site=(x['datasetKey'],x['stateProvince'],x['locality'])
        registry.setdefault(site,len(registry)+1)
        rows.append((x['species'],y['species'],day(x),registry[site],x['stateProvince'],fk,pk,x['datasetKey']))
    pd.DataFrame(rows,columns=['frog','caudate','date','waterbody_code','state','frog_gbif_id','caudate_gbif_id','dataset_uuid']).to_csv(out/'reviewed_paired_vouchers.csv',index=False)
    # Broader spatial search is a source coverage diagnostic; no occupancy or negative ecological labels.
    jobs={(day(x),round(x['decimalLatitude'],4),round(x['decimalLongitude'],4)) for x in frogs if x['species']=='Acris gryllus' and 'decimalLatitude' in x and 'decimalLongitude' in x}
    def local(j):
        t,lat,lon=j
        return download(cache/f'dragon_unrestricted_{t}_{lat}_{lon}.json',dict(country='US',taxonKey=789,eventDate=t,decimalLatitude=f'{lat-.02},{lat+.02}',decimalLongitude=f'{lon-.025},{lon+.025}'))
    with ThreadPoolExecutor(max_workers=5) as pool:
        local_keys={z['key'] for rr in pool.map(local,sorted(jobs)) for z in rr}
    ponds=defaultdict(set)
    for x in frogs:
        if x.get('locality') and x.get('stateProvince'):
            ponds[(x['datasetKey'],x['stateProvince'],x['locality'].strip().lower(),day(x)[:4])].add(x['species'])
    summary=dict(frog_positive_dated=dict(Counter(z['species'] for z in frogs)),unique_frog_dates=len(set(map(day,frogs))),predator_positive_same_dates=dict(Counter(z['order'] for z in predators)),both_frogs_same_dataset_state_locality_year=sum(len(v)==2 for v in ponds.values()),A_odonate_all_stage_search_boxes=len(jobs),A_odonate_all_stage_hits=len(local_keys))
    pd.DataFrame([(z['key'],z.get('species',z.get('order')),day(z),z['lifeStage'],z['datasetKey']) for z in records.values()],columns=['gbif_id','taxon','day','stage','dataset_uuid']).to_csv(out/'stage_record_index.csv',index=False)
    (out/'gbif_audit.json').write_text(json.dumps(summary,indent=2))
    print(summary)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('cache',type=Path);parser.add_argument('out',type=Path)
    args=parser.parse_args();audit(args.cache,args.out)
