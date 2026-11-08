#!/usr/bin/env python3
"""Valid regions of the sixteen-cell result, and reading (3): DECLARATION.md in this directory.

Records-only arithmetic on six committed files (DECLARATION.md section 2, pinned in INPUTS.sha256):
  V-ATLAS  (section 4): A1 mc_neff_truth >= 5000, A2 data stat sigma/f < 0.15, A3 |z| <= 2 at every graded truth.
  V-PRIOR  (section 5): rho = S_b / S_g < 0.5 in all four noise combinations, else "not valid" (all >= 0.5) or
           "unresolved (noise)".
  reading (3) (section 6, descriptive only): per (p_T, p_par) quadrant, the 2D-level departure of the data from the
           prior, and the contrasts between valid cells of the quadrant under each rule; no class, no sentence.
Controls (section 7) run first; any failure exits 3 with nothing classified.

Usage: python3 -B valid_region.py read --repo <clean clone at the bound commit> --out <new dir>
Exit: 0 readings written; 3 STOP (a control failed); 4 refused (usage, a missing input, or --out exists).
"""
import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

DECL_DIR = "docs/orchestration/state/2d-closeout/valid-region-20261107"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
INPUTS = {
    "I1": f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json",
    "I2": f"{FD}/fd/readout/fd_f0b_readout.json",
    "I3": f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json",
    "I4": f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json",
    "I5": "nd-unfolding/pv-ladder/readouts/h2_definition.json",
    "I6": f"{FD}/s1/readout/s1_assembly.json",
}
CELLS = [f"R{i:02d}" for i in range(16)]
QUADRANTS = {"Q1": CELLS[0:4], "Q2": CELLS[4:8], "Q3": CELLS[8:12], "Q4": CELLS[12:16]}
PT_EDGE, PZ_EDGE = 0.7, 4.5
EXTRA_AXES = ("eavail", "q3", "W")
GENERATORS = ("genie_cv", "genie_mec", "nuwro", "gibuu")
PRIOR = "mnvtune_v1"
TRUTH_NAMES = sorted(["W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro",
                      "A7_genie_cv", "A7_genie_mec", "A7_nuwro", "A7_gibuu"])
N_GRADED = 12
COV_KEY = "C_total_plus_C_resp_plus_C_PL5D"

POS = 3.0                            # reading (3): the printed resolved size is POS * sigma_ij (no bar applies)
NEFF_MIN, STAT_MAX, Z_CLOSURE = 5000.0, 0.15, 2.0
TAU = 0.5                            # V-PRIOR: valid iff rho < TAU (the lane's operationalization, not ATLAS's)
TAU_SENS = (1.0 / 3.0, 1.0)          # print-only
TOL = {"C-F": 1e-12, "C-GF": 1e-12, "C-COV-sym": 1e-12, "C-COV-sig": 1e-12}

VALID, NOT_VALID, UNRES_NOISE = "valid", "not valid", "unresolved (noise)"
R3_LABEL = ("descriptive only (DECLARATION.md section 6, audit VR-1): computed after the pulls against the prior "
            "were seen (L4); no class, no sentence, not a test")


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


def read_pins(repo):
    p = Path(repo) / DECL_DIR / "INPUTS.sha256"
    if not p.is_file():
        raise Refuse(f"no pins file {p}")
    pins = {}
    for line in p.read_text().splitlines():
        if line.strip():
            digest, path = line.split(None, 1)
            pins[path.strip()] = digest
    return pins


def load_inputs(repo):
    data = {}
    for key, rel in INPUTS.items():
        p = Path(repo) / rel
        if not p.is_file():
            raise Refuse(f"missing input {key} {rel}")
        data[key] = json.loads(p.read_text())
    return data


def predictions(i3):
    """name -> {cell: (f, g, sigma_Vg_over_f, g_over_f_minus_1)}."""
    out = {}
    for p in i3["predictions"]:
        out[p["name"]] = {c: (float(f), float(g), float(s), float(r)) for c, f, g, s, r in
                          zip(p["cells"], p["f"], p["g"], p["sigma_Vg_over_f"], p["g_over_f_minus_1"])}
    return out


def cell_boxes(i4):
    return {c["cell"]: c["box"] for c in i4["cells"]}


