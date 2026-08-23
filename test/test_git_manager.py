import pytest
import os
import shutil
import tempfile
import time
from pathlib import Path
from agent.git.manager import GitManager


def force_remove(path):
    """Force la suppression d'un dossier même si des fichiers sont verrouillés."""
    if not os.path.exists(path):
        return
    try:
        shutil.rmtree(path)
    except PermissionError:
        # Sur Windows, on attend un peu et on réessaie
        time.sleep(0.5)
        try:
            shutil.rmtree(path)
        except PermissionError:
            # Fallback : on renomme le dossier avant de supprimer
            import uuid
            temp_name = f"{path}_{uuid.uuid4().hex}"
            os.rename(path, temp_name)
            shutil.rmtree(temp_name, ignore_errors=True)


@pytest.fixture
def repo_path():
    """Crée un dossier temporaire pour les tests Git."""
    path = tempfile.mkdtemp()
    yield Path(path)
    force_remove(path)


@pytest.fixture
def git(repo_path):
    """Retourne un GitManager initialisé."""
    return GitManager(repo_path)


def test_init_creates_repo(git, repo_path):
    result = git.init()
    assert "Initialized" in result or "already initialized"
    assert (repo_path / ".git").exists()


def test_add_and_status(git, repo_path):
    git.init()

    test_file = repo_path / "test.txt"
    test_file.write_text("Hello")

    git.add("test.txt")
    status = git.status()
    assert "test.txt" in status or "No changes" not in status


def test_commit_and_log(git, repo_path):
    git.init()

    test_file = repo_path / "test.txt"
    test_file.write_text("Hello")

    git.add("test.txt")
    git.commit("Test commit")

    log = git.log()
    assert "Test commit" in log


def test_status_no_changes(git, repo_path):
    git.init()
    status = git.status()
    assert status == "No changes" or status.strip() == ""


def test_diff_no_changes(git, repo_path):
    git.init()
    diff = git.diff()
    assert diff == "No differences" or diff.strip() == ""


def test_branch_after_init(git):
    git.init()
    branch = git.branch()
    assert branch == "main" or branch == "master"


def test_is_repo_returns_false_in_non_repo(repo_path):
    git = GitManager(repo_path)
    assert not git.is_repo()


def test_is_repo_returns_true_after_init(git):
    git.init()
    assert git.is_repo()