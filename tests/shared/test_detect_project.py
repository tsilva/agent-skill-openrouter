"""Tests for shared/detect_project.py"""
from pathlib import Path

from detect_project import detect_project, glob_match


def test_detect_nodejs(temp_dir):
    """Detects Node.js project from package.json."""
    (temp_dir / "package.json").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "nodejs"
    assert result["confidence"] == "high"


def test_detect_python_pyproject(temp_dir):
    """Detects Python project from pyproject.toml."""
    (temp_dir / "pyproject.toml").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "python"
    assert result["confidence"] == "high"


def test_detect_python_requirements(temp_dir):
    """Detects Python project from requirements.txt."""
    (temp_dir / "requirements.txt").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "python"
    assert result["confidence"] == "medium"


def test_detect_rust(temp_dir):
    """Detects Rust project from Cargo.toml."""
    (temp_dir / "Cargo.toml").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "rust"
    assert result["confidence"] == "high"


def test_detect_go(temp_dir):
    """Detects Go project from go.mod."""
    (temp_dir / "go.mod").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "go"
    assert result["confidence"] == "high"


def test_detect_java_maven(temp_dir):
    """Detects Java project from pom.xml."""
    (temp_dir / "pom.xml").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "java"
    assert result["confidence"] == "high"


def test_detect_c_makefile(temp_dir):
    """Detects C project from Makefile (low confidence)."""
    (temp_dir / "Makefile").touch()
    result = detect_project(temp_dir)
    assert result["type"] == "c"
    assert result["confidence"] == "low"


def test_detect_unknown(temp_dir):
    """Returns unknown for empty directory."""
    result = detect_project(temp_dir)
    assert result["type"] == "unknown"
    assert result["confidence"] == "none"


def test_detect_not_directory():
    """Returns error for non-directory path."""
    result = detect_project(Path("/nonexistent/path"))
    assert result["type"] == "unknown"
    assert "error" in result


def test_glob_match_exact():
    """Matches exact file names."""
    files = ["package.json", "README.md", "index.js"]
    assert glob_match("package.json", files) == ["package.json"]
    assert glob_match("nonexistent", files) == []


def test_glob_match_extension():
    """Matches *.ext patterns."""
    files = ["app.csproj", "lib.csproj", "README.md"]
    assert glob_match("*.csproj", files) == ["app.csproj", "lib.csproj"]
