"""COV2D's pseudo-data job, step A (COV2D-DECLARATION.md sections 4.1, 4.2, 4.4, 6 (ii), 9.6 and 9.11): the counts, the
truth and the records of every nature of one truth, from one read of $UNI. omnifold_py310 (uproot, no ROOT); step B
(cov2d_pseudo_write.py, root_6_28) turns the counts into data files with the bound writer and reads them back.

* The natures: the 300 toys of ``cov2d.TOY_SEEDS[truth]``, each a ``cov2d.draw``, and the realization d_T at
  ``cov2d.REALIZATION_SEED[truth]``, the CV nature (no universe).
* r_T: one ``s5e_deform.ratio_weight`` call per truth on the concatenation of the truth rows (CV w_truth) and the
  signal rows (weight 0), on F1's 5D fine grid, so both trees get the same per-row factor and the rescale comes from
  the truth rows alone (section 4.1). Background rows get r = 1.
* Composition: each per-row array of a nature is ``cov2d.compose`` over its draw's universe columns, in draw order
  (bitwise, not a matrix product). The CV nature is the CV column itself.
* The Poisson mean: lambda = w_reco,D x r_T x s on the signal rows and w_bkg,D x s on the background rows, with s =
  dataPOTUsed / mcPOTUsed (``re2_driver.get_pot_scales``). The counts are ``cov2d_writer.draw_counts`` at lambda+ from
  ``numpy.random.default_rng([seed, DRAW_SALT, 1])``, over every signal row and then every background row.
* The truth: max(w_truth,D x r_T x s, 0) row by row (``cov2d.lam_plus``), summed per (pT, p_par) cell over the rows in
  the driver's truth phase space (``cov2d_receipt.truth_cell``). Step B normalizes it.
* The records (section 4.2 and 6 (ii)): lambda+'s records per tree, the truth tree's, sum lambda+ and its ratio to the
  data's 4,119,797 events, the negative mass per reco cell (signal, background), per truth cell S_c, m_seen,c, N_c and
  m_all,c, the non-finite weights zeroed, and the outlier cell's negative-composite rows.
* The director's R1 (2026-11-04), at the CV: the rows where the driver's truth denominator and this truth can differ
  (``driver_filter_differences``: w >= 1e4, in-box rows outside the truth phase space, non-finite rows). Any such row
  STOPs the job before any count is written; the truth definition is the director's.
* Section 9.6, before anything is written: ``cov2d.compose`` with one universe gives that universe's column bitwise,
  for MaRES_0, Flux_0 and GEANT_Pion_0, on every chunk of every tree.

Inputs (COV2D addendum A2, Joseph's ruling of 2026-11-05 on AR23's STOP #2): the four shared inputs ($UNI, the CFS CV,
the truth's F1 ratio and the flux constraint) are first staged into ``<out>/stage`` by ``cov2d.stage_copy``, each an
O_NOATIME copy hashed against its pin, with the shared file's atime recorded before and after (a record, not a stop).
pscratch's quota headroom (at least twice what is staged) is checked at submission, by the gate (``cov2d_jobs``). The
job reads only the copies, always through O_NOATIME, and the guard watches only the copies: their atime at the start
and at the end, both values recorded (``atime_ns``); any move STOPs.

  python cov2d_pseudo.py --truth G18 --out DIR [--uni PATH] [--cv PATH] [--prep DIR] [--constraint PATH] [--chunk N]

MEASURES: counts, truths and records of declared draws. CANNOT AUTHORIZE: an unfold, or a verdict.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CLIP = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/clip"
for p in (HERE, CLIP, REPO / "nd-unfolding", REPO / "nd-unfolding" / "pv-ladder"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402
import cov2d_receipt as rc  # noqa: E402
import cov2d_writer as cw  # noqa: E402

DATA_EVENTS = 4_119_797
TRUTH_VARS = rc.TRUTH_VARS
SIG_RECO = ("sim", "sim_pz", "sim_pass")
BKG_RECO = ("sim_background", "sim_background_pz", "sim_background_pass")
SINGLE = (("MaRES", 0), (c.FLUX, 0), ("GEANT_Pion", 0))


def natures(truth: str, w_flux: np.ndarray) -> list[dict]:
    """The 300 toys in seed order, then the realization (draw None: the CV nature)."""
    out = [{"role": "toy", "seed": d.seed, "draw": d} for d in c.declared_draws(truth, w_flux)]
    out.append({"role": "realization", "seed": c.REALIZATION_SEED[truth], "draw": None})
    return out


def column_positions() -> dict:
    """(band, idx) -> position in ``cov2d_receipt.universe_columns``' order."""
    pos, k = {}, 0
    for b in c.ORDER:
        for i in range(c.BANDS[b]):
            pos[(b, i)] = k
            k += 1
    return pos


