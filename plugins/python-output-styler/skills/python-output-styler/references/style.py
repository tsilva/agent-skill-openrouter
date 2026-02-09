#!/usr/bin/env python3
"""
style.py - Python output styling module

Import this module in Python scripts for gorgeous terminal output.
Uses Rich for panels, tables, spinners, and interactive widgets.
Falls back to plain print() when Rich is unavailable.

Usage:
    from style import header, success, error, info, section, progress, spin

Dependency:
    uv run --with rich script.py
"""

import os
import sys
import threading

# ---------------------------------------------------------------------------
# Environment detection
# ---------------------------------------------------------------------------

_NO_COLOR = bool(os.environ.get("NO_COLOR"))
_IS_TTY = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
_HAS_COLOR = _IS_TTY and not _NO_COLOR
_VERBOSITY = int(os.environ.get("STYLE_VERBOSE", "1"))

try:
    _COLS = os.get_terminal_size().columns
except (OSError, ValueError):
    _COLS = 60

# ---------------------------------------------------------------------------
# Rich detection
# ---------------------------------------------------------------------------

_HAS_RICH = False
_console = None

try:
    if _HAS_COLOR:
        from rich.console import Console
        from rich.panel import Panel
        from rich.rule import Rule
        from rich.table import Table
        from rich.text import Text
        from rich.progress import track
        import rich.inspect

        _HAS_RICH = True
        _console = Console(highlight=False)
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Color constants (plain-text fallback)
# ---------------------------------------------------------------------------

if _HAS_COLOR and not _HAS_RICH:
    _C_BRAND = "\033[38;5;141m"     # #AF87FF
    _C_SUCCESS = "\033[38;5;114m"   # #87D787
    _C_ERROR = "\033[38;5;203m"     # #FF5F5F
    _C_WARN = "\033[38;5;221m"      # #FFD75F
    _C_INFO = "\033[38;5;117m"      # #87CEEB
    _C_MUTED = "\033[38;5;244m"     # #808080
    _C_BOLD = "\033[1m"
    _C_RESET = "\033[0m"
else:
    _C_BRAND = _C_SUCCESS = _C_ERROR = _C_WARN = ""
    _C_INFO = _C_MUTED = _C_BOLD = _C_RESET = ""


# ---------------------------------------------------------------------------
# Output functions
# ---------------------------------------------------------------------------

def header(title, subtitle=""):
    """Bordered header panel with brand color."""
    full = f"{title}  {subtitle}" if subtitle else title
    if _HAS_RICH:
        _console.print()
        _console.print(Panel(
            f"[bold #AF87FF]{full}[/]",
            border_style="#AF87FF",
            expand=False,
            padding=(0, 2),
        ))
        _console.print()
    else:
        line = "\u2501" * (len(full) + 4)
        print()
        print(f"{_C_BRAND}\u250f{line}\u2513{_C_RESET}")
        print(f"{_C_BRAND}\u2503{_C_RESET}  {_C_BRAND}{_C_BOLD}{full}{_C_RESET}  {_C_BRAND}\u2503{_C_RESET}")
        print(f"{_C_BRAND}\u2517{line}\u251b{_C_RESET}")
        print()


def section(text):
    """Horizontal rule section divider."""
    if _HAS_RICH:
        _console.print()
        _console.print(Rule(title=text, style="#AF87FF bold"))
        _console.print()
    else:
        prefix = f"\u2501\u2501 {text} "
        trail_len = max(4, _COLS - len(prefix))
        trail = "\u2501" * trail_len
        print()
        print(f"{_C_BRAND}{_C_BOLD}{prefix}{trail}{_C_RESET}")
        print()


def success(text):
    """Checkmark with green text."""
    if _HAS_RICH:
        _console.print(f"  [#87D787]\u2713[/] [#87D787]{text}[/]")
    else:
        print(f"  {_C_SUCCESS}\u2713{_C_RESET} {_C_SUCCESS}{text}{_C_RESET}")


def error(text):
    """Cross with red text."""
    if _HAS_RICH:
        _console.print(f"  [#FF5F5F]\u2717[/] [#FF5F5F]{text}[/]")
    else:
        print(f"  {_C_ERROR}\u2717{_C_RESET} {_C_ERROR}{text}{_C_RESET}")


def warn(text):
    """Warning symbol with amber text."""
    if _HAS_RICH:
        _console.print(f"  [#FFD75F]\u26a0[/] [#FFD75F]{text}[/]")
    else:
        print(f"  {_C_WARN}\u26a0{_C_RESET} {_C_WARN}{text}{_C_RESET}")


def info(text):
    """Bullet with blue text."""
    if _HAS_RICH:
        _console.print(f"  [#87CEEB]\u25cf[/] [#87CEEB]{text}[/]")
    else:
        print(f"  {_C_INFO}\u25cf{_C_RESET} {_C_INFO}{text}{_C_RESET}")


