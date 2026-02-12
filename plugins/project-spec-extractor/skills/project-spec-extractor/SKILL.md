---
name: project-spec-extractor
description: Analyzes a codebase and generates a pure requirements specification (SPEC.md). Use when asked to "extract requirements", "create a spec", "generate a blueprint", or "distill this project".
license: MIT
compatibility: Any environment
argument-hint: "[--tech-agnostic] [path]"
disable-model-invocation: false
user-invocable: true
metadata:
  author: tsilva
  version: "1.0.0"
---

# Spec Extractor

Extract a pure requirements specification from a codebase — capturing *what* the project does without *how* it's built. The output SPEC.md serves as a portable blueprint: an agent can rebuild the project from scratch, resulting in simpler, cleaner code with the same features.

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| **Tech-preserving** (default) | *(none)* | Section 6 lists specific stack: languages, frameworks, databases, services by name |
| **Tech-agnostic** | `--tech-agnostic` | Section 6 describes abstract capabilities: "persistent relational storage", "server-side rendering framework" |

## Analysis Workflow

Execute these four phases sequentially. Read the directory tree first, then selectively read representative files — do NOT read every file.

### Phase 1: Project Identity

**Purpose:** Establish what the project IS.

**Read:** README, CLAUDE.md, package manifests (package.json, pyproject.toml, Cargo.toml, go.mod), .env.example, docker-compose.yml, config files.

**Extract:**
- Project name and one-line purpose
- Target users / audience
- Core value proposition

### Phase 2: Feature Discovery

**Purpose:** Discover what the project DOES.

**Read by project type:**
- **API/Web:** Routes, controllers, middleware, pages, components
- **CLI:** Command parsers, subcommands, argument definitions
- **Library:** Public API surface, exported functions/classes
- **Full-stack:** Both API and frontend layers

**Method:** Read directory tree first to understand structure, then read representative files from each functional area. Group features by user-facing domain, not code organization.

### Phase 3: Data & Integrations

**Purpose:** Map data entities and external dependencies.

**Read:** Schema/migration files, ORM models/entities, .env.example for third-party services, auth middleware, API client configurations.

**Extract:**
- Data entities and their relationships (not column-level schema)
- External services and their purpose (database, cache, email, payment, auth providers)
- Which integrations are required vs optional

### Phase 4: Behavioral Verification

**Purpose:** Confirm completeness by cross-referencing against tests.

**Read:** Test file names and descriptions (not test implementation), error types/messages, configuration keys.

**Verify:**
- Every test-described behavior appears in the feature list
- Error scenarios are reflected in acceptance criteria
- All configuration keys are documented

## SPEC.md Output Template

Write the specification using exactly these 9 sections. Scale the document to project complexity: ~1 page for a CLI tool, 3-5 pages for a full-stack app. Omit sections that don't apply (e.g., skip Non-Functional Requirements for simple projects).

```markdown
# SPEC.md — {Project Name}

## 1. Purpose

{1-3 sentences: what the project does, who it's for, why it exists.}

## 2. User-Facing Features

{Group by domain. Describe behaviors only — what users can do, not how it works internally.}

### {Domain Group}

- {Feature behavior description}
- {Feature behavior description}

## 3. User Flows

{Numbered steps from the user's perspective. Primary flows only — trust the rebuilding agent for edge cases.}

### {Flow Name}

1. {User action}
2. {System response}
3. {Next step}

## 4. Data Entities

| Entity | Description | Relationships |
|--------|-------------|---------------|
| {Name} | {What it represents} | {How it relates to other entities} |

## 5. External Integrations

| Service | Purpose | Required |
|---------|---------|----------|
| {Name} | {What it's used for} | Yes/No |

## 6. Technology Constraints

{Tech-preserving: list specific stack by name.}
{Tech-agnostic: describe abstract capabilities needed.}

## 7. Configuration & Environment

| Key | Purpose | Required |
|-----|---------|----------|
| {KEY_NAME} | {What it controls} | Yes/No |

## 8. Non-Functional Requirements

{Only include if relevant. Examples: performance targets, security requirements, accessibility standards.}

## 9. Acceptance Criteria

{Checkbox list of testable pass/fail behaviors. Every feature and integration should have at least one criterion.}

- [ ] {Testable behavior statement}
- [ ] {Testable behavior statement}
```

## Writing Rules

Follow these rules strictly when drafting SPEC.md:

1. **Describe behaviors, not mechanisms** — "Users can reset their password via email" not "The PasswordResetController sends a token using SendGrid"
2. **User-perspective language** — write from what a user sees and does, not what the code does internally
3. **No implementation names** — omit file names, class names, function names, database column names (except in Section 6 when using tech-preserving mode)
4. **Group by domain** — organize features by what they mean to users, not by how code is structured
5. **Scale to project size** — a CLI tool gets a concise 1-page spec; a full-stack app gets 3-5 pages
6. **High-level only** — capture requirements at a level where a competent agent can fill in the details during rebuild

## Self-Review Checklist

Before saving SPEC.md, verify every item:

- [ ] No implementation details leaked (no file names, class names, function names, library names outside Section 6)
- [ ] Every discovered feature from Phase 2 appears in the spec
- [ ] Acceptance criteria cover all features listed in Section 2
- [ ] Acceptance criteria cover all integrations listed in Section 5
- [ ] Section 6 matches selected mode (tech-preserving or tech-agnostic)
- [ ] Document length is proportional to project complexity

## Workflow

1. **Detect project type:**
   ```bash
   uv run shared/detect_project.py --path "$(pwd)"
   ```
2. **Parse arguments:** Check `$ARGUMENTS` for `--tech-agnostic` flag and optional path
3. **Execute analysis:** Run Phases 1-4 sequentially, reading directory tree first, then selective files
4. **Draft SPEC.md:** Follow the output template, applying writing rules
5. **Self-review:** Walk through the checklist above, fix any violations
6. **Write SPEC.md:** Save to the project root
