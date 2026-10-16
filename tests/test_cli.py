import sys
from importlib import metadata

import pytest

import md_iator
from md_iator import cli


@pytest.fixture(autouse=True)
def _no_pandoc_download(pandoc_checks):
    return pandoc_checks


def run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["md_iator", *map(str, args)])
    cli.main()


def exit_code(monkeypatch, *args):
    with pytest.raises(SystemExit) as exc:
        run(monkeypatch, *args)
    return exc.value.code


def test_cli_single_file_succeeds(engines, make, tmp_path, monkeypatch, capsys):
    src = make(tmp_path / "rapport.docx")

    run(monkeypatch, src)

    assert capsys.readouterr().out == f"converti : {tmp_path / 'rapport.md'}\n"


def test_cli_single_file_error_exits_1(engines, make, tmp_path, monkeypatch, capsys):
    src = make(tmp_path / "rapport.docx", corrupt=True)

    assert exit_code(monkeypatch, src) == 1
    assert capsys.readouterr().err == "erreur : fichier illisible\n"


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


def test_cli_docx_conversion_checks_pandoc(
    engines, make, tmp_path, monkeypatch, pandoc_checks
):
    src = tmp_path / "src"
    make(src / "a.docx")

    exit_code(monkeypatch, src, "-o", tmp_path / "out")

    assert pandoc_checks


def test_cli_pdf_only_batch_does_not_check_pandoc(
    engines, make, tmp_path, monkeypatch, pandoc_checks
):
    src = tmp_path / "src"
    make(src / "a.pdf")

    assert exit_code(monkeypatch, src, "-o", tmp_path / "out") == 0
    assert pandoc_checks == []


def test_cli_skipped_docx_does_not_check_pandoc(
    engines, make, tmp_path, monkeypatch, pandoc_checks
):
    src = tmp_path / "src"
    make(src / "a.docx")
    out = tmp_path / "out"
    make(out / "a.md", "déjà converti")

    assert exit_code(monkeypatch, src, "-o", out, "--skip-existing") == 0
    assert pandoc_checks == []


def _pandoc_offline(monkeypatch):
    def unavailable():
        raise md_iator.PandocUnavailableError("pandoc introuvable (simulé)")

    monkeypatch.setattr(md_iator, "ensure_pandoc", unavailable)


def test_cli_single_docx_offline_exits_1_without_traceback(
    engines, make, tmp_path, monkeypatch, capsys
):
    src = make(tmp_path / "rapport.docx")
    _pandoc_offline(monkeypatch)

    assert exit_code(monkeypatch, src) == 1
    assert capsys.readouterr().err == "erreur : pandoc introuvable (simulé)\n"


def test_cli_batch_offline_still_converts_pdfs(
    engines, make, tmp_path, monkeypatch, capsys
):
    src = tmp_path / "src"
    make(src / "a.docx")
    make(src / "b.pdf")
    _pandoc_offline(monkeypatch)

    assert exit_code(monkeypatch, src, "-o", tmp_path / "out") == 1
    captured = capsys.readouterr()
    assert captured.out.endswith("\n1 converti · 1 erreur\n")
    assert f"erreur : {src / 'a.docx'} — pandoc introuvable (simulé)" in captured.err
    assert "fichier/s" not in captured.err  # no progress bar outside a terminal


def test_cli_version(monkeypatch, capsys):
    assert exit_code(monkeypatch, "--version") == 0
    assert capsys.readouterr().out == f"md-iator {metadata.version('md-iator')}\n"


def test_cli_usage_uses_installed_command_name(monkeypatch, capsys):
    assert exit_code(monkeypatch, "--help") == 0
    assert capsys.readouterr().out.startswith("usage: md-iator ")


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
    assert cli.format_summary(summary) == expected


def test_cli_single_skip_existing_keeps_file(engines, make, tmp_path, monkeypatch, capsys):
    src = make(tmp_path / "rapport.docx")
    existing = make(tmp_path / "rapport.md", "écrit à la main")

    run(monkeypatch, src, "--skip-existing")

    assert capsys.readouterr().err == f"ignoré : {existing} existe déjà\n"
    assert existing.read_text(encoding="utf-8") == "écrit à la main"


def test_cli_batch_summary_counts_skipped(engines, make, tmp_path, monkeypatch, capsys):
    src = tmp_path / "src"
    make(src / "a.docx")
    make(src / "b.docx")
    out = tmp_path / "out"
    make(out / "a.md", "déjà converti")

    assert exit_code(monkeypatch, src, "-o", out, "--skip-existing") == 0
    assert capsys.readouterr().out.endswith("\n1 converti · 1 ignoré\n")


def test_cli_batch_interrupt_exits_130_with_resume_hint(
    engines, make, tmp_path, monkeypatch, capsys, interrupt_at
):
    src = tmp_path / "src"
    for name in ("a.docx", "b.docx", "c.docx"):
        make(src / name)
    interrupt_at(2)

    assert exit_code(monkeypatch, src, "-o", tmp_path / "out") == 130
    captured = capsys.readouterr()
    assert captured.out.endswith("\n1 converti\n")
    assert captured.err.endswith(
        "interrompu — 1/3 fichiers traités, aucun fichier partiel. "
        "Relancer avec --skip-existing pour reprendre.\n"
    )


def test_cli_single_interrupt_exits_130(engines, make, tmp_path, monkeypatch, capsys, interrupt_at):
    src = make(tmp_path / "rapport.docx")
    interrupt_at(1)

    assert exit_code(monkeypatch, src) == 130
    assert capsys.readouterr().err == "\ninterrompu — aucun fichier partiel.\n"
    assert not (tmp_path / "rapport.md").exists()


def test_cli_resume_after_interrupt_converts_only_the_rest(
    engines, make, tmp_path, monkeypatch, capsys, interrupt_at
):
    src = tmp_path / "src"
    for name in ("a.docx", "b.docx", "c.docx"):
        make(src / name)
    out = tmp_path / "out"
    interrupt_at(2)  # only the 2nd call is interrupted; later ones go through
    assert exit_code(monkeypatch, src, "-o", out) == 130
    capsys.readouterr()

    assert exit_code(monkeypatch, src, "-o", out, "--skip-existing") == 0
    assert capsys.readouterr().out.endswith("\n2 convertis · 1 ignoré\n")


def test_cli_help_is_in_french(monkeypatch, capsys):
    assert exit_code(monkeypatch, "--help") == 0
    out = capsys.readouterr().out
    assert "[-o SORTIE] [--skip-existing] SOURCE" in out
    assert "afficher cette aide et quitter" in out
