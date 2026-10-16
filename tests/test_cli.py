import sys

import pytest

import main
import md_iator


@pytest.fixture(autouse=True)
def _no_pandoc_download(pandoc_checks):
    return pandoc_checks


def run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["md_iator", *map(str, args)])
    main.main()


def exit_code(monkeypatch, *args):
    with pytest.raises(SystemExit) as exc:
        run(monkeypatch, *args)
    return exc.value.code


def test_cli_single_file_succeeds(engines, make, tmp_path, monkeypatch, capsys):
    src = make(tmp_path / "rapport.docx")

    run(monkeypatch, src)

    assert capsys.readouterr().out == f"converted: {tmp_path / 'rapport.md'}\n"


def test_cli_single_file_error_exits_1(engines, make, tmp_path, monkeypatch, capsys):
    src = make(tmp_path / "rapport.docx", corrupt=True)

    assert exit_code(monkeypatch, src) == 1
    assert capsys.readouterr().err == "error: fichier illisible\n"


def test_cli_batch_exits_0_when_all_succeed(engines, make, tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    make(src / "a.docx")
    make(src / "b.pdf")

    assert exit_code(monkeypatch, src, "-o", tmp_path / "out") == 0
    assert capsys.readouterr().out.endswith("\n2 convertis\n")


def test_cli_batch_exits_1_when_any_fails(engines, make, tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    make(src / "a.docx", corrupt=True)
    make(src / "b.pdf")

    assert exit_code(monkeypatch, src, "-o", tmp_path / "out") == 1
    assert capsys.readouterr().out.endswith("\n1 converti · 1 erreur\n")


def test_cli_missing_path_exits_2_without_pandoc_check(
    tmp_path, monkeypatch, capsys, pandoc_checks
):
    assert exit_code(monkeypatch, tmp_path / "absent.pdf") == 2
    assert "chemin introuvable" in capsys.readouterr().err
    assert pandoc_checks == []


def test_cli_help_does_not_check_pandoc(monkeypatch, pandoc_checks):
    assert exit_code(monkeypatch, "--help") == 0
    assert pandoc_checks == []


def test_cli_checks_pandoc_once_before_converting(
    engines, make, tmp_path, monkeypatch, pandoc_checks
):
    src = tmp_path / "src"
    make(src / "a.docx")
    make(src / "b.docx")

    exit_code(monkeypatch, src, "-o", tmp_path / "out")

    assert pandoc_checks == [1]


def test_cli_output_trailing_slash_creates_directory(engines, make, tmp_path, monkeypatch):
    src = make(tmp_path / "rapport.pdf")
    out = tmp_path / "sortie"

    run(monkeypatch, src, "-o", f"{out}/")

    assert (out / "rapport.md").is_file()


def test_cli_output_without_slash_is_file_name(engines, make, tmp_path, monkeypatch):
    src = make(tmp_path / "rapport.pdf")
    out = tmp_path / "sortie"

    run(monkeypatch, src, "-o", out)

    assert out.is_file()


def test_cli_single_empty_pdf_exits_0_without_file(engines, make, tmp_path, monkeypatch, capsys):
    src = make(tmp_path / "scan.pdf", "\f")

    run(monkeypatch, src)

    assert capsys.readouterr().err.endswith(
        f"vide : {src} — aucun texte extrait (PDF scanné ? passer par ocrmypdf)\n"
    )
    assert not (tmp_path / "scan.md").exists()


def test_cli_batch_empty_pdf_is_not_an_error(engines, make, tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    make(src / "scan.pdf", "\f")

    assert exit_code(monkeypatch, src, "-o", tmp_path / "out") == 0
    assert capsys.readouterr().out.endswith("\n0 converti · 1 vide\n")


def test_cli_folder_without_sources(engines, tmp_path, monkeypatch, capsys):
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")

    assert exit_code(monkeypatch, tmp_path) == 0
    assert capsys.readouterr().out == f"aucun fichier .docx ou .pdf dans {tmp_path}\n"


@pytest.mark.parametrize(
    "summary, expected",
    [
        (md_iator.Summary(converted=1), "1 converti"),
        (md_iator.Summary(converted=2, empty=3, errors=2), "2 convertis · 3 vides · 2 erreurs"),
        (md_iator.Summary(errors=1), "0 converti · 1 erreur"),
    ],
)
def test_format_summary_plural_and_omits_zero(summary, expected):
    assert main.format_summary(summary) == expected
