"""freeze_checks.py check 5 (FONTS): a figure's sans font fails outside the allowed figures' pages; TeX's own sans (the
\\mathsf T of a transpose, CMSS8) and monospace are listed, not failed (the director's ruling of 2026-11-28,
note-figfonts-20261128). pdffonts, pdfinfo and the aux are replaced by stubs, so no PDF is built."""
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("freeze_checks", HERE / "freeze_checks.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)


def run(monkeypatch, pages, labels=None, allowed=()):
    """pages: {page: [pdffonts names]}; labels: {label: page} as the aux would give them."""
    monkeypatch.setattr(fc, "SANS_ALLOWED", tuple(allowed))
    monkeypatch.setattr(fc, "aux_pages", lambda aux: dict(labels or {}))
    monkeypatch.setattr(fc, "pdf_pages", lambda pdf: max(pages))
    monkeypatch.setattr(fc, "page_fonts", lambda pdf, p: list(pages.get(p, [])))
    return fc.check_fonts(Path("new.pdf"), Path("new.aux"))


def test_sans_allowed_is_empty():
    assert fc.SANS_ALLOWED == ()


@pytest.mark.parametrize("font", ["BMQQDV+DejaVuSans", "GCWXDV+DejaVuSans-Oblique", "AAAAAA+Arial-BoldMT",
                                  "BBBBBB+Helvetica", "CCCCCC+LiberationSans", "DDDDDD+Cmss10"])
def test_a_figure_sans_font_fails(monkeypatch, font):
    ok, lines = run(monkeypatch, {1: ["XX+SFRM1000"], 2: ["YY+DejaVuSerif", font]}, {"fig:x": 2})
    assert not ok
    assert any(l.startswith("  sans on p.2") and font.split("+")[1] in l and "fig:x" in l for l in lines)
    assert lines[-1].startswith("FONTS :: FAIL (1 page(s)")


def test_a_figure_sans_font_passes_on_an_allowed_figures_page(monkeypatch):
    ok, lines = run(monkeypatch, {3: ["BMQQDV+DejaVuSans"]}, {"fig:x": 3}, allowed=["fig:x"])
    assert ok and lines[-1].startswith("FONTS :: PASS")


@pytest.mark.parametrize("font", ["KQZBXW+CMSS8", "ABCDEF+CMSS10", "QWERTY+SFSS1000"])
def test_tex_sans_on_a_text_page_is_listed_and_passes(monkeypatch, font):
    ok, lines = run(monkeypatch, {1: ["XX+SFRM1000"], 2: ["XX+SFRM1000", font, "ZZ+CMMI10"]})
    assert ok and lines[-1].startswith("FONTS :: PASS")
    name = font.split("+")[1]
    assert any("TeX sans, not a figure font" in l and f"p.2 {name}" in l for l in lines)
    assert not any(l.startswith("  sans on") for l in lines)


def test_monospace_is_listed_and_passes(monkeypatch):
    ok, lines = run(monkeypatch, {1: ["AA+SFTT1000", "BB+DejaVuSansMono"]})
    assert ok and any("monospace: p.1" in l for l in lines)


def test_an_allowed_label_missing_from_the_aux_fails(monkeypatch):
    ok, lines = run(monkeypatch, {1: ["XX+SFRM1000"]}, {}, allowed=["fig:gone"])
    assert not ok and any("not in the aux" in l for l in lines)
