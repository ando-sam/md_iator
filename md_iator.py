"""Convert DOCX and PDF files to Markdown using pypandoc and pdfplumber."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
import pypandoc
from tqdm import tqdm

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}


class EmptyDocumentError(Exception):
    """No text could be extracted, so no Markdown file is written."""


@dataclass
class Summary:
    converted: int = 0
    empty: int = 0
    skipped: int = 0
    errors: int = 0

    @property
    def processed(self) -> int:
        return self.converted + self.empty + self.skipped + self.errors


class BatchInterrupted(KeyboardInterrupt):
    """Ctrl-C during a batch, carrying what was done before it."""

    def __init__(self, summary: Summary, total: int):
        super().__init__()
        self.summary = summary
        self.total = total


def ensure_pandoc() -> None:
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
        has_text = False
        for i, page in enumerate(
            tqdm(pdf.pages, desc=src.name, unit="page", leave=False), start=1
        ):
            text = (page.extract_text() or "").strip()
            has_text = has_text or bool(text)
            pages.append(f"## Page {i}\n\n{text}")
    if not has_text:
        raise EmptyDocumentError(
            "aucun texte extrait (PDF scanné ? passer par ocrmypdf)"
        )
    dest.write_text("\n\n---\n\n".join(pages), encoding="utf-8")


def output_path(src: Path, output: Path | None = None) -> Path:
    if output is None:
        return src.with_suffix(".md")
    if output.is_dir():
        return output / src.with_suffix(".md").name
    return output


def convert_file(src: Path, output: Path | None = None) -> Path:
    ext = src.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"format non supporté : {ext}")

    dest = output_path(src, output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Convert into a temporary sibling, then rename: a failed or interrupted
    # conversion never leaves a truncated .md nor clobbers the previous one.
    tmp = dest.with_name(f".{dest.name}.{os.getpid()}.tmp")
    try:
        if ext == ".docx":
            convert_docx(src, tmp)
        elif ext == ".pdf":
            convert_pdf(src, tmp)
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)

    return dest


def batch_convert(
    folder: Path, output_dir: Path | None = None, skip_existing: bool = False
) -> Summary:
    # Extension matched case-insensitively; "~$" files are Word lock files.
    files = [
        p for p in folder.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
        and not p.name.startswith("~$")
    ]
    summary = Summary()
    written: dict[Path, Path] = {}
    bar = tqdm(sorted(files), desc="fichiers", unit="fichier")
    try:
        for src in bar:
            bar.set_postfix_str(src.name)
            if output_dir is not None:
                rel = src.relative_to(folder)
                dest = output_dir / rel.with_suffix(".md")
            else:
                dest = None
            target = dest if dest is not None else src.with_suffix(".md")
            try:
                if target in written:
                    raise ValueError(
                        f"sortie {target} déjà produite par {written[target]}"
                    )
                if skip_existing and target.exists():
                    # Still claims the target, so a same-named source that
                    # follows is reported as a collision rather than skipped.
                    written[target] = src
                    summary.skipped += 1
                    continue
                result = convert_file(src, dest)
                written[target] = src
                bar.write(f"  converted: {result}")
                summary.converted += 1
            except EmptyDocumentError as exc:
                bar.write(f"  vide : {src} — {exc}", file=sys.stderr)
                summary.empty += 1
            except Exception as exc:
                bar.write(f"  error: {src} — {exc}", file=sys.stderr)
                summary.errors += 1
    except KeyboardInterrupt:
        bar.close()
        raise BatchInterrupted(summary, len(files)) from None
    return summary

