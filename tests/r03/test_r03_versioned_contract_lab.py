"""Synthetic API compatibility, not an approved R03 server contract."""
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

MODULE = Path(__file__).resolve().parents[2] / 'labs/r03/versioned_contract_lab.py'
spec = importlib.util.spec_from_file_location('r03_contract_fixture', MODULE)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

@pytest.mark.parametrize('version', ['v1', 'v2-compatible', 'v2-breaking'])
def test_health(version):
    assert TestClient(lab.make_app(version)).get('/health').json() == {'status': 'ok'}

@pytest.mark.parametrize('value', [0, 1, 100, 101, 1000])
def test_old_consumer_survives_optional_request_field(value):
    payload = {'value': value}
    old = TestClient(lab.make_app('v1')).post('/v1/double', json=payload)
    new = TestClient(lab.make_app('v2-compatible')).post('/v1/double', json=payload)
    assert old.status_code == new.status_code == 200
    assert old.json() == new.json() == {'result': value * 2}

@pytest.mark.parametrize('value', [-1, 1001, 'garbage'])
def test_both_contracts_reject_invalid_payload(value):
    for version in ('v1', 'v2-compatible'):
        assert TestClient(lab.make_app(version)).post('/v1/double', json={'value': value}).status_code == 422

def test_breaking_required_field_rejects_old_consumer():
    old = TestClient(lab.make_app('v1')).post('/v1/double', json={'value': 20})
    changed = TestClient(lab.make_app('v2-breaking')).post('/v1/double', json={'value': 20})
    assert old.status_code == 200
    assert changed.status_code == 422

def test_breaking_range_rejects_previously_valid_value():
    old = TestClient(lab.make_app('v1')).post('/v1/double', json={'value': 101})
    changed = TestClient(lab.make_app('v2-breaking')).post('/v1/double', json={'value': 101, 'memo': 'valid'})
    assert old.status_code == 200
    assert changed.status_code == 422

def test_openapi_has_disjoint_request_schema_names():
    for version, name in [('v1', 'V1DoubleRequest'), ('v2-compatible', 'V2CompatibleRequest'), ('v2-breaking', 'V2BreakingRequest')]:
        schema = lab.make_app(version).openapi()
        assert name in schema['components']['schemas']
        assert schema['openapi'].startswith('3.')
