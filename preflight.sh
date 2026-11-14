#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$ROOT/reports}"; mkdir -p "$OUT"
REPORT="$OUT/preflight_$(date -u +%Y%m%dT%H%M%SZ).txt"
{
 echo 'Principal AI Platform v3.1 — read-only host audit'; date -Is
 grep -E '^(PRETTY_NAME|ID|VERSION_ID|VERSION_CODENAME)=' /etc/os-release || true
 uname -a; lscpu | grep -E 'Architecture:|Model name:|CPU\(s\):' || true
 free -h; df -h "$HOME"
 echo '-- Tool versions, and paths --'
 for item in 'git --version' 'python3 --version' 'uv --version' 'node --version' 'npm --version' 'docker --version' 'docker compose version' 'psql --version' 'redis-cli --version' 'az version' 'azd version' 'terraform version' 'gh --version' 'code --version' 'kubectl version --client' 'helm version --short' 'ruff --version' 'pytest --version'; do
   read -r -a argv <<< "$item"
   tool="${argv[0]}"
   echo "[$item]"
   if command -v "$tool" >/dev/null 2>&1; then
      command -v "$tool"
      timeout 10 "${argv[@]}" 2>&1 | head -8 || true
   else echo NOT_INSTALLED; fi
 done
 echo '-- Actual practice and existing service ports --'
 ss -ltn 2>/dev/null | grep -E ':(5432|6379|6333|6334|15432|16379|16333|4317|4318|8000|8080|8082|3000|5173|16686)\b' || true
 echo '-- Docker diagnosis --'
 command -v dockerd || true
 dpkg-query -W -f='${binary:Package} ${Version} ${Status}\n' docker-ce docker-ce-cli docker.io containerd.io 2>/dev/null || true
 systemctl is-enabled docker.service docker.socket containerd.service 2>&1 || true
 systemctl is-active docker.service docker.socket containerd.service 2>&1 || true
 systemctl status docker.service --no-pager -l 2>&1 | head -22 || true
 ls -l /var/run/docker.sock "${XDG_RUNTIME_DIR:-/nonexistent}/docker.sock" 2>&1 || true
 echo 'DOCKER_HOST set?'; [[ -n "${DOCKER_HOST:-}" ]] && echo yes || echo no
 echo 'Docker context:'; timeout 8 docker context show 2>&1 || true
 echo 'Docker API:'; timeout 8 docker info --format 'Server={{.ServerVersion}}' 2>&1 || true
 echo '-- git identity existence only --'
 git config --global user.name >/dev/null && echo 'name configured' || echo 'name missing'
 git config --global user.email >/dev/null && echo 'email configured' || echo 'email missing'
 echo 'No changes made to host.'
} | tee "$REPORT"
echo "Report: $REPORT"