def step(text):
    """Arrow with muted text. Suppressed in quiet mode."""
    if _VERBOSITY == 0:
        return
    if _HAS_RICH:
        _console.print(f"  [#808080]\u2192 {text}[/]")
    else:
        print(f"  {_C_MUTED}\u2192 {text}{_C_RESET}")


def note(text):
    """Gray 'Note:' prefixed text."""
    if _HAS_RICH:
        _console.print(f"  [#808080]Note: {text}[/]")
    else:
        print(f"  {_C_MUTED}Note: {text}{_C_RESET}")


def banner(text):
    """Bordered completion message in green."""
    if _HAS_RICH:
        _console.print()
        _console.print(Panel(
            f"[bold #87D787]{text}[/]",
            border_style="#87D787",
            expand=False,
            padding=(0, 2),
        ))
        _console.print()
    else:
        line = "\u2501" * (len(text) + 4)
        print()
        print(f"{_C_SUCCESS}\u250f{line}\u2513{_C_RESET}")
        print(f"{_C_SUCCESS}\u2503{_C_RESET}  {_C_SUCCESS}{_C_BOLD}{text}{_C_RESET}  {_C_SUCCESS}\u2503{_C_RESET}")
        print(f"{_C_SUCCESS}\u2517{line}\u251b{_C_RESET}")
        print()


def error_block(*lines):
    """Multi-line error box with red border."""
    if _HAS_RICH:
        content = "\n".join(lines)
        _console.print()
        _console.print(Panel(
            f"[#FF5F5F]{content}[/]",
            border_style="#FF5F5F",
            expand=False,
            padding=(0, 1),
        ))
        _console.print()
    else:
        print()
        for line in lines:
            print(f"  {_C_ERROR}\u2502{_C_RESET} {_C_ERROR}{line}{_C_RESET}")
        print()


def list_item(label, value):
    """Colored label: value pair."""
    if _HAS_RICH:
        _console.print(f"  [#AF87FF]\u2022[/] [bold #AF87FF]{label}:[/] [#808080]{value}[/]")
    else:
        print(f"  {_C_BRAND}\u2022{_C_RESET} {_C_BRAND}{_C_BOLD}{label}:{_C_RESET} {_C_MUTED}{value}{_C_RESET}")


def dim(text):
    """De-emphasized muted text. Suppressed in quiet mode."""
    if _VERBOSITY == 0:
        return
    if _HAS_RICH:
        _console.print(f"  [#808080]{text}[/]")
    else:
        print(f"  {_C_MUTED}{text}{_C_RESET}")


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def table(headers, *rows):
    """Formatted table with headers.

    Args:
        headers: List of column header strings.
        *rows: Each row is a list of cell strings.
    """
    if _HAS_RICH:
        t = Table(show_header=True, header_style="bold #AF87FF", border_style="#808080")
        for h in headers:
            t.add_column(h)
        for row in rows:
            t.add_row(*[str(c) for c in row])
        _console.print(t)
    else:
        # Plain-text table with aligned columns
        all_rows = [headers] + list(rows)
        col_widths = []
        for row in all_rows:
            for i, cell in enumerate(row):
                w = len(str(cell))
                if i >= len(col_widths):
                    col_widths.append(w)
                elif w > col_widths[i]:
                    col_widths[i] = w

        def _fmt_row(row, style_start="", style_end=""):
            cells = []
            for i, cell in enumerate(row):
                w = col_widths[i] if i < len(col_widths) else len(str(cell))
                cells.append(f"{style_start}{str(cell).ljust(w)}{style_end}")
            return "  " + " \u2502 ".join(cells)

        print(_fmt_row(headers, _C_BRAND + _C_BOLD, _C_RESET))
        sep = "  " + "\u2500\u253c\u2500".join("\u2500" * w for w in col_widths)
        print(f"{_C_MUTED}{sep}{_C_RESET}")
        for row in rows:
            print(_fmt_row(row, _C_MUTED, _C_RESET))


def pretty(obj):
    """Rich inspect for any Python object. Falls back to pprint."""
    if _HAS_RICH:
        rich.inspect.inspect(obj)
    else:
        import pprint
        pprint.pprint(obj)


# ---------------------------------------------------------------------------
# Progress functions
# ---------------------------------------------------------------------------

def progress(iterable, label=""):
    """Wrap an iterable with a Rich progress bar.

    Args:
        iterable: Any iterable (list, range, generator with __len__).
        label: Description shown next to the bar.

    Returns:
        Wrapped iterable that displays progress.
    """
    if _HAS_RICH:
        return track(iterable, description=f"  {label}" if label else "  Processing...")
    else:
        return iterable


