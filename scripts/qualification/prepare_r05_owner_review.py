#!/usr/bin/env python3
"""Create a reproducible *unapproved* R05 review dossier from observed candidate data."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED = {
    '029': '34883c2c14284e85b39531a677636b7b290178942a471e745da57b3b27be2279',
    '030': '9672f1b3350411080fd75bc08caaff335de684ae75a9fcf69b462f9f67e79be5',
}
FIELDS = [
    'candidate_id','import_path','triage','v029_kind','v030_kind',
    'suggested_review','discovery_evidence','proposed_decision','decision_rationale',
    'documentation_reference','contract_methods','owner_name','reviewer_name','review_status'
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

def build(priority, old, new, kernel_old, kernel_new, out):
    olddata,newdata=load(old),load(new)
    for label, obj in [('029',olddata),('030',newdata)]:
        if obj.get('wheel_sha256') != EXPECTED[label]:
            raise ValueError(f'{label} wheel hash mismatch')
    with open(priority, newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=103:
        raise ValueError(f'expected 103 priority rows, got {len(rows)}')
    kold,knew=load(kernel_old),load(kernel_new)
    if (kold.get('version'),knew.get('version'))!=('0.29.0','0.30.0'):
        raise ValueError('runtime report version mismatch')
    ab={r['name']:r for r in kold['bindings']}
    bb={r['name']:r for r in knew['bindings']}
    oldnames=set(ab); newnames=set(bb)
    # Runtime fields from dataclasses, typing etc are incidental even when importable.
    star={'source':'portable_ai_governance/kernel/types.py',
          'initializers_identical':True,
          'common_bindings':sorted(oldnames & newnames),
          'only_029':sorted(oldnames-newnames),'only_030':sorted(newnames-oldnames),
          'defined_in_sdk':sorted(n for n in oldnames & newnames if ab[n].get('defined_module')=='portable_ai_governance.kernel.types' and bb[n].get('defined_module')=='portable_ai_governance.kernel.types'),
          'incidental_imported':sorted(n for n in oldnames & newnames if ab[n].get('defined_module') in ('dataclasses','typing','__future__') or n=='types'),
          'unstable_signature_artifact':'dataclasses.field signature includes repr of MISSING_TYPE with process-specific memory address; do not compare text as SDK change',
          'public_api_approved':False}
    output=[]; seen=set()
    for r in rows:
        module=r['module']; symbol=r['symbol']
        if not module.startswith('portable_ai_governance/') or not module.endswith('.py') or not symbol:
            raise ValueError('invalid candidate identity')
        ident=(module,symbol)
        if ident in seen: raise ValueError(f'duplicate candidate {ident}')
        seen.add(ident)
        triage=r['triage']
        classification={
            'SHARED_TEST_IMPORT_SEED':'TESTED_IMPORT_CANDIDATE',
            'DECLARED_ALL_CANDIDATE':'DECLARED_EXPORT_CANDIDATE',
            'NEW_V030_CANDIDATE':'NEW_ONLY_REVIEW',
            'UNRESOLVED_STAR_IMPORT':'STAR_IMPORT_REVIEW'
        }.get(triage,'OTHER_REVIEW')
        entry={
            'candidate_id':sha((module+':'+symbol).encode())[:16],
            'import_path':None if symbol=='*' else module[:-3].replace('/','.')+'.'+symbol,
            'triage':triage, 'v029_kind':r.get('v029_kind',''), 'v030_kind':r.get('v030_kind',''),
            'suggested_review':classification,
            'discovery_evidence':f'{module}:{symbol} | v029={r.get("v029_kind", "")} | v030={r.get("v030_kind", "")}',
            'proposed_decision':'UNREVIEWED',
            'decision_rationale':'', 'documentation_reference':'', 'contract_methods':'',
            'owner_name':'','reviewer_name':'','review_status':'PENDING'
        }
        output.append(entry)
    output.sort(key=lambda r:r['import_path'] or r['discovery_evidence'])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/'r05_owner_review.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(output)
    report={
        'schema_version':1,'status':'PROPOSED_UNAPPROVED','qualified':False,
        'owner_approved':False,'reviewer_approved':False,
        'candidate_count':len(output),'category_counts':dict(Counter(x['suggested_review'] for x in output)),
        'source_hashes':{p:sha(Path(path).read_bytes()) for p,path in [('priority',priority),('old_inventory',old),('new_inventory',new),('kernel_029',kernel_old),('kernel_030',kernel_new)]},
        'star':star,
        'scope':'Only 103 prioritized records; all other discovered candidates unapproved and outside this bounded assessment',
        'records':output
    }
    (out/'r05_owner_review.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (out/'star_import_resolution.json').write_text(json.dumps(star,indent=2,sort_keys=True)+'\n')
    text=['# R05-B review dossier','', 'Status: PROPOSED / no owner approval','',f'- Candidate rows: {len(output)}',f'- Category counts: {report["category_counts"]}',f'- Kernel star source: `{star["source"]}`', f'- Kernel runtime bindings: {len(star["common_bindings"])} common',f'- SDK-defined kernel types: {", ".join(star["defined_in_sdk"])}',f'- Incidental imports: {", ".join(star["incidental_imported"])}', '', 'The dataclasses.field signature-only difference is a process-specific repr artifact, not an SDK compatibility change.', '', 'All 103 candidates remain UNREVIEWED. A maintainer must explicitly approve support decisions and policy scope.','']
    (out/'REVIEW_SUMMARY.md').write_text('\n'.join(text))
    print(json.dumps({'rows':len(output),'review_status':'PENDING','outdir':str(out),'star_defined_sdk':len(star['defined_in_sdk'])}))
    return report

def main():
    p=argparse.ArgumentParser()
    for x in ('priority','old','new','kernel-old','kernel-new','out'):
        p.add_argument('--'+x,required=True)
    a=p.parse_args()
    build(a.priority,a.old,a.new,a.kernel_old,a.kernel_new,a.out)

if __name__=='__main__':main()
