# Usage reference

## Synopsis

```
python main.py <input> [-o <output>]
```

| Argument | Description |
|---|---|
| `input` | Path to a `.docx` / `.pdf` file, or a folder |
| `-o`, `--output` | Output `.md` file (single-file mode) or output folder (batch mode) |

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
The exit code is `0` only if every file succeeded; `1` otherwise.

```
  converted: out/report.md
  error: documents/bad.pdf — EOF marker not found
  converted: out/slides.md

2/3 fichiers convertis.
```

### Name collisions

Two sources with the same name in the same folder (`report.docx` and
`report.pdf`) would both produce `report.md`. Files are processed in sorted
order: the first one is converted, the next one is reported as an error
instead of overwriting it.

```
  converted: out/report.md
  error: documents/report.pdf — sortie out/report.md déjà produite par documents/report.docx
```

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All conversions succeeded |
| `1` | At least one file failed (batch), or the single file failed |
| `2` | Invalid arguments or input path not found — nothing is converted |

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

Scanned PDFs (image-only) produce empty sections. For OCR support,
pre-process with a tool such as `ocrmypdf` before converting.

---

## First-run pandoc download

If `pandoc` is not found on your `PATH`, it is downloaded automatically
via `pypandoc.download_pandoc()` and stored in the pypandoc data directory.
This happens once; subsequent runs use the cached binary. The check runs
only after the arguments are validated, so `--help` or a missing input path
never triggers a download.

To install pandoc system-wide instead:

```bash
brew install pandoc   # macOS
apt install pandoc    # Debian/Ubuntu
```
