#!/usr/bin/env python3
"""Pre-commit hook to enforce a maximum line count per Python module.

This hook fails if any provided Python file exceeds the configured maximum
number of lines. It prints actionable guidance for splitting large modules
into smaller files within the same package.

Usage (pre-commit passes filenames automatically):
  python-module-length --max-lines 1000 <files...>

Exit codes:
  0 - All files within limit or no files provided
  1 - One or more files exceed the limit
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments.

    Args:
        argv: Optional iterable of CLI args (primarily for testing).

    Returns:
        Parsed arguments with attributes: max_lines (int) and files (list[str]).
    """
    parser = argparse.ArgumentParser(
        description=(
            "Fail if any Python module exceeds the configured maximum line count."
        )
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=1000,
        help="Maximum allowed lines per module (default: 1000)",
    )
    parser.add_argument("files", nargs="*", help="Python files to check")
    return parser.parse_args(list(argv) if argv is not None else None)


def count_lines(path: Path) -> int:
    """Return the number of lines in a text file using utf-8 with replacement.

    Args:
        path: The path to the file.

    Returns:
        The count of newline-terminated lines in the file.
    """
    # Use errors="replace" to be robust to odd encodings in legacy files.
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def find_violations(files: List[str], max_lines: int) -> List[Tuple[Path, int]]:
    """Find Python files exceeding the line limit.

    Args:
        files: Iterable of file paths to check.
        max_lines: Maximum allowed number of lines.

    Returns:
        A list of (path, line_count) for files that exceed the limit.
    """
    violations: List[Tuple[Path, int]] = []
    for name in files:
        p = Path(name)
        # Only consider real files that exist; pre-commit may pass deleted files.
        if not p.exists() or not p.is_file():
            continue
        if p.suffix.lower() != ".py":
            continue
        lines = count_lines(p)
        if lines > max_lines:
            violations.append((p, lines))
    return violations


def _is_test_file(path: Path) -> bool:
    """Return True if the path is within a tests directory.

    Works across platforms by inspecting path components.
    """
    parts = {p.lower() for p in path.parts}
    return "tests" in parts


def _print_section(header: str, items: List[Tuple[Path, int]]) -> None:
    """Print a simple section with file list.

    Args:
        header: Section header to print.
        items: List of (path, line_count) to display.
    """
    if not items:
        return
    print(header)
    for p, n in items:
        print(f"- {p} ({n} lines)")


def print_error(violations: List[Tuple[Path, int]], max_lines: int) -> None:
    """Print a clear, actionable error message for violations.

    Args:
        violations: List of (path, line_count) that exceeded the limit.
        max_lines: The configured maximum line count.
    """
    test_violations = [(p, n) for p, n in violations if _is_test_file(p)]
    app_violations = [(p, n) for p, n in violations if not _is_test_file(p)]

    print("Python module length check failed:\n")

    _print_section(
        header=f"Test files exceeding the {max_lines}-line limit:",
        items=test_violations,
    )
    if test_violations and app_violations:
        print("")
    _print_section(
        header=f"Application modules exceeding the {max_lines}-line limit:",
        items=app_violations,
    )

    # Guidance
    if test_violations:
        print("\nSuggestions (tests):")
        print("- Split by feature/scenario into multiple files.")
        print("- Extract common setup into fixtures (conftest.py).")
        print("- Prefer parametrization where appropriate.")

    if app_violations:
        print("\nSuggestions (application modules):")
        print("- Split into focused submodules within the same package.")
        print("- Preserve public API via re-exports in __init__.py if needed.")
        print("- Isolate shared types/constants to avoid import cycles.")

    print("\nOnce refactored, re-run pre-commit or commit again.")


def main(argv: List[str] | None = None) -> int:
    """Entrypoint for the length check.

    Args:
        argv: Optional CLI args (primarily for testing).

    Returns:
        Process exit code (0 on success, 1 on failure).
    """
    args = parse_args(argv)
    violations = find_violations(args.files, args.max_lines)
    if not violations:
        return 0
    print_error(violations, args.max_lines)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
