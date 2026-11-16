"""Development-only import checks. Not public API approval."""

import importlib
import json
import os
from importlib.metadata import version
from pathlib import Path

import pytest

manifest_path = os.environ.get("R05_SIMULATION_MANIFEST")

if not manifest_path:
    raise RuntimeError("R05_SIMULATION_MANIFEST is required")

manifest = json.loads(Path(manifest_path).read_text())

assert manifest["status"] == "SIMULATED_SCOPE_ONLY"
assert manifest["public_api_approved"] is False
assert manifest["owner_approved"] is False

paths = manifest["supported_common_candidates"]
assert len(paths) == 12
assert len(set(paths)) == 12


def test_installed_distribution_version():
    assert version("portable-agentic-ai-governance") == (
        os.environ["GOV_EXPECTED_VERSION"]
    )


@pytest.mark.parametrize("import_path", paths)
def test_provisional_common_import(import_path):
    module_path, separator, symbol = import_path.rpartition(".")

    assert separator
    assert module_path
    assert symbol

    module = importlib.import_module(module_path)

    assert symbol in vars(module)
    assert vars(module)[symbol] is not None
