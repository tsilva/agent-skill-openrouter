<div align="center">
  <img src="logo.png" alt="claude-skills" width="512"/>

  # claude-skills

  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Claude Code](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)](https://claude.ai/code)
  [![Skills](https://img.shields.io/badge/Skills-6-green)](plugins/)

  **🔧 Modular skills that supercharge Claude Code with specialized capabilities ⚡**

  [Installation](#-installation) · [Available Skills](#-available-skills) · [Creating Skills](#-creating-your-own-skills)
</div>

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Available Skills](#-available-skills)
  - [claude-skill-author](#claude-skill-author)
  - [claude-settings-author](#claude-settings-author)
  - [mcp-author](#mcp-author)
  - [project-logo-author](#project-logo-author)
  - [project-name-author](#project-name-author)
  - [project-readme-author](#project-readme-author)
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

### claude-skill-author
**v1.3.2** · Guides creation and modification of Claude Code agent skills

Create project-level, personal, and plugin-bundled marketplace skills with best practices baked in.

```
/claude-skill-author
```

---

### claude-settings-author
**v1.1.1** · Optimizes Claude Code settings configuration

Analyzes permission whitelists, detects dangerous patterns, identifies redundancies, and migrates WebFetch domains to sandbox network allowlists.

```
/claude-settings-author
```

---

### mcp-author
**v1.0.1** · Creates MCP servers using FastMCP

Build production-ready MCP servers with proper patterns for integrating external APIs with Claude Code.

```
/mcp-author
```

---

### project-logo-author
**v5.0.0** · Generates professional logos with transparent backgrounds

Creates distinctive project logos using AI image generation. Requires the `mcp-openrouter` MCP server.

```
/project-logo-author
```

---

### project-name-author
**v2.0.0** · Generates creative, memorable project names

Creates catchy, searchable names optimized for virality and discoverability.

```
/project-name-author
```

---

### project-readme-author
**v2.0.2** · Create and optimize README files

Create, modify, validate, and optimize README.md files following GitHub best practices with modern visual hierarchy.

```
/project-readme-author create|modify|validate|optimize
```

---

## 🛠️ Creating Your Own Skills

Use the `/claude-skill-author` skill to create new skills following the official specification:

```
/claude-skill-author create my-new-skill
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
│   ├── claude-skill-author/
│   ├── claude-settings-author/
│   ├── mcp-author/
│   ├── project-logo-author/
│   ├── project-name-author/
│   └── project-readme-author/
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
