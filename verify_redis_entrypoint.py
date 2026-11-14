#!/usr/bin/env python3
"""Validate limited Redis startup patch without printing expanded Compose secrets."""
import json
import subprocess
import sys

p = subprocess.run(["docker", "compose", "config", "--format", "json"], capture_output=True, text=True)
if p.returncode:
    print("FAIL: docker compose config (validate credentials first)", file=sys.stderr)
    sys.exit(p.returncode)
config = json.loads(p.stdout)
assert config["name"] == "principal-ai-platform-practice"
redis = config["services"]["redis"]
assert redis["image"] == "redis:7.4.5-alpine"
assert redis["entrypoint"] == ["/bin/sh", "-ec"]
assert isinstance(redis["command"], list) and len(redis["command"]) == 1
script = redis["command"][0]
assert script.count("exec docker-entrypoint.sh redis-server") == 1
assert "su-exec" not in script
for part in ["cp /run/secrets/redis.acl /tmp/redis.acl", "chown redis:redis /tmp/redis.acl", "chmod 600 /tmp/redis.acl", "--appendonly yes", "--aclfile /tmp/redis.acl"]:
    assert part in script, part
assert config["services"]["postgres"]["image"] == "postgres:17.6"
assert config["services"]["qdrant"]["image"] == "qdrant/qdrant:v1.15.4"
print("PASS: Redis startup delegates to official image entrypoint; argv and other image identities intact")
