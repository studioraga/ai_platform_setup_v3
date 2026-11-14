from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[2]/'scripts/qualification/compare_r05_method_contracts.py'
spec=importlib.util.spec_from_file_location('r05methodcmp',SCRIPT)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def report(version,methods=None):
    return {'schema_version':1,'distribution_version':version,'qualified':False,'public_api_approved':False,
            'classes':[{'path':'portable_ai_governance.kernel.Foo',
                        'constructor_signature':'(x)', 'declared_methods':methods or [], 'dataclass_fields':[]}]}

def test_identical_fixture(tmp_path):
    a=tmp_path/'a.json';b=tmp_path/'b.json'
    a.write_text(json.dumps(report('0.29.0')));b.write_text(json.dumps(report('0.30.0')))
    old,_=mod.load(a,'0.29.0');new,_=mod.load(b,'0.30.0')
    assert mod.compare(old,new)==[]

def test_method_delta_detected(tmp_path):
    a=tmp_path/'a.json';b=tmp_path/'b.json'
    a.write_text(json.dumps(report('0.29.0')))
    b.write_text(json.dumps(report('0.30.0',[{'name':'run','signature':'(self, x)'}])))
    old,_=mod.load(a,'0.29.0');new,_=mod.load(b,'0.30.0')
    assert mod.compare(old,new)[0]['kind']=='DECLARED_METHODS_DELTA'

def test_invalid_version_rejected(tmp_path):
    p=tmp_path/'input.json';p.write_text(json.dumps(report('0.30.0')))
    with pytest.raises(ValueError,match='Invalid report'):mod.load(p,'0.29.0')

def test_duplicate_class_rejected(tmp_path):
    r=report('0.29.0');r['classes'].append(dict(r['classes'][0]));p=tmp_path/'r.json';p.write_text(json.dumps(r))
    with pytest.raises(ValueError,match='Duplicate'):mod.load(p,'0.29.0')
