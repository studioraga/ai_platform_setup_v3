"""Synthetic-only R05-B candidate extraction tests; no Governance import."""
from __future__ import annotations
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'/'qualification'))
from export_r05_candidates import candidates  # noqa: E402


def test_static_candidates_and_unresolved_exports(tmp_path):
    wheel=tmp_path/'a.whl'
    with ZipFile(wheel,'w') as z:
        z.writestr('portable_ai_governance/__init__.py', 'from .api import *\n')
        z.writestr('portable_ai_governance/api.py',
                   '__all__ = ["Item", "ghost"]\nclass Item:\n    def run(self, x:int=1): pass\n')
    report=candidates(wheel)
    rows={(r['module'],r['symbol']):r for r in report['candidates']}
    assert rows['portable_ai_governance/api.py','Item']['kind']=='class'
    assert rows['portable_ai_governance/api.py','ghost']['kind']=='unresolved_declared_export'
    assert rows['portable_ai_governance/__init__.py','*']['status']=='UNRESOLVED'
    assert report['qualified'] is False


def test_implicit_candidate_does_not_claim_public_support(tmp_path):
    wheel=tmp_path/'a.whl'
    with ZipFile(wheel,'w') as z:
        z.writestr('portable_ai_governance/mod.py', 'from .internal import Alias\ndef work(): pass\n')
    rows=candidates(wheel)['candidates']
    assert any(r['symbol']=='work' and r['status']=='UNCLASSIFIED' for r in rows)
    assert any(r['symbol']=='Alias' and r['kind']=='import_alias' for r in rows)
    assert any(r['kind']=='declaration_status' and r['status']=='REVIEW' for r in rows)
