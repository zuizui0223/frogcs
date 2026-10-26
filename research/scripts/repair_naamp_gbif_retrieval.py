"""Repeat the SAME fixed 48 neighborhoods with pacing; stage is optional metadata."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import naamp_gbif_wetland_geo_g0 as original
from reliable_source_json import ReliableJSON

def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();client=ReliableJSON(a.cache)
    original.get_json=client.get
    sample,geometry=original.coord_source()
    print('Original SHA-verified fixed neighborhoods',len(sample),flush=True)
    result=original.audit_from_source(sample,geometry)
    result['retrieval_audit']=dict(client.audit)
    result['retrieved_at_utc']=datetime.now(timezone.utc).isoformat()
    result['repair_scope']='Same 48 fixed neighborhoods and first-page queries; no new sites/radius/time/species selection'
    result['old_429_failed_requests']=97
    result['all_GBIF_requests_succeeded']=all(r['successful']==r['source_queries'] for r in result['GBIF_recording_coverage'].values())
    for rec in result['GBIF_recording_coverage'].values():
        rec['all_retrieved_searches_exhaustive']=rec.pop('sample_complete_for_absence')
        rec['biological_absence_inferable']=False
    result['life_stage_is_optional_not_primary_eligibility_gate']=True
    result['background_first_page_not_complete_circle_effort']=True
    result['status']='RETRIEVAL_COMPLETE_WITH_EXPLICIT_PAGE_LIMITS' if result['all_GBIF_requests_succeeded'] else 'RETRIEVAL_INCOMPLETE_NOT_BIOLOGICAL_ZERO'
    result['protocol']='research/SPECIES_OCCURRENCE_FIRST_CONTRACT_2026-10-26.md'
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)
    if not result['all_GBIF_requests_succeeded']:raise SystemExit(4)

if __name__=='__main__':main()
