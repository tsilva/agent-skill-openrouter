---
name: repo-logo-generator
description: Generate logos for GitHub repositories via OpenRouter with native transparent backgrounds using GPT-5 Image. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
license: MIT
compatibility: python 3.8+, requires requests library, uses OpenRouter skill
metadata:
  version: "3.0.3"
---

# Repo Logo Generator

Generate professional logos with native transparent backgrounds using GPT-5 Image via OpenRouter.

## Path Resolution

The OpenRouter client must be resolved from the plugin cache using an absolute path. Never use relative paths when invoking scripts from other plugins.

**Dynamic resolution (recommended):**
```bash
# Find latest OpenRouter version
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/openrouter 2>/dev/null | sort -V | tail -n 1)
OPENROUTER_CLIENT="$HOME/.claude/plugins/cache/claude-skills/openrouter/$LATEST_VERSION/skills/openrouter/scripts/openrouter_client.py"

# Verify it exists
if [ ! -f "$OPENROUTER_CLIENT" ]; then
  echo "Error: OpenRouter plugin not found. Install via: /skills-discovery openrouter" >&2
  exit 1
fi

# Use in command
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests "$OPENROUTER_CLIENT" image \
  "model-name" \
  "Your prompt here" \
  --output logo.png
```

**Important:** Always validate that the OpenRouter client exists before attempting to execute it. If not found, inform the user immediately and do not proceed.

## REQUIRED: Execution Checklist (MUST complete in order)

Follow these steps exactly. Do not skip steps or improvise.

- [ ] **Step 0**: Create Todo List
  - Use TodoWrite to create a todo list with these items:
    1. Validate dependencies (find OpenRouter client, check API key)
    2. Load configuration files (project → user → default)
    3. Read project documentation to determine type
    4. Generate logo using OpenRouter
    5. Verify logo file and properties

  This is a multi-step task requiring todo list tracking per TodoWrite guidelines.

- [ ] **Step 1**: Validate Dependencies
  - Locate latest OpenRouter client using path resolution logic above
  - Verify `SKILL_OPENROUTER_API_KEY` environment variable is set
  - If either check fails, report to user immediately and do not proceed
  - Mark "Validate dependencies" todo as completed

- [ ] **Step 2**: Load config by reading each path in order (stop at first that exists):
  1. Read `./.claude/readme-generator.json` (project config)
  2. Read `~/.claude/readme-generator.json` (user config)
  3. Read `assets/default-config.json` from this skill's directory (default)

  **IMPORTANT**: Actually READ each file path, don't just search for JSON files.
  Mark "Load configuration files" todo as completed after this step.

- [ ] **Step 3**: Check if config has `style` parameter:
  - **If YES** (user has custom settings): Use the `config.style` value AS-IS for the entire prompt. DO NOT use the template below. DO NOT enforce "no text" or "vector style" rules. The user's style setting completely overrides all defaults.
  - **If NO** (using defaults): Continue to Step 4.

- [ ] **Step 4**: Read project files (README, package.json, etc.) to determine project type
  Mark "Read project documentation" todo as completed after this step.

- [ ] **Step 5**: Select visual metaphor from the table below and fill the prompt template

- [ ] **Step 6**: Generate logo using OpenRouter with native transparency:
  - Use `openai/gpt-5-image` model (or configured `config.model`)
  - Add `--background transparent` flag for transparent background
  - Save directly to `logo.png`
  - Use absolute path to OpenRouter client (resolved in Step 1)
  - Command format:
    ```bash
    UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests \
      "$OPENROUTER_CLIENT" image \
      "openai/gpt-5-image" \
      "[YOUR PROMPT HERE]" \
      --background transparent \
      --output logo.png
    ```
  Mark "Generate logo using OpenRouter" todo as completed after this step.

- [ ] **Step 7**: Verify logo exists and is valid PNG with transparency
  Mark "Verify logo file and properties" todo as completed after this step.

## Sandbox Compatibility

⚠️ **macOS Limitation**: On macOS, `uv run` may require `dangerouslyDisableSandbox: true` because UV accesses system configuration APIs (`SystemConfiguration.framework`) to detect proxy settings. This is a known UV limitation on macOS systems.

**Behavior:**
- On first execution, Claude may attempt with sandbox enabled
- If it fails with system-configuration errors, Claude will retry with sandbox disabled
- This is expected behavior and does not indicate a security issue

**Alternative (for restricted environments):**
If sandbox restrictions are problematic, you can pre-install dependencies:
```bash
python3 -m pip install requests
python3 /absolute/path/to/openrouter_client.py image MODEL "prompt" --output logo.png
```

However, we recommend the standard UV approach for portability and zero-setup benefits.

## Prompt Template (MANDATORY - DO NOT MODIFY FORMAT)

You MUST construct the prompt using this EXACT template. Do not paraphrase, do not add creative flourishes, do not skip any line.

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR_FROM_TABLE}.
Clean vector style. Icon colors from: {config.iconColors}.
Transparent background. No text, no letters, no words. Single centered icon, geometric shapes, works at {config.size}.
```

**Default values** (when no config exists):
- `config.style` = `minimalist`
- `config.iconColors` = `#ffffff, #58a6ff, #3fb950, #d29922, #a371f7`
- `config.size` = `64x64`
- `config.model` = `openai/gpt-5-image`

### Filled Example

For a CLI tool called "fastgrep":

