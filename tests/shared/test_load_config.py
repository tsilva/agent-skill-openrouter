"""Tests for shared/load_config.py"""
import os
from pathlib import Path

from load_config import load_config, deep_merge, expand_env_vars


def test_basic_merge(temp_dir):
    """Merges configs with proper precedence."""
    defaults = temp_dir / "defaults.json"
    user = temp_dir / "user.json"
    project = temp_dir / "project.json"

    defaults.write_text('{"a": 1, "b": {"x": 10}}')
    user.write_text('{"b": {"y": 20}}')
    project.write_text('{"a": 100}')

    result = load_config(str(defaults), str(user), str(project))

    assert result["a"] == 100  # project overrides
    assert result["b"]["x"] == 10  # preserved from defaults
    assert result["b"]["y"] == 20  # preserved from user


def test_missing_files_handled(temp_dir):
    """Missing config files don't cause errors."""
    defaults = temp_dir / "defaults.json"
    defaults.write_text('{"key": "value"}')

    result = load_config(
        str(defaults),
        "/nonexistent/user.json",
        "/nonexistent/project.json"
    )

    assert result["key"] == "value"


def test_env_var_expansion(temp_dir):
    """Environment variables are expanded in values."""
    os.environ["TEST_CONFIG_VAR"] = "expanded_value"
    try:
        config = temp_dir / "config.json"
        config.write_text('{"path": "$TEST_CONFIG_VAR", "path2": "${TEST_CONFIG_VAR}"}')

        result = load_config(str(config))

        assert result["path"] == "expanded_value"
        assert result["path2"] == "expanded_value"
    finally:
        del os.environ["TEST_CONFIG_VAR"]


def test_env_var_missing_preserved(temp_dir):
    """Missing env vars are preserved in output."""
    config = temp_dir / "config.json"
    config.write_text('{"path": "$NONEXISTENT_VAR_XYZ"}')

    result = load_config(str(config))

    assert result["path"] == "$NONEXISTENT_VAR_XYZ"


def test_meta_sources(temp_dir):
    """Meta field tracks loaded sources."""
    defaults = temp_dir / "defaults.json"
    defaults.write_text('{"key": "value"}')

    result = load_config(str(defaults))

    assert "_meta" in result
    assert "defaults" in result["_meta"]["sources"]


def test_deep_merge_nested():
    """Deep merge handles nested dictionaries."""
    base = {"a": {"b": {"c": 1}}}
    override = {"a": {"b": {"d": 2}}}

    result = deep_merge(base, override)

    assert result["a"]["b"]["c"] == 1
    assert result["a"]["b"]["d"] == 2


def test_deep_merge_override_value():
    """Deep merge overrides values, not just adds."""
    base = {"a": 1}
    override = {"a": 2}

    result = deep_merge(base, override)

    assert result["a"] == 2


def test_expand_env_vars_nested():
    """Env var expansion works in nested structures."""
    os.environ["NESTED_TEST_VAR"] = "nested_value"
    try:
        data = {"outer": {"inner": "$NESTED_TEST_VAR"}}
        result = expand_env_vars(data)
        assert result["outer"]["inner"] == "nested_value"
    finally:
        del os.environ["NESTED_TEST_VAR"]


def test_expand_env_vars_list():
    """Env var expansion works in lists."""
    os.environ["LIST_TEST_VAR"] = "list_value"
    try:
        data = {"items": ["$LIST_TEST_VAR", "static"]}
        result = expand_env_vars(data)
        assert result["items"] == ["list_value", "static"]
    finally:
        del os.environ["LIST_TEST_VAR"]
