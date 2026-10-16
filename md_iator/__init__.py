"""Convert DOCX and PDF files to Markdown using pypandoc and pdfplumber."""

import functools
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
import pypandoc
from tqdm import tqdm

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}


class EmptyDocumentError(Exception):
    """No text could be extracted, so no Markdown file is written."""


class PandocUnavailableError(Exception):
    """pandoc is missing and could not be downloaded."""


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


@functools.cache
def _pandoc_problem() -> str | None:
    # Cached, so a failed download is attempted once per run, not per file.
    try:
        pypandoc.get_pandoc_version()
        return None
    except OSError:
        pass
    tqdm.write("pandoc introuvable — téléchargement en cours...", file=sys.stderr)
    try:
        pypandoc.download_pandoc(delete_installer=True)
    except Exception:
        return (
            "pandoc introuvable et téléchargement impossible (réseau ?). "
            "Installer pandoc : https://pandoc.org/installing.html"
        )
    tqdm.write("pandoc installé.", file=sys.stderr)
    return None


def ensure_pandoc() -> None:
    problem = _pandoc_problem()
    if problem:
        raise PandocUnavailableError(problem)


def media_dir(dest: Path) -> Path:
    # Spaces and punctuation would break the image links in CommonMark.
    slug = re.sub(r"[^\w.-]+", "_", dest.stem).strip("_") or "document"
    return dest.with_name(f"{slug}_media")


def convert_docx(src: Path, dest: Path) -> None:
    ensure_pandoc()
    # Run pandoc from dest's folder so image links are relative to the .md.
    pypandoc.convert_file(
        str(src.resolve()),
        "markdown",
        outputfile=str(dest.resolve()),
        extra_args=[f"--extract-media={media_dir(dest).name}"],
        cworkdir=str(dest.parent.resolve()),
    )


def convert_pdf(src: Path, dest: Path) -> None:
    with pdfplumber.open(src) as pdf:
        pages = []
        has_text = False
        for i, page in enumerate(
            tqdm(pdf.pages, desc=src.name, unit="page", leave=False, disable=None),
            start=1,
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

    # Convert inside a temporary sibling folder, then move the result into
    # place: a failed or interrupted conversion never leaves a truncated .md
    # nor clobbers the previous one.
    stage = dest.with_name(f".{dest.name}.{os.getpid()}.tmp")
    stage.mkdir(exist_ok=True)
    try:
        staged = stage / dest.name
        if ext == ".docx":
            convert_docx(src, staged)
        elif ext == ".pdf":
            convert_pdf(src, staged)
        _merge_media(media_dir(staged), media_dir(dest))
        staged.replace(dest)
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    return dest


def _merge_media(staged: Path, final: Path) -> None:
    # Moved file by file into the existing folder, which is never deleted:
    # it may hold files the user put there.
    if not staged.is_dir():
        return
    for file in staged.rglob("*"):
        if file.is_file():
            target = final / file.relative_to(staged)
            target.parent.mkdir(parents=True, exist_ok=True)
            file.replace(target)


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
    bar = tqdm(sorted(files), desc="fichiers", unit="fichier", disable=None)
    try:
        for src in bar:
            bar.set_postfix_str(src.name)
            if output_dir is not None:
                rel = src.relative_to(folder)
                dest = output_dir / rel.with_suffix(".md")
            else:
                dest = None
            target = dest if dest is not None else src.with_suffix(".md")
            # A DOCX also claims its images folder: "a b.docx" and "a_b.docx"
            # would otherwise mix their images in "a_b_media/".
            claims = [target]
            if src.suffix.lower() == ".docx":
                claims.append(media_dir(target))
            try:
                for claim in claims:
                    if claim in written:
                        raise ValueError(
                            f"sortie {claim} déjà produite par {written[claim]}"
                        )
                if skip_existing and target.exists():
                    # Still claims the target, so a same-named source that
                    # follows is reported as a collision rather than skipped.
                    written.update(dict.fromkeys(claims, src))
                    summary.skipped += 1
                    continue
                result = convert_file(src, dest)
                written.update(dict.fromkeys(claims, src))
                bar.write(f"  converti : {result}")
                summary.converted += 1
            except EmptyDocumentError as exc:
                bar.write(f"  vide : {src} — {exc}", file=sys.stderr)
                summary.empty += 1
            except Exception as exc:
                bar.write(f"  erreur : {src} — {exc}", file=sys.stderr)
                summary.errors += 1
    except KeyboardInterrupt:
        bar.close()
        raise BatchInterrupted(summary, len(files)) from None
    return summary

