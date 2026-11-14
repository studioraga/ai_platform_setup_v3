#!/usr/bin/env python3
"""Read-only runtime reflection of reviewed, explicit R05 class paths.

Run in each isolated installed wheel interpreter. Does not invoke SDK methods.
Static/class descriptors are read from class __dict__, without calling them.
"""
from __future__ import annotations
import argparse
from dataclasses import fields, is_dataclass, MISSING
import hashlib
from importlib import import_module, metadata
import inspect
import json
from pathlib import Path

DISTRIBUTION = 'portable-agentic-ai-governance'
REVIEWED_CLASSES = (
    'portable_ai_governance.kernel.authorization.AuthorizationEngine',
    'portable_ai_governance.kernel.authorization.AuthorizationRule',
    'portable_ai_governance.kernel.budgets.RunBudget',
    'portable_ai_governance.kernel.replay_cache.PersistentNonceCache',
    'portable_ai_governance.kernel.state_machine.WorkflowState',
    'portable_ai_governance.kernel.types.AgentResult',
    'portable_ai_governance.kernel.types.PolicyDecision',
    'portable_ai_governance.kernel.types.Principal',
)

def signature(obj):
    try:
        return str(inspect.signature(obj))
    except (ValueError, TypeError):
        return None

def inspect_class(path):
    module_name, name = path.rsplit('.', 1)
    cls = vars(import_module(module_name))[name]
    if not inspect.isclass(cls):
        raise TypeError(f'Expected class: {path}')
    methods = []
    for method_name, raw in sorted(vars(cls).items()):
        if method_name.startswith('_') and method_name != '__init__':
            continue
        if isinstance(raw, staticmethod):
            kind, function = 'staticmethod', raw.__func__
        elif isinstance(raw, classmethod):
            kind, function = 'classmethod', raw.__func__
        elif inspect.isfunction(raw):
            kind, function = 'instance_method', raw
        else:
            continue
        methods.append({'name':method_name,'kind':kind,'signature':signature(function),
                        'coroutine':inspect.iscoroutinefunction(function)})
    datafields = []
    if is_dataclass(cls):
        for field in fields(cls):
            datafields.append({'name':field.name, 'type':str(field.type),
                               'required':field.default is MISSING and field.default_factory is MISSING,
                               'has_default_factory':field.default_factory is not MISSING,
                               'default_repr':repr(field.default) if field.default is not MISSING else None})
    return {'path':path,'constructor_signature':signature(cls),'declared_methods':methods,
            'dataclass_fields':datafields,
            'inherited_methods_unresolved': True,
            'public_api_approved':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-version', choices=['0.29.0','0.30.0'], required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    installed=metadata.version(DISTRIBUTION)
    if installed != a.expected_version:
        p.error(f'Distribution mismatch: expected {a.expected_version}, got {installed}')
    pkg=import_module('portable_ai_governance')
    origin=Path(pkg.__file__).resolve()
    if 'site-packages' not in origin.parts:
        p.error(f'Not a site-packages SDK import: {origin}')
    report={'schema_version':1,'phase':'R05-C method discovery',
            'distribution_version':installed,'package_location':str(origin),
            'classes':[inspect_class(path) for path in REVIEWED_CLASSES],
            'qualified':False,'public_api_approved':False,
            'limitations':['Only explicit seeded classes, not comprehensive public scope',
                           'Method invocation and inherited descriptors not evaluated',
                           'Distribution version and path do not establish wheel hash provenance']}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'version':installed,'classes':len(report['classes']),'qualified':False}))
if __name__=='__main__': main()
