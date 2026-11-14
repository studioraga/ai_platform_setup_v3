#!/usr/bin/env python3
"""Safely reconcile existing Node1 R05 evidence without granting full R05 acceptance."""
from pathlib import Path
import argparse, shutil
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));args=p.parse_args()
root=args.root.resolve();r=root/'reports/r05-sdk-compatibility'
old=r/'v029_shared_contract.txt';new=r/'v030_shared_contract.txt';review=r/'compatibility_review.md'
for f in (old,new,review):
    if not f.is_file():raise SystemExit(f'BLOCKED: missing {f}')
for f in (old,new):
    value=f.read_text()
    if '7 passed' not in value or 'failed' in value or 'error' in value:
        raise SystemExit(f'BLOCKED: contract evidence does not prove seven passing tests: {f}')
text=review.read_text()
if 'PENDING NODE1 VERIFICATION' not in text and '7 passed' in text:
    print('Already reconciled; no change');raise SystemExit(0)
shutil.copy2(review,review.with_name(review.name+'.before-reconciliation'))
text=text.replace('v0.29.0 result: PENDING NODE1 VERIFICATION','v0.29.0 result: 7 passed (Node1 consumer contract; exit 0 in supplied execution log)')
text=text.replace('v0.30.0 result: PENDING NODE1 VERIFICATION','v0.30.0 result: 7 passed (Node1 consumer contract; exit 0 in supplied execution log)')
text=text.replace('Shared consumer compatibility: PENDING NODE1 VERIFICATION','Shared consumer compatibility: PASS for seven tested shared contracts only')
review.write_text(text)
print('Reconciled R05 limited shared-contract evidence; full R05 and production release remain pending')
