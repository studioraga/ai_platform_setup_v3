#!/usr/bin/env python3
"""Modify a COPY of Governance source only; never the active repository."""
import argparse
import pathlib
import re
import tomllib

p = argparse.ArgumentParser()
p.add_argument('--snapshot', type=pathlib.Path, required=True)
p.add_argument('--active-repository', type=pathlib.Path, required=True)
a = p.parse_args()
root = a.snapshot.resolve(strict=True)
active = a.active_repository.resolve(strict=True)
assert root != active and not root.is_relative_to(active) and not active.is_relative_to(root), 'Refusing to change live repository'
project_file = root / 'pyproject.toml'
init_file = root / 'src/portable_ai_governance/__init__.py'
readme = root / 'README.md'
assert all(x.is_file() for x in (project_file, init_file, readme)), 'Snapshot missing required metadata source/readme'
raw = project_file.read_text()
data = tomllib.loads(raw)
project = data['project']
version = project['version']
assert re.fullmatch(r'\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)?', version), 'Unexpected version'
if 'readme' not in project:
    # Insert at start of project table, avoiding manipulation of any later section.
    assert raw.count('[project]') == 1, 'Unexpected [project] table count'
    raw = raw.replace('[project]', '[project]\nreadme = "README.md"', 1)
    tomllib.loads(raw)
    project_file.write_text(raw)
else:
    print('readme already declared:', project['readme'])
source = init_file.read_text()
regex = r'(?m)^__version__\s*=\s*[\'\"]([^\'\"]+)[\'\"]\s*$'
match = re.search(regex, source)
assert match, 'No simple __version__ assignment; manual review required'
old = match.group(1)
source = re.sub(regex, f'__version__ = "{version}"', source, count=1)
init_file.write_text(source)
print(f'PASS: Snapshot only; project version {version}, module version {old} -> {version}; README metadata present')