def composite(cv: np.ndarray, U: np.ndarray, pos: dict, draw) -> np.ndarray:
    """A nature's per-row array on one chunk: compose over its universes in draw order, or the CV for the CV nature."""
    if draw is None:
        return np.array(cv, dtype=np.float64, copy=True)
    return c.compose(cv, [U[:, pos[u]] for u in draw.universes])


def r_rows(ratio: dict, gen_truth: np.ndarray, w_truth_cv: np.ndarray, gen_sig: np.ndarray):
    """(r on the truth rows, r on the signal rows) from ONE ratio_weight call on the concatenation."""
    import pvl_lib
    import s5e_deform
    edges = [pvl_lib.FINE[a] for a in pvl_lib.AXES5]
    gen = np.concatenate([gen_truth, gen_sig])
    w = np.concatenate([np.asarray(w_truth_cv, np.float64), np.zeros(gen_sig.shape[0])])
    r = s5e_deform.ratio_weight(gen, edges, w, ratio, 1.0)
    return r[:gen_truth.shape[0]], r[gen_truth.shape[0]:]


def read_pot(f) -> tuple[float, float]:
    """(dataPOTUsed, mcPOTUsed) from an open uproot file, the TParameters re2_driver.get_pot_scales reads."""
    return float(f["dataPOTUsed"].member("fVal")), float(f["mcPOTUsed"].member("fVal"))


def finite(a: np.ndarray) -> tuple[np.ndarray, int]:
    """Non-finite weights zeroed (as 1B's loader and the receipt do), and their count."""
    bad = ~np.isfinite(a)
    return np.where(bad, 0.0, a), int(bad.sum())


def single_universe_control(cv: np.ndarray, U: np.ndarray, pos: dict) -> list[str]:
    """Section 9.6 on one chunk: compose with one universe is that universe's column, bitwise."""
    bad = []
    for u in SINGLE:
        got = c.compose(cv, [U[:, pos[u]]])
        if got.tobytes() != np.ascontiguousarray(U[:, pos[u]], np.float64).tobytes():
            bad.append(f"{u[0]}_{u[1]}")
    return bad


class Truth:
    """Per nature: the clipped truth per cell, the unclipped composite count N_c and its negative part m_all,c, and the
    truth tree's lambda+ record."""
    def __init__(self, n_nat: int, n_cells: int):
        self.clipped = np.zeros((n_nat, n_cells))
        self.N = np.zeros((n_nat, n_cells))
        self.m_all = np.zeros((n_nat, n_cells))
        self.rec = [{"sum_lambda": 0.0, "sum_lambda_neg": 0.0, "rows_neg": 0} for _ in range(n_nat)]

    def add(self, k: int, w: np.ndarray, cell: np.ndarray, outlier: int, neg_rows: list, start: int):
        plus, rec = c.lam_plus(w)
        for key in rec:
            self.rec[k][key] += rec[key]
        ok = cell >= 0
        n = self.clipped.shape[1]
        self.clipped[k] += np.bincount(cell[ok], weights=plus[ok], minlength=n)
        self.N[k] += np.bincount(cell[ok], weights=w[ok], minlength=n)
        self.m_all[k] += np.bincount(cell[ok], weights=np.where(w[ok] < 0, -w[ok], 0.0), minlength=n)
        hit = np.flatnonzero((cell == outlier) & (w < 0))
        neg_rows.extend((int(start + i), float(w[i])) for i in hit)


