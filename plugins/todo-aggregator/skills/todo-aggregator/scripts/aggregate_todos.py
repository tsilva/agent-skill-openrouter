#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
TODO Aggregator - Collect and consolidate TODO files from multiple repos.

Scans a repos directory for TODO and TODO.md files at each repo root,
then generates a consolidated markdown report.

Usage:
    uv run aggregate_todos.py --repos-dir /path/to/repos
    uv run aggregate_todos.py --repos-dir /path/to/repos --operation list
    uv run aggregate_todos.py --repos-dir /path/to/repos --output report.md
"""

import argparse
import fnmatch
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def load_config(config_path: Path) -> dict:
    """Load config from JSON file, return empty dict if missing."""
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not parse config {config_path}: {e}", file=sys.stderr)
    return {}


def should_include_repo(repo_name: str, config: dict) -> bool:
    """Check if repo should be included based on config filters."""
    include_patterns = config.get("include", [])
    exclude_patterns = config.get("exclude", [])

    # If include list is set, repo must match at least one pattern
    if include_patterns:
        matched = any(fnmatch.fnmatch(repo_name, pattern) for pattern in include_patterns)
        if not matched:
            return False

    # Check exclude patterns
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(repo_name, pattern):
            return False

    return True


def find_todo_file(repo_path: Path) -> Optional[Path]:
    """Find TODO file in repo root. Prefer TODO.md over TODO."""
    todo_md = repo_path / "TODO.md"
    todo = repo_path / "TODO"

    if todo_md.exists() and todo_md.is_file():
        return todo_md
    if todo.exists() and todo.is_file():
        return todo
    return None


def parse_tasks(content: str) -> list[str]:
    """
    Extract task lines from content.

    Recognizes:
    - [ ] Incomplete task
    - [x] Completed task
    - Plain bullet items (treated as-is)
    """
    tasks = []
    for line in content.splitlines():
        stripped = line.strip()
        # Match checkbox tasks: - [ ], - [x], - [X]
        if re.match(r"^-\s*\[[xX ]\]", stripped):
            tasks.append(stripped)
        # Match plain bullets that look like tasks (start with "- " but not a nested list indicator)
        elif re.match(r"^-\s+\S", stripped) and not stripped.startswith("- -"):
            # Convert plain bullets to unchecked checkboxes for consistency
            task_text = stripped[2:].strip()  # Remove "- "
            tasks.append(f"- [ ] {task_text}")
    return tasks


def scan_repos(repos_dir: Path, config: dict) -> dict[str, dict]:
    """
    Scan repos directory and collect TODO files.

    Returns dict mapping repo name to {path, todo_file, tasks}.
    """
    results = {}

    if not repos_dir.is_dir():
        print(f"Error: {repos_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    for entry in sorted(repos_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue

        repo_name = entry.name

        if not should_include_repo(repo_name, config):
            continue

        todo_file = find_todo_file(entry)
        if todo_file:
            try:
                content = todo_file.read_text(encoding="utf-8")
                tasks = parse_tasks(content)
                results[repo_name] = {
                    "path": str(entry),
                    "todo_file": todo_file.name,
                    "tasks": tasks,
                }
            except OSError as e:
                print(f"Warning: Could not read {todo_file}: {e}", file=sys.stderr)

    return results


def generate_markdown(repos_data: dict[str, dict]) -> str:
    """Generate consolidated markdown report."""
    lines = [
        "# Aggregated TODOs",
        "",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d')}",
        "",
    ]

    if not repos_data:
        lines.append("*No TODO files found.*")
        return "\n".join(lines)

    for repo_name, data in repos_data.items():
        lines.append(f"## {repo_name}")
        lines.append("")

        if data["tasks"]:
            for task in data["tasks"]:
                lines.append(task)
        else:
            lines.append("*No tasks found in TODO file.*")

        lines.append("")

    return "\n".join(lines)


def list_repos(repos_data: dict[str, dict]) -> str:
    """Generate list of repos with TODO files."""
    lines = ["Repos with TODO files:"]

    if not repos_data:
        lines.append("  (none found)")
        return "\n".join(lines)

    for repo_name, data in repos_data.items():
        lines.append(f"- {repo_name} ({data['todo_file']})")

    return "\n".join(lines)


def main():
    # Handle --test early before full argument parsing
    if "--test" in sys.argv:
        run_tests()
        return

    parser = argparse.ArgumentParser(
        description="Aggregate TODO files from multiple repos"
    )
    parser.add_argument(
        "--repos-dir",
        required=True,
        help="Path to repos folder",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--operation",
        choices=["aggregate", "list"],
        default="aggregate",
        help="Operation to perform (default: aggregate)",
    )
    parser.add_argument(
        "--config",
        help="Path to config file (default: {repos-dir}/.todo-aggregator.json)",
    )

    args = parser.parse_args()

    repos_dir = Path(args.repos_dir).expanduser().resolve()

    # Load config
    if args.config:
        config_path = Path(args.config).expanduser().resolve()
    else:
        config_path = repos_dir / ".todo-aggregator.json"

    config = load_config(config_path)

    # Scan repos
    repos_data = scan_repos(repos_dir, config)

    # Generate output
    if args.operation == "list":
        output = list_repos(repos_data)
    else:
        output = generate_markdown(repos_data)

    # Write output
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.write_text(output, encoding="utf-8")
        print(f"Report written to {output_path}", file=sys.stderr)
    else:
        print(output)


def run_tests():
    """Self-tests for the module."""
    import tempfile
    import shutil

    print("Running self-tests...")

    # Test parse_tasks
    content = """# My TODO

