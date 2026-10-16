"""Convert DOCX and PDF files to Markdown using pypandoc and pdfplumber."""

import sys
from pathlib import Path

import pdfplumber
import pypandoc
from tqdm import tqdm

SUPPORTED_EXTENSIONS = {".docx", ".pdf"}


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
        for i, page in enumerate(
            tqdm(pdf.pages, desc=src.name, unit="page", leave=False), start=1
        ):
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
    # Extension matched case-insensitively; "~$" files are Word lock files.
    files = [
        p for p in folder.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
        and not p.name.startswith("~$")
    ]
    ok, errors = 0, 0
    written: dict[Path, Path] = {}
    bar = tqdm(sorted(files), desc="fichiers", unit="fichier")
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
            result = convert_file(src, dest)
            written[target] = src
            bar.write(f"  converted: {result}")
            ok += 1
        except Exception as exc:
            bar.write(f"  error: {src} — {exc}", file=sys.stderr)
            errors += 1
    return ok, errors

