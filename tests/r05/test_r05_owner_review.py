import csv
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
def load(name):
    p=ROOT/'scripts'/'qualification'/name
    spec=importlib.util.spec_from_file_location(name[:-3],p)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod);return mod

def test_manifest_generation_on_fixture(tmp_path):
    gen=load('prepare_r05_owner_review.py')
    priority=tmp_path/'priority.csv'
    with priority.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['module','symbol','triage','v029_kind','v030_kind']);w.writeheader()
        for i in range(103):w.writerow({'module':'portable_ai_governance/kernel/types.py','symbol':f'Export{i}','triage':'SHARED_TEST_IMPORT_SEED','v029_kind':'class','v030_kind':'class'})
    paths=[]
    for label,version in [('029','0.29.0'),('030','0.30.0')]:
        inv=tmp_path/f'inv{label}.json';inv.write_text(json.dumps({'wheel_sha256':gen.EXPECTED[label]}))
        rt=tmp_path/f'rt{label}.json';rt.write_text(json.dumps({'version':version,'bindings':[{'name':'Principal','defined_module':'portable_ai_governance.kernel.types'},{'name':'field','defined_module':'dataclasses','signature':f'<MISSING at 0x{label}>'}]}))
        paths.extend([inv,rt])
    result=gen.build(priority,paths[0],paths[2],paths[1],paths[3],tmp_path/'out')
    assert len(result['records'])==103 and not result['qualified']
    assert result['star']['incidental_imported']==['field']
    assert result['star']['defined_in_sdk']==['Principal']
    validate=load('validate_r05_owner_review.py')
    assert len(validate.check(tmp_path/'out'/'r05_owner_review.csv'))==103
    with pytest.raises(ValueError,match='unresolved'):
        validate.check(tmp_path/'out'/'r05_owner_review.csv',True)

def test_validator_rejects_unsubstantiated_supported_symbol(tmp_path):
    v=load('validate_r05_owner_review.py')
    file=tmp_path/'review.csv'
    fields=['candidate_id','import_path','proposed_decision','decision_rationale','documentation_reference','owner_name','reviewer_name','review_status']
    with file.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for i in range(103):w.writerow({'candidate_id':str(i),'proposed_decision':'SUPPORTED_COMMON' if i==0 else 'UNREVIEWED'})
    with pytest.raises(ValueError,match='invalid review'):
        v.check(file)