def quadrant_of(box):
    lo_pt = box["pt"][1] <= PT_EDGE
    lo_pz = box["pz"][1] <= PZ_EDGE
    return {(True, True): "Q1", (True, False): "Q2", (False, True): "Q3", (False, False): "Q4"}[(lo_pt, lo_pz)]


def differing_axes(box_a, box_b):
    return [a for a in EXTRA_AXES if list(box_a[a]) != list(box_b[a])]


# ---------------------------------------------------------------------------------------------------- controls

def _ctl(name, ok, detail):
    return {"control": name, "pass": bool(ok), "detail": detail}


def ctl_pin(repo, pins):
    bad = {}
    for key, rel in INPUTS.items():
        want = pins.get(rel)
        got = sha256(Path(repo) / rel)
        if got != want:
            bad[key] = {"want": want, "got": got}
    return _ctl("C-PIN", not bad, bad or "6/6 equal")


def ctl_cells(d):
    bad = []
    if d["I1"]["cells"] != CELLS:
        bad.append("I1")
    for p in d["I3"]["predictions"]:
        if p["name"] != "gibuu" and p["cells"] != CELLS:
            bad.append(f"I3:{p['name']}")
    if [c["cell"] for c in d["I4"]["cells"]] != CELLS:
        bad.append("I4")
    if d["I6"]["cells"] != CELLS:
        bad.append("I6")
    rc = d["I5"]["reporting_cells"]
    if [c["id"] for c in rc] != list(range(16)) or not all(c["reported"] for c in rc):
        bad.append("I5")
    return _ctl("C-CELLS", not bad, bad or "R00-R15 in order in I1, I3, I4, I6; I5 ids 0-15 all reported")


def ctl_box(d):
    bad = []
    b4 = cell_boxes(d["I4"])
    for c, rc in zip(CELLS, d["I5"]["reporting_cells"]):
        if {k: list(v) for k, v in b4[c].items()} != {k: list(v) for k, v in rc["box"].items()}:
            bad.append(f"{c}: I4 box != I5 box")
    for q, cells in QUADRANTS.items():
        for c in cells:
            if quadrant_of(b4[c]) != q:
                bad.append(f"{c}: quadrant {quadrant_of(b4[c])} != {q}")
        if len({(tuple(b4[c]["pt"]), tuple(b4[c]["pz"])) for c in cells}) != 1:
            bad.append(f"{q}: (pt, pz) box not identical")
        for a, b in itertools.combinations(cells, 2):
            if not differing_axes(b4[a], b4[b]):
                bad.append(f"{a},{b}: no extra axis differs")
    return _ctl("C-BOX", not bad, bad or "I4 = I5 boxes; quadrants as declared; siblings differ only in extra axes")


def ctl_domain(d):
    b4 = cell_boxes(d["I4"])
    low = [c for c in CELLS if b4[c]["pz"][1] <= PZ_EDGE]
    gib = [p["cells"] for p in d["I3"]["predictions"] if p["name"] == "gibuu"]
    fam = [t["p_parallel_lt_4p5"]["cells"] for t in d["I1"]["truths"] if t.get("own_vertex") == "gibuu"]
    ok = len(gib) == 1 and gib[0] == low and len(low) == 8 and fam and all(f == low for f in fam)
    return _ctl("C-DOMAIN", ok, {"low_pz_cells": low, "gibuu_cells": gib, "gibuu_family_cells": fam})


def select_truths(i1):
    return [t for t in i1["truths"] if t["graded"] and t["group"] != "prior"]


def ctl_truths(d):
    names = sorted(t["name"] for t in select_truths(d["I1"]))
    n_graded = sum(1 for t in d["I1"]["truths"] if t["graded"])
    ok = names == TRUTH_NAMES and n_graded == N_GRADED
    return _ctl("C-TRUTHS", ok, {"selected": names, "n_graded": n_graded})


def ctl_bias(d):
    a = {t["name"]: (t["bias"], t["noise_sigma"]) for t in d["I1"]["truths"]}
    b = {t["name"]: (t["bias"], t["noise_sigma"]) for t in d["I2"]["truths"]}
    ok = a == b
    return _ctl("C-BIAS", ok, "bias and noise_sigma identical in I1 and I2" if ok else
                sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)))


