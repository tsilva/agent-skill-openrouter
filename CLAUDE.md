# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code skills repository containing multiple modular plugins. Each skill provides specialized capabilities through the Claude Code plugin system. Skills are organized as independent plugins with their own versioning.

## Repository Architecture

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json         # Lists all available plugins
├── plugins/
│   └── {plugin-name}/           # One directory per plugin
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin metadata (name, version, author)
│       └── skills/
│           └── {skill-name}/    # Skill definition
│               ├── SKILL.md     # Skill instructions and metadata (required)
│               ├── scripts/     # Executable code (optional)
│               ├── references/  # Documentation loaded on-demand (optional)
│               └── assets/      # Static resources like templates, icons (optional)
├── shared/                      # Cross-skill utilities
│   ├── bump-version.py          # Plugin version bumping
│   ├── detect_project.py        # Project type detection
│   ├── load_config.py           # Config loading and merging
│   ├── repo_utils.py            # Repository discovery
│   ├── select_operation.py      # Operation selection logic
│   ├── substitute_template.py   # Template variable substitution
│   └── validate_skill.py        # Skill validation against spec
├── CLAUDE.md                    # This file
└── README.md                    # Repository documentation
```

### Design Principles

1. **One plugin per skill**: Each skill is a self-contained plugin with independent versioning
2. **Minimal dependencies**: Scripts should be standalone with minimal external dependencies
3. **Absolute paths**: All file operations should use absolute paths
4. **MCP integration**: Skills can leverage MCP servers for external APIs (e.g., mcp-openrouter for AI models)

## Available Skills

### README Author

Create, modify, validate, and optimize README.md files following GitHub best practices.

**Key files:**
- `plugins/project-readme-author/skills/project-readme-author/SKILL.md` - Skill definition
- `plugins/project-readme-author/.claude-plugin/plugin.json` - Plugin metadata

**Operations:**
- **create** - Build README from scratch for new projects
- **modify** - Update specific sections while preserving structure
- **validate** - Score against best practices checklist
- **optimize** - Auto-fix issues and enhance quality

**Features:**
- Smart project analysis (auto-detects language, framework, package manager)
- Modern README structure with centered hero, badges, and visual hierarchy
- Logo generation integration with project-logo-author skill
- Best practices for GitHub READMEs (accessibility, mobile-friendly, scannable)

### Spec Extractor

Analyze a codebase and generate a pure requirements specification (SPEC.md) capturing what the project does without how it's built.

**Key files:**
- `plugins/project-spec-extractor/skills/project-spec-extractor/SKILL.md` - Skill definition
- `plugins/project-spec-extractor/.claude-plugin/plugin.json` - Plugin metadata

**Modes:**
- **Tech-preserving** (default) - Lists specific stack names in Technology Constraints
- **Tech-agnostic** (`--tech-agnostic`) - Describes abstract capabilities instead

**Use cases:**
- Rebuild a project from scratch with cleaner code
- Port a project to a different tech stack
- Generate living documentation as a portable blueprint

### Logo Author

Generate professional logos with transparent backgrounds using AI image generation and chromakey processing.

**Key files:**
- `plugins/project-logo-author/skills/project-logo-author/SKILL.md` - Skill definition
- `plugins/project-logo-author/.claude-plugin/plugin.json` - Plugin metadata

**Requirements:** mcp-openrouter and mcp-image-tools MCP servers

### Bash Output Styler

Applies terminal styling to bash scripts using gum with ANSI fallback.

**Key files:**
- `plugins/bash-output-styler/skills/bash-output-styler/SKILL.md` - Skill definition
- `plugins/bash-output-styler/skills/bash-output-styler/references/style.sh` - Styling library

### Python Output Styler

Applies terminal styling to Python scripts using Rich with plain-text fallback.

**Key files:**
- `plugins/python-output-styler/skills/python-output-styler/SKILL.md` - Skill definition
- `plugins/python-output-styler/skills/python-output-styler/references/style.py` - Styling module

## Skill Authoring

For creating or modifying skills, use the `plugin-dev` plugin which provides comprehensive guidance on skill structure, progressive disclosure, trigger phrases, and best practices.

**Version management tooling:**
- `shared/validate_skill.py` - Validates skills against the Agent Skills specification
- `shared/bump-version.py` - Bumps plugin versions across all 3 locations (SKILL.md, plugin.json, marketplace.json)

**IMPORTANT:** When making ANY change to ANY file within a plugin directory (`plugins/*/`), version must be bumped. Use `shared/bump-version.py <plugin-name> --type patch` to bump versions consistently.

## Dependency Management Best Practices

Following official Agent Skills specification and Anthropic recommendations.

### Gold Standard: UV with Inline Dependencies

All scripts use UV with inline dependency declarations:
```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with pillow scripts/chromakey.py ...
```

**Why UV is preferred:**
- Zero setup for users (no pip install needed)
- Dependencies declared inline (PEP 723 standard)
- Automatic caching and fast execution
- Full portability across systems
- Official Anthropic/Claude Code recommendation

### Handling Missing Dependencies

Scripts validate dependencies at import with helpful error messages:
```python
try:
    from PIL import Image
except ImportError:
    print("Error: pillow library required.", file=sys.stderr)
    print("Run with: uv run --with pillow <script>", file=sys.stderr)
    sys.exit(1)
```

**Pattern:**
- Print to `stderr` (not stdout)
- Exit with code 1
- Provide exact recovery command
- Name the specific missing library

### macOS Sandbox Limitation

UV accesses `SystemConfiguration.framework` APIs for proxy detection, which requires `dangerouslyDisableSandbox: true` on macOS. This is a known UV limitation, not a skill design issue.

**Expected behavior:**
- On first execution, Claude may attempt with sandbox enabled
- If it fails with system-configuration errors, Claude will retry with sandbox disabled
- This is normal and does not indicate a security problem

**Fallback:** For restricted environments, users can pre-install dependencies and use plain Python:
```bash
python3 -m pip install pillow
python3 /absolute/path/to/script.py ...
```

However, the UV approach is strongly preferred for its portability and zero-setup benefits.

### Optional Dependencies

For non-critical dependencies, use graceful degradation:
```python
try:
    from colorama import Fore, Style
    HAS_COLOR = True
except ImportError:
    # Fallback: no colors
    class Fore:
        RED = GREEN = ""
    HAS_COLOR = False
```

This allows the script to function even when optional packages are unavailable.

## Shared Utilities

The `shared/` directory contains deterministic utilities that replace LLM decision-making for algorithmic tasks.

### repo_utils.py

Discovers git repositories in a directory.

```bash
uv run shared/repo_utils.py --path /path/to/repos
```

**Output:**
```
/path/to/repos/repo-alpha
/path/to/repos/repo-beta
```

**Features:**
- Case-insensitive sorting
- Detects repos by .git directory presence

### detect_project.py

Detects project type from file presence.

```bash
uv run shared/detect_project.py --path /path/to/repo
```

**Output:**
```json
{"type": "python", "confidence": "high", "files": ["pyproject.toml"]}
```

**Supported types:** nodejs, python, rust, go, java, dotnet, ruby, php, cpp, c, unknown

### load_config.py

Loads and merges multi-level JSON configs with precedence.

```bash
uv run shared/load_config.py \
  --defaults "assets/defaults.json" \
  --user "~/.claude/config.json" \
  --project ".claude/config.json"
```

**Features:**
- Deep merging (project > user > defaults)
- Environment variable expansion (`$HOME`, `${VAR}`)
- Graceful handling of missing files

### select_operation.py

Determines skill operation from arguments and file state.

```bash
uv run shared/select_operation.py \
  --skill project-readme-author \
  --args "validate this readme" \
  --check-files "README.md"
```

**Output:**
```json
{"operation": "validate", "reason": "Explicit keyword found", "source": "argument_keyword"}
```

**Supported skills:** readme, project-readme-author, project-logo-author

### substitute_template.py

Replaces `{VARIABLE}` placeholders in templates.

```bash
uv run shared/substitute_template.py \
  --template "assets/template.txt" \
  --vars '{"PROJECT_NAME": "my-app", "TYPE": "python"}'
```

**Features:**
- Reports unsubstituted variables as warnings
- Case-sensitive matching (uppercase only)

### validate_skill.py

Validates a single skill against the Agent Skills specification.

```bash
uv run shared/validate_skill.py plugins/my-skill/skills/my-skill/
uv run shared/validate_skill.py plugins/my-skill/skills/my-skill/ --suggest
```

**Checks:**
- Frontmatter fields (name, description, compatibility)
- Body line count and character budget limits
- Plugin.json schema and version sync across all 3 locations
- Script path portability ({SKILL_DIR} usage)
- Referenced file existence

**Exit codes:** 0 = passed, 1 = failed

### bump-version.py

Bumps plugin version numbers across all 3 locations with semantic versioning.

```bash
uv run shared/bump-version.py <plugin-name> --type patch
uv run shared/bump-version.py <plugin-name> --type minor --dry-run
uv run shared/bump-version.py <plugin-name> --check-uncommitted
```

**Updates:** SKILL.md metadata, plugin.json, marketplace.json

### Self-Testing

All utilities support `--test` for self-testing:

```bash
uv run shared/detect_project.py --test
uv run shared/load_config.py --test
uv run shared/repo_utils.py --test
uv run shared/select_operation.py --test
uv run shared/substitute_template.py --test
```

## Maintenance

- **Keep Available Skills in sync**: When adding a new plugin, add an entry to the Available Skills section above
- **README.md must be kept up to date** with any significant project changes

## Conventions

- **Skill names**: lowercase, hyphenated (e.g., `readme-generator`, `code-review`). Max 64 chars.
- **Plugin names**: typically match skill name for single-skill plugins
- **Scripts**: Place in `scripts/` subdirectory
  - Prefer single-file with minimal dependencies
  - Use `#!/usr/bin/env python3` shebang for portability
  - Include docstrings explaining purpose and usage
  - Handle errors gracefully with helpful messages
- **References**: Place in `references/` subdirectory for detailed documentation
- **Assets**: Place in `assets/` subdirectory for templates, icons, and static files
