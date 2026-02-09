#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""
Trim transparent padding from PNG images.

Detects the bounding box of non-transparent content, adds a configurable
margin, crops, and resizes back to original dimensions using Lanczos
resampling. This maximizes canvas utilization for logo images.

Usage:
    uv run scripts/trim_transparent.py --input logo.png --output logo.png --margin 5
"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: pillow library required.", file=sys.stderr)
    print("Run with: uv run --with pillow scripts/trim_transparent.py", file=sys.stderr)
    sys.exit(1)


def trim_transparent(input_path: str, output_path: str, margin: int = 5) -> dict:
    """Trim transparent padding from a PNG image.

    Args:
        input_path: Absolute path to input PNG.
        output_path: Absolute path to save trimmed PNG (can be same as input).
        margin: Margin as percentage (0-25) of the larger dimension.

    Returns:
        Dict with trimming results.
    """
    img = Image.open(input_path).convert("RGBA")
    original_width, original_height = img.size

    alpha = img.split()[3]
    bbox = alpha.getbbox()

    if bbox is None:
        # Fully transparent image — copy unchanged
        if input_path != output_path:
            shutil.copy2(input_path, output_path)
        return {
            "trimmed": False,
            "reason": "fully_transparent",
            "original_size": [original_width, original_height],
        }

    # Calculate content ratio before trimming
    content_width = bbox[2] - bbox[0]
    content_height = bbox[3] - bbox[1]
    content_ratio = round(
        (content_width * content_height) / (original_width * original_height), 3
    )

    # Expand bbox by margin percentage of the larger dimension
    larger_dim = max(original_width, original_height)
    margin_px = int(larger_dim * margin / 100)

    expanded_bbox = (
        max(0, bbox[0] - margin_px),
        max(0, bbox[1] - margin_px),
        min(original_width, bbox[2] + margin_px),
        min(original_height, bbox[3] + margin_px),
    )

    # Crop and resize back to original dimensions
    cropped = img.crop(expanded_bbox)
    resized = cropped.resize((original_width, original_height), Image.LANCZOS)

    # Save — use temp file if overwriting in place
    if input_path == output_path:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        resized.save(tmp_path, "PNG")
        shutil.move(tmp_path, output_path)
    else:
        resized.save(output_path, "PNG")

    return {
        "trimmed": True,
        "original_bbox": list(bbox),
        "expanded_bbox": list(expanded_bbox),
        "content_ratio": content_ratio,
        "original_size": [original_width, original_height],
    }


def run_tests() -> bool:
    """Self-test mode."""
    passed = 0
    failed = 0

    # Test 1: Trim image with padding
    print("Test 1: Trim image with transparent padding...")
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    # Draw a small icon in the center (50x50 in 200x200 canvas)
    for x in range(75, 125):
        for y in range(75, 125):
            img.putpixel((x, y), (255, 0, 0, 255))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        input_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        output_path = f.name

    img.save(input_path, "PNG")
    result = trim_transparent(input_path, output_path, margin=5)

    assert result["trimmed"] is True, f"Expected trimmed=True, got {result['trimmed']}"
    assert result["original_bbox"] == [75, 75, 125, 125], f"Wrong bbox: {result['original_bbox']}"
    assert result["content_ratio"] < 0.1, f"Content ratio should be small: {result['content_ratio']}"

    # Verify output image exists and has correct dimensions
    out_img = Image.open(output_path)
    assert out_img.size == (200, 200), f"Output should maintain original size: {out_img.size}"

    # Verify the icon now fills more of the canvas
    out_alpha = out_img.convert("RGBA").split()[3]
    out_bbox = out_alpha.getbbox()
    out_content_width = out_bbox[2] - out_bbox[0]
    assert out_content_width > 150, f"Icon should fill more canvas after trim: width={out_content_width}"

    Path(input_path).unlink()
    Path(output_path).unlink()
    print(f"  PASS (content_ratio={result['content_ratio']}, output icon width={out_content_width})")
    passed += 1

    # Test 2: Fully transparent image
    print("Test 2: Fully transparent image (no-op)...")
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        input_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        output_path = f.name

    img.save(input_path, "PNG")
    result = trim_transparent(input_path, output_path, margin=5)

    assert result["trimmed"] is False, f"Expected trimmed=False, got {result['trimmed']}"
    assert result["reason"] == "fully_transparent"

    Path(input_path).unlink()
    Path(output_path).unlink()
    print("  PASS")
    passed += 1

    # Test 3: In-place overwrite
    print("Test 3: In-place overwrite...")
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(80, 120):
        for y in range(80, 120):
            img.putpixel((x, y), (0, 0, 255, 255))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        inplace_path = f.name

    img.save(inplace_path, "PNG")
    result = trim_transparent(inplace_path, inplace_path, margin=5)

    assert result["trimmed"] is True
    out_img = Image.open(inplace_path)
    assert out_img.size == (200, 200)

    Path(inplace_path).unlink()
    print("  PASS")
    passed += 1

    # Test 4: Zero margin
    print("Test 4: Zero margin trim...")
    img = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(50, 150):
        for y in range(50, 150):
            img.putpixel((x, y), (0, 255, 0, 255))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        input_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        output_path = f.name

    img.save(input_path, "PNG")
    result = trim_transparent(input_path, output_path, margin=0)

    assert result["trimmed"] is True
    assert result["expanded_bbox"] == [50, 50, 150, 150], f"Zero margin should match content bbox: {result['expanded_bbox']}"

    Path(input_path).unlink()
    Path(output_path).unlink()
    print("  PASS")
    passed += 1

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trim transparent padding from PNG images"
    )
    parser.add_argument("--input", required=False, help="Input PNG path (absolute)")
    parser.add_argument("--output", required=False, help="Output PNG path (absolute)")
    parser.add_argument(
        "--margin",
        type=int,
        default=5,
        help="Margin percentage 0-25 (default: 5)",
    )
    parser.add_argument("--test", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    if args.test:
        return 0 if run_tests() else 1

    if not args.input or not args.output:
        parser.error("--input and --output are required (unless --test)")

    if not 0 <= args.margin <= 25:
        print("Error: --margin must be between 0 and 25", file=sys.stderr)
        return 1

    result = trim_transparent(args.input, args.output, args.margin)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
