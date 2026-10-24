"""
Unit tests for JSONStorage in tinydb.storages
Author: Wabil Rehman (Wabil-Rehman / Wabilrehman2626@gmail.com)
Covers: File initialization, 0-byte empty file handling, read/write serialization,
file truncation on smaller payload, closed file handle boundaries, and access modes.
"""

from pathlib import Path
import json
import pytest

from tinydb.storages import JSONStorage


# ---------------------------------------------------------------------------
# JSONStorage Lifecycle and Boundary Tests [ECP & BVA]
# ---------------------------------------------------------------------------

@pytest.mark.order(160)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.smoke
def test_jsonstorage_read_empty_0_byte_file_returns_none_bva(tmp_path: Path):
    """BVA4 / EC6: A newly created 0-byte file returns None on read()."""
    db_file = tmp_path / "empty_db.json"
    storage = JSONStorage(str(db_file), create_dirs=True)
    try:
        assert storage.read() is None
        assert db_file.exists()
        assert db_file.stat().st_size == 0
    finally:
        storage.close()


@pytest.mark.order(161)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.smoke
def test_jsonstorage_write_and_read_persistence_ecp(tmp_path: Path):
    """EC7: Write dictionary state, flush to disk, and read back identical data."""
    db_file = tmp_path / "valid_db.json"
    storage = JSONStorage(str(db_file), create_dirs=True)
    data = {
        "_default": {
            "1": {"product": "Server", "cores": 64},
            "2": {"product": "Switch", "ports": 48}
        }
    }
    try:
        storage.write(data)
        read_data = storage.read()
        assert read_data == data
        assert read_data["_default"]["1"]["cores"] == 64
    finally:
        storage.close()


@pytest.mark.order(162)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_jsonstorage_overwrite_smaller_payload_truncates_file_bva(tmp_path: Path):
    """BVA5: Overwriting a large payload with a significantly smaller payload truncates file."""
    db_file = tmp_path / "truncate_db.json"
    storage = JSONStorage(str(db_file), create_dirs=True)
    try:
        large_payload = {
            "_default": {str(i): {"data": "X" * 200, "idx": i} for i in range(1, 50)}
        }
        storage.write(large_payload)
        large_size = db_file.stat().st_size

        small_payload = {"_default": {"1": {"data": "tiny"}}}
        storage.write(small_payload)
        small_size = db_file.stat().st_size

        # File size must shrink and data must parse cleanly without trailing garbage
        assert small_size < large_size
        assert storage.read() == small_payload
    finally:
        storage.close()


@pytest.mark.order(163)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.regression
def test_jsonstorage_readonly_mode_write_raises_ioerror_ecp(tmp_path: Path):
    """EC9: Attempting to write to a storage opened in read-only mode 'r' raises IOError."""
    db_file = tmp_path / "readonly_db.json"
    # Pre-populate with valid JSON
    db_file.write_text(json.dumps({"_default": {}}), encoding="utf-8")

    ro_storage = JSONStorage(str(db_file), access_mode="r")
    try:
        assert ro_storage.read() == {"_default": {}}
        with pytest.raises(IOError, match='Cannot write to the database'):
            ro_storage.write({"_default": {"1": {"bad": True}}})
    finally:
        ro_storage.close()


@pytest.mark.order(164)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_jsonstorage_operations_on_closed_handle_raise_error_bva(tmp_path: Path):
    """BVA6: Performing read or write on a closed JSONStorage handle raises ValueError."""
    db_file = tmp_path / "closed_db.json"
    storage = JSONStorage(str(db_file), create_dirs=True)
    storage.write({"_default": {"1": {"v": 1}}})
    storage.close()

    with pytest.raises(ValueError, match="I/O operation on closed file"):
        storage.read()

    with pytest.raises(ValueError, match="I/O operation on closed file"):
        storage.write({"_default": {"1": {"v": 2}}})


@pytest.mark.order(165)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_jsonstorage_utf8_unicode_encoding_bva(tmp_path: Path):
    """EC8 / BVA: Writing and reading international multi-byte UTF-8 unicode text."""
    db_file = tmp_path / "unicode_db.json"
    storage = JSONStorage(str(db_file), create_dirs=True, encoding="utf-8")
    unicode_payload = {
        "_default": {
            "1": {
                "greeting_ur": "ہیلو دنیا",
                "greeting_zh": "你好，世界",
                "greeting_de": "Grüße Schön",
                "symbols": "⭐🔥⚡🛡️"
            }
        }
    }
    try:
        storage.write(unicode_payload)
        read_back = storage.read()
        assert read_back == unicode_payload
        assert read_back["_default"]["1"]["greeting_ur"] == "ہیلو دنیا"
        assert read_back["_default"]["1"]["symbols"] == "⭐🔥⚡🛡️"
    finally:
        storage.close()


@pytest.mark.order(166)
@pytest.mark.storages
@pytest.mark.ecp
@pytest.mark.regression
def test_jsonstorage_with_formatting_kwargs(tmp_path: Path):
    """BVA7: Custom serializer kwargs such as indent and sort_keys."""
    db_file = tmp_path / "formatted_db.json"
    storage = JSONStorage(str(db_file), create_dirs=True, indent=2, sort_keys=True)
    payload = {
        "_default": {
            "b": {"name": "Second"},
            "a": {"name": "First"}
        }
    }
    try:
        storage.write(payload)
        content = db_file.read_text(encoding="utf-8")
        # Indented JSON has newlines and spaces
        assert "\n" in content
        assert '  "_default"' in content
        assert storage.read() == payload
    finally:
        storage.close()


@pytest.mark.order(167)
@pytest.mark.storages
@pytest.mark.boundary
@pytest.mark.regression
def test_jsonstorage_invalid_access_mode_warning(tmp_path: Path):
    """EC11: Opening JSONStorage with unconventional mode emits warning."""
    db_file = tmp_path / "warn_db.json"
    with pytest.warns(UserWarning, match="Using an `access_mode` other than"):
        storage = JSONStorage(str(db_file), access_mode="w", create_dirs=True)
        storage.close()
