#!/usr/bin/env python3
"""Obtain official USGS NAAMP Counts.csv with exact pinned checksum.

This separate analysis does not change the frozen RC6 manuscript.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from download_public_naamp_sources import fetch, METADATA

COUNTS_PIN='60a3f6bc29402cd81fb01155923baaa07bccd172bce8b94fe1051d3ae25e7086'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    a=p.parse_args()
    obj=json.loads(fetch(METADATA).decode('utf-8'))
    targets=[x for x in obj.get('files',[]) if x.get('name')=='Counts.csv']
    if len(targets)!=1:raise RuntimeError('Official Counts.csv not uniquely identified')
    url=targets[0].get('downloadUri') or targets[0].get('url') or targets[0].get('uri')
    if not url or not url.startswith('https://www.sciencebase.gov/'):
        raise ValueError('Unexpected source of Counts.csv')
    raw=fetch(url)
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=COUNTS_PIN:raise ValueError('Counts.csv SHA256 mismatch')
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    print(json.dumps({'source':'official USGS NAAMP Counts.csv','bytes':len(raw),
                      'sha256':digest,'frog_outcome_accessed':True}))

if __name__=='__main__':main()
