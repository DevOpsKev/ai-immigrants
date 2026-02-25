#!/usr/bin/env python3
"""
AI Immigrants PDF Build Script

Assembles front matter, chapters, and back matter into a single markdown
file with raw LaTeX injections for structural control, then passes it
to pandoc + XeLaTeX.

Usage:
  python scripts/build-pdf.py [--git-hash HASH] [--build-date DATE] [--variant screen|print|both]

Output:
  output/ai-immigrants.pdf        (screen: RGB, cover, clickable links)
  output/ai-immigrants-print.pdf  (print: no cover, black links)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

# === CONFIGURATION ===

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
METADATA_FILE = REPO_ROOT / "metadata.yaml"
TEMPLATE_FILE = REPO_ROOT / "build" / "pdf" / "template.tex"
COVER_IMAGE = REPO_ROOT / "assets" / "front-cover-pdf.png"
OUTPUT_DIR = REPO_ROOT / "output"
BOOK_TITLE = "ai-immigrants"

# Fonts — TeX Gyre ships with texlive-fonts-recommended
MAIN_FONT = "TeX Gyre Pagella"      # Palatino — elegant prose serif
SANS_FONT = "TeX Gyre Heros"        # Helvetica — clean headings
FONT_SIZE = "10.5pt"

# Ordered content files (relative to CONTENT_DIR)
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
    """Verify pandoc and xelatex are available."""
    for cmd, pkg in [("pandoc", "pandoc"), ("xelatex", "texlive-xetex")]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
        except FileNotFoundError:
            print(f"Error: {cmd} not found. Install {pkg}.")
            sys.exit(1)


def raw_latex(code: str) -> str:
    """Wrap LaTeX code in a pandoc raw block."""
    return f"\n```{{=latex}}\n{code}\n```\n"


def preprocess_front_matter(content: str) -> str:
    """Prepare front matter markdown for PDF.

    - Strip pandoc div wrappers (::: {.class} ... :::)
    - Mark headings as unnumbered and unlisted (keep out of TOC)
    """
    # Strip div wrappers
    content = re.sub(r'^:::\s*\{[^}]*\}\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^:::\s*$', '', content, flags=re.MULTILINE)

    # Add {.unnumbered .unlisted} to # headings
    content = re.sub(
        r'^(#+\s+.+?)(\s*\{[^}]*\})?\s*$',
        r'\1 {.unnumbered .unlisted}',
        content,
        flags=re.MULTILINE,
    )

    return content.strip()


def preprocess_back_matter(content: str) -> str:
    """Prepare back matter markdown for PDF.

    - Mark top-level heading as unnumbered (but keep in TOC)
    """
    content = re.sub(
        r'^(#\s+.+?)(\s*\{[^}]*\})?\s*$',
        r'\1 {.unnumbered}',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    return content.strip()


def read_file(relative_path: str) -> str | None:
    """Read a content file, returning None if missing."""
    path = CONTENT_DIR / relative_path
    if not path.exists():
        print(f"  Warning: {relative_path} not found, skipping")
        return None
    return path.read_text(encoding="utf-8")


def assemble_markdown() -> str:
    """Assemble all content into a single markdown string.

    Structure:
      [front matter — unnumbered, not in TOC]
      \\tableofcontents
      \\mainmatter
      [chapters]
      \\backmatter
      [references]
    """
    sections: list[str] = []

    # --- Front matter ---
    print("  Front matter:")
    for f in FRONT_MATTER:
        content = read_file(f)
        if content is None:
            continue
        processed = preprocess_front_matter(content)

        # Copyright page: small text, pushed to bottom
        if "copyright" in f.lower():
            processed = (
                raw_latex(
                    "\\thispagestyle{empty}\n"
                    "\\vspace*{\\fill}\n"
                    "\\begingroup\\small\\setlength{\\parskip}{4pt}"
                )
                + "\n\n"
                + processed
                + "\n\n"
                + raw_latex("\\endgroup\\cleardoublepage")
            )

        sections.append(processed)
        print(f"    [ok] {f}")

    # --- TOC + mainmatter switch ---
    sections.append(raw_latex("\\tableofcontents\n\\mainmatter"))

    # --- Chapters ---
    print("  Chapters:")
    for f in CHAPTERS:
        content = read_file(f)
        if content is None:
            continue
        sections.append(content.strip())
        print(f"    [ok] {f}")

    # --- Back matter ---
    print("  Back matter:")
    sections.append(raw_latex("\\backmatter"))
    for f in BACK_MATTER:
        content = read_file(f)
        if content is None:
            continue
        sections.append(preprocess_back_matter(content))
        print(f"    [ok] {f}")

    return "\n\n".join(sections)


def build_pdf(variant: str, git_hash: str | None, build_date: str | None):
    """Build a single PDF variant."""
    is_print = variant == "print"
    suffix = "-print" if is_print else ""
    output_file = OUTPUT_DIR / f"{BOOK_TITLE}{suffix}.pdf"

    print(f"\n{'='*60}")
    print(f"  Building: {output_file.name} ({variant})")
    print(f"{'='*60}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Assemble content
    print("Scanning content...")
    assembled = assemble_markdown()

    if not assembled.strip():
        print("ERROR: No content found.")
        sys.exit(1)

    # Write assembled markdown for pandoc (and debugging)
    assembled_path = OUTPUT_DIR / "assembled.md"
    assembled_path.write_text(assembled, encoding="utf-8")
    print(f"\nAssembled markdown: {assembled_path}")
    print(f"Length: {len(assembled)} chars, {assembled.count(chr(10))} lines")

    # Build pandoc command
    cmd = [
        "pandoc",
        str(assembled_path),
        "--pdf-engine=xelatex",
        "--top-level-division=chapter",
        "-o",
        str(output_file),
    ]

    if TEMPLATE_FILE.exists():
        cmd.append(f"--template={TEMPLATE_FILE}")
    if METADATA_FILE.exists():
        cmd.append(f"--metadata-file={METADATA_FILE}")

    # Fonts
    cmd.extend(
        [
            f"--variable=mainfont:{MAIN_FONT}",
            f"--variable=sansfont:{SANS_FONT}",
            f"--variable=fontsize:{FONT_SIZE}",
        ]
    )

    # Variant-specific options
    if is_print:
        cmd.append("--variable=print:true")
    else:
        if COVER_IMAGE.exists():
            cmd.extend(
                [
                    "--variable=include-cover:true",
                    f"--variable=cover-image:{COVER_IMAGE}",
                ]
            )

    # Build info
    if git_hash:
        cmd.append(f"--variable=git-hash:{git_hash}")
    if build_date:
        cmd.append(f"--variable=build-date:{build_date}")

    print(f"\nPandoc command:\n  {' '.join(cmd)}\n")
    print("Running pandoc + xelatex...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR:\n{result.stderr}")
        print(f"\nDEBUG: Check {assembled_path} for the assembled markdown")
        sys.exit(1)

    size_kb = output_file.stat().st_size / 1024
    print(f"Done: {output_file} ({size_kb:.1f} KB)")

    # Clean up assembled file on success
    assembled_path.unlink(missing_ok=True)

    return output_file


def main():
    parser = argparse.ArgumentParser(description="Build AI Immigrants PDFs")
    parser.add_argument("--git-hash", help="Short git commit hash")
    parser.add_argument("--build-date", help="Build date (YYYY-MM-DD)")
    parser.add_argument(
        "--variant",
        choices=["screen", "print", "both"],
        default="both",
        help="Which variant(s) to build (default: both)",
    )
    args = parser.parse_args()

    variants = ["screen", "print"] if args.variant == "both" else [args.variant]
    for v in variants:
        build_pdf(v, args.git_hash, args.build_date)

    print(f"\n{'='*60}")
    print("  All builds complete.")
    print(f"{'='*60}")


if __name__ == "__main__":
    check_deps()
    main()
