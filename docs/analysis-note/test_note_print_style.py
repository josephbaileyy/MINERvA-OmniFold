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
