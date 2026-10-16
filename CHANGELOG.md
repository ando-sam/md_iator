# Changelog

All notable changes to md_iator. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [0.2.0] — unreleased

### Breaking

- All messages are in French. The prefixes `converted:` and `error:` are now
  `converti :` and `erreur :`, and the batch summary `N/M fichiers convertis.`
  is replaced by `3 convertis · 1 vide · 1 erreur`. Scripts parsing the output
  must be updated.
- The code now lives in the `md_iator/` package. Without installation, run
  `python -m md_iator` instead of `python md_iator.py`. The installed
  `md-iator` command is unchanged.
- DOCX files are converted to GitHub-flavored Markdown instead of pandoc's own
  Markdown. Tables were pandoc grid or multiline tables, which VSCode and
  GitHub do not display as tables; they are now pipe tables, or HTML
  `<table>` when a cell holds a nested table or several paragraphs. Image
  sizes become `<img … style="width:…">` instead of `{width="…"}` attributes
  shown as plain text. Tools that read pandoc's Markdown attributes lose them.

### Added

- `--skip-existing`: keep existing `.md` files instead of overwriting them;
  rerunning an interrupted batch with it resumes where it stopped.
- `--version`.
- DOCX images are extracted into `<name>_media/` next to the `.md`, with
  working relative links. They were previously linked but never extracted.
- PDFs with no extractable text (scanned) write nothing and are reported as
  `vide :`, instead of producing an empty file counted as a success.
- Ctrl-C prints the partial summary and a resume hint, and exits with `130`.
- Exit code `2` for invalid arguments or a missing input path is documented.
- MIT license and package metadata.

### Changed

- Supported platforms are Linux and macOS, tested in CI with Python 3.10 to
  3.14. Windows is not supported: its test runs failed and it is no longer
  tested.
- Every `.md` is written to a temporary file and renamed, so a failed or
  interrupted conversion never leaves a truncated file or replaces the
  previous one.
- pandoc is checked, and downloaded if needed, only when a `.docx` is actually
  converted. Offline, each `.docx` fails with an installation hint while PDFs
  are still converted.
- Progress bars are shown only when stderr is a terminal.
- `-o folder/` (trailing slash) creates the folder in single-file mode instead
  of writing a file named `folder`.

### Fixed

- Batch mode skipped files with upper-case extensions (`REPORT.PDF`).
- Batch mode tried to convert Word lock files (`~$report.docx`).
- `report.docx` and `report.pdf` in the same folder silently overwrote each
  other's `.md`; the second one is now reported as a collision.
- `--help` or a wrong path triggered a pandoc download.

## [0.1.0]

- First version: DOCX (pandoc) and PDF (pdfplumber) to Markdown, single file
  or recursive folder.
