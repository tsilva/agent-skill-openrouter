"""Shared pytest fixtures for claudeskillz tests."""
import sys
import tempfile
from pathlib import Path

import pytest

# Add shared directory to path for imports
REPO_ROOT = Path(__file__).parents[1]
SHARED_DIR = REPO_ROOT / "shared"
sys.path.insert(0, str(SHARED_DIR))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_repo(temp_dir):
    """Create a mock git repository."""
    repo = temp_dir / "test-repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    return repo


@pytest.fixture
def mock_readme(mock_repo):
    """Create a mock README.md in a repo."""
    readme = mock_repo / "README.md"
    readme.write_text("# Test Project\n\nA simple test project for testing.")
    return readme
