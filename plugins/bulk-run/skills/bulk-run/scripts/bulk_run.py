#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Bulk-run: Execute a Claude Code skill across multiple repositories in parallel.

Usage:
    uv run bulk_run.py run --skill <name> [--repos-dir <path>] [--filter <glob>] [--batch-size <n>]
    uv run bulk_run.py status
    uv run bulk_run.py resume
    uv run bulk_run.py --test
"""

import argparse
import fnmatch
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Import shared utilities from repository root
SHARED_DIR = Path(__file__).resolve().parents[5] / "shared"
sys.path.insert(0, str(SHARED_DIR))

from repo_utils import find_repos

PROGRESS_FILE = Path.home() / ".claude" / "bulk-run-progress.json"


def load_progress() -> dict | None:
    """Load progress file if it exists."""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return None


def save_progress(progress: dict) -> None:
    """Atomically save progress file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    progress["updated_at"] = datetime.now(timezone.utc).isoformat()
    tmp = PROGRESS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(progress, indent=2))
    tmp.rename(PROGRESS_FILE)


def run_skill_on_repo(skill: str, repo_path: Path, timeout: int = 300) -> dict:
    """Run a Claude skill on a single repo. Returns result dict."""
    start = time.monotonic()
    try:
        result = subprocess.run(
            ["claude", "-p", f"/{skill}"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = round(time.monotonic() - start, 1)
        if result.returncode == 0:
            return {"status": "success", "duration": duration}
        else:
            error = (result.stderr or result.stdout or "unknown error")[:500]
            return {"status": "failed", "duration": duration, "error": error}
    except subprocess.TimeoutExpired:
        duration = round(time.monotonic() - start, 1)
        return {"status": "failed", "duration": duration, "error": "timeout"}
    except FileNotFoundError:
        return {"status": "failed", "duration": 0, "error": "claude CLI not found"}


def cmd_run(args: argparse.Namespace) -> int:
    """Execute skill across repos."""
    repos_dir = Path(args.repos_dir).resolve()
    all_repos = find_repos(repos_dir)

    if not all_repos:
        print(f"No repositories found in {repos_dir}", file=sys.stderr)
        return 1

    # Apply filter
    if args.filter and args.filter != "*":
        repos = [r for r in all_repos if fnmatch.fnmatch(r.name, args.filter)]
    else:
        repos = all_repos

    if not repos:
        print(f"No repos matching filter '{args.filter}'", file=sys.stderr)
        return 1

    # Initialize progress
    progress = {
        "skill": args.skill,
        "repos_dir": str(repos_dir),
        "filter": args.filter or "*",
        "batch_size": args.batch_size,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "repos": {r.name: {"status": "pending"} for r in repos},
    }
    save_progress(progress)

    print(f"Running /{args.skill} on {len(repos)} repos (batch size: {args.batch_size})")
    print()

    return _execute_pending(progress, repos_dir, args.skill, args.batch_size)


def _execute_pending(progress: dict, repos_dir: Path, skill: str, batch_size: int) -> int:
    """Run skill on all pending repos in progress."""
    pending = [
        name
        for name, info in progress["repos"].items()
        if info["status"] == "pending"
    ]

    if not pending:
        print("No pending repos to process.")
        return 0

    succeeded = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        futures = {
            executor.submit(run_skill_on_repo, skill, repos_dir / name): name
            for name in pending
        }
        for future in as_completed(futures):
            name = futures[future]
            result = future.result()
            progress["repos"][name] = result
            save_progress(progress)

            status_icon = "+" if result["status"] == "success" else "x"
            line = f"  [{status_icon}] {name} ({result['duration']}s)"
            if result["status"] == "failed":
                line += f" - {result.get('error', '')[:80]}"
                failed += 1
            else:
                succeeded += 1
            print(line)

    total = succeeded + failed
    print()
    print(f"Done: {succeeded}/{total} succeeded, {failed}/{total} failed")
    return 0 if failed == 0 else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show progress of last run."""
    progress = load_progress()
    if not progress:
        print("No bulk-run progress found.", file=sys.stderr)
        return 1

    repos = progress["repos"]
    total = len(repos)
    by_status = {}
    for info in repos.values():
        s = info["status"]
        by_status[s] = by_status.get(s, 0) + 1

    print(f"Skill:      /{progress['skill']}")
    print(f"Repos dir:  {progress['repos_dir']}")
    print(f"Filter:     {progress['filter']}")
    print(f"Batch size: {progress['batch_size']}")
    print(f"Started:    {progress['started_at']}")
    print(f"Updated:    {progress['updated_at']}")
    print()
    print(f"Total: {total}")
    for s in ["success", "failed", "pending"]:
        if s in by_status:
            print(f"  {s}: {by_status[s]}")

    # Show failed repos
    failed = {name: info for name, info in repos.items() if info["status"] == "failed"}
    if failed:
        print()
        print("Failed repos:")
        for name, info in failed.items():
            print(f"  {name}: {info.get('error', 'unknown')[:80]}")

    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    """Resume interrupted run."""
    progress = load_progress()
    if not progress:
        print("No bulk-run progress found to resume.", file=sys.stderr)
        return 1

    pending = [n for n, i in progress["repos"].items() if i["status"] == "pending"]
    failed = [n for n, i in progress["repos"].items() if i["status"] == "failed"]

    # Reset failed to pending for retry
    for name in failed:
        progress["repos"][name] = {"status": "pending"}

    to_run = len(pending) + len(failed)
    if to_run == 0:
        print("All repos already completed. Nothing to resume.")
        return 0

    print(f"Resuming: {to_run} repos ({len(pending)} pending, {len(failed)} failed->retry)")
    save_progress(progress)

    repos_dir = Path(progress["repos_dir"])
    return _execute_pending(
        progress, repos_dir, progress["skill"], progress["batch_size"]
    )


def run_tests() -> bool:
    """Self-tests."""
    import tempfile

    all_passed = True

    # Test 1: find_repos with empty dir
    with tempfile.TemporaryDirectory() as tmpdir:
        repos = find_repos(Path(tmpdir))
        if repos != []:
            print(f"FAIL: Empty dir, got {repos}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Empty directory returns empty list")

    # Test 2: find_repos discovers repos
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        for name in ["repo-beta", "repo-alpha"]:
            (tmpdir / name).mkdir()
            (tmpdir / name / ".git").mkdir()
        (tmpdir / "not-a-repo").mkdir()

        repos = find_repos(tmpdir)
        names = [r.name for r in repos]
        if names != ["repo-alpha", "repo-beta"]:
            print(f"FAIL: Expected ['repo-alpha', 'repo-beta'], got {names}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Finds and sorts repos")

    # Test 3: find_repos with filter
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        for name in ["mcp-foo", "mcp-bar", "other"]:
            (tmpdir / name).mkdir()
            (tmpdir / name / ".git").mkdir()

        repos = find_repos(tmpdir)
        filtered = [r for r in repos if fnmatch.fnmatch(r.name, "mcp-*")]
        names = [r.name for r in filtered]
        if names != ["mcp-bar", "mcp-foo"]:
            print(f"FAIL: Filter, got {names}", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Glob filter works")

    # Test 4: Progress file save/load
    with tempfile.TemporaryDirectory() as tmpdir:
        global PROGRESS_FILE
        orig = PROGRESS_FILE
        PROGRESS_FILE = Path(tmpdir) / "progress.json"

        progress = {
            "skill": "test",
            "repos_dir": "/tmp",
            "filter": "*",
            "batch_size": 3,
            "started_at": "2026-01-01T00:00:00",
            "repos": {"a": {"status": "pending"}},
        }
        save_progress(progress)
        loaded = load_progress()
        if loaded is None or loaded["skill"] != "test":
            print("FAIL: Progress save/load", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Progress save/load")

        # Test 5: Atomic write (tmp file cleaned up)
        if PROGRESS_FILE.with_suffix(".tmp").exists():
            print("FAIL: tmp file not cleaned up", file=sys.stderr)
            all_passed = False
        else:
            print("PASS: Atomic write cleans up tmp")

        PROGRESS_FILE = orig

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Bulk-run Claude Code skills across repos")
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run", help="Run skill across repos")
    run_parser.add_argument("--skill", required=True, help="Skill name (without /)")
    run_parser.add_argument("--repos-dir", default=".", help="Directory containing repos")
    run_parser.add_argument("--filter", default="*", help="Glob pattern for repo names")
    run_parser.add_argument("--batch-size", type=int, default=3, help="Parallel workers")

    # status
    subparsers.add_parser("status", help="Show progress")

    # resume
    subparsers.add_parser("resume", help="Resume interrupted run")

    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if args.command == "run":
        sys.exit(cmd_run(args))
    elif args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "resume":
        sys.exit(cmd_resume(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
