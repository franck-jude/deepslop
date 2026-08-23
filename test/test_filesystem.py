import pytest
from pathlib import Path
from agent.io.filesystem import (
    write_file,
    read_file,
    ensure_dir,
    backup_file,
    restore_file,
    file_exists,
    delete_file,
)

def test_write_and_read_file(tmp_path):
    filepath = tmp_path / "test.txt"
    content = "Hello, Vic Viper!"

    write_file(filepath, content)
    assert filepath.exists()
    assert read_file(filepath) == content

def test_ensure_dir_creates_parents(tmp_path):
    path = tmp_path / "a" / "b" / "c" / "file.txt"
    ensure_dir(path)
    assert path.parent.exists()

def test_backup_and_restore_file(tmp_path):
    filepath = tmp_path / "data.txt"
    write_file(filepath, "v1")

    backup_path = backup_file(filepath, backup_dir=tmp_path / "backups")
    assert backup_path.exists()

    write_file(filepath, "v2")
    restore_file(filepath, backup_path)

    assert read_file(filepath) == "v1"

def test_file_exists(tmp_path):
    filepath = tmp_path / "exists.txt"
    assert not file_exists(filepath)
    write_file(filepath, "test")
    assert file_exists(filepath)

def test_delete_file(tmp_path):
    filepath = tmp_path / "to_delete.txt"
    write_file(filepath, "test")
    assert file_exists(filepath)
    delete_file(filepath)
    assert not file_exists(filepath)