---
name: settings-cleaner
description: Analyzes and cleans up Claude Code permission whitelists by identifying overly specific approvals, dangerous patterns, and redundant entries. Use when asked to "clean up settings", "review permissions", "optimize allowlist", or "audit security settings". Provides interactive review before making changes.
license: MIT
compatibility: python 3.8+
metadata:
  author: tsilva
  version: "1.0.3"
---

# Settings Cleaner

Audit and optimize Claude Code permission whitelists for security and efficiency.

## Quick Start

**IMPORTANT**: Always run from the user's current working directory and pass the project settings path explicitly.

```bash
# Analyze permissions (read-only)
uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py analyze \
  --project-settings {USER_CWD}/.claude/settings.local.json

# Interactive cleanup with confirmation prompts
uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py clean \
  --project-settings {USER_CWD}/.claude/settings.local.json

# Auto-fix redundant permissions only (safest, no prompts)
uv run --with colorama {SKILL_BASE}/scripts/settings_cleaner.py auto-fix \
  --project-settings {USER_CWD}/.claude/settings.local.json
```

Where:
- `{SKILL_BASE}` = Absolute path to the skill directory (from Base directory message)
- `{USER_CWD}` = User's current working directory (use `pwd` or equivalent to get absolute path)

## What It Checks

The skill categorizes permissions into four types:

### 🔴 Dangerous Patterns

Overly broad permissions that grant unrestricted access:
- `Bash(*:*)` - Any bash command
- `Read(/*)` - Read any file on system
- `Write(/*)` - Write any file on system
- `Edit(/*)` - Edit any file on system
- `Bash(rm:*)` - Any rm command
- `Bash(sudo:*)` - Any sudo command

### 🟡 Overly Specific Patterns

Exact commands with hardcoded arguments that should be generalized:
- `Bash(python test.py --verbose)` → Suggest `Bash(python:*)`
- `Bash(npm install express)` → Suggest `Bash(npm:*)`
- `Bash(git commit -m "message")` → Suggest `Bash(git:*)`

### 🔵 Redundant Permissions

Project permissions already covered by broader global permissions:
- Global has `Bash(python:*)`, project has `Bash(python test.py)` → Redundant
- Global has `WebFetch`, project has `WebFetch(domain:example.com)` → Redundant
- Global has `Bash(*:*)`, project has any `Bash(...)` → Redundant

### ✅ Good Permissions

Well-scoped permissions that follow best practices:
- `Bash(pytest:*)` - All pytest commands
- `Read(/Users/tsilva/repos/*)` - Scoped to specific directory
- `WebFetch(domain:api.openrouter.ai)` - Specific domain

## Commands

| Command | Description | Modifications |
|---------|-------------|---------------|
| `analyze` | Read-only audit of permissions | None (report only) |
| `clean` | Interactive cleanup with confirmations | Yes (with prompts) |
| `auto-fix` | Remove redundant permissions automatically | Yes (redundancies only) |

## Example Output

```
🔴 DANGEROUS (1 found):
  - Bash(*:*) [Global]
    Risk: Allows any bash command without restriction
    Remove? [y/N]:

🟡 OVERLY SPECIFIC (2 found):
  - Bash(python test.py --verbose) [Project]
    → Suggest: Bash(python:*)
    Generalize? [y/N]:

🔵 REDUNDANT (1 found):
  - Bash(pytest:*) [Project]
    Covered by: Bash(python:*) [Global]
    Remove? [Y/n]:

✅ GOOD (5 permissions)
```

## Safety Features

1. **Automatic backups**: Creates `.bak` files before any modifications
2. **Interactive mode**: Prompts for each dangerous/specific pattern
3. **Auto-fix safety**: Only removes redundancies (no dangerous/specific changes)
4. **JSON validation**: Verifies structure after loading and before saving
5. **Color-coded output**: Clear visual categorization of issues

## Implementation Notes

### Pattern Matching

The skill uses pattern subsetting logic to determine redundancy:

```python
# Tool-level wildcards
WebFetch covers WebFetch(domain:*)

# Command-level wildcards
Bash(python:*) covers Bash(python ...) with any arguments
Bash(*:*) covers all Bash commands

# Exact matches
Bash(ls -la) only covers that exact command
```

### Files Analyzed

- **Global**: `~/.claude/settings.json`
- **Project**: `./.claude/settings.local.json`

Only the `permissions.allow[]` array is reviewed.

## Usage from Claude Code

Trigger the skill by asking:
- "Clean up my settings"
- "Review my permissions"
- "Audit my security settings"
- "Optimize my allowlist"
- "Check for redundant permissions"

### Execution Instructions for Claude

When this skill is invoked, you MUST:

1. **Get the skill base directory** from the "Base directory for this skill" message
2. **Get the user's current working directory** (they're already in the right place)
3. **Run the script with absolute paths** - DO NOT cd into the skill directory

Example invocation:
```bash
uv run --with colorama /absolute/path/to/skill/scripts/settings_cleaner.py analyze \
  --project-settings /absolute/path/to/user/cwd/.claude/settings.local.json
```

**Why this matters**: The script needs to find the project's `.claude/settings.local.json` file in the user's working directory, not in the skill's directory. Running from the wrong location will cause it to miss project-specific permissions and fail to detect redundancies.

Workflow:
1. Run the analyze command with proper paths
2. Show the findings to the user
3. Ask if they want to proceed with cleanup
4. Execute the appropriate command (clean or auto-fix) with the same path arguments
