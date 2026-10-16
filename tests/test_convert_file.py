import pytest

import md_iator


def test_output_next_to_source_without_output(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx", "Titre")

    dest = md_iator.convert_file(src)

    assert dest == tmp_path / "rapport.md"
    assert dest.read_text(encoding="utf-8") == "# Titre\n"


def test_output_explicit_file_creates_parents(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx")
    out = tmp_path / "a" / "b" / "notes.md"

    assert md_iator.convert_file(src, out) == out
    assert out.is_file()


def test_output_existing_directory(engines, make, tmp_path):
    src = make(tmp_path / "src" / "rapport.pdf")
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    assert md_iator.convert_file(src, out_dir) == out_dir / "rapport.md"


def test_extension_uppercase_accepted(engines, make, tmp_path):
    src = make(tmp_path / "SCAN.PDF", "texte")

    assert md_iator.convert_file(src) == tmp_path / "SCAN.md"


def test_unsupported_extension_raises(make, tmp_path):
    src = make(tmp_path / "notes.txt")

    with pytest.raises(ValueError, match="format non supporté"):
        md_iator.convert_file(src)
    assert not (tmp_path / "notes.md").exists()


def test_source_not_modified(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx", "Titre")

    md_iator.convert_file(src)

    assert src.read_text(encoding="utf-8") == "Titre"


def test_failed_conversion_leaves_no_file(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx", corrupt=True)

    with pytest.raises(RuntimeError):
        md_iator.convert_file(src)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["rapport.docx"]


@pytest.mark.parametrize("exc", [RuntimeError("panne"), KeyboardInterrupt()])
def test_interrupted_conversion_keeps_previous_output(make, monkeypatch, tmp_path, exc):
    src = make(tmp_path / "rapport.pdf")
    previous = make(tmp_path / "rapport.md", "ancienne version")

    def write_half_then_fail(src, dest):
        dest.write_text("tronqué", encoding="utf-8")
        raise exc

    monkeypatch.setattr(md_iator, "convert_pdf", write_half_then_fail)

    with pytest.raises(type(exc)):
        md_iator.convert_file(src)

    assert previous.read_text(encoding="utf-8") == "ancienne version"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["rapport.md", "rapport.pdf"]
