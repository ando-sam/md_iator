# Usage reference

## Synopsis

```
md-iator SOURCE [-o SORTIE] [--skip-existing]
md-iator --version
```

| Argument | Description |
|---|---|
| `SOURCE` | Path to a `.docx` / `.pdf` file, or a folder |
| `-o SORTIE`, `--output SORTIE` | Output `.md` file (single-file mode) or output folder (batch mode) |
| `--skip-existing` | Leave existing `.md` files untouched instead of overwriting them |
| `--version` | Print the installed version (`md-iator 0.1.0`) and exit |

Without installation, `python main.py` accepts the same arguments.

Progress bars are drawn on `stderr` only when it is a terminal; they are
turned off when output is redirected or in CI, so logs stay readable.

### Messages

Everything the tool prints is in French. One line per file, then a summary:

| Prefix | Stream | Meaning |
|---|---|---|
| `converti :` | stdout | `.md` written |
| `vide :` | stderr | PDF with no extractable text, nothing written |
| `ignoré :` | stderr | existing `.md` kept (`--skip-existing`, single-file mode) |
| `erreur :` | stderr | conversion failed |

Since 0.2.0 the prefixes are French: `converted:` became `converti :` and
`error:` became `erreur :`. Scripts that parse the output must be updated.
The framing printed by Python's `argparse` (`usage:`, `options:`, and its own
`error:` lines for invalid arguments) stays in English.

---

## Single-file mode

Triggered when `input` is a file.

```bash
# Output written next to the source: report.md
python main.py report.docx

# Explicit output file
python main.py report.docx -o converted/report.md

# PDF with custom destination
python main.py scan.pdf -o notes/scan.md
```

The output directory is created automatically if it does not exist.

To write into a folder that does not exist yet, end `-o` with a slash:
`-o notes/` creates `notes/` and writes `notes/scan.md`. Without the trailing
slash, `-o notes` is taken as the output file name.

---

## Batch mode

Triggered when `input` is a directory. All `.docx` and `.pdf` files are
discovered **recursively**. Extensions are matched case-insensitively
(`REPORT.PDF` is included), and Word lock files (`~$report.docx`) are skipped.

```bash
# Each file gets a sibling .md in the same folder
python main.py ./documents/

# All .md files go to ./out/, mirroring the subfolder structure
python main.py ./documents/ -o ./out/
```

### Example tree

```
documents/
├── report.docx        →  documents/report.md
├── slides.pdf         →  documents/slides.md
└── archive/
    └── old.docx       →  documents/archive/old.md
```

With `-o ./out/`:

```
out/
├── report.md
├── slides.md
└── archive/
    └── old.md
```

### Error handling in batch mode

If a single file fails (corrupted, unsupported encoding, etc.), the error is
printed to `stderr` and conversion continues with the remaining files.
The exit code is `0` only if no file failed; `1` otherwise. Empty PDFs
(see below) are not failures.

```
  converti : out/report.md
  erreur : documents/bad.pdf — EOF marker not found
  converti : out/slides.md

2 convertis · 1 erreur
```

The final summary counts converted files, empty PDFs and errors; a zero count
is left out (except `convertis`). A folder with no `.docx` or `.pdf` prints
`aucun fichier .docx ou .pdf dans <folder>` and exits with `0`.

Each `.md` is written to a temporary file next to its destination, then
renamed. A failed or interrupted conversion (Ctrl-C included) never leaves a
truncated `.md` behind, and never replaces a previous `.md`.

### Name collisions

Two sources with the same name in the same folder (`report.docx` and
`report.pdf`) would both produce `report.md`. Files are processed in sorted
order: the first one is converted, the next one is reported as an error
instead of overwriting it.

```
  converti : out/report.md
  erreur : documents/report.pdf — sortie out/report.md déjà produite par documents/report.docx
```

### Skipping existing outputs and resuming

By default an existing `.md` is overwritten. With `--skip-existing`, a source
whose `.md` already exists is left alone and counted as skipped:

```bash
python main.py ./documents/ -o ./out/ --skip-existing
```

```
4 convertis · 1 ignoré
```

Skipped files get no line of their own, only the count in the summary. A
skipped source still claims its `.md`, so a same-named source that follows
(`report.pdf` after `report.docx`) is still reported as a collision. In
single-file mode, the skip is reported on `stderr`:
`ignoré : report.md existe déjà` (exit code `0`).

### Interrupting a run

Ctrl-C stops the run cleanly: the file being converted is discarded (no
partial `.md`), the summary of what was done is printed, and the exit code is
`130`.

```
1 converti
interrompu — 1/5 fichiers traités, aucun fichier partiel. Relancer avec --skip-existing pour reprendre.
```

Running the same command again with `--skip-existing` resumes where it
stopped.

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All conversions succeeded |
| `1` | At least one file failed (batch), or the single file failed |
| `2` | Invalid arguments or input path not found — nothing is converted |
| `130` | Interrupted with Ctrl-C |

---

## Output format details

### DOCX

Pandoc converts DOCX with full structural fidelity:

- ATX headings (`# H1`, `## H2`, …)
- Bullet and numbered lists
- Bold / italic / inline code
- Tables → GitHub-flavored Markdown tables
- Hyperlinks → `[text](url)`

### PDF

pdfplumber extracts raw text. Each page becomes a section:

```markdown
## Page 1

First page content...

---

## Page 2

Second page content...
```

A PDF with no extractable text at all (typically a scanned, image-only PDF)
produces **no** `.md` file. It is reported on `stderr` and counted as empty,
not as an error:

```
  vide : scans/invoice.pdf — aucun texte extrait (PDF scanné ? passer par ocrmypdf)
```

Run it through an OCR tool such as `ocrmypdf` first, then convert again. A PDF
where only some pages have no text is converted normally, with empty sections
for those pages.

---

## First-run pandoc download

If `pandoc` is not found on your `PATH`, it is downloaded automatically
via `pypandoc.download_pandoc()` and stored in the pypandoc data directory.
This happens once; subsequent runs use the cached binary. The download notice
is printed on `stderr`.

pandoc is only needed for `.docx` files: it is checked the first time a
`.docx` is actually converted. `--help`, `--version`, a missing input path, a
PDF-only folder, or `.docx` files skipped with `--skip-existing` never check
or download it.

If pandoc is missing and cannot be downloaded (no network), each `.docx` is
reported as an error with an installation hint, while PDFs are still
converted:

```
  erreur : documents/report.docx — pandoc introuvable et téléchargement impossible (réseau ?). Installer pandoc : https://pandoc.org/installing.html
  converti : out/slides.md

1 converti · 1 erreur
```

The download is attempted only once per run.

To install pandoc system-wide instead:

```bash
brew install pandoc   # macOS
apt install pandoc    # Debian/Ubuntu
```
