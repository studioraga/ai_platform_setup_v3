#!/usr/bin/env python3
"""R05-B triage only: compare wheel candidate JSON and shared-test import usage.

Never infers maintainer-approved public status from names, __all__, or use in tests.
"""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

PKG = 'portable_ai_governance'


def test_imports(path: Path) -> set[tuple[str, str]]:
    """Return direct `from portable_ai_governance... import name` uses."""
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    rows = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and (
            node.module == PKG or node.module.startswith(PKG + '.')
        ):
            for a in node.names:
                if a.name != '*':
                    rows.add((node.module.replace('.', '/') + '.py', a.name))
    return rows


def normalize(data: dict) -> dict[tuple[str, str], dict]:
    result = {}
    for row in data['candidates']:
        # Status records are module-level flags, not importable symbols.
        if row['kind'] == 'declaration_status':
            continue
        key = (row['module'], row['symbol'])
        if key in result:
            raise ValueError(f'Duplicate static candidate: {key}')
        result[key] = row
    return result


def build(old: dict, new: dict, seeded: set[tuple[str, str]]) -> dict:
    o, n = normalize(old), normalize(new)
    rows = []
    for module, symbol in sorted(set(o) | set(n) | seeded):
        a = o.get((module, symbol))
        b = n.get((module, symbol))
        used = (module, symbol) in seeded
        if (a and a['kind'] == 'star_import') or (b and b['kind'] == 'star_import'):
            finding = 'UNRESOLVED_STAR_IMPORT'
        elif used and not (a and b):
            finding = 'SHARED_TEST_IMPORT_MISSING_STATIC_CANDIDATE'
        elif not a:
            finding = 'NEW_V030_CANDIDATE'
        elif not b:
            finding = 'ABSENT_V030_REVIEW_BREAKING'
        elif a['kind'] != b['kind'] or a['detail'] != b['detail']:
            finding = 'STATIC_DECLARATION_DELTA'
        elif used:
            finding = 'SHARED_TEST_IMPORT_SEED'
        elif a['basis'] == 'static___all__' or b['basis'] == 'static___all__':
            finding = 'DECLARED_ALL_CANDIDATE'
        else:
            finding = 'IMPLICIT_CANDIDATE'
        rows.append({
            'module':module, 'symbol':symbol,
            'v029_kind':a['kind'] if a else '', 'v030_kind':b['kind'] if b else '',
            'v029_basis':a['basis'] if a else '', 'v030_basis':b['basis'] if b else '',
            'shared_test_usage':used, 'triage':finding,
            'public_decision':'UNREVIEWED', 'documented_reference':'', 'owner':'',
        })
    return {
        'schema_version':1,
        'source_wheels_sha256':{'v029':old['wheel_sha256'], 'v030':new['wheel_sha256']},
        'candidate_rows':len(rows),
        'shared_test_imports':len(seeded),
        'records':rows,
        'qualification_status':'NOT_APPROVED',
        'limitations':[
            'Static declarations and shared tests are not proof of supported public API.',
            'Star-import and dynamic re-export resolution requires manual/runtime review.',
            'Inherited methods, serialization, error semantics and pre-1.0 policy require later gates.',
        ]
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--old-candidates',type=Path,required=True)
    p.add_argument('--new-candidates',type=Path,required=True)
    p.add_argument('--shared-test',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--csv',type=Path,required=True)
    a=p.parse_args()
    old=json.loads(a.old_candidates.read_text());new=json.loads(a.new_candidates.read_text())
    # Basic input shape and provenance guard: callers separately compare wheel hashes.
    for d in (old,new):
        if d.get('qualified') is not False or not d.get('wheel_sha256') or not isinstance(d.get('candidates'),list):
            p.error('Invalid candidate inventory or unexpectedly approved input')
    report=build(old,new,test_imports(a.shared_test))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.csv.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    fields=['module','symbol','v029_kind','v030_kind','v029_basis','v030_basis','shared_test_usage','triage','public_decision','documented_reference','owner']
    with a.csv.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(report['records'])
    from collections import Counter
    print(json.dumps({'rows':len(report['records']), 'shared_test_imports':len(test_imports(a.shared_test)),
      'triage_counts':dict(Counter(r['triage'] for r in report['records'])), 'qualified':False},sort_keys=True))

if __name__=='__main__':main()
