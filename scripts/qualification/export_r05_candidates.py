#!/usr/bin/env python3
"""R05-B: static, unapproved candidate symbols from wheel AST; no SDK import."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from audit_r05_public_api import inventory


def candidates(wheel: Path) -> dict:
    modules = inventory(wheel)
    rows = []
    for module, data in sorted(modules.items()):
        declared = data['__all__']
        defined = set(data['functions']) | set(data['classes']) | set(data['constants']) | set(data['imports'])
        names = sorted(set(declared) if declared is not None else defined)
        for name in names:
            if declared is None and name.startswith('_'):
                continue
            if name in data['functions']:
                kind, detail = 'function', data['functions'][name]
            elif name in data['classes']:
                kind, detail = 'class', data['classes'][name]
            elif name in data['imports']:
                kind, detail = 'import_alias', data['imports'][name]
            elif name in data['constants']:
                kind, detail = 'constant', data['constants'][name]
            else:
                kind, detail = 'unresolved_declared_export', None
            rows.append({'module':module, 'symbol':name, 'kind':kind,
                         'basis':'static___all__' if declared is not None else 'nonprivate_top_level',
                         'detail':detail, 'status':'UNCLASSIFIED'})
        if data['star_imports']:
            rows.append({'module':module, 'symbol':'*', 'kind':'star_import',
                         'basis':'requires_export_resolution', 'detail':data['star_imports'],
                         'status':'UNRESOLVED'})
        if declared is None:
            rows.append({'module':module, 'symbol':'__all__', 'kind':'declaration_status',
                         'basis':'missing_or_dynamic', 'detail':None, 'status':'REVIEW'})
    return {'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),
            'module_count':len(modules),'candidate_count':len(rows), 'candidates':rows,
            'qualified':False, 'limitations':['Candidate list is not an approved public API.',
            'AST does not resolve inherited or runtime exports.',
            'Unresolved static __all__ expressions require manual inspection.',
            'Runtime behavior and exceptions require isolated consumer tests.']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wheel',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if not args.wheel.is_file() or not zipfile.is_zipfile(args.wheel):
        p.error('wheel must be a readable ZIP wheel file')
    result=candidates(args.wheel)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'modules':result['module_count'],
                      'candidates':result['candidate_count'],'qualified':False}))

if __name__=='__main__':
    main()
