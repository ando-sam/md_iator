import pytest

import md_iator


def md_files(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md"))


def test_batch_recursive_mirrors_tree_under_output(engines, make, tmp_path):
    src = tmp_path / "docs"
    make(src / "rapport.docx")
    make(src / "archive" / "old.pdf")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=2)
    assert md_files(out) == ["archive/old.md", "rapport.md"]


def test_batch_without_output_writes_next_to_sources(engines, make, tmp_path):
    make(tmp_path / "a.docx")
    make(tmp_path / "sub" / "b.pdf")

    assert md_iator.batch_convert(tmp_path) == md_iator.Summary(converted=2)
    assert md_files(tmp_path) == ["a.md", "sub/b.md"]


def test_batch_ignores_unsupported_files(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "notes.txt")
    make(src / "a.docx")

    assert md_iator.batch_convert(src, tmp_path / "out") == md_iator.Summary(converted=1)


def test_batch_continues_after_error(engines, make, tmp_path, capsys):
    src = tmp_path / "src"
    make(src / "a.docx", corrupt=True)
    make(src / "b.pdf")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1, errors=1)
    assert md_files(out) == ["b.md"]
    assert f"erreur : {src / 'a.docx'}" in capsys.readouterr().err


def test_batch_counts_empty_pdf_apart_from_errors(engines, make, tmp_path, capsys):
    src = tmp_path / "src"
    make(src / "scan.pdf", "\f")
    make(src / "a.docx")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1, empty=1)
    assert md_files(out) == ["a.md"]
    assert f"vide : {src / 'scan.pdf'} — aucun texte extrait" in capsys.readouterr().err


def test_batch_empty_source_does_not_claim_output(engines, make, tmp_path):
    src = tmp_path / "src"
    # "rapport.PDF" sorts before "rapport.docx", so the empty one runs first.
    make(src / "rapport.PDF", "\f")
    make(src / "rapport.docx", "depuis docx")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1, empty=1)
    assert (out / "rapport.md").read_text(encoding="utf-8") == "# depuis docx\n"


def test_batch_includes_uppercase_extension(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "SCAN.PDF")
    make(src / "Rapport.DOCX")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=2)
    assert md_files(out) == ["Rapport.md", "SCAN.md"]


def test_batch_skips_word_lock_files(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "rapport.docx")
    make(src / "~$rapport.docx", corrupt=True)

    assert md_iator.batch_convert(src, tmp_path / "out") == md_iator.Summary(converted=1)


@pytest.mark.parametrize("with_output", [True, False])
def test_batch_collision_reports_error_without_overwrite(
    engines, make, tmp_path, capsys, with_output
):
    src = tmp_path / "src"
    make(src / "rapport.docx", "depuis docx")
    make(src / "rapport.pdf", "depuis pdf")
    out = tmp_path / "out" if with_output else None

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1, errors=1)
    target = (out or src) / "rapport.md"
    assert target.read_text(encoding="utf-8") == "# depuis docx\n"
    err = capsys.readouterr().err
    assert f"erreur : {src / 'rapport.pdf'}" in err
    assert "déjà produite" in err


def test_batch_collision_second_converts_when_first_failed(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "rapport.docx", corrupt=True)
    make(src / "rapport.pdf", "depuis pdf")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1, errors=1)
    assert (out / "rapport.md").read_text(encoding="utf-8") == (
        "## Page 1\n\ndepuis pdf"
    )


def test_batch_overwrites_existing_output_by_default(engines, make, tmp_path):
    src = tmp_path / "src"
    make(src / "a.docx", "nouveau")
    out = tmp_path / "out"
    make(out / "a.md", "écrit à la main")

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1)
    assert (out / "a.md").read_text(encoding="utf-8") == "# nouveau\n"


@pytest.mark.parametrize("with_output", [True, False])
def test_batch_skip_existing_keeps_existing_output(engines, make, tmp_path, with_output):
    src = tmp_path / "src"
    make(src / "a.docx")
    make(src / "b.pdf")
    out = tmp_path / "out" if with_output else None
    existing = make((out or src) / "a.md", "écrit à la main")

    summary = md_iator.batch_convert(src, out, skip_existing=True)

    assert summary == md_iator.Summary(converted=1, skipped=1)
    assert existing.read_text(encoding="utf-8") == "écrit à la main"
    assert ((out or src) / "b.md").is_file()


def test_batch_skipped_source_still_claims_its_output(engines, make, tmp_path, capsys):
    src = tmp_path / "src"
    make(src / "rapport.docx")
    make(src / "rapport.pdf")
    out = tmp_path / "out"
    make(out / "rapport.md", "déjà converti")

    summary = md_iator.batch_convert(src, out, skip_existing=True)

    assert summary == md_iator.Summary(skipped=1, errors=1)
    assert f"erreur : {src / 'rapport.pdf'}" in capsys.readouterr().err


def test_batch_interrupt_reports_progress(engines, make, tmp_path, interrupt_at):
    src = tmp_path / "src"
    for name in ("a.docx", "b.docx", "c.docx"):
        make(src / name)
    out = tmp_path / "out"
    interrupt_at(2)

    with pytest.raises(md_iator.BatchInterrupted) as exc:
        md_iator.batch_convert(src, out)

    assert exc.value.summary == md_iator.Summary(converted=1)
    assert (exc.value.summary.processed, exc.value.total) == (1, 3)
    assert md_files(out) == ["a.md"]
