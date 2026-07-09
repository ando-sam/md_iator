#!/usr/bin/env python3
"""Convert DOCX and PDF files to Markdown using pypandoc and pdfplumber."""

import argparse
import sys
from pathlib import Path

import pdfplumber
import pypandoc

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}


def _ensure_pandoc() -> None:
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("pandoc introuvable — téléchargement en cours...", flush=True)
        pypandoc.download_pandoc(delete_installer=True)
        print("pandoc installé.")


def convert_docx(src: Path, dest: Path) -> None:
    pypandoc.convert_file(str(src), "markdown", outputfile=str(dest))


def convert_pdf(src: Path, dest: Path) -> None:
    with pdfplumber.open(src) as pdf:
        pages = []
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"## Page {i}\n\n{text.strip()}")
    dest.write_text("\n\n---\n\n".join(pages), encoding="utf-8")


def convert_file(src: Path, output: Path | None = None) -> Path:
    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"format non supporté : {ext}")

    if output is None:
        dest = src.with_suffix(".md")
    elif output.is_dir():
        dest = output / src.with_suffix(".md").name
    else:
        dest = output

    dest.parent.mkdir(parents=True, exist_ok=True)

    if ext == ".docx":
        convert_docx(src, dest)
    elif ext == ".pdf":
        convert_pdf(src, dest)

    return dest


def batch_convert(folder: Path, output_dir: Path | None = None) -> tuple[int, int]:
    files = [
        p for ext in SUPPORTED_EXTENSIONS for p in folder.rglob(f"*{ext}")
    ]
    ok, errors = 0, 0
    for src in sorted(files):
        if output_dir is not None:
            rel = src.relative_to(folder)
            dest = output_dir / rel.with_suffix(".md")
        else:
            dest = None
        try:
            result = convert_file(src, dest)
            print(f"  converted: {result}")
            ok += 1
        except Exception as exc:
            print(f"  error: {src} — {exc}", file=sys.stderr)
            errors += 1
    return ok, errors


def main() -> None:
    _ensure_pandoc()
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

    if src.is_dir():
        ok, errors = batch_convert(src, output)
        total = ok + errors
        print(f"\n{ok}/{total} fichiers convertis.")
        sys.exit(1 if errors else 0)
    else:
        try:
            dest = convert_file(src, output)
            print(f"converted: {dest}")
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
