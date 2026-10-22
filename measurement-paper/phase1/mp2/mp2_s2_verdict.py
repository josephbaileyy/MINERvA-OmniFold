#!/usr/bin/env python3
"""MP-2 S2 V2/V3 verdicts (root_6_28; no refit; 0 node-h) under binding addendum 14 §2, "Release".

  1. Blind: ndf_fine from raw counts only (Tune rows in G's support per fine cell, G's nevt). If it is < 200 the
     script stops (exit 5) before the sealed file is opened, so the director is told before any verdict is read.
  2. The sealed file's sha256 is verified against the one its gates file recorded, and its stat is taken before and
     after (asserted unchanged; the file is never written).
  3. From the stored weights (weights_<G>_<fset>.npz) and the harmonized arrays, V2-fine, the J pulls and the four V3
     distributions are recomputed exactly as mp2_s2_fit.py's gates did and asserted equal to the sealed statistics, so
     the weights are proven to be the sealed run's. V3-n then replaces the per-neutron sumw2 with the event-clustered
     variance sum_e (n_e,b w_e)^2 on both sides.
  4. §2's rules, per replica, every gate on all five replicas (R3):
       V2-fine  chi2/ndf <= 1.5 over the fine cells with >= 20 entries on both sides
       V2-J     max over the 109 J cells of |pull| <= 3.4970 (Sidak: (1 - 2 Phibar(z))^109 = 0.95); 109 pulls asserted
       V3       p_d = min(1, 2 min(p_chi,d, p_z,d)), p_z,d = 1 - (1 - 2 Phibar(z_max,d))^n_d over d's n_d used bins;
                passes iff min p_d > 0.05/4 (Holm at 0.05 over the four rejects none); ndf < 1 fails closed
  5. Writes verdict_v2v3_<G>_<fset>.json (never overwrites), with every bar quoted, the Holm-adjusted p's, and the
     across-replica correlation of the J pulls (descriptive). V1 and V4 are carried from the gates file.

Usage: python3 mp2_s2_verdict.py --gen G --fset primary|fallback --fit DIR --harm DIR [DIR] --contract S5C_JSON [--blind-only]
       (--harm and --contract must equal the gates run's when its argv records them; the harmonized inputs' sha256 are
       checked against the gates file's sources either way)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import mp2_s2_fit as F  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402

ALPHA = 0.05
V2_FINE_CHI2NDF = 1.5
V2_J_BAR = 3.4970
N_J = 109
NDF_FINE_MIN = 200
N_V3 = 4
V3_HOLM_BAR = ALPHA / N_V3                      # min p_d must exceed this
EQ_REL = 1e-12                                  # recomputed vs sealed statistics


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stat_of(p) -> dict:
    st = os.stat(p)
    return {"size": st.st_size, "mode": oct(st.st_mode & 0o7777), "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
            "ino": st.st_ino}


def sidak_p(zmax: float, n: int) -> float:
    """1 - (1 - 2 Phibar(zmax))^n, computed without cancellation."""
    from scipy.stats import norm
    return float(-np.expm1(n * np.log1p(-2.0 * norm.sf(zmax))))


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = np.argsort(ps, kind="stable")
    adj, run = np.empty(m), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i]))
        adj[i] = run
    return adj.tolist()


def same(a, b, what):
    if a is None or b is None:
        if a is not b:
            raise SystemExit(f"STOP: {what}: recomputed {a} vs sealed {b}")
        return
    if abs(a - b) > EQ_REL * max(abs(a), abs(b), 1e-300):
        raise SystemExit(f"STOP: {what}: recomputed {a!r} differs from sealed {b!r}")


def clustered(ev_id, ib, wt, nb):
    """Bin contents, the event-clustered variance sum_e (n_e,b w_e)^2, and raw entries, for entries (ev_id, ib) of
    weight wt (wt constant within an event)."""
    key = ev_id.astype(np.int64) * nb + ib
    uk, first, cnt = np.unique(key, return_index=True, return_counts=True)
    b = uk % nb
    return (np.bincount(ib, wt, nb), np.bincount(b, (cnt * wt[first]) ** 2, nb), np.bincount(ib, None, nb).astype(float))


def v3_rule(st: dict) -> dict:
    from scipy.stats import chi2 as chi2d
    ndf, n = st["ndf"], st["n_bins_used"]
    if ndf is None or ndf < 1:
        return {"ndf": ndf, "n_bins_used": n, "p_chi": None, "p_z": None, "p_d": 0.0, "fail_closed": "ndf < 1"}
    p_chi = float(chi2d.sf(st["chi2"], ndf))
    p_z = sidak_p(st["max_abs_pull_used"], n)
    return {"ndf": ndf, "n_bins_used": n, "chi2": st["chi2"], "chi2_ndf": st["chi2_ndf"], "p_chi": p_chi,
            "z_max": st["max_abs_pull_used"], "p_z": p_z, "p_d": min(1.0, 2.0 * min(p_chi, p_z))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True, choices=sorted(F.SUPPORT))
    ap.add_argument("--fset", required=True, choices=sorted(F.FSETS))
    ap.add_argument("--fit", type=Path, required=True)
    ap.add_argument("--harm", nargs="+", required=True)
    ap.add_argument("--contract", required=True, help="the s5c contract (J partition)")
    ap.add_argument("--blind-only", action="store_true", help="step 1 only; the sealed file is not opened")
    a = ap.parse_args(argv)
    from scipy.stats import norm
    z_bar = float(norm.isf((1.0 - (1.0 - ALPHA) ** (1.0 / N_J)) / 2.0))
    if abs(z_bar - V2_J_BAR) > 5e-5:
        raise SystemExit(f"STOP: the Sidak bar computes to {z_bar}, not {V2_J_BAR}")
    gp = a.fit / f"gates_{a.gen}_{a.fset}.json"
    gates = json.loads(gp.read_text())
    gargv = gates["argv"]
    harm, contract_path = a.harm, a.contract
    if "--harm" in gargv and "--contract" in gargv:
        if gargv[gargv.index("--harm") + 1: gargv.index("--contract")] != harm or gargv[gargv.index("--contract") + 1] != contract_path:
            raise SystemExit("STOP: --harm/--contract differ from the gates run's argv")
        argv_check = "equal to the gates run's argv"
    else:
        argv_check = "the gates file's argv records no --harm/--contract (gates run in-process)"
    for k_, src in gates["sources"].items():
        if F.sha256(src["path"]) != src["sha256"]:
            raise SystemExit(f"STOP: {src['path']} differs from the gates file's record")
    hd = next(Path(d) for d in harm if (Path(d) / f"events_{a.gen}.npz").exists())
    td = next(Path(d) for d in harm if (Path(d) / "tune_CH.npz").exists())
    tz = np.load(td / "tune_CH.npz")
    ev = np.load(hd / f"events_{a.gen}.npz")
    prod = np.load(hd / f"harmonized_{a.gen}.npz")
    lo, hi = F.SUPPORT[a.gen]
    ins = (tz["enu"] >= lo) & (tz["enu"] <= hi)
    T_fine, T_w, T_i = tz["fine"][ins], tz["w_truth"][ins], tz["i"][ins].astype(np.int64)
    gm = ev["tgt"] != 0                                                # R13, as the gates
    import gen5d_flux_reweight as gfr
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    dV = g5.widths(*g5.AXES).reshape(-1)
    nfine = dV.size
    tn_fine = np.bincount(T_fine, None, nfine).astype(float)
    Gc, Gv, Gn = prod["xsec_flat"] * dV, prod["sumw2_flat"] * dV ** 2, prod["nevt_flat"]
    use = (tn_fine >= F.V2_NMIN) & (Gn >= F.V2_NMIN)
    ndf_fine_blind = int(use.sum()) - 1
    out = {"schema": "mp2-s2-verdict-v2v3/1", "gen": a.gen, "fset": a.fset, "argv": sys.argv,
           "code_sha256": sha256(Path(__file__).resolve()), "fit_code_sha256": sha256(HERE / "mp2_s2_fit.py"),
           "rules": "binding addendum 14 §2 (Joseph's decision DEC:16-19)", "gates_file": {"path": str(gp), "sha256": sha256(gp)},
           "inputs": {"harm": harm, "contract": {"path": contract_path, "sha256": sha256(contract_path)}, "argv_check": argv_check},
           "blind": {"ndf_fine": ndf_fine_blind, "min": NDF_FINE_MIN}}
    print("BLIND", a.gen, a.fset, "ndf_fine", ndf_fine_blind, flush=True)
    if ndf_fine_blind < NDF_FINE_MIN:
        print(f"STOP: ndf_fine {ndf_fine_blind} < {NDF_FINE_MIN}: the director is told before any verdict is read", flush=True)
        return 5
    if a.blind_only:
        return 0
    sp = Path(gates["V2_V3"]["sealed_file"])
    st0 = stat_of(sp)
    if sha256(sp) != gates["V2_V3"]["sealed_sha256"]:
        raise SystemExit(f"STOP: {sp} sha256 differs from the gates file's record")
    sealed = json.loads(sp.read_text())
    wz = np.load(a.fit / f"weights_{a.gen}_{a.fset}.npz")
    if not np.array_equal(wz["i"], T_i):
        raise SystemExit("STOP: the weights file's Tune rows are not the gates' rows")
    contract = json.loads(Path(contract_path).read_text())
    cmap, ncell = s1.coarse_map(s1.J_EDGES, contract["measurement"]["partition_J"]["supported_cells"])
    if ncell != N_J:
        raise SystemExit(f"STOP: {ncell} J cells, not {N_J}")
    rep = cmap >= 0
    # neutron entries: Tune (in support) and G (R13 mask), with their event ids for clustering
    sel_t = ins[tz["nKE_ev"]]
    pos_t = np.searchsorted(np.nonzero(ins)[0], tz["nKE_ev"][sel_t])
    gn_ok = gm[ev["nKE_ev"]]
    g_ev = ev["nKE_ev"][gn_ok]
    reps, pulls_all = {}, []
    for k in range(F.K):
        sk = sealed["replicas"][str(k)]
        w = T_w * wz[f"wG_k{k}"]
        tc, tv = np.bincount(T_fine, w, nfine), np.bincount(T_fine, w * w, nfine)
        fine = F.chi2_shape(tc, tv, tn_fine, Gc, Gv, Gn, F.V2_NMIN)
        for f_ in ("chi2", "scale_s"):
            same(fine[f_], sk["V2"]["fine"][f_], f"replica {k} V2-fine {f_}")
        if fine["ndf"] != sk["V2"]["fine"]["ndf"] or fine["ndf"] != ndf_fine_blind:
            raise SystemExit(f"STOP: replica {k} ndf_fine {fine['ndf']} vs sealed {sk['V2']['fine']['ndf']} vs blind {ndf_fine_blind}")
        s_ = fine["scale_s"]
        jt, jtv = np.bincount(cmap[rep], tc[rep], ncell), np.bincount(cmap[rep], tv[rep], ncell)
        jg, jgv = np.bincount(cmap[rep], Gc[rep], ncell), np.bincount(cmap[rep], Gv[rep], ncell)
        jpull = (s_ * jt - jg) / np.sqrt(s_ * s_ * jtv + jgv)
        sp_j = np.asarray(sk["V2"]["J"]["pulls"], float)
        if jpull.size != N_J or sp_j.size != N_J or not np.all(np.isfinite(jpull)):
            raise SystemExit(f"STOP: replica {k}: {jpull.size} J pulls (sealed {sp_j.size}), not {N_J} finite")
        if np.max(np.abs(jpull - sp_j)) > EQ_REL * max(1.0, float(np.max(np.abs(sp_j)))):
            raise SystemExit(f"STOP: replica {k}: J pulls differ from the sealed ones")
        pulls_all.append(jpull)
        v3s, v3r = {}, {}
        for key, bins in F.V3_BINS.items():
            nb = bins.size - 1
            if key == "neutron_KE_MeV":
                tx, twt, tid = tz["nKE_val"][sel_t], w[pos_t], pos_t
                gx, gwt, gid = ev["nKE_val"][gn_ok], ev["c"][g_ev], g_ev
            else:
                tx, twt, tid = tz[key][ins], w, None
                gx, gwt, gid = ev[key][gm], ev["c"][gm], None
            ib_t, ib_g = np.digitize(tx, bins) - 1, np.digitize(gx, bins) - 1
            if ib_t.min() < 0 or ib_g.min() < 0:
                raise SystemExit(f"STOP: {key}: a value below the first bin edge")
            frozen = F.chi2_shape(np.bincount(ib_t, twt, nb), np.bincount(ib_t, twt * twt, nb), np.bincount(ib_t, None, nb).astype(float),
                                  np.bincount(ib_g, gwt, nb), np.bincount(ib_g, gwt * gwt, nb), np.bincount(ib_g, None, nb).astype(float), F.V2_NMIN)
            same(frozen["chi2"], sk["V3"][key]["chi2"], f"replica {k} V3 {key} chi2")
            if frozen["ndf"] != sk["V3"][key]["ndf"]:
                raise SystemExit(f"STOP: replica {k} V3 {key} ndf differs from the sealed one")
            if key == "neutron_KE_MeV":                                # V3-n (addendum 14 §2)
                tcn, tvn, tnn = clustered(tid, ib_t, twt, nb)
                gcn, gvn, gnn = clustered(gid, ib_g, gwt, nb)
                st = F.chi2_shape(tcn, tvn, tnn, gcn, gvn, gnn, F.V2_NMIN)
                st["variance"] = "event-clustered sum_e (n_e,b w_e)^2 (V3-n)"
            else:
                st = frozen
            v3s[key] = st
            v3r[key] = v3_rule(st)
        pds = [v3r[key]["p_d"] for key in F.V3_BINS]
        adj = holm(pds)
        for key, pa in zip(F.V3_BINS, adj):
            v3r[key]["p_holm"] = pa
        reps[str(k)] = {
            "V2_fine": {"chi2": fine["chi2"], "ndf": fine["ndf"], "chi2_ndf": fine["chi2_ndf"], "bar": V2_FINE_CHI2NDF,
                        "pass": bool(fine["chi2_ndf"] is not None and fine["chi2_ndf"] <= V2_FINE_CHI2NDF)},
            "V2_J": {"n_pulls": int(jpull.size), "max_abs_pull": float(np.max(np.abs(jpull))),
                     "argmax_cell": int(np.argmax(np.abs(jpull))), "bar": V2_J_BAR,
                     "pass": bool(np.max(np.abs(jpull)) <= V2_J_BAR)},
            "V3": {"distributions": v3r, "min_p_d": float(min(pds)), "bar_min_p_d_gt": V3_HOLM_BAR,
                   "pass": bool(min(pds) > V3_HOLM_BAR and all("fail_closed" not in v3r[key] for key in F.V3_BINS))},
            "V3_statistics": v3s}
    P = np.asarray(pulls_all)
    cc = np.corrcoef(P)
    off = cc[~np.eye(F.K, dtype=bool)]
    st1 = stat_of(sp)
    if st1 != st0 or sha256(sp) != gates["V2_V3"]["sealed_sha256"]:
        raise SystemExit(f"STOP: {sp} changed while it was read")
    allpass = {g: all(reps[str(k)][g]["pass"] for k in range(F.K)) for g in ("V2_fine", "V2_J", "V3")}
    out.update(sealed={"path": str(sp), "sha256": gates["V2_V3"]["sealed_sha256"], "stat_before": st0, "stat_after": st1},
               weights={"path": str(a.fit / f"weights_{a.gen}_{a.fset}.npz"), "sha256": sha256(a.fit / f"weights_{a.gen}_{a.fset}.npz")},
               recomputation="V2-fine, J pulls and the frozen-form V3 statistics recomputed from the weights equal the sealed ones "
                             f"to <= {EQ_REL} relative (asserted)",
               replicas=reps,
               J_pull_correlation_across_replicas={"status": "DESCRIPTIVE (addendum 14 §2)", "mean_offdiag": float(off.mean()),
                                                  "min_offdiag": float(off.min()), "max_offdiag": float(off.max())},
               verdict={"V1": gates["verdict"]["V1"], "V4_all_replicas": gates["verdict"]["V4_all_replicas"],
                        "V2_fine_all_replicas": allpass["V2_fine"], "V2_J_all_replicas": allpass["V2_J"],
                        "V3_all_replicas": allpass["V3"],
                        "S2": bool(gates["verdict"]["V1"] and gates["verdict"]["V4_all_replicas"] and all(allpass.values()))})
    vp = a.fit / f"verdict_v2v3_{a.gen}_{a.fset}.json"
    if vp.exists():
        raise SystemExit(f"refusing to overwrite {vp}")
    vp.write_text(json.dumps(out, indent=1, default=float) + "\n")
    os.chmod(vp, 0o444)
    print("VERDICT_V2V3", a.gen, a.fset, json.dumps(out["verdict"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
