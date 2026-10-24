# Equivalence Class Partitioning (ECP) & Boundary Value Analysis (BVA): `Table` Module

**Target Module**: `tinydb.table`  
**Target Class**: `tinydb.table.Table`  
**Authors**: Mohammad Ahmed (`mahmed379`) & Wabil Rehman (`Wabil-Rehman`)

---

## 1. Module Overview
The `Table` class manages document collections, indexing, ID allocation, query execution, caching, and persistence dispatching. Document IDs are positive integers (`int >= 1`), and stored documents must implement the `Mapping` interface.

---

## 2. Partitioning & Boundary Analysis

### 2.1 Function: `insert(document)`
- **Input Domain**: `document: Mapping`
- **Equivalence Classes**:
  - `EC1` (Valid): Standard dictionary with string keys and primitive values `{"name": "Alice", "score": 100}`. Expected: Generates new doc_id `1`, returns `1`.
  - `EC2` (Valid): Empty dictionary `{}`. Expected: Accepted as valid document mapping, returns positive integer ID.
  - `EC3` (Valid): Pre-instantiated `Document(value, doc_id=N)`. Expected: Uses explicit ID `N`.
  - `EC4` (Invalid): Non-mapping input (`"string"`, `123`, `[1, 2]`, `None`). Expected: Raises `ValueError("Document is not a Mapping")`.
  - `EC5` (Invalid): Pre-instantiated `Document` whose `doc_id` already exists in table. Expected: Raises `ValueError("Document with ID ... already exists")`.
- **Boundary Value Analysis**:
  - `BVA1`: First inserted document in empty table -> allocated doc_id = `1` (minimum positive ID).
  - `BVA2`: Subsequent insert -> allocated doc_id = `2` (`next_id = max(keys) + 1`).
  - `BVA3`: Document with large integer ID `doc_id = 1_000_000` inserted -> next auto-assigned ID becomes `1_000_001`.

### 2.2 Function: `insert_multiple(documents)`
- **Input Domain**: `documents: Iterable[Mapping]`
- **Equivalence Classes**:
  - `EC6` (Valid): List of multiple valid dictionaries `[{"k": 1}, {"k": 2}]`. Expected: Returns list of IDs `[1, 2]`.
  - `EC7` (Valid): Empty list `[]`. Expected: Returns `[]`, table remains unchanged.
  - `EC8` (Invalid): Iterable containing at least one non-mapping element. Expected: Raises `ValueError`.
  - `EC9` (Invalid): Iterable with duplicate explicit `Document` IDs. Expected: Raises `ValueError`.
- **Boundary Value Analysis**:
  - `BVA4`: `documents` of length 0 (empty list).
  - `BVA5`: `documents` of length 1 (single item batch).
  - `BVA6`: `documents` of length 50+ (high-volume batch ID sequencing).

### 2.3 Function: `get(cond, doc_id, doc_ids)`
- **Input Domain**: `cond: Optional[QueryLike]`, `doc_id: Optional[int]`, `doc_ids: Optional[list]`
- **Equivalence Classes**:
  - `EC10` (Valid): `doc_id` matches an existing document. Expected: Returns `Document` instance with `.doc_id`.
  - `EC11` (Valid): `doc_id` does not exist in table. Expected: Returns `None`.
  - `EC12` (Valid): `cond` matches exactly 1 document. Expected: Returns single `Document`.
  - `EC13` (Valid): `cond` matches >1 document. Expected: Returns first matching document in insertion order.
  - `EC14` (Valid): `cond` matches 0 documents. Expected: Returns `None`.
  - `EC15` (Valid): `doc_ids` provided as a list. Expected: Returns list of matching documents.
  - `EC16` (Invalid): No parameters provided (`cond=None, doc_id=None, doc_ids=None`). Expected: Raises `RuntimeError`.
- **Boundary Value Analysis**:
  - `BVA7`: `doc_id = 0` (boundary below valid auto IDs) -> Returns `None`.
  - `BVA8`: `doc_id = 1` (minimum valid auto ID).
  - `BVA9`: `doc_ids = []` (empty list) -> Returns `[]`.
  - `BVA10`: `doc_ids` containing mix of valid and non-existent IDs.

