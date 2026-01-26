# SKILL.md Specification Details

Full reference for the [Agent Skills Specification](https://agentskills.io/specification).

## Frontmatter Fields

### Required Fields

#### `name`

- **Type:** string
- **Constraints:**
  - 1-64 characters
  - Lowercase letters (a-z), numbers (0-9), hyphens (-) only
  - No leading or trailing hyphens
  - No consecutive hyphens (--)
  - Must exactly match parent directory name
  - Cannot contain "anthropic" or "claude" (repository rule)
- **Purpose:** Becomes the slash command (`/name`)

#### `description`

- **Type:** string
- **Constraints:**
  - 1-1024 characters
  - Non-empty (cannot be whitespace only)
- **Best Practices:**
  - Write in third person ("Generates..." not "Generate...")
  - Include trigger phrases ("Use when...", "Triggers on...")
  - Include keywords Claude can match against
  - Describe both WHAT and WHEN

### Optional Fields

#### `license`

- **Type:** string
- **Constraints:** None
- **Repository Rule:** Use `MIT` for all skills in this repo

#### `compatibility`

- **Type:** string
- **Constraints:** Max 500 characters
- **Purpose:** Environment requirements
- **Examples:**
  - `python 3.8+`
  - `requires mcp-openrouter MCP server`
  - `macOS and Linux only`

#### `metadata`

- **Type:** key-value mapping (object)
- **Purpose:** Author, version, custom properties
- **Standard Keys:**
  - `author`: Your name/handle
  - `version`: Semantic version (e.g., "1.0.0")
- **Example:**
  ```yaml
  metadata:
    author: your-name
    version: "1.0.0"
    category: utility
  ```

#### `allowed-tools`

- **Type:** space-delimited string
- **Purpose:** Pre-approved tools (experimental)
- **Example:** `Read Glob Grep Bash(npm*)`

#### `argument-hint`

- **Type:** string
- **Purpose:** Shows in autocomplete what arguments the slash command expects
- **Examples:**
  - `[file-path]`
  - `[issue-number]`
  - `[analyze|clean|auto-fix]`
  - `[project|plugin] [skill-name]`

#### `disable-model-invocation`

- **Type:** boolean
- **Default:** `false`
- **Purpose:** When `true`, skill can only be invoked manually via `/name`
- **Use Case:** Prevent accidental triggering for destructive operations

#### `user-invocable`

- **Type:** boolean
- **Default:** `true`
- **Purpose:** When `false`, hides skill from `/` menu
- **Note:** Claude can still trigger it automatically based on description

## Progressive Disclosure Tiers

Skills use 3-tier loading to minimize context usage:

### Tier 1: Metadata (~100 tokens)

- Loaded at startup for ALL installed skills
- Contains: `name` and `description` only
- Used for: Skill selection, matching user intent

### Tier 2: SKILL.md Body (<5000 tokens)

- Loaded when skill triggers (explicit `/name` or auto-triggered)
- Contains: Everything between `---` markers and end of file
- Budget: **15,000 characters maximum** (hard limit)

### Tier 3: Bundled Resources (variable)

- Loaded on-demand when Claude reads them
- Located in:
  - `scripts/` - Executable code
  - `references/` - Additional documentation
  - `assets/` - Static files (templates, icons)
- Keep references one level deep from SKILL.md

## Size Limits Summary

| Element | Limit | Enforcement |
|---------|-------|-------------|
| `name` | 64 chars | Error |
| `description` | 1024 chars | Error |
| `compatibility` | 500 chars | Error |
| SKILL.md total | 15,000 chars | Error |
| Body lines | 500 lines | Warning |

## File Structure

```
skill-name/
├── SKILL.md          # Required - skill definition and instructions
├── scripts/          # Executable code Claude can run
│   └── *.py          # Python scripts (use UV for deps)
├── references/       # On-demand documentation
│   └── *.md          # Detailed guides, specs
└── assets/           # Static resources
    └── *             # Templates, icons, fonts
```

- **scripts/**: Token-efficient - code runs without loading into context
- **references/**: Loaded only when Claude needs detailed information
- **assets/**: Output files, never loaded into context
