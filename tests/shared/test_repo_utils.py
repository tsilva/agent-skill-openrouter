"""Tests for shared/repo_utils.py"""
from pathlib import Path

from repo_utils import find_repos


def test_find_repos_empty_dir(temp_dir):
    """Empty directory returns empty list."""
    assert find_repos(temp_dir) == []


def test_find_repos_non_existent():
    """Non-existent path returns empty list."""
    assert find_repos(Path("/nonexistent/path/that/does/not/exist")) == []


def test_find_repos_detects_git(mock_repo, temp_dir):
    """Detects directories with .git folder."""
    repos = find_repos(temp_dir)
    assert len(repos) == 1
    assert repos[0].name == "test-repo"


def test_find_repos_ignores_non_git(temp_dir):
    """Ignores directories without .git folder."""
    non_repo = temp_dir / "not-a-repo"
    non_repo.mkdir()

    repos = find_repos(temp_dir)
    assert repos == []


def test_find_repos_sorts_case_insensitive(temp_dir):
    """Repositories sorted case-insensitively."""
    for name in ["Zebra", "alpha", "BETA"]:
        repo = temp_dir / name
        repo.mkdir()
        (repo / ".git").mkdir()

    repos = find_repos(temp_dir)
    names = [r.name for r in repos]
    assert names == ["alpha", "BETA", "Zebra"]


def test_find_repos_multiple(temp_dir):
    """Finds multiple repos correctly."""
    for name in ["repo-alpha", "repo-beta", "repo-gamma"]:
        repo = temp_dir / name
        repo.mkdir()
        (repo / ".git").mkdir()

    # Also add a non-repo
    (temp_dir / "not-a-repo").mkdir()

    repos = find_repos(temp_dir)
    assert len(repos) == 3
    names = [r.name for r in repos]
    assert names == ["repo-alpha", "repo-beta", "repo-gamma"]
