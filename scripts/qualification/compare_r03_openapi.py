#!/usr/bin/env python3
"""Conservative OpenAPI comparison for R03 contract research, not acceptance.

Only directly inspect local #/components/schemas refs. Unsupported constructs
are reported as REVIEW_REQUIRED rather than declared compatible.
"""
import argparse
import json
from pathlib import Path

HTTP = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}


def resolve(doc, schema):
    seen = set()
    while isinstance(schema, dict) and '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/components/schemas/') or ref in seen:
            return None
        seen.add(ref)
        name = ref.split('/')[-1].replace('~1', '/').replace('~0', '~')
        schema = doc.get('components', {}).get('schemas', {}).get(name)
    return schema if isinstance(schema, dict) else None


def properties(doc, schema):
    s = resolve(doc, schema)
    if not s:
        return None
    if any(x in s for x in ('allOf','anyOf','oneOf','not','discriminator')):
        return None
    return s


def compare(old, new):
    findings = []
    def add(severity, code, place, detail):
        findings.append({'severity': severity, 'code': code, 'location': place, 'detail': detail})
    if not str(old.get('openapi','')).startswith('3.') or not str(new.get('openapi','')).startswith('3.'):
        add('REVIEW_REQUIRED','VERSION_UNSUPPORTED','openapi','Expected OpenAPI 3.x documents')
    old_paths = old.get('paths', {})
    new_paths = new.get('paths', {})
    for path, operations in old_paths.items():
        if path not in new_paths:
            add('BREAKING','PATH_REMOVED',path,'Previously exposed path removed')
            continue
        for method in sorted(set(operations) & HTTP):
            place = method.upper() + ' ' + path
            if method not in new_paths[path]:
                add('BREAKING','OPERATION_REMOVED',place,'Previously exposed operation removed')
                continue
            op = operations[method]
            op2 = new_paths[path][method]
            old_params = {(p.get('in'),p.get('name')):p for p in op.get('parameters',[]) if isinstance(p,dict)}
            new_params = {(p.get('in'),p.get('name')):p for p in op2.get('parameters',[]) if isinstance(p,dict)}
            for key,param in new_params.items():
                if key not in old_params and param.get('required'):
                    add('BREAKING','NEW_REQUIRED_PARAMETER',place,str(key))
            for key in old_params:
                if key not in new_params:
                    add('REVIEW_REQUIRED','PARAMETER_REMOVED',place,str(key))
            if bool(op2.get('requestBody',{}).get('required')) and not bool(op.get('requestBody',{}).get('required')):
                add('BREAKING','BODY_NOW_REQUIRED',place,'Request body became mandatory')
            old_body=op.get('requestBody',{}).get('content',{}).get('application/json',{}).get('schema')
            new_body=op2.get('requestBody',{}).get('content',{}).get('application/json',{}).get('schema')
            if old_body and not new_body:
                add('BREAKING','REQUEST_JSON_REMOVED',place,'JSON request content removed')
            if old_body and new_body:
                a=properties(old,old_body)
                b=properties(new,new_body)
                if a is None or b is None:
                    add('REVIEW_REQUIRED','COMPLEX_REQUEST_SCHEMA',place,'Unresolved or composite request schema')
                else:
                    req_a=set(a.get('required',[]))
                    req_b=set(b.get('required',[]))
                    for field in sorted(req_b-req_a):
                        add('BREAKING','NEW_REQUIRED_BODY_FIELD',place+'.'+field,'Required body field introduced')
                    props_a=a.get('properties',{})
                    props_b=b.get('properties',{})
                    for field in sorted(set(props_a)-set(props_b)):
                        add('REVIEW_REQUIRED','BODY_FIELD_REMOVED',place+'.'+field,'Old input property removed')
                    for field in sorted(set(props_a)&set(props_b)):
                        x,y=props_a[field],props_b[field]
                        if x.get('type')!=y.get('type'):
                            add('BREAKING','BODY_FIELD_TYPE_CHANGED',place+'.'+field,f'{x.get("type")} -> {y.get("type")}')
                        for limit, narrowed in [('minimum',lambda x,y:y>x),('maximum',lambda x,y:y<x),('minLength',lambda x,y:y>x),('maxLength',lambda x,y:y<x)]:
                            if limit in y and (limit not in x or narrowed(x[limit],y[limit])):
                                add('BREAKING','BODY_CONSTRAINT_NARROWED',place+'.'+field,limit)
                        if 'enum' in x and 'enum' in y and not set(map(str,x['enum'])) <= set(map(str,y['enum'])):
                            add('BREAKING','BODY_ENUM_NARROWED',place+'.'+field,'Previously allowed values removed')
            old_res=op.get('responses',{})
            new_res=op2.get('responses',{})
            for code in old_res:
                if code not in new_res:
                    add('REVIEW_REQUIRED','RESPONSE_STATUS_REMOVED',place,str(code))
                elif old_res[code].get('content') != new_res[code].get('content'):
                    add('REVIEW_REQUIRED','RESPONSE_SCHEMA_CHANGED',place,str(code))
            if op.get('security')!=op2.get('security'):
                add('REVIEW_REQUIRED','SECURITY_CHANGED',place,'Operation security requirement changed')
    if old.get('security')!=new.get('security'):
        add('REVIEW_REQUIRED','GLOBAL_SECURITY_CHANGED','security','Global security requirements changed')
    findings.sort(key=lambda x:(x['severity'],x['code'],x['location']))
    return {'schema_version':1,'status':'PRELIMINARY_R03_ANALYSIS','qualified':False,
            'compatible':not any(x['severity']=='BREAKING' for x in findings) and not any(x['severity']=='REVIEW_REQUIRED' for x in findings),
            'breaking_count':sum(x['severity']=='BREAKING' for x in findings),
            'review_required_count':sum(x['severity']=='REVIEW_REQUIRED' for x in findings), 'findings':findings,
            'limitations':['Only selected OpenAPI 3.x surface compared', 'No full JSON Schema composition/ref or security equivalence proof', 'No deployed server, generated client or auth-negative evidence']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--old',required=True)
    p.add_argument('--new',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    old=json.loads(Path(a.old).read_text()); new=json.loads(Path(a.new).read_text())
    result=compare(old,new)
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','breaking_count','review_required_count','compatible','qualified')}))
    if result['breaking_count'] or result['review_required_count']:
        raise SystemExit(2)
if __name__=='__main__': main()
