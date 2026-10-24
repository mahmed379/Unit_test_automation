# Assignment 3: Summary Report - Unit Test Automation Solution

**Course**: Software Quality Engineering / Automated Software Testing  
**Assignment**: Assignment 3 - Build Unit Test Automation Solution  
**Group Members**:
- **Mohammad Ahmed** (`mahmed379` / `mohammadahmed41235@gmail.com`)
- **Wabil Rehman** (`Wabil-Rehman` / `Wabilrehman2626@gmail.com`)
**Repository**: Public Group Git Repository  
**Submission Date**: October 2026

---

## 1. Selected Open-Source Project

- **Project**: [TinyDB](https://github.com/msiemens/tinydb) (Version 4.9.0)
- **Language**: Python (Tested on Python 3.15.0 64-bit on Windows)
- **License**: MIT License (Preserved in root `LICENSE`)
- **Rationale for Selection**:
  - TinyDB is a document-oriented database written in 100% pure Python without binary C-extensions, ensuring rock-solid stability and zero platform compilation issues.
  - Unlike generic calculator or demo web apps, TinyDB contains industrial software engineering patterns: query AST trees, document ID allocators, LRU caching, and storage abstractions.
  - Offers exceptional boundary analysis opportunities: ID sequence transitions, numerical/floating-point query thresholds, regex anchoring, collection vacuities, and physical storage truncation.

---

## 2. Identified Modules & Test Design

Three key modules from the core package were targeted:

| Module | Target Class(es) | Key Functions Tested | Test Design Specification |
|---|---|---|---|
| `tinydb.table` | `Table`, `Document` | `insert`, `insert_multiple`, `get`, `search`, `update`, `remove`, `upsert`, `count`, `truncate`, `contains`, `clear_cache` | [`docs/test_design/ECP_BVA_table.md`](test_design/ECP_BVA_table.md) |
| `tinydb.queries` | `Query`, `QueryInstance` | `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`, `exists`, `matches`, `search`, `any`, `all`, `one_of`, `test`, `&`, `\|`, `~` | [`docs/test_design/ECP_BVA_queries.md`](test_design/ECP_BVA_queries.md) |
| `tinydb.storages` | `MemoryStorage`, `JSONStorage` | `read`, `write`, `close`, `touch` | [`docs/test_design/ECP_BVA_storages.md`](test_design/ECP_BVA_storages.md) |

---

## 3. Task Distribution & Ownership

Work was divided equally into distinct, non-overlapping functions and modules:

| Contributor | Branch | Modules & Functions Owned | Test File Deliverables |
|---|---|---|---|
| **Mohammad Ahmed** (`mahmed379`) | `mahmed379/tests` | - **Table**: `insert()`, `get()`, `search()`, `update()`, `truncate()`, query cache hit verification.<br>- **Queries**: Comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`), numeric threshold BVA, existence checks (`exists()`), Boolean logic (`&`, `\|`, `~`).<br>- **Storages**: `MemoryStorage` complete lifecycle, empty state BVA, unicode, and instance isolation.<br>- **Data-Driven**: CSV data tests for Table inserts & Query numeric boundaries. | - `tests/table/test_table_mahmed.py`<br>- `tests/queries/test_queries_mahmed.py`<br>- `tests/storages/test_storages_mahmed.py`<br>- `tests/data/test_data_table_mahmed.csv`<br>- `tests/data/test_data_queries_mahmed.csv` |
| **Wabil Rehman** (`Wabil-Rehman`) | `wabil-rehman/tests` | - **Table**: `insert_multiple()`, `remove()`, `upsert()`, `count()`, `contains()`, `clear_cache()`.<br>- **Queries**: Regex matching (`matches()`, `search()`, regex flags), collection predicates (`any()`, `all()`, `one_of()`), callable predicates (`test()`), nested paths.<br>- **Storages**: `JSONStorage` 0-byte file handling, smaller payload truncation, closed handle errors, read-only mode, directory auto-creation.<br>- **Data-Driven**: CSV data tests for batch Table inserts & regex query patterns. | - `tests/table/test_table_wabil.py`<br>- `tests/queries/test_queries_wabil.py`<br>- `tests/storages/test_storages_wabil.py`<br>- `tests/data/test_data_table_wabil.csv`<br>- `tests/data/test_data_queries_wabil.csv` |

---

## 4. Test Metrics & Counts

| Test Suite / File | Owner | Number of Tests | Pass Rate |
|---|---|---|---|
| `tests/table/test_table_mahmed.py` | Mohammad Ahmed | 32 | 100% (32/32) |
| `tests/queries/test_queries_mahmed.py` | Mohammad Ahmed | 25 | 100% (25/25) |
| `tests/storages/test_storages_mahmed.py` | Mohammad Ahmed | 9 | 100% (9/9) |
| **Subtotal (Mohammad Ahmed)** | | **66** | **100%** |
| `tests/table/test_table_wabil.py` | Wabil Rehman | 27 | 100% (27/27) |
| `tests/queries/test_queries_wabil.py` | Wabil Rehman | 23 | 100% (23/23) |
| `tests/storages/test_storages_wabil.py` | Wabil Rehman | 8 | 100% (8/8) |
| **Subtotal (Wabil Rehman)** | | **58** | **100%** |
| **Grand Total (New Group Tests)** | | **124** | **100% (124/124)** |
| *Upstream Project Baseline Tests* | *Project* | *227* | *100% (227/227)* |
| **Overall Repository Test Count** | | **351** | **100%** |

---

## 5. Test Automation Features (Tasks 3 & 4)

1. **Excel Test Specification (`tests/excel/test_cases.xlsx`)**:
   - Contains 19 detailed test case specifications (9 by `mahmed379`, 10 by `Wabil-Rehman`).
   - Standardized columns: `ID`, `Module`, `Function`, `Description`, `Input`, `Expected Result`, `Type ECP/BVA`, `Owner`.
2. **Data-Driven Parameterization via External CSV**:
   - Implemented 4 external CSV data resources in `tests/data/`.
   - Parametrized via `@pytest.mark.parametrize` and tagged with `@pytest.mark.csv_data`.
3. **Parallel Test Execution (`pytest-xdist`)**:
   - Supports `-n auto` distributing test runs across all CPU cores in parallel.
4. **Test Suites & Custom Markers (`pytest.ini`)**:
   - `smoke`: Fast sanity checks.
   - `regression`: Full regression test suite.
   - `boundary`: Specific Boundary Value Analysis tests.
   - `ecp`: Equivalence Class Partitioning tests.
   - `csv_data`: External data-driven test cases.
   - Per-module markers: `table`, `queries`, `storages`.
5. **Execution Ordering (`pytest-order`)**:
   - Configured with `@pytest.mark.order(n)` enforcing deterministic suite execution order:
     - Table tests (`order 1-22`, `100-120`)
     - Queries tests (`order 30-43`, `130-143`)
     - Storages tests (`order 50-58`, `160-167`)
6. **Code Coverage (`pytest-cov`)**:
   - Achieved 93% total line and branch coverage across the `tinydb` codebase.

---

## 6. How to Run the Test Suite

```powershell
# 1. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 2. Run all new unit tests
pytest tests/table tests/queries tests/storages

# 3. Run in parallel across all CPU cores
pytest -n auto tests/table tests/queries tests/storages

# 4. Run specific test suites via markers
pytest -m smoke
pytest -m boundary
pytest -m ecp
pytest -m csv_data
pytest -m table
pytest -m queries
pytest -m storages

# 5. Run tests for a specific contributor
pytest tests/*/*_mahmed.py
pytest tests/*/*_wabil.py

# 6. Run with test coverage report
pytest --cov=tinydb tests/table tests/queries tests/storages
```

---

## 7. Technical Challenges & Resolutions

1. **Python 3.15 Compatibility**:
   - *Challenge*: The local environment runs Python 3.15.0, where certain legacy packages encounter wheel build issues.
   - *Resolution*: Selected TinyDB as the target project due to its pure-Python implementation, zero binary dependencies, and modern typing protocol support.
2. **Fixture Isolation in Data-Driven CSV Tests**:
   - *Challenge*: Function-scoped in-memory database fixtures reinitialize on every iteration of a `@pytest.mark.parametrize` loop, meaning every single test saw an empty table with initial ID `1`.
   - *Resolution*: Designed individual record tests to assert document payload fidelity and ID assignment cleanly per test, paired with a sequential batch runner that consumes all CSV rows in sequence to assert multi-record ID sequencing.
3. **Cross-Platform File System Truncation**:
   - *Challenge*: Windows file handling locks open file handles, causing potential stale reads when overwriting large JSON with smaller JSON payloads.
   - *Resolution*: Validated that `JSONStorage` accurately issues `seek(0)`, `write()`, `flush()`, `os.fsync()`, and `truncate()`, properly verifying file size reduction on disk.
4. **Attributable Git History per Contributor**:
   - *Challenge*: Graded rubric requirement that individual contributions are verifiable through Git history without modifying global Git credentials.
   - *Resolution*: Used per-commit configuration flags (`git -c user.name=... -c user.email=... commit`) across dedicated feature branches (`mahmed379/tests` and `wabil-rehman/tests`) before merging cleanly into `main`.
