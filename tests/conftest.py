import csv
import os.path
import tempfile
from pathlib import Path
from typing import Any

import pytest  # type: ignore

from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, JSONStorage


DATA_DIR = Path(__file__).parent / 'data'


def load_csv_records(filename: str) -> list[dict[str, str]]:
    """Helper function to load test records from tests/data/<filename>."""
    csv_path = DATA_DIR / filename
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV data file not found: {csv_path}")
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture(params=['memory', 'json'])
def db(request, tmp_path: Path):
    if request.param == 'json':
        db_ = TinyDB(tmp_path / 'test.db', storage=JSONStorage)
    else:
        db_ = TinyDB(storage=MemoryStorage)

    db_.drop_tables()
    db_.insert_multiple({'int': 1, 'char': c} for c in 'abc')

    yield db_


@pytest.fixture
def storage():
    return CachingMiddleware(MemoryStorage)()
