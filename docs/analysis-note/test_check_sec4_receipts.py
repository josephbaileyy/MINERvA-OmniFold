"""Tests for check_sec4_receipts.py: the Sec. IV printed values match their receipts, and wrong values are rejected."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("check_sec4_receipts", HERE / "check_sec4_receipts.py")
chk = importlib.util.module_from_spec(spec)
sys.modules["check_sec4_receipts"] = chk
spec.loader.exec_module(chk)

pytestmark = pytest.mark.skipif(not chk.STATE.is_dir(), reason="receipts exist only in the canonical repository")


def test_current_sources_pass():
    rows = chk.evaluate(chk.load())
    assert rows and all(good for _, good, _ in rows), [r for r in rows if not r[1]]


def test_self_test_rejects_every_perturbation():
    assert chk.self_test() == 0


@pytest.mark.parametrize("old,new", [
    (r"\SI{0.674}{\percent}", r"\SI{0.664}{\percent}"),
    (r"\SI{97.7}{\percent}", r"\SI{96.7}{\percent}"),
    (r"reduces it to below \SI{0.3}{\percent}", r"reduces it to below \SI{0.2}{\percent}"),
    (r"\SIrange{16}{31}{\percent}", r"\SIrange{16}{33}{\percent}"),
])
def test_a_wrong_printed_value_fails(old, new):
    src = chk.load()
    src["paper_body.tex"] = re.sub(r"\s+", " ", src["paper_body.tex"])  # the checker matches whitespace-normalized text
    assert src["paper_body.tex"].count(old) == 1
    src["paper_body.tex"] = src["paper_body.tex"].replace(old, new)
    assert not all(good for _, good, _ in chk.evaluate(src))


def test_a_missing_value_fails():
    src = chk.load()
    src["paper_body.tex"] = re.sub(r"differ by at most \\SI\{1\.4\}", "differ by a little", src["paper_body.tex"])
    rows = dict((label, good) for label, good, _ in chk.evaluate(src))
    assert rows["treatments on data (VL152)"] is False
