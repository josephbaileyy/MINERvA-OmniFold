"""Tests for check_sec4_receipts.py: the Sec. IV printed values match their receipts, and wrong values are rejected."""
from __future__ import annotations

import gzip
import importlib.util
import json
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


@pytest.mark.parametrize("name,old,new,label", [
    ("paper_body.tex", r"\SI{0.676}{\percent}", r"\SI{0.686}{\percent}", "statistical block median (Q_R, S1)"),
    # The rebuilt-band 2-sigma rescore (97.7%) binds in the note since r18 moved it there: $C_2=0.977$.
    ("sec_validation.tex", r"$C_2=0.977$", r"$C_2=0.967$",
     "rescoring against the rebuilt (VL170) band, 2 and 1 sigma (note sec:coverage)"),
    ("paper_body.tex", r"reduces it to below \SI{0.3}{\percent}", r"reduces it to below \SI{0.2}{\percent}",
     "negative-weight residual, highest-W cells (VL151)"),
    ("paper_body.tex", r"\SIrange{16}{31}{\percent}", r"\SIrange{16}{33}{\percent}",
     "other fixed shapes, most affected cell (VL154)"),
    ("paper_body.tex", r"reduces it to below \SI{0.3}{\percent}", r"reduces it to below \SI{0.9}{\percent}",  # true but loose
     "negative-weight residual, highest-W cells (VL151)"),
])
@needs_receipts
def test_a_wrong_printed_value_fails(name, old, new, label):
    src = chk.load()
    # The checker's own reading: comments stripped, then whitespace collapsed. Collapsing first would let the first
    # % comment swallow the rest of the file, and every case would fail for that reason alone.
    src[name] = chk.text(name, src)
    assert all(good for _, good, _ in chk.evaluate(src)), "control: the unperturbed sources must pass"
    assert src[name].count(old) == 1
    src[name] = src[name].replace(old, new)
    rows = dict((lab, good) for lab, good, _ in chk.evaluate(src))
    assert rows[label] is False
    assert sum(not good for good in rows.values()) == 1, "only the perturbed value's check fails"


PHRASE = r"differ\s+by\s+at\s+most"  # the printed phrase, across any line wrap


@needs_receipts
def test_a_missing_value_fails():
    src = chk.load()
    # The phrase may wrap across a source line (it does since register round r12), so match any whitespace.
    src["paper_body.tex"] = re.sub(PHRASE + r"\s+\\SI\{1\.4\}", "differ by a little", src["paper_body.tex"])
    rows = dict((label, good) for label, good, _ in chk.evaluate(src))
    assert rows["treatments on data (VL152)"] is False


@needs_receipts
def test_a_value_kept_only_in_a_latex_comment_is_not_found():
    src = chk.load()
    assert len(re.findall(PHRASE, src["paper_body.tex"])) == 1
    src["paper_body.tex"] = re.sub(PHRASE, "\n% differ by at most", src["paper_body.tex"])
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
    original["paper_body.tex"] = re.sub(PHRASE, "differ by roughly", original["paper_body.tex"])
    monkeypatch.setattr(chk, "load", lambda: dict(original))
    assert chk.self_test() == 1
    assert "NOT FOUND   treatments on data (VL152)" in capsys.readouterr().out


def test_a_gzip_receipt_reads_by_suffix(tmp_path, monkeypatch):
    """Q9: the Stage F budget is committed gzipped; receipt() must read it as its plain twin, and fail if absent."""
    payload = {"Q": {"median_pct": 6.4479}, "stat": {"median_pct": 0.6843}}
    (tmp_path / "b.json").write_text(json.dumps(payload))
    with gzip.open(tmp_path / "b.json.gz", "wt", encoding="utf-8") as fh:
        json.dump(payload, fh)
    monkeypatch.setattr(chk, "STATE", tmp_path)
    assert chk.receipt("b.json.gz") == chk.receipt("b.json") == payload
    with pytest.raises(FileNotFoundError):
        chk.receipt("missing.json.gz")


@needs_receipts
def test_the_q_bindings_read_the_committed_budget():
    # Q_R (RE-2 part C, partc-r2/outA/budget_Q.json, bbe13622...): Q.median_pct 6.41367, stat.median_pct 0.676376,
    # Q.integral_sigma_pct 4.75917 (Q, before: 6.4479, 0.6843, 4.7550)
    assert chk.BUDGET_Q.endswith("partc-r2/outA/budget_Q.json.gz")
    assert abs(chk.total_median() - 6.4137) < 1e-4 and abs(chk.stat_median() - 0.6764) < 1e-4
    assert abs(chk.total_integral() - 4.7592) < 1e-4


@needs_receipts
def test_a_wrong_integral_macro_fails():
    src = chk.load()
    assert src["values.tex"].count(r"\newcommand{\uqIntegral}{4.76}") == 1
    src["values.tex"] = src["values.tex"].replace(r"\newcommand{\uqIntegral}{4.76}", r"\newcommand{\uqIntegral}{4.75}")
    rows = dict((label, good) for label, good, _ in chk.evaluate(src))
    assert rows["total integral uncertainty (Q_R)"] is False
