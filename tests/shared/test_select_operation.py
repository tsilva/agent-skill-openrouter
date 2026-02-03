"""Tests for shared/select_operation.py"""
from pathlib import Path

from select_operation import select_operation, parse_keywords, SKILL_RULES


def test_explicit_keyword_validate():
    """Explicit validate keyword detected."""
    result = select_operation("readme", "please validate this", [], Path("."))
    assert result["operation"] == "validate"
    assert result["source"] == "argument_keyword"


def test_explicit_keyword_create():
    """Explicit create keyword detected."""
    result = select_operation("readme", "create a new readme", [], Path("."))
    assert result["operation"] == "create"


def test_explicit_keyword_optimize():
    """Explicit optimize keyword detected."""
    result = select_operation("readme", "improve the readme", [], Path("."))
    assert result["operation"] == "optimize"


def test_file_exists_modify(temp_dir):
    """File exists defaults to modify operation."""
    (temp_dir / "README.md").touch()
    result = select_operation("readme", "", ["README.md"], temp_dir)
    assert result["operation"] == "modify"
    assert result["source"] == "file_state"


def test_file_missing_create(temp_dir):
    """Missing file defaults to create operation."""
    result = select_operation("readme", "", ["README.md"], temp_dir)
    assert result["operation"] == "create"
    assert result["source"] == "file_state"


def test_keyword_overrides_file_state(temp_dir):
    """Explicit keyword overrides file state."""
    (temp_dir / "README.md").touch()
    result = select_operation("readme", "create a new readme", ["README.md"], temp_dir)
    assert result["operation"] == "create"


def test_unknown_skill():
    """Unknown skill returns error."""
    result = select_operation("unknown-skill", "", [], Path("."))
    assert result.get("error") is True
    assert "valid_skills" in result


def test_repo_maintain_operations():
    """repo-maintain skill has correct operations."""
    result = select_operation("repo-maintain", "audit repos", [], Path("."))
    assert result["operation"] == "audit"

    result = select_operation("repo-maintain", "fix issues", [], Path("."))
    assert result["operation"] == "fix"


def test_project_logo_author_operations(temp_dir):
    """project-logo-author skill operations."""
    # Missing logo -> create
    result = select_operation("project-logo-author", "", ["logo.png"], temp_dir)
    assert result["operation"] == "create"

    # Existing logo -> regenerate
    (temp_dir / "logo.png").touch()
    result = select_operation("project-logo-author", "", ["logo.png"], temp_dir)
    assert result["operation"] == "regenerate"


def test_parse_keywords_match():
    """parse_keywords matches whole words."""
    keywords = {"validate": "validate", "check": "validate"}
    assert parse_keywords("validate this", keywords) == "validate"
    assert parse_keywords("please check it", keywords) == "validate"


def test_parse_keywords_no_match():
    """parse_keywords returns None for no match."""
    keywords = {"validate": "validate"}
    assert parse_keywords("do something else", keywords) is None
    assert parse_keywords("", keywords) is None


def test_skill_rules_defined():
    """All expected skills have rules."""
    expected_skills = ["readme", "project-readme-author", "repo-maintain",
                       "claude-skill-author", "project-logo-author"]
    for skill in expected_skills:
        assert skill in SKILL_RULES, f"Missing rules for {skill}"
