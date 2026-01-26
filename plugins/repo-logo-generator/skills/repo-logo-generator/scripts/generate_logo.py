#!/usr/bin/env python3
"""
Chromakey transparency conversion for logo images.

This script converts a chromakey background (green by default) to transparent
using professional-quality edge detection without "halo" artifacts.

Usage:
    uv run --with pillow generate_logo.py input.png --output logo.png

Dependencies: pillow
"""

import argparse
import io
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: pillow library required.", file=sys.stderr)
    print("Run with: uv run --with pillow generate_logo.py ...", file=sys.stderr)
    sys.exit(1)


def parse_hex_color(hex_color: str) -> tuple:
    """Parse hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def chromakey_to_transparent(img: Image.Image, key_color: tuple = (0, 255, 0),
                              tolerance: int = 70) -> Image.Image:
    """Convert chromakey background to transparent with smooth edges.

    Uses color distance in RGB space to calculate alpha. This is the same
    technique used in professional film/TV green screen compositing.

    Args:
        img: PIL Image to process
        key_color: RGB tuple of the key color (default: green #00FF00)
        tolerance: Base tolerance for key color detection (default: 70)

    Returns:
        PIL Image with transparency applied
    """
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    pixels = img.load()
    kr, kg, kb = key_color

    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            distance = math.sqrt((r - kr)**2 + (g - kg)**2 + (b - kb)**2)

            if distance < tolerance:
                pixels[x, y] = (r, g, b, 0)
            elif distance < tolerance * 3:
                alpha = int(255 * (distance - tolerance) / (tolerance * 2))
                pixels[x, y] = (r, g, b, min(255, alpha))

    return img


def compress_png(image_path: Path, quality: int = 80) -> tuple:
    """Compress PNG using pngquant if available."""
    import shutil
    import subprocess

    original_size = image_path.stat().st_size

    if not shutil.which("pngquant"):
        print("  pngquant not found, skipping compression", file=sys.stderr)
        return original_size, original_size

    quality_min = max(0, quality - 20)
    result = subprocess.run([
        "pngquant",
        "--quality", f"{quality_min}-{quality}",
        "--speed", "1",
        "--strip",
        "--force",
        "--output", str(image_path),
        str(image_path)
    ], capture_output=True)

    if result.returncode not in (0, 99):
        return original_size, original_size

    compressed_size = image_path.stat().st_size
    return original_size, compressed_size


def main():
    parser = argparse.ArgumentParser(
        description="Convert chromakey background to transparent"
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("--output", "-o", required=True, help="Output filename")
    parser.add_argument("--key-color", "-k", default="#00FF00",
                        help="Chromakey color in hex (default: #00FF00 green)")
    parser.add_argument("--tolerance", "-t", type=int, default=70,
                        help="Color tolerance for transparency (default: 70)")
    parser.add_argument("--no-compress", dest="compress", action="store_false",
                        help="Skip PNG compression")
    parser.add_argument("--compress-quality", type=int, default=80,
                        help="pngquant quality 1-100 (default: 80)")

    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        img = Image.open(input_path)
        print(f"Processing: {input_path}", file=sys.stderr)

        key_rgb = parse_hex_color(args.key_color)
        print(f"  Key color: {args.key_color} -> RGB{key_rgb}", file=sys.stderr)

        transparent_img = chromakey_to_transparent(img, key_color=key_rgb,
                                                    tolerance=args.tolerance)
        print("  Transparency conversion complete", file=sys.stderr)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        transparent_img.save(output_path, format='PNG')

        if args.compress:
            orig_size, comp_size = compress_png(output_path, args.compress_quality)
            if orig_size != comp_size:
                reduction = (1 - comp_size / orig_size) * 100
                print(f"  Compressed: {orig_size:,}B -> {comp_size:,}B ({reduction:.1f}%)", file=sys.stderr)

        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
