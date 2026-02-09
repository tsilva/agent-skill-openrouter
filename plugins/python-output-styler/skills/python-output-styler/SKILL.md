---
name: python-output-styler
description: |
  Applies gorgeous terminal styling to Python scripts using Rich with plain-text fallback.
  Use when creating or modifying Python scripts that produce user-facing terminal output.
  Use when asked to "style python output", "make python pretty", "add colors to python script", or "improve python terminal UX".
license: MIT
user-invocable: true
argument-hint: "[script-path]"
metadata:
  author: tsilva
  version: "1.0.0"
---

# Python Output Styling

Style all user-facing Python script output using the bundled `style.py` module.

## Workflow

1. Read [references/style.py](references/style.py) to understand available functions
2. If `style.py` doesn't exist alongside the target script, copy from [references/style.py](references/style.py) into the same directory
3. Import functions in the target script: `from style import header, success, error, info, section`
4. Replace raw `print()` statements with styled output function calls
5. Replace `input()` prompts with `styled_input`, `confirm`, or `choose` as appropriate
6. Wrap long-running iterables with `progress` for animated feedback
7. Wrap long-running functions with `spin` for animated spinner feedback
8. Verify script still works when Rich is not installed (graceful degradation to plain print)

## Dependency

Rich is the preferred rendering backend. Install via:

```bash
uv run --with rich script.py
```

When Rich is unavailable, all functions fall back to plain `print()` output automatically.

## Color Palette

| Name    | Hex       | Rich Markup        | Use                          |
|---------|-----------|--------------------|------------------------------|
| Brand   | `#AF87FF` | `[bold #AF87FF]`   | Headers, emphasis            |
| Success | `#87D787` | `[#87D787]`        | Checkmarks, completion       |
| Error   | `#FF5F5F` | `[#FF5F5F]`        | Errors, failures             |
| Warning | `#FFD75F` | `[#FFD75F]`        | Warnings, caution            |
| Info    | `#87CEEB` | `[#87CEEB]`        | Info messages, tips          |
| Muted   | `#808080` | `[#808080]`        | Paths, secondary text        |

## Output Functions

| Function | Symbol | Color | Purpose |
|----------|--------|-------|---------|
| `header(title, subtitle="")` | box | Brand | Bordered header panel |
| `section(text)` | `━━` | Brand | Horizontal rule divider |
| `success(text)` | `✓` | Success | Completed actions |
| `error(text)` | `✗` | Error | Error messages |
| `warn(text)` | `⚠` | Warning | Warnings |
| `info(text)` | `●` | Info | Informational |
| `step(text)` | `→` | Muted | Action log (suppressed when quiet) |
| `note(text)` | — | Muted | "Note:" prefixed |
| `banner(text)` | box | Success | Completion banner |
| `error_block(*lines)` | `│` | Error | Multi-line error box |
| `list_item(label, value)` | `•` | Brand+Muted | Key-value display |
| `dim(text)` | — | Muted | De-emphasized text (suppressed when quiet) |

## Utility Functions

| Function | Purpose |
|----------|---------|
| `table(headers, *rows)` | Formatted table with headers. `headers` is a list of strings, each `row` is a list of strings |
| `pretty(obj)` | Rich inspect for any Python object (falls back to `pprint`) |

## Progress Functions

| Function | Returns | Purpose |
|----------|---------|---------|
| `progress(iterable, label="")` | Wrapped iterable | Rich progress bar wrapping any iterable |
| `spin(title, func, *args, **kwargs)` | Function result | Animated spinner wrapping a function call |

## Interactive Functions

| Function | Returns | Purpose |
|----------|---------|---------|
| `confirm(prompt, default=True)` | `bool` | y/n prompt |
| `choose(header, *options)` | `str` | Numbered selection menu |
| `styled_input(prompt, password=False)` | `str` | Styled text input (avoids shadowing built-in `input`) |

## Pattern Mapping

| Old Pattern | New Pattern |
|-------------|-------------|
| `print("Title")` + `print("=====")` | `header("Title", "Subtitle")` |
| `print("✓ done")` | `success("done")` |
| `print("Error: ...")` | `error("...")` |
| `print("Warning: ...")` | `warn("...")` |
| `print("  - Label: value")` | `list_item("Label", "value")` |
| `input("Continue? (y/n) ")` | `confirm("Continue?")` |
| `print("Section...")` between blocks | `section("Section")` |
| `print("Note: ...")` | `note("...")` |
| Multi-line error block | `error_block("line1", "line2")` |
| Numbered menu with `input()` | `choose("Pick one:", "A", "B", "C")` |
| `input("Name: ")` | `styled_input("Name:")` |
| `getpass.getpass("Password: ")` | `styled_input("Password:", password=True)` |
| `for item in items: ...` (slow) | `for item in progress(items, "Processing"): ...` |
| Long function call with no feedback | `result = spin("Installing...", install_pkg, "name")` |
| `pprint(obj)` | `pretty(obj)` |

## Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `NO_COLOR` | unset | Disables all color output when set to any value |
| `STYLE_VERBOSE` | `1` | `0`=quiet (suppresses `step`/`dim`), `1`=default, `2`=verbose |

## Rules

- ALWAYS import from `style.py` — never use Rich directly in scripts
- NEVER hard-code ANSI codes in scripts — use `style.py` functions exclusively
- Use `styled_input` instead of `input` for styled prompts to avoid shadowing the built-in
- `confirm` returns a `bool` — use directly in `if confirm("Continue?"): ...`
- `spin` returns the wrapped function's return value — use: `result = spin("Building...", build_fn)`
- `choose` returns the selected option string — use: `choice = choose("Pick:", "A", "B")`
- `progress` wraps an iterable — use: `for item in progress(items, "Processing"): ...`
- Do NOT wrap instant operations with `spin` — only use for functions that take noticeable time
- Preserve all existing logic — only change output formatting, never behavior
- Scripts must work identically when Rich is not installed (plain print fallback)
