"""
Unit tests for Query and QueryInstance classes in tinydb.queries
Author: Mohammad Ahmed (mahmed379 / mohammadahmed41235@gmail.com)
Covers: Comparison operators (==, !=, <, <=, >, >=), existence checks,
boolean logic (&, |, ~), numeric/float boundaries, and CSV data-driven tests.
"""

import pytest

from tinydb import Query
from tests.conftest import load_csv_records


# ---------------------------------------------------------------------------
# 1. Comparison Operator Tests [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(30)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_equality_and_inequality_ecp():
    """EC1/EC2: Test value equality (==) and inequality (!=) on primitive types."""
    q = Query()
    q_eq = q.status == "active"
    q_ne = q.status != "active"

    assert q_eq({"status": "active"}) is True
    assert q_eq({"status": "pending"}) is False
    assert q_ne({"status": "pending"}) is True
    assert q_ne({"status": "active"}) is False


@pytest.mark.order(31)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.smoke
@pytest.mark.parametrize("value, expected_lt, expected_le, expected_eq, expected_ge, expected_gt", [
    (49, True,  True,  False, False, False),  # Just below boundary
    (50, False, True,  True,  True,  False),  # Exactly on boundary
    (51, False, False, False, True,  True),   # Just above boundary
])
def test_query_numeric_threshold_boundaries_bva(
    value, expected_lt, expected_le, expected_eq, expected_ge, expected_gt
):
    """BVA1-BVA3: Test 3-point boundary values around threshold = 50."""
    q = Query()
    doc = {"score": value}
    assert (q.score < 50)(doc) == expected_lt
    assert (q.score <= 50)(doc) == expected_le
    assert (q.score == 50)(doc) == expected_eq
    assert (q.score >= 50)(doc) == expected_ge
    assert (q.score > 50)(doc) == expected_gt


@pytest.mark.order(32)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_negative_and_zero_numbers_bva():
    """BVA4: Boundary analysis for negative numbers and zero."""
    q = Query()
    neg_doc = {"val": -5}
    zero_doc = {"val": 0}
    pos_doc = {"val": 5}

    assert (q.val < 0)(neg_doc) is True
    assert (q.val < 0)(zero_doc) is False
    assert (q.val <= 0)(zero_doc) is True
    assert (q.val >= 0)(zero_doc) is True
    assert (q.val > 0)(pos_doc) is True


@pytest.mark.order(33)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_floating_point_boundaries_bva():
    """BVA5: Floating point precision boundary testing."""
    q = Query()
    doc_zero = {"f": 0.0}
    doc_neg_zero = {"f": -0.0}
    doc_small = {"f": 0.000000001}

    assert (q.f == 0.0)(doc_zero) is True
    assert (q.f == 0.0)(doc_neg_zero) is True
    assert (q.f > 0.0)(doc_small) is True
    assert (q.f < 0.00000001)(doc_small) is True


@pytest.mark.order(34)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_missing_field_evaluates_false_safely_ecp():
    """EC3: Evaluating query against a document missing the key returns False."""
    q = Query()
    doc_without_key = {"other": 100}

    assert (q.missing_key == 42)(doc_without_key) is False
    assert (q.missing_key < 42)(doc_without_key) is False
    assert (q.missing_key > 42)(doc_without_key) is False
    assert (q.missing_key != 42)(doc_without_key) is False


@pytest.mark.order(35)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_type_mismatch_ecp():
    """EC4: Comparing incompatible types behaves safely without throwing."""
    q = Query()
    doc_str = {"val": "100"}

    # String compared to integer
    assert (q.val == 100)(doc_str) is False
    assert (q.val != 100)(doc_str) is True


# ---------------------------------------------------------------------------
# 2. Key Existence Tests [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(36)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_exists_present_and_absent_ecp():
    """EC19: exists() evaluates to True for present key, False for absent key."""
    q = Query()
    doc_with_key = {"username": "john"}
    doc_without_key = {"email": "john@example.com"}

    assert q.username.exists()(doc_with_key) is True
    assert q.username.exists()(doc_without_key) is False


