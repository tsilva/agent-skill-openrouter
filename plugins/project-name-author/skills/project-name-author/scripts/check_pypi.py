#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# ///
"""
Check PyPI package name availability.

Queries the PyPI JSON API to determine if package names are available.
Applies PEP 503 normalization (lowercase, replace _/./- with -).

Usage:
    uv run scripts/check_pypi.py name1 name2 name3
    uv run scripts/check_pypi.py --json name1 name2 name3
    uv run scripts/check_pypi.py --test

Output (default):
    name1: Available on PyPI
    name2: Taken on PyPI

Output (--json):
    {"name1": {"available": true, "normalized": "name1", "status": "available"}, ...}
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple


def normalize_name(name: str) -> str:
    """
    Normalize package name per PEP 503.

    - Lowercase
    - Replace runs of [-_.] with single hyphen
    """
    return re.sub(r"[-_.]+", "-", name.lower())


def check_pypi_availability(name: str, timeout: float = 5.0) -> Dict:
    """
    Check if a package name is available on PyPI.

    Args:
        name: The package name to check
        timeout: Request timeout in seconds

    Returns:
        Dict with keys: available, normalized, status, error (optional)
    """
    normalized = normalize_name(name)
    url = f"https://pypi.org/pypi/{normalized}/json"

    result = {
        "available": False,
        "normalized": normalized,
        "status": "unknown",
    }

    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "check-pypi/1.0 (claude-skills)")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # 200 = package exists = taken
            result["available"] = False
            result["status"] = "taken"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # 404 = not found = available
            result["available"] = True
            result["status"] = "available"
        else:
            result["status"] = "error"
            result["error"] = f"HTTP {e.code}"
    except urllib.error.URLError as e:
        result["status"] = "error"
        result["error"] = str(e.reason)
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def check_multiple(names: List[str], timeout: float = 5.0) -> Dict[str, Dict]:
    """
    Check multiple package names in parallel.

    Args:
        names: List of package names to check
        timeout: Request timeout per check

    Returns:
        Dict mapping original names to their availability results
    """
    results = {}

    with ThreadPoolExecutor(max_workers=min(len(names), 10)) as executor:
        futures = {
            executor.submit(check_pypi_availability, name, timeout): name
            for name in names
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = {
                    "available": False,
                    "normalized": normalize_name(name),
                    "status": "error",
                    "error": str(e),
                }

    return results


def run_tests() -> bool:
    """Self-test with normalization and live API checks."""
    all_passed = True

    # Test PEP 503 normalization
    print("Testing PEP 503 normalization...")
    normalization_tests = [
        ("My_Package", "my-package"),
        ("some.package", "some-package"),
        ("UPPER-case", "upper-case"),
        ("multiple---dashes", "multiple-dashes"),
        ("mixed_.-chars", "mixed-chars"),
        ("simple", "simple"),
    ]

    for input_name, expected in normalization_tests:
        result = normalize_name(input_name)
        if result == expected:
            print(f"  PASS: {input_name!r} -> {result!r}")
        else:
            print(f"  FAIL: {input_name!r} -> expected {expected!r}, got {result!r}")
            all_passed = False

    # Test live API - known taken package
    print("\nTesting live API (known taken package: 'requests')...")
    result = check_pypi_availability("requests")
    if result["status"] == "taken" and not result["available"]:
        print(f"  PASS: 'requests' is taken")
    else:
        print(f"  FAIL: 'requests' should be taken, got {result}")
        all_passed = False

    # Test live API - likely available (random gibberish)
    print("\nTesting live API (likely available: 'zzz-nonexistent-pkg-12345')...")
    result = check_pypi_availability("zzz-nonexistent-pkg-12345")
    if result["status"] == "available" and result["available"]:
        print(f"  PASS: random name is available")
    elif result["status"] == "error":
        print(f"  WARN: Could not check (network error: {result.get('error', 'unknown')})")
    else:
        print(f"  FAIL: random name should be available, got {result}")
        all_passed = False

    # Test parallel checking
    print("\nTesting parallel checking...")
    names = ["requests", "flask", "zzz-fake-name-99999"]
    results = check_multiple(names)
    if len(results) == 3:
        print(f"  PASS: checked {len(results)} packages in parallel")
        for name, res in results.items():
            status = res["status"]
            print(f"    {name}: {status}")
    else:
        print(f"  FAIL: expected 3 results, got {len(results)}")
        all_passed = False

    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Check PyPI package name availability"
    )
    parser.add_argument(
        "names",
        nargs="*",
        help="Package names to check"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-tests"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Request timeout in seconds (default: 5)"
    )

    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if not args.names:
        parser.error("At least one package name is required (or use --test)")

    results = check_multiple(args.names, timeout=args.timeout)

    if args.json:
        # Output in input order
        ordered = {name: results[name] for name in args.names}
        print(json.dumps(ordered, indent=2))
    else:
        # Human-readable output in input order
        for name in args.names:
            res = results[name]
            if res["status"] == "available":
                print(f"{name}: Available on PyPI")
            elif res["status"] == "taken":
                print(f"{name}: Taken on PyPI")
            else:
                error = res.get("error", "unknown error")
                print(f"{name}: Error ({error})")


if __name__ == "__main__":
    main()
