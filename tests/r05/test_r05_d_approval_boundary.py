"""R05-D negative acceptance boundary, independent of SDK imports."""

import json
import os
from pathlib import Path


def test_unapproved_behavioral_contract_remains_pending():
    root = Path(os.environ["R05_NEXT_REPORT"])
    report = json.loads(
        (root / "behavior/r05_d_contract_gaps.json").read_text()
    )

    assert report["status"] == "PENDING_NORMATIVE_CONTRACTS"
    assert report["approved"] is False
    assert len(report["items"]) >= 5


def test_simulation_does_not_authorize_sdk_api():
    root = Path(os.environ["SIM_ROOT"])
    manifest = json.loads(
        (root / "decisions/r05_simulated_manifest.json").read_text()
    )

    assert manifest["status"] == "SIMULATED_SCOPE_ONLY"
    assert manifest["public_api_approved"] is False
    assert manifest["r05_requirement_approved"] is False
