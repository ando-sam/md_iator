# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Pyenv virtualenv `md_iator` (set via `.python-version`). Installable via `pip install -e .` (pyproject.toml, deps pinnées : `pypandoc`, `pdfplumber`, `tqdm`) — expose la commande `md-iator`.

Pandoc binary is not required at install time — the app downloads it automatically on first run via `pypandoc.download_pandoc()`.

## Usage

```bash
# Fichier unique
md-iator rapport.docx
md-iator rapport.pdf -o ./output/rapport.md

# Dossier entier (batch récursif)
md-iator ./documents/
md-iator ./documents/ -o ./markdown/

# Sans installation (fallback)
python md_iator.py rapport.docx
```

Formats supportés : `.docx` (via pandoc) et `.pdf` (via pdfplumber).

## Architecture

`md_iator.py` est un fichier unique :

- `convert_docx(src, dest)` — délègue à `pypandoc.convert_file`
- `convert_pdf(src, dest)` — extrait le texte page par page avec `pdfplumber`, insère des séparateurs `---` entre les pages
- `convert_file(src, output)` — dispatch par extension, calcule le chemin de sortie
- `batch_convert(folder, output_dir)` — `rglob` récursif, extensions insensibles à la casse, ignore les fichiers verrou Word `~$*`, signale en erreur une source dont le `.md` cible a déjà été produit (pas d'écrasement), continue sur erreur
- `main()` — argparse avec un positional `input` (fichier ou dossier) et `-o/--output` optionnel ; un `-o` terminé par `/` est créé comme dossier ; pandoc n'est vérifié/téléchargé qu'après validation des arguments

Tests pytest dans `tests/` : `pip install -e ".[dev]"` puis `python -m pytest`. `tests/conftest.py` remplace pandoc et pdfplumber par des faux moteurs (fixtures `engines`, `make`, `pandoc_checks`) — aucun réseau ni vrai document. Ne pas confondre avec `test/`, qui contient des documents d'exemple locaux non versionnés.

Pas de linter configuré. `docs/usage.md` contient la référence CLI complète.
