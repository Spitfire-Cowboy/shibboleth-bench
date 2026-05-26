from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'dataset' / 'items.jsonl'


def load_rows():
    return [json.loads(line) for line in DATASET.read_text(encoding='utf-8').splitlines() if line.strip()]


def test_dataset_ids_are_unique_and_ordered():
    rows = load_rows()
    ids = [row['id'] for row in rows]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_dataset_image_paths_exist():
    for row in load_rows():
        path = ROOT / row['image_path']
        assert path.exists(), row['image_path']


def test_dataset_has_multiple_categories():
    categories = {row['category'] for row in load_rows()}
    assert len(categories) >= 6
