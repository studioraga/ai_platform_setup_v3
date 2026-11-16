#!/usr/bin/env python3

import argparse
import importlib
import inspect
import json
from importlib.metadata import version
from pathlib import Path


def describe(value):
    result = {
        "runtime_type": type(value).__name__,
        "defined_module": getattr(value, "__module__", None),
        "qualname": getattr(value, "__qualname__", None),
    }

    if inspect.isclass(value) or inspect.isfunction(value):
        try:
            result["signature"] = str(inspect.signature(value))
        except (TypeError, ValueError):
            result["signature"] = None

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    actual = version("portable-agentic-ai-governance")
    if actual != args.expected_version:
        raise SystemExit(
            f"Installed version mismatch: {actual}"
        )

    module = importlib.import_module(
        "portable_ai_governance.kernel"
    )

    public_names = sorted(
        name for name in vars(module)
        if not name.startswith("_")
    )

    bindings = []

    for name in public_names:
        value = vars(module)[name]
        bindings.append({
            "name": name,
            **describe(value),
        })

    declared_all = vars(module).get("__all__")
    if isinstance(declared_all, (list, tuple)):
        declared_all = list(declared_all)
    else:
        declared_all = None

    report = {
        "schema_version": 1,
        "version": actual,
        "module": module.__name__,
        "declared_all": declared_all,
        "bindings": bindings,
        "qualified": False,
        "public_api_approved": False,
    }

    p = Path(args.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2) + "\n")

    print(json.dumps({
        "version": actual,
        "bindings": len(bindings),
        "qualified": False,
    }))


if __name__ == "__main__":
    main()
