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
python main.py rapport.docx
```

Formats supportés : `.docx` (via pandoc) et `.pdf` (via pdfplumber).

## Architecture

Deux modules :

`md_iator.py` — logique de conversion :

- `ensure_pandoc()` — vérifie pandoc, le télécharge s'il est absent ; appelé par `convert_docx` (donc seulement si un DOCX est vraiment converti) ; résultat mis en cache par `_pandoc_problem()` (`functools.cache`) — un téléchargement raté n'est tenté qu'une fois et lève `PandocUnavailableError` (message lisible + lien d'installation)
- `media_dir(dest)` — dossier d'images d'un DOCX, à côté du `.md` : `<nom>_media/`, espaces et ponctuation remplacés par `_` (liens CommonMark valides)
- `convert_docx(src, dest)` — délègue à `pypandoc.convert_file`, lancé depuis le dossier de `dest` avec `--extract-media` pour des liens d'images relatifs au `.md`
- `convert_pdf(src, dest)` — extrait le texte page par page avec `pdfplumber`, insère des séparateurs `---` entre les pages ; lève `EmptyDocumentError` si aucune page n'a de texte (PDF scanné), sans rien écrire
- `output_path(src, output)` — calcule le chemin du `.md` (à côté de la source, dans un dossier existant, ou fichier explicite)
- `convert_file(src, output)` — dispatch par extension, chemin via `output_path` ; convertit dans un dossier temporaire voisin (`.<nom>.md.<pid>.tmp/`), puis déplace les images (fusion, le dossier `_media` existant n'est jamais supprimé) et renomme le `.md` (jamais de `.md` tronqué)
- Barres `tqdm` créées avec `disable=None` : affichées seulement si stderr est un terminal
- `batch_convert(folder, output_dir, skip_existing)` — `rglob` récursif, extensions insensibles à la casse, ignore les fichiers verrou Word `~$*`, signale en erreur une source dont le `.md` cible a déjà été produit (pas d'écrasement), continue sur erreur ; un DOCX réserve aussi son dossier `_media` (collision `a b.docx` / `a_b.docx` signalée) ; avec `skip_existing`, saute une cible existante tout en la réservant (la collision reste signalée) ; renvoie un `Summary` (`converted`, `empty`, `skipped`, `errors`) ; sur Ctrl-C lève `BatchInterrupted` (sous-classe de `KeyboardInterrupt`) avec le `Summary` partiel et le total

`main.py` — point d'entrée CLI (`md-iator = "main:main"`) :

- `format_summary(summary)` — récap final en français (`2 convertis · 1 vide · 1 erreur`, compteurs à 0 omis sauf `convertis`)
- `main()` — argparse avec un positional `input` (fichier ou dossier) et `-o/--output` optionnel ; un `-o` terminé par `/` est créé comme dossier ; `--version` (via `importlib.metadata`) ; `prog="md-iator"` ; `--skip-existing` ; Ctrl-C → récap partiel, message de reprise, code 130

Tests pytest dans `tests/` : `pip install -e ".[dev]"` puis `python -m pytest`. `tests/conftest.py` remplace pandoc et pdfplumber par des faux moteurs (fixtures `engines`, `make`, `interrupt_at` — simule un Ctrl-C au n-ième `convert_file` —, `pandoc_checks` ; ce dernier patche `md_iator.ensure_pandoc`, que `convert_docx` appelle via le module, et `engines` le requiert — aucun test de conversion ne touche le réseau) — aucun réseau ni vrai document. Ne pas confondre avec `test/`, qui contient des documents d'exemple locaux non versionnés.

Pas de linter configuré. `docs/usage.md` contient la référence CLI complète.
