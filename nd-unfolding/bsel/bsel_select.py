#!/usr/bin/env python3
"""(b) part 1: the frozen measured/exploratory selection of R00-R15 (B-SEL-DECLARATION.md rev 1, sha256 04debd57...).

Implements the declaration's §2-§4 exactly, on the committed readouts and the six fetched copies:
  beta_{c,t} = b_{c,t} R_{c,t};  SE_{c,t} = sigma_{c,t} R_{c,t} (closure_nuwro: + the pooled row-4 split variance);
  U_{c,t} = |beta| + 1.96 SE;  measured iff max_t U <= 1.0 S_g,c and no row-4 split flip;  discriminating iff
  measured and max_t U <= 0.5 S_g,c.  S_g over GENIE CV, GENIE+MEC, NuWro (RMS pairwise, Tune v1 units); S_g+ adds GiBUU
  on R00-R03, R08-R11 (printed only).
Every control is a STOP (exit 5, nothing written). The record holds no absolute cross section.

MEASURES: the labels. CANNOT AUTHORIZE: any data statement, held-out claim, covariance validation or estimator change.
usage: bsel_select.py --repo REPO --fetched DIR --out DIR
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

SCHEMA = "bsel-selection/1"
KAPPA = 1.0
KAPPA_DISC = 0.5
Z = 1.96
TOL = 1e-12
F0B_TRUTHS = ("nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro", "A7_mnvtune", "A7_genie_cv",
              "A7_genie_mec", "A7_nuwro", "A7_gibuu")
F1_TRUTHS = ("F1_genie_v3_g18", "F1_genie_v3_ar23")
TRUTHS = F0B_TRUTHS + F1_TRUTHS
A7 = ("A7_mnvtune", "A7_genie_cv", "A7_genie_mec", "A7_nuwro", "A7_gibuu")
PRIOR_TRUTHS = ("nominal", "A7_mnvtune")  # R = 1 exactly
PANEL = ("genie_cv", "genie_mec", "nuwro")
PANEL_PLUS = PANEL + ("gibuu",)
GIBUU_CELLS = (0, 1, 2, 3, 8, 9, 10, 11)  # p_par < 4.5 (FD-F0-DECLARATION.md:259)
ROW4_SEEDS = tuple(range(970000, 970016))
N_CELLS = 16
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
COMMITTED = {  # declaration §1
    f"{FD}/with-cpl/readout/fd_f0b_readout.json": "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6",
    f"{FD}/readout/fd_f1_readout.json": "cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7",
    f"{FD}/receipts-prr/read/cluster/readout.json": "9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead",
    f"{FD}/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json":
        "a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875",
    "nd-unfolding/pv-ladder/readouts/h2_definition.json": "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
}
FETCHED = {  # declaration §1
    "fd_f0b_experiments.npz": "7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9",
    "fd_f1_experiments.npz": "997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc",
    "f1_closure_genie_v3_g18.npz": "198205b6466a4b7ab65555c15c3248b379830a4d6a376b1599fe51923aeb4c94",
    "f1_closure_genie_v3_ar23.npz": "532a6ac014274e54f2c1fa82b46a3411ff0a62c803e108cf85fa6bcfe070e208",
    "L-5D-PV_e_closure_tune_v1.npz": "eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08",
    "L-5D-PV_e_closure_nuwro.npz": "fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182",
}
CLOSURE_OF = {"closure_nuwro": "L-5D-PV_e_closure_nuwro.npz", "F1_genie_v3_g18": "f1_closure_genie_v3_g18.npz",
              "F1_genie_v3_ar23": "f1_closure_genie_v3_ar23.npz"}
TUNE_V1_CLOSURE = "L-5D-PV_e_closure_tune_v1.npz"


class Stop(RuntimeError):
    def __init__(self, control: str, why: str):
        super().__init__(f"{control}: {why}")
        self.control = control


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel_close(a, b, tol=TOL) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(a.shape == b.shape and np.all(np.abs(a - b) <= tol * np.maximum(np.abs(b), 1e-300)))


# ------------------------------------------------------------------------------------------- the pure rule (§2-§3)
def sg(g: dict, names, cells=None) -> np.ndarray:
    """RMS over unordered pairs of (g_a - g_b)/g_TuneV1; NaN outside ``cells`` when given."""
    t = np.asarray(g["mnvtune_v1"], float)
    pairs = list(itertools.combinations(names, 2))
    s = np.sqrt(sum(((np.asarray(g[a], float) - np.asarray(g[b], float)) / t) ** 2 for a, b in pairs) / len(pairs))
    if cells is not None:
        out = np.full(N_CELLS, np.nan)
        out[list(cells)] = s[list(cells)]
        return out
    return s


def bounds(beta: dict, se: dict) -> dict:
    return {t: np.abs(beta[t]) + Z * se[t] for t in beta}


def labels(U: dict, S: np.ndarray) -> np.ndarray:
    worst = np.max(np.vstack([U[t] for t in U]), axis=0)
    return worst <= KAPPA * S


def flips(U: dict, S: np.ndarray, split_U: dict) -> np.ndarray:
    """split_U[t]: (16, 16) per-split guarded bounds for an A7 truth. A cell flips if any one replacement changes it."""
    base = labels(U, S)
    out = np.zeros(N_CELLS, bool)
    for t, rows in split_U.items():
        for row in rows:
            alt = dict(U)
            alt[t] = row
            out |= labels(alt, S) != base
    return out


def select(beta: dict, se: dict, split_beta: dict, g: dict) -> dict:
    """The rule on prepared inputs (Tune v1 units): beta, se per truth (16,), split_beta per A7 truth (16 splits, 16)."""
    S = sg(g, PANEL)
    if not np.all(S > 0):
        raise Stop("C-SG", "S_g is not positive on every cell")
    Sp = sg(g, PANEL_PLUS, GIBUU_CELLS)
    U = bounds(beta, se)
    split_U = {t: np.abs(split_beta[t]) + Z * se[t][None, :] for t in split_beta}
    worst = np.max(np.vstack([U[t] for t in TRUTHS]), axis=0)
    arg = [TRUTHS[i] for i in np.argmax(np.vstack([U[t] for t in TRUTHS]), axis=0)]
    at_means = worst <= KAPPA * S
    fl = flips(U, S, split_U)
    measured = at_means & ~fl
    disc = measured & (worst <= KAPPA_DISC * S)
    sens = np.where(np.isnan(Sp), np.nan, (worst <= KAPPA * np.nan_to_num(Sp, nan=0.0)).astype(float))
    cells = []
    for c in range(N_CELLS):
        cells.append({"cell": f"R{c:02d}", "label": "measured" if measured[c] else "exploratory",
                      "discriminating": bool(disc[c]), "flips": bool(fl[c]), "measured_at_means": bool(at_means[c]),
                      "S_g": float(S[c]), "S_g_plus_gibuu": None if np.isnan(Sp[c]) else float(Sp[c]),
                      "worst_U": float(worst[c]), "worst_truth": arg[c],
                      "U": {t: float(U[t][c]) for t in TRUTHS},
                      "sensitivity_measured_at_means_with_S_g_plus": None if np.isnan(sens[c]) else bool(sens[c])})
    return {"cells": cells, "n_measured": int(measured.sum()), "n_discriminating": int(disc.sum()),
            "kappa": KAPPA, "kappa_discrimination": KAPPA_DISC, "z": Z}


# ------------------------------------------------------------------------------------------- inputs and controls (§1, §4)
def check_pins(repo: Path, fetched: Path) -> None:
    for rel, pin in COMMITTED.items():
        if sha256_path(repo / rel) != pin:
            raise Stop("C-PIN", f"{rel} is not its pin")
    for name, pin in FETCHED.items():
        if sha256_path(fetched / name) != pin:
            raise Stop("C-PIN", f"the fetched {name} is not its pin")


def readout_truths(path: Path) -> dict:
    return {t["name"]: t for t in json.loads(path.read_text())["truths"]}


def cell_X(npz: Path, M16: np.ndarray, key: str) -> np.ndarray:
    with np.load(npz, allow_pickle=False) as z:
        return M16 @ np.asarray(z[key], float)


def prepare(repo: Path, fetched: Path, M16: np.ndarray) -> tuple[dict, dict, dict, dict, dict]:
    f0b = readout_truths(repo / f"{FD}/with-cpl/readout/fd_f0b_readout.json")
    f1 = readout_truths(repo / f"{FD}/readout/fd_f1_readout.json")
    prr = json.loads((repo / f"{FD}/receipts-prr/read/cluster/readout.json").read_text())["table"]
    preds = {p["name"]: p for p in json.loads(
        (repo / f"{FD}/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json").read_text())["predictions"]}
    gro = {}
    for n in PANEL + ("mnvtune_v1",):  # §4 C-SG: the panel and the unit on all 16 cells
        if n not in preds or len(preds[n]["g"]) != N_CELLS or preds[n].get("cells") != [f"R{c:02d}" for c in range(N_CELLS)]:
            raise Stop("C-SG", f"generator {n} is missing or not on R00-R15")
        gro[n] = preds[n]["g"]
    gib = preds.get("gibuu")  # §2: GiBUU only on its supported cells, for the S_g+ printout
    if gib is None or gib.get("cells") != [f"R{c:02d}" for c in GIBUU_CELLS] or len(gib["g"]) != len(GIBUU_CELLS):
        raise Stop("C-SG", "GiBUU's prediction is not on exactly R00-R03 and R08-R11")
    g_gib = np.full(N_CELLS, np.nan)
    g_gib[list(GIBUU_CELLS)] = gib["g"]
    gro["gibuu"] = g_gib.tolist()
    rec = {**{t: f0b.get(t) for t in F0B_TRUTHS}, **{t: f1.get(t) for t in F1_TRUTHS}}
    missing = [t for t, v in rec.items() if v is None]
    if missing:
        raise Stop("C-TAB", f"truths missing from the readouts: {missing}")
    b = {t: np.asarray(rec[t]["bias"], float) for t in TRUTHS}
    sig = {t: np.asarray(rec[t]["noise_sigma"], float) for t in TRUTHS}
    # R (§2)
    xt_v1 = cell_X(fetched / TUNE_V1_CLOSURE, M16, "xtrue_flat")
    if not np.all(xt_v1 > 0):
        raise Stop("C-R", "the Tune v1 closure has a non-positive cell")
    R = {}
    for t in F0B_TRUTHS:
        if t in CLOSURE_OF:
            continue
        key = f"B0/{t}/s991000"
        if key not in prr:
            raise Stop("C-R", f"FD-PRR's readout has no {key}")
        R[t] = 1.0 + np.asarray(prr[key]["d"], float)
    for t, f in CLOSURE_OF.items():
        x = cell_X(fetched / f, M16, "xtrue_flat")
        if not np.all(x > 0):
            raise Stop("C-R", f"{f} has a non-positive cell")
        R[t] = x / xt_v1
    for t in PRIOR_TRUTHS:
        if not np.array_equal(R[t], np.ones(N_CELLS)):
            raise Stop("C-R", f"R is not exactly 1 at the prior truth {t}")
    for t in TRUTHS:
        if R[t].shape != (N_CELLS,) or not np.all(R[t] > 0):
            raise Stop("C-R", f"R at {t} is not 16 positive values")
    # C-TAB: the tables reproduce the readouts
    tab = {}
    with np.load(fetched / "fd_f0b_experiments.npz", allow_pickle=False) as z:
        tab.update({k: np.asarray(z[k]) for k in z.files})
    with np.load(fetched / "fd_f1_experiments.npz", allow_pickle=False) as z:
        tab.update({f"F1::{k}": np.asarray(z[k]) for k in z.files})
    for t in TRUTHS:
        if t == "closure_nuwro":
            xh = cell_X(fetched / CLOSURE_OF[t], M16, "xsec_flat")
            xt = cell_X(fetched / CLOSURE_OF[t], M16, "xtrue_flat")
            if not rel_close(xh / xt - 1.0, b[t], 1e-10) or np.any(sig[t] != 0):
                raise Stop("C-TAB", "closure_nuwro's product does not reproduce the readout (r, N = 0)")
            continue
        key = f"r_{t}" if f"r_{t}" in tab else f"F1::r_{t}"
        if key not in tab:
            raise Stop("C-TAB", f"no table set for {t}")
        r = np.asarray(tab[key], float)
        if r.ndim != 2 or r.shape[1] != N_CELLS:
            raise Stop("C-TAB", f"{key} is not B x 16")
        mean = r.mean(axis=0)
        noise = np.sqrt(np.diag(np.cov(r, rowvar=False, ddof=1)) / r.shape[0])
        if not (rel_close(mean, b[t]) and rel_close(noise, sig[t])):
            raise Stop("C-TAB", f"{key} does not reproduce the readout's bias and noise_sigma to {TOL}")
    # C-SPLIT and the row-4 per-split values
    split_r = {}
    for t in A7:
        seeds = np.asarray(tab.get(f"seed_{t}", []))
        if sorted(seeds.tolist()) != list(ROW4_SEEDS):
            raise Stop("C-SPLIT", f"{t}'s row-4 seeds are not 970000-970015")
        split_r[t] = np.asarray(tab[f"r_{t}"], float)
    return b, sig, R, split_r, gro


def assemble(b, sig, R, split_r) -> tuple[dict, dict, dict, dict]:
    beta = {t: b[t] * R[t] for t in TRUTHS}
    se = {t: sig[t] * R[t] for t in TRUTHS}
    split_beta = {t: split_r[t] * R[t][None, :] for t in A7}
    s2 = np.mean([np.var(split_beta[t], axis=0, ddof=1) for t in A7], axis=0)  # pooled single-split variance
    se["closure_nuwro"] = np.sqrt(se["closure_nuwro"] ** 2 + s2)
    return beta, se, split_beta, {"pooled_split_sd": np.sqrt(s2).tolist()}


def leak_check(out: dict, absolutes: list[np.ndarray]) -> None:
    """C-LEAK: no absolute cross section (any |value| < 1e-30) and none of the given absolute vectors in the record."""
    vals = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, float):
            vals.append(o)
    walk(out)
    v = np.abs(np.asarray(vals, float))
    if np.any((v > 0) & (v < 1e-30)):
        raise Stop("C-LEAK", "an absolute-scale value is in the record")
    for a in absolutes:
        for x in np.abs(np.asarray(a, float)).ravel():
            if x > 0 and np.any(np.isclose(v, x, rtol=1e-12, atol=0)):
                raise Stop("C-LEAK", "an absolute vector entry is in the record")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="bsel_select.py", allow_abbrev=False)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--fetched", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    sys.path.insert(0, str(a.repo / "nd-unfolding"))
    try:
        import estimator_stability_analyze as an
        check_pins(a.repo, a.fetched)
        M16 = an.cell_matrix(str(a.repo / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
        b, sig, R, split_r, g = prepare(a.repo, a.fetched, M16)
        beta, se, split_beta, extra = assemble(b, sig, R, split_r)
        res = select(beta, se, split_beta, g)
        out = {"schema": SCHEMA, "declaration_sha256": "04debd573c7b6a0ad57feb61266384515d4ca2b597d0047cf80aeea303faf8db",
               "inputs_sha256": {**COMMITTED, **FETCHED}, **res, "R": {t: R[t].tolist() for t in TRUTHS},
               "beta": {t: beta[t].tolist() for t in TRUTHS}, "se": {t: se[t].tolist() for t in TRUTHS}, **extra}
        absolutes = [cell_X(a.fetched / f, M16, k) for f in (TUNE_V1_CLOSURE, *CLOSURE_OF.values())
                     for k in ("xtrue_flat", "xsec_flat")] + [np.asarray(v, float)[np.isfinite(np.asarray(v, float))] for v in g.values()]
        leak_check(out, absolutes)
    except Stop as e:
        print(f"STOP {e}", file=sys.stderr)
        return 5
    a.out.mkdir(parents=True)
    (a.out / "selection.json").write_text(json.dumps(out, indent=1) + "\n")
    lines = [f"B-SEL selection: {res['n_measured']} measured, {res['n_discriminating']} discriminating, of 16"]
    for c in res["cells"]:
        lines.append(f"{c['cell']}: {c['label']}{' (discriminating)' if c['discriminating'] else ''}; worst U "
                     f"{c['worst_U']:.4f} at {c['worst_truth']}; S_g {c['S_g']:.4f}; flips {c['flips']}; S_g+ "
                     f"{'n/a' if c['S_g_plus_gibuu'] is None else format(c['S_g_plus_gibuu'], '.4f')}")
    (a.out / "selection.txt").write_text("\n".join(lines) + "\n")
    print(json.dumps({"verdict": "COMPLETE"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