def ctl_f(d):
    f = dict(zip(CELLS, map(float, d["I4"]["f"])))
    worst = 0.0
    for name, cells in predictions(d["I3"]).items():
        for c, (fp, _g, _s, _r) in cells.items():
            worst = max(worst, abs(fp / f[c] - 1.0))
    return _ctl("C-F", worst <= TOL["C-F"], {"max_rel": worst})


def ctl_gf(d):
    worst = 0.0
    for name, cells in predictions(d["I3"]).items():
        for c, (fp, g, _s, r) in cells.items():
            worst = max(worst, abs((g / fp - 1.0) - r))
    return _ctl("C-GF", worst <= TOL["C-GF"], {"max_abs": worst})


def ctl_cov(d):
    C = np.asarray(d["I4"]["matrices"][COV_KEY], float)
    f = np.asarray(d["I4"]["f"], float)
    scale = np.max(np.abs(C))
    asym = float(np.max(np.abs(C - C.T)) / scale)
    try:
        np.linalg.cholesky(C)
        chol = True
    except np.linalg.LinAlgError:
        chol = False
    sig = np.sqrt(np.diag(C)) / f
    want = np.asarray(d["I4"]["relative_sigma"][COV_KEY], float)
    dev = float(np.max(np.abs(sig / want - 1.0)))
    ok = asym <= TOL["C-COV-sym"] and chol and dev <= TOL["C-COV-sig"]
    return _ctl("C-COV", ok, {"asym_rel": asym, "cholesky": chol, "sigma_rel_dev": dev})


def ctl_rho():
    """The classifier on synthetic inputs: a returned prior is not valid; a recovered truth is valid."""
    deltas = [0.10, -0.06, 0.08]
    var0 = [0.0, 0.0, 0.0]
    sg = spread(deltas, var0)
    returned = spread([-x for x in deltas], var0)
    recovered = spread([0.0, 0.0, 0.0], var0)
    r1 = rho4(returned, sg)
    r0 = rho4(recovered, sg)
    c1, c0 = cls_prior(r1, TAU), cls_prior(r0, TAU)
    ok = all(abs(v - 1.0) < 1e-12 for v in r1.values()) and c1 == NOT_VALID and \
        all(v == 0.0 for v in r0.values()) and c0 == VALID
    return _ctl("C-RHO", ok, {"returned_prior": c1, "recovered_truth": c0})


def ctl_finite(d):
    bad = []
    for t in d["I1"]["truths"]:
        if not np.all(np.isfinite(t["bias"])) or not np.all(np.isfinite(t["noise_sigma"])) or \
                not np.all(np.isfinite(t["grade"]["z"])):
            bad.append(f"I1:{t['name']}")
    for name, cells in predictions(d["I3"]).items():
        for c, (fp, g, s, r) in cells.items():
            if not (math.isfinite(fp) and math.isfinite(g) and math.isfinite(s) and g > 0 and fp > 0 and s >= 0):
                bad.append(f"I3:{name}:{c}")
    stat = np.asarray(d["I6"]["relative_sigma"]["stat"], float)
    if not (np.all(np.isfinite(stat)) and np.all(stat > 0)):
        bad.append("I6:stat")
    neff = np.asarray([c["mc_neff_truth"] for c in d["I5"]["reporting_cells"]], float)
    if not (np.all(np.isfinite(neff)) and np.all(neff > 0)):
        bad.append("I5:mc_neff_truth")
    if not np.all(np.isfinite(np.asarray(d["I4"]["matrices"][COV_KEY], float))):
        bad.append("I4:cov")
    return _ctl("C-FINITE", not bad, bad or "all finite; stat, n_eff, g positive")


def run_controls(repo, pins, d):
    out = [ctl_pin(repo, pins)]
    if not out[0]["pass"]:
        return out
    for fn in (ctl_cells, ctl_box, ctl_domain, ctl_truths, ctl_bias, ctl_f, ctl_gf, ctl_cov, ctl_finite):
        try:
            out.append(fn(d))
        except (KeyError, IndexError, TypeError, ValueError) as e:
            out.append(_ctl(fn.__name__.replace("ctl_", "C-").upper(), False, f"{type(e).__name__}: {e}"))
    out.append(ctl_rho())
    return out


