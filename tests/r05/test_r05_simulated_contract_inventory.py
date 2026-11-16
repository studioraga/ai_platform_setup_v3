"""R05-C observational contract verification.

Requires the R05 coverage JSON. Does not approve an API.
"""

import json
import os
from pathlib import Path

import pytest


def load_coverage():
    source = os.environ.get("R05_COVERAGE_REPORT")
    if not source:
        pytest.skip("R05_COVERAGE_REPORT not supplied")

    report = json.loads(Path(source).read_text())
    assert report["status"] == "SIMULATION_CHARACTERIZATION"
    assert report["qualified"] is False
    return report


def test_common_contract_inventory():
    report = load_coverage()
    assert report["candidate_count"] == 12
    assert len(report["records"]) == 12
    assert report["unresolved_import_paths"] == []


def test_no_normative_approval():
    report = load_coverage()
    assert report["public_api_approved"] is False
    assert all(
        r["normative_method_contract_approved"] is False
        for r in report["records"]
    )


@pytest.mark.parametrize("key", [
    "v029_importable",
    "v030_importable",
])
def test_import_coverage(key):
    report = load_coverage()
    assert all(r[key] is True for r in report["records"])


def test_observed_top_level_signatures():
    report = load_coverage()
    assert all(
        r["top_level_signature_equal"] is True
        for r in report["records"]
    )
