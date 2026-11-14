"""R05-B/C local non-SDK tests; no historical wheel dependencies."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'/'qualification'))
from classify_r05_public_candidates import build, test_imports as parse_test_imports  # noqa: E402
from probe_r05_runtime_exports import seed_imports  # noqa: E402


def r(module, symbol, kind='class', basis='nonprivate_top_level', detail=None):
    return {'module':module,'symbol':symbol,'kind':kind,'basis':basis,'detail':detail,'status':'UNCLASSIFIED'}


def test_triage_does_not_approve_seeded_symbols():
    key=('portable_ai_governance/kernel/types.py','Principal')
    a={'wheel_sha256':'a','candidates':[r(*key)]}
    b={'wheel_sha256':'b','candidates':[r(*key)]}
    x=build(a,b,{key})
    assert x['qualification_status']=='NOT_APPROVED'
    assert x['records'][0]['triage']=='SHARED_TEST_IMPORT_SEED'
    assert x['records'][0]['public_decision']=='UNREVIEWED'


def test_triage_reports_new_and_removed():
    old={'wheel_sha256':'a','candidates':[r('portable_ai_governance/a.py','gone')]}
    new={'wheel_sha256':'b','candidates':[r('portable_ai_governance/b.py','added')]}
    got={t['symbol']:t['triage'] for t in build(old,new,set())['records']}
    assert got['gone']=='ABSENT_V030_REVIEW_BREAKING'
    assert got['added']=='NEW_V030_CANDIDATE'


def test_triage_reports_declaration_delta():
    a={'wheel_sha256':'a','candidates':[r('portable_ai_governance/a.py','x',detail={'sig':'a'})]}
    b={'wheel_sha256':'b','candidates':[r('portable_ai_governance/a.py','x',detail={'sig':'b'})]}
    assert build(a,b,set())['records'][0]['triage']=='STATIC_DECLARATION_DELTA'


def test_import_parser_uses_explicit_from_imports_only(tmp_path):
    path=tmp_path/'test.py'
    path.write_text('from portable_ai_governance.kernel.types import Principal as P\nfrom unrelated import Thing\n')
    assert ('portable_ai_governance/kernel/types.py','Principal') in parse_test_imports(path)
    assert ('portable_ai_governance.kernel.types','Principal') in seed_imports(path)
    assert len(seed_imports(path)) == 1
