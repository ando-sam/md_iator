"""Cleanup of the pandoc tree of a DOCX: Word table of contents, empty headings.

Blocks are built in the shape pandoc's JSON gives for a real Word document.
"""

import md_iator

SPACE = {"t": "Space"}


def words(text: str) -> list[dict]:
    inlines: list[dict] = []
    for word in text.split():
        if inlines:
            inlines.append(SPACE)
        inlines.append({"t": "Str", "c": word})
    return inlines


def header(level: int, text: str, classes: tuple[str, ...] = ()) -> dict:
    return {"t": "Header", "c": [level, ["", list(classes), []], words(text)]}


def para(*inlines: dict) -> dict:
    return {"t": "Para", "c": list(inlines)}


def link(text: str, target: str, *nested: dict) -> dict:
    return {"t": "Link", "c": [["", [], []], words(text) + list(nested), [target, ""]]}


def toc_entry(title: str, anchor: str, page: int) -> dict:
    # Word puts the page number in a link nested in the entry's link.
    return para(link(title, anchor, SPACE, link(str(page), anchor)))


def test_word_table_of_contents_is_removed():
    blocks = [
        para(*words("AKANJO S.A.")),
        header(1, "TABLE DES MATIERES", ("TOC-Heading",)),
        toc_entry("1. CONTEXTE", "#contexte", 2),
        toc_entry("2. BESOIN", "#besoin", 3),
        header(1, "1. CONTEXTE"),
        para(*words("Texte.")),
    ]

    assert md_iator.clean_docx_blocks(blocks) == [blocks[0], blocks[4], blocks[5]]


def test_toc_removal_stops_at_first_block_that_is_not_an_entry():
    intro = para(*words("Ce document décrit le besoin."))
    blocks = [
        header(1, "Sommaire", ("TOC-Heading",)),
        toc_entry("Contexte", "#contexte", 2),
        intro,
        para(link("Contexte", "#contexte")),
    ]

    assert md_iator.clean_docx_blocks(blocks) == [intro, blocks[3]]


def test_internal_links_outside_the_table_of_contents_are_kept():
    blocks = [header(1, "Annexe"), para(link("voir le contexte", "#contexte"))]

    assert md_iator.clean_docx_blocks(blocks) == blocks


def test_entry_with_external_link_is_not_part_of_the_table_of_contents():
    external = para(link("Odoo", "https://www.odoo.com"))
    blocks = [header(1, "Sommaire", ("TOC-Heading",)), external]

    assert md_iator.clean_docx_blocks(blocks) == [external]


def bold(text: str) -> dict:
    return para({"t": "Strong", "c": words(text)})


def test_toc_titled_by_bold_paragraph_after_empty_toc_heading_is_removed():
    # Word left the "TOC Heading" title empty; the author typed it in bold.
    blocks = [
        {"t": "Header", "c": [1, ["section", ["TOC-Heading"], []], []]},
        bold("TABLE DES MATIERES"),
        toc_entry("1. Objet du document", "#objet-du-document", 1),
        toc_entry("2. Positionnement", "#positionnement", 1),
        header(1, "1. Objet du document"),
    ]

    assert md_iator.clean_docx_blocks(blocks) == [blocks[4]]


def test_word_toc_without_toc_heading_is_recognised_by_its_page_links():
    blocks = [
        bold("Sommaire"),
        toc_entry("1. Contexte", "#contexte", 2),
        header(1, "1. Contexte"),
    ]

    assert md_iator.clean_docx_blocks(blocks) == [blocks[2]]


def test_bold_paragraph_before_plain_internal_links_is_kept():
    # No "TOC Heading" title and no page numbers: not a table of contents.
    blocks = [bold("Voir aussi"), para(link("Contexte", "#contexte"))]

    assert md_iator.clean_docx_blocks(blocks) == blocks


def test_empty_headings_are_removed():
    image = para({"t": "Image", "c": [["", [], []], [], ["a_media/media/image1.png", ""]]})
    blocks = [
        header(3, "03 Mise au point"),
        image,
        {"t": "Header", "c": [3, ["section", [], []], []]},
        {"t": "Header", "c": [3, ["section-1", [], []], [SPACE]]},
        header(3, "04 Besoins"),
    ]

    assert md_iator.clean_docx_blocks(blocks) == [blocks[0], image, blocks[4]]


def test_heading_holding_only_an_image_is_kept():
    image = {"t": "Image", "c": [["", [], []], [], ["a_media/media/image1.png", ""]]}
    blocks = [{"t": "Header", "c": [3, ["", [], []], [image]]}]

    assert md_iator.clean_docx_blocks(blocks) == blocks


def test_docx_conversion_drops_the_table_of_contents(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx", "Titre TOC")

    text = md_iator.convert_file(src).read_text(encoding="utf-8")

    assert text == "# Titre TOC\n"
