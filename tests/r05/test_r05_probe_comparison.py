"""Unit tests for comparison logic; no historical SDK import required."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / 'scripts' / 'qualification' / 'compare_r05_runtime_probes.py'
spec = importlib.util.spec_from_file_location('r05probe_compare', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def report(tmp_path, name, version, signature='(x)', status='IMPORTABLE'):
    p = tmp_path / name
    p.write_text(json.dumps({'expected_version': version, 'distribution_version': version,
        'qualified': False, 'package_location': '/tmp/venv/lib/python3.12/site-packages/portable_ai_governance/__init__.py',
        'imports': [{'module': 'portable_ai_governance.kernel.types', 'symbol': 'Principal',
                     'status': status, 'signature': signature, 'type': 'type'}]}))
    return mod.load_report(p, version)


def test_matching_reports_remain_unqualified(tmp_path):
    got = mod.compare(report(tmp_path, 'old.json', '0.29.0'), report(tmp_path, 'new.json', '0.30.0'))
    assert got['finding_count'] == 0
    assert got['qualified'] is False
    assert got['public_api_approved'] is False


def test_signature_difference_is_review_finding(tmp_path):
    got = mod.compare(report(tmp_path, 'old.json', '0.29.0'), report(tmp_path, 'new.json', '0.30.0', '(y)'))
    assert got['findings'][0]['kind'] == 'SIGNATURE_DELTA'


def test_import_failure_is_review_finding(tmp_path):
    got = mod.compare(report(tmp_path, 'old.json', '0.29.0'), report(tmp_path, 'new.json', '0.30.0', status='IMPORT_ERROR'))
    assert got['findings'][0]['kind'] == 'IMPORT_FAILURE'


def test_duplicate_symbol_is_rejected(tmp_path):
    p = tmp_path / 'duplicate.json'
    d = {'expected_version': '0.29.0', 'distribution_version': '0.29.0', 'qualified': False,
         'package_location': '/tmp/site-packages/portable_ai_governance/__init__.py',
         'imports': [{'module': 'portable_ai_governance.kernel.types', 'symbol': 'Principal', 'status': 'IMPORTABLE'}] * 2}
    p.write_text(json.dumps(d))
    import pytest
    with pytest.raises(ValueError, match='duplicate import'):
        mod.load_report(p, '0.29.0')


def test_version_mismatch_rejected(tmp_path):
    import pytest
    p = tmp_path / 'bad.json'
    p.write_text(json.dumps({'expected_version': '0.29.0', 'distribution_version': '0.29.0'}))
    with pytest.raises(ValueError, match='version mismatch'):
        mod.load_report(p, '0.30.0')
