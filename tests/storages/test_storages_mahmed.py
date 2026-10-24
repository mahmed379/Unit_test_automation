"""
Unit tests for MemoryStorage in tinydb.storages
Author: Mohammad Ahmed (mahmed379 / mohammadahmed41235@gmail.com)
Covers: MemoryStorage lifecycle, empty state boundaries, nested JSON types,
unicode persistence, idempotence, and instance isolation.
"""

import pytest

from tinydb.storages import MemoryStorage


@pytest.fixture
def mem_storage() -> MemoryStorage:
    """Fixture returning a fresh MemoryStorage instance."""
    return MemoryStorage()


# ---------------------------------------------------------------------------
# MemoryStorage Lifecycle and Boundary Tests [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(50)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.smoke
def test_memorystorage_initial_read_is_none_ecp(mem_storage: MemoryStorage):
    """EC1: An unwritten MemoryStorage instance must return None on read()."""
    assert mem_storage.read() is None


@pytest.mark.order(51)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.smoke
def test_memorystorage_write_and_read_dict_ecp(mem_storage: MemoryStorage):
    """EC2: Writing dictionary state persists and is retrieved identically."""
    data = {
        "_default": {
            "1": {"title": "Software Testing", "credits": 3},
            "2": {"title": "Operating Systems", "credits": 4}
        }
    }
    mem_storage.write(data)
    read_data = mem_storage.read()
    assert read_data == data
    assert read_data["_default"]["1"]["credits"] == 3


@pytest.mark.order(52)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_memorystorage_write_empty_dict_bva(mem_storage: MemoryStorage):
    """BVA1: Writing an empty dict {} returns {} on read(), distinct from None."""
    mem_storage.write({})
    read_data = mem_storage.read()
    assert read_data == {}
    assert read_data is not None


@pytest.mark.order(53)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_memorystorage_idempotent_multiple_reads_bva(mem_storage: MemoryStorage):
    """BVA2: Consecutive read operations without intermediate writes are idempotent."""
    payload = {"_default": {"1": {"sensor": "temp", "val": 24.5}}}
    mem_storage.write(payload)

    first_read = mem_storage.read()
    second_read = mem_storage.read()
    third_read = mem_storage.read()

    assert first_read == second_read == third_read == payload


@pytest.mark.order(54)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.regression
def test_memorystorage_overwrite_updates_state_ecp(mem_storage: MemoryStorage):
    """EC3: Successive write calls overwrite prior in-memory state cleanly."""
    initial_data = {"_default": {"1": {"version": 1}}}
    updated_data = {"_default": {"1": {"version": 2}, "2": {"version": 1}}}

    mem_storage.write(initial_data)
    assert mem_storage.read() == initial_data

    mem_storage.write(updated_data)
    assert mem_storage.read() == updated_data


@pytest.mark.order(55)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.regression
def test_memorystorage_close_safe_noop_ecp(mem_storage: MemoryStorage):
    """EC4: Calling close() on MemoryStorage does not corrupt memory or raise errors."""
    mem_storage.write({"_default": {"1": {"active": True}}})
    mem_storage.close()
    # Memory remains readable after close
    assert mem_storage.read() == {"_default": {"1": {"active": True}}}


@pytest.mark.order(56)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_memorystorage_nested_complex_json_types_bva(mem_storage: MemoryStorage):
    """BVA3: Complex nested JSON structures including lists, booleans, None."""
    complex_data = {
        "_default": {
            "1": {
                "metadata": {
                    "tags": ["unit-test", "automation", "python"],
                    "enabled": True,
                    "score": 99.95,
                    "notes": None
                }
            }
        }
    }
    mem_storage.write(complex_data)
    result = mem_storage.read()
    assert result == complex_data
    assert result["_default"]["1"]["metadata"]["tags"] == ["unit-test", "automation", "python"]
    assert result["_default"]["1"]["metadata"]["notes"] is None


@pytest.mark.order(57)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_memorystorage_unicode_characters_bva(mem_storage: MemoryStorage):
    """BVA: Multi-language unicode characters (Arabic, Japanese, Emoji) in memory."""
    unicode_data = {
        "_default": {
            "1": {
                "english": "Hello World",
                "arabic": "مرحبا بالعالم",
                "japanese": "こんにちは世界",
                "emoji": "🚀🎉✅"
            }
        }
    }
    mem_storage.write(unicode_data)
    result = mem_storage.read()
    assert result == unicode_data
    assert result["_default"]["1"]["arabic"] == "مرحبا بالعالم"
    assert result["_default"]["1"]["emoji"] == "🚀🎉✅"


@pytest.mark.order(58)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_memorystorage_instance_isolation_bva():
    """BVA: Two independent MemoryStorage instances do not share state."""
    storage1 = MemoryStorage()
    storage2 = MemoryStorage()

    storage1.write({"_default": {"1": {"instance": 1}}})
    storage2.write({"_default": {"1": {"instance": 2}}})

    assert storage1.read()["_default"]["1"]["instance"] == 1
    assert storage2.read()["_default"]["1"]["instance"] == 2
