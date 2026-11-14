#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
# Explicit allowlist. Private diagnostics and arbitrary recursive files must not enter a shareable manifest.
files=()
for name in base_packages.txt python_setup.txt python_requirements_resolved.txt python_dependency_check.txt python_tests.txt python_lint.txt react_setup.txt react_component_tests.txt playwright_tests.txt local_services_smoke.txt postgres_persistence.txt cloud_tools.txt terraform_offline.txt helm_validation.txt section1_acceptance.md form8825_verification.md governance_verification.md; do
  [[ -f "reports/$name" ]] && files+=("reports/$name")
done
[[ ${#files[@]} -gt 0 ]] || { echo 'No accepted evidence files to hash'; exit 2; }
sha256sum "${files[@]}" > reports/evidence.sha256
sha256sum -c reports/evidence.sha256
printf '%s\n' 'Manifest generated. Inspect logs for tokens/credentials before sharing; hashing is not redaction.'
