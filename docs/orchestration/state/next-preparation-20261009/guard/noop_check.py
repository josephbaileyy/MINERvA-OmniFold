"""On the canonical checkout, each derived import root equals the literal it replaced (pure paths)."""
from pathlib import PurePosixPath as P
C = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))
toy = P(C) / "2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py"
ki = P(C) / "2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py"
cases = {"fixed_truth_toy OMNIFOLD_PY": (str(toy.parent.parents[2] / "unbinned_unfolding" / "python"),
                                         C + "/unbinned_unfolding/python"),
         "ki85_compare UQ": (str(ki.parent.parent), C + "/2d-unfolding/uq")}
for k, (derived, literal) in cases.items():
    print(f"{k}: derived == replaced literal: {derived == literal}")
assert all(a == b for a, b in cases.values())
