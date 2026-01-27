<div align="center">
  <img src="logo.png" alt="claude-skills" width="512"/>

  # claude-skills

  [![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-DA7856?style=flat&logo=anthropic)](https://claude.ai/code)
  [![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/tsilva/claude-skills?style=flat)](https://github.com/tsilva/claude-skills/stargazers)

  **🔌 Supercharge Claude Code with auto-generated READMEs, custom logos, and security auditing**

  [Documentation](CLAUDE.md) · [Skills Marketplace](#installation)
</div>

---

## Table of Contents

- [Why Claude Skills?](#why-claude-skills)
- [Available Skills](#available-skills)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Skills](#skills)
  - [README Generator](#readme-generator)
  - [Repo Logo Generator](#repo-logo-generator)
  - [Repo Name Generator](#repo-name-generator)
  - [Settings Author](#settings-author)
- [Repository Structure](#repository-structure)
- [Dependency Management](#dependency-management)
- [Adding New Skills](#adding-new-skills)
- [Contributing](#contributing)
- [License](#license)

---

## Why Claude Skills?

- **📝 Professional READMEs in seconds** - Auto-generate documentation following GitHub best practices
- **🎨 Custom logos on demand** - Create minimalist repo logos with AI image generation
- **🔐 Security auditing built-in** - Automatically identify and clean up dangerous or redundant permissions
- **⚡ Plug and play** - Install only what you need, each skill works independently

> **Note:** For access to 300+ AI models (GPT-5, Gemini, Llama, Mistral, etc.), use the [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server.

## Available Skills

| Skill | Description | Version | Slash Command |
|-------|-------------|---------|---------------|
| [README Generator](#readme-generator) | Create cutting-edge README files with badges and visual hierarchy | 2.0.2 | `/project-readme-author` |
| [Repo Logo Generator](#repo-logo-generator) | Generate logos with native transparent backgrounds (requires mcp-openrouter) | 5.0.0 | `/project-logo-author` |
| [Repo Name Generator](#repo-name-generator) | Generate creative, memorable repository names | 2.0.0 | `/project-name-author` |
| [Settings Author](#settings-author) | Audit and optimize Claude Code permission whitelists | 1.1.1 | `/claude-settings-author` |

## Installation

### Via Claude Code Marketplace

```bash
# Add the skills marketplace
/skills-discovery tsilva/claude-skills

# Or install individual skills directly
/skills-discovery project-readme-author
/skills-discovery project-logo-author
/skills-discovery claude-settings-author
```

### Manual Installation

```bash
git clone https://github.com/tsilva/claude-skills.git
cd claude-skills
git config core.hooksPath hooks  # Enable pre-commit version validation
```

## Quick Start

### Using Slash Commands

All skills are available as slash commands in Claude Code. Simply type `/` to see available commands with autocomplete:

```bash
/project-readme-author              # Generate a README for the current project
/project-readme-author ./my-project # Generate README for a specific path
/project-logo-author           # Generate a logo for your repository
/project-logo-author minimalist # Generate with a specific style preference
/claude-settings-author analyze      # Analyze permission whitelists
/claude-settings-author clean        # Interactive cleanup with confirmations
/claude-settings-author auto-fix     # Auto-remove redundant permissions
```

You can also ask Claude to use these skills naturally:
- "Create a README for this project" → triggers `/project-readme-author`
- "Generate a logo for my repo" → triggers `/project-logo-author`
- "Clean up my settings" → triggers `/claude-settings-author`

### Logo Generation

Logo generation uses the [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server:

1. **Generate image** via `mcp__openrouter__generate_image` with green background
2. **Apply chromakey** via the bundled script to convert green to transparent

Simply use `/project-logo-author` and Claude handles the workflow automatically.

---

## Skills

### README Generator

<p>
  <img src="https://img.shields.io/badge/Version-2.0.2-green?style=flat" alt="Version">
</p>

Create READMEs that hook readers in 5 seconds, prove value in 30 seconds, and enable success in under 10 minutes.

#### Framework: Hook -> Prove -> Enable -> Extend

| Phase | Time | Purpose |
|-------|------|---------|
| **Hook** | 0-5 sec | Logo + badges + one-liner |
| **Prove** | 5-30 sec | Features + social proof |
| **Enable** | 30s - 10m | Install + working example |
| **Extend** | Committed | Docs + contributing |

#### Features

- **Smart analysis** - Auto-detects project type, language, framework
- **Modern design** - Centered hero, badge collections, visual hierarchy
- **Logo integration** - Works with project-logo-author skill
- **Best practices** - Follows GitHub README conventions

[Full documentation](plugins/project-readme-author/skills/project-readme-author/SKILL.md)

---

### Repo Logo Generator

<p>
  <img src="https://img.shields.io/badge/Version-5.0.0-green?style=flat" alt="Version">
  <a href="https://github.com/tsilva/mcp-openrouter"><img src="https://img.shields.io/badge/Requires-mcp--openrouter-6366f1?style=flat" alt="Requires mcp-openrouter"></a>
</p>

Generate professional logos with transparent backgrounds using chromakey technology. Uses [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server to generate logos with Gemini, then applies professional chromakey for smooth transparency.

#### Features

- **Chromakey transparency** - Industry-standard green screen technique eliminates halo artifacts
- **Multiple styles** - Supports minimalist, pixel art, vector, and complex designs
- **Configurable** - Customize colors, style, and model via JSON config files
- **MCP integration** - Uses mcp-openrouter for AI image generation

#### Visual Metaphors

| Project Type | Metaphor |
|--------------|----------|
| CLI tool | Geometric terminal, origami |
| Library | Interconnected blocks |
| Web app | Modern interface window |
| API | Messenger bird with data |
| Framework | Architectural scaffold |

#### Prerequisites

Requires the [mcp-openrouter](https://github.com/tsilva/mcp-openrouter) MCP server to be configured.

[Full documentation](plugins/project-logo-author/skills/project-logo-author/SKILL.md)

---

### Repo Name Generator

<p>
  <img src="https://img.shields.io/badge/Version-2.0.0-green?style=flat" alt="Version">
</p>

Generate creative, memorable repository names optimized for virality. Analyzes your project to suggest names that are catchy, searchable, and shareable.

#### Virality Criteria

| Factor | Description | Examples |
|--------|-------------|----------|
| **Memorable** | Short, easy to spell/say | `vite`, `bun`, `deno` |
| **Searchable** | Unique, SEO-friendly | `fastapi`, `prisma` |
| **Shareable** | Fun to mention | `husky`, `panda` |
| **Descriptive** | Hints at purpose | `typescript`, `autoprefixer` |
| **Clever** | Wordplay, metaphors | `yarn`, `brew`, `nest` |

#### Features

- **Smart analysis** - Examines README, package files, and source code
- **Diverse styles** - Creative, professional, playful, technical, and punny options
- **6 suggestions** - Always provides exactly 6 name options with taglines

[Full documentation](plugins/project-name-author/skills/project-name-author/SKILL.md)

---

### Settings Author

<p>
  <img src="https://img.shields.io/badge/Version-1.1.1-green?style=flat" alt="Version">
  <img src="https://img.shields.io/badge/Security-Audit-red?style=flat" alt="Security">
</p>

Audit and optimize Claude Code permission whitelists by identifying dangerous patterns, overly specific approvals, and redundant entries.

#### What It Checks

| Category | Description | Example |
|----------|-------------|---------|
| 🔴 **Dangerous** | Overly broad permissions | `Bash(*:*)`, `Read(/*)`, `Skill(*)` |
| 🟡 **Specific** | Hardcoded arguments | `Bash(python test.py)` → `Bash(python:*)` |
| 🔵 **Redundant** | Covered by broader permission | Project has `Bash(ls -la)`, global has `Bash(ls:*)` |
| ✅ **Good** | Well-scoped permissions | `Bash(pytest:*)`, `Read(/Users/name/*)` |

**New in v1.1.0**: Self-awareness detection - the tool now detects when it's analyzing its own permissions and provides guidance on whether to retain them.

#### Commands

```bash
# Analyze permissions (read-only)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama plugins/claude-settings-author/skills/claude-settings-author/scripts/settings_cleaner.py analyze

# Interactive cleanup with confirmations
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama plugins/claude-settings-author/skills/claude-settings-author/scripts/settings_cleaner.py clean

# Auto-fix redundant permissions only (safest)
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with colorama plugins/claude-settings-author/skills/claude-settings-author/scripts/settings_cleaner.py auto-fix
```

#### Safety Features

- **Automatic backups** - Creates `.bak` files before any modifications
- **Interactive mode** - Prompts for each dangerous/specific pattern
- **Auto-fix safety** - Only removes redundancies (no dangerous changes)
- **Color-coded output** - Clear visual categorization of issues

#### Usage from Claude Code

Simply ask:
- "Clean up my settings"
- "Review my permissions"
- "Audit my security settings"

[Full documentation](plugins/claude-settings-author/skills/claude-settings-author/SKILL.md)

---

## Repository Structure

```
claude-skills/
├── plugins/
│   ├── project-readme-author/   # README Generator skill (v2.0.2)
│   ├── project-logo-author/     # Logo Generator skill (v5.0.0)
│   ├── project-name-author/     # Repo Name Generator skill (v2.0.0)
│   ├── claude-settings-author/  # Settings Author skill (v1.1.1)
│   └── claude-skill-author/     # Skill authoring tools (v1.3.2)
├── .claude-plugin/
│   └── marketplace.json         # Plugin registry
├── logo.png                     # Repository logo
├── CLAUDE.md                    # Developer documentation
└── README.md                    # This file
```

## Dependency Management

This repository follows Agent Skills best practices using **UV for portable, zero-setup execution**:

```bash
UV_CACHE_DIR=/tmp/claude/uv-cache uv run --with pillow scripts/chromakey.py ...
```

**Benefits:**
- No environment setup required
- Dependencies declared inline (PEP 723 standard)
- Automatic caching for fast execution
- Full portability across systems

**macOS Sandbox Note:** On macOS, UV may require `dangerouslyDisableSandbox` because it accesses system configuration APIs. This is a known UV limitation.

## Adding New Skills

See [CLAUDE.md](CLAUDE.md#adding-a-new-skill) for step-by-step instructions on creating skills.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-skill`)
3. Add your skill following the structure in [CLAUDE.md](CLAUDE.md)
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgements

- **[Claude Code](https://claude.ai/code)** - AI-powered development by Anthropic
- **[shields.io](https://shields.io)** - Badge generation service

---

<p align="center">
  Made with Claude Code
</p>
