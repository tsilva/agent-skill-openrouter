<div align="center">
  <img src="logo.png" alt="claude-skills" width="512"/>

  # claude-skills

  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)](https://claude.ai/code)
  [![Skills](https://img.shields.io/badge/Skills-5-green)](plugins/)

  **🔧 Modular skills that supercharge Claude Code with specialized capabilities ⚡**

  [Installation](#-installation) · [Available Skills](#-available-skills) · [Creating Skills](#-creating-your-own-skills)
</div>

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Available Skills](#-available-skills)
  - [bash-output-styler](#bash-output-styler)
  - [project-logo-author](#project-logo-author)
  - [project-readme-author](#project-readme-author)
  - [project-spec-extractor](#project-spec-extractor)
  - [python-output-styler](#python-output-styler)
- [Creating Your Own Skills](#-creating-your-own-skills)
- [Repository Structure](#-repository-structure)
- [License](#-license)

---

## 🚀 Installation

Add this repository to your Claude Code plugins:

```bash
claude plugins:add tsilva/claude-skills
```

Or install individual skills by navigating to `Settings → Plugins → Add from URL` and using:

```
https://github.com/tsilva/claude-skills
```

---

## 🧩 Available Skills

### bash-output-styler
**v2.0.0** · Applies gorgeous terminal styling to bash scripts using gum with ANSI fallback

Style all user-facing shell script output with a bundled `style.sh` library that provides headers, spinners, tables, progress bars, and color-coded messages with graceful degradation.

```
/bash-output-styler [script-path]
```

---

### project-logo-author
**v5.1.0** · Generates professional logos with transparent backgrounds

Creates distinctive project logos using AI image generation. Requires the `mcp-openrouter` MCP server.

```
/project-logo-author
```

---

### project-readme-author
**v2.5.1** · Create and optimize README files

Create, modify, validate, and optimize README.md files following GitHub best practices with modern visual hierarchy.

```
/project-readme-author create|modify|validate|optimize
```

---

### project-spec-extractor
**v1.0.0** · Analyzes a codebase and generates a pure requirements specification

Extract what a project does into a clean SPEC.md — no implementation details, just behaviors, features, and acceptance criteria. Use for rebuilding projects from scratch, porting to different stacks, or living documentation.

```
/project-spec-extractor [--tech-agnostic] [path]
```

---

### python-output-styler
**v1.0.0** · Applies gorgeous terminal styling to Python scripts using Rich with plain-text fallback

Style all user-facing Python script output with a bundled `style.py` module that provides headers, spinners, tables, progress bars, and color-coded messages with graceful degradation.

```
/python-output-styler [script-path]
```

---

## 🛠 Creating Your Own Skills

Use the `plugin-dev` plugin to create new skills following the official specification:

```
/plugin-dev:skill-development
```

### Skill Structure

```
plugins/
└── my-skill/
    ├── .claude-plugin/
    │   └── plugin.json      # Plugin metadata
    └── skills/
        └── my-skill/
            ├── SKILL.md     # Skill instructions (required)
            ├── scripts/     # Executable code (optional)
            ├── references/  # Documentation (optional)
            └── assets/      # Static resources (optional)
```

### Design Principles

- **One plugin per skill** - Self-contained with independent versioning
- **Minimal dependencies** - Scripts use UV with inline dependency declarations
- **Absolute paths** - All file operations use absolute paths
- **MCP integration** - Skills can leverage MCP servers for external APIs

---

## 📁 Repository Structure

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json     # Lists all available plugins
├── plugins/
│   ├── bash-output-styler/
│   ├── project-logo-author/
│   ├── project-readme-author/
│   ├── project-spec-extractor/
│   └── python-output-styler/
├── shared/                  # Cross-skill utilities
├── CLAUDE.md                # Project instructions for Claude
├── README.md                # This file
└── logo.png                 # Repository logo
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with 🤖 Claude Code</sub>
</div>
