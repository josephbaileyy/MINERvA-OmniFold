"""L-row G1 (referee6 major 3): Clopper-Pearson 95 % intervals on the observed coverage fractions of the 2D coverage
test (COV2D) at AR23 and G18, from the committed score and null files, and the same interval's form for LL5D's grade
(300 toys per truth, 16 cells). Read-only; no job. Run from the repository root: python3 -I <this file>.

Definitions, as the scorer counts (nd-unfolding/fd_1b_mc.py grade): a cell's count is #{toys with |e_c| <= sigma_c}
of 300; the joint count is #{toys with chi2 <= the null's chi2_cut}. The null contents p_cell and q_joint are the
graded test's own expected fractions (null_<T>.json "null"). Each interval here is a two-sided 95 % Clopper-Pearson
interval for ONE fraction; they are not simultaneous, and they are not the test's flag rule (Bonferroni 0.025/205
per cell and 0.025 joint, one-sided, at the null content minus 3 MC standard errors, fd_1b_null.thresholds)."""
import hashlib
import json
from pathlib import Path

from scipy.stats import beta

R = Path("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/readout")
N = 300


def cp(k, n, level=0.95):
    a = 1 - level
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


out = {"schema": "lrows-g1-cp/1", "level": 0.95, "method": "Clopper-Pearson, two-sided, per fraction", "tunes": {}}
for t in ("AR23", "G18"):
    sp, np_ = R / t / f"score_{t}.json", R / t / f"null_{t}.json"
    s, nl = json.loads(sp.read_text()), json.loads(np_.read_text())
    g, null = s["grade"], nl["null"]
    assert len(g["counts"]) == 205 and len(null["p_cell"]) == 205
    lo, hi = cp(g["joint_count"], N)
    cells = []
    for i, (k, p) in enumerate(zip(g["counts"], null["p_cell"])):
        a, b = cp(int(k), N)
        cells.append({"i": i, "count": int(k), "frac": k / N, "cp95": [a, b], "p_null": float(p),
                      "null_vs_cp": "above" if p > b else "below" if p < a else "inside", "flagged": g["cell_flag"][i]})
    n_above = sum(c["null_vs_cp"] == "above" for c in cells)
    n_below = sum(c["null_vs_cp"] == "below" for c in cells)
    out["tunes"][t] = {
        "score_sha256": hashlib.sha256(sp.read_bytes()).hexdigest(), "null_sha256": hashlib.sha256(np_.read_bytes()).hexdigest(),
        "verdict": g["verdict"], "ndf": g["ndf"],
        "joint": {"count": g["joint_count"], "of": N, "frac": g["joint_count"] / N, "cp95": [lo, hi],
                  "q_null": float(null["q_joint"]), "k_joint": g["k_joint"]},
        "cells": {"n": 205, "null_content_above_cp95": n_above, "null_content_below_cp95": n_below,
                  "null_content_inside_cp95": 205 - n_above - n_below,
                  "flagged": [c for c in cells if c["flagged"]],
                  "min_frac": min(cells, key=lambda c: c["frac"]), "per_cell": cells},
    }
# LL5D's form: the same rule on 300 toys per truth and 16 cells; the interval at each count k (no result yet)
out["ll5d_form"] = {"n": N, "cells": 16,
                    "note": "LL5D grades #{|e_tc| <= sigma_c} and #{chi2_t in region} of 300 per truth and reading "
                            "(LL5D-DECLARATION.md:471-472); its readout will give k, and the interval is cp95(k, 300)",
                    "at_k": {str(k): cp(k, N) for k in (0, 1, 5, 10, 150, 180, 190, 200, 205, 210, 220, 285, 300)},
                    "half_width_at_nominal_0.6827": (lambda ab: (ab[1] - ab[0]) / 2)(cp(round(0.682689 * N), N))}
Path(__file__).with_name("cp_intervals.json").write_text(json.dumps(out, indent=1) + "\n")
for t, v in out["tunes"].items():
    j = v["joint"]
    print(f"{t}: joint {j['count']}/{N} = {j['frac']:.4f}, CP95 [{j['cp95'][0]:.4f}, {j['cp95'][1]:.4f}]; null q {j['q_null']:.4f}")
    c = v["cells"]
    print(f"  cells: null content above CP95 upper in {c['null_content_above_cp95']}, below lower in {c['null_content_below_cp95']}, inside {c['null_content_inside_cp95']} of 205")
    for f in c["flagged"]:
        print(f"  flagged cell {f['i']}: {f['count']}/{N} = {f['frac']:.3f}, CP95 [{f['cp95'][0]:.3f}, {f['cp95'][1]:.3f}], null {f['p_null']:.4f}")
    m = c["min_frac"]
    print(f"  lowest cell {m['i']}: {m['count']}/{N}, CP95 [{m['cp95'][0]:.3f}, {m['cp95'][1]:.3f}], null {m['p_null']:.4f}")
print("LL5D form: half-width at k=205 of 300:", round(out["ll5d_form"]["half_width_at_nominal_0.6827"], 4))
