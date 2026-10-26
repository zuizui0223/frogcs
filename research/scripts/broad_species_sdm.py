"""Retrospective, broad-area species SDMs; outputs are relative suitability."""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
import shutil
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import rasterio
from shapely.geometry import shape
from shapely import contains_xy
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from reliable_source_json import ReliableJSON

ROOT = Path(__file__).resolve().parents[2]
API = 'https://api.gbif.org/v1/occurrence/search'
ORDERS = {'Anura': 952, 'Caudata': 953, 'Odonata': 789}
QUERY = dict(country='US', hasCoordinate='true', hasGeospatialIssue='false',
             year='1980,2015', occurrenceStatus='PRESENT',
             decimalLatitude='24,50', decimalLongitude='-125,-66',
             coordinateUncertaintyInMeters='0,1000')
BIO = (1, 4, 12, 15)


def write_csv(path, rows):
    if not rows:
        return
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'wt', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf8')


def get_json(client, **kwargs):
    return client.get(API + '?' + urlencode({**QUERY, **kwargs}))


def cell(lon, lat):
    return (math.floor((lon + 180) * 6), math.floor((90 - lat) * 6))


def fold(lon, lat, size=2):
    # Stable hash of a whole spatial block. No labels influence fold assignment.
    key = f'{math.floor(lon / size)},{math.floor(lat / size)}'
    return int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % 5


def thin(rows):
    result = {}
    for r in sorted(rows, key=lambda x: int(x['id'])):
        result.setdefault(cell(r['lon'], r['lat']), r)
    return list(result.values())


def inventory(client, out):
    src = ROOT / 'research/results/naamp_three_guild_occurrence/occurrences.csv.gz'
    with gzip.open(src, 'rt', encoding='utf8') as f:
        candidates = {r['species_key']: r for r in csv.DictReader(f) if r['quality'] == 'strict'}
    rows, totals = [], {}
    for guild, key in ORDERS.items():
        obj = get_json(client, taxonKey=key, limit=0, facet='speciesKey', facetLimit=1000)
        totals[guild] = obj['count']
        facets = obj['facets'][0]['counts']
        if len(facets) >= 1000:
            raise ValueError('Species facet may be truncated')
        counts = {r['name']: r['count'] for r in facets}
        species = [dict(guild=guild, species=r['species'], species_key=k,
                        broad_count=counts.get(k, 0), selected=False)
                   for k, r in candidates.items() if r['guild'] == guild]
        species.sort(key=lambda r: (-r['broad_count'], r['species_key']))
        for r in species[:5]:
            r['selected'] = True
        for r in species:
            if r['species'] in ('Ambystoma maculatum', 'Ambystoma tigrinum', 'Ambystoma opacum'):
                r['selected'] = True
            r['selection_reason'] = ('pond_breeding_stage_hypothesis' if r['species'].startswith('Ambystoma ') and r['selected']
                                     else 'top_five_record_count' if r['selected'] else 'not_in_initial_model_cohort')
        rows.extend(species)
    write_csv(out / 'species_inventory.csv', rows)
    write_json(out / 'inventory.json', dict(date_utc=datetime.now(timezone.utc).isoformat(), query=QUERY, order_counts=totals,
                                         candidate_species=len(rows), selected_species=sum(r['selected'] for r in rows)))
    return rows