```
A minimalist logo for fastgrep: A magnifying glass with speed lines forming a geometric pattern.
Clean vector style. Icon colors from: #ffffff, #58a6ff, #3fb950, #d29922, #a371f7.
Transparent background. No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64.
```

## Visual Metaphors by Project Type (MUST use this table)

Select the metaphor that matches the project type. Do NOT invent alternatives.

| Project Type | Visual Metaphor |
|--------------|-----------------|
| CLI tool | Origami transformation, geometric terminal |
| Library | Interconnected building blocks |
| Web app | Modern interface window, minimal chrome |
| API | Messenger bird carrying data packet |
| Framework | Architectural scaffold, blueprint |
| Tool | Precision instrument, sharp edges |
| Converter | Metamorphosis symbol (butterfly) |
| Runner | Sprinter in motion, speed lines |
| Validator | Wax seal of approval |
| Linter | Elegant brush sweeping |
| Test framework | Test tube with checkmarks |
| Dashboard | Mission control panel |
| Analytics | Magnifying glass revealing patterns |
| Database | Stacked cylinders, data nodes |
| Security | Shield, lock, key |
| Default | Abstract geometric shape |

## ❌ DO NOT

- Invent custom visual metaphors (use the table above)
- Paraphrase the template (use it verbatim with values filled in)
- Add extra descriptive language like "network nodes", "data fragments", "circuit patterns", "flowing streams"
- Skip any line of the template
- Add "gradient", "3D", "glossy", "photorealistic" or similar non-minimalist styles
- Include text, letters, or words in the logo description

## Configuration Reference

Logo generation can be customized via configuration files. Check in order (first found wins):

1. **Project config**: `./.claude/readme-generator.json`
2. **User config**: `~/.claude/readme-generator.json`
3. **Default config**: `assets/default-config.json` (bundled with this skill)

Read JSON if exists, extract `logo` object. Project overrides user overrides default.

### Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `iconColors` | `["#ffffff", "#58a6ff", "#3fb950", "#d29922", "#a371f7"]` | Preferred icon colors |
| `style` | `minimalist` | Logo style description (completely overrides default prompt if set) |
| `size` | `64x64` | Target size for logo |
| `aspectRatio` | `1:1` | Aspect ratio for generation |
| `model` | `openai/gpt-5-image` | OpenRouter model for image generation (GPT-5 Image supports native transparency) |

### Example Configuration

**Minimalist style (default):**
```json
{
  "logo": {
    "iconColors": ["#7aa2f7", "#bb9af7", "#7dcfff"],
    "style": "minimalist",
    "model": "openai/gpt-5-image"
  }
}
```

**Pixel art style (LucasArts adventure game aesthetic):**
```json
{
  "logo": {
    "iconColors": "Vibrant saturated colors inspired by classic LucasArts VGA adventure games",
    "style": "Pixel art in the painterly style of classic LucasArts VGA adventure games (1990s era). Create a charming character mascot with a funny expression. Surround with floating icon-only symbols relevant to the project. Use classic adventure game title banner style with ornate border. Rich dithering, vibrant saturated colors, whimsical and humorous. MUST include the project name as pixel art text in the banner.",
    "model": "openai/gpt-5-image"
  }
}
```

## Native Transparent Backgrounds

**How it works:**
GPT-5 Image supports native transparent background generation. To generate transparent backgrounds, you must specify transparency in BOTH:
1. **API parameter**: Use `--background transparent` flag in the command
2. **Prompt text**: Include "Transparent background" in the prompt itself

Both are required - the API parameter alone is not sufficient.

**Benefits:**
- ✅ **Single generation** - no post-processing required
- ✅ **No color constraints** - use any colors including magenta/pink
- ✅ **Real alpha channel** - proper RGBA transparency
- ✅ **Works with all styles** - pixel art, vector, complex designs
- ✅ **Clean edges** - AI-generated smooth transparency

**Compatibility:**
- ✅ Multi-colored pixel art (character sprites, detailed scenes)
- ✅ Complex LucasArts/adventure game styles
- ✅ Logos with text labels and detailed shading
- ✅ Minimalist vector designs
- ✅ Any style that GPT-5 Image supports

**Quality:**
GPT-5 Image consistently produces high-quality transparent backgrounds with proper alpha channels. Tested results show 50-90% transparency depending on logo complexity, with all corners transparent for centered designs.

## Technical Requirements

Logos must meet these criteria:
- **Centered**: Works in circular and square crops
- **High contrast**: Clear visibility on various backgrounds
- **Clean style**: Works at multiple sizes (16x16 to 512x512)
- **Single focal point**: One clear visual element

## Usage

Use the **openrouter** skill's image generation capability with the `--background transparent` flag:

```bash
# Resolve OpenRouter client path (see Path Resolution section above)
LATEST_VERSION=$(ls -1 ~/.claude/plugins/cache/claude-skills/openrouter 2>/dev/null | sort -V | tail -n 1)
OPENROUTER_CLIENT="$HOME/.claude/plugins/cache/claude-skills/openrouter/$LATEST_VERSION/skills/openrouter/scripts/openrouter_client.py"

# Generate logo with transparent background
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests \
  "$OPENROUTER_CLIENT" image \
  "openai/gpt-5-image" \
  "Your logo prompt here" \
  --background transparent \
  --output logo.png
```

**Note on Sandbox Mode**: The `UV_CACHE_DIR=/tmp/claude/uv-cache` prefix ensures `uv` uses an allowed cache directory. When Claude runs these commands, it may still need to disable sandbox due to `uv` accessing macOS system configuration APIs (see Sandbox Compatibility section above).