- [ ] Incomplete task
- [x] Completed task
- [X] Also completed
- Plain bullet item
- Another plain item

## Notes
Some notes here.
"""
    tasks = parse_tasks(content)
    assert len(tasks) == 5, f"Expected 5 tasks, got {len(tasks)}"
    assert tasks[0] == "- [ ] Incomplete task"
    assert tasks[1] == "- [x] Completed task"
    assert tasks[2] == "- [X] Also completed"
    assert tasks[3] == "- [ ] Plain bullet item"
    print("  parse_tasks: OK")

    # Test should_include_repo
    config_include = {"include": ["my-*", "test-repo"]}
    assert should_include_repo("my-project", config_include) is True
    assert should_include_repo("test-repo", config_include) is True
    assert should_include_repo("other-repo", config_include) is False

    config_exclude = {"exclude": ["archived-*", "temp-*"]}
    assert should_include_repo("my-project", config_exclude) is True
    assert should_include_repo("archived-project", config_exclude) is False
    assert should_include_repo("temp-test", config_exclude) is False

    config_both = {"include": ["project-*"], "exclude": ["project-archived"]}
    assert should_include_repo("project-active", config_both) is True
    assert should_include_repo("project-archived", config_both) is False
    assert should_include_repo("other", config_both) is False
    print("  should_include_repo: OK")

    # Test find_todo_file
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "test-repo"
        repo.mkdir()

        # No TODO file
        assert find_todo_file(repo) is None

        # Only TODO
        (repo / "TODO").write_text("- [ ] Task")
        assert find_todo_file(repo) == repo / "TODO"

        # Both files - prefer TODO.md
        (repo / "TODO.md").write_text("- [ ] Task from md")
        assert find_todo_file(repo) == repo / "TODO.md"
    print("  find_todo_file: OK")

    # Test full scan
    with tempfile.TemporaryDirectory() as tmpdir:
        repos_dir = Path(tmpdir)

        # Create test repos
        (repos_dir / "repo-a").mkdir()
        (repos_dir / "repo-a" / "TODO.md").write_text("- [ ] Task A")

        (repos_dir / "repo-b").mkdir()
        (repos_dir / "repo-b" / "TODO").write_text("- [x] Task B done")

        (repos_dir / "repo-no-todo").mkdir()

        (repos_dir / ".hidden-repo").mkdir()
        (repos_dir / ".hidden-repo" / "TODO.md").write_text("- [ ] Hidden")

        # Scan without config
        results = scan_repos(repos_dir, {})
        assert len(results) == 2
        assert "repo-a" in results
        assert "repo-b" in results
        assert "repo-no-todo" not in results
        assert ".hidden-repo" not in results

        # Scan with include filter
        results = scan_repos(repos_dir, {"include": ["repo-a"]})
        assert len(results) == 1
        assert "repo-a" in results

        # Scan with exclude filter
        results = scan_repos(repos_dir, {"exclude": ["repo-b"]})
        assert len(results) == 1
        assert "repo-a" in results
    print("  scan_repos: OK")

    # Test generate_markdown
    repos_data = {
        "test-repo": {
            "path": "/tmp/test-repo",
            "todo_file": "TODO.md",
            "tasks": ["- [ ] Task 1", "- [x] Task 2"],
        }
    }
    md = generate_markdown(repos_data)
    assert "# Aggregated TODOs" in md
    assert "## test-repo" in md
    assert "- [ ] Task 1" in md
    assert "- [x] Task 2" in md
    print("  generate_markdown: OK")

    # Test list_repos
    output = list_repos(repos_data)
    assert "test-repo (TODO.md)" in output
    print("  list_repos: OK")

    print("\nAll tests passed!")


if __name__ == "__main__":
    main()
