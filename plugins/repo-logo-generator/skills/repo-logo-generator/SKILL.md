---
name: repo-logo-generator
description: Generate logos for GitHub repositories via OpenRouter with native transparent backgrounds using GPT-5 Image. Works with pixel art, vector designs, and complex multi-colored styles. Use when asked to "generate a logo", "create repo logo", or "make a project logo".
metadata:
  version: "3.0.1"
---

# Repo Logo Generator

Generate professional logos with native transparent backgrounds using GPT-5 Image via OpenRouter.

## REQUIRED: Execution Checklist (MUST complete in order)

Follow these steps exactly. Do not skip steps or improvise.

- [ ] **Step 1**: Load config by reading each path in order (stop at first that exists):
  1. Read `./.claude/readme-generator.json` (project config)
  2. Read `~/.claude/readme-generator.json` (user config)
  3. Read `assets/default-config.json` from this skill's directory (default)

  **IMPORTANT**: Actually READ each file path, don't just search for JSON files.
- [ ] **Step 2**: Check if config has `style` parameter:
  - **If YES** (user has custom settings): Use the `config.style` value AS-IS for the entire prompt. DO NOT use the template below. DO NOT enforce "no text" or "vector style" rules. The user's style setting completely overrides all defaults.
  - **If NO** (using defaults): Continue to Step 3.
- [ ] **Step 3**: Read project files (README, package.json, etc.) to determine project type
- [ ] **Step 4**: Select visual metaphor from the table below and fill the prompt template
- [ ] **Step 5**: Generate logo using OpenRouter with native transparency:
  - Use `openai/gpt-5-image` model (or configured `config.model`)
  - Add `--background transparent` flag for transparent background
  - Save directly to `logo.png`
  - Command format:
    ```bash
    UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests \
      plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
      "openai/gpt-5-image" \
      "[YOUR PROMPT HERE]" \
      --background transparent \
      --output logo.png
    ```
- [ ] **Step 6**: Verify logo exists and is valid PNG with transparency

## Prompt Template (MANDATORY - DO NOT MODIFY FORMAT)

You MUST construct the prompt using this EXACT template. Do not paraphrase, do not add creative flourishes, do not skip any line.

```
A {config.style} logo for {PROJECT_NAME}: {VISUAL_METAPHOR_FROM_TABLE}.
Clean vector style. Icon colors from: {config.iconColors}.
No text, no letters, no words. Single centered icon, geometric shapes, works at {config.size}.
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
No text, no letters, no words. Single centered icon, geometric shapes, works at 64x64.
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
GPT-5 Image supports native transparent background generation via the `background: "transparent"` parameter. The OpenRouter client passes this through using the `--background transparent` flag.

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
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with requests \
  plugins/openrouter/skills/openrouter/scripts/openrouter_client.py image \
  "openai/gpt-5-image" \
  "Your logo prompt here" \
  --background transparent \
  --output logo.png
```

**Note on Sandbox Mode**: The `UV_CACHE_DIR=/tmp/claude/uv-cache` prefix ensures `uv` uses an allowed cache directory. When Claude runs these commands, it may still need to disable sandbox due to `uv` accessing macOS system configuration APIs. Users running commands manually won't encounter this restriction.