# ---------------------------------------------------------------------------------------------------- V-PRIOR

def spread(values, variances):
    """(raw, sub): root mean square about zero, and with the per-element variance subtracted (floored at 0)."""
    v = np.asarray(values, float)
    w = np.asarray(variances, float)
    raw = math.sqrt(float(np.mean(v ** 2)))
    sub = math.sqrt(max(0.0, float(np.mean(v ** 2 - w))))
    return raw, sub


def rho4(sb, sg):
    """The four combinations (b raw/sub) x (g raw/sub); None where S_g is 0."""
    out = {}
    for bi, bn in enumerate(("b_raw", "b_sub")):
        for gi, gn in enumerate(("g_raw", "g_sub")):
            out[f"{bn}/{gn}"] = None if sg[gi] <= 0.0 else sb[bi] / sg[gi]
    return out


def cls_prior(rhos, tau):
    vals = list(rhos.values())
    if any(v is None for v in vals):
        return UNRES_NOISE
    if all(v < tau for v in vals):
        return VALID
    if all(v >= tau for v in vals):
        return NOT_VALID
    return UNRES_NOISE


def truth_cells(t, gibuu_domain=True):
    if gibuu_domain and t.get("own_vertex") == "gibuu":
        return set(t["p_parallel_lt_4p5"]["cells"])
    return set(CELLS)


def bias_spread(truths, cell, gibuu_domain=True):
    k = CELLS.index(cell)
    b, nu, names = [], [], []
    for t in truths:
        if cell in truth_cells(t, gibuu_domain):
            b.append(float(t["bias"][k]))
            nu.append(float(t["noise_sigma"][k]) ** 2)
            names.append(t["name"])
    return spread(b, nu), names


def prior_spread(preds, cell):
    """delta_G = g_G/g_P - 1 over the generators defined in the cell, with v_G = (1+delta)^2 (s_G^2 + s_P^2)."""
    fP, gP, sP_f, _ = preds[PRIOR][cell]
    sP = sP_f * fP / gP
    deltas, var, names = [], [], []
    for G in GENERATORS:
        if cell not in preds.get(G, {}):
            continue
        fG, gG, sG_f, _ = preds[G][cell]
        sG = sG_f * fG / gG
        dlt = gG / gP - 1.0
        deltas.append(dlt)
        var.append((1.0 + dlt) ** 2 * (sG ** 2 + sP ** 2))
        names.append(G)
    return spread(deltas, var), names


def v_prior(d):
    truths = select_truths(d["I1"])
    preds = predictions(d["I3"])
    cmod = d["I4"]["relative_sigma"]["C_model_abs"]
    rows = {}
    for k, c in enumerate(CELLS):
        sb, tnames = bias_spread(truths, c)
        sg, gnames = prior_spread(preds, c)
        r = rho4(sb, sg)
        sb_all, tall = bias_spread(truths, c, gibuu_domain=False)
        rows[c] = {
            "truths": tnames, "generators": gnames,
            "S_b": {"raw": sb[0], "sub": sb[1]}, "S_g": {"raw": sg[0], "sub": sg[1]},
            "rho": r, "class": cls_prior(r, TAU),
            "print_only": {
                "class_tau_1/3": cls_prior(r, TAU_SENS[0]),
                "class_tau_1": cls_prior(r, TAU_SENS[1]),
                "gibuu_truths_on_all_cells": {"truths": tall, "rho": rho4(sb_all, sg),
                                              "class": cls_prior(rho4(sb_all, sg), TAU)},
                "C_model_relative_sigma": float(cmod[k]),
            },
        }
    return rows


# ---------------------------------------------------------------------------------------------------- V-ATLAS

def cls_atlas(neff, stat, zs):
    a1 = neff >= NEFF_MIN
    a2 = stat < STAT_MAX
    a3 = all(abs(z) <= Z_CLOSURE for z in zs.values())
    return {"A1": a1, "A2": a2, "A3": a3, "class": VALID if (a1 and a2 and a3) else NOT_VALID}


