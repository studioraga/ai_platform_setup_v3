#!/usr/bin/env bash
set -Eeuo pipefail
# ShellCheck cannot follow a host system file in the source archive.
# shellcheck source=/dev/null
. /etc/os-release
if [[ "${ID:-}" != ubuntu || "${VERSION_ID:-}" != '24.04' ]]; then echo 'Refusing: designed only for Ubuntu 24.04'; exit 2; fi
if [[ "$(id -u)" -eq 0 ]]; then echo 'Run as normal user with sudo privilege'; exit 2; fi
sudo apt-get update
sudo apt-get install -y ca-certificates curl wget gnupg git git-lfs jq unzip zip tar build-essential pkg-config make gcc g++ libssl-dev libffi-dev libpq-dev python3 python3-dev python3-venv python3-pip sqlite3 postgresql-client redis-tools shellcheck ripgrep fd-find graphviz openssl
# Do not overwrite system Python, Node, GPU or existing virtual environments.
echo 'Base dependencies installed. Follow README.md for uv/Node/Docker/cloud optional stages.'
