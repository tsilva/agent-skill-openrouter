---
name: todo-aggregator
description: Scans repos directory, collects TODO/TODO.md files, generates consolidated markdown report to stdout.
argument-hint: "[aggregate|list] --repos-dir <path>"
license: MIT
metadata:
  author: tsilva
  version: "1.0.0"
---

# TODO Aggregator

Scan a repos directory, collect TODO and TODO.md files from each repo root, and generate a consolidated markdown report.

## Operations

| Operation | Triggers | Purpose |
|-----------|----------|---------|
| `aggregate` | Default, "aggregate", no keyword | Scan and generate consolidated markdown to stdout |
| `list` | "list" keyword | Show which repos have TODO files (names only) |

### Operation Detection

Use the deterministic operation selector:

```bash
uv run shared/select_operation.py --skill todo-aggregator --args "$ARGUMENTS" --check-files ""
```

**Fallback rules:**
1. Check `$ARGUMENTS` for explicit operation keyword (`list`)
2. If no keyword → `aggregate`

## Aggregate Workflow

Run the aggregation script:

```bash
uv run scripts/aggregate_todos.py --repos-dir /path/to/repos
```

Optional arguments:
- `--output <path>` - Write to file instead of stdout
- `--config <path>` - Custom config path (default: `{repos-dir}/.todo-aggregator.json`)

### Output Format

```markdown
# Aggregated TODOs

> Generated: 2026-01-28

## repo-name-1

- [ ] Incomplete task
- [x] Completed task

## repo-name-2

- [ ] Different task
```

## List Workflow

Show repos that have TODO files:

```bash
uv run scripts/aggregate_todos.py --repos-dir /path/to/repos --operation list
```

Output:
```
Repos with TODO files:
- repo-name-1 (TODO.md)
- repo-name-2 (TODO)
```

## Config File

Location: `{repos-dir}/.todo-aggregator.json`

```json
{
  "include": ["repo-a", "repo-b"],
  "exclude": ["archived-*", "temp-*"]
}
```

**Filter behavior:**
- If `include` is set, ONLY those repos are scanned
- `exclude` patterns are applied after include (glob patterns supported)
- If neither set, all repos with TODO/TODO.md are included

## Task Parsing

The script recognizes these task formats:
- `- [ ] Incomplete task` - Standard unchecked checkbox
- `- [x] Completed task` - Standard checked checkbox
- `- Task without checkbox` - Plain bullet (treated as incomplete)

All tasks are included in output, preserving their completion state.

## Usage Examples

```
/todo-aggregator                           # Aggregate TODOs from current directory
/todo-aggregator --repos-dir ~/repos       # Aggregate from specific repos folder
/todo-aggregator list                      # List repos with TODO files
/todo-aggregator list --repos-dir ~/repos  # List from specific folder
```
