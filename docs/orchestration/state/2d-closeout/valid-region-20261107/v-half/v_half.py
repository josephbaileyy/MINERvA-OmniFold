#!/usr/bin/env python3
"""V-HALF: the per-cell half-departure bias rule on R00-R15 (DECLARATION.md in this directory;
DECISION-20261109-joseph-bias-half-rule.md; the director's option-B ruling of 2026-11-09).

Per cell c and graded truth t (F0b's 12, GiBUU-family truths on all 16 cells):
  r  = F0b's committed relative bias X_hat/X - 1 (H1, `bias`), nu its noise (H1, `noise_sigma`);
  d  = (X - P)/P, FD-PRR section 4.1's departure, from FD-PRR's committed readout (H2, B0 at split 991000, Addendum A2);
  b  = r (1 + d), section 4.1's bias (X_hat - X)/P.
The rule applies where |d| >= 0.01; (c, t) passes when |b| <= 0.5 |d|, equivalently |r| <= 0.5 |d| / (1 + d).
Noise: margin m = 0.5|d| - |b| with sigma_m^2 = ((1 + d) nu)^2 + (0.5 sgn(d) - |r|)^2 sigma_d^2, sigma_d the
sample s.d. of d over FD-PRR's five splits at A7_gibuu; pass if m - K sigma_m >= 0, fail if m + K sigma_m < 0, else
"unresolved (noise)", K = 2. Cell: "not valid" if any pair fails; else "no d" if any truth lacks d; else "unresolved
(noise)" if any pair is unresolved; else "rule applies at no truth" if none applies; else "valid".
Print-only, beside the verdict and read by nothing: option (A) on FD-PRR's own B0 bias; each cell's threshold
boundaries; the GiBUU-family truths dropped on the p_par >= 4.5 cells; the band at K = 1 and 3.

Usage: python3 -B v_half.py read --repo <clean clone at the bound commit> --out <new dir>
Exit: 0 readings written; 3 STOP (a control failed, nothing classified); 4 refused (usage, a missing input or pin,
or --out exists).
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

DECL_DIR = "docs/orchestration/state/2d-closeout/valid-region-20261107/v-half"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
H1 = f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json"
PINS_H1 = "INPUTS.sha256"          # H1's pin, committed with the declaration
PINS_H2 = "PRR-READOUT.sha256"     # H2's path and pin, added by the binding once FD-PRR's read is committed
CELLS = [f"R{i:02d}" for i in range(16)]
# F0b's 12 graded truths (H1, in its order) -> FD-PRR's truth names (prr_probe.TRUTHS): the same names
TRUTH_MAP = {t: t for t in ("nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro", "A7_mnvtune",
                            "A7_genie_cv", "A7_genie_mec", "A7_nuwro", "A7_gibuu")}
GIBUU_FAMILY = "gibuu"
PRIMARY_SEED = 991000
NOISE_TRUTH, NOISE_SEEDS = "A7_gibuu", (991000, 994001, 994002, 994003, 994004)
PRIOR_TRUTH = "nominal"

FLOOR = 0.01        # the rule applies where |d| >= FLOOR (FD-PRR section 4.1's floor; the decision's addition)
HALF = 0.5          # (c, t) passes when |b| <= HALF |d| (the advisor's 50 %)
K = 2.0             # the noise band, in sigma_m
K_SENS = (1.0, 3.0)  # print-only
TOL_PRR, TOL_HAND = 1e-9, 1e-12

PASS, FAIL, UNRES, NA, NOD = "pass", "fail", "unresolved (noise)", "not applicable", "no d"
VALID, NOT_VALID, NO_D, NOWHERE = "valid", "not valid", "no d", "rule applies at no truth"
LICENCE = {
    "citable_for": ["each cell's V-HALF class, with its inputs, as declared"],
    "not_citable_for": ["coverage", "a measurement", "the cause of any failure",
                        "V-HALF as ATLAS's rule, or as the advisor's exact formulation (the 1 % floor, the noise "
                        "treatment and the hybrid source of d are this record's additions)",
                        "a failing cell as excluded, wrong or unreported",
                        "held-out truths (the truths are not held out)",
                        "any paper or note sentence without the PRD-referee read and Joseph",
                        "the print-only sections, which change no class"],
}


class Stop(Exception):
    """A control failed: exit 3, nothing classified."""


class Refuse(Exception):
    """Usage or input problem: exit 4."""


# ---------------------------------------------------------------------------------------------------- inputs

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_pin(repo, name):
    p = Path(repo) / DECL_DIR / name
    if not p.is_file():
        raise Refuse(f"no pin file {p}")
    lines = [ln for ln in p.read_text().splitlines() if ln.strip()]
    if len(lines) != 1:
        raise Refuse(f"{p}: expected one 'sha256  path' line, found {len(lines)}")
    digest, path = lines[0].split(None, 1)
    return path.strip(), digest


def load(repo):
    h1_path, h1_pin = read_pin(repo, PINS_H1)
    h2_path, h2_pin = read_pin(repo, PINS_H2)
    if h1_path != H1:
        raise Refuse(f"{PINS_H1} names {h1_path}, not {H1}")
    out = {"pins": {"H1": (h1_path, h1_pin), "H2": (h2_path, h2_pin)}}
    for key, rel in (("H1", h1_path), ("H2", h2_path)):
        p = Path(repo) / rel
        if not p.is_file():
            raise Refuse(f"missing input {key} {rel}")
        out[key] = json.loads(p.read_text())
    return out


def graded(h1):
    return [t for t in h1["truths"] if t.get("graded") is True]


def prr_entry(h2, truth, seed):
    return h2["table"].get(f"B0/{truth}/s{seed}")


def arrays(h1, h2):
    """Per truth (H1's order): r, nu (H1); d and FD-PRR's own b (H2, B0 at the primary split), or None for no d."""
    out = {}
    for t in graded(h1):
        e = prr_entry(h2, TRUTH_MAP[t["name"]], PRIMARY_SEED)
        out[t["name"]] = {"r": np.asarray(t["bias"], float), "nu": np.asarray(t["noise_sigma"], float),
                          "d": None if e is None or "d" not in e else np.asarray(e["d"], float),
                          "b_prr": None if e is None else np.asarray(e["b"], float),
                          "own_vertex": t.get("own_vertex"),
                          "low_cells": (t.get("p_parallel_lt_4p5") or {}).get("cells")}
    return out


def sigma_d(h2):
    """Per cell, the sample s.d. (ddof 1) of d over FD-PRR's five splits at A7_gibuu: the only measured points."""
    rows = [np.asarray(prr_entry(h2, NOISE_TRUTH, s)["d"], float) for s in NOISE_SEEDS]
    return np.std(np.vstack(rows), axis=0, ddof=1)


def sigma_b_prr(h2):
    """Per cell, the sample s.d. of FD-PRR's own B0 bias over the five splits at A7_gibuu (option A, print-only)."""
    rows = [np.asarray(prr_entry(h2, NOISE_TRUTH, s)["b"], float) for s in NOISE_SEEDS]
    return np.std(np.vstack(rows), axis=0, ddof=1)


# ---------------------------------------------------------------------------------------------------- the rule

def pair(r, nu, d, sd, k=K, half=HALF, floor=FLOOR):
    """One (cell, truth): the class and its terms. b = r (1 + d); m = half |d| - |b|."""
    if d is None:
        return {"class": NOD}
    b = r * (1.0 + d)
    rec = {"r": r, "nu": nu, "d": d, "b": b, "applies": bool(abs(d) >= floor)}
    if not rec["applies"]:
        rec["class"] = NA
        return rec
    m = half * abs(d) - abs(b)
    sm = math.sqrt(((1.0 + d) * nu) ** 2 + (half * math.copysign(1.0, d) - abs(r)) ** 2 * sd ** 2)
    rec.update({"margin": m, "sigma_m": sm, "lo": m - k * sm, "hi": m + k * sm})
    if rec["lo"] >= 0.0:
        rec["class"] = PASS
    elif rec["hi"] < 0.0:
        rec["class"] = FAIL
    else:
        rec["class"] = UNRES
    return rec


def cell_class(classes):
    if FAIL in classes:
        return NOT_VALID
    if NOD in classes:
        return NO_D
    if UNRES in classes:
        return UNRES
    if all(c == NA for c in classes):
        return NOWHERE
    return VALID


def classify(A, sd, k=K, half=HALF, floor=FLOOR, domain=False, use_prr_b=False, sd_b=None):
    """Every cell's class and its pairs. domain: drop GiBUU-family truths off their p_par < 4.5 cells (print-only).
    use_prr_b: option (A), FD-PRR's own B0 bias b in place of r (1 + d), its noise sd_b (print-only)."""
    cells = {}
    for ci, c in enumerate(CELLS):
        pairs = {}
        for name, a in A.items():
            if domain and a["own_vertex"] == GIBUU_FAMILY and c not in (a["low_cells"] or []):
                continue
            d = None if a["d"] is None else float(a["d"][ci])
            if use_prr_b and d is not None:
                bp = float(a["b_prr"][ci])
                pairs[name] = pair(bp / (1.0 + d), float(sd_b[ci]) / (1.0 + d), d, float(sd[ci]), k, half, floor)
            else:
                pairs[name] = pair(float(a["r"][ci]), float(a["nu"][ci]), d, float(sd[ci]), k, half, floor)
        cells[c] = {"class": cell_class([p["class"] for p in pairs.values()]), "pairs": pairs}
    return cells


def boundaries(A):
    """Print-only, per cell (point values, no noise band): h_star, the least threshold fraction at which the cell is
    valid at the declared floor; and the floors at which h_star changes, from the |d| values of the truths."""
    out = {}
    for ci, c in enumerate(CELLS):
        q = []
        for name, a in A.items():
            if a["d"] is None:
                continue
            d = float(a["d"][ci])
            if d != 0.0:
                q.append((abs(d), abs(float(a["r"][ci]) * (1.0 + d)) / abs(d), name))
        q.sort(reverse=True)

        def h_star(fl):
            v = [x[1] for x in q if x[0] >= fl]
            return max(v) if v else None
        steps, last = [], object()
        for ad, _, name in q:
            h = h_star(ad)
            if h != last:
                steps.append({"floor_up_to": ad, "h_star": h, "last_truth_admitted": name})
                last = h
        out[c] = {"h_star_at_floor": h_star(FLOOR), "valid_at_half_by_point": None if h_star(FLOOR) is None
                  else bool(HALF >= h_star(FLOOR)), "steps": steps}
    return out


# ---------------------------------------------------------------------------------------------------- controls

def _ctl(name, ok, detail):
    return {"control": name, "pass": bool(ok), "detail": detail}


def ctl_pin(repo, D):
    bad = {}
    for key, (rel, want) in D["pins"].items():
        got = sha256(Path(repo) / rel)
        if got != want:
            bad[key] = {"path": rel, "want": want, "got": got}
    return _ctl("C-PIN", not bad, bad or "H1 and H2 equal their pins")


def ctl_cells(D):
    h1 = D["H1"]
    bad = [t["name"] for t in graded(h1) if len(t["bias"]) != 16 or len(t["noise_sigma"]) != 16]
    ok = list(h1["cells"]) == CELLS and not bad
    return _ctl("C-CELLS", ok, {"cells": list(h1["cells"]) == CELLS, "bad_lengths": bad})


def ctl_truths(D):
    names = [t["name"] for t in graded(D["H1"])]
    have = {n: prr_entry(D["H2"], TRUTH_MAP.get(n, ""), PRIMARY_SEED) is not None for n in names}
    seeds = {s: prr_entry(D["H2"], NOISE_TRUTH, s) is not None for s in NOISE_SEEDS}
    ok = names == list(TRUTH_MAP) and all(seeds.values())
    return _ctl("C-TRUTHS", ok, {"graded_in_order": names == list(TRUTH_MAP), "n_graded": len(names),
                                 "with_prr_entry": have, "noise_seeds": seeds,
                                 "note": "a truth without an H2 entry or d is 'no d' per cell, not a STOP"})


def ctl_prr(D):
    """H2 is a COMPLETE FD-PRR readout; at every B0 entry used, b = r (1 + d) holds (its own d, b and r agree);
    d is exactly 0 at B0/nominal at every noise split; every d, b and r present at those entries has one value per
    cell, 16 (H2 carries no cell labels, so their order rests on prr_read's own M16)."""
    h2 = D["H2"]
    bad = []
    keys = [(TRUTH_MAP[n], PRIMARY_SEED) for n in TRUTH_MAP] + [(NOISE_TRUTH, s) for s in NOISE_SEEDS]
    short = []
    for t, s in dict.fromkeys(keys + [(PRIOR_TRUTH, s) for s in NOISE_SEEDS]):
        e = prr_entry(h2, t, s)
        if e is not None and any(len(e[k]) != len(CELLS) for k in ("b", "r", "d") if k in e):
            short.append(f"B0/{t}/s{s}")
    for t, s in keys:
        e = prr_entry(h2, t, s)
        if e is None or "d" not in e:
            continue
        b, r, d = (np.asarray(e[k], float) for k in ("b", "r", "d"))
        if not np.allclose(b, r * (1.0 + d), rtol=TOL_PRR, atol=1e-15):
            bad.append(f"B0/{t}/s{s}")
    zeros = [s for s in NOISE_SEEDS if prr_entry(h2, PRIOR_TRUTH, s) is None
             or np.any(np.asarray(prr_entry(h2, PRIOR_TRUTH, s).get("d", [1.0]), float) != 0.0)]
    ok = h2.get("verdict") == "COMPLETE" and not bad and not zeros and not short
    return _ctl("C-PRR", ok, {"verdict": h2.get("verdict"), "b_ne_r_1pd": bad, "prior_d_not_zero": zeros,
                              "not_16_long": short})


def ctl_domain(D):
    fam = [t for t in graded(D["H1"]) if t.get("own_vertex") == GIBUU_FAMILY]
    sets = {t["name"]: sorted((t.get("p_parallel_lt_4p5") or {}).get("cells") or []) for t in fam}
    first = next(iter(sets.values()), None)
    ok = len(fam) == 2 and first is not None and len(first) == 8 and all(v == first for v in sets.values()) \
        and set(first) <= set(CELLS)
    return _ctl("C-DOMAIN", ok, sets)


def ctl_finite(D):
    A = arrays(D["H1"], D["H2"])
    bad = []
    for n, a in A.items():
        if not (np.all(np.isfinite(a["r"])) and np.all(np.isfinite(a["nu"])) and np.all(a["nu"] >= 0.0)):
            bad.append(f"{n}: r or nu")
        if a["d"] is not None and not (np.all(np.isfinite(a["d"])) and np.all(1.0 + a["d"] > 0.0)):
            bad.append(f"{n}: d")
    sd = sigma_d(D["H2"])
    if not np.all(np.isfinite(sd)):
        bad.append("sigma_d")
    return _ctl("C-FINITE", not bad, bad or "all finite; nu >= 0; 1 + d > 0")


def ctl_form(D):
    """The two forms of the rule agree on every applicable pair, by point value: |b| <= 0.5|d| iff
    |r| <= 0.5|d|/(1 + d)."""
    A = arrays(D["H1"], D["H2"])
    bad, n = [], 0
    for name, a in A.items():
        if a["d"] is None:
            continue
        for ci, c in enumerate(CELLS):
            d, r = float(a["d"][ci]), float(a["r"][ci])
            if abs(d) < FLOOR:
                continue
            n += 1
            f1 = abs(r * (1.0 + d)) <= HALF * abs(d)
            f2 = abs(r) <= HALF * abs(d) / (1.0 + d)
            if f1 != f2 and abs(HALF * abs(d) - abs(r * (1.0 + d))) > 1e-15:
                bad.append(f"{c}/{name}")
    return _ctl("C-FORM", not bad, {"pairs_checked": n, "disagree": bad})


HAND_CELL, HAND_TRUTH = "R06", "A7_gibuu"


def ctl_hand(D):
    """d and b re-derived at one cell from the raw records, by a separate path: d read directly from H2 and again as
    b_prr / r_prr - 1 from FD-PRR's own b and r; r read directly from H1; b = r (1 + d) by hand."""
    ci = CELLS.index(HAND_CELL)
    e = D["H2"]["table"][f"B0/{TRUTH_MAP[HAND_TRUTH]}/s{PRIMARY_SEED}"]
    d_raw = float(e["d"][ci])
    d_alt = float(e["b"][ci]) / float(e["r"][ci]) - 1.0 if float(e["r"][ci]) != 0.0 else None
    t = next(x for x in D["H1"]["truths"] if x["name"] == HAND_TRUTH)
    r_raw = float(t["bias"][ci])
    b_hand = r_raw + r_raw * d_raw
    A = arrays(D["H1"], D["H2"])[HAND_TRUTH]
    p = pair(float(A["r"][ci]), float(A["nu"][ci]), float(A["d"][ci]), 0.0)
    ok = (p["d"] == d_raw and p["r"] == r_raw and abs(p["b"] - b_hand) <= TOL_HAND * max(1e-300, abs(b_hand))
          and (d_alt is None or abs(d_alt - d_raw) <= 1e-6 * max(1.0, abs(d_raw))))
    return _ctl("C-HAND", ok, {"cell": HAND_CELL, "truth": HAND_TRUTH, "d_raw": d_raw, "d_from_prr_b_over_r": d_alt,
                               "r_raw": r_raw, "b_hand": b_hand, "b_code": p["b"]})


def run_controls(repo, D):
    out = [ctl_pin(repo, D)]
    if not out[0]["pass"]:
        return out
    for fn in (ctl_cells, ctl_truths, ctl_prr, ctl_domain, ctl_finite, ctl_form, ctl_hand):
        try:
            out.append(fn(D))
        except (KeyError, IndexError, TypeError, ValueError, StopIteration, ZeroDivisionError) as e:
            out.append(_ctl(fn.__name__.replace("ctl_", "C-").upper(), False, f"{type(e).__name__}: {e}"))
    return out


# ---------------------------------------------------------------------------------------------------- readout

def readings(D):
    A = arrays(D["H1"], D["H2"])
    sd = sigma_d(D["H2"])
    main_ = classify(A, sd)
    out = {
        "rule": {"floor": FLOOR, "half": HALF, "K": K, "forms": ["|b| <= 0.5 |d|", "|r| <= 0.5 |d| / (1 + d)"],
                 "b": "r (1 + d)", "sigma_m": "sqrt(((1 + d) nu)^2 + (0.5 sgn(d) - |r|)^2 sigma_d^2)"},
        "sigma_d": {"truth": NOISE_TRUTH, "seeds": list(NOISE_SEEDS), "per_cell": sd.tolist(),
                    "note": "the only measured points of d's noise, applied to every truth"},
        "cells": {c: {"class": v["class"], "pairs": v["pairs"]} for c, v in main_.items()},
        "counts": {k: sum(1 for v in main_.values() if v["class"] == k) for k in (VALID, NOT_VALID, NO_D, UNRES, NOWHERE)},
        "print_only": {
            "label": "print-only, beside the verdict: read by nothing, changes no class",
            "option_A_prr_b0_bias": {c: v["class"] for c, v in
                                     classify(A, sd, use_prr_b=True, sd_b=sigma_b_prr(D["H2"])).items()},
            "gibuu_excluded_on_p_par_ge_4p5": {c: v["class"] for c, v in classify(A, sd, domain=True).items()},
            "band_K": {str(k): {c: v["class"] for c, v in classify(A, sd, k=k).items()} for k in K_SENS},
            "boundaries": boundaries(A),
            "applicability_near_floor": {c: [n for n, p in v["pairs"].items() if "d" in p
                                             and abs(abs(p["d"]) - FLOOR) < K * float(sd[CELLS.index(c)])]
                                         for c, v in main_.items()},
        },
    }
    return out


def text_summary(out):
    lines = ["V-HALF readout (DECLARATION.md; print-only sections change no class)"]
    for c in out["controls"]:
        lines.append(f"  {c['control']}: {'PASS' if c['pass'] else 'FAIL'}")
    if "readings" not in out:
        lines.append("STOP: a control failed; nothing classified")
        return "\n".join(lines) + "\n"
    R = out["readings"]
    lines.append(f"counts: {R['counts']}")
    po = R["print_only"]
    for c, v in R["cells"].items():
        fails = [n for n, p in v["pairs"].items() if p["class"] == FAIL]
        unres = [n for n, p in v["pairs"].items() if p["class"] == UNRES]
        nod = [n for n, p in v["pairs"].items() if p["class"] == NOD]
        app = sum(1 for p in v["pairs"].values() if p.get("applies"))
        lines.append(f"{c}: {v['class']}  (applies at {app}; fail {fails}; unresolved {unres}; no d {nod})"
                     f"  | print-only: A {po['option_A_prr_b0_bias'][c]}; GiBUU-excluded "
                     f"{po['gibuu_excluded_on_p_par_ge_4p5'][c]}; h* {po['boundaries'][c]['h_star_at_floor']}")
    lines.append("CITABLE FOR: " + "; ".join(LICENCE["citable_for"]))
    lines.append("NOT CITABLE FOR: " + "; ".join(LICENCE["not_citable_for"]))
    return "\n".join(lines) + "\n"


def do_read(repo, out_dir):
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise Refuse(f"{out_dir} exists; use a new directory")
    D = load(repo)
    controls = run_controls(repo, D)
    out = {"schema": "v-half-readout/1", "licence": LICENCE, "controls": controls,
           "inputs": {k: {"path": p, "sha256": s} for k, (p, s) in D["pins"].items()},
           "code_sha256": sha256(Path(__file__).resolve()), "numpy": np.__version__,
           "python": sys.version.split()[0]}
    ok = all(c["pass"] for c in controls)
    if ok:
        out["readings"] = readings(D)
    out_dir.mkdir(parents=True)
    (out_dir / "readout.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    (out_dir / "readout.txt").write_text(text_summary(out))
    return 0 if ok else 3


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    r.add_argument("--repo", required=True)
    r.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        rc = do_read(a.repo, a.out)
    except Refuse as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 4
    print("readings written" if rc == 0 else "STOP: a control failed; see readout.json", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
