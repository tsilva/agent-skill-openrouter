#!/usr/bin/env python3
"""
Validate a single skill against the Agent Skills specification.

Usage:
    python validate_skill.py /path/to/skill-dir           # Validate skill at path
    python validate_skill.py /path/to/skill-dir --verbose # Show all details
    python validate_skill.py /path/to/skill-dir --suggest # Include optimization hints

For plugin-bundled skills, also validates plugin.json and version sync.
For project-level skills (.claude/skills/), skips plugin-specific checks.

Exit codes: 0 = passed, 1 = failed
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Validation issue severity level."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    SUGGESTION = "SUGGESTION"


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: Severity
    file_path: str
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity.value}: {self.file_path} [{self.field}]: {self.message}"


@dataclass
class ValidationResult:
    """Validation result for a skill."""
    skill_path: Path
    skill_name: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)

    @property
    def passed(self) -> bool:
        return not self.has_errors


# =============================================================================
# YAML Frontmatter Parser (regex-based, no PyYAML dependency)
# =============================================================================

def parse_skill_md(skill_md_path: Path) -> tuple[dict[str, Any], str, int]:
    """
    Parse a SKILL.md file and extract frontmatter and body.

    Returns:
        (frontmatter_dict, body_text, body_line_count)
    """
    content = skill_md_path.read_text()

    # Match YAML frontmatter between --- markers
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
    if not match:
        return {}, content, content.count('\n') + 1

    frontmatter_text = match.group(1)
    body = content[match.end():]
    body_line_count = body.count('\n') + 1 if body.strip() else 0

    frontmatter = parse_simple_yaml(frontmatter_text)

    return frontmatter, body, body_line_count


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """
    Parse simple YAML frontmatter without PyYAML.
    Handles:
    - Top-level scalar values: key: value
    - Nested objects: key:\n  subkey: value
    - Quoted strings
    """
    result: dict[str, Any] = {}
    lines = text.split('\n')
    current_key = None
    nested_content: list[str] = []

    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if indent == 0 and ':' in stripped:
            if current_key and nested_content:
                result[current_key] = parse_nested_yaml(nested_content)
                nested_content = []

            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()

            if value:
                result[key] = parse_yaml_value(value)
                current_key = None
            else:
                current_key = key
        elif current_key and indent > 0:
            nested_content.append(line)

    if current_key and nested_content:
        result[current_key] = parse_nested_yaml(nested_content)

    return result


def parse_nested_yaml(lines: list[str]) -> dict[str, Any]:
    """Parse nested YAML content (one level deep)."""
    result: dict[str, Any] = {}
    for line in lines:
        stripped = line.strip()
        if ':' in stripped and not stripped.startswith('#'):
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            if value:
                result[key] = parse_yaml_value(value)
    return result


def parse_yaml_value(value: str) -> str:
    """Parse a YAML value, handling quotes."""
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


# =============================================================================
# Validators
# =============================================================================

def validate_name(
    name: str | None,
    skill_dir_name: str,
    file_path: str
) -> list[ValidationIssue]:
    """
    Validate the 'name' field against Agent Skills spec.

    Rules:
    - Required, 1-64 characters
    - Lowercase letters, numbers, hyphens only
    - No leading/trailing hyphens
    - No consecutive hyphens (--)
    - Must match parent directory name
    - Cannot contain "anthropic" (repo rule)
    """
    issues = []

    if not name:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' is required but missing"
        ))
        return issues

    if len(name) > 64:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' exceeds 64 characters ({len(name)} chars)"
        ))

    if len(name) < 1:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' must be at least 1 character"
        ))

    if not re.match(r'^[a-z0-9-]+$', name):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' must contain only lowercase letters, numbers, and hyphens (got: '{name}')"
        ))

    if name.startswith('-') or name.endswith('-'):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' cannot start or end with a hyphen (got: '{name}')"
        ))

    if '--' in name:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' cannot contain consecutive hyphens (got: '{name}')"
        ))

    if name != skill_dir_name:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            f"'name' must match parent directory (name='{name}', dir='{skill_dir_name}')"
        ))

    name_lower = name.lower()
    if 'anthropic' in name_lower:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "name",
            "'name' cannot contain 'anthropic'"
        ))

    return issues


def validate_description(description: str | None, file_path: str) -> list[ValidationIssue]:
    """
    Validate the 'description' field.

    Rules:
    - Required, 1-1024 characters
    - Non-empty (not just whitespace)
    """
    issues = []

    if description is None:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "description",
            "'description' is required but missing"
        ))
        return issues

    if not description.strip():
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "description",
            "'description' cannot be empty or whitespace-only"
        ))
        return issues

    if len(description) > 1024:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "description",
            f"'description' exceeds 1024 characters ({len(description)} chars)"
        ))

    return issues


def validate_optional_fields(frontmatter: dict[str, Any], file_path: str) -> list[ValidationIssue]:
    """Validate optional frontmatter fields."""
    issues = []

    compatibility = frontmatter.get('compatibility')
    if compatibility and len(str(compatibility)) > 500:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "compatibility",
            f"'compatibility' exceeds 500 characters ({len(str(compatibility))} chars)"
        ))

    metadata = frontmatter.get('metadata')
    if metadata is not None and not isinstance(metadata, dict):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "metadata",
            f"'metadata' must be a key-value mapping, got {type(metadata).__name__}"
        ))

    allowed_tools = frontmatter.get('allowed-tools')
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "allowed-tools",
            f"'allowed-tools' must be a space-delimited string, got {type(allowed_tools).__name__}"
        ))

    return issues


def validate_body(body_line_count: int, file_path: str) -> list[ValidationIssue]:
    """Validate SKILL.md body (warning if >500 lines)."""
    issues = []

    if body_line_count > 500:
        issues.append(ValidationIssue(
            Severity.WARNING, file_path, "body",
            f"Body exceeds 500 lines ({body_line_count} lines) - consider reducing"
        ))

    return issues


def validate_character_budget(
    skill_md_path: Path,
    file_path: str,
    char_budget: int = 15000
) -> list[ValidationIssue]:
    """Validate skill file size is within context budget."""
    issues = []

    try:
        content = skill_md_path.read_text()
        char_count = len(content)

        if char_count > char_budget:
            issues.append(ValidationIssue(
                Severity.ERROR, file_path, "character-budget",
                f"SKILL.md exceeds context budget ({char_count:,} chars, limit: {char_budget:,}). "
                f"Skill must be compressed. See references/compression-guide.md."
            ))
    except Exception as e:
        issues.append(ValidationIssue(
            Severity.ERROR, file_path, "character-budget",
            f"Could not read file: {e}"
        ))

    return issues


# =============================================================================
# Optimization Suggestions
# =============================================================================

def suggest_description_optimization(
    description: str | None,
    file_path: str
) -> list[ValidationIssue]:
    """Suggest improvements for the description field."""
    issues = []

    if not description:
        return issues

    desc_lower = description.lower()

    # Check for trigger phrases
    trigger_phrases = ['use when', 'triggers on', 'use for', 'invoke when']
    has_trigger = any(phrase in desc_lower for phrase in trigger_phrases)
    if not has_trigger:
        issues.append(ValidationIssue(
            Severity.SUGGESTION, file_path, "description",
            "Consider adding trigger phrases (e.g., 'Use when...') to improve skill activation"
        ))

    # Check for verb-first pattern (third person)
    first_word = description.split()[0] if description.split() else ""
    verb_endings = ('s', 'es', 'ates', 'izes', 'ifies')
    if first_word and not first_word.lower().endswith(verb_endings):
        issues.append(ValidationIssue(
            Severity.SUGGESTION, file_path, "description",
            f"Consider starting with a verb in third person (e.g., 'Generates...' not '{first_word}')"
        ))

    # Check description length
    if len(description) < 50:
        issues.append(ValidationIssue(
            Severity.SUGGESTION, file_path, "description",
            f"Description is short ({len(description)} chars). Consider adding keywords and triggers (50-200 chars recommended)"
        ))

    return issues


def suggest_instruction_optimization(
    body: str,
    body_line_count: int,
    file_path: str
) -> list[ValidationIssue]:
    """Suggest improvements for the instruction body."""
    issues = []

    if not body.strip():
        return issues

    body_lower = body.lower()

    # Check for numbered workflow steps
    has_numbered_steps = bool(re.search(r'^\s*[1-9]\.\s+', body, re.MULTILINE))
    has_workflow_section = '## workflow' in body_lower or '# workflow' in body_lower
    if has_workflow_section and not has_numbered_steps:
        issues.append(ValidationIssue(
            Severity.SUGGESTION, file_path, "body",
            "Workflow section found but no numbered steps. Number steps explicitly (1. 2. 3.) for clarity"
        ))

    # Check for obvious operation explanations
    obvious_patterns = [
        r'use the read tool',
        r'use the write tool',
        r'use the edit tool',
        r'make sure the (?:file|path) exists',
        r'check if the file exists',
    ]
    for pattern in obvious_patterns:
        if re.search(pattern, body_lower):
            issues.append(ValidationIssue(
                Severity.SUGGESTION, file_path, "body",
                f"Consider removing obvious operation explanations (found: '{pattern}'). Claude knows standard operations."
            ))
            break

    # Check for large body without references
    if body_line_count > 200:
        has_reference = 'references/' in body
        if not has_reference:
            issues.append(ValidationIssue(
                Severity.SUGGESTION, file_path, "body",
                f"Large body ({body_line_count} lines) without reference files. Consider extracting detailed content to references/"
            ))

    return issues


def validate_plugin_json(plugin_json_path: Path) -> list[ValidationIssue]:
    """
    Validate plugin.json schema.

    Required fields: name, description, version, author.name
    """
    issues = []
    rel_path = str(plugin_json_path)

    if not plugin_json_path.exists():
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "file",
            "plugin.json file is missing"
        ))
        return issues

    try:
        with open(plugin_json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "json",
            f"Invalid JSON: {e}"
        ))
        return issues

    required = ['name', 'description', 'version']
    for field_name in required:
        if field_name not in data:
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, field_name,
                f"Required field '{field_name}' is missing"
            ))
        elif not data[field_name]:
            issues.append(ValidationIssue(
                Severity.ERROR, rel_path, field_name,
                f"Required field '{field_name}' is empty"
            ))

    author = data.get('author', {})
    if not isinstance(author, dict):
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "author",
            "'author' must be an object"
        ))
    elif 'name' not in author or not author['name']:
        issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "author.name",
            "Required field 'author.name' is missing or empty"
        ))

    return issues


def validate_version_sync(
    skill_md_path: Path,
    plugin_json_path: Path,
    marketplace_path: Path | None,
    plugin_name: str
) -> list[ValidationIssue]:
    """Validate versions are synchronized across files."""
    issues = []
    versions: dict[str, str | None] = {}

    if skill_md_path.exists():
        frontmatter, _, _ = parse_skill_md(skill_md_path)
        metadata = frontmatter.get('metadata', {})
        if isinstance(metadata, dict):
            versions['SKILL.md'] = metadata.get('version')

    if plugin_json_path.exists():
        try:
            with open(plugin_json_path) as f:
                data = json.load(f)
                versions['plugin.json'] = data.get('version')
        except (json.JSONDecodeError, IOError):
            pass

    if marketplace_path and marketplace_path.exists():
        try:
            with open(marketplace_path) as f:
                data = json.load(f)
                for plugin in data.get('plugins', []):
                    if plugin.get('name') == plugin_name:
                        versions['marketplace.json'] = plugin.get('version')
                        break
        except (json.JSONDecodeError, IOError):
            pass

    present_versions = {k: v for k, v in versions.items() if v is not None}

    if len(present_versions) > 1:
        unique_versions = set(present_versions.values())
        if len(unique_versions) > 1:
            version_details = ', '.join(f"{k}={v}" for k, v in present_versions.items())
            issues.append(ValidationIssue(
                Severity.ERROR, str(skill_md_path), "version",
                f"Version mismatch: {version_details}"
            ))

    return issues


# =============================================================================
# Internal Validation Hooks
# =============================================================================

def run_validation_hook(
    skill_path: Path,
    suggest: bool = False,
    timeout: int = 30
) -> list[ValidationIssue]:
    """
    Execute skill's internal validation hook if present.

    Hooks are optional scripts at scripts/validate_hook.py that allow skills
    to define their own validation logic (e.g., config schema validation).

    Args:
        skill_path: Path to the skill directory
        suggest: Whether to include optimization suggestions
        timeout: Maximum execution time in seconds

    Returns:
        List of ValidationIssues from the hook (empty if no hook exists)
    """
    hook_path = skill_path / "scripts" / "validate_hook.py"

    if not hook_path.exists():
        return []

    # Build command
    cmd = [sys.executable, str(hook_path), str(skill_path)]
    if suggest:
        cmd.append("--suggest")

    # Execute with timeout
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return [ValidationIssue(
            Severity.WARNING,
            str(hook_path.relative_to(skill_path)),
            "hook",
            f"Validation hook timed out after {timeout}s"
        )]

    if result.returncode != 0:
        stderr_msg = result.stderr.strip() if result.stderr else "no error message"
        return [ValidationIssue(
            Severity.ERROR,
            str(hook_path.relative_to(skill_path)),
            "hook",
            f"Hook failed (exit {result.returncode}): {stderr_msg}"
        )]

    # Parse JSON output
    try:
        data = json.loads(result.stdout)
        return [
            ValidationIssue(
                Severity[issue["severity"]],
                issue["file_path"],
                issue["field"],
                issue["message"]
            )
            for issue in data.get("issues", [])
        ]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return [ValidationIssue(
            Severity.ERROR,
            str(hook_path.relative_to(skill_path)),
            "hook",
            f"Invalid hook output: {e}"
        )]


# =============================================================================
# Skill Type Detection
# =============================================================================

def detect_skill_type(skill_path: Path) -> tuple[str, Path | None, Path | None]:
    """
    Detect skill type and return related paths.

    Returns:
        (skill_type, plugin_json_path, marketplace_path)
        - skill_type: "plugin" or "project" or "personal"
        - plugin_json_path: Path to plugin.json (or None)
        - marketplace_path: Path to marketplace.json (or None)
    """
    # Check if this is a plugin-bundled skill
    # Pattern: plugins/{plugin-name}/skills/{skill-name}/
    parts = skill_path.parts

    try:
        plugins_idx = parts.index('plugins')
        if plugins_idx + 3 < len(parts) and parts[plugins_idx + 2] == 'skills':
            plugin_name = parts[plugins_idx + 1]
            repo_root = Path(*parts[:plugins_idx])
            plugin_json = repo_root / 'plugins' / plugin_name / '.claude-plugin' / 'plugin.json'
            marketplace = repo_root / '.claude-plugin' / 'marketplace.json'
            return "plugin", plugin_json, marketplace
    except ValueError:
        pass

    # Check for project-level skill (.claude/skills/)
    if '.claude' in parts:
        return "project", None, None

    # Check for personal skill (~/.claude/skills/)
    home = Path.home()
    if skill_path.is_relative_to(home / '.claude' / 'skills'):
        return "personal", None, None

    return "unknown", None, None


# =============================================================================
# Main Validation Logic
# =============================================================================

def validate_skill(skill_path: Path, suggest: bool = False) -> ValidationResult:
    """Validate a single skill at the given path."""
    skill_path = skill_path.resolve()
    skill_md_path = skill_path / "SKILL.md"
    skill_name = skill_path.name

    result = ValidationResult(
        skill_path=skill_path,
        skill_name=skill_name
    )

    # Check SKILL.md exists
    if not skill_md_path.exists():
        result.issues.append(ValidationIssue(
            Severity.ERROR, str(skill_path), "SKILL.md",
            "SKILL.md file not found in skill directory"
        ))
        return result

    rel_path = f"{skill_name}/SKILL.md"

    # Parse SKILL.md
    try:
        frontmatter, body, body_line_count = parse_skill_md(skill_md_path)
    except Exception as e:
        result.issues.append(ValidationIssue(
            Severity.ERROR, rel_path, "parse",
            f"Failed to parse SKILL.md: {e}"
        ))
        return result

    # Validate frontmatter
    result.issues.extend(validate_name(
        frontmatter.get('name'),
        skill_name,
        rel_path
    ))

    result.issues.extend(validate_description(
        frontmatter.get('description'),
        rel_path
    ))

    result.issues.extend(validate_optional_fields(frontmatter, rel_path))

    # Validate body
    result.issues.extend(validate_body(body_line_count, rel_path))

    # Validate character budget
    result.issues.extend(validate_character_budget(skill_md_path, rel_path))

    # Detect skill type and validate plugin-specific files
    skill_type, plugin_json_path, marketplace_path = detect_skill_type(skill_path)

    if skill_type == "plugin" and plugin_json_path:
        result.issues.extend(validate_plugin_json(plugin_json_path))

        plugin_name = plugin_json_path.parent.parent.name
        result.issues.extend(validate_version_sync(
            skill_md_path,
            plugin_json_path,
            marketplace_path,
            plugin_name
        ))

    # Run internal validation hook if present
    result.issues.extend(run_validation_hook(skill_path, suggest))

    # Add optimization suggestions if requested
    if suggest:
        result.issues.extend(suggest_description_optimization(
            frontmatter.get('description'),
            rel_path
        ))
        result.issues.extend(suggest_instruction_optimization(
            body,
            body_line_count,
            rel_path
        ))

    return result


def print_result(result: ValidationResult, verbose: bool = False, suggest: bool = False) -> None:
    """Print validation result to stdout."""
    for issue in result.issues:
        print(issue)

    if result.issues:
        print()

    error_count = sum(1 for i in result.issues if i.severity == Severity.ERROR)
    warning_count = sum(1 for i in result.issues if i.severity == Severity.WARNING)
    suggestion_count = sum(1 for i in result.issues if i.severity == Severity.SUGGESTION)

    print(f"Skill: {result.skill_name}")
    print(f"  Path: {result.skill_path}")
    print(f"  Errors: {error_count}")
    print(f"  Warnings: {warning_count}")
    if suggest:
        print(f"  Suggestions: {suggestion_count}")
    print()

    if result.passed:
        print("Validation PASSED")
    else:
        print("Validation FAILED")


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a single skill against Agent Skills specification"
    )
    parser.add_argument(
        "skill_path",
        type=str,
        help="Path to skill directory (e.g., plugins/my-skill/skills/my-skill/)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--suggest", "-s",
        action="store_true",
        help="Include optimization suggestions beyond errors and warnings"
    )

    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()

    if not skill_path.exists():
        print(f"ERROR: Path does not exist: {skill_path}", file=sys.stderr)
        return 1

    if not skill_path.is_dir():
        print(f"ERROR: Path is not a directory: {skill_path}", file=sys.stderr)
        return 1

    result = validate_skill(skill_path, suggest=args.suggest)
    print_result(result, verbose=args.verbose, suggest=args.suggest)

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