@pytest.mark.order(37)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
@pytest.mark.parametrize("falsy_val", [None, False, 0, "", [], {}])
def test_query_exists_falsy_values_bva(falsy_val):
    """BVA12: exists() returns True even when key holds falsy / None values."""
    q = Query()
    doc = {"flag": falsy_val}
    assert q.flag.exists()(doc) is True


# ---------------------------------------------------------------------------
# 3. Boolean Algebra Combinators (&, |, ~) [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(38)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_boolean_and_operator_ecp():
    """EC5/EC6: Binary AND (&) requires both conditions to match."""
    q = Query()
    query = (q.role == "admin") & (q.level >= 5)

    assert query({"role": "admin", "level": 10}) is True
    assert query({"role": "admin", "level": 2}) is False
    assert query({"role": "guest", "level": 10}) is False
    assert query({"role": "guest", "level": 1}) is False


@pytest.mark.order(39)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_boolean_or_operator_ecp():
    """EC7: Binary OR (|) succeeds if either condition matches."""
    q = Query()
    query = (q.role == "admin") | (q.is_special == True)

    assert query({"role": "admin", "is_special": False}) is True
    assert query({"role": "user", "is_special": True}) is True
    assert query({"role": "admin", "is_special": True}) is True
    assert query({"role": "guest", "is_special": False}) is False


@pytest.mark.order(40)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_boolean_invert_operator_ecp():
    """EC8: Unary inversion (~) negates query result."""
    q = Query()
    query = ~(q.locked == True)

    assert query({"locked": False}) is True
    assert query({"locked": True}) is False
    # If key is absent, (q.locked == True) evaluates to False, so inversion is True
    assert query({"other": 1}) is True


@pytest.mark.order(41)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_de_morgans_laws_bva():
    """BVA / EC9: Verify De Morgan's Law: ~(A & B) == (~A | ~B)."""
    q = Query()
    doc1 = {"a": 1, "b": 1}
    doc2 = {"a": 1, "b": 2}
    doc3 = {"a": 2, "b": 2}

    cond_a = q.a == 1
    cond_b = q.b == 1

    lhs = ~(cond_a & cond_b)
    rhs = (~cond_a) | (~cond_b)

    for doc in [doc1, doc2, doc3]:
        assert lhs(doc) == rhs(doc)


@pytest.mark.order(42)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_empty_query_raises_runtime_error_ecp():
    """Verifies that an empty unconfigured Query() raises RuntimeError on evaluation."""
    empty_q = Query()
    with pytest.raises(RuntimeError, match="Empty query was evaluated"):
        empty_q({"field": "val"})


# ---------------------------------------------------------------------------
# 4. Task 3: CSV Data-Driven Parameterized Tests for Queries
# ---------------------------------------------------------------------------

@pytest.mark.order(43)
@pytest.mark.queries
@pytest.mark.csv_data
@pytest.mark.parametrize("row", load_csv_records("test_data_queries_mahmed.csv"))
def test_query_csv_data_driven_numeric_boundaries(row: dict[str, str]):
    """Task 3: Consume CSV test data to verify numeric boundary comparisons."""
    score = int(row["score"])
    threshold = int(row["threshold"])
    doc = {"score": score}
    q = Query()

    expected_lt = row["expected_lt"] == "True"
    expected_le = row["expected_le"] == "True"
    expected_eq = row["expected_eq"] == "True"
    expected_ge = row["expected_ge"] == "True"
    expected_gt = row["expected_gt"] == "True"

    assert (q.score < threshold)(doc) == expected_lt
    assert (q.score <= threshold)(doc) == expected_le
    assert (q.score == threshold)(doc) == expected_eq
    assert (q.score >= threshold)(doc) == expected_ge
    assert (q.score > threshold)(doc) == expected_gt
