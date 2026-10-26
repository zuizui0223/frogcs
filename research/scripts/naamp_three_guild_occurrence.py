"""Occurrence-first NAAMP-centered pilot; recording neighborhoods are NOT ponds."""
import argparse, csv, gzip, hashlib, io, itertools, json, math
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode
import numpy as np
import naamp_gbif_wetland_geo_g0 as geo
from reliable_source_json import ReliableJSON
from naamp_prior_community_allocation import loadmod, ROOT

GUILDS=('Anura','Caudata','Odonata')

def overlap(a,b):
    both=len(a&b); union=len(a|b)
    return dict(a=len(a),b=len(b),shared=both,union=union,jaccard=both/union if union else None,
                sorensen=2*both/(len(a)+len(b)) if len(a)+len(b) else None)

def schoener(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    return float(1-.5*np.abs(a/a.sum()-b/b.sum()).sum()) if a.sum()>0 and b.sum()>0 else None

def quality(row):
    try:u=float(row['coordinateUncertaintyInMeters'])
    except (KeyError,ValueError,TypeError):return 'unknown'
    return 'strict' if math.isfinite(u) and 0<=u<=1000 else 'exclude'

def prior_fraction(rows,year,season):
    q=[x['strong'] for x in rows if x['year']<year and x['season']==season]
    return len(q),float(np.mean(q)) if q else None

def matched_history(rows):
    groups=defaultdict(list)
    for r in rows:groups[r['run']].append(r)
    out=[]
    for rid,rs in groups.items():
        if len(rs)!=2:continue
        if sorted(r['strong'] for r in rs)!=[0,1]:continue
        chosen=next(r for r in rs if r['strong']);silent=next(r for r in rs if not r['strong'])
        if silent['any'] or min(r['prior_n'] for r in rs)<2:continue
        if any(v is None for r in rs for v in r['env']):continue
        if max(abs(a-b) for a,b in zip(chosen['env'],silent['env']))>10:continue
        out.append(dict(run=rid,route=chosen['route'],history_difference=chosen['prior']-silent['prior'],
                        chosen_prior=chosen['prior'],silent_prior=silent['prior']))
    return out

def matched_history_all(rows):
    """Disjoint greedy matches within a run, using environment only, never prior outcomes."""
    by=defaultdict(list);out=[]
    for r in rows:
        if r['prior_n']<2 or r.get('timeout')!=0 or r.get('noise') is None or r.get('air') is None or any(v is None for v in r['env']):continue
        by[r['run']].append(r)
    for run,rs in by.items():
        candidates=[]
        for a in rs:
            if not a['strong']:continue
            for b in rs:
                if b['any'] or a['noise']!=b['noise'] or abs(a['air']-b['air'])>2:continue
                diff=[abs(x-y) for x,y in zip(a['env'],b['env'])]
                if max(diff)>10:continue
                candidates.append((sum(diff)/10+abs(a['air']-b['air'])/2,a['site'],b['site'],a,b))
        used=set()
        for score,sa,sb,a,b in sorted(candidates,key=lambda x:x[:3]):
            if sa in used or sb in used:continue
            used.update([sa,sb]);out.append(dict(run=run,route=a['route'],chosen_site=sa,silent_site=sb,
                history_difference=a['prior']-b['prior'],chosen_prior=a['prior'],silent_prior=b['prior'],matching_distance=score))
    return out

def all_geometry():
    b=geo.get_bytes(geo.COORD_URL)
    if hashlib.sha256(b).hexdigest()!=geo.COORD_SHA:raise ValueError('coordinate drift')
    groups=defaultdict(dict);bad=set()
    for r in csv.DictReader(io.StringIO(b.decode('utf-8-sig'))):
        try:lat,lon=float(r['lat']),float(r['lon'])
        except (ValueError,TypeError):continue
        sid=r['SiteID'].strip();rt=r['RouteNumber'].strip()
        if not sid or not rt or not 24<=lat<=50 or not -125<=lon<=-66:continue
        if sid in groups[rt] and groups[rt][sid]!=(lat,lon):bad.add(rt)
        groups[rt][sid]=(lat,lon)
    out=[]
    for rt,points in groups.items():
        if rt in bad or len(points)<8:continue
        coords=list(points.values())
        if max(geo.hav(*a,*b) for i,a in enumerate(coords) for b in coords[i+1:])>40:continue
        out.extend((rt,sid,*xy) for sid,xy in points.items())
    if len({r[1] for r in out})!=len(out):raise ValueError('SiteID occurs in multiple geometry routes')
    return out

def token(text):return hashlib.sha256(str(text).encode()).hexdigest()[:16]

def fetch_occurrences(sample,client,out):
    records={};members={};queries=[]
    for i,(route,site,lat,lon) in enumerate(sample):
        center=token(site);dlat=25/111.32;dlon=25/(111.32*math.cos(math.radians(lat)))
        for guild in GUILDS:
            params=dict(limit=300,country='US',hasCoordinate='true',hasGeospatialIssue='false',
                        year='2001,2015',occurrenceStatus='PRESENT',taxonKey=geo.TAXA[guild],
                        decimalLatitude=f'{lat-dlat:.6f},{lat+dlat:.6f}',decimalLongitude=f'{lon-dlon:.6f},{lon+dlon:.6f}')
            query=dict(center=center,guild=guild,status='INCOMPLETE',pages=0,total_bbox=None)
            qa=Counter()
            try:
                for page in range(20):
                    obj=client.get(geo.GBIF+'?'+urlencode({**params,'offset':300*page}))
                    if not isinstance(obj.get('results'),list) or not isinstance(obj.get('count'),int):raise ValueError('GBIF schema')
                    query.update(pages=page+1,total_bbox=obj['count'])
                    for r in obj['results']:
                        qa['bbox_rows_read']+=1
                        try:
                            dist=geo.hav(lat,lon,float(r['decimalLatitude']),float(r['decimalLongitude']))
                            key=str(r['key']);year=int(r['year'])
                        except (KeyError,ValueError,TypeError):qa['invalid_coordinate_id_year']+=1;continue
                        try:month=int(r['month'])
                        except (KeyError,ValueError,TypeError):month=None
                        if month is not None and not 1<=month<=12:month=None
                        if dist>25:qa['outside_circle']+=1;continue
                        if not 2001<=year<=2015:qa['invalid_year']+=1;continue
                        if not r.get('speciesKey') or not r.get('species'):qa['unresolved_species']+=1;continue
                        rec=dict(id=key,guild=guild,species=r['species'],species_key=str(r['speciesKey']),
                                 year=year,month=month,stage_raw=r.get('lifeStage') or '',dataset=r.get('datasetKey'),
                                 quality=quality(r),uncertainty=r.get('coordinateUncertaintyInMeters'))
                        if key in records and records[key]!=rec:raise ValueError('Conflicting duplicate occurrence')
                        records[key]=rec;members[(center,key)]=dict(center=center,id=key,distance_km=dist)
                    if obj.get('endOfRecords') or (page+1)*300>=obj['count']:
                        query['status']='COMPLETE';break
                if query['status']!='COMPLETE':query['status']='PAGE_CAP'
            except Exception as exc:query['status']='ERROR';query['error']=str(exc)[:250]
            query['row_screen_counts']=dict(qa);queries.append(query)
        print('GBIF center complete',i+1,'unique records',len(records),flush=True)
    writecsv(out/'occurrences.csv.gz',list(records.values()))
    writecsv(out/'neighborhood_membership.csv.gz',list(members.values()))
    return records,list(members.values()),queries

def writecsv(path,rows):
    if not rows:return
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path,'wt',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def environments(sample,cache):
    import rasterio
    import earthenv_global_flooded_vegetation_1deg as env
    pins=json.loads((ROOT/'research/results/earthenv_wetland_1deg/observed_results.json').read_text(encoding='utf8'))['download_receipts']
    values={token(s):[] for _,s,_,_ in sample};receipts={}
    for cls in (8,12):
        path=cache/f'earthenv_{cls}.tif'
        if path.exists():
            receipt=dict(pins[str(cls)]);receipt['reused_hash_verified_local_file']=True
            if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt['sha256']:raise ValueError('Cached EarthEnv drift')
        else:receipt=env.get(env.BASE+str(cls)+'.tif',path)
        if receipt['sha256']!=pins[str(cls)]['sha256']:raise ValueError('EarthEnv source hash drift')
        receipts[str(cls)]=receipt
        with rasterio.open(path) as src:
            for (_,site,lat,lon),v in zip(sample,src.sample([(x[3],x[2]) for x in sample])):
                value=float(v[0]);values[token(site)].append(value if 0<=value<=100 else None)
    return values,receipts

def summaries(records,members,queries,env):
    complete={q['center'] for q in queries if all(z['status']=='COMPLETE' for z in queries if z['center']==q['center'])}
    results=[]
    for radius in (5,25):
      for accuracy in ('strict','strict_plus_unknown'):
        rows=[]
        for m in members:
            r=records[m['id']]
            if m['center'] not in complete or m['distance_km']>radius or r['quality']=='exclude':continue
            if accuracy=='strict' and r['quality']!='strict':continue
            rows.append({**r,'center':m['center']})
        sets={g:set(r['center'] for r in rows if r['guild']==g) for g in GUILDS}
        annual={g:set((r['center'],r['year']) for r in rows if r['guild']==g) for g in GUILDS}
        cubes={g:set((r['center'],r['year'],r['month']) for r in rows if r['guild']==g and r['month'] is not None) for g in GUILDS}
        pairs=[]
        for a,b in itertools.combinations(GUILDS,2):
            seasonal=[];hab=[]
            for g in (a,b):
                months=Counter(x[2] for x in cubes[g]);seasonal.append([months[m] for m in range(1,13)])
                bins=Counter()
                for c,y,m in cubes[g]:
                    if any(v is None for v in env[c]):continue
                    code=tuple(int(np.digitize(v,[1,10,30,60])) for v in env[c]);bins[code]+=1
                hab.append(bins)
            keys=sorted(set(hab[0])|set(hab[1]))
            common_years={x[:2] for x in cubes[a]}&{x[:2] for x in cubes[b]}
            within=[]
            for cy in common_years:
                ma={x[2] for x in cubes[a] if x[:2]==cy};mb={x[2] for x in cubes[b] if x[:2]==cy}
                within.append(schoener([int(m in ma) for m in range(1,13)],[int(m in mb) for m in range(1,13)]))
            pairs.append(dict(guild_a=a,guild_b=b,neighborhood=overlap(sets[a],sets[b]),
                         neighborhood_year=overlap(annual[a],annual[b]),
                         neighborhood_year_month=overlap(cubes[a],cubes[b]),
                         seasonal_schoener_D=schoener(*seasonal),
                         jointly_recorded_center_years=len(within),
                         mean_within_center_year_month_overlap=float(np.mean(within)) if within else None,
                         background_environment_schoener_D=schoener(*[[v[k] for k in keys] for v in hab]),
                         occupied_environment_bins=[len(h) for h in hab]))
        results.append(dict(radius_km=radius,accuracy=accuracy,complete_centers=len(complete),
            unique_occurrences=len({r['id'] for r in rows}),memberships=len(rows),
            guild_counts={g:dict(unique_occurrences=len({r['id'] for r in rows if r['guild']==g}),
                species=len({r['species_key'] for r in rows if r['guild']==g}),centers=len(sets[g]),
                datasets=len({r['dataset'] for r in rows if r['guild']==g and r['dataset']}),
                unknown_month_unique_occurrences=len({r['id'] for r in rows if r['guild']==g and r['month'] is None}),
                unlabelled_stage_unique_occurrences=len({r['id'] for r in rows if r['guild']==g and not r['stage_raw']})) for g in GUILDS},
            three_guild_centers=len(set.intersection(*sets.values())),three_guild_center_year_months=len(set.intersection(*cubes.values())),pairs=pairs))
    return results

def overlay_occurrences(records,members,queries,rows,radius=25):
    """Record support, not absence/exposure: same center-period and strictly prior years."""
    complete={q['center'] for q in queries if all(z['status']=='COMPLETE' for z in queries if z['center']==q['center'])}
    monthly=defaultdict(set);annual=defaultdict(set);names=defaultdict(set)
    for m in members:
        r=records[m['id']]
        if m['center'] not in complete or m['distance_km']>radius or r['quality']!='strict':continue
        annual[(m['center'],r['year'],r['guild'])].add(r['species_key'])
        if r['month'] is not None:
            monthly[(m['center'],r['year'],r['month'],r['guild'])].add(r['species_key'])
            names[(m['center'],r['year'],r['month'])].add(r['species'])
    out=[]
    for row in rows:
        r=dict(row);c=r['site'];y=int(r['year']);month=int(r['month']);valid=c in complete
        r['gbif_complete_neighborhood']=valid
        for g in GUILDS:
            r[g+'_same_month_recorded_species']=len(monthly[(c,y,month,g)]) if valid else None
            prior=set().union(*(annual[(c,yy,g)] for yy in range(2001,y)))
            r[g+'_prior_years_recorded_species']=len(prior) if valid else None
        r['same_month_exact_name_naamp_gbif_matches']=len(set(r['source_taxa'].split('|'))&names[(c,y,month)]) if valid else None
        out.append(r)
    return out

def naamp_history(sample,env,cache,out,full=False):
    base=loadmod('occurrence_naamp_base',ROOT/'scripts/naamp/run_naamp_ecological_pulse.py')
    raw={};item=None
    for name,sha in base.PINS.items():
        p=cache/name
        if not p.exists():
            if item is None:item=base.get_json(base.ITEM_URL)
            p.write_bytes(base.get_bytes(base.find_file(item,name)))
        b=p.read_bytes()
        if hashlib.sha256(b).hexdigest()!=sha:raise ValueError('NAAMP source hash drift')
        raw[name]=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
    runs,_=base.build_runs(raw);metadata={str(r.RunID):r for r in runs.itertuples(index=False)}
    centers={str(s):token(s) for _,s,_,_ in sample};counts=defaultdict(int);invalid=set();taxa=defaultdict(set)
    for r in raw['Counts.csv']:
        key=(str(r['RunID']).strip(),str(r['StopNumber']).strip());ci=str(r.get('CallingIndex','')).strip()
        if ci not in ('0','1','2','3'):invalid.add(key);continue
        counts[key]=max(counts[key],int(ci))
        if ci in ('1','2','3'):taxa[key].add(str(r.get('Species','')).strip())
    rows=[];seen=set()
    for r in raw['Stops.csv']:
        rid=str(r['RunID']).strip();sid=str(r.get('SiteID','')).strip();st=str(r['StopNumber']).strip()
        if rid not in metadata or sid not in centers or str(r.get('SkippedStop','')).strip()!='0' or (rid,st) in invalid:continue
        key=(rid,sid)
        if key in seen:raise ValueError('Duplicate completed site survey')
        seen.add(key);m=metadata[rid];ci=counts[(rid,st)]
        date=(datetime(int(m.SurveyYear),1,1)+timedelta(days=int(m.doy)-1)).date()
        def num(value):
            try:v=float(value);return v if math.isfinite(v) else None
            except (ValueError,TypeError):return None
        air=num(r.get('AirTemp'));mass=num(r.get('MassNoiseIndex'));noise=num(r.get('Noise'));timeout=num(r.get('TimeOut'))
        if air is not None:
            air=(air-32)*5/9 if m.TempScale=='F' else air if m.TempScale=='C' else None
        if air is not None and not -10<=air<=45:air=None
        noise=int(mass>=2) if mass is not None and 0<=mass<=4 else int(noise) if noise in (0,1) else None
        rows.append(dict(run=token(rid),route=token(m.route_cluster),site=centers[sid],year=int(m.SurveyYear),date=date.isoformat(),month=date.month,doy=int(m.doy),air=air,noise=noise,timeout=timeout,
                         season=str(m.RunNumber),any=int(ci>=1),strong=int(ci>=2),env=env[centers[sid]],
                         source_taxa=sorted(taxa[(rid,st)])))
    bysite=defaultdict(list)
    for r in rows:bysite[r['site']].append(r)
    for r in rows:r['prior_n'],r['prior']=prior_fraction(bysite[r['site']],r['year'],r['season'])
    matched=matched_history_all(rows) if full else matched_history(rows)
    detail=[{**r,'source_taxa':'|'.join(r['source_taxa']),'env':json.dumps(r['env'])} for r in rows]
    writecsv(out/'naamp_completed_site_surveys.csv.gz',detail)
    writecsv(out/'matched_strong_silent_history.csv',matched)
    routes=defaultdict(list)
    for r in matched:routes[r['route']].append(r['history_difference'])
    route_means=np.array([np.mean(v) for v in routes.values()]);interval=None
    if full and len(routes)>=10:
        rng=np.random.default_rng(20261026);ix=rng.integers(0,len(routes),size=(2000,len(routes)))
        interval=np.quantile(route_means[ix].mean(axis=1),[.025,.975]).tolist()
    return dict(source_sha256=base.PINS,eligible_complete_runs=len(runs),selected_centers_with_completed_visits=len(bysite),
                selected_completed_visits=len(rows),strong_visits=sum(r['strong'] for r in rows),silent_visits=sum(not r['any'] for r in rows),
                matched_strong_silent_visits=len(matched),independent_matched_routes=len({r['route'] for r in matched}),
                mean_prior_strong_difference=float(np.mean([r['history_difference'] for r in matched])) if matched else None,
                equal_route_mean_prior_difference=float(route_means.mean()) if len(route_means) else None,
                equal_route_bootstrap_interval=interval,
                matching_scope='all geometry-valid source sites; current local temperature/noise/timeout and same run' if full else 'fixed48 endpoints; center landcover and same run',
                note='Association with past calling, not causal memory; source-center background does not measure pond hydroperiod or plants.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True);a.cache.mkdir(parents=True,exist_ok=True)
    sample,geometry=geo.coord_source();client=ReliableJSON(a.cache/'json')
    records,members,queries=fetch_occurrences(sample,client,a.out)
    (a.out/'queries.json').write_text(json.dumps(queries,indent=2),encoding='utf8')
    env,receipts=environments(sample,a.cache)
    rows=[dict(center=token(s),route=token(rt),earthenv_flooded=env[token(s)][0],earthenv_water=env[token(s)][1]) for rt,s,_,_ in sample]
    writecsv(a.out/'center_environment.csv',rows)
    result=dict(date_utc=datetime.now(timezone.utc).isoformat(),source_geometry=geometry,query_status=dict(Counter(q['status'] for q in queries)),
                retrieval=dict(client.audit),environment_receipts=receipts,overlap=summaries(records,members,queries,env))
    result['environment_diagnostics']=dict(centers=len(env),both_zero_centers=sum(v==[0,0] for v in env.values()),distinct_value_pairs=len({tuple(v) for v in env.values()}),
        assignment='landcover at listening center, not GBIF organism location or breeding pond')
    try:
        result['naamp_history']=naamp_history(sample,env,a.cache,a.out)
        with gzip.open(a.out/'naamp_completed_site_surveys.csv.gz','rt',encoding='utf8') as f:visits=list(csv.DictReader(f))
        joined=overlay_occurrences(records,members,queries,visits)
        writecsv(a.out/'naamp_gbif_center_month_overlay.csv.gz',joined)
        result['record_overlay']=dict(rows=len(joined),same_month_support_visits={g:sum((r[g+'_same_month_recorded_species'] or 0)>0 for r in joined) for g in GUILDS},
           exact_name_naamp_gbif_match_visits=sum((r['same_month_exact_name_naamp_gbif_matches'] or 0)>0 for r in joined),
           spatial_scope_km=25,temporal_scope='same calendar month/year, not necessarily same date',
           zero_means='no retrieved record under specified filters, NOT biological absence')
    except Exception as exc:result['naamp_history']={'status':'FAILED','error':str(exc)}
    try:
        allsites=all_geometry();allenvironments,_=environments(allsites,a.cache)
        target=a.out/'full_naamp_history';target.mkdir(exist_ok=True)
        result['full_naamp_environment_matched_history']=naamp_history(allsites,allenvironments,a.cache,target,full=True)
        result['full_naamp_environment_matched_history']['geometry_sites']=len(allsites)
    except Exception as exc:result['full_naamp_environment_matched_history']={'status':'FAILED','error':str(exc)}
    result['status']='COMPLETE_BOUNDED_PILOT' if all(q['status']=='COMPLETE' for q in queries) and result['naamp_history'].get('status')!='FAILED' and result['full_naamp_environment_matched_history'].get('status')!='FAILED' else 'INCOMPLETE_EXPLICIT_GAPS'
    result['limits']=['not verified ponds','no biological absences','overlapping circles not independent','no availability-corrected niche or causal competition',
                      'stage unknown retained','EarthEnv background is not measured hydroperiod/pond plants','original N/L/C not redefined']
    (a.out/'observed_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)
    if result['status']!='COMPLETE_BOUNDED_PILOT':raise SystemExit(4)

if __name__=='__main__':main()
