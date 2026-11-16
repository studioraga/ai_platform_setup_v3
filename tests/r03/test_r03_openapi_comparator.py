import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts' / 'qualification' / 'compare_r03_openapi.py'
spec=importlib.util.spec_from_file_location('r03_comparator',SCRIPT)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def doc(request_required=False, maximum=1000):
    return {'openapi':'3.1.0','paths':{'/v1/double':{'post':{'requestBody':{'required':True,'content':{'application/json':{'schema':{'$ref':'#/components/schemas/DoubleRequest'}}}},'responses':{'200':{'description':'OK'}}}}},'components':{'schemas':{'DoubleRequest':{'type':'object','properties':{'value':{'type':'integer','minimum':0,'maximum':maximum},**({'label':{'type':'string'}} if request_required else {})},'required':['value']+(['label'] if request_required else [])}}}}

def test_identical():
    result=mod.compare(doc(),doc());assert result['breaking_count']==0 and result['review_required_count']==0 and result['qualified'] is False

def test_added_optional_field_not_breaking():
    d=doc();n=doc();n['components']['schemas']['DoubleRequest']['properties']['memo']={'type':'string'}
    assert mod.compare(d,n)['breaking_count']==0

def test_added_required_field_detected():
    result=mod.compare(doc(),doc(request_required=True));assert any(x['code']=='NEW_REQUIRED_BODY_FIELD' for x in result['findings'])

def test_narrowed_maximum_detected():
    result=mod.compare(doc(),doc(maximum=100));assert any(x['code']=='BODY_CONSTRAINT_NARROWED' for x in result['findings'])

def test_removed_path_detected():
    n=doc();n['paths']={}
    assert any(x['code']=='PATH_REMOVED' for x in mod.compare(doc(),n)['findings'])

def test_security_delta_requires_review():
    n=doc();n['security']=[{'BearerAuth':[]}]
    assert mod.compare(doc(),n)['review_required_count']>=1

def test_unknown_composite_requires_review():
    n=doc();n['components']['schemas']['DoubleRequest']={'allOf':[{'type':'object'}]}
    assert mod.compare(doc(),n)['review_required_count']>=1
