import pytest

import md_iator


def md_files(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md"))


def test_batch_recursive_mirrors_tree_under_output(engines, make, tmp_path):
    src = tmp_path / "docs"
    make(src / "rapport.docx")
    make(src / "archive" / "old.pdf")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == (2, 0)
    assert md_files(out) == ["archive/old.md", "rapport.md"]


def test_batch_without_output_writes_next_to_sources(engines, make, tmp_path):
    make(tmp_path / "a.docx")
    make(tmp_path / "sub" / "b.pdf")

    assert md_iator.batch_convert(tmp_path) == (2, 0)
    assert md_files(tmp_path) == ["a.md", "sub/b.md"]


def test_batch_ignores_unsupported_files(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "notes.txt")
    make(src / "a.docx")

    assert md_iator.batch_convert(src, tmp_path / "out") == (1, 0)


def test_batch_continues_after_error(engines, make, tmp_path, capsys):
    src = tmp_path / "src"
    make(src / "a.docx", corrupt=True)
    make(src / "b.pdf")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == (1, 1)
    assert md_files(out) == ["b.md"]
    assert f"error: {src / 'a.docx'}" in capsys.readouterr().err


def test_batch_includes_uppercase_extension(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "SCAN.PDF")
    make(src / "Rapport.DOCX")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == (2, 0)
    assert md_files(out) == ["Rapport.md", "SCAN.md"]


def test_batch_skips_word_lock_files(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "rapport.docx")
    make(src / "~$rapport.docx", corrupt=True)

    assert md_iator.batch_convert(src, tmp_path / "out") == (1, 0)


@pytest.mark.parametrize("with_output", [True, False])
def test_batch_collision_reports_error_without_overwrite(
    engines, make, tmp_path, capsys, with_output
):
    src = tmp_path / "src"
    make(src / "rapport.docx", "depuis docx")
    make(src / "rapport.pdf", "depuis pdf")
    out = tmp_path / "out" if with_output else None

    assert md_iator.batch_convert(src, out) == (1, 1)
    target = (out or src) / "rapport.md"
    assert target.read_text(encoding="utf-8") == "# depuis docx\n"
    err = capsys.readouterr().err
    assert f"error: {src / 'rapport.pdf'}" in err
    assert "déjà produite" in err


def test_batch_collision_second_converts_when_first_failed(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "rapport.docx", corrupt=True)
    make(src / "rapport.pdf", "depuis pdf")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == (1, 1)
    assert (out / "rapport.md").read_text(encoding="utf-8") == (
        "## Page 1\n\ndepuis pdf"
    )