def retrieve(client, inventory_rows, out):
    rows, receipts, excluded_datasets = [], [], {}
    for spec in inventory_rows:
        if not spec['selected']:
            continue
        sid = spec['species_key']
        filename = out / f'occurrences_{sid}.csv.gz'
        receipt_file = out / f'query_{sid}.json'
        if filename.exists() and receipt_file.exists():
            receipt = json.loads(receipt_file.read_text())
            if receipt.get('complete') and receipt.get('query') == QUERY:
                with gzip.open(filename, 'rt', encoding='utf8') as f:
                    cached = list(csv.DictReader(f))
                for r in cached:
                    r['lon'], r['lat'] = float(r['lon']), float(r['lat'])
                rows.extend(cached)
                receipts.append(receipt)
                continue
        found, seen, qa = [], set(), Counter()
        offset, count = 0, None
        while True:
            if offset >= 99000:
                raise RuntimeError(f'{sid}: query needs subdivision; no partial model allowed')
            obj = get_json(client, taxonKey=sid, limit=300, offset=offset)
            count = obj['count']
            for r in obj['results']:
                qa['read'] += 1
                if r.get('basisOfRecord') in ('FOSSIL_SPECIMEN', 'LIVING_SPECIMEN'):
                    qa['excluded_basis'] += 1
                    continue
                if str(r.get('speciesKey')) != sid:
                    qa['different_species'] += 1
                    continue
                ds = r['datasetKey']
                if ds not in excluded_datasets:
                    meta = client.get('https://api.gbif.org/v1/dataset/' + ds)
                    title = meta.get('title', '').lower()
                    excluded_datasets[ds] = ('naamp' in title or 'north american amphibian monitoring' in title)
                if excluded_datasets[ds]:
                    qa['NAAMP_dataset'] += 1
                    continue
                rid = str(r['key'])
                if rid in seen:
                    qa['duplicate_id'] += 1
                    continue
                seen.add(rid)
                found.append(dict(id=rid, species_key=sid, species=spec['species'], guild=spec['guild'],
                                  lon=float(r['decimalLongitude']), lat=float(r['decimalLatitude']),
                                  year=r.get('year', ''), month=r.get('month', ''),
                                  stage=r.get('lifeStage', ''), dataset=ds,
                                  basis=r.get('basisOfRecord', ''), uncertainty=r.get('coordinateUncertaintyInMeters')))
            offset += len(obj['results'])
            if obj.get('endOfRecords') or offset >= count:
                break
            if not obj['results']:
                raise ValueError('Unexpected empty intermediate GBIF page')
        receipt = dict(species_key=sid, query=QUERY, date_utc=datetime.now(timezone.utc).isoformat(),
                       count=count, complete=True, kept=len(found), screens=dict(qa))
        write_csv(filename, found)
        write_json(receipt_file, receipt)
        rows.extend(found)
        receipts.append(receipt)
        print(spec['guild'], spec['species'], 'retained', len(found), flush=True)
    write_json(out / 'retrieval.json', receipts)
    return rows


