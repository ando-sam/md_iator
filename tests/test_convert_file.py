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
