"""
Unit tests for Query and QueryInstance classes in tinydb.queries
Author: Wabil Rehman (Wabil-Rehman / Wabilrehman2626@gmail.com)
Covers: matches, search, regex flags, any, all, one_of, test, nested field paths,
and CSV data-driven tests.
"""

import re
import pytest

from tinydb import Query
from tests.conftest import load_csv_records


# ---------------------------------------------------------------------------
# 1. Regex Matching Tests (matches, search) [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(130)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_matches_regex_full_match_ecp():
    """EC10: matches() performs anchored regular expression matching."""
    q = Query()
    matcher = q.serial.matches(r"^SN-\d{4}$")

    assert matcher({"serial": "SN-1234"}) is True
    assert matcher({"serial": "SN-123"}) is False      # Length boundary
    assert matcher({"serial": "X-SN-1234-Y"}) is False # Unanchored failure


@pytest.mark.order(131)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_search_regex_substring_ecp():
    """EC11: search() succeeds on unanchored substring regex matches."""
    q = Query()
    searcher = q.description.search(r"error:\s*\d+")

    assert searcher({"description": "Server returned error: 404 not found"}) is True
    assert searcher({"description": "All systems operational"}) is False


@pytest.mark.order(132)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
@pytest.mark.parametrize("non_string_val", [123, 45.67, True, None, [], {}])
def test_query_regex_non_string_returns_false_safely_bva(non_string_val):
    """EC12: Regex operations on non-string fields safely return False without error."""
    q = Query()
    assert q.field.matches(r"^\d+$")({"field": non_string_val}) is False
    assert q.field.search(r"\d+")({"field": non_string_val}) is False


@pytest.mark.order(133)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_matches_with_regex_flags_bva():
    """EC13: matches() respects regular expression flags (e.g. re.IGNORECASE)."""
    q = Query()
    case_insensitive = q.code.matches(r"^token-[a-z]+$", flags=re.IGNORECASE)

    assert case_insensitive({"code": "TOKEN-XYZ"}) is True
    assert case_insensitive({"code": "token-xyz"}) is True
    assert case_insensitive({"code": "token-123"}) is False


# ---------------------------------------------------------------------------
# 2. Collection & Sequence Predicates (any, all, one_of) [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(134)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_one_of_membership_ecp():
    """EC14: one_of() validates value inclusion within a specified candidate list."""
    q = Query()
    role_check = q.role.one_of(["admin", "moderator", "owner"])

    assert role_check({"role": "admin"}) is True
    assert role_check({"role": "owner"}) is True
    assert role_check({"role": "guest"}) is False


@pytest.mark.order(135)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_one_of_empty_list_boundary_bva():
    """EC15: one_of([]) with empty candidate list always returns False."""
    q = Query()
    assert q.role.one_of([])({"role": "admin"}) is False


@pytest.mark.order(136)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_any_callable_and_sequence_ecp():
    """EC16: any() succeeds when at least one element satisfies condition."""
    q = Query()
    # Any with a nested query condition
    has_admin = q.roles.any(Query().name == "admin")
    assert has_admin({"roles": [{"name": "guest"}, {"name": "admin"}]}) is True
    assert has_admin({"roles": [{"name": "guest"}]}) is False

    # Any with a value list
    has_numeric_tag = q.tags.any([10, 20, 30])
    assert has_numeric_tag({"tags": [5, 10, 15]}) is True
    assert has_numeric_tag({"tags": [1, 2, 3]}) is False


@pytest.mark.order(137)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_any_empty_sequence_and_non_sequence_bva():
    """BVA10: any() on empty list or non-sequence returns False."""
    q = Query()
    assert q.items.any([1, 2])({"items": []}) is False
    assert q.items.any([1, 2])({"items": 999}) is False


@pytest.mark.order(138)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_all_callable_and_sequence_ecp():
    """EC17: all() requires every element in list to satisfy condition."""
    q = Query()
    all_positive = q.scores.all(Query().val > 0)

    assert all_positive({"scores": [{"val": 1}, {"val": 5}]}) is True
    assert all_positive({"scores": [{"val": 1}, {"val": -2}]}) is False


@pytest.mark.order(139)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_all_empty_sequence_vacuous_truth_bva():
    """BVA: all() on empty sequence [] returns True under vacuous truth."""
    q = Query()
    assert q.scores.all(Query().val > 0)({"scores": []}) is True


# ---------------------------------------------------------------------------
# 3. Custom Predicate (test) and Nested Field Traversal [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(140)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.smoke
def test_query_custom_test_callable_ecp():
    """EC20: test() executes arbitrary user-defined callable predicate."""
    def is_even_positive(val):
        return isinstance(val, int) and val > 0 and val % 2 == 0

    q = Query()
    even_checker = q.num.test(is_even_positive)

    assert even_checker({"num": 4}) is True
    assert even_checker({"num": 7}) is False
    assert even_checker({"num": -2}) is False
    assert even_checker({"num": "4"}) is False


@pytest.mark.order(141)
@pytest.mark.queries
@pytest.mark.ecp
@pytest.mark.regression
def test_query_custom_test_with_extra_arguments_ecp():
    """EC21: test() correctly forwards extra frozen arguments to callback."""
    def in_range(val, low, high):
        return low <= val <= high

    q = Query()
    range_checker = q.age.test(in_range, 18, 65)

    assert range_checker({"age": 25}) is True
    assert range_checker({"age": 18}) is True
    assert range_checker({"age": 65}) is True
    assert range_checker({"age": 16}) is False
    assert range_checker({"age": 70}) is False


@pytest.mark.order(142)
@pytest.mark.queries
@pytest.mark.boundary
@pytest.mark.regression
def test_query_nested_path_traversal_dot_and_bracket_bva():
    """BVA13: Multi-level nested field resolution using dot and bracket syntax."""
    q = Query()
    dot_query = q.company.dept.team.lead == "Alice"
    bracket_query = q["company"]["dept"]["team"]["lead"] == "Alice"

    matching_doc = {
        "company": {
            "dept": {
                "team": {
                    "lead": "Alice"
                }
            }
        }
    }
    non_matching_doc = {
        "company": {
            "dept": {
                "team": {
                    "lead": "Bob"
                }
            }
        }
    }
    broken_path_doc = {"company": {"dept": "engineering"}}

    assert dot_query(matching_doc) is True
    assert bracket_query(matching_doc) is True
    assert dot_query(non_matching_doc) is False
    assert dot_query(broken_path_doc) is False


# ---------------------------------------------------------------------------
# 4. Task 3: CSV Data-Driven Parameterized Tests for Queries (Wabil)
# ---------------------------------------------------------------------------

@pytest.mark.order(143)
@pytest.mark.queries
@pytest.mark.csv_data
@pytest.mark.parametrize("row", load_csv_records("test_data_queries_wabil.csv"))
def test_query_csv_data_driven_regex_matching_wabil(row: dict[str, str]):
    """Task 3: Consume CSV test data to verify regex pattern matching against inputs."""
    input_str = row["input_string"]
    pattern = row["pattern"]
    expected_match = row["expected_match"] == "True"
    expected_search = row["expected_search"] == "True"

    q = Query()
    doc = {"text": input_str}

    assert q.text.matches(pattern)(doc) == expected_match
    assert q.text.search(pattern)(doc) == expected_search
