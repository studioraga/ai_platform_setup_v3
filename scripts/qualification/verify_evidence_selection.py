#!/usr/bin/env python3
"""Verify evidence selection and SHA-256 manifest coverage; not an engineering acceptance."""
from pathlib import Path
import argparse, hashlib, sys
p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--write',action='store_true');args=p.parse_args()
root=Path(args.root).resolve();sel=root/'reports/section1-closure/accepted_files.txt';manifest=root/'reports/section1-closure/evidence.sha256'
if not sel.is_file(): sys.exit('BLOCKED: no local evidence selection (expected on new host)')
names=[x.strip() for x in sel.read_text().splitlines() if x.strip() and not x.lstrip().startswith('#')]
if len(set(names))!=len(names):sys.exit('FAIL: duplicate selected paths')
records=[]
for n in names:
    rel=Path(n)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts or rel.parts[0]!='reports':sys.exit(f'FAIL: unsafe path {n}')
    target=(root/rel).resolve()
    if not target.is_relative_to(root/'reports') or not target.is_file():sys.exit(f'FAIL: missing/outside {n}')
    records.append(f'{hashlib.sha256(target.read_bytes()).hexdigest()}  {n}')
if args.write:
    manifest.parent.mkdir(parents=True,exist_ok=True);manifest.write_text('\n'.join(records)+'\n');print(f'WROTE {len(records)} hashed entries; review for secrets separately')
else:
    if not manifest.is_file():sys.exit('FAIL: manifest missing')
    original=manifest.read_text().splitlines()
    if original!=records:sys.exit(f'FAIL: selected {len(records)} != current manifest records {len(original)} or digest mismatch')
    print(f'PASS: all {len(records)} selected evidence files match manifest (not correctness acceptance)')
