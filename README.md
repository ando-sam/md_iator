# md_iator

> Convert **DOCX** and **PDF** files to clean **Markdown** — single file or entire folder, one command.

```bash
python md_iator.py report.docx
python md_iator.py ./documents/ -o ./markdown/
```

---

## Features

- **DOCX → Markdown** via [pandoc](https://pandoc.org/) (auto-downloaded on first run)
- **PDF → Markdown** via [pdfplumber](https://github.com/jsvine/pdfplumber), with page-level headings
- **Single file** or **recursive batch** conversion
- Custom output path with `-o`
- Errors on individual files never abort a batch run
- Zero system setup — pandoc is fetched automatically if missing

---

## Requirements

- Python 3.10+
- pyenv virtualenv `md_iator` (or any env with `pypandoc` and `pdfplumber` installed)

---

## Usage

### Single file

```bash
# Output next to the source file
python md_iator.py report.docx          # → report.md

# Custom output path
python md_iator.py report.pdf -o out/report.md
```

### Batch (folder)

```bash
# Convert all .docx and .pdf in ./docs/ (recursive)
python md_iator.py ./docs/

# Send all results to a separate folder, preserving subfolder structure
python md_iator.py ./docs/ -o ./markdown/
```

### Help

```bash
python md_iator.py --help
```

---

## Supported formats

| Input  | Engine     | Notes                                      |
|--------|------------|--------------------------------------------|
| `.docx`| pandoc     | Full fidelity: headings, lists, bold, etc. |
| `.pdf` | pdfplumber | Text extraction; one `## Page N` per page  |

---

## Output format

**DOCX** files are converted with full pandoc fidelity — headings, bullet lists, bold/italic, tables, and links are all preserved in Markdown.

**PDF** files produce one section per page:

```markdown
## Page 1

Content of the first page...

---

## Page 2

Content of the second page...
```

---

## Project structure

```
md_iator/
├── md_iator.py      # CLI entry point — the whole app
└── docs/
    └── usage.md     # Full CLI reference and examples
```
