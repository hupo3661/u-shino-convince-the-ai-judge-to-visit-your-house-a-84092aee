#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Ships the finished invitation image to the make.fun output folder.

The letter itself is rendered by ``render.py`` and stored beside this
file as ``entry.png``. This entry point is deliberately boring: it
sanity-checks those bytes as a PNG (whole file, at most 1 MiB, at most
1024 by 1024 pixels, per the competition gate), then copies them
verbatim to the destination folder, so repeated runs always deliver
the identical file. Nothing here talks to the network.
"""

import os
import struct
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_IMAGE = SCRIPT_DIR / "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The gate allows at most 1 MiB and 1024 by 1024 pixels; the size window
# below exists to catch a truncated, swapped or corrupt file before it
# gets copied anywhere.
SMALLEST_OK_BYTES = 10_000
LARGEST_OK_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
IHDR_LABEL_AT = slice(12, 16)
DIMENSIONS_AT = slice(16, 24)
HEADER_MIN_BYTES = 24


def resolve_destination():
    """Work out where the copy should land and make sure the folder exists.

    The ``MAKEFUN_OUTPUT_DIR`` environment variable wins when set;
    otherwise the copy goes to ``/output``.
    """
    requested = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    folder = Path(requested) if requested else Path("/output")
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "entry.png"


def fail(message):
    """Print a clear validation error and stop before anything is copied."""
    print(f"entry.png rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_ihdr_dimensions(data):
    """Return the (width, height) declared in the PNG IHDR chunk."""
    if len(data) < HEADER_MIN_BYTES or data[:8] != PNG_SIGNATURE:
        fail("not a whole PNG file (bad or truncated 8-byte signature/header)")
    if data[IHDR_LABEL_AT] != b"IHDR":
        fail("no IHDR chunk at the expected offset")
    width, height = struct.unpack(">II", data[DIMENSIONS_AT])
    if width <= 0 or height <= 0:
        fail(f"IHDR declares impossible dimensions {width}x{height}")
    return width, height


def ensure_png_structure(data):
    """Check the structural markers a complete PNG must carry."""
    if not data.endswith(b"IEND\xaeB`\x82"):
        fail("missing IEND trailer: file looks truncated")
    width, height = parse_ihdr_dimensions(data)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail(f"dimensions {width}x{height} exceed the {MAX_WIDTH}x{MAX_HEIGHT} gate")
    return width, height


def main():
    if not SOURCE_IMAGE.is_file():
        fail("entry.png is missing next to main.py")

    data = SOURCE_IMAGE.read_bytes()
    if len(data) < SMALLEST_OK_BYTES:
        fail(f"only {len(data)} bytes, far smaller than a real letter image")
    if len(data) > LARGEST_OK_BYTES:
        fail(f"{len(data)} bytes exceeds the 1 MiB gate")

    width, height = ensure_png_structure(data)

    destination = resolve_destination()
    destination.write_bytes(data)

    # Re-read and verify the copy is byte-for-byte identical.
    if destination.read_bytes() != data:
        fail("re-read copy does not match entry.png byte for byte")

    print(f"entry.png ({width}x{height}, {len(data)} bytes) -> {destination}")


if __name__ == "__main__":
    main()
