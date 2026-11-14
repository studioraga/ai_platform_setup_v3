#!/usr/bin/env python3
"""Run inside clean consumer venv, from outside source tree. Offline deny-case contract."""
from pathlib import Path
from importlib import metadata
import portable_ai_governance as pkg
from portable_ai_governance.enterprise_freeze import assess_candidate_readiness, finalize_freeze

installed = metadata.version('portable-agentic-ai-governance')
assert pkg.__version__ == installed, (pkg.__version__, installed)
assert 'site-packages' in Path(pkg.__file__).resolve().parts, pkg.__file__
result = assess_candidate_readiness(
    m29_integrity=False,
    m29_receipt_valid=False,
    matrix={'all_requirements_evidenced': False},
    platform_ready=False,
    pentest_ready=False,
    organizational_ready=False,
    no_private_keys=True,
)
assert result['candidate_ready'] is False
assert result['blocking_gates']
assert result['gates']['no_private_keys_in_verifier_package'] is True
freeze = finalize_freeze(candidate_ready=False, node2_verified=False)
assert freeze['freeze_authorized'] is False
assert set(freeze['blocking_gates']) == {'candidate_ready', 'm30_node2_independent_verification'}
print('PASS: installed wheel metadata and module version match:', installed)
print('PASS: M30 candidate readiness rejects missing evidence')
print('PASS: M30 freeze rejects missing independent approval')
