#!/usr/bin/env python3
"""Verify docker compose config --format json output without printing secrets."""
import json
import subprocess
import sys

p = subprocess.run(['docker','compose','config','--format','json'],capture_output=True,text=True)
if p.returncode:
    print('FAIL: docker compose config. Run ./validate_env.sh first.', file=sys.stderr)
    sys.exit(p.returncode)
cfg=json.loads(p.stdout)
assert cfg['name']=='principal-ai-platform-practice','Unexpected compose project'
s=cfg['services']['redis']
assert s['entrypoint']==['/bin/sh','-ec'],f'Incorrect Redis entrypoint: {s["entrypoint"]!r}'
cmd=s['command']
assert isinstance(cmd,list) and len(cmd)==1, 'Redis startup command must be ONE argv element for sh -c'
script=cmd[0]
for token in ['cp /run/secrets/redis.acl', 'chown redis:redis', 'chmod 600', 'exec su-exec redis redis-server', '--appendonly yes', '--aclfile /tmp/redis.acl']:
    assert token in script, f'Expected startup component missing: {token}'
assert cfg['services']['postgres']['image']=='postgres:17.6'
assert cfg['services']['qdrant']['image']=='qdrant/qdrant:v1.15.4'
print('PASS: isolated Compose project, Redis sh -ec argv construction and unchanged image identities')
