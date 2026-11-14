#!/usr/bin/env python3
"""Fail-closed verification of the practice Qdrant Cosine point after restart."""
import argparse
import json
import math
from pathlib import Path


def validate(path: Path) -> None:
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data.get('status') == 'ok', f"Qdrant API status: {data.get('status')!r}"
    points = data.get('result')
    assert isinstance(points, list) and len(points) == 1, f"Unexpected points: {points!r}"
    point = points[0]
    assert point.get('id') == 1, f"Wrong point ID: {point.get('id')!r}"
    payload = point.get('payload') or {}
    assert payload.get('tenant_id') == 'practice', f"Wrong tenant: {payload!r}"
    assert payload.get('kind') == 'persistence', f"Wrong kind: {payload!r}"
    actual = point.get('vector')
    assert isinstance(actual, list) and len(actual) == 3, f"Unexpected vector: {actual!r}"
    assert all(isinstance(x, (int, float)) and math.isfinite(x) for x in actual), 'Nonfinite vector'
    original = (0.1, 0.2, 0.3)
    length = math.sqrt(sum(x * x for x in original))
    expected = [x / length for x in original]
    tolerance = 1e-5
    assert all(math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance) for a, b in zip(actual, expected)), (
        f'Normalized cosine vector mismatch: actual={actual!r} expected={expected!r}'
    )
    assert math.isclose(math.sqrt(sum(x * x for x in actual)), 1.0, abs_tol=tolerance), 'Vector norm differs from 1'
    print('PASS: Qdrant Cosine vector and payload persist after restart')
    print(f'Original: {list(original)}')
    print(f'Stored normalized vector: {actual}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--response', type=Path, default=Path('reports/qdrant_persistence.json'))
    args = parser.parse_args()
    validate(args.response)
