"""1B gate-D pre-check: the per-cell, per-band attribution assembled from committed readouts (Part 0 of the director's
2026-11-06 scope ruling, under DECISION-20261106-joseph-diagnoses-jinst-corrections.md item 1.2). 0 node-h.

It opens five committed readouts, refuses unless each has its pinned sha256, and does arithmetic on their values. It
opens no product, no pscratch file and no COV2D input, and it draws nothing.

    python3 -I -B attribution.py REPO_ROOT OUT_JSON      (prints the tables; writes OUT_JSON)

The class of a band in a cell is fixed here, from values already in the records:
  undefined  the band's block is zero on both sides (diag.json sigma_ratio null);
  noise      I0 marks the band noise-consistent on both sides at the upper floor in that cell (i0.json
             per_band.noise_consistent_upper), so its sigma ratio is not resolved from the measured floor;
  matching   otherwise, sigma ratio sqrt(E_b / M_b) inside gate D's window [0.9, 1.1];
  over       above 1.1;
  under      below 0.9.
The same window classes each group's ratio (gate-d.json per_group_sigma_ratio) and the two harness ratios (I2's
F_src, stage 0's kappa), which carry no per-cell noise flag.
"""
import hashlib
import json
import statistics
import sys
from pathlib import Path

FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b"
INPUTS = {
    "gate_d": (f"{FD}/stage2/run/score/gate-d.json", "e1838c0ae2e66c1a0dffd505c41da44381a2d2b798cfc17d353e2d1260542c63"),
    "diag": (f"{FD}/diag/diag.json", "6fd6669efdae5e8dd0934962b4547537a92d37371df6ad481c7df7dd2dfb2a4f"),
    "i0": (f"{FD}/inv/i0/i0.json", "9a4142d348f591134ba4912a2197ca958ea387ec58b095622bce5f206d007021"),
    "i2": (f"{FD}/inv/i2/i2.json", "a9d3dc9c0e331eb635d6598c03b5bf95f6931f88c0cf0a43a1e73e2df9135bdb"),
    "stage0": (f"{FD}/staged/stage0/readout.json", "05be73ee363c5263ffb5db14ad23a0de1efa27c7d755bad804bddd677d9ca5bb"),
}
GROUPS = ("interaction", "flux", "detector")


def load(root: Path) -> dict:
    out = {}
    for key, (rel, pin) in INPUTS.items():
        raw = (root / rel).read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        if got != pin:
            sys.exit(f"REFUSED: {rel} has sha256 {got}, pin {pin}")
        out[key] = json.loads(raw)
    return out


def window_class(r, lo, hi) -> str:
    return "matching" if lo <= r <= hi else ("over" if r > hi else "under")


def quantiles(xs) -> dict:
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=10, method="exclusive")  # the method that gives I2 section 4.2's 0.63-1.63
    return {"n": len(xs), "min": xs[0], "p10": q[0], "median": statistics.median(xs), "p90": q[-1], "max": xs[-1]}


