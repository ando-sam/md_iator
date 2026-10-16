#!/usr/bin/env python3
"""Command-line entry point for md_iator."""

import argparse
import os
import sys
from pathlib import Path

import md_iator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="md_iator",
        description="Convertit des fichiers DOCX et PDF en Markdown.",
    )
    parser.add_argument("input", help="fichier ou dossier source")
    parser.add_argument(
        "-o", "--output",
        help="fichier .md de sortie (mode fichier unique) ou dossier de sortie (mode batch)",
        default=None,
    )
    args = parser.parse_args()

    src = Path(args.input)
    output = Path(args.output) if args.output else None

    if not src.exists():
        parser.error(f"chemin introuvable : {src}")

    # Path() drops the trailing separator, so "-o out/" must be created here
    # for convert_file to see a directory rather than a file name.
    if args.output and args.output.endswith(("/", os.sep)):
        output.mkdir(parents=True, exist_ok=True)

    md_iator.ensure_pandoc()

    if src.is_dir():
        ok, errors = md_iator.batch_convert(src, output)
        total = ok + errors
        print(f"\n{ok}/{total} fichiers convertis.")
        sys.exit(1 if errors else 0)
    else:
        try:
            dest = md_iator.convert_file(src, output)
            print(f"converted: {dest}")
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
