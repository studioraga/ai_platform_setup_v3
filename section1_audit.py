#!/usr/bin/env python3
import csv, sys, json
from pathlib import Path
root=Path(__file__).resolve().parent
path=root/'requirements_evidence_gap_drills.csv'
with path.open(newline='') as f: rows=list(csv.DictReader(f))
expected={f'R{i:02d}' for i in range(1,17)}
actual={r['ID'] for r in rows}
assert actual==expected and len(rows)==16, 'Missing or duplicate R01-R16'
valid={'NOT_RUN','PASS','FAIL','BLOCKED','NOT_APPLICABLE'}
for r in rows:
 assert r['live_host_status'] in valid, (r['ID'],r['live_host_status'])
 if r['live_host_status']=='PASS':
  assert r['artifact_path'] and r['acceptance_result'] not in ('','PENDING'), r['ID']+' lacks proof'
  assert (root/r['artifact_path']).is_file(), r['ID']+' artifact missing'
summary={x:sum(r['live_host_status']==x for r in rows) for x in sorted(valid)}
print(json.dumps({'rows':len(rows),'live_host_status':summary},indent=2))
print('Mapping schema PASS; Section 1 complete only after evidence review and explicit sign-off.')