def main(root: Path, out_path: Path) -> None:
    r = load(root)
    gd, dg, i0, i2, s0 = r["gate_d"], r["diag"], r["i0"], r["i2"], r["stage0"]
    cells, (lo, hi) = gd["cells"], gd["window"]
    rho = gd["rho"]
    n = len(cells)

    # controls: the five records describe the same cells, window and rho, and their identities hold
    assert n == 16 and all(x["cells"] == cells for x in (dg, i0, i2, s0))
    assert all(x["window"] == gd["window"] for x in (dg, i0, i2, s0))
    assert dg["rho"] == rho and i0["rho"] == rho, "rho differs between gate D, the diagnosis and I0"
    assert s0["i2_sha256"] == INPUTS["i2"][1] and s0["i0_sha256"] == INPUTS["i0"][1] and i2["i0_sha256"] == INPUTS["i0"][1]
    bands = dg["per_band"]
    assert len(bands) == 38 and set(bands) == set(i0["per_band"])
    term = {b: [v["share_toys"][c] * rho[c] ** 2 - v["share_s1"][c] for c in range(n)] for b, v in bands.items()}
    for c in range(n):
        assert abs(sum(t[c] for t in term.values()) - (rho[c] ** 2 - 1)) < 1e-9, "terms do not sum to rho^2 - 1"
    assert max(abs(term[b][c] - i0["per_band"][b]["term"][c]) for b in bands for c in range(n)) < 1e-12
    for b, v in bands.items():
        for c in range(n):
            if v["sigma_ratio"][c] is not None:
                s2 = v["share_toys"][c] * rho[c] ** 2 / v["share_s1"][c]
                assert abs(s2 / v["sigma_ratio"][c] ** 2 - 1) < 1e-12
    f = i2["factors"]
    for c in range(n):
        assert abs(f["F_src"][c] * f["F_prior"][c] * f["F_truth"][c] - f["total"][c]) < 1e-12
        assert abs(f["total"][c] - gd["per_group_sigma_ratio"]["interaction"][c]) < 1e-12
    inter = [b for b, v in bands.items() if v["group"] == "interaction"]
    assert set(inter) == set(i2["per_band"]) and len(inter) == 33

    failing = [cells[c] for c in range(n) if not lo <= rho[c] <= hi]

    # 1. each band in each cell
    per_band, counts = {}, {}
    for b, v in bands.items():
        noise = set(i0["per_band"][b]["noise_consistent_upper"])
        cls = []
        for c in range(n):
            s = v["sigma_ratio"][c]
            cls.append("undefined" if s is None else "noise" if cells[c] in noise else window_class(s, lo, hi))
        per_band[b] = {"group": v["group"], "sigma_ratio": v["sigma_ratio"], "term": term[b], "class": cls}
        for k in cls:
            counts.setdefault(v["group"], {}).setdefault(k, 0)
            counts[v["group"]][k] += 1

    # 2. each group in each cell (gate D's own per-group ratio), and the split of each failing cell's rho^2 - 1
    per_group = {g: {"sigma_ratio": gd["per_group_sigma_ratio"][g],
                     "class": [window_class(x, lo, hi) for x in gd["per_group_sigma_ratio"][g]]} for g in GROUPS}
    split = {}
    for c in range(n):
        if cells[c] not in failing:
            continue
        tot = rho[c] ** 2 - 1
        gsum = {g: sum(term[b][c] for b in bands if bands[b]["group"] == g) for g in GROUPS}
        ranked = sorted(bands, key=lambda b: -abs(term[b][c]))
        split[cells[c]] = {"rho": rho[c], "rho2_minus_1": tot,
                           "group_term": gsum, "group_share": {g: gsum[g] / tot for g in GROUPS},
                           "largest_terms": [[b, term[b][c]] for b in ranked[:3]]}
        assert abs(split[cells[c]]["group_share"]["interaction"] - i2["interaction_share_of_rho2_minus_1"][cells[c]]) < 1e-12

    # 3. the two harness checks, per cell
    harness = {"F_src": {"value": f["F_src"], "class": [window_class(x, lo, hi) for x in f["F_src"]]},
               "kappa": {"value": s0["kappa"], "class": [window_class(x, lo, hi) for x in s0["kappa"]]}}
    # per interaction band, sqrt(E_b / B_b) = 1 / (B_over_E): descriptive, and I2 section 4.2's quoted spread as a control
    b_over_e = [x for b in inter for x in i2["per_band"][b]["B_over_E"] if x is not None and b != "NormDISCC"]
    harness["per_band_B_over_E"] = quantiles(b_over_e)

    # 4. I2's factor table carried, with the director's narrowing as a label (no prior is involved in F_prior)
    factors = {k: f[k] for k in ("total", "F_src", "F_prior", "F_truth")}
    factor_class = {k: [window_class(x, lo, hi) for x in f[k]] for k in ("F_src", "F_prior", "F_truth")}

    out = {
        "schema": "fd-1b-precheck-attribution/1", "label": "DERIVATION, arithmetic on committed readouts",
        "inputs": {k: {"path": p, "sha256": s} for k, (p, s) in INPUTS.items()},
        "cells": cells, "window": gd["window"], "rho": rho, "failing_cells": failing,
        "class_rule": __doc__.split("The class of a band in a cell is fixed here, from values already in the records:")[1]
        .split("The same window")[0].strip(),
        "per_band": per_band, "class_counts_by_group": counts,
        "per_group": per_group, "failing_cell_split": split,
        "harness": harness, "i2_factors": factors, "i2_factor_class": factor_class,
        "i2_factor_label": "F_prior is the ratio sqrt(B/A) of the response-only block to S1's whole universe at the "
                           "nominal truth; it involves no prior, since A = B + C does not hold (I2 section 4.3; the "
                           "director's I2 review section 3)",
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    out_path.write_text(json.dumps(out, indent=1) + "\n")

    # the printed tables
    print(f"inputs: " + ", ".join(f"{k} {s[:8]}" for k, (_, s) in INPUTS.items()))
    print(f"window {lo}-{hi}; failing cells ({len(failing)}): {' '.join(failing)}")
    print("\n== band classes per group (band-cells)")
    for g in GROUPS:
        print(f"  {g:12s} " + "  ".join(f"{k} {counts[g].get(k, 0)}" for k in ("matching", "over", "under", "noise", "undefined")))
    print("\n== group sigma ratio per cell (gate D per_group_sigma_ratio), class")
    print("  cell  rho    " + "  ".join(f"{g:>17s}" for g in GROUPS))
    for c in range(n):
        print(f"  {cells[c]}  {rho[c]:.3f}  " + "  ".join(
            f"{per_group[g]['sigma_ratio'][c]:8.3f} {per_group[g]['class'][c]:>8s}" for g in GROUPS))
    print("\n== failing cells: share of rho^2 - 1 by group; the three largest |terms|")
    for k, v in split.items():
        sh = v["group_share"]
        print(f"  {k} rho {v['rho']:.3f} rho2-1 {v['rho2_minus_1']:+.3f}  interaction {sh['interaction']:+.3f}  "
              f"flux {sh['flux']:+.3f}  detector {sh['detector']:+.3f}  | "
              + ", ".join(f"{b} {t:+.3f}" for b, t in v["largest_terms"]))
    print("\n== harness checks per cell: I2 F_src = sqrt(E/B); stage 0 kappa = sqrt(Dnom/A_unc)")
    for c in range(n):
        print(f"  {cells[c]}  F_src {f['F_src'][c]:.3f} {harness['F_src']['class'][c]:>8s}   "
              f"kappa {s0['kappa'][c]:.4f} {harness['kappa']['class'][c]:>8s}")
    q = harness["per_band_B_over_E"]
    print(f"  per interaction band-cell sqrt(B/E): n {q['n']}, median {q['median']:.3f}, p10 {q['p10']:.2f}, "
          f"p90 {q['p90']:.2f}, range {q['min']:.3f}-{q['max']:.3f}")
    print("\n== I2 factors per cell (interaction group), class")
    for c in range(n):
        print(f"  {cells[c]}  total {f['total'][c]:.3f}  " + "  ".join(
            f"{k} {f[k][c]:.3f} {factor_class[k][c]:>8s}" for k in ("F_src", "F_prior", "F_truth")))
    print("\n== per band: classes over the 16 cells (M matching, + over, - under, n noise, . undefined)")
    sym = {"matching": "M", "over": "+", "under": "-", "noise": "n", "undefined": "."}
    for g in GROUPS:
        for b in sorted(bb for bb in bands if bands[bb]["group"] == g):
            tabs = sum(abs(x) for x in term[b])
            print(f"  {g[:5]:5s} {b:22s} {''.join(sym[k] for k in per_band[b]['class'])}  sum|term| {tabs:.3f}")
    print(f"\ncode sha256 {out['code_sha256']}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