def v_atlas(d):
    graded = [t for t in d["I1"]["truths"] if t["graded"]]
    neff = [float(c["mc_neff_truth"]) for c in d["I5"]["reporting_cells"]]
    stat = [float(x) for x in d["I6"]["relative_sigma"]["stat"]]
    b4 = cell_boxes(d["I4"])
    rows = {}
    for k, c in enumerate(CELLS):
        zs = {t["name"]: float(t["grade"]["z"][k]) for t in graded}
        res = cls_atlas(neff[k], stat[k], zs)
        hi_pz = b4[c]["pz"][1] > PZ_EDGE
        zs_v = {n: z for n, z in zs.items()
                if not (hi_pz and [t for t in graded if t["name"] == n][0].get("own_vertex") == "gibuu")}
        rows[c] = {"mc_neff_truth": neff[k], "stat_rel": stat[k], "z": zs, **res,
                   "print_only": {"A3_without_gibuu_family_above_pz_4.5": all(abs(z) <= Z_CLOSURE
                                                                             for z in zs_v.values())}}
    per_truth = {t["name"]: {"p": t["grade"]["p"], "p_lt_0.01": t["grade"]["p_lt_0.01"]} for t in graded}
    return rows, per_truth


# ---------------------------------------------------------------------------------------------------- reading (3)

def zscore(delta, sigma):
    if sigma > 0:
        return delta / sigma
    return 0.0 if delta == 0 else math.copysign(math.inf, delta)


def departure(d):
    """r_c = f/g_P - 1 and its covariance R = D C D + diag(f^2 V_P / g_P^4), D = diag(1/g_P)."""
    preds = predictions(d["I3"])
    f = np.asarray(d["I4"]["f"], float)
    C = np.asarray(d["I4"]["matrices"][COV_KEY], float)
    gP = np.asarray([preds[PRIOR][c][1] for c in CELLS])
    VP = np.asarray([(preds[PRIOR][c][2] * preds[PRIOR][c][0]) ** 2 for c in CELLS])
    r = f / gP - 1.0
    Dinv = np.diag(1.0 / gP)
    R = Dinv @ C @ Dinv + np.diag(f ** 2 * VP / gP ** 4)
    return f, gP, VP, C, r, R


def quadrant_departure(f, gP, VP, C, idx):
    F, G = float(f[idx].sum()), float(gP[idx].sum())
    rq = F / G - 1.0
    var = float(C[np.ix_(idx, idx)].sum()) / G ** 2 + F ** 2 * float(VP[idx].sum()) / G ** 4
    return rq, math.sqrt(var)


def contrast(r, R, i, j):
    s = math.sqrt(R[i, i] + R[j, j] - 2.0 * R[i, j])
    return float(r[i] - r[j]), s


def reading3(d, valid_sets):
    """Descriptive only: r_c, z_c, r_Q, z_Q, and every valid-pair contrast per rule. No class, no sentence."""
    f, gP, VP, C, r, R = departure(d)
    b4 = cell_boxes(d["I4"])
    zc = {c: zscore(float(r[k]), math.sqrt(R[k, k])) for k, c in enumerate(CELLS)}
    quads = {}
    for q, cells in QUADRANTS.items():
        idx = np.asarray([CELLS.index(c) for c in cells])
        rq, sq = quadrant_departure(f, gP, VP, C, idx)
        quads[q] = {"cells": cells, "r_Q": rq, "sigma_Q": sq, "z_Q": zscore(rq, sq)}
    out = {"label": R3_LABEL,
           "per_cell": {c: {"r": float(r[k]), "sigma": math.sqrt(R[k, k]), "z": zc[c]} for k, c in enumerate(CELLS)},
           "quadrants": quads, "rules": {}}
    for rule, valid in valid_sets.items():
        rq_out, n_contrasts = {}, 0
        for q, cells in QUADRANTS.items():
            vq = [c for c in cells if c in valid]
            pairs = []
            for a, b in itertools.combinations(vq, 2):
                i, j = CELLS.index(a), CELLS.index(b)
                dl, s = contrast(r, R, i, j)
                pairs.append({"pair": [a, b], "delta": dl, "sigma": s, "z": zscore(dl, s),
                              "resolved_3sigma": POS * s, "axes": differing_axes(b4[a], b4[b])})
            n_contrasts += len(pairs)
            rq_out[q] = {"valid_cells": vq, "contrasts": pairs}
        out["rules"][rule] = {"quadrants": rq_out, "n_contrasts": n_contrasts}
    return out


