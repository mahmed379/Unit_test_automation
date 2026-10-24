# Equivalence Class Partitioning (ECP) & Boundary Value Analysis (BVA): `Queries` Module

**Target Module**: `tinydb.queries`  
**Target Classes**: `tinydb.queries.Query`, `tinydb.queries.QueryInstance`  
**Authors**: Mohammad Ahmed (`mahmed379`) & Wabil Rehman (`Wabil-Rehman`)

---

## 1. Module Overview
The `queries` module supplies the AST-like query building DSL for TinyDB. `Query` objects build paths and comparison nodes which evaluate into executable `QueryInstance` callables with deterministic hashing for query caching.

---

## 2. Partitioning & Boundary Analysis

### 2.1 Comparison Operators (`__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`)
- **Input Domain**: Document values compared against RHS boundary values.
- **Equivalence Classes**:
  - `EC1` (Valid): Numeric equality (`val == RHS`).
  - `EC2` (Valid): String equality with exact case matching.
  - `EC3` (Valid): Missing field evaluated -> Safely returns `False` without exception.
  - `EC4` (Valid): Type mismatch (e.g. comparing integer field against string) -> Returns `False` or follows Python comparison semantics.
- **Boundary Value Analysis (Numeric Range: e.g. Threshold = 50)**:
  - `BVA1`: Value = `49` (Just below boundary: `val < 50` is `True`, `val >= 50` is `False`).
  - `BVA2`: Value = `50` (On boundary: `val == 50`, `val <= 50`, `val >= 50` are `True`; `val < 50`, `val > 50` are `False`).
  - `BVA3`: Value = `51` (Just above boundary: `val > 50` is `True`, `val <= 50` is `False`).
  - `BVA4`: Negative numbers: `-1`, `0`, `1`.
  - `BVA5`: Floating point precision boundaries: `0.0`, `-0.0`, `1e-9`.

### 2.2 Logical Combinators (`__and__`, `__or__`, `__invert__`)
- **Input Domain**: Two `QueryInstance` objects combined via `&`, `|`, or inverted with `~`.
- **Equivalence Classes**:
  - `EC5` (Valid): `True & True` -> `True`.
  - `EC6` (Valid): `True & False` / `False & True` / `False & False` -> `False`.
  - `EC7` (Valid): `False | False` -> `False`; any other combination -> `True`.
  - `EC8` (Valid): `~True` -> `False`; `~False` -> `True`.
  - `EC9` (Valid): Nested De Morgan's Law verification: `~(A & B) == (~A | ~B)`.
- **Boundary Value Analysis**:
  - `BVA6`: Multi-clause chaining (3+ conditions combined).
  - `BVA7`: Inverting a query that tests a non-existent key (since missing key evaluates to `False`, inverting returns `True`).

### 2.3 Regular Expressions (`matches`, `search`)
- **Input Domain**: `regex: str`, `flags: int = 0`
- **Equivalence Classes**:
  - `EC10` (Valid): String value matches full regex (`matches`).
  - `EC11` (Valid): String value matches substring only (`search` succeeds, `matches` fails if unanchored).
  - `EC12` (Valid): Non-string value passed (e.g. integer or list) -> Returns `False` cleanly without throwing `TypeError`.
  - `EC13` (Valid): Case-insensitive flag `re.IGNORECASE`.
- **Boundary Value Analysis**:
  - `BVA8`: Empty string `""` matching empty pattern `r"^$"`.
  - `BVA9`: Pattern matching beginning vs end of string.

### 2.4 Set & Sequence Predicates (`any`, `all`, `one_of`)
- **Input Domain**: Collections, sequences, and nested document lists.
- **Equivalence Classes**:
  - `EC14` (Valid): `one_of([item1, item2])` with target value in candidate list.
  - `EC15` (Valid): `one_of([])` empty candidate list -> Evaluates to `False`.
  - `EC16` (Valid): `any(predicate)` over list of sub-documents where 1 element matches.
  - `EC17` (Valid): `all(predicate)` where all elements match vs at least 1 fails.
  - `EC18` (Valid): `any` or `all` called on non-sequence field (e.g. integer) -> Safely returns `False`.
- **Boundary Value Analysis**:
  - `BVA10`: Empty sequence `[]` in document -> `any()` is `False`, `all()` is `True` (vacuous truth).
  - `BVA11`: Sequence of length 1 matching vs not matching.

### 2.5 User-Defined Predicate (`test`) & Key Existence (`exists`)
- **Equivalence Classes**:
  - `EC19` (Valid): `exists()` on present key -> `True`; missing key -> `False`.
  - `EC20` (Valid): `test(custom_func)` where `custom_func` returns boolean.
  - `EC21` (Valid): `test(custom_func, arg1, arg2)` with additional freezeable arguments.
- **Boundary Value Analysis**:
  - `BVA12`: Key present in document with value `None` or `False` -> `exists()` evaluates to `True`.
  - `BVA13`: Deeply nested path `Query().profile.address.zipcode == "12345"`.

---

## 3. Work Allocation
- **Mohammad Ahmed (`mahmed379`)**: Focuses on comparison boundaries (`__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`), `exists()`, and boolean algebra (`&`, `|`, `~`) (`tests/queries/test_queries_mahmed.py`).
- **Wabil Rehman (`Wabil-Rehman`)**: Focuses on `matches()`, `search()`, `any()`, `all()`, `one_of()`, `test()`, and nested field traversal (`tests/queries/test_queries_wabil.py`).
