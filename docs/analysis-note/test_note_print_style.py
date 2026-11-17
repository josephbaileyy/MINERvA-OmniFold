"""note_print_style.py: the paper's figure rcParams, opt-in and without side effects (director, 2026-11-13)."""
import ast
import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
nps = importlib.import_module("note_print_style")

# The paper's values as recorded: docs/analysis-note/figures/methods_short/make_figures.py:287-289 on
# draft/methods-short-20261109 at a871379960f2 (PR #977).
RECORDED_PAPER_RC = {"font.family": "serif", "mathtext.fontset": "cm", "font.size": 8.5,
                     "axes.labelsize": 9.3, "xtick.labelsize": 8.3, "ytick.labelsize": 8.3,
                     "axes.linewidth": .6, "pdf.fonttype": 42}
PAPER_PRODUCER = ROOT / "docs/analysis-note/figures/methods_short/make_figures.py"


def test_paper_values_as_recorded():
    assert nps.PAPER_RC == RECORDED_PAPER_RC
    assert nps.PRINT_RC == dict(RECORDED_PAPER_RC, **{"font.serif": ["DejaVu Serif"]})


def test_paper_values_against_the_paper_producer_when_present():
    """Once #977 is on this branch, its producer's rcParams literal must equal PAPER_RC."""
    if not PAPER_PRODUCER.exists():
        return
    tree = ast.parse(PAPER_PRODUCER.read_text())
    found = [ast.literal_eval(n.args[0]) for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "update"
             and getattr(getattr(n.func, "value", None), "attr", "") == "rcParams" and n.args
             and isinstance(n.args[0], ast.Dict)]
    assert nps.PAPER_RC in found, f"the paper's rcParams changed: {found}"


def test_import_has_no_side_effects():
    code = ("import matplotlib as mpl, matplotlib.axes as ma; before = dict(mpl.rcParams); t = ma.Axes.set_title;"
            "import note_print_style; assert dict(mpl.rcParams) == before; assert ma.Axes.set_title is t; print('ok')")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout.strip() == "ok", r.stderr


def test_apply_and_figsize():
    import matplotlib as mpl
    saved = dict(mpl.rcParams)
    try:
        nps.apply()
        for k, v in nps.PRINT_RC.items():
            assert mpl.rcParams[k] == mpl.RcParams({k: v})[k], k   # rcParams validates (font.family becomes a list)
    finally:
        mpl.rcParams.update(saved)
    assert nps.figsize(1.0, 0.5) == (6.5, 3.25)
    w, h = nps.figsize(0.49, 1.0)
    assert abs(w - 3.185) < 1e-12 and abs(h - 3.185) < 1e-12


def test_group_r_print_font_is_the_papers_fonts():
    """restyle_2026_10.PRINT_FONT (group R's font-only pass) is exactly the font keys of PRINT_RC."""
    sys.path.insert(0, str(ROOT / "2d-unfolding"))
    rs = importlib.import_module("restyle_2026_10")
    assert rs.PRINT_FONT == {k: nps.PRINT_RC[k] for k in ("font.family", "font.serif", "mathtext.fontset")}


def test_group_r_print_font_is_opt_in():
    """Without --print-font, on() changes no rcParams; with it, only PRINT_FONT's keys change, and only under --style."""
    code = ("import sys, argparse, matplotlib as mpl; sys.path.insert(0, sys.argv[1]); import restyle_2026_10 as rs;"
            "ap = argparse.ArgumentParser(); rs.add_option(ap); before = dict(mpl.rcParams);"
            "assert rs.on(ap.parse_args(['--style', rs.STYLE])) and dict(mpl.rcParams) == before;"
            "assert not rs.on(ap.parse_args(['--print-font'])) and dict(mpl.rcParams) == before;"
            "assert rs.on(ap.parse_args(['--style', rs.STYLE, '--print-font']));"
            "changed = {k for k in before if mpl.rcParams[k] != before[k]};"
            "assert changed <= set(rs.PRINT_FONT), changed;"
            "want = mpl.RcParams(rs.PRINT_FONT); assert all(mpl.rcParams[k] == want[k] for k in want); print('ok')")
    out = subprocess.run([sys.executable, "-c", code, str(ROOT / "2d-unfolding")], capture_output=True, text=True)
    assert out.returncode == 0 and out.stdout.strip() == "ok", out.stderr
