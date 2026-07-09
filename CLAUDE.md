# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Pyenv virtualenv `md_iator` (set via `.python-version`). Dependencies already installed: `pypandoc`, `pdfplumber`.

Pandoc binary is not required at install time — the app downloads it automatically on first run via `pypandoc.download_pandoc()`.

## Usage

```bash
# Fichier unique
python md_iator.py rapport.docx
python md_iator.py rapport.pdf -o ./output/rapport.md

# Dossier entier (batch récursif)
python md_iator.py ./documents/
python md_iator.py ./documents/ -o ./markdown/
```

Formats supportés : `.docx` (via pandoc) et `.pdf` (via pdfplumber).

## Architecture

`md_iator.py` est un fichier unique :

- `convert_docx(src, dest)` — délègue à `pypandoc.convert_file`
- `convert_pdf(src, dest)` — extrait le texte page par page avec `pdfplumber`, insère des séparateurs `---` entre les pages
- `convert_file(src, output)` — dispatch par extension, calcule le chemin de sortie
- `batch_convert(folder, output_dir)` — `rglob` récursif sur `.docx` et `.pdf`, continue sur erreur
- `main()` — argparse avec un positional `input` (fichier ou dossier) et `-o/--output` optionnel
