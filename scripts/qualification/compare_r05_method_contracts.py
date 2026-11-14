#!/usr/bin/env python3
"""Fail-closed declaration comparison for explicit R05-C candidate class reports."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

VERSIONS=('0.29.0','0.30.0')

def load(path, version):
    raw=path.read_bytes();r=json.loads(raw)
    if r.get('schema_version')!=1 or r.get('distribution_version')!=version or r.get('qualified') is not False or r.get('public_api_approved') is not False:
        raise ValueError(f'Invalid report metadata: {path}')
    classes=r.get('classes')
    if not isinstance(classes,list) or not classes:
        raise ValueError('Missing classes')
    idx={}
    for c in classes:
        if not isinstance(c,dict) or not isinstance(c.get('path'),str) or not c['path'].startswith('portable_ai_governance.'):
            raise ValueError('Invalid class')
        if c['path'] in idx:
            raise ValueError('Duplicate class')
        idx[c['path']]=c
    return idx,hashlib.sha256(raw).hexdigest()

def compare(old,new):
    findings=[]
    for path in sorted(set(old)|set(new)):
        a,b=old.get(path),new.get(path)
        if a is None or b is None:
            findings.append({'path':path,'kind':'CLASS_MISSING'})
            continue
        for key in ('constructor_signature','declared_methods','dataclass_fields'):
            if a.get(key)!=b.get(key):
                findings.append({'path':path,'kind':key.upper()+'_DELTA',
                                 'old':a.get(key),'new':b.get(key)})
    return findings

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--old',type=Path,required=True);p.add_argument('--new',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:
        old,old_sha=load(a.old,VERSIONS[0]);new,new_sha=load(a.new,VERSIONS[1])
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as e:
        p.error(str(e))
    findings=compare(old,new)
    r={'schema_version':1,'phase':'R05-C method declaration comparison','qualified':False,
       'public_api_approved':False,'common_classes':len(set(old)&set(new)),
       'finding_count':len(findings),'findings':findings,
       'input_sha256':{'v029':old_sha,'v030':new_sha}}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'common_classes':r['common_classes'],'findings':len(findings),'qualified':False}))
    if findings:raise SystemExit(2)
if __name__=='__main__':main()
