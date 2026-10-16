"""Fake conversion engines, so tests need neither pandoc nor real PDF files.

A fake source file is plain UTF-8 text:
- `.docx` converts to "# <content>\\n";
- `.pdf` holds its pages separated by form feeds (an empty page extracts as
  None, like pdfplumber on an image-only page);
- a file created with `corrupt=True` makes both engines raise.
"""

from pathlib import Path

import pytest

import md_iator

CORRUPT = "CORRUPT"


class FakePage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str | None:
        return self._text or None


class FakePdf:
    def __init__(self, texts: list[str]):
        self.pages = [FakePage(t) for t in texts]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _read(path) -> str:
    content = Path(path).read_text(encoding="utf-8")
    if content == CORRUPT:
        raise RuntimeError("fichier illisible")
    return content


@pytest.fixture
def engines(monkeypatch, pandoc_checks):
    # Requesting pandoc_checks keeps every conversion test off the network.
    def convert_file(source, to, outputfile):
        Path(outputfile).write_text(f"# {_read(source)}\n", encoding="utf-8")

    monkeypatch.setattr(md_iator.pypandoc, "convert_file", convert_file)
    monkeypatch.setattr(
        md_iator.pdfplumber, "open", lambda src: FakePdf(_read(src).split("\f"))
    )


@pytest.fixture
def pandoc_checks(monkeypatch) -> list[int]:
    """Record calls to ensure_pandoc instead of touching the network."""
    calls: list[int] = []
    monkeypatch.setattr(md_iator, "ensure_pandoc", lambda: calls.append(1))
    return calls


@pytest.fixture
def make():
    def _make(path: Path, content: str = "contenu", corrupt: bool = False) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(CORRUPT if corrupt else content, encoding="utf-8")
        return path

    return _make


@pytest.fixture
def interrupt_at(monkeypatch):
    """Make the n-th call to convert_file raise KeyboardInterrupt (Ctrl-C)."""

    def _interrupt_at(n: int) -> None:
        real = md_iator.convert_file
        calls = 0

        def convert_file(src, output=None):
            nonlocal calls
            calls += 1
            if calls == n:
                raise KeyboardInterrupt
            return real(src, output)

        monkeypatch.setattr(md_iator, "convert_file", convert_file)

    return _interrupt_at