def spin(title, func, *args, **kwargs):
    """Animated spinner wrapping a function call.

    Args:
        title: Text shown next to the spinner.
        func: Callable to execute.
        *args, **kwargs: Passed to func.

    Returns:
        The return value of func(*args, **kwargs).

    Raises:
        Any exception raised by func.
    """
    if _HAS_RICH:
        result = None
        exc = None
        def _run():
            nonlocal result, exc
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                exc = e
        with _console.status(f"  {title}", spinner="dots"):
            t = threading.Thread(target=_run)
            t.start()
            t.join()
        if exc is not None:
            raise exc
        return result
    else:
        if _HAS_COLOR:
            sys.stderr.write(f"  {_C_INFO}\u2192{_C_RESET} {title}...")
            sys.stderr.flush()
        try:
            result = func(*args, **kwargs)
        except Exception:
            if _HAS_COLOR:
                sys.stderr.write(f"\r  {_C_ERROR}\u2717{_C_RESET} {title}   \n")
            raise
        if _HAS_COLOR:
            sys.stderr.write(f"\r  {_C_SUCCESS}\u2713{_C_RESET} {title}   \n")
        return result


# ---------------------------------------------------------------------------
# Interactive functions
# ---------------------------------------------------------------------------

def confirm(prompt, default=True):
    """Yes/no prompt.

    Args:
        prompt: Question text.
        default: Default when user presses Enter (True=yes, False=no).

    Returns:
        bool
    """
    suffix = "(Y/n)" if default else "(y/N)"
    if _HAS_RICH:
        _console.print(f"  [#AF87FF]\u25b8[/] {prompt} [#808080]{suffix}[/] ", end="")
    else:
        sys.stdout.write(f"  {_C_BRAND}\u25b8{_C_RESET} {prompt} {_C_MUTED}{suffix}{_C_RESET} ")
        sys.stdout.flush()
    try:
        answer = builtins_input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    if not answer:
        return default
    return answer.startswith("y")


def choose(header_text, *options):
    """Numbered selection menu.

    Args:
        header_text: Menu title.
        *options: Choices to display.

    Returns:
        The selected option string.
    """
    if _HAS_RICH:
        _console.print(f"  [bold #AF87FF]{header_text}[/]")
        for i, opt in enumerate(options, 1):
            _console.print(f"  [#808080]{i})[/] {opt}")
    else:
        print(f"  {_C_BRAND}{_C_BOLD}{header_text}{_C_RESET}")
        for i, opt in enumerate(options, 1):
            print(f"  {_C_MUTED}{i}){_C_RESET} {opt}")

    total = len(options)
    while True:
        if _HAS_RICH:
            _console.print(f"  [#AF87FF]\u25b8[/] [#808080][1-{total}]:[/] ", end="")
        else:
            sys.stdout.write(f"  {_C_BRAND}\u25b8{_C_RESET} {_C_MUTED}[1-{total}]:{_C_RESET} ")
            sys.stdout.flush()
        try:
            raw = builtins_input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return options[0] if options else ""
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= total:
                return options[idx - 1]
        if _HAS_RICH:
            _console.print("  [#FF5F5F]Invalid choice[/]")
        else:
            print(f"  {_C_ERROR}Invalid choice{_C_RESET}")


def styled_input(prompt, password=False):
    """Styled text input (avoids shadowing built-in input).

    Args:
        prompt: Prompt text.
        password: Mask input if True.

    Returns:
        str
    """
    if _HAS_RICH:
        _console.print(f"  [#AF87FF]\u25b8[/] {prompt} ", end="")
    else:
        sys.stdout.write(f"  {_C_BRAND}\u25b8{_C_RESET} {prompt} ")
        sys.stdout.flush()
    if password:
        import getpass
        return getpass.getpass("")
    try:
        return builtins_input()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


# Keep a reference to the real built-in input
builtins_input = input


# ---------------------------------------------------------------------------
# Demo / self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    header("Python Output Styler", "v1.0.0 Demo")

    section("Output Functions")
    success("Operation completed successfully")
    error("Something went wrong")
    warn("Disk space running low")
    info("Server running on port 8080")
    step("Loading configuration...")
    note("This is an informational note")
    list_item("Version", "1.0.0")
    list_item("Author", "tsilva")
    dim("De-emphasized secondary text")

    section("Error Block")
    error_block(
        "Failed to connect to database",
        "Host: localhost:5432",
        "Reason: Connection refused",
    )

    section("Banner")
    banner("All checks passed!")

    section("Table")
    table(
        ["Name", "Status", "Version"],
        ["rich", "installed", "13.x"],
        ["gum", "n/a", "-"],
        ["python", "installed", "3.12"],
    )

    section("Pretty Inspect")
    pretty({"key": "value", "nested": [1, 2, 3]})

    section("Progress")
    import time
    for _ in progress(range(20), "Processing items"):
        time.sleep(0.05)

    section("Spinner")
    result = spin("Simulating work", time.sleep, 1.0)

    banner("Demo complete!")
