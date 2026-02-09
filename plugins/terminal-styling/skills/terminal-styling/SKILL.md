---
name: terminal-styling
description: |
  Applies gorgeous terminal styling to shell scripts using gum with ANSI fallback.
  Use when creating or modifying shell scripts that produce user-facing terminal output.
  Use when asked to "style output", "make pretty", "add colors", or "improve terminal UX".
license: MIT
user-invocable: true
argument-hint: "[script-path]"
metadata:
  author: tsilva
  version: "1.0.0"
---

# Terminal Styling

Style all user-facing shell script output using the bundled `style.sh` library.

## Workflow

1. Read [references/style.sh](references/style.sh) to understand available functions
2. If `style.sh` doesn't exist alongside the target script, copy from [references/style.sh](references/style.sh) into the same directory
3. Source `style.sh` in the target script: `source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/style.sh" 2>/dev/null || true`
4. Replace raw `echo` statements with styled output function calls
5. Replace `read -p` prompts with `confirm`, `input`, or `choose` as appropriate
6. Wrap long-running commands with `spin` for animated feedback
7. Use `table` for structured multi-column data and `progress` for counted loops
8. Verify script still works when `style.sh` is missing (graceful degradation)

## Color Palette

| Name    | Hex       | ANSI 256 | Use                          |
|---------|-----------|----------|------------------------------|
| Brand   | `#AF87FF` | 141      | Headers, emphasis            |
| Success | `#87D787` | 114      | Checkmarks, completion       |
| Error   | `#FF5F5F` | 203      | Errors, failures             |
| Warning | `#FFD75F` | 221      | Warnings, caution            |
| Info    | `#87CEEB` | 117      | Info messages, tips          |
| Muted   | `#808080` | 244      | Paths, secondary text        |

## Output Functions

| Function | Symbol | Color | Purpose |
|----------|--------|-------|---------|
| `header "brand" "subtitle"` | box | Brand | Bordered header |
| `section "text"` | `━━` | Brand | Horizontal rule divider (fills terminal width) |
| `success "text"` | `✓` | Success | Completed actions |
| `error "text"` | `✗` | Error | Error messages |
| `warn "text"` | `⚠` | Warning | Warnings |
| `info "text"` | `●` | Info | Informational |
| `step "text"` | `→` | Muted | Action log (suppressed when quiet) |
| `note "text"` | — | Muted | "Note:" prefixed |
| `banner "text"` | box | Success | Completion banner |
| `error_block "lines..."` | `│` | Error | Multi-line error box |
| `list_item "label" "value"` | `•` | Brand+Muted | Key-value display |
| `dim "text"` | — | Muted | De-emphasized text (suppressed when quiet) |
| `table "h1,h2" "v1,v2" ...` | box | Brand+Muted | Formatted table with headers |
| `progress cur total [label]` | `████░░` | Brand | Inline progress bar |

## Interactive Functions

| Function | Returns | Purpose |
|----------|---------|---------|
| `confirm "prompt" [timeout] [affirm] [neg]` | Sets `REPLY` | y/n prompt (backward-compatible) |
| `spin "title" command [args...]` | Exit code | Animated spinner wrapping a command |
| `choose "header" "opt1" "opt2" ...` | stdout | Interactive selection menu |
| `input "prompt" [placeholder] [--password]` | stdout | Styled text input |

## Pattern Mapping

| Old Pattern | New Pattern |
|-------------|-------------|
| `echo "Title"` + `echo "====="` | `header "Title" "Subtitle"` |
| `echo "✓ done"` | `success "done"` |
| `echo "Error: ..."` | `error "..."` |
| `echo "Warning: ..."` | `warn "..."` |
| `echo "  - Label: value"` | `list_item "Label" "value"` |
| `read -p "Continue? (y/n) "` | `confirm "Continue?"` |
| `echo "Section..."` between blocks | `section "Section"` |
| `echo "Note: ..."` | `note "..."` |
| Multi-line error block | `error_block "line1" "line2"` |
| `select opt in ...` / numbered menu | `choose "Pick one:" "A" "B" "C"` |
| `read -p "Name: "` | `input "Name:" "placeholder"` |
| Long command with no feedback | `spin "Installing..." brew install pkg` |
| Aligned columns / status tables | `table "Name,Status" "jq,installed"` |
| Counter loop with echo progress | `progress $i $total "Processing"` |

## Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `NO_COLOR` | unset | Disables all color output when set to any value |
| `STYLE_VERBOSE` | `1` | `0`=quiet (suppresses `step`/`dim`), `1`=default, `2`=verbose |
| `COLORTERM` | unset | Set to `truecolor` or `24bit` to enable RGB color palette |

## Rules

- ALWAYS source `style.sh` with fallback: `source "$SCRIPT_DIR/style.sh" 2>/dev/null || true`
- NEVER import gum directly in scripts — `style.sh` handles tool detection
- NEVER hard-code ANSI codes in scripts — use `style.sh` functions exclusively
- `confirm` function sets `REPLY` variable, compatible with existing `[[ $REPLY =~ ^[Yy]$ ]]` checks
- `spin` returns the wrapped command's exit code — use in conditionals: `if spin "Building..." make; then ...`
- `choose` and `input` return values via stdout — capture with: `result=$(choose "Pick:" "A" "B")`
- Do NOT wrap instant operations with `spin` — only use for commands that take noticeable time
- Interactive functions (`choose`, `input`, `confirm`) require a TTY — they read from `/dev/tty`
- Preserve all existing logic — only change output formatting, never behavior
- Scripts must work identically when `style.sh` is missing (plain echo fallback)
