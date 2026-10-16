import base64
import re
from pathlib import Path
from urllib.parse import unquote

import pypandoc
import pytest

import md_iator

IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def image_links(md: Path) -> list[str]:
    return [unquote(link) for link in IMAGE_LINK.findall(md.read_text(encoding="utf-8"))]


def dead_links(md: Path) -> list[str]:
    return [link for link in image_links(md) if not (md.parent / link).is_file()]


@pytest.mark.parametrize(
    "md_name, expected",
    [
        ("rapport.md", "rapport_media"),
        ("Mon rapport.md", "Mon_rapport_media"),
        ("Mon rapport (v2).md", "Mon_rapport_v2_media"),
        ("été 2026.md", "été_2026_media"),
        ("a.b-c.md", "a.b-c_media"),
        ("(( )).md", "document_media"),
    ],
)
def test_media_dir_name_is_link_safe(tmp_path, md_name, expected):
    assert md_iator.media_dir(tmp_path / md_name) == tmp_path / expected


def test_docx_images_go_next_to_md_with_working_links(engines, make, tmp_path):
    src = make(tmp_path / "src" / "Mon rapport (v2).docx", "texte IMAGE")
    out = tmp_path / "out"
    out.mkdir()

    dest = md_iator.convert_file(src, out)

    assert dest == out / "Mon rapport (v2).md"
    assert image_links(dest) == ["Mon_rapport_v2_media/media/image1.png"]
    assert dead_links(dest) == []
    assert sorted(p.name for p in out.iterdir()) == ["Mon rapport (v2).md", "Mon_rapport_v2_media"]


def test_docx_without_images_creates_no_media_dir(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx", "texte")

    md_iator.convert_file(src)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["rapport.docx", "rapport.md"]


def test_reconversion_keeps_user_files_in_media_dir(engines, make, tmp_path):
    src = make(tmp_path / "rapport.docx", "texte IMAGE")
    user_file = make(tmp_path / "rapport_media" / "notes.txt", "à garder")

    md_iator.convert_file(src)
    md_iator.convert_file(src)

    assert user_file.read_text(encoding="utf-8") == "à garder"
    assert dead_links(tmp_path / "rapport.md") == []


def test_failed_docx_conversion_leaves_no_media_dir(make, monkeypatch, tmp_path):
    src = make(tmp_path / "rapport.docx")

    def extract_then_fail(src, dest):
        image = md_iator.media_dir(dest) / "media" / "image1.png"
        image.parent.mkdir(parents=True)
        image.write_bytes(b"\x89PNG fake")
        raise RuntimeError("panne")

    monkeypatch.setattr(md_iator, "convert_docx", extract_then_fail)

    with pytest.raises(RuntimeError):
        md_iator.convert_file(src)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["rapport.docx"]


def test_batch_reports_images_folder_collision(engines, make, tmp_path, capsys):
    src = tmp_path / "src"
    make(src / "a b.docx", "IMAGE")
    make(src / "a_b.docx", "IMAGE")
    out = tmp_path / "out"

    assert md_iator.batch_convert(src, out) == md_iator.Summary(converted=1, errors=1)
    err = capsys.readouterr().err
    assert f"erreur : {src / 'a_b.docx'} — sortie {out / 'a_b_media'} déjà produite" in err


def _pandoc_available() -> bool:
    try:
        pypandoc.get_pandoc_version()
        return True
    except OSError:
        return False


@pytest.mark.skipif(not _pandoc_available(), reason="pandoc absent (pas de téléchargement en test)")
def test_real_pandoc_docx_image_links_resolve(tmp_path):
    (tmp_path / "pixel.png").write_bytes(PIXEL_PNG)
    src = tmp_path / "Mon rapport.docx"
    pypandoc.convert_text(
        "# Doc\n\n![logo](pixel.png)\n", "docx", format="md",
        outputfile=str(src), cworkdir=str(tmp_path),
    )
    out = tmp_path / "out"
    out.mkdir()

    dest = md_iator.convert_file(src, out)

    links = image_links(dest)
    assert len(links) == 1 and links[0].startswith("Mon_rapport_media/")
    assert dead_links(dest) == []
