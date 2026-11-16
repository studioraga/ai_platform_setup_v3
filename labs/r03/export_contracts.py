"""Export deterministic, synthetic OpenAPI schemas for comparison."""
import argparse
import importlib.util
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--out', required=True)
a = p.parse_args()
source = Path(__file__).resolve().parent / 'versioned_contract_lab.py'
spec = importlib.util.spec_from_file_location('r03_fixture_app', source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
for variant in ('v1', 'v2-compatible', 'v2-breaking'):
    path = out / f'{variant}.json'
    path.write_text(json.dumps(mod.make_app(variant).openapi(), indent=2, sort_keys=True) + '\n')
    print(path)