def driver_filter_differences(pt: np.ndarray, pz: np.ndarray, w_raw: np.ndarray, s: float, drv: dict) -> dict:
    """The director's R1 counts at the CV: where the driver's truth denominator (collect_truth_denom_arrays: finite,
    0 <= w < 1e4, inside the pT/p_par box with its edges) and this job's truth (truth_cell: the driver's truth phase
    space) can disagree. (a) finite rows with w >= 1e4; (b) finite rows in the box, in a TH2D cell, but outside the
    truth phase space; (c) rows with a non-finite pt, pz or w. Each with its count and its per-cell mass (w x s,
    on the row's TH2D cell when it has one)."""
    pe, ze = np.asarray(drv["PT_EDGES"], float), np.asarray(drv["PZ_EDGES"], float)
    nz = ze.size - 1
    n_cells = (pe.size - 1) * nz
    with np.errstate(invalid="ignore"):
        fin = np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w_raw)
        i = np.searchsorted(pe, pt, side="right") - 1
        j = np.searchsorted(ze, pz, side="right") - 1
        incell = fin & (i >= 0) & (i < pe.size - 1) & (j >= 0) & (j < nz)
        box = fin & (pt >= pe[0]) & (pt <= pe[-1]) & (pz >= ze[0]) & (pz <= ze[-1])
        cell = np.where(incell, i * nz + j, -1)
        tc = rc.truth_cell(np.where(fin, pt, 0.0), np.where(fin, pz, 0.0))
        cats = {"w_ge_1e4": fin & (w_raw >= 1e4),
                "box_outside_phase_space": box & incell & (tc < 0) & (w_raw >= 0) & (w_raw < 1e4),
                "nonfinite": ~fin}
    out = {}
    for k, m in cats.items():
        ok = m & (cell >= 0)
        mass = np.bincount(cell[ok], weights=np.where(np.isfinite(w_raw[ok]), w_raw[ok], 0.0) * s, minlength=n_cells)
        out[k] = {"rows": int(m.sum()), "cells": {int(x): float(mass[x]) for x in np.flatnonzero(mass)}}
    return out


def seen_sums(lam: np.ndarray, kept: np.ndarray, tcell: np.ndarray, n_cells: int) -> tuple[np.ndarray, np.ndarray]:
    """S_c (signed lambda) and m_seen,c (|sum lambda-|) over the reco-kept signal rows whose truth lies in cell c."""
    ok = kept & (tcell >= 0)
    S = np.bincount(tcell[ok], weights=lam[ok], minlength=n_cells)
    m = np.bincount(tcell[ok], weights=np.where(lam[ok] < 0, -lam[ok], 0.0), minlength=n_cells)
    return S, m


