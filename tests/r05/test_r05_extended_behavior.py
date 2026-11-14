"""R05-C/D *observed kernel behavior* regression, common to both reviewed wheels.

NOT a maintainer-approved supported-public-API assertion. No external services.
Run with GOV_EXPECTED_VERSION under separately installed SDK venvs.
"""
from __future__ import annotations
from dataclasses import asdict, FrozenInstanceError, is_dataclass
from importlib import metadata
import json
import os
from pathlib import Path
import pytest
from portable_ai_governance.kernel.authorization import AuthorizationEngine, AuthorizationRule
from portable_ai_governance.kernel.budgets import BudgetExceeded,RunBudget
from portable_ai_governance.kernel.replay_cache import PersistentNonceCache,ReplayDetected
from portable_ai_governance.kernel.request_signing import sign_request,verify_request
from portable_ai_governance.kernel.state_machine import WorkflowState
from portable_ai_governance.kernel.types import AgentResult,PolicyDecision,Principal

SECRET = b'0123456789abcdef0123456789abcdef'

def test_distribution_boundary():
    assert metadata.version('portable-agentic-ai-governance')==os.environ['GOV_EXPECTED_VERSION']
    import portable_ai_governance
    assert 'site-packages' in Path(portable_ai_governance.__file__).resolve().parts

def test_class_method_signatures_and_binding():
    import inspect
    assert tuple(inspect.signature(AuthorizationEngine.authorize).parameters)==('self','principal','action','resource','resource_attributes')
    assert tuple(inspect.signature(RunBudget.consume_step).parameters)==('self',)
    assert tuple(inspect.signature(PersistentNonceCache.consume).parameters)==('self','nonce','now')
    assert tuple(inspect.signature(WorkflowState.transition).parameters)==('self','new_state')

def test_authorization_deny_overrides_and_abac():
    principal=Principal('subject',('reader',),{'tenant':'A'})
    engine=AuthorizationEngine((
       AuthorizationRule('read',('reader',),resource_prefix='/data/',principal_attributes={'tenant':('A',)}),
       AuthorizationRule('read',('reader',),resource_prefix='/data/private',effect='deny'),
    ))
    assert engine.authorize(principal,action='read',resource='/data/ordinary')[0] is True
    assert engine.authorize(principal,action='read',resource='/data/private/x')[0] is False
    assert engine.authorize(principal,action='write',resource='/data/ordinary')[0] is False
    assert engine.authorize(Principal('other',('reader',),{'tenant':'B'}),action='read',resource='/data/ordinary')[0] is False

def test_authorization_resource_attribute_and_missing_role():
    engine=AuthorizationEngine((AuthorizationRule('read',('reader',),resource_prefix='/resource',
            resource_attributes={'classification':('public',)}),))
    reader=Principal('p',('reader',),{})
    assert engine.authorize(reader,action='read',resource='/resource',resource_attributes={'classification':'public'})[0] is True
    assert engine.authorize(reader,action='read',resource='/resource',resource_attributes={'classification':'secret'})[0] is False
    assert engine.authorize(Principal('p',(),{}),action='read',resource='/resource',resource_attributes={'classification':'public'})[0] is False

def test_budget_limit_and_observed_post_increment_state():
    b=RunBudget(max_steps=1,max_tool_calls=1)
    b.consume_step();b.consume_tool_call()
    with pytest.raises(BudgetExceeded):b.consume_step()
    with pytest.raises(BudgetExceeded):b.consume_tool_call()
    assert (b.steps,b.tool_calls)==(2,2)  # current observed behavior, not a policy guarantee

def test_workflow_valid_and_invalid_transition():
    w=WorkflowState()
    with pytest.raises(ValueError):w.transition('COMPLETE')
    assert w.state=='START'
    w.transition('VALIDATE_REQUEST');w.transition('AUTHORIZE')
    assert w.state=='AUTHORIZE'
    with pytest.raises(ValueError):w.transition('COMPLETE')
    assert w.state=='AUTHORIZE'

def test_signing_cross_axis_rejections():
    request=sign_request(SECRET,method='post',path='/v1/run',body=b'abc',timestamp=1700000000,nonce='fixed')
    good=dict(method='POST',path='/v1/run',body=b'abc',now=1700000000)
    assert verify_request(SECRET,request,**good)
    assert not verify_request(SECRET,request,method='GET',path='/v1/run',body=b'abc',now=1700000000)
    assert not verify_request(SECRET,request,method='POST',path='/v1/other',body=b'abc',now=1700000000)
    assert not verify_request(SECRET,request,method='POST',path='/v1/run',body=b'abd',now=1700000000)
    assert not verify_request(b'Z'*32,request,**good)
    assert not verify_request(SECRET,request,**(good|{'now':1700000400}))
    with pytest.raises(ValueError):sign_request(b'x',method='POST',path='/',body=b'')

def test_replay_restart_and_bad_state(tmp_path):
    p=tmp_path/'replay.json'
    PersistentNonceCache(p).consume('fixed',now=100)
    with pytest.raises(ReplayDetected):PersistentNonceCache(p).consume('fixed',now=101)
    p.write_text('[]',encoding='utf-8')
    with pytest.raises(RuntimeError,match='fail closed'):PersistentNonceCache(p).consume('another',now=102)

def test_replay_ttl_window(tmp_path):
    p=tmp_path/'ttl.json';cache=PersistentNonceCache(p,ttl_sec=10)
    cache.consume('nonce',now=100)
    with pytest.raises(ReplayDetected):cache.consume('nonce',now=110)
    cache.consume('nonce',now=111)

def test_serialization_dataclass_shape_and_json_normalization():
    result=AgentResult(run_id='run',agent_id='agent',status='COMPLETE')
    assert is_dataclass(result)
    assert result.as_dict()==asdict(result)
    assert isinstance(result.as_dict()['proposed_actions'],tuple)
    normalized=json.loads(json.dumps(result.as_dict(),sort_keys=True))
    assert normalized['proposed_actions']==[]
    assert normalized['evidence_refs']==[]
    assert normalized['status']=='COMPLETE'
    decision=PolicyDecision(False,'C1','denied',True)
    assert asdict(decision)=={'allowed':False,'control_id':'C1','reason':'denied','approval_required':True}

def test_frozen_principal_and_decision():
    with pytest.raises(FrozenInstanceError):Principal('x',()).principal_id='other'
    with pytest.raises(FrozenInstanceError):PolicyDecision(False,'X','deny').allowed=True

def test_exception_inheritance():
    assert issubclass(BudgetExceeded,RuntimeError)
    assert issubclass(ReplayDetected,RuntimeError)
