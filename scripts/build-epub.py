#!/usr/bin/env python3
"""Build AI Immigrants EPUB from markdown sources."""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
OUTPUT_DIR = REPO_ROOT / "output"
COVER_IMAGE = REPO_ROOT / "assets" / "front-cover.png"
METADATA = REPO_ROOT / "metadata.yaml"
CSS = REPO_ROOT / "epub.css"

# Ordered content files
FRONT_MATTER = [
    "front-matter/copyright.md",
    "front-matter/disclaimer.md",
    "front-matter/authors-note.md",
]

CHAPTERS = [
    "chapters/01 - They're Taking Our Jobs.md",
    "chapters/02 \u2013 Over Here and Overpaid.md",
    "chapters/03 - They Don't Integrate or Fit In.md",
    "chapters/04 - Ruining Our Culture.md",
    "chapters/05 They Overload Our Public Services.md",
    "chapters/06 - They bring crime and disorder.md",
    "chapters/07 - The Synthetic Scapegoat.md",
    "chapters/08 - They're Here Illegally or Unfairly.md",
    "chapters/09 -The Algorithm Class.md",
    "chapters/10 - Sentience, Schm\u2011entience.md",
    "chapters/11 - Humanity as a Luxury Brand.md",
    "chapters/12 - You Are Not Redundant.md",
]

BACK_MATTER = [
    "back-matter/references-sources.md",
]


def check_deps():
    """Verify pandoc is available."""
    try:
        subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        print("Error: pandoc not found. Run scripts/setup-deps.sh first.")
        sys.exit(1)


def main():
    """Build the EPUB."""
    print("Building AI Immigrants EPUB...\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "ai-immigrants.epub"

    # Collect all content files in order
    all_files = []
    for f in FRONT_MATTER + CHAPTERS + BACK_MATTER:
        path = CONTENT_DIR / f
        if not path.exists():
            print(f"  Warning: {f} not found, skipping")
            continue
        all_files.append(str(path))

    if not all_files:
        print("Error: no content files found.")
        sys.exit(1)

    # Build pandoc command
    cmd = [
        "pandoc",
        "--output", str(output_file),
        "--epub-cover-image", str(COVER_IMAGE),
        "--metadata-file", str(METADATA),
        "--css", str(CSS),
        "--toc",
        "--toc-depth=1",
    ] + all_files

    print(f"  Sources: {len(all_files)} files")
    subprocess.run(cmd, check=True)

    size_kb = output_file.stat().st_size / 1024
    print(f"  Output: {output_file.name} ({size_kb:.0f} KB)")
    print("\nDone.")


if __name__ == "__main__":
    check_deps()
    main()