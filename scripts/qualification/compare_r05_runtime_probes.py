#!/usr/bin/env python3
"""Fail-closed R05-C discovery comparison of independently captured import probes.

This does NOT authorize any public API or prove package provenance/behavior.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {'old': '0.29.0', 'new': '0.30.0'}


def load_report(path: Path, expected_version: str) -> dict:
    report = json.loads(path.read_text(encoding='utf-8'))
    if report.get('expected_version') != expected_version or report.get('distribution_version') != expected_version:
        raise ValueError(f'{path}: expected/distribution version mismatch')
    if report.get('qualified') is not False:
        raise ValueError(f'{path}: runtime probe must remain unqualified')
    location = Path(report.get('package_location', ''))
    if 'site-packages' not in location.parts or location.name != '__init__.py':
        raise ValueError(f'{path}: unexpected package origin')
    imports = report.get('imports')
    if not isinstance(imports, list) or not imports:
        raise ValueError(f'{path}: missing imports')
    index = {}
    for item in imports:
        module, symbol = item.get('module'), item.get('symbol')
        if not isinstance(module, str) or not module.startswith('portable_ai_governance.') or not isinstance(symbol, str):
            raise ValueError(f'{path}: invalid import identity')
        key = (module, symbol)
        if key in index:
            raise ValueError(f'{path}: duplicate import {key}')
        index[key] = item
    return {'report': report, 'index': index, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def compare(old: dict, new: dict) -> dict:
    a, b = old['index'], new['index']
    issues = []
    for key in sorted(set(a) | set(b)):
        x, y = a.get(key), b.get(key)
        label = '.'.join(key)
        if x is None or y is None:
            issues.append({'symbol': label, 'kind': 'IMPORT_SET_MISMATCH'})
        elif x.get('status') != 'IMPORTABLE' or y.get('status') != 'IMPORTABLE':
            issues.append({'symbol': label, 'kind': 'IMPORT_FAILURE', 'old': x.get('status'), 'new': y.get('status')})
        else:
            for field in ('type', 'signature'):
                if x.get(field) != y.get(field):
                    issues.append({'symbol': label, 'kind': field.upper() + '_DELTA', 'old': x.get(field), 'new': y.get(field)})
    return {'schema_version': 1, 'phase': 'R05-C preliminary top-level import probe',
            'qualified': False, 'public_api_approved': False,
            'observed_common_imports': len(set(a) & set(b)),
            'old_report_sha256': old['sha256'], 'new_report_sha256': new['sha256'],
            'findings': issues, 'finding_count': len(issues),
            'limitations': ['Does not prove wheel binary provenance or maintainer-approved public status',
                            'Does not inspect class methods, invoke functions, or test serialization/exceptions',
                            'Runtime imports may execute module initialization code']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old', required=True, type=Path)
    parser.add_argument('--new', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        old = load_report(args.old, EXPECTED['old'])
        new = load_report(args.new, EXPECTED['new'])
        result = compare(old, new)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        parser.error(str(e))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'common_imports': result['observed_common_imports'],
                      'findings': result['finding_count'], 'qualified': False}))
    if result['finding_count']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
