import pytest

import md_iator


@pytest.fixture(autouse=True)
def fresh_pandoc_cache():
    md_iator._pandoc_problem.cache_clear()
    yield
    md_iator._pandoc_problem.cache_clear()


@pytest.fixture
def downloads(monkeypatch):
    """Simulate pandoc missing from PATH; record download attempts."""
    calls: list[int] = []

    def missing():
        raise OSError("pandoc absent")

    monkeypatch.setattr(md_iator.pypandoc, "get_pandoc_version", missing)
    return calls


def test_present_pandoc_is_not_downloaded(monkeypatch):
    monkeypatch.setattr(md_iator.pypandoc, "get_pandoc_version", lambda: "3.1")
    monkeypatch.setattr(
        md_iator.pypandoc, "download_pandoc", lambda **kw: pytest.fail("download")
    )

    md_iator.ensure_pandoc()


def test_missing_pandoc_is_downloaded_once(monkeypatch, downloads, capsys):
    monkeypatch.setattr(
        md_iator.pypandoc, "download_pandoc", lambda **kw: downloads.append(1)
    )

    md_iator.ensure_pandoc()
    md_iator.ensure_pandoc()

    assert downloads == [1]
    err = capsys.readouterr().err
    assert "pandoc introuvable — téléchargement en cours..." in err
    assert "pandoc installé." in err


def test_failed_download_raises_readable_error_once(monkeypatch, downloads):
    def offline(**kw):
        downloads.append(1)
        raise OSError("réseau injoignable")

    monkeypatch.setattr(md_iator.pypandoc, "download_pandoc", offline)

    for _ in range(2):
        with pytest.raises(md_iator.PandocUnavailableError, match="pandoc.org/installing"):
            md_iator.ensure_pandoc()

    assert downloads == [1]
