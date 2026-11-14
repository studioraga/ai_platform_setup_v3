#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
{
 date -Is
 for command in az azd terraform kubectl helm gh code; do
   printf '\n-- %s --\n' "$command"
   if ! command -v "$command" >/dev/null 2>&1; then echo 'NOT_INSTALLED'; continue; fi
   case "$command" in
     az) az version;; azd) azd version;; terraform) terraform version;;
     kubectl) kubectl version --client;; helm) helm version --short;;
     gh) gh --version;; code) code --version;;
   esac
 done
} 2>&1 | tee reports/cloud_tools.txt
