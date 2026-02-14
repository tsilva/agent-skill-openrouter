---
name: code-simplifier
description: Scans a codebase for simplification opportunities and applies approved changes. Use when asked to simplify code, reduce complexity, or clean up a project.
license: MIT
user-invocable: true
disable-model-invocation: true
metadata:
  author: tsilva
  version: "1.1.0"
---

# Code Simplifier

Analyze an entire codebase for simplification opportunities, present findings for approval, then apply changes. Inspired by spartan programming principles — every line must justify its existence.

## Phase 1 — Analysis

### Scan

1. Build a file manifest of all source files in the project.
2. **Exclude:** tests, generated code, vendor/node_modules, configs (JSON/YAML/TOML), lock files, migrations, build output, `.min.*` files.
3. Read every source file. Map cross-file references: call sites, imports, exports, type usage.
4. Apply the five rule categories below to every file. Record each finding with: file path, line range, category, description, estimated lines removable.

### Rule Categories

#### 1. Dead Code Elimination
- Functions/methods never called or referenced anywhere in the codebase
- Imports not used in the file
- Variables assigned but never read
- Unreachable branches (`if false`, impossible type checks, post-return code)
- Commented-out code blocks (3+ lines)
- Dead feature flags (always on/off with no toggle path)
- Unused types, interfaces, enums

**Before marking dead:** Search the entire codebase including string literals (dynamic dispatch, reflection, serialization keys, route tables, CLI handlers). If a function name appears in strings or configs, flag it but do NOT auto-mark as dead.

#### 2. Flatten, Inline & Reduce Nesting
- **Guard clauses:** Invert top-level `if` blocks wrapping entire function bodies — test failure case, return early, dedent main logic
- **Nested conditionals:** Collapse into flat guard sequences
- **`else` after early exit:** Remove wrapping `else` after `return`/`continue`/`break`/`throw`, dedent remaining code
- **Loop nesting:** Use `continue`-on-mismatch to reduce loop body indentation; extract inner loops when nesting exceeds 2 levels
- **Callback/promise nesting:** Flatten into `async`/`await` sequences
- Trivial one-line helpers called from a single site — inline them
- Ternary or expression form where clearer than if/else block
- Wrapper functions that just forward arguments with no added logic
- Unnecessary intermediate variables used only once on the next line

**Nesting target:** After applying this category, no function should exceed 3 levels of indentation from its definition.

#### 3. DRY Consolidation
- Duplicated blocks (3+ lines, ≥2 occurrences) — extract shared function
- Near-duplicates differing only by a parameter — parameterize
- Copy-pasted logic across files — create shared utility
- Multiple functions doing the same thing with different names

**Auto-consolidation:** When extracting a shared function, determine the best location (same file, shared module, or utils), create it, then replace all call sites.

#### 4. Remove Unnecessary Abstractions
- Wrapper classes adding no logic beyond delegation
- Interfaces/traits with exactly one implementation (and no plugin/DI use)
- Factory functions that construct a single type
- Inheritance used solely for code sharing (not polymorphism)
- Over-parameterized generics used with one concrete type
- Single-link delegation chains (A calls B calls C, A could call C)
- Config/options objects wrapping 1-2 values — pass directly

#### 5. Legacy & Compatibility Code Removal
- `@deprecated` / `@obsolete` shims kept for backwards compatibility
- Version-checking code for versions below the project's minimum (e.g., `if sys.version_info < (3, 6)`)
- Polyfills for universally available features (e.g., `Array.prototype.flat`, `fetch`, `Promise`)
- Compatibility wrappers normalizing old platform APIs (vendor prefixes, etc.)
- Renamed-but-kept re-exports (`export { newName as oldName }`)
- Migration or schema-upgrade code that has already been applied
- TODO/FIXME comments referencing completed work or merged PRs
- Feature flags for permanently-enabled features
- `try`/`except ImportError` blocks for packages that are now hard dependencies

**Before removing:** Check the project's declared minimum version (e.g., `engines`, `python_requires`, `tsconfig.target`) before removing version-gated code. If no minimum is declared, flag for user confirmation rather than auto-removing.

## Phase 2 — Report

Present findings in this format:

```
## Simplification Report

**Summary:** {total_findings} findings across {file_count} files — ~{total_lines} lines removable

### 1. Dead Code Elimination ({count} findings, ~{lines} lines)

| # | File | Lines | Finding | Lines Removed |
|---|------|-------|---------|---------------|
| 1 | src/utils.ts | 42-58 | `formatLegacy()` never called | 17 |

### 2. Flatten, Inline & Reduce Nesting ({count} findings, ~{lines} lines)
...

### 3. DRY Consolidation ({count} findings, ~{lines} lines)
...

### 4. Remove Unnecessary Abstractions ({count} findings, ~{lines} lines)
...

### 5. Legacy & Compatibility Code Removal ({count} findings, ~{lines} lines)
...
```

After the table, ask:
```
Which changes should I apply? (all / none / comma-separated numbers, e.g. 1,3,5-8)
```

If zero findings: report "No simplification opportunities found." and stop.

## Phase 3 — Apply

1. Group approved changes by file.
2. Within each file, apply changes in **reverse line order** (highest line numbers first) to avoid offset drift.
3. For DRY extractions: create the shared function first, then replace all call sites.
4. For abstraction removal: update all dependents before removing the abstraction.
5. After all changes, report:

```
Done. {files_changed} files changed, {lines_removed} lines removed.
```

## Safety Rules

- **Never change observable behavior.** Inputs, outputs, side effects, error semantics must remain identical.
- **Never remove code with side effects** (logging, API calls, DB writes, event emissions) unless confirmed dead by call-graph analysis.
- **Never simplify error handling** into less specific forms (don't collapse distinct catch blocks, don't widen error types).
- **Flag but don't auto-remove** functions referenced in: route definitions, CLI command registrations, dependency injection containers, serialization annotations, decorator registries, or dynamic `getattr`/`eval`/`reflect` patterns.
- **Preserve public API surfaces.** Exported symbols from package entry points are not dead even if unused internally.
- When uncertain, **skip the finding** rather than risk a behavior change.
