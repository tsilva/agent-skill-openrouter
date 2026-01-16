#!/usr/bin/env python3
"""
Auto-bump version numbers for a skill plugin.

Usage: python bump-version.py <plugin-name>

Bumps the patch version (e.g., 1.0.4 -> 1.0.5) in:
1. plugins/<plugin>/skills/<skill>/SKILL.md (metadata.version)
2. plugins/<plugin>/.claude-plugin/plugin.json (version)
3. .claude-plugin/marketplace.json (version for that plugin)
"""

import json
import re
import sys
from pathlib import Path


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse a version string into (major, minor, patch) tuple."""
    # Remove quotes if present
    version_str = version_str.strip().strip('"').strip("'")
    parts = version_str.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version_str}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bump_patch(version_str: str) -> str:
    """Bump the patch version and return new version string."""
    major, minor, patch = parse_version(version_str)
    return f"{major}.{minor}.{patch + 1}"


def find_skill_md(plugin_dir: Path) -> Path | None:
    """Find the SKILL.md file for a plugin."""
    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        return None

    # Find the first skill directory with a SKILL.md
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                return skill_md
    return None


def extract_version_from_skill_md(skill_md_path: Path) -> str | None:
    """Extract version from SKILL.md frontmatter."""
    content = skill_md_path.read_text()

    # Match YAML frontmatter between --- markers
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter = match.group(1)

    # Find version in metadata section
    # Look for: metadata:\n  ...\n  version: "X.Y.Z"
    version_match = re.search(r'^\s*version:\s*["\']?([^"\'\n]+)["\']?', frontmatter, re.MULTILINE)
    if version_match:
        return version_match.group(1).strip()

    return None


def update_skill_md(skill_md_path: Path, new_version: str) -> bool:
    """Update the version in SKILL.md frontmatter."""
    content = skill_md_path.read_text()

    # Match and replace version in frontmatter
    # Handle both quoted and unquoted versions
    new_content = re.sub(
        r'(^\s*version:\s*)["\']?[^"\'\n]+["\']?',
        f'\\1"{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE
    )

    if new_content == content:
        return False

    skill_md_path.write_text(new_content)
    return True


def update_plugin_json(plugin_json_path: Path, new_version: str) -> bool:
    """Update the version in plugin.json."""
    if not plugin_json_path.exists():
        return False

    with open(plugin_json_path) as f:
        data = json.load(f)

    old_version = data.get("version")
    data["version"] = new_version

    with open(plugin_json_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # Add trailing newline

    return old_version != new_version


def update_marketplace_json(marketplace_path: Path, plugin_name: str, new_version: str) -> bool:
    """Update the version for a plugin in marketplace.json."""
    if not marketplace_path.exists():
        return False

    with open(marketplace_path) as f:
        data = json.load(f)

    plugins = data.get("plugins", [])
    updated = False

    for plugin in plugins:
        if plugin.get("name") == plugin_name:
            if plugin.get("version") != new_version:
                plugin["version"] = new_version
                updated = True
            break

    if updated:
        with open(marketplace_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")  # Add trailing newline

    return updated


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <plugin-name>")
        sys.exit(1)

    plugin_name = sys.argv[1]

    # Determine repo root (script is in scripts/)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    # Locate files
    plugin_dir = repo_root / "plugins" / plugin_name
    if not plugin_dir.exists():
        print(f"Error: Plugin directory not found: {plugin_dir}")
        sys.exit(1)

    skill_md_path = find_skill_md(plugin_dir)
    if not skill_md_path:
        print(f"Error: SKILL.md not found for plugin: {plugin_name}")
        sys.exit(1)

    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"

    # Extract current version
    current_version = extract_version_from_skill_md(skill_md_path)
    if not current_version:
        print(f"Error: Could not extract version from {skill_md_path}")
        sys.exit(1)

    # Bump version
    new_version = bump_patch(current_version)
    print(f"  Bumping version: {current_version} -> {new_version}")

    # Update all files
    updates = []

    if update_skill_md(skill_md_path, new_version):
        updates.append(f"  Updated: {skill_md_path.relative_to(repo_root)}")

    if update_plugin_json(plugin_json_path, new_version):
        updates.append(f"  Updated: {plugin_json_path.relative_to(repo_root)}")

    if update_marketplace_json(marketplace_path, plugin_name, new_version):
        updates.append(f"  Updated: {marketplace_path.relative_to(repo_root)}")

    for update in updates:
        print(update)

    if not updates:
        print("  No files needed updating.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