def neg_per_reco_cell(lam: np.ndarray, rcell: np.ndarray, n_cells: int) -> np.ndarray:
    ok = rcell >= 0
    return np.bincount(rcell[ok], weights=np.where(lam[ok] < 0, lam[ok], 0.0), minlength=n_cells)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", required=True, choices=sorted(c.TOY_SEEDS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--uni", default=rc.UNI)
    ap.add_argument("--cv", default=cw.CV)
    ap.add_argument("--prep", default=rc.PREP)
    ap.add_argument("--constraint", default=c.CONSTRAINT)
    ap.add_argument("--chunk", type=int, default=rc.CHUNK)
    ap.add_argument("--no-pins", action="store_true", help="tests only: skip the digest pins")
    a = ap.parse_args(argv)
    import uproot
    import clip_probe as cp
    import fd_1b_toys

    t0 = time.time()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=False)
    ratio_src = str(Path(a.prep) / fd_1b_toys.TRUTHS[rc.TUNES[a.truth]])
    rec = {"truth": a.truth, "host": os.uname().nodename, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "uproot": uproot.__version__, "numpy": np.__version__, "chunk": a.chunk, "stop": [], "pins_checked": not a.no_pins}
    shared = {"uni": (a.uni, c.UNI_SHA256), "cv": (a.cv, c.CV_SHA256), "constraint": (a.constraint, c.CONSTRAINT_SHA256),
              "ratio": (ratio_src, fd_1b_toys.committed_ratio_sha256(rc.TUNES[a.truth]))}
    stage = out / "stage"
    stage.mkdir()
    rec["staged"], off_pin = c.stage_all(shared, stage, not a.no_pins, "step A")
    if off_pin:                            # a STOP (the director's ruling on A2 section 6), before any product
        rec["off_pin"] = off_pin
        rec["stop"].append(off_pin["text"])
        rec["verdict"], rec["seconds"] = "STOP", round(time.time() - t0, 1)
        (out / "pseudo_a.json").write_text(json.dumps(rec, indent=1, sort_keys=True))
        print(f"COV2D-PSEUDO-A {a.truth} STOP natures=0 stops=1\nSTOP {off_pin['text']}")
        return 3
    rec["shared_atime_moved"] = [v["src"] for v in rec["staged"].values() if v["src_atime_moved"]]   # a record only
    copy = {k: v["path"] for k, v in rec["staged"].items()}
    before, rec["settle_atime_ns"] = c.settle_atime(copy.values())     # D2: the guard's first reading, settled
    if before is None:                     # a refusal before any of the step's work (the director's ruling), not a STOP
        rec["refused"] = (f"the staged copies' atime did not read the same twice {c.SETTLE_WAIT:g} s apart in "
                          f"{c.SETTLE_TRIES} tries")
        rec["verdict"], rec["seconds"] = "REFUSED", round(time.time() - t0, 1)
        (out / "pseudo_a.json").write_text(json.dumps(rec, indent=1, sort_keys=True))
        print(f"COV2D-PSEUDO-A {a.truth} REFUSED {rec['refused']}")
        return 2

    text, sha = rc.read_noatime(copy["constraint"])
    w_flux = c.flux_weights(text.decode())
    data, sha = rc.read_noatime(copy["ratio"])
    rec["ratio_sha256"] = sha
    ratio = json.loads(data)
    nat = natures(a.truth, w_flux)
    rec["natures"] = [{"role": n["role"], "seed": n["seed"],
                       "universes": [f"{b}:{i}" for b, i in n["draw"].universes] if n["draw"] else [],
                       "lateral_signs": list(n["draw"].lateral_signs) if n["draw"] else [],
                       "norm_z": n["draw"].norm_z if n["draw"] else None} for n in nat]
    pos = column_positions()
    drv = rc.driver_phase_space()
    n_cells = (len(drv["PT_EDGES"]) - 1) * (len(drv["PZ_EDGES"]) - 1)

    with rc.open_noatime(copy["cv"]) as fh:
        pot_cv = read_pot(uproot.open(fh))
    with rc.open_noatime(copy["uni"]) as fh:
        f = uproot.open(fh)
        pot = read_pot(f)
        if pot != pot_cv:
            raise c.Refusal(f"$UNI's POT {pot} differs from $CV's {pot_cv}")
        s = pot[0] / pot[1]
        rec["pot"] = {"data": pot[0], "mc": pot[1], "scale": s}
        ts, tt, tb = f["mc_signal_reco"], f["mc_truth_denom"], f["mc_background"]
        missing = [k for k in TRUTH_VARS if k not in ts.keys()]
        if missing:
            raise c.Refusal(f"mc_signal_reco on $UNI lacks {missing}: r_T cannot be applied to the signal rows")

        gt = tt.arrays(list(TRUTH_VARS) + ["w_truth"], library="np")
        gen_t = np.stack([np.asarray(gt[k], np.float64) for k in TRUTH_VARS], axis=1)
        w_raw = np.asarray(gt["w_truth"], np.float64)
        rec["r1_counts"] = driver_filter_differences(gen_t[:, 0], gen_t[:, 1], w_raw, s, drv)
        nonzero = {k: v["rows"] for k, v in rec["r1_counts"].items() if v["rows"]}
        if nonzero:
            rec["stop"].append(f"R1: the driver's truth denominator and the truth phase space can differ at the CV "
                               f"({nonzero}); section 9.4 is not run and the truth definition goes to the director")
        w_t_cv, _ = finite(w_raw)
        del gt, w_raw
        gs = ts.arrays(list(TRUTH_VARS) + list(SIG_RECO), library="np")
        gen_s = np.stack([np.asarray(gs[k], np.float64) for k in TRUTH_VARS], axis=1)
        r_t, r_s = r_rows(ratio, gen_t, w_t_cv, gen_s)
        tcell_t = rc.truth_cell(gen_t[:, 0], gen_t[:, 1])
        tcell_s = rc.truth_cell(gen_s[:, 0], gen_s[:, 1])
        ok = tcell_t >= 0   # section 9.4's input: the CV nature at r = 1, clipped as the toys' truth is
        truth_cv_r1 = np.bincount(tcell_t[ok], weights=np.maximum(w_t_cv[ok] * s, 0.0), minlength=n_cells)
        kept_s, rcell_s = cp.reco_cell(np.asarray(gs["sim"], float), np.asarray(gs["sim_pz"], float), gs["sim_pass"])
        pass_s = np.asarray(gs["sim_pass"]) != 0
        np.savez(out / "reco_signal.npz", **{k: np.asarray(gs[k]) for k in SIG_RECO})
        del gen_t, gen_s, gs
        gb = tb.arrays(list(BKG_RECO), library="np")
        kept_b, rcell_b = cp.reco_cell(np.asarray(gb["sim_background"], float),
                                       np.asarray(gb["sim_background_pz"], float), gb["sim_background_pass"])
        pass_b = np.asarray(gb["sim_background_pass"]) != 0
        np.savez(out / "reco_background.npz", **{k: np.asarray(gb[k]) for k in BKG_RECO})
        del gb
        rec["r_T"] = {"min": float(min(r_t.min(), r_s.min())), "max": float(max(r_t.max(), r_s.max()))}

        n_nat = len(nat)
        lam = {"signal": np.empty((n_nat, ts.num_entries)), "background": np.empty((n_nat, tb.num_entries))}
        rec["nonfinite_zeroed"] = {}
        single_bad = set()
        truth = Truth(n_nat, n_cells)
        outlier_rows = [[] for _ in range(n_nat)]
        S = np.zeros((n_nat, n_cells))
        m_seen = np.zeros((n_nat, n_cells))
        neg_reco = {"signal": np.zeros((n_nat, n_cells)), "background": np.zeros((n_nat, n_cells))}
        S_reco = np.zeros((n_nat, n_cells))   # section 6 (ii): the signed signal lambda per reco cell
        for name, tree, prefix in rc.ARRAYS:
            t = f[tree]
            cols = [prefix] + rc.universe_columns(prefix)
            zeroed = 0
            for start in range(0, t.num_entries, a.chunk):
                stop = min(start + a.chunk, t.num_entries)
                arr = t.arrays(cols, entry_start=start, entry_stop=stop, library="np")
                cv, z = finite(np.asarray(arr[prefix], np.float64))
                U, zu = finite(np.stack([np.asarray(arr[k], np.float64) for k in cols[1:]], axis=1))
                zeroed += z + zu
                del arr
                single_bad.update(single_universe_control(cv, U, pos))
                for k, n in enumerate(nat):
                    A = composite(cv, U, pos, n["draw"])
                    if name == "wt":
                        truth.add(k, A * r_t[start:stop] * s, tcell_t[start:stop], c.OUTLIER_CELL,
                                  outlier_rows[k], start)
                    elif name == "wr":
                        L = A * r_s[start:stop] * s
                        lam["signal"][k, start:stop] = L
                        Sk, mk = seen_sums(L, kept_s[start:stop], tcell_s[start:stop], n_cells)
                        S[k] += Sk
                        m_seen[k] += mk
                        rc_k = np.where(kept_s[start:stop], rcell_s[start:stop], -1)
                        neg_reco["signal"][k] += neg_per_reco_cell(L, rc_k, n_cells)
                        S_reco[k] += np.bincount(rc_k[rc_k >= 0], weights=L[rc_k >= 0], minlength=n_cells)
                    else:
                        L = A * s
                        lam["background"][k, start:stop] = L
                        neg_reco["background"][k] += neg_per_reco_cell(L, np.where(kept_b[start:stop],
                                                                                   rcell_b[start:stop], -1), n_cells)
            rec["nonfinite_zeroed"][name] = zeroed
    if single_bad:
        rec["stop"].append(f"section 9.6: compose with one universe is not that universe's column for "
                           f"{sorted(single_bad)}")

    rec["toys"] = []
    if not rec["stop"]:
        for k, n in enumerate(nat):
            rng = np.random.default_rng([n["seed"], c.DRAW_SALT, 1])
            ks, kb, lr = cw.draw_counts(lam["signal"][k], lam["background"][k], rng)
            if max(int(ks.max(initial=0)), int(kb.max(initial=0))) > np.iinfo(np.uint16).max:
                raise c.Refusal(f"seed {n['seed']}: a count exceeds uint16")
            ps_, pb_ = np.maximum(lam["signal"][k], 0.0), np.maximum(lam["background"][k], 0.0)
            sum_plus = float(ps_.sum()) + float(pb_.sum())
            # the rows the writer keeps (pass): section 9.11 compares d_T's written total with this
            sum_plus_passed = float(ps_[pass_s].sum()) + float(pb_[pass_b].sum())
            np.savez(out / f"counts_{n['seed']}.npz", signal=ks.astype(np.uint16), background=kb.astype(np.uint16))
            rec["toys"].append({"role": n["role"], "seed": n["seed"], "lambda": lr, "truth_lambda": truth.rec[k],
                                "sum_lambda_plus": sum_plus, "ratio_to_data": sum_plus / DATA_EVENTS,
                                "sum_lambda_plus_passed": sum_plus_passed,
                                "count_passed": int(ks[pass_s].sum() + kb[pass_b].sum()),
                                "outlier_neg_rows": outlier_rows[k]})
        np.savez(out / "cells.npz", truth_clipped=truth.clipped, truth_cv_r1=truth_cv_r1, N=truth.N,
                 m_all=truth.m_all, S=S, m_seen=m_seen,
                 neg_reco_signal=neg_reco["signal"], neg_reco_background=neg_reco["background"], S_reco=S_reco,
                 seeds=np.array([n["seed"] for n in nat]))

    rec["atime_moved"], rec["atime_ns"] = c.atime_guard(before, c.atime_ns(copy.values()))
    if rec["atime_moved"]:
        rec["stop"].append(f"atime moved on {rec['atime_moved']}")
    rec["verdict"] = "STOP" if rec["stop"] else "PASS"
    rec["seconds"] = round(time.time() - t0, 1)
    (out / "pseudo_a.json").write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-PSEUDO-A {a.truth} {rec['verdict']} natures={len(nat)} stops={len(rec['stop'])}")
    if rec["shared_atime_moved"]:
        print(f"SHARED-ATIME (a record, not a stop) moved during staging on {rec['shared_atime_moved']}")
    for x in rec["stop"]:
        print(f"STOP {x}")
    return 0 if rec["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
