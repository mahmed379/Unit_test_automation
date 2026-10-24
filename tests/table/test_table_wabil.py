"""
Unit tests for Table class in tinydb.table
Author: Wabil Rehman (Wabil-Rehman / Wabilrehman2626@gmail.com)
Covers: insert_multiple, remove, upsert, count, contains, clear_cache, and CSV data-driven tests.
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
    return Table(storage=storage, name='wabil_table')


# ---------------------------------------------------------------------------
# 1. Tests for Table.insert_multiple() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(100)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_insert_multiple_valid_documents_ecp(table: Table):
    """EC6: Batch inserting valid dictionaries returns sequential ID list."""
    docs = [
        {"item": "Laptop", "price": 1200},
        {"item": "Mouse", "price": 25},
        {"item": "Keyboard", "price": 75}
    ]
    ids = table.insert_multiple(docs)
    assert ids == [1, 2, 3]
    assert len(table) == 3
    assert table.get(doc_id=1)["item"] == "Laptop"
    assert table.get(doc_id=3)["item"] == "Keyboard"


@pytest.mark.order(101)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_multiple_empty_list_bva(table: Table):
    """EC7 / BVA4: Inserting empty list returns [] and leaves table unchanged."""
    ids = table.insert_multiple([])
    assert ids == []
    assert len(table) == 0


@pytest.mark.order(102)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_multiple_single_item_bva(table: Table):
    """BVA5: Inserting single-item list returns list with single ID."""
    ids = table.insert_multiple([{"key": "single"}])
    assert ids == [1]
    assert len(table) == 1


@pytest.mark.order(103)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
@pytest.mark.parametrize("invalid_batch", [
    [{"valid": 1}, "not-a-dict", {"valid": 2}],
    [100, 200],
    [None]
])
def test_insert_multiple_invalid_non_mapping_element_ecp(table: Table, invalid_batch):
    """EC8: Any non-mapping item in batch raises ValueError."""
    with pytest.raises(ValueError, match="Document is not a Mapping"):
        table.insert_multiple(invalid_batch)


@pytest.mark.order(104)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_multiple_with_explicit_document_ids(table: Table):
    """BVA: Batch inserting Document objects with explicit IDs."""
    batch = [
        Document({"code": "A"}, doc_id=10),
        Document({"code": "B"}, doc_id=20)
    ]
    ids = table.insert_multiple(batch)
    assert ids == [10, 20]
    assert table.get(doc_id=10)["code"] == "A"
    assert table.get(doc_id=20)["code"] == "B"


@pytest.mark.order(105)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_insert_multiple_large_batch_sequencing_bva(table: Table):
    """BVA6: Large batch insertion (50 documents) verifies continuous ID sequencing."""
    batch = [{"index": i} for i in range(50)]
    ids = table.insert_multiple(batch)
    assert ids == list(range(1, 51))
    assert len(table) == 50


# ---------------------------------------------------------------------------
# 2. Tests for Table.remove() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(106)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_remove_by_condition_matching_subset_ecp(table: Table):
    """EC26: Remove matching documents by query condition."""
    table.insert_multiple([
        {"user": "u1", "status": "banned"},
        {"user": "u2", "status": "active"},
        {"user": "u3", "status": "banned"}
    ])
    q = Query()
    removed_ids = table.remove(q.status == "banned")
    assert sorted(removed_ids) == [1, 3]
    assert len(table) == 1
    assert table.get(doc_id=2)["status"] == "active"


@pytest.mark.order(107)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_remove_by_condition_zero_matches_bva(table: Table):
    """EC28 / BVA: Removing by condition that matches zero docs returns []."""
    table.insert({"tag": "alpha"})
    q = Query()
    removed = table.remove(q.tag == "omega")
    assert removed == []
    assert len(table) == 1


@pytest.mark.order(108)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_remove_by_doc_ids_list_ecp(table: Table):
    """EC27: Remove documents by explicit list of doc_ids."""
    table.insert_multiple([{"x": 10}, {"x": 20}, {"x": 30}])
    removed = table.remove(doc_ids=[1, 3])
    assert removed == [1, 3]
    assert len(table) == 1
    assert table.get(doc_id=2)["x"] == 20


@pytest.mark.order(109)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_remove_by_doc_ids_with_missing_and_negative_ids_bva(table: Table):
    """BVA16: Non-existent IDs (e.g. -1, 999) are silently skipped on remove."""
    table.insert({"data": "keep"})
    removed = table.remove(doc_ids=[-1, 999])
    assert removed == []
    assert len(table) == 1


@pytest.mark.order(110)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_remove_invalid_no_arguments_ecp(table: Table):
    """EC29: Calling remove() with no condition or IDs raises RuntimeError."""
    with pytest.raises(RuntimeError, match="Use truncate.*to remove all documents"):
        table.remove()


# ---------------------------------------------------------------------------
# 3. Tests for Table.upsert() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(111)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_upsert_existing_document_updates_ecp(table: Table):
    """EC30: Upsert on matching query updates existing document fields."""
    table.insert({"service": "redis", "port": 6379})
    q = Query()
    updated_ids = table.upsert({"port": 6380}, q.service == "redis")
    assert updated_ids == [1]
    assert table.get(doc_id=1)["port"] == 6380
    assert len(table) == 1


@pytest.mark.order(112)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_upsert_missing_document_inserts_ecp(table: Table):
    """EC31: Upsert on non-matching query inserts new document."""
    table.insert({"service": "redis", "port": 6379})
    q = Query()
    new_ids = table.upsert({"service": "postgres", "port": 5432}, q.service == "postgres")
    assert new_ids == [2]
    assert len(table) == 2
    assert table.get(doc_id=2)["service"] == "postgres"


@pytest.mark.order(113)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_upsert_into_empty_table_bva(table: Table):
    """BVA17: Upsert into empty table always inserts with doc_id 1."""
    q = Query()
    ids = table.upsert({"init": True}, q.init == True)
    assert ids == [1]
    assert len(table) == 1


@pytest.mark.order(114)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_upsert_missing_query_and_id_raises_value_error(table: Table):
    """EC32: Upserting standard dict without query condition raises ValueError."""
    with pytest.raises(ValueError, match="If you don't specify a search query"):
        table.upsert({"data": "bad"})


# ---------------------------------------------------------------------------
# 4. Tests for Table.count(), Table.contains(), Table.clear_cache() [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(115)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.smoke
def test_count_matching_documents_ecp(table: Table):
    """EC35: count() accurately reflects number of matching records."""
    table.insert_multiple([
        {"tier": "free"},
        {"tier": "pro"},
        {"tier": "free"}
    ])
    q = Query()
    assert table.count(q.tier == "free") == 2
    assert table.count(q.tier == "pro") == 1
    assert table.count(q.tier == "enterprise") == 0


@pytest.mark.order(116)
@pytest.mark.table
@pytest.mark.ecp
@pytest.mark.regression
def test_contains_by_doc_id_and_query_ecp(table: Table):
    """EC: contains() returns True for existing doc_id or condition, False otherwise."""
    table.insert({"metric": "cpu", "usage": 88})
    q = Query()

    assert table.contains(doc_id=1) is True
    assert table.contains(doc_id=99) is False
    assert table.contains(q.metric == "cpu") is True
    assert table.contains(q.metric == "ram") is False


@pytest.mark.order(117)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_contains_invalid_no_arguments_ecp(table: Table):
    """Calling contains() with neither condition nor doc_id raises RuntimeError."""
    with pytest.raises(RuntimeError, match="either cond or doc_id"):
        table.contains()


@pytest.mark.order(118)
@pytest.mark.table
@pytest.mark.boundary
@pytest.mark.regression
def test_clear_cache_empties_query_cache_bva(table: Table):
    """Verifies that clear_cache() purges query cache entries."""
    table.insert({"dept": "sales"})
    q = Query()
    table.search(q.dept == "sales")
    # Cache now contains 1 entry
    assert len(table._query_cache) == 1
    table.clear_cache()
    assert len(table._query_cache) == 0


# ---------------------------------------------------------------------------
# 5. Task 3: CSV Data-Driven Parameterized Tests for Table (Wabil)
# ---------------------------------------------------------------------------

@pytest.mark.order(119)
@pytest.mark.table
@pytest.mark.csv_data
@pytest.mark.parametrize("row", load_csv_records("test_data_table_wabil.csv"))
def test_insert_csv_data_driven_wabil(table: Table, row: dict[str, str]):
    """Task 3: Consume CSV test data to verify product catalog document inserts."""
    doc = {
        "product_name": row["product_name"],
        "category": row["category"],
        "price": float(row["price"])
    }
    assigned_id = table.insert(doc)
    assert assigned_id == 1
    retrieved = table.get(doc_id=1)
    assert retrieved is not None
    assert retrieved["product_name"] == row["product_name"]
    assert retrieved["category"] == row["category"]
    assert retrieved["price"] == float(row["price"])


@pytest.mark.order(120)
@pytest.mark.table
@pytest.mark.csv_data
def test_insert_multiple_batch_csv_data_wabil(table: Table):
    """Task 3: Batch insert all CSV records using insert_multiple and verify sequential IDs."""
    rows = load_csv_records("test_data_table_wabil.csv")
    batch = [
        {
            "product_name": r["product_name"],
            "category": r["category"],
            "price": float(r["price"])
        }
        for r in rows
    ]
    ids = table.insert_multiple(batch)
    assert ids == [1, 2, 3, 4, 5]
    assert len(table) == 5

    q = Query()
    assert table.count(q.category == "Electronics") == 3
    assert table.count(q.category == "Furniture") == 1
    assert table.count(q.category == "Stationery") == 1
