---
name: repo-logo-generator
description: Generate logos for GitHub repositories using mcp-openrouter with programmatic transparency conversion. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: python 3.8+, requires pillow library, requires mcp-openrouter MCP server
argument-hint: "[style-preference]"
disable-model-invocation: false
user-invocable: true
metadata:
  version: "4.0.0"
---

# Repo Logo Generator

Generate professional logos with transparent backgrounds using:
1. **mcp-openrouter** MCP tool generates logo with green (#00FF00) background
2. **PIL chromakey script** converts green to transparent with smooth edges

## REQUIRED: Execution Checklist

Follow these steps exactly. Do not skip steps.

### Step 1: Load Configuration

Read config files in order (first found wins):
1. `./.claude/readme-generator.json` (project config)
2. `~/.claude/readme-generator.json` (user config)
3. Use defaults if no config found

**Default values:**
- `style` = `minimalist`
- `iconColors` = `#58a6ff, #d29922, #a371f7, #7aa2f7, #f97583`
- `size` = `1K`
- `model` = `google/gemini-3-pro-image-preview`
- `keyColor` = `#00FF00`
- `tolerance` = `70`

### Step 2: Check for Custom Style

- **If config has `style` parameter**: Use `config.style` AS-IS for the prompt. Skip to Step 4.
- **If no custom style**: Continue to Step 3.

### Step 3: Build Prompt from Template

Read project files (README, package.json, etc.) to determine project type, then use this template:

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR}.
Clean vector style. Icon colors from: {config.iconColors}.
Pure bright green (#00FF00) background only. Do not use green tones anywhere in the design.
No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64.
```

**Visual Metaphors by Project Type:**

| Type | Metaphor |
|------|----------|
| CLI tool | Origami transformation, geometric terminal |
| Library | Interconnected building blocks |
| Web app | Modern interface window |
| API | Messenger bird carrying data packet |
| Framework | Architectural scaffold |
| Converter | Metamorphosis symbol (butterfly) |
| Database | Stacked cylinders, data nodes |
| Security | Shield, lock, key |
| Default | Abstract geometric shape |

### Step 4: Generate Image with MCP Tool

Use the `mcp__openrouter__generate_image` tool:

```
model: "google/gemini-3-pro-image-preview" (or config.model)
prompt: [your constructed prompt]
output_path: /tmp/claude/logo_raw.png
aspect_ratio: "1:1"
size: "1K"
```

### Step 5: Apply Chromakey Transparency

Locate the chromakey script and run it:

```bash
# Find script in plugin cache
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/repo-logo-generator 2>/dev/null | sort -V | tail -n 1)
SCRIPT="$HOME/.claude/plugins/cache/claude-skills/repo-logo-generator/$LATEST_VERSION/skills/repo-logo-generator/scripts/generate_logo.py"

# Apply transparency
uv run --with pillow "$SCRIPT" /tmp/claude/logo_raw.png \
  --output logo.png \
  --key-color "#00FF00" \
  --tolerance 70
```

### Step 6: Verify Output

Confirm logo.png exists and is a valid PNG with transparency.

## Configuration Reference

Config files use this structure:
```json
{
  "logo": {
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "minimalist",
    "model": "google/gemini-3-pro-image-preview",
    "keyColor": "#00FF00",
    "tolerance": 70
  }
}
```

**Pixel art example:**
```json
{
  "logo": {
    "style": "SNES 16-bit pixel art. Charming mascot. VISIBLE CHUNKY PIXELS with dithering. Bright saturated colors. Pure green (#00FF00) background only.",
    "keyColor": "#00FF00",
    "tolerance": 70
  }
}
```

## Chromakey Script Options

```bash
uv run --with pillow generate_logo.py INPUT --output OUTPUT [options]

Options:
  --key-color "#00FF00"    Chromakey color (default: green)
  --tolerance 70           Color tolerance (default: 70)
  --no-compress            Skip PNG compression
```

## DO NOT

- Invent custom visual metaphors (use the table)
- Add "gradient", "3D", "glossy" styles
- Include text in logos
- Use green tones in the icon (reserved for chromakey)
- Skip the chromakey conversion step