# ---------------------------------------------------------------------------------------------------- read

def readings(d):
    atlas, per_truth = v_atlas(d)
    prior = v_prior(d)
    valid_sets = {"V-ATLAS": {c for c in CELLS if atlas[c]["class"] == VALID},
                  "V-PRIOR": {c for c in CELLS if prior[c]["class"] == VALID}}
    return {
        "V-ATLAS": {"cells": atlas, "per_truth": per_truth, "valid": sorted(valid_sets["V-ATLAS"]),
                    "guide_item_5": "not met: no reported interval has validated coverage (DECLARATION.md section 4)"},
        "V-PRIOR": {"cells": prior, "valid": sorted(valid_sets["V-PRIOR"]), "tau": TAU,
                    "label": "the lane's operationalization of 'comparable', not ATLAS's"},
        "reading3": reading3(d, valid_sets),
    }


def text_summary(out):
    L = ["valid-region readout (DECLARATION.md); not a measurement; no coverage claim", ""]
    L.append("controls: " + ", ".join(f"{c['control']} {'PASS' if c['pass'] else 'FAIL'}" for c in out["controls"]))
    if "readings" not in out:
        return "\n".join(L) + "\nSTOP: no readings\n"
    rd = out["readings"]
    L.append("")
    L.append("cell  n_eff        stat%   A3    V-ATLAS     S_b(raw,sub)        S_g(raw,sub)        rho(min..max)   V-PRIOR")
    for c in CELLS:
        a, p = rd["V-ATLAS"]["cells"][c], rd["V-PRIOR"]["cells"][c]
        rv = [v for v in p["rho"].values() if v is not None]
        rr = f"{min(rv):.3f}..{max(rv):.3f}" if rv else "undefined"
        L.append(f"{c}  {a['mc_neff_truth']:11.0f}  {100 * a['stat_rel']:6.3f}  {'ok' if a['A3'] else 'FAIL':4}  "
                 f"{a['class']:10}  {p['S_b']['raw']:.5f},{p['S_b']['sub']:.5f}    "
                 f"{p['S_g']['raw']:.5f},{p['S_g']['sub']:.5f}    {rr:14}  {p['class']}")
    L.append("")
    L.append("reading (3): " + rd["reading3"]["label"])
    for c, v in rd["reading3"]["per_cell"].items():
        L.append(f"  {c}: r {v['r']:+.4f} sigma {v['sigma']:.4f} z {v['z']:+.2f}")
    for q, v in rd["reading3"]["quadrants"].items():
        L.append(f"{q} {v['cells']}: r_Q {v['r_Q']:+.4f} sigma {v['sigma_Q']:.4f} z_Q {v['z_Q']:+.2f}")
    for rule, v in rd["reading3"]["rules"].items():
        L.append("")
        L.append(f"{rule}: {v['n_contrasts']} contrasts between valid cells within a quadrant")
        for q, w in v["quadrants"].items():
            L.append(f"  {q} valid {w['valid_cells']}")
            for p in w["contrasts"]:
                L.append(f"     {p['pair'][0]}-{p['pair'][1]} r_i-r_j {p['delta']:+.4f} z {p['z']:+.2f} "
                         f"(3 sigma = {p['resolved_3sigma']:.4f}; axes {','.join(p['axes'])})")
    return "\n".join(L) + "\n"


def do_read(repo, out_dir):
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise Refuse(f"{out_dir} exists; use a new directory")
    pins = read_pins(repo)
    d = load_inputs(repo)
    controls = run_controls(repo, pins, d)
    out = {"schema": "valid-region-readout/1", "controls": controls,
           "inputs_sha256": {k: pins.get(v) for k, v in INPUTS.items()},
           "code_sha256": sha256(Path(__file__).resolve()),
           "numpy": np.__version__, "python": sys.version.split()[0]}
    ok = all(c["pass"] for c in controls)
    if ok:
        out["readings"] = readings(d)
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
