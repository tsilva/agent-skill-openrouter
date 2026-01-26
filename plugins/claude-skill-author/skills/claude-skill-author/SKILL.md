---
name: claude-skill-author
description: Guide for creating and modifying Claude Code agent skills. Covers project-level skills (.claude/skills/), personal skills (~/.claude/skills/), and plugin-bundled marketplace skills. Use when creating a new skill, updating an existing skill, converting a project skill to a plugin, or when asked about skill authoring.
license: MIT
argument-hint: "[project|plugin] [skill-name]"
metadata:
  author: tsilva
  version: "1.0.0"
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
python plugins/claude-skill-author/skills/claude-skill-author/scripts/validate_skill.py plugins/{name}/skills/{name}
```

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
| `argument-hint` | Shown in autocomplete (e.g., `[file-path]`) |
| `disable-model-invocation` | `true` = only manual `/name` invocation |
| `user-invocable` | `false` = hide from `/` menu, Claude can still auto-trigger |

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

**Hard limit: 15,000 characters** for SKILL.md. Validation enforces this.

If over budget, see `references/compression-guide.md`.

## Description Best Practices

The description triggers skill activation. Claude uses it to select from 100+ skills.

**Good:**
```yaml
description: Extract text from PDFs, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, extraction.
```

**Bad:**
```yaml
description: Helps with documents
```

**Rules:**
- Third person ("Generates..." not "Generate...")
- Include trigger phrases ("Use when...", "Triggers on...")
- Keywords Claude can match on
- 1-1024 characters

## Separation of Concerns

**Critical rule: Skills are black boxes.**

A skill should only know WHAT another skill does, not HOW.

```
# CORRECT - Reference public interface
"Invoke repo-logo-generator to generate a logo"

# WRONG - Reference internal implementation
"Check ~/.claude/repo-logo-generator.json for config"
```

Never:
- Read another skill's config files
- Depend on another skill's internal file structure
- Assume how another skill implements its features

## Version Management (Plugin Skills Only)

After modifying a SKILL.md file:

### 1. Check if Already Bumped

```bash
python scripts/bump-version.py {plugin} --check-uncommitted
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
python scripts/bump-version.py {plugin} --type {patch|minor|major}
```

### 4. Validate

```bash
python plugins/claude-skill-author/skills/claude-skill-author/scripts/validate_skill.py plugins/{plugin}/skills/{skill}
```

## Validation

Validates against Agent Skills spec and repository rules.

### Single Skill

```bash
python plugins/claude-skill-author/skills/claude-skill-author/scripts/validate_skill.py /path/to/skill
```

### Validation Checks

- Required fields: name, description
- Name format: lowercase, hyphens, 1-64 chars, matches directory
- Description: 1-1024 chars, non-empty
- Character budget: max 15,000 chars
- Body lines: warning if >500
- Version sync (plugin skills): SKILL.md, plugin.json, marketplace.json

### Exit Codes

- 0 = passed
- 1 = failed (errors found)

## Best Practices

### Conciseness

Claude is smart. Only add context Claude doesn't already have.

- Challenge each piece: "Does Claude really need this?"
- One good example beats three mediocre ones
- Keep SKILL.md body under 500 lines

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
python plugins/claude-skill-author/skills/claude-skill-author/scripts/validate_skill.py plugins/{name}/skills/{name}
```

### Validate

```bash
python plugins/claude-skill-author/skills/claude-skill-author/scripts/validate_skill.py /path/to/skill
```

### Version Bump

```bash
python scripts/bump-version.py {plugin} --type {patch|minor|major}
```

For detailed templates, see `references/templates.md`.
For compression techniques, see `references/compression-guide.md`.
For full frontmatter field reference, see `references/spec-details.md`.
