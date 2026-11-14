#!/usr/bin/env python3
"""R05-C preparation: read-only runtime import/signature probe of known shared-test imports.

Must run with each wheel-installed consumer Python in isolation. No network, writes,
or API methods are invoked. Imported package initializers may have normal import effects.
"""
from __future__ import annotations
import argparse
import ast
from importlib import import_module, metadata
import inspect
import json
import os
from pathlib import Path
import sys

PKG='portable_ai_governance'


def seed_imports(path:Path):
    tree=ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    pairs=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom) and node.module and (node.module == PKG or node.module.startswith(PKG+'.')):
            pairs.update((node.module,a.name) for a in node.names if a.name!='*')
    return sorted(pairs)


def signature_of(obj):
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return None


def probe(test_path:Path, expected_version:str) -> dict:
    actual=metadata.version('portable-agentic-ai-governance')
    if actual != expected_version:
        raise RuntimeError(f'installed distribution mismatch: expected {expected_version}, observed {actual}')
    root=import_module(PKG)
    location=Path(root.__file__).resolve()
    if 'site-packages' not in location.parts:
        raise RuntimeError(f'package imported outside site-packages: {location}')
    out=[]
    for module, symbol in seed_imports(test_path):
        record={'module':module,'symbol':symbol,'status':'NOT_PROBED', 'type':'', 'signature':None}
        try:
            mod=import_module(module)
            obj=getattr(mod,symbol)
            record.update(status='IMPORTABLE',type=type(obj).__name__,signature=signature_of(obj))
        except Exception as e:
            record.update(status='IMPORT_ERROR',error_type=type(e).__name__)
        out.append(record)
    return {'expected_version':expected_version,'distribution_version':actual,
            'package_location':str(location),'imports':out,
            'qualified':False,'scope':'Only imported symbols from existing seven-test suite; no methods executed'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--shared-test',type=Path,required=True)
    p.add_argument('--expected-version',required=True,choices=['0.29.0','0.30.0'])
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    result=probe(a.shared_test,a.expected_version)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    if any(r['status']!='IMPORTABLE' for r in result['imports']):
        print('FAIL: one or more shared-test exports not importable',file=sys.stderr)
        raise SystemExit(3)
    print(json.dumps({'version':a.expected_version,'imported':len(result['imports']),'qualified':False}))

if __name__=='__main__':main()
