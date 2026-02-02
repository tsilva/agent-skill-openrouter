# Badges and Visual Elements

Reference material for badge implementation, visual elements, and social proof.

## Badge Implementation

```markdown
[![Build](https://img.shields.io/github/actions/workflow/status/user/repo/ci.yml?branch=main)](link)
[![Coverage](https://img.shields.io/codecov/c/github/user/repo)](link)
[![PyPI](https://img.shields.io/pypi/v/package-name)](link)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](link)
[![Downloads](https://img.shields.io/pypi/dm/package-name)](link)
[![Discord](https://img.shields.io/discord/SERVER_ID)](link)
```

**Rules:**
- Use shields.io for all badges (consistent styling)
- Pick one style (flat, flat-square, for-the-badge) and use it consistently
- For CLI tools, include a Repology badge showing packaging status

## Dark/Light Mode Support

For theme-aware logos, use the `<picture>` element:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="logo-light.png">
  <img src="logo-light.png" alt="Project Name" width="{DISPLAY_WIDTH}">
</picture>
```

## Visual Elements

### GIF Demos (Mandatory for CLI Tools)

Terminal recordings are mandatory for CLI tools. Use:
- **vhs** - scripted terminal GIFs (recommended)
- **terminalizer** - interactive recording
- **asciinema** - terminal session sharing

**GIF Requirements:**
- Under 10MB (GitHub limit)
- 10-15fps is sufficient
- Show the "aha moment" - core value in action
- Drag-drop into README editor to host on GitHub's CDN

### Screenshots

For UI-heavy projects:
- Include both light and dark mode versions
- Compress before adding (ImageOptim, XConvert)
- Use descriptive alt text

### Tables

Use tables for:
- Feature comparisons
- API parameters
- Benchmark results
- Installation matrices (cross-platform)

### Architecture Diagrams

For complex projects, use Mermaid (GitHub-native):

```markdown
```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
```
```

## Social Proof

### "Used By" Section

Place prominently after hero section with 6-12 company logos:

```markdown
## Used By

<p align="center">
  <img src="logos/company1.svg" alt="Company 1" height="40">
  &nbsp;&nbsp;&nbsp;
  <img src="logos/company2.svg" alt="Company 2" height="40">
</p>
```

### Star CTA

Engaging call-to-action patterns:
- `⭐ Star if this saved you hours of debugging!`
- `🌟 If this helped, a star would make our day!`

**Rules**: One CTA max. Humor optional but never cringe.

### Community Links

```markdown
[![Discord](https://img.shields.io/discord/SERVER_ID?label=Discord&logo=discord)](link)
[![Twitter](https://img.shields.io/twitter/follow/handle?style=social)](link)
```

### Supporting Files

These files signal project maturity:
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- LICENSE
