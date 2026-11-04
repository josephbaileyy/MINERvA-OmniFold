"""ADDENDUM-A1 §3: gatesim2.py (the audit's simulator, unchanged) with the dry run's task list as coded ("nine", the
control's closure_nuwro added) or as bound at dd47f98e ("eight"). Run with cwd = a checkout's nd-unfolding,
PYTHONDONTWRITEBYTECODE=1:  python3 -B <this> nine|eight <gatesim2 args>."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, ".")
import estimator_stability_probe as probe  # noqa: E402

variant = sys.argv.pop(1)
if variant == "eight":
    probe.DRY_TASKS = tuple(t for t in probe.DRY_TASKS if t != probe.TRUTH_CONTROL_TASK)
elif variant != "nine":
    raise SystemExit(f"variant {variant!r}: nine or eight")
gs = Path(__file__).resolve().parent / "gatesim2.py"
sys.argv[0] = str(gs)
runpy.run_path(str(gs), run_name="__main__")
