#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
PII and credential scanner for repository files.

Detects sensitive data patterns while respecting .gitignore rules.
Returns JSON results for integration with audit workflows.

Usage:
    uv run shared/pii_scanner.py /path/to/repo
    uv run shared/pii_scanner.py /path/to/repo --json
    uv run shared/pii_scanner.py --test
"""

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

# Credential detection patterns
PATTERNS = {
    "aws_access_key": {
        "pattern": r"AKIA[0-9A-Z]{16}",
        "description": "AWS Access Key ID",
        "severity": "high",
    },
    "aws_secret_key": {
        "pattern": r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "description": "AWS Secret Access Key",
        "severity": "critical",
    },
    "github_token": {
        "pattern": r"gh[ps]_[A-Za-z0-9_]{36,}",
        "description": "GitHub Personal Access Token",
        "severity": "critical",
    },
    "github_oauth": {
        "pattern": r"gho_[A-Za-z0-9_]{36,}",
        "description": "GitHub OAuth Token",
        "severity": "critical",
    },
    "private_key": {
        "pattern": r"-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----",
        "description": "Private Key",
        "severity": "critical",
    },
    "generic_password": {
        "pattern": r"(?i)(?:password|passwd|pwd)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
        "description": "Hardcoded Password",
        "severity": "high",
    },
    "generic_secret": {
        "pattern": r"(?i)(?:secret|api_key|apikey|access_token)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
        "description": "Hardcoded Secret/API Key",
        "severity": "high",
    },
    "database_url": {
        "pattern": r"(?i)(?:postgres|mysql|mongodb|redis)://[^:]+:[^@]+@[^\s]+",
        "description": "Database URL with Credentials",
        "severity": "critical",
    },
    "slack_webhook": {
        "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
        "description": "Slack Webhook URL",
        "severity": "high",
    },
    "stripe_key": {
        "pattern": r"sk_(?:live|test)_[A-Za-z0-9]{24,}",
        "description": "Stripe Secret Key",
        "severity": "critical",
    },
    "jwt_token": {
        "pattern": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "description": "JWT Token",
        "severity": "medium",
    },
}

# File extensions to skip (binary, media, etc.)
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".pyc", ".pyo", ".so", ".dll", ".exe",
    ".woff", ".woff2", ".ttf", ".eot",
    ".lock", ".sum",
}

# Directories to always skip
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    "env", ".tox", ".pytest_cache", ".mypy_cache",
    "dist", "build", ".eggs", "*.egg-info",
}


def parse_gitignore(repo_path: Path) -> list[str]:
    """Parse .gitignore file and return list of patterns."""
    gitignore_path = repo_path / ".gitignore"
    patterns = []

    if gitignore_path.exists():
        try:
            content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    patterns.append(line)
        except Exception:
            pass

    return patterns


def is_ignored(file_path: Path, repo_path: Path, gitignore_patterns: list[str]) -> bool:
    """Check if file matches any gitignore pattern."""
    rel_path = str(file_path.relative_to(repo_path))

    for pattern in gitignore_patterns:
        # Handle directory patterns
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            if fnmatch.fnmatch(rel_path, f"{dir_pattern}/*") or fnmatch.fnmatch(rel_path, f"*/{dir_pattern}/*"):
                return True
        # Handle file patterns
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_path.name, pattern):
            return True
        # Handle **/ patterns
        if pattern.startswith("**/"):
            if fnmatch.fnmatch(rel_path, pattern[3:]) or fnmatch.fnmatch(file_path.name, pattern[3:]):
                return True

    return False


def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped based on extension or name."""
    if file_path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if file_path.name.startswith("."):
        return True
    return False


def should_skip_dir(dir_name: str) -> bool:
    """Check if directory should be skipped."""
    for pattern in SKIP_DIRS:
        if fnmatch.fnmatch(dir_name, pattern):
            return True
    return False


