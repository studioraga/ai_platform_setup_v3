#!/usr/bin/env python3
"""Offline, side-effect-free wheel AST contract inventory. Candidate findings need review.

No imports or execution of the SDK. Do not use this report as a release decision.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

PKG = 'portable_ai_governance/'

def show(node):
    return ast.unparse(node) if node is not None else None

def signature(fn):
    a = fn.args
    pos = a.posonlyargs + a.args
    dstart = len(pos) - len(a.defaults)
    args = []
    for i, arg in enumerate(pos):
        args.append({'name':arg.arg,'kind':'posonly' if i < len(a.posonlyargs) else 'poskw',
                     'annotation':show(arg.annotation), 'default':show(a.defaults[i-dstart]) if i >= dstart else None})
    if a.vararg:
        args.append({'name':a.vararg.arg,'kind':'vararg','annotation':show(a.vararg.annotation),'default':None})
    for arg, default in zip(a.kwonlyargs,a.kw_defaults):
        args.append({'name':arg.arg,'kind':'kwonly','annotation':show(arg.annotation),'default':show(default)})
    if a.kwarg:
        args.append({'name':a.kwarg.arg,'kind':'kwarg','annotation':show(a.kwarg.annotation),'default':None})
    return {'async':isinstance(fn,ast.AsyncFunctionDef),'parameters':args,'returns':show(fn.returns)}

def public_imports(tree):
    imports = {}
    star = []
    declared_all = None
    for node in tree.body:
        if isinstance(node,ast.ImportFrom):
            for alias in node.names:
                if alias.name=='*':
                    star.append({'module':node.module,'level':node.level})
                else:
                    exposed=alias.asname or alias.name
                    if not exposed.startswith('_'):
                        imports[exposed]={'source':node.module,'level':node.level,'name':alias.name}
        elif isinstance(node,ast.Import):
            for alias in node.names:
                exposed=alias.asname or alias.name.split('.')[0]
                if not exposed.startswith('_'):
                    imports[exposed]={'source':alias.name,'level':0,'name':None}
        elif isinstance(node,(ast.Assign,ast.AnnAssign)):
            targets = node.targets if isinstance(node,ast.Assign) else [node.target]
            if any(isinstance(t,ast.Name) and t.id=='__all__' for t in targets):
                try:
                    value=ast.literal_eval(node.value)
                    if isinstance(value,(list,tuple)) and all(isinstance(v,str) for v in value):
                        declared_all=value
                except (ValueError, TypeError, SyntaxError):
                    pass
    return imports,star,declared_all

def inventory(wheel):
    out={}
    with zipfile.ZipFile(wheel) as z:
        for name in sorted(z.namelist()):
            if not (name.startswith(PKG) and name.endswith('.py')):continue
            if '..' in Path(name).parts:raise ValueError('unsafe wheel path')
            tree=ast.parse(z.read(name),filename=name)
            imports,star,all_=public_imports(tree)
            classes={};functions={};constants={}
            for node in tree.body:
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and not node.name.startswith('_'):
                    functions[node.name]=signature(node)
                elif isinstance(node,ast.ClassDef) and not node.name.startswith('_'):
                    methods={}; fields={}; decorators=[show(d) for d in node.decorator_list]
                    for child in node.body:
                        if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
                            # Include dunder methods (e.g. __init__) as public contract candidates.
                            if not child.name.startswith('_') or (child.name.startswith('__') and child.name.endswith('__')):
                                methods[child.name]={'signature':signature(child),'decorators':[show(d) for d in child.decorator_list]}
                        elif isinstance(child,ast.AnnAssign) and isinstance(child.target,ast.Name):
                            if not child.target.id.startswith('_'):
                                fields[child.target.id]={'annotation':show(child.annotation),'default':show(child.value)}
                    classes[node.name]={'methods':methods,'annotated_fields':fields,'decorators':decorators,'bases':[show(b) for b in node.bases]}
                elif isinstance(node,(ast.Assign,ast.AnnAssign)):
                    targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                    for target in targets:
                        if isinstance(target,ast.Name) and not target.id.startswith('_'):
                            constants[target.id]={'annotation':show(node.annotation) if isinstance(node,ast.AnnAssign) else None,
                                                  'value_type':type(node.value).__name__ if node.value else None}
            out[name]={'functions':functions,'classes':classes,'imports':imports,'star_imports':star,
                       '__all__':all_,'constants':constants}
    return out

def compare(old,new):
    diffs=[]
    for mod in sorted(set(old)|set(new)):
        if mod not in old:
            diffs.append({'module':mod,'category':'module_added','severity':'ADDITIVE'});continue
        if mod not in new:
            diffs.append({'module':mod,'category':'module_removed','severity':'REVIEW_BREAKING'});continue
        for part in ('functions','classes','imports','star_imports','__all__','constants'):
            a=old[mod][part]; b=new[mod][part]
            if isinstance(a,dict):
                for key in sorted(set(a)|set(b)):
                    if key not in a:
                        diffs.append({'module':mod,'category':part+'_added','symbol':key,'severity':'ADDITIVE'})
                    elif key not in b:
                        diffs.append({'module':mod,'category':part+'_removed','symbol':key,'severity':'REVIEW_BREAKING'})
                    elif a[key]!=b[key]:
                        if part=='classes':
                            for member_type in ('methods','annotated_fields'):
                                am=a[key][member_type];bm=b[key][member_type]
                                for member in sorted(set(am)|set(bm)):
                                    if member not in am:
                                        diffs.append({'module':mod,'category':member_type+'_added','symbol':key+'.'+member,'severity':'ADDITIVE'})
                                    elif member not in bm:
                                        diffs.append({'module':mod,'category':member_type+'_removed','symbol':key+'.'+member,'severity':'REVIEW_BREAKING'})
                                    elif am[member]!=bm[member]:
                                        diffs.append({'module':mod,'category':member_type+'_changed','symbol':key+'.'+member,'severity':'REVIEW_REQUIRED','old':am[member],'new':bm[member]})
                            if any(a[key][k]!=b[key][k] for k in ('decorators','bases')):
                                diffs.append({'module':mod,'category':'class_declaration_changed','symbol':key,'severity':'REVIEW_REQUIRED'})
                        else:
                            diffs.append({'module':mod,'category':part+'_changed','symbol':key,'severity':'REVIEW_REQUIRED','old':a[key],'new':b[key]})
            elif a!=b:
                diffs.append({'module':mod,'category':part+'_changed','severity':'REVIEW_REQUIRED','old':a,'new':b})
    return diffs

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--old',required=True,type=Path);p.add_argument('--new',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    for x in (args.old,args.new):
        if not x.is_file() or not zipfile.is_zipfile(x):p.error('missing or invalid wheel: '+str(x))
    old=inventory(args.old);new=inventory(args.new);changes=compare(old,new)
    report={'phase':'R05-A discovery','qualified':False,'old_sha256':hashlib.sha256(args.old.read_bytes()).hexdigest(),
            'new_sha256':hashlib.sha256(args.new.read_bytes()).hexdigest(),
            'old_modules':len(old),'new_modules':len(new),'changes':changes,
            'counts':{kind:sum(c['severity']==kind for c in changes) for kind in ('ADDITIVE','REVIEW_REQUIRED','REVIEW_BREAKING')},
            'limitations':['AST inventory; does not import SDK or resolve star imports at runtime',
                           'Public designation is provisional; inspect documented exports and __all__',
                           'No inference of behavior or supported SemVer from syntax alone',
                           'All findings need independent manual disposition']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'report':str(args.output),'old_modules':len(old),'new_modules':len(new),'counts':report['counts']}))
if __name__=='__main__':main()
