"""Fake conversion engines, so tests need neither pandoc nor real PDF files.

A fake source file is plain UTF-8 text:
- `.docx` converts to "# <content>\\n"; if the content contains IMAGE, the
  fake pandoc also extracts one image, the way `--extract-media` does; if it
  contains TOC, the document starts with a Word table of contents. Like real
  pandoc, the fake reads the DOCX into a JSON tree (`convert_file`) and writes
  Markdown from the tree (`convert_text`);
- `.pdf` holds its pages separated by form feeds (an empty page extracts as
  None, like pdfplumber on an image-only page);
- a file created with `corrupt=True` makes both engines raise.
"""

import json
from pathlib import Path

import pytest

import md_iator

CORRUPT = "CORRUPT"
IMAGE = "IMAGE"
TOC = "TOC"


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


def _str(text: str) -> list[dict]:
    return [{"t": "Str", "c": text}]


def _inline_md(inline: dict) -> str:
    if inline["t"] == "Space":
        return " "
    if inline["t"] in ("Link", "Image"):
        _, content, (target, _) = inline["c"]
        bang = "!" if inline["t"] == "Image" else ""
        return f"{bang}[{''.join(map(_inline_md, content))}]({target})"
    return inline["c"]


def _block_md(block: dict) -> str:
    if block["t"] == "Header":
        level, _, inlines = block["c"]
        return "#" * level + " " + "".join(map(_inline_md, inlines))
    return "".join(map(_inline_md, block["c"]))


@pytest.fixture
def engines(monkeypatch, pandoc_checks):
    # Requesting pandoc_checks keeps every conversion test off the network.
    def convert_file(source, to, extra_args=(), cworkdir=None):
        assert to == "json"
        content = _read(source)
        blocks = [{"t": "Header", "c": [1, ["", [], []], _str(content)]}]
        if TOC in content:
            entry = {"t": "Link", "c": [["", [], []], _str("Titre"), ["#titre", ""]]}
            blocks[:0] = [
                {"t": "Header", "c": [1, ["", ["TOC-Heading"], []], _str("Sommaire")]},
                {"t": "Para", "c": [entry]},
            ]
        media = [a.split("=", 1)[1] for a in extra_args if a.startswith("--extract-media=")]
        if IMAGE in content and media:
            image = Path(cworkdir) / media[0] / "media" / "image1.png"
            image.parent.mkdir(parents=True, exist_ok=True)
            image.write_bytes(b"\x89PNG fake")
            target = f"{media[0]}/media/image1.png"
            blocks.append({"t": "Para", "c": [
                {"t": "Image", "c": [["", [], []], _str("logo"), [target, ""]]}
            ]})
        return json.dumps({"pandoc-api-version": [1, 23, 1], "meta": {}, "blocks": blocks})

    def convert_text(source, to, format, outputfile):
        assert (to, format) == ("gfm", "json")
        blocks = json.loads(source)["blocks"]
        text = "\n\n".join(map(_block_md, blocks)) + "\n"
        Path(outputfile).write_text(text, encoding="utf-8")

    monkeypatch.setattr(md_iator.pypandoc, "convert_file", convert_file)
    monkeypatch.setattr(md_iator.pypandoc, "convert_text", convert_text)
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