### 2.4 Function: `search(cond)`
- **Input Domain**: `cond: QueryLike`
- **Equivalence Classes**:
  - `EC17` (Valid): Query matches subset of documents. Expected: Returns matching list.
  - `EC18` (Valid): Query matches all documents. Expected: Returns list of all documents.
  - `EC19` (Valid): Query matches no documents. Expected: Returns `[]`.
  - `EC20` (Valid): Search executed multiple times with identical query. Expected: Cache hit returns cached copy.
- **Boundary Value Analysis**:
  - `BVA11`: Search on empty table (`len(table) == 0`) -> Returns `[]`.
  - `BVA12`: Table with 1 document matching vs not matching.

### 2.5 Function: `update(fields, cond, doc_ids)`
- **Input Domain**: `fields: Union[Mapping, Callable]`, `cond: Optional[QueryLike]`, `doc_ids: Optional[Iterable[int]]`
- **Equivalence Classes**:
  - `EC21` (Valid): Update with dictionary fields on matching `cond`. Expected: Merges fields, returns list of updated IDs.
  - `EC22` (Valid): Update with callable/lambda function `lambda doc: doc.update(...)`. Expected: Mutates matching documents in place.
  - `EC23` (Valid): Update by `doc_ids=[...]`. Expected: Updates only specified IDs; ignores missing IDs silently.
  - `EC24` (Valid): Update with `cond=None` and `doc_ids=None`. Expected: Updates all documents in table.
  - `EC25` (Valid): Query matches 0 documents. Expected: Returns `[]`, no table modification.
- **Boundary Value Analysis**:
  - `BVA13`: Update on empty table -> Returns `[]`.
  - `BVA14`: Updating key that previously did not exist in document (adding new field).

### 2.6 Function: `remove(cond, doc_ids)`
- **Input Domain**: `cond: Optional[QueryLike]`, `doc_ids: Optional[Iterable[int]]`
- **Equivalence Classes**:
  - `EC26` (Valid): Remove by `cond` matching one or more documents. Expected: Documents deleted, returns removed IDs.
  - `EC27` (Valid): Remove by `doc_ids` list. Expected: Deletes matching IDs, skips non-existent, returns removed IDs.
  - `EC28` (Valid): Remove where `cond` matches 0 documents. Expected: Returns `[]`.
  - `EC29` (Invalid): Neither `cond` nor `doc_ids` specified. Expected: Raises `RuntimeError("Use truncate() to remove all documents")`.
- **Boundary Value Analysis**:
  - `BVA15`: Remove last remaining document in table -> `len(table)` transitions from 1 to 0.
  - `BVA16`: Removing non-existent `doc_ids=[-1, 999]` -> Returns `[]`.

### 2.7 Function: `upsert(document, cond)`
- **Input Domain**: `document: Mapping`, `cond: Optional[QueryLike]`
- **Equivalence Classes**:
  - `EC30` (Valid): Matching document exists -> Performs `update` and returns updated doc_ids.
  - `EC31` (Valid): No matching document exists -> Performs `insert` and returns `[new_doc_id]`.
  - `EC32` (Invalid): `cond=None` and `document` has no `doc_id`. Expected: Raises `ValueError`.
- **Boundary Value Analysis**:
  - `BVA17`: Upsert into empty table -> Always inserts with doc_id `1`.
  - `BVA18`: Upsert matching multiple existing documents -> Updates all matched documents.

### 2.8 Function: `truncate()` & `count(cond)`
- **Equivalence Classes**:
  - `EC33` (Valid): `truncate()` on table with documents -> Resets length to 0, resets next_id.
  - `EC34` (Valid): `truncate()` on already empty table -> Idempotent no-op.
  - `EC35` (Valid): `count(cond)` -> Returns integer count matching search result count.
- **Boundary Value Analysis**:
  - `BVA19`: `count` = 0 (no matches).
  - `BVA20`: `count` = `len(table)` (all match).

---

## 3. Work Allocation
- **Mohammad Ahmed (`mahmed379`)**: Focuses on `insert`, `get`, `search`, `update`, `truncate`, and cache validation (`tests/table/test_table_mahmed.py`).
- **Wabil Rehman (`Wabil-Rehman`)**: Focuses on `insert_multiple`, `remove`, `upsert`, `count`, `contains`, and batch ID boundary conditions (`tests/table/test_table_wabil.py`).
