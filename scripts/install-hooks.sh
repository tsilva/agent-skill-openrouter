#!/bin/bash
#
# Install git hooks for the claude-skills repository
#
# Usage: ./scripts/install-hooks.sh
#
# Creates a symlink from .git/hooks/pre-commit to hooks/pre-commit
# This allows the hook source to be tracked in the repository.
#

set -e

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Not inside a git repository."
    exit 1
fi

cd "$REPO_ROOT"

# Ensure hooks directory exists
if [ ! -d "hooks" ]; then
    echo "Error: hooks/ directory not found."
    exit 1
fi

# Ensure .git/hooks exists
mkdir -p .git/hooks

# Install pre-commit hook
HOOK_SOURCE="../../hooks/pre-commit"
HOOK_TARGET=".git/hooks/pre-commit"

if [ -L "$HOOK_TARGET" ]; then
    echo "Removing existing symlink: $HOOK_TARGET"
    rm "$HOOK_TARGET"
elif [ -f "$HOOK_TARGET" ]; then
    echo "Warning: Existing hook file found at $HOOK_TARGET"
    echo "Backing up to $HOOK_TARGET.bak"
    mv "$HOOK_TARGET" "$HOOK_TARGET.bak"
fi

# Create symlink (relative path for portability)
ln -s "$HOOK_SOURCE" "$HOOK_TARGET"

echo "Installed git hooks:"
echo "  pre-commit -> hooks/pre-commit"
echo ""
echo "Hook installed successfully!"
echo "SKILL.md changes will now auto-bump version numbers on commit."
