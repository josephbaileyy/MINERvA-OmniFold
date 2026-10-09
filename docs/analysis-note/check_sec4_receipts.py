#!/usr/bin/env python3
"""Tie the paper's Sec. IV printed values to their committed receipts (PRD release audit ea939701, G11).

Each check finds one printed value in paper_body.tex (or values.tex), recomputes it from the committed receipt that
backs it, and compares at the printed precision: |computed - printed| <= half a unit in the printed last digit
("round"), or computed < printed ("below", for "below X%"). A value that cannot be located, or a receipt key that
is missing, is a failure. Release-reproducible values are checked by publication/release/figs/fig_numbers.py
instead; this covers the Sec. IV values the release cannot recompute.

  python3 check_sec4_receipts.py              # exit 0 only if every check passes
  python3 check_sec4_receipts.py --self-test  # each printed value perturbed by one unit must be rejected

The receipts live in the canonical repository (docs/orchestration/state/). In a checkout without them (the standalone
note repository) the check reports SKIP and exits 0; the canonical build_all.sh is where it is enforced.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Only the canonical layout <repo>/docs/analysis-note/ has receipts at <repo>/docs/orchestration/state/; anywhere else
# (the standalone note repository) there is nothing to check, and no unrelated directory may be picked up instead.
STATE = (HERE.parents[1] / "docs/orchestration/state" if HERE.name == "analysis-note" and HERE.parent.name == "docs"
         else HERE / ".no-receipts-outside-the-canonical-layout")


def receipt(rel: str) -> dict:
    return json.loads((STATE / rel).read_text())


def ev(name: str) -> bool:
    return bool(re.fullmatch(r"EW\d+", name))


def highest_w(name: str) -> bool:  # the W catch column of the 7 x 6 (E_avail, W) grid: EW5, EW11, ..., EW41
    return ev(name) and int(name[2:]) % 6 == 5


def stat_median():
    return receipt("ki84-adopt-20261006/recompute_2d_budget.json")["VL170"]["boot"]["median_pct"]


def total_median():
    return receipt("ki84-adopt-20261006/recompute_2d_budget.json")["VL170"]["block_sum"]["median_pct"]


def rescore(key):
    return 100.0 * receipt("ki84-rebuild-20261006/rescore_vl169_toys_vl170.json")["vl170"][key]


def interim(key):
    return receipt("coverage-2d-20261005/interim_score.json")["result"][key]


def purity_bias_max():  # VL149: purity-method nominal-truth bias, highest-W cells
    worst = receipt("s5c/d1/d1_summary.json")["groups"]["split_F2"]["worst"]
    return max(abs(c["mean_rel_pct"]) for c in worst if highest_w(c["name"]))


def dev():
    return receipt("s5n/stage1/dev_receipt.json")


def negweight_highw_max():  # VL151: negative-weight treatment, highest-W cells
    return max(abs(v["mean_rel_pct"]) for v in dev()["grid"]["C3_nominal"]["high_W"].values())


def negweight_joint_max():  # VL151: largest residual over the joint (J) cells; per_functional.mean_rel is a fraction
    d = dev()
    pf, names = d["grid"]["C3_nominal"]["per_functional"]["mean_rel"], d["functional_names"]
    hw = d["grid"]["C3_nominal"]["high_W"]
    i = names.index("EW41")
    assert abs(100.0 * pf[i] - hw["EW41"]["mean_rel_pct"]) < 1e-9, "per_functional.mean_rel is not a fraction"
    return max(100.0 * abs(v) for v, n in zip(pf, names) if n.startswith("J"))


def data_method_diff():  # VL152: negweight minus purity on data
    return dev()["controls"]["C7"]["rel_diff_max_abs_pct"]


def regularization_max():  # VL151: GiBUU/GENIE E_avail shape, largest high-W departure
    return max(abs(v["mean_rel_pct"]) for v in dev()["grid"]["C4_eavail_shape"]["high_W"].values())


def shapes_range():  # VL154 A4: worst (E_avail, W) cell for each withheld shape, joint-test estimator
    pts = receipt("s5e/cand/assess_receipt.json")["points"]
    v = [pts[w]["ew_max_abs_pct"] for w in ("W1", "W2", "W3")]
    return min(v), max(v)


def half_of_cells():  # VL154 A4: cells whose model dependence is within the adopted sigma, of 42
    return receipt("s5e/cand/assess_receipt.json")["A4"]["n_useful_cells"] / 42.0


# (label, source file, regex with one or two captured printed values, computed value(s), mode)
CHECKS = [
    ("total median uncertainty (VL172)", "values.tex", r"\\newcommand\{\\uqMedian\}\{([0-9.]+)\}", total_median, "round"),
    ("closure toys (VL169)", "values.tex", r"\\newcommand\{\\covTwoDNtoy\}\{([0-9.]+)\}", lambda: interim("n_toys"), "round"),
    ("first-built band, within 2 sigma (VL169)", "values.tex", r"\\newcommand\{\\covTwoDCTwoPctOne\}\{([0-9.]+)\}",
     lambda: 100.0 * interim("C2"), "round"),
    ("first-built band, within 1 sigma (VL169)", "values.tex", r"\\newcommand\{\\covTwoDCOne\}\{([0-9.]+)\}",
     lambda: interim("C1"), "round"),
    ("two-sigma nominal", "paper_body.tex", r"against \\SI\{([0-9.]+)\}\{\\percent\} nominal",
     lambda: 100.0 * math.erf(2.0 / math.sqrt(2.0)), "round"),
    ("rebuilt band, statistical median (VL170/VL172)", "paper_body.tex",
     r"median statistical uncertainty of \\SI\{([0-9.]+)\}\{\\percent\}", stat_median, "round"),
    ("rescoring against the rebuilt band, 2 and 1 sigma", "paper_body.tex",
     r"removes the tail undercoverage: \\SI\{([0-9.]+)\}\{\\percent\} fall within two standard deviations and "
     r"\\SI\{([0-9.]+)\}\{\\percent\} within one", lambda: (rescore("C2"), rescore("C1")), "round"),
    ("purity bias, highest-W cells (VL149)", "paper_body.tex", r"biased by up to \\SI\{([0-9.]+)\}\{\\percent\} in simulation",
     purity_bias_max, "round"),
    ("negative-weight residual, highest-W cells (VL151)", "paper_body.tex", r"reduces it to below \\SI\{([0-9.]+)\}\{\\percent\}",
     negweight_highw_max, "below"),
    ("negative-weight residual, joint cells (VL151)", "paper_body.tex",
     r"leaving up to \\SI\{([0-9.]+)\}\{\\percent\} in some joint cells", negweight_joint_max, "round"),
    ("treatments on data (VL152)", "paper_body.tex", r"differ by at most \\SI\{([0-9.]+)\}\{\\percent\}", data_method_diff, "round"),
    ("regularization bias at high W (VL151)", "paper_body.tex", r"by up to \\SI\{([0-9.]+)\}\{\\percent\} at high \$W\$",
     regularization_max, "round"),
    ("other fixed shapes, most affected cell (VL154)", "paper_body.tex", r"it is \\SIrange\{([0-9.]+)\}\{([0-9.]+)\}\{\\percent\} in the most affected",
     shapes_range, "round"),
]
VERBAL = [("about half of those cells (VL154: 20 of 42)", "paper_body.tex", r"within the quoted total uncertainty in about half of those cells",
           half_of_cells, 0.40, 0.60)]


def half_ulp(printed: str) -> float:
    return 0.5 * 10.0 ** -(len(printed.split(".")[1]) if "." in printed else 0)


def text(name: str, sources: dict[str, str]) -> str:
    return re.sub(r"\s+", " ", sources[name])


def evaluate(sources: dict[str, str]) -> list[tuple[str, bool, str]]:
    rows = []
    for label, src, pat, fn, mode in CHECKS:
        m = re.findall(pat, text(src, sources))
        if len(m) != 1:
            rows.append((label, False, f"printed value found {len(m)} times in {src} (expected 1)"))
            continue
        printed = m[0] if isinstance(m[0], tuple) else (m[0],)
        comp = fn()
        comp = comp if isinstance(comp, tuple) else (comp,)
        if mode == "round":
            good = all(abs(c - float(p)) <= half_ulp(p) for c, p in zip(comp, printed))
        else:  # below
            good = all(c < float(p) for c, p in zip(comp, printed))
        rows.append((label, good, f"printed {'/'.join(printed)} | receipt {'/'.join(f'{c:.6g}' for c in comp)} | {mode}"))
    for label, src, pat, fn, lo, hi in VERBAL:
        found = len(re.findall(pat, text(src, sources))) == 1
        c = fn()
        rows.append((label, found and lo <= c <= hi, f"phrase found={found} | receipt {c:.3f} in [{lo}, {hi}]"))
    return rows


def load() -> dict[str, str]:
    return {n: (HERE / n).read_text() for n in ("paper_body.tex", "values.tex")}


def self_test() -> int:
    """Every printed value, moved by one unit in its last digit in the direction that must fail, is rejected."""
    base = load()
    ok = all(g for _, g, _ in evaluate(base))
    caught = 0
    for idx, (label, src, pat, fn, mode) in enumerate(CHECKS):
        s = text(src, base)
        m = re.search(pat, s)
        for gi in range(1, (m.lastindex or 0) + 1):
            p = m.group(gi)
            step = 2 * half_ulp(p)
            bad = p
            for k in (1, 2, 5, 10, 50):  # smallest perturbation that leaves the tolerance (or crosses "below")
                cand = float(p) - k * step if mode == "below" else float(p) + k * step
                bad = f"{cand:.{len(p.split('.')[1]) if '.' in p else 0}f}"
                trial = dict(base)
                trial[src] = s[:m.start(gi)] + bad + s[m.end(gi):]
                if not dict((r[0], r[1]) for r in evaluate(trial))[label]:
                    break
            else:
                print(f"  NOT CAUGHT  {label}: {p} -> {bad}")
                ok = False
                continue
            caught += 1
            print(f"  caught      {label}: {p} -> {bad}")
    trial = dict(base)
    trial["paper_body.tex"] = text("paper_body.tex", base).replace("about half of those cells", "about a third of those cells")
    if dict((r[0], r[1]) for r in evaluate(trial))[VERBAL[0][0]]:
        print("  NOT CAUGHT  verbal phrase removal"); ok = False
    else:
        caught += 1; print("  caught      verbal phrase changed")
    print(f"SELF-TEST :: {'PASS' if ok else 'FAIL'} ({caught} perturbations rejected)")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if not STATE.is_dir():
        print(f"SEC4-RECEIPTS :: SKIP -- no receipts at {STATE} (standalone checkout); enforced by the canonical build")
        return 0
    if "--self-test" in argv:
        return self_test()
    rows = evaluate(load())
    for label, good, info in rows:
        print(f"  {'ok  ' if good else 'FAIL'} {label}: {info}")
    ok = all(g for _, g, _ in rows)
    print(f"SEC4-RECEIPTS :: {'PASS' if ok else 'FAIL'} ({sum(g for _, g, _ in rows)}/{len(rows)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
