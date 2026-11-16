#!/usr/bin/env python3
"""Fail-closed completeness and approval-eligibility checker, NEVER grants approval."""
import argparse,csv,json
from pathlib import Path
VALID={'SUPPORTED_COMMON','SUPPORTED_V030_ONLY','INTERNAL','DEFERRED_OUT_OF_SCOPE','UNCERTAIN','BREAKING_REVIEW','UNREVIEWED'}

def check(path, require_complete=False):
    with open(path,newline='',encoding='utf-8') as f:
        rdr=csv.DictReader(f);rows=list(rdr); headers=set(rdr.fieldnames or ())
    fields={'candidate_id','import_path','proposed_decision','decision_rationale','documentation_reference','owner_name','reviewer_name','review_status'}
    if not fields.issubset(headers): raise ValueError('missing review columns')
    if len(rows)!=103 or len({r['candidate_id'] for r in rows})!=103: raise ValueError('missing/duplicated candidate IDs')
    pending=[]; issues=[]
    for r in rows:
        d=r['proposed_decision']
        if d not in VALID: issues.append(f'{r["candidate_id"]}: invalid classification {d}')
        if d in ('UNREVIEWED','UNCERTAIN','BREAKING_REVIEW'):
            pending.append(r['candidate_id'])
        if d not in ('UNREVIEWED',) and not r['decision_rationale'].strip(): issues.append(f'{r["candidate_id"]}: missing rationale')
        if d.startswith('SUPPORTED_'):
            if not r['documentation_reference'].strip(): issues.append(f'{r["candidate_id"]}: missing source documentation')
            if not r['owner_name'].strip(): issues.append(f'{r["candidate_id"]}: missing owner')
        if d in ('INTERNAL','DEFERRED_OUT_OF_SCOPE') and not r['decision_rationale'].strip(): issues.append(f'{r["candidate_id"]}: missing exclusion rationale')
    print(json.dumps({'total':len(rows),'pending_decisions':len(pending),'issues':issues[:20],'qualified':False,'approved':False}))
    if issues:raise ValueError('invalid review decisions')
    if require_complete and pending: raise ValueError(f'{len(pending)} unresolved review decisions')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--require-complete',action='store_true');a=p.parse_args()
    check(a.csv,a.require_complete)
