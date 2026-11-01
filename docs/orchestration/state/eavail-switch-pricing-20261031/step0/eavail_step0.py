#!/usr/bin/env python3
"""Step 0 of the E_avail 139.57 MeV pricing (ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md §4.3):
exact prior-level populations under 135 and 139.57 MeV, read-only, login node, no Slurm.

Every existing file is opened with O_NOATIME (the owner's right on Linux), so no read changes a file's access time and
so its pscratch purge exposure. Each target's stat (size, atime, mtime) is recorded before and after; a changed atime
stops the run (exit 4). Outputs go only to --out (a new directory).

(1) sha256 of the 5D omnifile and of_inputs_5d.npz (pinned digests checked).
(2) From the omnifile's mc_truth_denom (the completeness denominator, selected exactly as
    unfold_nd_omnifold_unbinned.collect_truth_denom_nd with the 20 degree truth gate and POT scaling) and mc_signal_reco
    (rows inside the same truth phase space): populations of the 16 H2 cells and the 7 fine E_avail bins with
    E_avail = MC_eavail (135) and E_avail' = MC_eavail - 0.00457 * MC_npip (139.57); the w_truth-weighted mean MC_npip
    in E_avail bins. Control C1: the 135 truth-denominator histogram on the fine grid must equal of_inputs_5d.npz's
    denom_nd.
(3) From MP-2's S1 dumps (rows joined to MCgen, per-particle fs_pdg/fs_E in MeV): the count of charged pions with stored
    E <= 139.57 MeV, which MC_npip (E - 139.57 > 0) does not count.

Usage: python step0.py --out DIR --fine-map fine_map_h2.npy
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
import uproot

P = "/pscratch/sd/j/josephrb"
N = f"{P}/MINERvA-OmniFold/nd-unfolding"
OMNI = f"{N}/runEventLoopOmniFold_5D_MEFHC.root"
OMNI_SHA = "b6d2651cfdbc52790cc7ed6032f2062a3e0ea50c12d63725beba29098dd5175a"   # mp2_s1_dump.py OMNI5D_SHA
OFIN = f"{N}/of_inputs_5d.npz"
OFIN_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"   # s1_assemble.INPUT_NPZ_SHA256
MP2 = f"{P}/measurement-paper/phase1/mp2/s1"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
FINE_MAP_SHA = "930326a3a7c0852d4047b5468d8ea3b63d046b896e4a4de1557e29f95102e18c"  # s1_assemble.FINE_MAP_SHA256
FINE = [  # s5p_stage1_inspect.FINE, axis order pt, pz, eavail, q3, W (= unfold_nd EXTRA_AXES and u2d edges)
    [0.0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5],
    [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0],
    [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0],
    [0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0],
    [0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0],
]
DM = 0.00457                                  # GeV, 139.57 - 135 MeV
MAX_THETA = math.radians(20.0)                # unfold_2d_omnifold_unbinned.MAX_MUON_THETA_RAD
NARROW = [0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0]
BRANCHES = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "MC_npip", "w_truth"]
STATS = {}


def st(path):
    s = os.stat(path)
    return {"size": s.st_size, "atime_ns": s.st_atime_ns, "mtime_ns": s.st_mtime_ns}


def open_noatime(path):
    if path not in STATS:
        STATS[path] = {"before": st(path)}
    return os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb")


def check_atime(path):
    STATS[path]["after"] = a = st(path)
    if a["atime_ns"] != STATS[path]["before"]["atime_ns"]:
        print(f"[STOP] atime of {path} changed: {STATS[path]}", flush=True)
        sys.exit(4)


def sha256(path):
    h = hashlib.sha256()
    with open_noatime(path) as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    check_atime(path)
    return h.hexdigest()


def fine_index(cols):
    """Flat C-order fine index, -1 outside, by np.histogramdd's rule (right edge of the last bin included)."""
    idx = []
    for c, e in zip(cols, FINE):
        e = np.asarray(e)
        k = np.searchsorted(e, c, side="right") - 1
        k = np.where(c == e[-1], len(e) - 2, k)
        idx.append(np.where((c >= e[0]) & (c <= e[-1]), k, -1))
    ok = np.all([k >= 0 for k in idx], axis=0)
    flat = np.full(cols[0].size, -1, np.int64)
    flat[ok] = np.ravel_multi_index([k[ok] for k in idx], [len(e) - 1 for e in FINE])
    return flat


