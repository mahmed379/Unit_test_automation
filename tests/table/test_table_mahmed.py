"""
Unit tests for Table class in tinydb.table
Author: Mohammad Ahmed (mahmed379 / mohammadahmed41235@gmail.com)
Covers: insert, get, search, update, truncate, query cache, and CSV data-driven tests.
"""

from pathlib import Path
import pytest

from tinydb import Query
from tinydb.storages import MemoryStorage
from tinydb.table import Table, Document
from tests.conftest import load_csv_records


@pytest.fixture
def table() -> Table:
    """Fixture providing a fresh in-memory Table instance for each test."""
    storage = MemoryStorage()
    return Table(storage=storage, name='test_table')


# ---------------------------------------------------------------------------
# 1. Tests for Table.insert() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(1)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_insert_valid_document_ecp(table: Table):
    """EC1: Valid standard dictionary insertion returns starting doc_id 1."""
    doc = {"name": "Alice", "role": "Engineer"}
    doc_id = table.insert(doc)
    assert doc_id == 1
    assert len(table) == 1
    retrieved = table.get(doc_id=doc_id)
    assert retrieved is not None
    assert retrieved["name"] == "Alice"
    assert retrieved["role"] == "Engineer"


@pytest.mark.order(2)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_empty_mapping_bva(table: Table):
    """EC2 / BVA: Inserting an empty dictionary is valid and allocates ID 1."""
    doc_id = table.insert({})
    assert doc_id == 1
    assert len(table) == 1
    stored = table.get(doc_id=1)
    assert stored == {}
    assert stored.doc_id == 1


@pytest.mark.order(3)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_sequential_ids_bva(table: Table):
    """BVA1/BVA2: Consecutive inserts allocate monotonically increasing IDs."""
    id1 = table.insert({"item": "A"})
    id2 = table.insert({"item": "B"})
    id3 = table.insert({"item": "C"})
    assert id1 == 1
    assert id2 == 2
    assert id3 == 3
    assert len(table) == 3


@pytest.mark.order(4)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_with_explicit_document_id(table: Table):
    """EC3 / BVA3: Inserting Document with explicit large ID sets next ID."""
    doc = Document({"service": "auth"}, doc_id=500)
    doc_id = table.insert(doc)
    assert doc_id == 500
    # Next auto insert should allocate 501
    next_id = table.insert({"service": "billing"})
    assert next_id == 501


@pytest.mark.order(5)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
@pytest.mark.parametrize("invalid_input", [
    "not-a-dict",
    12345,
    ["item1", "item2"],
    None,
    3.14159,
])
def test_insert_invalid_non_mapping_type(table: Table, invalid_input):
    """EC4: Inserting non-mapping objects must raise ValueError."""
    with pytest.raises(ValueError, match="Document is not a Mapping"):
        table.insert(invalid_input)


@pytest.mark.order(6)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_duplicate_explicit_doc_id(table: Table):
    """EC5: Inserting Document with an existing doc_id raises ValueError."""
    table.insert(Document({"entry": 1}, doc_id=42))
    with pytest.raises(ValueError, match="already exists"):
        table.insert(Document({"entry": 2}, doc_id=42))


# ---------------------------------------------------------------------------
# 2. Tests for Table.get() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(7)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_get_by_valid_doc_id_ecp(table: Table):
    """EC10: Querying existing document by doc_id returns Document instance."""
    table.insert({"title": "Introduction to AST"})
    doc = table.get(doc_id=1)
    assert doc is not None
    assert doc["title"] == "Introduction to AST"
    assert doc.doc_id == 1


@pytest.mark.order(8)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
@pytest.mark.parametrize("non_existent_id", [0, -1, 999])
def test_get_by_boundary_doc_ids_bva(table: Table, non_existent_id):
    """BVA7 / EC11: Boundary IDs (0, negative, missing) safely return None."""
    table.insert({"key": "value"})
    assert table.get(doc_id=non_existent_id) is None


@pytest.mark.order(9)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_get_by_condition_single_match_ecp(table: Table):
    """EC12: Query matching exactly one document returns that document."""
    table.insert({"env": "dev", "port": 3000})
    table.insert({"env": "prod", "port": 443})
    q = Query()
    result = table.get(q.env == "prod")
    assert result is not None
    assert result["port"] == 443
    assert result.doc_id == 2


@pytest.mark.order(10)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_get_by_condition_multiple_matches_bva(table: Table):
    """EC13 / BVA: Condition matching >1 docs returns the FIRST inserted doc."""
    table.insert({"category": "book", "title": "First"})
    table.insert({"category": "book", "title": "Second"})
    q = Query()
    first = table.get(q.category == "book")
    assert first is not None
    assert first["title"] == "First"
    assert first.doc_id == 1


@pytest.mark.order(11)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_get_by_condition_no_match_ecp(table: Table):
    """EC14: Query condition matching zero documents returns None."""
    table.insert({"user": "admin"})
    q = Query()
    assert table.get(q.user == "guest") is None


