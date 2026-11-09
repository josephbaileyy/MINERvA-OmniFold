"""FD-PRR addendum A2: run prr_read.main on test_prr's EndToEnd fixture (test_planted_classes' plants), in a given
clone, writing readout.json and readout.txt to OUT. Used at M_A1 and at the A2 code commit, with PYTHONHASHSEED=0 (the
fixture's truths are seeded by hash((truth, seed))), so the two outputs can be compared byte for byte.
Usage: PYTHONHASHSEED=0 python3 -B fixture_read.py <clone> <out dir>
"""
import sys
from pathlib import Path

clone, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(clone / "nd-unfolding" / "prior_retention"))
import test_prr as TP  # noqa: E402  (it sets up the remaining import paths from its own location)

assert Path(TP.__file__).resolve().is_relative_to(clone), TP.__file__
t = TP.EndToEnd("test_planted_classes")
t.setUp()
try:
    plant = t.floor_plant()
    plant.update({("K50", "A7_gibuu"): 0.1, ("C1000", "A7_gibuu"): 0.40, ("O2", "q3"): 0.5, ("O3", "q3"): 0.1})
    ibu = {(5, "A7_gibuu"): 0.15, (200, "A7_gibuu"): 0.05, (5, "q3"): 0.3, (200, "q3"): 0.31}
    t.build(plant, ibu)
    rc = TP.RD.main(["--run", str(t.run), "--repo", str(clone), "--out", str(out)])
finally:
    t.tearDown()
sys.exit(rc)
