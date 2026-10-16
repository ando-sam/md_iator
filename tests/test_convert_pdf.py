import md_iator


def test_pdf_one_section_per_page_with_separator(engines, make, tmp_path):
    src = make(tmp_path / "doc.pdf", "un\fdeux")
    dest = tmp_path / "doc.md"

    md_iator.convert_pdf(src, dest)

    assert dest.read_text(encoding="utf-8") == (
        "## Page 1\n\nun\n\n---\n\n## Page 2\n\ndeux"
    )


def test_pdf_page_without_text_gives_empty_section(engines, make, tmp_path):
    src = make(tmp_path / "scan.pdf", "\f  texte  ")
    dest = tmp_path / "scan.md"

    md_iator.convert_pdf(src, dest)

    assert dest.read_text(encoding="utf-8") == (
        "## Page 1\n\n\n\n---\n\n## Page 2\n\ntexte"
    )
