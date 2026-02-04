---
name: claude-skill-author
description: Guides creation and modification of Claude Code agent skills. Covers project-level skills (.claude/skills/), personal skills (~/.claude/skills/), and plugin-bundled marketplace skills. Use when creating a skill, updating an existing skill, converting a project skill to a plugin, or when asked about skill authoring.
license: MIT
argument-hint: "[project|plugin] [skill-name]"
user-invocable: true
metadata:
  author: tsilva
  version: "1.4.0"
---

# Skill Author Guide

Create and modify Claude Code agent skills following the [Agent Skills specification](https://agentskills.io/specification).

## Skill Types

### Project-Level Skills (Simple)

Location: `.claude/skills/{skill-name}/SKILL.md`

- No plugin.json or marketplace registration
- No version management needed
- Best for: project-specific workflows, team conventions
- Minimal structure - just the SKILL.md file

### Personal Skills

Location: `~/.claude/skills/{skill-name}/SKILL.md`

- Available across all projects for the user
- Same structure as project skills
- Best for: personal workflows, preferences

### Plugin-Bundled Skills (Shareable)

Location: `plugins/{plugin-name}/skills/{skill-name}/SKILL.md`

- Requires plugin.json manifest and marketplace.json entry
- Version sync across 3 files (SKILL.md, plugin.json, marketplace.json)
- Best for: reusable, shareable skills

## Workflow: Project Skills

```bash
mkdir -p .claude/skills/{name}
```

Create `.claude/skills/{name}/SKILL.md`:
```yaml
---
name: {name}
description: What it does. Use when [triggers].
---

# {Title}

Instructions here...
```

Done. No further steps needed.

## Workflow: Plugin Skills

### 1. Create Structure

```bash
mkdir -p plugins/{name}/.claude-plugin
mkdir -p plugins/{name}/skills/{name}/scripts
```

### 2. Create plugin.json

`plugins/{name}/.claude-plugin/plugin.json`:
```json
{
  "name": "{name}",
  "description": "What this skill does.",
  "version": "1.0.0",
  "author": { "name": "your-name" }
}
```

### 3. Create SKILL.md

`plugins/{name}/skills/{name}/SKILL.md`:
```yaml
---
name: {name}
description: What it does. Use when [triggers]. Third person.
license: MIT
metadata:
  author: your-name
  version: "1.0.0"
---

# {Title}

Instructions...
```

### 4. Register in Marketplace

Add to `.claude-plugin/marketplace.json` plugins array:
```json
{
  "name": "{name}",
  "source": "./plugins/{name}",
  "description": "Same as plugin.json",
  "version": "1.0.0"
}
```

### 5. Validate

```bash
python {SKILL_DIR}/scripts/validate_skill.py plugins/{name}/skills/{name}
```

**Note:** For any future changes to this skill, you MUST bump the version. See "Version Management" section.

## SKILL.md Structure

### Required Frontmatter

| Field | Constraints |
|-------|-------------|
| `name` | 1-64 chars. Lowercase, numbers, hyphens. Match directory. No "anthropic". |
| `description` | 1-1024 chars. Third person. Include triggers ("Use when..."). |

### Optional Frontmatter

| Field | Purpose |
|-------|---------|
| `license` | Use `MIT` for this repo |
| `compatibility` | Max 500 chars. Requirements (e.g., "python 3.8+") |
| `metadata` | Key-value mapping (author, version) |
| `argument-hint` | **Recommended for user-invocable skills.** Shown in autocomplete. |
| `disable-model-invocation` | `true` = only manual `/name` invocation |
| `user-invocable` | `false` = hide from `/` menu, Claude can still auto-trigger |

### Argument Hints

Add `argument-hint` to show expected arguments in autocomplete:

```yaml
argument-hint: "[create|modify|validate] [path]"  # Operations
argument-hint: "[project|plugin] [skill-name]"    # Multiple args
```

Add when skill accepts arguments via `$ARGUMENTS`. Skip if no arguments or not user-invocable.

### Slash Commands

Every skill becomes a slash command via its `name` field:
- `name: my-skill` becomes `/my-skill`
- Arguments passed as `$ARGUMENTS` or appended to instructions

### Directory Structure

```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Executable code
├── references/       # On-demand documentation
└── assets/           # Static resources
```

### Character Budget

| Threshold | Severity | Action |
|-----------|----------|--------|
| 8,000 chars | WARNING | Consider compressing |
| 12,000 chars | ERROR | Must compress or use references/ |

If over budget, see `references/compression-guide.md`.

## Description Best Practices

The description triggers skill activation. Claude selects from 100+ skills based on it.

**Rules:** Third person ("Generates..."), include triggers ("Use when..."), add keywords, 1-1024 chars.

**Good:** `Extract text from PDFs, fill forms. Use when working with PDF files.`
**Bad:** `Helps with documents`

## Separation of Concerns

**Critical rule: Skills are black boxes.**

A skill should only know WHAT another skill does, not HOW.

```
# CORRECT - Reference public interface
"Invoke project-logo-author to generate a logo"

# WRONG - Reference internal implementation
"Check ~/.claude/project-logo-author.json for config"
```

Never:
- Read another skill's config files
- Depend on another skill's internal file structure
- Assume how another skill implements its features

## Version Management (Plugin Skills Only)

**MANDATORY: Any change to any file in a plugin skill requires a version bump.** This includes:
- SKILL.md content or frontmatter changes
- Script modifications
- Reference documentation updates
- Asset changes

No exceptions. The only question is bump type (patch/minor/major), not whether to bump.

After modifying any file in a plugin skill:

### 1. Check if Already Bumped

```bash
python {SKILL_DIR}/scripts/bump-version.py {plugin} --check-uncommitted
```
- Exit 0 = already bumped, skip to validation
- Exit 1 = needs bump

### 2. Determine Bump Type

| Change | Bump |
|--------|------|
| Docs, typos, clarifications | patch |
| New features, parameters | minor |
| Breaking changes, removed features | major |

### 3. Apply Bump

```bash
python {SKILL_DIR}/scripts/bump-version.py {plugin} --type {patch|minor|major}
```

### 4. Validate

```bash
python {SKILL_DIR}/scripts/validate_skill.py plugins/{plugin}/skills/{skill}
```

## Validation

Validates against Agent Skills spec and repository rules.

### Single Skill

```bash
python {SKILL_DIR}/scripts/validate_skill.py /path/to/skill
```

### Validation Checks

**Errors (must fix):**
- Required fields: name, description
- Name format: lowercase, hyphens, 1-64 chars, matches directory
- Name cannot contain "anthropic" (reserved)
- Name cannot use "claude-" prefix (use descriptive names)
- Name/description cannot contain XML characters (`<`, `>`)
- Description: 1-1024 chars, non-empty
- Character budget: >12,000 chars
- Body lines: >400 lines
- Version sync (plugin skills): SKILL.md, plugin.json, marketplace.json

**Warnings (should fix):**
- Character budget: >8,000 chars
- Body lines: >300 lines
- Large skills (>150 lines or >6,000 chars) without references/
- Windows-style paths (backslashes) - use forward slashes
- Vague names: "helper", "utils", "tools", "documents", "data", "files"
- Referenced files in SKILL.md that don't exist

**Suggestions (--suggest flag):**
- Gerund-form naming (e.g., "processing-pdfs" vs "pdf-processor")
- Trigger phrases in description
- Third-person verb form
- Time-sensitive language ("currently", "as of version X")
- TOC for reference files >100 lines
- MCP tool qualified names (server:tool format)
- Deeply nested references (references linking to other references)
- Missing `argument-hint` for user-invocable skills

### Exit Codes

- 0 = passed
- 1 = failed (errors found)

## Best Practices

### Conciseness

- Challenge each piece: "Does Claude really need this?"
- One good example beats three mediocre ones

### Progressive Disclosure

Skills use 3-tier loading:

1. **Metadata** (~100 tokens): name, description - loaded at startup
2. **SKILL.md body** (<5000 tokens): loaded when skill triggers
3. **Bundled resources**: loaded on-demand from scripts/, references/

### Writing Style

- Imperative form: "Extract text..." not "This extracts text..."
- File references one level deep from SKILL.md
- Table of contents for files >100 lines

### Scripts

- Bundle for deterministic operations
- Document "magic numbers" with comments
- Helpful error messages that guide resolution
- Use UV with inline dependencies (PEP 723)
- **Always use `{SKILL_DIR}/scripts/` prefix** when referencing scripts in SKILL.md bash blocks. Bare paths like `scripts/foo.py` break when installed as a plugin.

## Skill Optimization

Use `--suggest` flag for optimization hints:
```bash
python {SKILL_DIR}/scripts/validate_skill.py /path/to/skill --suggest
```

**WIRE framework:** Workflow (numbered steps), Inputs (typed), Rules (explicit), Examples (one per concept).

**Anti-patterns:** Explaining obvious operations, multiple equivalent examples, verbose error handling, hardcoded paths.

For detailed optimization techniques, see `references/optimization-guide.md`.

## Quick Reference

### Create Project Skill

```bash
mkdir -p .claude/skills/{name}
# Create SKILL.md with name and description
```

### Create Plugin Skill

```bash
mkdir -p plugins/{name}/.claude-plugin plugins/{name}/skills/{name}
# Create plugin.json, SKILL.md, marketplace.json entry
python {SKILL_DIR}/scripts/validate_skill.py plugins/{name}/skills/{name}
```

### Validate

```bash
python {SKILL_DIR}/scripts/validate_skill.py /path/to/skill
```

### Version Bump (Required for ANY Change)

```bash
python {SKILL_DIR}/scripts/bump-version.py {plugin} --type {patch|minor|major}
```

**Always bump versions.** Any change = version bump. No exceptions.

For detailed templates, see `references/templates.md`.
For compression techniques, see `references/compression-guide.md`.
For full frontmatter field reference, see `references/spec-details.md`.
