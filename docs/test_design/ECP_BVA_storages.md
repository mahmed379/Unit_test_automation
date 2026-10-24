# Equivalence Class Partitioning (ECP) & Boundary Value Analysis (BVA): `Storages` Module

**Target Module**: `tinydb.storages`  
**Target Classes**: `tinydb.storages.MemoryStorage`, `tinydb.storages.JSONStorage`, `tinydb.storages.Storage`  
**Authors**: Mohammad Ahmed (`mahmed379`) & Wabil Rehman (`Wabil-Rehman`)

---

## 1. Module Overview
The `storages` module provides serialization and deserialization abstractions. `MemoryStorage` maintains the document tree in an in-memory dictionary, while `JSONStorage` serializes data to disk with file locking, flushing, and directory management.

---

## 2. Partitioning & Boundary Analysis

### 2.1 Class: `MemoryStorage`
- **Equivalence Classes**:
  - `EC1` (Valid): Initialized state before any write -> `read()` returns `None`.
  - `EC2` (Valid): Writing dictionary mapping `{"_default": {"1": {"a": 1}}}` -> `read()` returns identical structure.
  - `EC3` (Valid): Overwriting existing data with new mapping -> `read()` reflects latest state.
  - `EC4` (Valid): `close()` called on `MemoryStorage` -> Acts as safe no-op without memory corruption.
- **Boundary Value Analysis**:
  - `BVA1`: Write empty dictionary `{}` -> `read()` returns `{}` (not `None`).
  - `BVA2`: Multiple read operations without intervening write -> Idempotent references returned.
  - `BVA3`: Nested dictionary structures with arbitrary JSON types (strings, lists, booleans, nulls).

### 2.2 Class: `JSONStorage`
- **Equivalence Classes**:
  - `EC5` (Valid): `access_mode='r+'` on newly created file (`create_dirs=True`). Expected: Touches file, allows read and write.
  - `EC6` (Valid): `read()` on 0-byte file. Expected: Returns `None` (triggers clean TinyDB table initialization).
  - `EC7` (Valid): `write()` followed by `read()` -> Preserves JSON serialized payload.
  - `EC8` (Valid): UTF-8 unicode encoding with multi-byte characters (emoji, Cyrillic, Arabic).
  - `EC9` (Invalid): Read-only access mode `'r'` when attempting `write()`. Expected: Raises `IOError`.
  - `EC10` (Invalid): Non-existent parent directory when `create_dirs=False`. Expected: Raises `FileNotFoundError`.
  - `EC11` (Invalid): Unhandled access mode (e.g. `'x'`). Expected: Triggers user warning.
- **Boundary Value Analysis**:
  - `BVA4`: File size = 0 bytes (empty file) -> `read()` returns `None`.
  - `BVA5`: Overwriting a large JSON payload with a significantly smaller payload -> Checks that `truncate()` executes properly so no stale bytes remain.
  - `BVA6`: Calling `close()` and attempting subsequent read/write -> Raises `ValueError("I/O operation on closed file")`.
  - `BVA7`: Complex kwargs passed to serializer (`indent=2`, `sort_keys=True`).

---

## 3. Work Allocation
- **Mohammad Ahmed (`mahmed379`)**: Focuses on `MemoryStorage` lifecycle, in-memory isolation, empty state boundaries, and persistence idempotence (`tests/storages/test_storages_mahmed.py`).
- **Wabil Rehman (`Wabil-Rehman`)**: Focuses on `JSONStorage` file boundaries (0-byte file, smaller payload truncation, closed handle semantics, read-only mode, and directory creation) (`tests/storages/test_storages_wabil.py`).