def scan_file(file_path: Path) -> list[dict]:
    """Scan a single file for credential patterns."""
    findings = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    lines = content.splitlines()

    for pattern_name, pattern_info in PATTERNS.items():
        regex = re.compile(pattern_info["pattern"])

        for line_num, line in enumerate(lines, 1):
            matches = regex.finditer(line)
            for match in matches:
                findings.append({
                    "pattern": pattern_name,
                    "description": pattern_info["description"],
                    "severity": pattern_info["severity"],
                    "line": line_num,
                    "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                })

    return findings


def scan_repo(repo_path: Path, respect_gitignore: bool = True) -> dict:
    """
    Scan entire repository for credentials.

    Args:
        repo_path: Path to repository root
        respect_gitignore: If True, skip files matching .gitignore patterns

    Returns:
        Dict with findings per file
    """
    repo_path = Path(repo_path).resolve()

    if not repo_path.exists():
        return {"error": f"Path does not exist: {repo_path}"}

    gitignore_patterns = parse_gitignore(repo_path) if respect_gitignore else []

    results = {
        "repo": str(repo_path),
        "files_scanned": 0,
        "files_with_findings": 0,
        "total_findings": 0,
        "findings": {},
        "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
    }

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip based on directory
        if any(should_skip_dir(part) for part in file_path.relative_to(repo_path).parts):
            continue

        # Skip based on file type
        if should_skip_file(file_path):
            continue

        # Skip if gitignored
        if respect_gitignore and is_ignored(file_path, repo_path, gitignore_patterns):
            continue

        results["files_scanned"] += 1

        file_findings = scan_file(file_path)
        if file_findings:
            rel_path = str(file_path.relative_to(repo_path))
            results["findings"][rel_path] = file_findings
            results["files_with_findings"] += 1
            results["total_findings"] += len(file_findings)

            for finding in file_findings:
                results["by_severity"][finding["severity"]] += 1

    return results


def run_tests() -> bool:
    """Self-test the PII scanning logic."""
    import tempfile

    all_passed = True

    # Test 1: Detect AWS access key
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".git").mkdir()  # Make it look like a repo
        test_file = tmpdir / "config.py"
        test_file.write_text('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')

        results = scan_repo(tmpdir)
        if results["total_findings"] != 1:
            print(f"FAIL: AWS key detection - expected 1 finding, got {results['total_findings']}", file=sys.stderr)
            all_passed = False
        elif results["by_severity"]["high"] != 1:
            print(f"FAIL: AWS key should be high severity", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Detect AWS access key")

    # Test 2: Detect GitHub token
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".git").mkdir()
        test_file = tmpdir / "script.sh"
        test_file.write_text('export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"')

        results = scan_repo(tmpdir)
        if results["total_findings"] != 1:
            print(f"FAIL: GitHub token detection - expected 1 finding, got {results['total_findings']}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Detect GitHub token")

    # Test 3: Skip gitignored files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".git").mkdir()
        gitignore = tmpdir / ".gitignore"
        gitignore.write_text("*.secret")
        secret_file = tmpdir / "creds.secret"
        secret_file.write_text('PASSWORD = "supersecretpassword123"')

        results = scan_repo(tmpdir, respect_gitignore=True)
        if results["total_findings"] != 0:
            print(f"FAIL: Should skip gitignored files - got {results['total_findings']} findings", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Skip gitignored files")

    # Test 4: Clean repo returns no findings
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".git").mkdir()
        clean_file = tmpdir / "main.py"
        clean_file.write_text('print("Hello, world!")')

        results = scan_repo(tmpdir)
        if results["total_findings"] != 0:
            print(f"FAIL: Clean repo should have 0 findings - got {results['total_findings']}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Clean repo returns no findings")

    # Test 5: Non-existent path returns error
    results = scan_repo(Path("/nonexistent/path"))
    if "error" not in results:
        print("FAIL: Non-existent path should return error", file=sys.stderr)
        all_passed = False
    else:
        print("PASS: Non-existent path returns error")

    # Test 6: Detect private key
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / ".git").mkdir()
        key_file = tmpdir / "id_rsa"
        key_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----")

        results = scan_repo(tmpdir)
        if results["total_findings"] != 1:
            print(f"FAIL: Private key detection - expected 1 finding, got {results['total_findings']}", file=sys.stderr)
            all_passed = False
        elif results["by_severity"]["critical"] != 1:
            print(f"FAIL: Private key should be critical severity", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Detect private key")

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Scan repository for credentials and sensitive data"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        type=Path,
        help="Path to repository to scan",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Don't respect .gitignore patterns",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-tests",
    )

    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if not args.repo_path:
        print("Usage: pii_scanner.py <repo_path>", file=sys.stderr)
        print("       pii_scanner.py --test", file=sys.stderr)
        sys.exit(1)

    results = scan_repo(args.repo_path, respect_gitignore=not args.no_gitignore)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if "error" in results:
            print(f"Error: {results['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"Repository: {results['repo']}")
        print(f"Files scanned: {results['files_scanned']}")
        print(f"Files with findings: {results['files_with_findings']}")
        print(f"Total findings: {results['total_findings']}")
        print()

        if results["total_findings"] > 0:
            print("Findings by severity:")
            for severity in ["critical", "high", "medium", "low"]:
                count = results["by_severity"][severity]
                if count > 0:
                    print(f"  {severity.upper()}: {count}")
            print()

            print("Details:")
            for file_path, findings in results["findings"].items():
                print(f"\n  {file_path}:")
                for f in findings:
                    print(f"    Line {f['line']}: {f['description']} ({f['severity']})")

    # Exit with error code if critical findings
    if results.get("by_severity", {}).get("critical", 0) > 0:
        sys.exit(2)
    elif results.get("total_findings", 0) > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
