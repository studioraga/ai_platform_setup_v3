#!/usr/bin/env bash
set -Eeuo pipefail
printf '\nDocker context: '; docker context show || true
printf '\nEngine/service packages:\n'; dpkg-query -W docker-ce docker-ce-cli docker.io containerd.io 2>&1 || true
printf '\nSystemd state:\n'; systemctl is-active docker docker.socket containerd 2>&1 || true
printf '\nSocket:\n'; ls -l /var/run/docker.sock 2>&1 || true
if docker info >/dev/null 2>&1; then echo 'PASS: daemon accessible'; exit 0; fi
if systemctl list-unit-files docker.service --no-legend 2>/dev/null | grep -q '^docker.service'; then
 echo 'Docker service exists. For an intentionally stopped daemon, review logs and run: sudo systemctl start docker'
 echo 'Inspect: sudo journalctl -u docker -b --no-pager -n 100'
else
 echo 'Docker system service missing. Check rootless context before installing Engine.'
 echo 'Official install: https://docs.docker.com/engine/install/ubuntu/'
fi
if [[ -S /var/run/docker.sock ]]; then echo 'Socket exists but inaccessible: compare sudo docker info, id -nG, and docker context.'; fi
exit 1
