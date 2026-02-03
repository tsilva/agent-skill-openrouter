"""Tests for shared/substitute_template.py"""
from substitute_template import substitute, find_placeholders


def test_basic_substitution():
    """Basic variable substitution works."""
    content = "Hello {NAME}, welcome to {PROJECT}!"
    variables = {"NAME": "Alice", "PROJECT": "TestApp"}
    result, missing = substitute(content, variables)

    assert result == "Hello Alice, welcome to TestApp!"
    assert missing == []


def test_missing_variable():
    """Missing variables are detected and preserved."""
    content = "Hello {NAME}, your {ROLE} is ready"
    variables = {"NAME": "Bob"}
    result, missing = substitute(content, variables)

    assert "ROLE" in missing
    assert "{ROLE}" in result
    assert "Bob" in result


def test_no_placeholders():
    """Text without placeholders unchanged."""
    content = "Plain text without placeholders"
    result, missing = substitute(content, {"UNUSED": "value"})

    assert result == content
    assert missing == []


def test_multiple_occurrences():
    """Same placeholder replaced everywhere."""
    content = "{NAME} said hello. {NAME} left."
    variables = {"NAME": "Charlie"}
    result, missing = substitute(content, variables)

    assert result == "Charlie said hello. Charlie left."


def test_case_sensitivity():
    """Only uppercase placeholders are replaced."""
    content = "Hello {name} and {NAME}"
    variables = {"NAME": "Dave"}
    result, missing = substitute(content, variables)

    assert "{name}" in result  # lowercase preserved
    assert "Dave" in result


def test_find_placeholders():
    """Finds all uppercase placeholders."""
    content = "Hello {NAME}, welcome to {PROJECT}! See {name} too."
    placeholders = find_placeholders(content)

    assert "NAME" in placeholders
    assert "PROJECT" in placeholders
    assert "name" not in placeholders  # lowercase not detected


def test_placeholder_with_numbers():
    """Placeholders can contain numbers."""
    content = "Value is {VAR1} and {VAR2}"
    placeholders = find_placeholders(content)

    assert "VAR1" in placeholders
    assert "VAR2" in placeholders


def test_placeholder_with_underscores():
    """Placeholders can contain underscores."""
    content = "Path: {BASE_PATH}/{SUB_DIR}"
    variables = {"BASE_PATH": "/home", "SUB_DIR": "data"}
    result, missing = substitute(content, variables)

    assert result == "Path: /home/data"


def test_empty_content():
    """Empty content returns empty."""
    result, missing = substitute("", {"NAME": "Test"})
    assert result == ""
    assert missing == []


def test_missing_sorted():
    """Missing variables returned sorted."""
    content = "{ZEBRA} {ALPHA} {BETA}"
    result, missing = substitute(content, {})

    assert missing == ["ALPHA", "BETA", "ZEBRA"]
