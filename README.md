# md_iator

> Convert a whole folder of **DOCX** and **PDF** files to **Markdown** in one
> command — and know, without opening anything, which files could not be read.

```bash
md-iator ./documents/ -o ./markdown/
```

```
  converti : markdown/archive/old.md
  converti : markdown/report.md
  vide : documents/scan.pdf — aucun texte extrait (PDF scanné ? passer par ocrmypdf)
  converti : markdown/slides.md

3 convertis · 1 vide
```

The tool talks in French; this documentation is in English.

---

## Install

Runs on **Linux and macOS** with Python 3.10 or later. Windows is not
supported. [pipx](https://pipx.pypa.io/) installs the command in its own
environment:

```bash
pipx install git+https://github.com/ando-sam/md_iator.git
md-iator --version
```

`pip install git+https://github.com/ando-sam/md_iator.git` works too, inside
a virtual environment.

Nothing else to install: [pandoc](https://pandoc.org/), used for DOCX, is
downloaded automatically the first time a `.docx` is converted, once.
PDF-only use never needs it.

---

## Quick start

```bash
# One file — writes report.md next to report.docx
md-iator report.docx

# One file, chosen destination
md-iator report.pdf -o notes/report.md

# A whole folder, recursively — mirrors the tree under ./markdown/
md-iator ./documents/ -o ./markdown/

# Resume an interrupted run, or refresh only what is missing
md-iator ./documents/ -o ./markdown/ --skip-existing
```

`md-iator --help` lists every option; [docs/usage.md](docs/usage.md) is the
full reference.

---

## What you get

| Input | Engine | Output |
|---|---|---|
| `.docx` | pandoc | GitHub-flavored Markdown, as rendered by VSCode and GitHub: headings, lists, bold/italic, tables, links; images extracted to `<name>_media/` next to the `.md`, with working relative links |
| `.pdf` | pdfplumber | Raw text, one `## Page N` section per page, separated by `---` |

### Built for folders

- Every `.docx` / `.pdf` is found recursively, whatever the case of the
  extension (`REPORT.PDF` included). Word lock files (`~$report.docx`) are
  ignored.
- One broken file never stops the run: it is reported and the next one
  starts.
- Two sources that would write the same `.md` (`report.docx` and
  `report.pdf`) are reported as a collision — nothing is overwritten.
- Each `.md` is written to a temporary file first, then renamed: an error or
  a Ctrl-C never leaves a truncated file.
- Ctrl-C prints what was done and how to resume:

  ```
  1 converti
  interrompu — 1/5 fichiers traités, aucun fichier partiel. Relancer avec --skip-existing pour reprendre.
  ```

- Progress bars appear in a terminal only, so CI logs stay clean.

### Messages

| Prefix | Meaning |
|---|---|
| `converti :` | `.md` written |
| `vide :` | PDF with no extractable text (usually scanned): nothing written |
| `ignoré :` | `.md` already there, kept because of `--skip-existing` |
| `erreur :` | conversion failed — the reason follows |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | No error (empty PDFs and skipped files are not errors) |
| `1` | At least one file failed |
| `2` | Invalid arguments or input path not found |
| `130` | Interrupted with Ctrl-C |

---

## Limitations

- **Windows**: not supported and not tested. The tests fail there, and DOCX
  image links are suspected not to work. Use Linux or macOS.
- **Scanned PDFs**: there is no OCR. Run them through
  [ocrmypdf](https://ocrmypdf.readthedocs.io/) first, then convert again.
- **PDF layout**: only the text is extracted — no headings, tables or images.
- **DOCX heading numbers** added automatically by Word (`A.`, `1.1`) are
  lost, and the Word table of contents is copied with links that do not lead
  to the headings in VSCode or on GitHub.
- **Offline first run**: if pandoc is missing and cannot be downloaded, each
  `.docx` fails with an installation hint; PDFs are still converted. Install
  pandoc yourself in that case: <https://pandoc.org/installing.html>.

---

## Upgrading from 0.1

The message prefixes are now French: `converted:` became `converti :` and
`error:` became `erreur :`, and the summary reads `3 convertis · 1 vide`
instead of `N/M fichiers convertis.`. Update any script that parses the
output. DOCX files are now converted to GitHub-flavored Markdown instead of
pandoc's own Markdown: convert them again to get tables that VSCode and
GitHub display. See [CHANGELOG.md](CHANGELOG.md).

---

## Development

```bash
git clone https://github.com/ando-sam/md_iator.git
cd md_iator
pip install -e ".[dev]"
python -m pytest
```

The tests replace pandoc and pdfplumber with fakes, so they run offline in
under a second; one extra test uses the real pandoc when it is installed.
Without installing, `python -m md_iator` runs the CLI from the repository
root.

```
md_iator/
├── __init__.py   # conversion: DOCX, PDF, folder runs
├── cli.py        # command line: arguments, messages, exit codes
└── __main__.py   # python -m md_iator
tests/            # pytest suite
docs/usage.md     # full CLI reference
```

---

## License

[MIT](LICENSE)
