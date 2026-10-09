"""Tests for check_sec4_receipts.py: the Sec. IV printed values match their receipts, and wrong values are rejected."""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_sec4_receipts", HERE / "check_sec4_receipts.py")
chk = importlib.util.module_from_spec(spec)
sys.modules["check_sec4_receipts"] = chk
spec.loader.exec_module(chk)

needs_receipts = pytest.mark.skipif(not chk.STATE.is_dir(), reason="receipts exist only in the canonical repository")


@needs_receipts
def test_current_sources_pass():
    rows = chk.evaluate(chk.load())
    assert rows and all(good for _, good, _ in rows), [r for r in rows if not r[1]]


@needs_receipts
def test_self_test_rejects_every_perturbation():
    assert chk.self_test() == 0


@pytest.mark.parametrize("old,new", [
    (r"\SI{0.674}{\percent}", r"\SI{0.664}{\percent}"),
    (r"\SI{97.7}{\percent}", r"\SI{96.7}{\percent}"),
    (r"reduces it to below \SI{0.3}{\percent}", r"reduces it to below \SI{0.2}{\percent}"),
    (r"\SIrange{16}{31}{\percent}", r"\SIrange{16}{33}{\percent}"),
    (r"reduces it to below \SI{0.3}{\percent}", r"reduces it to below \SI{0.9}{\percent}"),  # true but loose
])
@needs_receipts
def test_a_wrong_printed_value_fails(old, new):
    src = chk.load()
    src["paper_body.tex"] = re.sub(r"\s+", " ", src["paper_body.tex"])  # the checker matches whitespace-normalized text
    assert src["paper_body.tex"].count(old) == 1
    src["paper_body.tex"] = src["paper_body.tex"].replace(old, new)
    assert not all(good for _, good, _ in chk.evaluate(src))


@needs_receipts
def test_a_missing_value_fails():
    src = chk.load()
    src["paper_body.tex"] = re.sub(r"differ by at most \\SI\{1\.4\}", "differ by a little", src["paper_body.tex"])
    rows = dict((label, good) for label, good, _ in chk.evaluate(src))
    assert rows["treatments on data (VL152)"] is False


@needs_receipts
def test_a_value_kept_only_in_a_latex_comment_is_not_found():
    src = chk.load()
    assert src["paper_body.tex"].count("differ by at most") == 1
    src["paper_body.tex"] = src["paper_body.tex"].replace("differ by at most", "\n% differ by at most")
    rows = dict((label, good) for label, good, _ in chk.evaluate(src))
    assert rows["treatments on data (VL152)"] is False


def test_an_escaped_percent_is_not_a_comment():
    assert chk.text("x", {"x": "a 50\\% b % gone\nc"}) == "a 50\\% b c"


def _run_copy(rel: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:  # removed afterwards
        dest = Path(tmp) / rel
        dest.mkdir(parents=True)
        shutil.copy(HERE / "check_sec4_receipts.py", dest)
        return subprocess.run([sys.executable, "check_sec4_receipts.py"], cwd=dest, capture_output=True, text=True)


def test_the_canonical_layout_without_receipts_fails():
    proc = _run_copy("repo/docs/analysis-note")
    assert proc.returncode == 1 and "SEC4-RECEIPTS :: FAIL" in proc.stdout, proc.stdout


def test_a_standalone_layout_skips():
    proc = _run_copy("MINERvA-OmniFold-Analysis-Note")
    assert proc.returncode == 0 and "SEC4-RECEIPTS :: SKIP" in proc.stdout, proc.stdout


@needs_receipts
def test_the_self_test_fails_cleanly_when_a_printed_value_is_missing(monkeypatch, capsys):
    """Review cycle 2: it crashed (AttributeError) on a missing value; it must report it and fail."""
    original = chk.load()
    original["paper_body.tex"] = original["paper_body.tex"].replace("differ by at most", "differ by roughly")
    monkeypatch.setattr(chk, "load", lambda: dict(original))
    assert chk.self_test() == 1
    assert "NOT FOUND   treatments on data (VL152)" in capsys.readouterr().out
