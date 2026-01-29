---
name: bulk-run
description: Run any Claude Code skill across multiple repos in parallel batches with progress tracking and resume. Use when asked to run a skill on multiple repos, bulk execute, or batch process repositories.
argument-hint: "<skill-name> [--filter <pattern>] [--batch-size <n>] [--repos-dir <path>]"
license: MIT
metadata:
  author: tsilva
  version: "1.0.0"
---

# Bulk Run

Run a Claude Code skill across all repos in a directory with parallel execution, progress tracking, and resume.

## Operations

| Operation | Triggers | Purpose |
|-----------|----------|---------|
| `run` | `/<skill>`, skill name as first arg | Execute skill across repos |
| `status` | "status" | Show progress of last/current run |
| `resume` | "resume" | Resume interrupted run |

## Run Operation

Execute the bulk run script:

```bash
uv run {SKILL_DIR}/scripts/bulk_run.py run \
  --skill "<skill-name>" \
  --repos-dir "<path>" \
  --filter "<glob-pattern>" \
  --batch-size <n>
```

**Defaults:**
- `--repos-dir`: current working directory
- `--filter`: `*` (all repos)
- `--batch-size`: `3`

**Example:**
```bash
uv run {SKILL_DIR}/scripts/bulk_run.py run --skill "readme-author" --repos-dir "$(pwd)" --filter "mcp-*" --batch-size 4
```

Present output to user: per-repo status lines as they complete, then final summary.

## Status Operation

```bash
uv run {SKILL_DIR}/scripts/bulk_run.py status
```

Shows last run progress from `~/.claude/bulk-run-progress.json`.

## Resume Operation

```bash
uv run {SKILL_DIR}/scripts/bulk_run.py resume
```

Reads progress file, skips completed repos, re-runs pending/failed.

## Notes

- The script spawns `claude -p "/<skill>"` subprocesses per repo
- Requires `dangerouslyDisableSandbox: true` (spawns subprocesses)
- Progress persisted to `~/.claude/bulk-run-progress.json` after each repo

## Usage Examples

```
/bulk-run /readme-author                          # All repos in CWD
/bulk-run /readme-author --filter "mcp-*"         # Filtered
/bulk-run /readme-author --batch-size 4           # Concurrency control
/bulk-run status                                  # Check progress
/bulk-run resume                                  # Resume interrupted run
```
