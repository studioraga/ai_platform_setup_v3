#!/usr/bin/env python3
"""Trace simulated common import paths to bounded method evidence.

No supported-public-API approval is inferred.
"""

import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--simulation", required=True)
    p.add_argument("--runtime-old", required=True)
    p.add_argument("--runtime-new", required=True)
    p.add_argument("--methods-old", required=True)
    p.add_argument("--methods-new", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    sim = load(a.simulation)
    old = load(a.runtime_old)
    new = load(a.runtime_new)
    mo = load(a.methods_old)
    mn = load(a.methods_new)

    if sim.get("status") != "SIMULATED_SCOPE_ONLY":
        raise SystemExit("FAIL: Not a simulation manifest")

    if sim.get("public_api_approved") is not False:
        raise SystemExit("FAIL: Unexpected public approval")

    expected = sim.get("supported_common_candidates", [])
    if len(expected) != 12 or len(set(expected)) != 12:
        raise SystemExit("FAIL: Common candidate inventory invalid")

    def imports_index(report):
        result = {}
        for entry in report["imports"]:
            key = f'{entry["module"]}.{entry["symbol"]}'
            if key in result:
                raise ValueError(f"Duplicate runtime import: {key}")
            result[key] = entry
        return result

    def classes_index(report):
        result = {}
        for entry in report["classes"]:
            key = entry["path"]
            if key in result:
                raise ValueError(f"Duplicate class: {key}")
            result[key] = entry
        return result

    a29 = imports_index(old)
    a30 = imports_index(new)
    m29 = classes_index(mo)
    m30 = classes_index(mn)

    rows = []
    blocking = []

    for path in sorted(expected):
        x = a29.get(path)
        y = a30.get(path)

        import_verified = (
            x is not None
            and y is not None
            and x.get("status") == "IMPORTABLE"
            and y.get("status") == "IMPORTABLE"
        )

        method_observed = path in m29 and path in m30

        row = {
            "import_path": path,
            "v029_importable": bool(
                x and x.get("status") == "IMPORTABLE"
            ),
            "v030_importable": bool(
                y and y.get("status") == "IMPORTABLE"
            ),
            "runtime_type_v029": x.get("type") if x else None,
            "runtime_type_v030": y.get("type") if y else None,
            "top_level_signature_equal": (
                x.get("signature") == y.get("signature")
                if x and y else None
            ),
            "method_inventory_both_versions": method_observed,
            "normative_method_contract_approved": False,
            "normative_behavior_approved": False,
            "classification": "OBSERVED_ONLY",
        }

        if not import_verified:
            blocking.append(path)

        rows.append(row)

    result = {
        "schema_version": 1,
        "status": "SIMULATION_CHARACTERIZATION",
        "qualified": False,
        "public_api_approved": False,
        "candidate_count": len(rows),
        "unresolved_import_paths": blocking,
        "records": rows,
    }

    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "candidates": len(rows),
        "unresolved_imports": len(blocking),
        "method_inventory_in_both": sum(
            r["method_inventory_both_versions"] for r in rows
        ),
        "qualified": False,
    }))

    if blocking:
        raise SystemExit("FAIL: Runtime import coverage incomplete")


if __name__ == "__main__":
    main()
