"""Tests for shared/extract_tagline.py"""
from pathlib import Path

from extract_tagline import extract_tagline, strip_yaml_frontmatter, is_skip_line


def test_simple_tagline(temp_dir):
    """Extracts simple tagline after header."""
    readme = temp_dir / "README.md"
    readme.write_text("# My Project\n\nA simple utility for testing things.")
    assert extract_tagline(readme) == "A simple utility for testing things."


def test_tagline_with_bold(temp_dir):
    """Strips bold formatting from tagline."""
    readme = temp_dir / "README.md"
    readme.write_text("# My Project\n\n**A bold tagline for emphasis**")
    assert extract_tagline(readme) == "A bold tagline for emphasis"


def test_skip_badges_and_html(temp_dir):
    """Skips badges and HTML, extracts real tagline."""
    readme = temp_dir / "README.md"
    readme.write_text("""# Project
<div align="center">

![Badge](https://img.shields.io/badge)

</div>

The real tagline is here.
""")
    assert extract_tagline(readme) == "The real tagline is here."


def test_yaml_frontmatter_stripping(temp_dir):
    """Strips YAML frontmatter before extracting tagline."""
    readme = temp_dir / "README.md"
    readme.write_text("""---
title: Test
---

# Project

This is the tagline after frontmatter.
""")
    assert extract_tagline(readme) == "This is the tagline after frontmatter."


def test_non_existent_file():
    """Returns None for non-existent file."""
    assert extract_tagline(Path("/nonexistent/README.md")) is None


def test_truncation_for_long_taglines(temp_dir):
    """Truncates taglines over 350 characters."""
    readme = temp_dir / "README.md"
    long_text = "A " + "very " * 100 + "long tagline."
    readme.write_text(f"# Project\n\n{long_text}")

    tagline = extract_tagline(readme)
    assert tagline is not None
    assert len(tagline) <= 350
    assert tagline.endswith("...")


def test_skip_short_lines(temp_dir):
    """Skips lines that are too short to be taglines."""
    readme = temp_dir / "README.md"
    readme.write_text("# Project\n\nHi\n\nThis is a proper tagline for the project.")
    assert extract_tagline(readme) == "This is a proper tagline for the project."


def test_strip_yaml_frontmatter_present():
    """Strips YAML frontmatter when present."""
    content = """---
title: Test
---

Content here."""
    result = strip_yaml_frontmatter(content)
    assert "---" not in result
    assert "Content here." in result


def test_strip_yaml_frontmatter_absent():
    """Returns content unchanged when no frontmatter."""
    content = "# Title\n\nContent"
    assert strip_yaml_frontmatter(content) == content


def test_is_skip_line_empty():
    """Empty lines should be skipped."""
    assert is_skip_line("") is True
    assert is_skip_line("   ") is True


def test_is_skip_line_header():
    """Headers should be skipped."""
    assert is_skip_line("# Title") is True
    assert is_skip_line("## Subtitle") is True


def test_is_skip_line_badge():
    """Badge images should be skipped."""
    assert is_skip_line("![Badge](https://example.com)") is True


def test_is_skip_line_html():
    """HTML tags should be skipped."""
    assert is_skip_line("<div>") is True
    assert is_skip_line("</div>") is True


def test_is_skip_line_valid_text():
    """Valid text lines should not be skipped."""
    assert is_skip_line("A proper tagline for the project.") is False
