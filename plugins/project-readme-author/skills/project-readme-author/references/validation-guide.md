# Validation Guide

Reference material for the validate and optimize operations.

## Scoring Output Format

```
README Validation Report
========================

Overall Score: 72/100 (Professional)

ESSENTIAL (Required) - 6/7 passed
  ✅ Project logo present
  ✅ Badges (5 found)
  ✅ One-liner description
  ❌ GIF/screenshot missing
  ✅ Installation command
  ✅ Code example
  ✅ License info

PROFESSIONAL - 4/6 passed
  ✅ Table of contents
  ✅ Feature highlights
  ❌ Multiple install methods
  ✅ Documentation links
  ✅ Contributing section
  ❌ "Used by" logos

ELITE - 1/6 passed
  ❌ Dark/light mode images
  ❌ Architecture diagram
  ❌ Benchmark comparisons
  ❌ FAQ section
  ✅ Star history graph
  ❌ Contributor avatars

Recommendations:
1. Add a GIF demo showing core functionality
2. Include installation options for npm, yarn, and pnpm
3. Add "Used by" section with company logos
```

## Scoring Tiers

| Tier | Score Range | Meaning |
|------|-------------|---------|
| Essential | 0-50 | Missing critical elements |
| Professional | 51-80 | Solid README, room for improvement |
| Elite | 81-100 | Exceptional, comprehensive README |

## Project-Type Specific Checks

For CLI tools, also check:
- [ ] Terminal GIF demo
- [ ] Cross-platform installation matrix
- [ ] Shell integration instructions

For AI/ML projects, also check:
- [ ] Model card with YAML metadata
- [ ] Hardware requirements table
- [ ] Citation in BibTeX format

## Quick Reference Checklists

### Essential (Must Include)

- [ ] Project logo (width = half actual pixels, centered)
- [ ] 4-7 relevant badges
- [ ] One-liner description ("What and why?")
- [ ] GIF/screenshot demonstration
- [ ] One-liner installation command
- [ ] Minimal working code example
- [ ] License information

### Professional Tier

- [ ] Table of contents (if >500 words)
- [ ] Feature highlights with benefits
- [ ] Multiple installation methods
- [ ] Documentation links
- [ ] Contributing section
- [ ] "Used by" company logos

### Elite Tier

- [ ] Dark/light mode image support
- [ ] Architecture diagram
- [ ] Benchmark comparisons
- [ ] FAQ section
- [ ] Star history graph
- [ ] Contributor avatars

### AI/ML Specific

- [ ] Model card with YAML metadata
- [ ] Hardware requirements table
- [ ] Benchmark results with reproducibility
- [ ] Colab/demo links
- [ ] Training vs. inference split
- [ ] Ethical considerations
- [ ] Citation in BibTeX format

### CLI Specific

- [ ] Terminal GIF demo
- [ ] Cross-platform installation matrix
- [ ] Shell integration instructions
- [ ] Configuration file examples
- [ ] Keybinding reference table
- [ ] Performance benchmarks