def download(url, path):
    if not path.exists():
        tmp = path.with_suffix('.part')
        request = urllib.request.Request(url, headers={'User-Agent':'Frogcs-EcologyMacro/1.0', 'Accept':'application/octet-stream,*/*'})
        with urllib.request.urlopen(request, timeout=180) as src, open(tmp, 'wb') as dest:
            shutil.copyfileobj(src, dest)
        tmp.replace(path)
    return dict(url=url, bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def rasters(cache, out):
    z = cache / 'wc2.1_10m_bio.zip'
    receipts = [download('https://geodata.ucdavis.edu/climate/worldclim/2_1/base/' + z.name, z)]
    paths = []
    with zipfile.ZipFile(z) as archive:
        for n in BIO:
            name = f'wc2.1_10m_bio_{n}.tif'
            if not (cache / name).exists():
                with archive.open(name) as src, open(cache / name, 'wb') as dest:
                    dest.write(src.read())
            paths.append(cache / name)
    pins = json.loads((ROOT / 'research/results/earthenv_wetland_1deg/observed_results.json').read_text())['download_receipts']
    for n in (8, 12):
        path = cache / f'earthenv_{n}.tif'
        receipt = download(f'https://data.earthenv.org/consensus_landcover/with_DISCover/consensus_full_class_{n}.tif', path)
        if receipt['sha256'] != pins[str(n)]['sha256']:
            raise ValueError('EarthEnv hash mismatch')
        receipts.append(receipt)
        paths.append(path)
    write_json(out / 'environment_receipts.json', receipts)
    return paths


def sample(paths, rows):
    xy = [(r['lon'], r['lat']) for r in rows]
    columns = []
    for path in paths:
        with rasterio.open(path) as src:
            values = np.array([float(v[0]) if not np.ma.is_masked(v[0]) else np.nan
                               for v in src.sample(xy, masked=True)])
            if 'earthenv' in str(path):
                values[(values < 0) | (values > 100)] = np.nan
            columns.append(values)
    return np.column_stack(columns)


def features(x):
    # Standardizing before squares is part of the fitted model, not a global preprocessing step.
    from sklearn.preprocessing import FunctionTransformer
    return make_pipeline(StandardScaler(), FunctionTransformer(lambda z: np.column_stack([z, z*z])),
                         StandardScaler(), LogisticRegression(C=1, class_weight='balanced', max_iter=2000))


def evaluate(x, y, xy, size):
    groups = np.array([fold(r['lon'], r['lat'], size) for r in xy])
    values = []
    for k in range(5):
        test = groups == k
        train = ~test
        pos, neg = int(y[test].sum()), int((1-y[test]).sum())
        row = dict(fold=k, block_degrees=size, positive_test=pos, background_test=neg, auc=None)
        if pos >= 5 and neg >= 20 and y[train].sum() >= 20 and (1-y[train]).sum() >= 20:
            model = features(x)
            model.fit(x[train], y[train])
            row['auc'] = float(roc_auc_score(y[test], model.predict_proba(x[test])[:, 1]))
        values.append(row)
    return values


def us_domain(cache, out):
    url = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'
    path = cache / 'ne_110m_admin_0_countries.geojson'
    receipt = download(url, path)
    features = json.loads(path.read_text(encoding='utf8'))['features']
    us = next(f for f in features if f['properties']['ADM0_A3'] == 'USA')
    write_json(out / 'us_domain.geojson', us)
    write_json(out / 'domain_receipt.json', receipt)
    return shape(us['geometry'])


def in_domain(domain, rows):
    return np.asarray(contains_xy(domain, [r['lon'] for r in rows], [r['lat'] for r in rows]), dtype=bool)


def fit_models(records, paths, out, sites, domain):
    inside = in_domain(domain, records)
    write_json(out / 'domain_screen.json', dict(retrieved=len(records), retained=int(inside.sum()),
               excluded_outside_generalized_us_polygon=int((~inside).sum())))
    records = [r for r, keep in zip(records, inside) if keep]
    rng = np.random.default_rng(20261026)
    # Uniform area on the sphere, restricted to continental-US rectangle and climate land mask.
    lat = np.degrees(np.arcsin(rng.uniform(np.sin(np.radians(24)), np.sin(np.radians(50)), 10000)))
    lon = rng.uniform(-125, -66, 10000)
    bg = [dict(lon=float(a), lat=float(b)) for a, b in zip(lon, lat)]
    bx = sample(paths, bg)
    keep = np.flatnonzero(np.isfinite(bx).all(axis=1) & in_domain(domain, bg))[:4000]
    bg, bx = [bg[i] for i in keep], bx[keep]
    write_csv(out / 'background.csv.gz', [{**r, **dict(zip(['bio1','bio4','bio12','bio15','flooded','water'], x))} for r,x in zip(bg,bx)])
    sx = sample(paths, sites) if sites else np.empty((0, 6))
    write_csv(out / 'naamp_site_environment.csv.gz', [{**r, **dict(zip(['bio1','bio4','bio12','bio15','flooded','water'], x))} for r,x in zip(sites,sx)])
    thinned = []
    for sid in sorted({r['species_key'] for r in records}):
        thinned.extend(thin([r for r in records if r['species_key'] == sid]))
    tx = sample(paths, thinned)
    valid = np.isfinite(tx).all(axis=1)
    thinned, tx = [r for i,r in enumerate(thinned) if valid[i]], tx[valid]
    write_csv(out / 'training_presence_environment.csv.gz', [{**r, **dict(zip(['bio1','bio4','bio12','bio15','flooded','water'], x))} for r,x in zip(thinned,tx)])
    results, predictions, bg_predictions = [], [], {}
    for sid in sorted({r['species_key'] for r in records}):
        idx = np.array([r['species_key'] == sid for r in thinned])
        pr = [r for r in thinned if r['species_key'] == sid]
        if len(pr) < 30:
            results.append(dict(species_key=sid, status='insufficient_cells', cells=len(pr)))
            continue
        px = tx[idx]
        for kind in ('uniform', 'target_group'):
            if kind == 'uniform':
                br, xx = bg, bx
            else:
                br = thin([r for r in thinned if r['guild'] == pr[0]['guild'] and r['species_key'] != sid])
                xx = sample(paths, br)
                if len(br) < 100:
                    continue
            x, y = np.vstack([px, xx]), np.r_[np.ones(len(px)), np.zeros(len(xx))]
            cv = evaluate(x, y, pr + br, 2) + evaluate(x, y, pr + br, 4)
            model = features(x)
            model.fit(x, y)
            bg_score = model.decision_function(bx)
            bg_predictions[(sid, kind)] = bg_score
            summary = dict(species_key=sid, species=pr[0]['species'], guild=pr[0]['guild'], status='fit',
                           background=kind, cells=len(px), background_cells=len(xx), cv=cv)
            results.append(summary)
            ok = np.isfinite(sx).all(axis=1)
            valid_indices = np.flatnonzero(ok)
            scores = model.decision_function(sx[ok]) if ok.any() else []
            sorted_bg = np.sort(bg_score)
            for i, score in zip(valid_indices, scores):
                predictions.append(dict(site=sites[i]['site'], species_key=sid, species=pr[0]['species'], guild=pr[0]['guild'],
                                        background=kind, suitability_percentile=float(np.searchsorted(sorted_bg, score, side='right')/len(sorted_bg)),
                                        environment_extrapolation=bool(((sx[i] < x.min(axis=0)) | (sx[i] > x.max(axis=0))).any())))
            print('fit', pr[0]['species'], kind, 'cells', len(px), flush=True)
    write_json(out / 'models.json', results)
    write_csv(out / 'naamp_species_suitability.csv.gz', predictions)
    overlaps = []
    for kind in ('uniform', 'target_group'):
        keys = sorted(k for k in bg_predictions if k[1] == kind)
        for a,b in itertools.combinations(keys, 2):
            u,v = bg_predictions[a], bg_predictions[b]
            u,v = np.exp(u-u.max()), np.exp(v-v.max())
            d = 1 - .5 * np.abs(u/u.sum()-v/v.sum()).sum()
            overlaps.append(dict(species_a=a[0], species_b=b[0], background=kind, schoener_d=float(d)))
    write_csv(out / 'predicted_background_overlap.csv', overlaps)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--inventory-only', action='store_true')
    ap.add_argument('--project-naamp', action='store_true')
    ap.add_argument('--occurrences-from', type=Path)
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.occurrences_from and (args.occurrences_from/'inventory.json').exists():
        source_inventory = args.occurrences_from/'inventory.json'
        previous_query = json.loads(source_inventory.read_text())['query']
        if previous_query != QUERY:
            raise ValueError('Cannot reuse occurrences with a different retrieval scope')
        for receipt_path in args.occurrences_from.glob('query_*.json'):
            receipt = json.loads(receipt_path.read_text())
            sid = receipt['species_key']
            data = args.occurrences_from/f'occurrences_{sid}.csv.gz'
            if receipt.get('complete') and data.exists():
                receipt['query'] = previous_query
                receipt['reused_inventory_sha256'] = hashlib.sha256(source_inventory.read_bytes()).hexdigest()
                shutil.copyfile(data, args.out/data.name)
                write_json(args.out/receipt_path.name, receipt)
    client = ReliableJSON(args.cache/'json', interval=.6)
    inv = inventory(client, args.out)
    print('inventory', json.loads((args.out/'inventory.json').read_text()), flush=True)
    if args.inventory_only:
        return
    records = retrieve(client, inv, args.out)
    paths = rasters(args.cache, args.out)
    sites = []
    if args.project_naamp:
        from naamp_three_guild_occurrence import all_geometry, token
        sites = [dict(route=rt, site=token(sid), lat=lat, lon=lon) for rt,sid,lat,lon in all_geometry()]
    results = fit_models(records, paths, args.out, sites, us_domain(args.cache, args.out))
    write_json(args.out/'run_summary.json', dict(records=len(records), unique_ids=len({r['id'] for r in records}),
               records_by_guild=dict(Counter(r['guild'] for r in records)),
               fitted_species=len({r['species_key'] for r in results if r['status']=='fit'}),
               projected_sites=len(sites), interpretation='Relative climate/landscape suitability, not calibrated occupancy probability',
               source_audit=dict(client.audit)))


if __name__ == '__main__':
    main()
