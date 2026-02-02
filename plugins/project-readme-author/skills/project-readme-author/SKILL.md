---
name: project-readme-author
description: Create, modify, validate, and optimize README.md files following GitHub best practices.
license: MIT
compatibility: Any environment
argument-hint: "[create|modify|validate|optimize] [path]"
disable-model-invocation: false
user-invocable: true
metadata:
  author: tsilva
  version: "2.3.0"
---

# README Author

Create READMEs that hook readers in 5 seconds, prove value in 30 seconds, and enable success in under 10 minutes.

## Operations

| Operation | Triggers | Purpose |
|-----------|----------|---------|
| **create** | No README exists, "create/generate README" | Build from scratch |
| **modify** | README exists, "update/change README" | Preserve structure, update sections |
| **validate** | "check/review/audit README" | Score against best practices |
| **optimize** | "improve/enhance README" | Fix issues, enhance quality |

### Operation Detection

Use the deterministic operation selector:

```bash
uv run shared/select_operation.py --skill project-readme-author --args "$ARGUMENTS" --check-files "README.md"
```

**Fallback rules (if script unavailable):**
1. Check `$ARGUMENTS` for explicit operation keywords
2. Check if README.md exists at target path
3. Default: `create` if no README, `modify` if README exists

---

## Create Operation

Use when building a README from scratch. Follow the Core Framework and Workflow sections below.

## Modify Operation

Use when updating an existing README while preserving its structure.

- **Keep custom prose** — user-written descriptions, explanations, context
- **Update dynamic content** — versions, badge URLs, install commands
- **Respect markers** — content within `<!-- custom -->...<!-- /custom -->` is never touched
- **Preserve section order** — don't reorder unless explicitly requested
- **Preserve manual notes** — any hand-written note, warning, tip that's factually relevant
- **Default to preservation** — when relevance is unclear, use AskUserQuestion to confirm
- **Never assume obsolescence** — only remove when explicitly asked or factually incorrect
- **Deprecated sections** — ask user via AskUserQuestion before removing

**When in doubt, preserve existing content and use AskUserQuestion to confirm before removing anything.**

## Validate Operation

Score an existing README against best practices. See [references/validation-guide.md](references/validation-guide.md) for scoring format, tiers, project-type checks, and checklists.

## Optimize Operation

**Quick Wins (auto-apply):** Center hero, add alt text, fix badge URLs, add TOC if >500 words, standardize badge style, fix heading hierarchy, add emojis to headers.

**Requires Approval:** Add new sections, rewrite tagline, change badge selection, remove emojis, restructure content order.

---

## Core Framework: Hook → Prove → Enable → Extend

| Phase | Time | Purpose | Elements |
|-------|------|---------|----------|
| **Hook** | 0-5 sec | Instant recognition | Logo + badges + one-liner + demo visual |
| **Prove** | 5-30 sec | Build credibility | Social proof, features, trust signals |
| **Enable** | 30 sec - 10 min | Immediate success | One-liner install + working example |
| **Extend** | Committed users | Deep engagement | Docs links, contributing, API reference |

**The goal: Time to first success under 10 minutes.** The first 5-10 lines visible without scrolling determine whether users stay or leave.

## Logo Generation (Mandatory)

Every README must have a logo:

1. **Check for existing logo** — look for `logo.png` at repo root; if found, skip to README generation
2. **Generate if missing** — invoke the **project-logo-author** skill
3. **Determine display size** — use `mcp__image-tools__get_image_metadata` to get width, then divide by 2 for retina display (e.g., 1024px → `width="512"`)

## Hero Section

The hero section must be center-aligned with these elements in order:

### Title Rule

**The title must be exactly the repository name.** Preserve original casing — `my-awesome-tool` stays `my-awesome-tool`, not "My Awesome Tool".

```markdown
<div align="center">
  <img src="logo.png" alt="Project Name" width="{DISPLAY_WIDTH}"/>

  [![Build](badge)](link) [![Version](badge)](link) [![License](badge)](link)

  **A clear, catchy one-liner that explains what this does and why it matters**

  [Documentation](url) · [Demo](url) · [Discord](url)
</div>
```

### Hero Elements

| Element | Specification |
|---------|---------------|
| Logo | Width = half actual pixels (for retina), centered |
| Badges | 3-6 maximum, shields.io for consistency |
| Tagline | One sentence with emoji(s), max 350 chars (fits GitHub "About" field) |
| Quick links | Docs, demo, community (if available) |

### Tagline Rules

- **Must include emoji(s)** — 1-3 relevant emojis reinforcing the message
- **Max 350 characters** — ideal 80-150 chars, punchy and scannable
- ✅ "🔧 Magnificent app which corrects your previous console command"
- ✅ "⚡ High-performance, easy to learn, fast to code, ready for production"
- ❌ "A Python library for doing Y" (no emoji, too generic)
- **Source from pyproject.toml** — if `description` field exists, use as base tagline and enhance with emojis. If crafting new and `pyproject.toml` exists, sync back.

### GIF Demo Placement

For CLI tools, place an animated GIF demo **immediately after the tagline**.

## Badges

Use 4-7 badges in priority order: Build/CI → Coverage → Version → License → Downloads → Community.

For badge implementation details and code, see [references/badges-and-visuals.md](references/badges-and-visuals.md).

## Writing Style

- **Active voice, imperative mood**: "Install the package" not "The package can be installed"
- **Second person, present tense**: "You can configure..." with contractions for conversational tone
- **Short paragraphs**: Max 3-5 lines, one concept per paragraph
- **Emojis**: Use liberally on section headers (🚀 Quick Start), feature bullets (⚡ Fast), status indicators (✅ Done), and CTAs (⭐ Star us!). 2-4 per section, never in code blocks.

## README by Project Type

For detailed templates and examples by project type (AI/ML, CLI, Libraries, Web Apps), see [references/project-types.md](references/project-types.md).

For visual elements, social proof, and community links, see [references/badges-and-visuals.md](references/badges-and-visuals.md).

## Workflow

### Create Workflow

1. **Detect project type**: `uv run shared/detect_project.py --path "$(pwd)"`
2. **Extract metadata** — name, description, version, author, license. Use `pyproject.toml` `description` as tagline if available (add emojis, preserve core message). If no description, write crafted tagline back.
3. **Check/generate logo** — look for `logo.png`, generate with project-logo-author if missing
4. **Calculate display width** — half actual pixel width for retina
5. **Generate README.md** — following Hook → Prove → Enable → Extend structure

### Modify Workflow

1. Read existing README, identify sections, detect custom content
2. Confirm uncertain deletions via AskUserQuestion
3. Apply requested changes (follow pyproject.toml tagline sync rules)
4. Validate result — no broken links or formatting

### Validate Workflow

Run Essential → Professional → Elite checklists plus project-type specifics. Calculate weighted score, generate report with actionable recommendations. See [references/validation-guide.md](references/validation-guide.md).

### Optimize Workflow

1. Run validation to identify issues
2. Apply quick wins (safe auto-fixes)
3. Present suggestions requiring approval (follow pyproject.toml tagline sync rules)
4. Re-validate and show improvement