def pops(flat, w, fm):
    n = int(np.prod([len(e) - 1 for e in FINE]))
    fine = np.bincount(flat[flat >= 0], weights=w[flat >= 0], minlength=n)
    cells = np.bincount(fm[fm >= 0], weights=fine[fm >= 0], minlength=16)
    ea = np.unravel_index(np.arange(n), [len(e) - 1 for e in FINE])[2]
    ebins_rep = np.bincount(ea[fm >= 0], weights=fine[fm >= 0], minlength=7)
    ebins_all = np.bincount(ea, weights=fine, minlength=7)
    return fine, cells, ebins_rep, ebins_all


def read_tree(f, name):
    t = f[name]
    have = set(t.keys())
    miss = [b for b in BRANCHES if b not in have]
    if miss:
        print(f"[STOP] {name} lacks {miss}", flush=True)
        sys.exit(3)
    a = t.arrays(BRANCHES, library="np")
    return {k: np.asarray(v, np.float64) for k, v in a.items()}


def select(a, pot_scale):
    """collect_truth_denom_nd's rule: finite, 0 <= w < 1e4, pt/pz in the box, theta_mu < 20 deg; w x pot_scale."""
    fin = np.all([np.isfinite(a[k]) for k in ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth")], axis=0)
    w = a["w_truth"]
    box = (a["MC"] >= FINE[0][0]) & (a["MC"] <= FINE[0][-1]) & (a["MC_pz"] >= FINE[1][0]) & (a["MC_pz"] <= FINE[1][-1])
    with np.errstate(invalid="ignore"):
        th = np.arctan2(a["MC"], a["MC_pz"]) < MAX_THETA
    keep = fin & (w >= 0) & (w < 1e4) & box & th
    return keep, w * pot_scale


def population_block(a, keep, w, fm):
    out = {}
    npip = a["MC_npip"]
    for tag, eav in (("135", a["MC_eavail"]), ("139.57", a["MC_eavail"] - DM * npip)):
        cols = [a["MC"][keep], a["MC_pz"][keep], eav[keep], a["MC_q3"][keep], a["MC_W"][keep]]
        flat = fine_index(cols)
        fine, cells, er, ea = pops(flat, w[keep], fm)
        out[tag] = {"fine": fine, "cells": cells, "ebins_reported": er, "ebins_all": ea}
    c0, c1 = out["135"]["cells"], out["139.57"]["cells"]
    r0, r1 = out["135"]["ebins_reported"], out["139.57"]["ebins_reported"]
    a0, a1 = out["135"]["ebins_all"], out["139.57"]["ebins_all"]
    e, wk, nk = a["MC_eavail"][keep], w[keep], npip[keep]
    mult = {}
    for edges, label in ((FINE[2], "fine"), (NARROW, "narrow")):
        k = np.searchsorted(edges, e, side="right") - 1
        rows = []
        for j in range(len(edges) - 1):
            m = k == j
            sw = float(wk[m].sum())
            rows.append({"bin": [edges[j], edges[j + 1]], "sum_w": sw,
                         "mean_npip": float((wk[m] * nk[m]).sum() / sw) if sw > 0 else None,
                         "share_npip": {str(q): float(wk[m & (np.minimum(nk, 3) == q)].sum() / sw) if sw > 0 else None
                                        for q in range(4)}})
        mult[label] = rows
    moved = np.searchsorted(FINE[2], e, side="right") != np.searchsorted(FINE[2], e - DM * nk, side="right")
    return {
        "rows_kept": int(keep.sum()), "rows_total": int(keep.size), "sum_w": float(wk.sum()),
        "npip_mean_w": float((wk * nk).sum() / wk.sum()), "npip_negative_rows": int((nk < 0).sum()),
        "weight_share_changing_fine_eavail_bin": float(wk[moved].sum() / wk.sum()),
        "cells_135": c0.tolist(), "cells_139p57": c1.tolist(),
        "cells_rel_change": ((c1 - c0) / c0).tolist(),
        "ebins_reported_135": r0.tolist(), "ebins_reported_139p57": r1.tolist(),
        "ebins_reported_rel_change": ((r1 - r0) / r0).tolist(),
        "ebins_all_rel_change": ((a1 - a0) / a0).tolist(),
        "multiplicity_135_eavail_bins": mult,
    }, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fine-map", required=True)
    ap.add_argument("--skip-mp2", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    fm = np.load(a.fine_map)
    if hashlib.sha256(fm.astype("<i4").tobytes()).hexdigest() != FINE_MAP_SHA:
        print("[STOP] fine map digest", flush=True); sys.exit(3)
    rec = {"schema": "eavail-step0/1", "host": os.uname().nodename, "start_utc": time.strftime("%FT%TZ", time.gmtime()),
           "code_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
           "fine_map_sha256": FINE_MAP_SHA, "dm_GeV": DM}
    rec["sha256"] = {OMNI: sha256(OMNI), OFIN: sha256(OFIN)}
    rec["sha256_ok"] = {OMNI: rec["sha256"][OMNI] == OMNI_SHA, OFIN: rec["sha256"][OFIN] == OFIN_SHA}
    print(f"[1] sha256 ok: {rec['sha256_ok']} ({time.time() - t0:.0f} s)", flush=True)
    if not all(rec["sha256_ok"].values()):
        print("[STOP] a pinned digest differs", flush=True); sys.exit(3)

    with open_noatime(OMNI) as fh:
        f = uproot.open(fh, object_cache=None, array_cache=None)
        dpot = float(f["dataPOTUsed"].member("fVal")); mpot = float(f["mcPOTUsed"].member("fVal"))
        pot_scale = dpot / mpot
        td = read_tree(f, "mc_truth_denom")
        sg = read_tree(f, "mc_signal_reco")
    check_atime(OMNI)
    rec["pot"] = {"data": dpot, "mc": mpot, "scale": pot_scale}
    print(f"[2] read trees: truth_denom {td['MC'].size} rows, signal {sg['MC'].size} rows ({time.time() - t0:.0f} s)",
          flush=True)

    keep, w = select(td, pot_scale)
    rec["truth_denom"], blk = population_block(td, keep, w, fm)
    with open_noatime(OFIN) as fh:
        z = np.load(fh)
        dn = np.asarray(z["denom_nd"], np.float64).ravel(order="C")
        edges_ok = all(np.array_equal(np.asarray(z[f"edges_{i}"], float), np.asarray(FINE[i], float)) for i in range(5))
    check_atime(OFIN)
    mine = blk["135"]["fine"]
    rec["control_C1"] = {"edges_equal": bool(edges_ok), "bitwise_equal": bool(np.array_equal(mine, dn)),
                         "max_rel_diff": float(np.max(np.abs(mine - dn) / np.where(dn != 0, np.abs(dn), 1.0))),
                         "sum_mine": float(mine.sum()), "sum_npz": float(dn.sum())}
    print(f"[2] C1 {rec['control_C1']}", flush=True)
    if not (edges_ok and rec["control_C1"]["max_rel_diff"] < 1e-9):
        print("[STOP] control C1: the 135 truth denominator does not reproduce of_inputs_5d.npz denom_nd", flush=True)
        json.dump(rec, open(os.path.join(a.out, "step0.json"), "w"), indent=1)
        sys.exit(5)

    keep_s, w_s = select(sg, pot_scale)
    rec["signal_reco_truth_phase_space"], _ = population_block(sg, keep_s, w_s, fm)

    if not a.skip_mp2:
        tot = low = low135 = 0
        per = {}
        for pl in PLAYLISTS:
            pth = f"{MP2}/s1_{pl}.npz"
            with open_noatime(pth) as fh:
                z = np.load(fh)
                pdg = np.asarray(z["fs_pdg"]); E = np.asarray(z["fs_E"], np.float64)
            check_atime(pth)
            pic = np.abs(pdg) == 211
            n, l, l0 = int(pic.sum()), int((pic & (E <= 139.57)).sum()), int((pic & (E <= 135.0)).sum())
            per[pl] = {"pi_pm": n, "E_le_139p57": l, "E_le_135": l0}
            tot += n; low += l; low135 += l0
        rec["mp2_pi_pm_low_E"] = {"per_playlist": per, "pi_pm": tot, "E_le_139p57": low, "E_le_135": low135,
                                  "note": "unweighted particle counts over MP-2's joined MCgen rows"}
        print(f"[3] MP-2: {tot} charged pions, {low} with E <= 139.57 MeV ({time.time() - t0:.0f} s)", flush=True)

    rec["stat"] = STATS
    rec["wall_s"] = time.time() - t0
    json.dump(rec, open(os.path.join(a.out, "step0.json"), "w"), indent=1)
    print(f"[done] {rec['wall_s']:.0f} s; every atime unchanged", flush=True)


if __name__ == "__main__":
    main()
