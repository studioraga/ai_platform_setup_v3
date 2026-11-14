#!/usr/bin/env python3
"""Static SDK API inventory comparison. No package code is executed."""

import argparse
import ast
import json
from pathlib import Path
from zipfile import ZipFile


def inventory(wheel):
    result = {}

    with ZipFile(wheel) as z:
        for name in z.namelist():
            if not name.startswith("portable_ai_governance/"):
                continue
            if not name.endswith(".py"):
                continue

            tree = ast.parse(z.read(name), filename=name)

            functions = {}
            classes = []

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_"):
                        functions[node.name] = ast.unparse(node.args)

                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        classes.append(node.name)

            result[name] = {
                "functions": functions,
                "classes": sorted(classes),
            }

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    old = inventory(args.old)
    new = inventory(args.new)

    old_modules = set(old)
    new_modules = set(new)
    shared = old_modules & new_modules

    removed_functions = {}
    changed_signatures = {}

    for module in sorted(shared):
        old_functions = old[module]["functions"]
        new_functions = new[module]["functions"]

        removed = sorted(set(old_functions) - set(new_functions))

        if removed:
            removed_functions[module] = removed

        changed = {
            name: {
                "old": signature,
                "new": new_functions[name],
            }
            for name, signature in old_functions.items()
            if name in new_functions
            and signature != new_functions[name]
        }

        if changed:
            changed_signatures[module] = changed

    removed_classes = {}

    for module in sorted(shared):
        missing = sorted(
            set(old[module]["classes"]) - set(new[module]["classes"])
        )
        if missing:
            removed_classes[module] = missing

    report = {
        "old_module_count": len(old),
        "new_module_count": len(new),
        "removed_modules": sorted(old_modules - new_modules),
        "added_modules": sorted(new_modules - old_modules),
        "removed_top_level_functions": removed_functions,
        "changed_top_level_signatures": changed_signatures,
        "removed_top_level_classes": removed_classes,
        "limitations": (
            "Static inventory only; does not resolve re-exports, "
            "class-method signatures, runtime behavior or schemas."
        ),
    }

    Path(args.output).write_text(
        json.dumps(report, indent=2) + "\n"
    )

    print(json.dumps({
        key: value
        for key, value in report.items()
        if key not in ("added_modules",)
    }, indent=2))


if __name__ == "__main__":
    main()