@pytest.mark.order(12)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_get_invalid_no_arguments_ecp(table: Table):
    """EC16: Calling get() with no arguments raises RuntimeError."""
    with pytest.raises(RuntimeError, match="either cond or doc_id or doc_ids"):
        table.get()


# ---------------------------------------------------------------------------
# 3. Tests for Table.search() and Query Cache [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(13)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_search_matches_subset_ecp(table: Table):
    """EC17: Search returning a subset of matching records."""
    table.insert({"status": "active", "code": 200})
    table.insert({"status": "inactive", "code": 500})
    table.insert({"status": "active", "code": 201})
    q = Query()
    active_docs = table.search(q.status == "active")
    assert len(active_docs) == 2
    assert [d["code"] for d in active_docs] == [200, 201]


@pytest.mark.order(14)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_search_matches_empty_table_bva(table: Table):
    """BVA11: Search on an empty table returns an empty list []."""
    q = Query()
    results = table.search(q.any_field == "value")
    assert results == []


@pytest.mark.order(15)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_search_query_cache_hit_bva(table: Table):
    """EC20: Search query results are cached and retrieved on second call."""
    table.insert({"level": "DEBUG"})
    table.insert({"level": "INFO"})
    q = Query()
    first_res = table.search(q.level == "INFO")
    second_res = table.search(q.level == "INFO")
    assert first_res == second_res
    # Inserting a new doc invalidates cache
    table.insert({"level": "INFO"})
    third_res = table.search(q.level == "INFO")
    assert len(third_res) == 2


# ---------------------------------------------------------------------------
# 4. Tests for Table.update() and Table.truncate() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(16)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_update_by_condition_ecp(table: Table):
    """EC21: Update matching documents with new dictionary fields."""
    table.insert({"name": "Task 1", "done": False})
    table.insert({"name": "Task 2", "done": False})
    q = Query()
    updated_ids = table.update({"done": True}, q.name == "Task 1")
    assert updated_ids == [1]
    assert table.get(doc_id=1)["done"] is True
    assert table.get(doc_id=2)["done"] is False


@pytest.mark.order(17)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_update_all_unconditionally_bva(table: Table):
    """EC24 / BVA: Unconditional update modifies all documents in table."""
    table.insert({"val": 10})
    table.insert({"val": 20})
    updated_ids = table.update({"archived": True})
    assert set(updated_ids) == {1, 2}
    for doc in table.all():
        assert doc["archived"] is True


@pytest.mark.order(18)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_update_with_callable_mutator_ecp(table: Table):
    """EC22: Update using callable mutator function modifies values in place."""
    table.insert({"counter": 5})
    table.update(lambda d: d.update({"counter": d["counter"] * 10}))
    doc = table.get(doc_id=1)
    assert doc["counter"] == 50


@pytest.mark.order(19)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_update_on_empty_table_bva(table: Table):
    """BVA13: Update on empty table returns empty list and causes no side effects."""
    updated = table.update({"flag": 1})
    assert updated == []


@pytest.mark.order(20)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_truncate_populated_and_empty_table_bva(table: Table):
    """EC33 / EC34 / BVA: Truncate clears table, resets next_id, is idempotent."""
    table.insert({"x": 1})
    table.insert({"x": 2})
    assert len(table) == 2
    table.truncate()
    assert len(table) == 0
    assert table.all() == []
    # Verify next insert re-starts with ID 1
    new_id = table.insert({"x": 99})
    assert new_id == 1
    # Truncate on empty table is idempotent
    table.truncate()
    assert len(table) == 0


# ---------------------------------------------------------------------------
# 5. Task 3: CSV Data-Driven Parameterized Tests for Table
# ---------------------------------------------------------------------------

@pytest.mark.order(21)
@pytest.mark.table
@pytest.mark.csv_data
@pytest.mark.parametrize("row", load_csv_records("test_data_table_mahmed.csv"))
def test_insert_csv_data_driven_mahmed(table: Table, row: dict[str, str]):
    """Task 3: Consume external CSV test data to verify document insert and field indexing."""
    doc = {
        "name": row["name"],
        "age": int(row["age"]),
        "city": row["city"]
    }
    assigned_id = table.insert(doc)
    assert assigned_id == 1
    retrieved = table.get(doc_id=assigned_id)
    assert retrieved is not None
    assert retrieved["name"] == row["name"]
    assert retrieved["age"] == int(row["age"])
    assert retrieved["city"] == row["city"]


@pytest.mark.order(22)
@pytest.mark.table
@pytest.mark.csv_data
def test_insert_batch_csv_data_sequential(table: Table):
    """Task 3: Sequentially insert all CSV records and verify sequential ID generation."""
    rows = load_csv_records("test_data_table_mahmed.csv")
    for row in rows:
        expected_id = int(row["expected_id"])
        doc = {
            "name": row["name"],
            "age": int(row["age"]),
            "city": row["city"]
        }
        assigned_id = table.insert(doc)
        assert assigned_id == expected_id

    assert len(table) == len(rows)
    for row in rows:
        expected_id = int(row["expected_id"])
        doc = table.get(doc_id=expected_id)
        assert doc is not None
        assert doc["name"] == row["name"]

