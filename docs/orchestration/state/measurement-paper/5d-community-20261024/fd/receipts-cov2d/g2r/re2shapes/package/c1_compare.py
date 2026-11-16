"""C1 for RE-2-shapes (the director's ruling 2 of 2026-11-14, criterion as restated the same day): route A's Q
against data_g2r.npz's C_new.

The reported matrix is C_new (data_g2r.npz, the graded and adopted D1 object). Route A re-runs RE-2 part C's refined
arm with the J2 universes swapped for G2R's, and supplies the derived quantities in re2's shapes. C1 passes only if:
  (a) the entries: |Q_A - C_new|_ij <= 1e-14 sqrt(C_new_ii C_new_jj) for every i, j (scaled by the diagonal: the size
      of summation-order rounding). If a diagonal factor is not positive, the entry must be equal.
  (b) Q's printed numbers: for every row of re2c_values_spec.tsv (the deploy's) whose source is budget_Q and whose
      path is Q.median_pct or Q.integral_sigma_pct, re2c_values.render (the row's transform and format, i.e. the
      digits the note prints) of re2c_build_q.metrics(Q_A) equals that of metrics(C_new), and of route A's own
      budget_Q.json. x and F are as G2R took them: x from cov2d_Q_205.npz, F from S5's functionals.
  (c) the per-band medians: for every spec row whose source is budget_Q and whose path is bands.<b>.<metric>, route
      A's budget_Q.json value, rendered, equals the reference rendered. For a band G2R rebuilt (band__<b> in
      data_g2r.npz) the reference is metrics(build_repair.wcov(band__<b>, w)) with w the Flux universe weights (first
      100 "Flux" rows of the NuE constraint file, as re2c_rollup.flux_weights takes them) for Flux and 1 otherwise.
      For any other band (the laterals, unchanged by G2R) it is partc-r2's budget_Q.json.
  (d) x and F equal partc-r2's.
It prints without gating on them: (i) the per-entry max relative |dQ|/|C_new|, the count above 1e-15 and the worst
(i, j); (ii) max|dQ| / max|C_new|; (iii) the max of the diagonal-scaled statistic of (a); (iv) bitwise equality; and
(U_A - U_R) against (C_univ_new - C_univ_old), scaled by its maximum.
Every input outside the deploy is read O_NOATIME and checked against its digest: data_g2r.npz (DATA_SHA), partc-r2's
outA/cov2d_Q_205.npz (Q_R_SHA), outA/budget_Q.json (BUDGET_R_SHA), s5/production_cov.npz (S5_R_SHA), and the
constraint file (build_repair.PINNED). Route A's files are its own outputs; their digests are recorded.
    python3 -I c1_compare.py --deploy D --route-a <g2r arm out> --partc-r2 <dir> --data-npz <data_g2r.npz> --out c1.json
Exit 0 only if (a)-(d) hold; 1 otherwise (a STOP to the director, unrepaired); 2 if an input fails its digest.
"""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
import sys

import numpy as np

DATA_SHA = "3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b"     # data_g2r.npz (receipts-cov2d/g2r/readout/data)
Q_R_SHA = "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2"      # partc-r2 outA/cov2d_Q_205.npz (its SHA256SUMS)
BUDGET_R_SHA = "bbe13622656e9f43978d9cb022ac74ca4ba059b1cf56fed9e082bfb3b1be03aa"  # partc-r2 outA/budget_Q.json
S5_R_SHA = "631cf255fff43b5cb35acd9cefdcee99e5ee95b85dc2f30d8e0aca513095eea1"     # partc-r2 s5/production_cov.npz
SCALED_TOL, REL_PRINT = 1e-14, 1e-15
SPEC = "2d-unfolding/re2/partc/re2c_values_spec.tsv"
PARTC = "2d-unfolding/re2/partc"
BRP = "docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py"


def read(path, want=None):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    raw = b"".join(chunks)
    got = hashlib.sha256(raw).hexdigest()
    if want is not None and got != want:
        print(f"C1 DIGEST {path}: {got}, not {want}")
        sys.exit(2)
    return raw, got


def npz(path, want=None):
    raw, got = read(path, want)
    return dict(np.load(io.BytesIO(raw), allow_pickle=False)), got


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def flux_w(text):
    """re2c_rollup.flux_weights' reading of the constraint: rows "Flux <i> <w>", i = 0..99."""
    cons = {}
    for line in text.splitlines():
        t = line.split()
        if len(t) == 3 and t[0] == "Flux":
            cons[int(t[1])] = float(t[2])
    return np.array([cons[i] for i in range(100)])


def main():
    ap = argparse.ArgumentParser()
    for k in ("--deploy", "--route-a", "--partc-r2", "--data-npz", "--out"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    D = a.deploy
    sys.path[:0] = [os.path.join(D, PARTC), os.path.join(D, "2d-unfolding"), D]
    import re2c_build_q as bq
    import re2c_values as rv
    BR = module("build_repair", os.path.join(D, BRP))
    data, data_sha = npz(a.data_npz, DATA_SHA)
    qr, _ = npz(os.path.join(a.partc_r2, "outA", "cov2d_Q_205.npz"), Q_R_SHA)
    s5r, _ = npz(os.path.join(a.partc_r2, "s5", "production_cov.npz"), S5_R_SHA)
    bud_r = json.loads(read(os.path.join(a.partc_r2, "outA", "budget_Q.json"), BUDGET_R_SHA)[0])
    cons_raw, cons_sha = read(BR.INPUTS["constraint"], BR.PINNED["constraint"])
    qa, qa_sha = npz(os.path.join(a.route_a, "outA", "cov2d_Q_205.npz"))
    s5a, s5a_sha = npz(os.path.join(a.route_a, "s5", "production_cov.npz"))
    bud_raw, bud_sha = read(os.path.join(a.route_a, "outA", "budget_Q.json"))
    bud_a = json.loads(bud_raw)
    Cn = np.asarray(data["C_new"], np.float64)
    QA = np.asarray(qa["Q"], np.float64)
    rec = {"schema": "re2shapes-c1/2", "inputs": {"data_npz": [a.data_npz, data_sha], "route_a_q205": qa_sha,
                                                  "route_a_s5": s5a_sha, "route_a_budget_Q": bud_sha, "q_r": Q_R_SHA,
                                                  "budget_r": BUDGET_R_SHA, "s5_r": S5_R_SHA,
                                                  "constraint": [BR.INPUTS["constraint"], cons_sha]},
           "shape": [list(QA.shape), list(Cn.shape)]}
    if QA.shape != Cn.shape:
        rec.update(verdict="FAIL", why="shapes differ")
        return finish(a, rec)
    d = np.abs(QA - Cn)
    dg = np.diag(Cn)
    scale = np.sqrt(np.outer(np.maximum(dg, 0), np.maximum(dg, 0)))
    pos = np.outer(dg > 0, dg > 0)
    stat = np.where(pos, d / np.where(pos, scale, 1.0), np.where(d == 0, 0.0, np.inf))
    zero = Cn == 0
    rel = np.where(zero, np.where(d == 0, 0.0, np.inf), d / np.where(zero, 1.0, np.abs(Cn)))
    ir, jr = np.unravel_index(int(np.argmax(rel)), rel.shape)
    i_s, j_s = np.unravel_index(int(np.argmax(stat)), stat.shape)
    rec["a_entries"] = {"max_scaled": float(stat.max()), "tol": SCALED_TOL, "n_above": int((stat > SCALED_TOL).sum()),
                        "worst": {"i": int(i_s), "j": int(j_s), "Q_A": float(QA[i_s, j_s]), "C_new": float(Cn[i_s, j_s])},
                        "pass": bool(stat.max() <= SCALED_TOL)}
    rec["i_per_entry_rel"] = {"max": float(rel.max()), "n_above_1e-15": int((rel > REL_PRINT).sum()), "n": int(rel.size),
                              "worst": {"i": int(ir), "j": int(jr), "Q_A": float(QA[ir, jr]), "C_new": float(Cn[ir, jr])}}
    rec["ii_scaled_by_max"] = float(d.max() / np.abs(Cn).max())
    rec["iii_max_diag_scaled"] = rec["a_entries"]["max_scaled"]
    rec["iv_bitwise_equal"] = bool(np.array_equal(QA, Cn))
    x = np.asarray(qa["x"], np.float64)
    F = np.asarray(s5a["functionals"], np.float64)
    rec["d_x_equal_partc_r2"] = bool(np.array_equal(x, np.asarray(qr["x"], np.float64)))
    rec["d_F_equal_partc_r2"] = bool(np.array_equal(F, np.asarray(s5r["functionals"], np.float64)))
    rows = [r for r in csv.DictReader(open(os.path.join(D, SPEC)), delimiter="\t") if r["source"] == "budget_Q"]
    mA, mC = bq.metrics(QA, x, F), bq.metrics(Cn, x, F)
    b_rows, c_rows = [], []
    w = flux_w(cons_raw.decode())
    ref_band = {}
    for r in rows:
        p = r["path"]
        if p in ("Q.median_pct", "Q.integral_sigma_pct"):
            k = p.split(".")[1]
            got = {"route_a_metrics": rv.render(mA[k], r["transform"], r["fmt"]),
                   "c_new_metrics": rv.render(mC[k], r["transform"], r["fmt"]),
                   "route_a_budget": rv.render(rv.extract(bud_a, p), r["transform"], r["fmt"])}
            b_rows.append({"id": r["id"], "path": p, "fmt": r["fmt"], "printed_purity": r["printed"], **got,
                           "pass": len(set(got.values())) == 1})
        elif p.startswith("bands."):
            _, b, k = p.split(".", 2)
            if f"band__{b}" in data:
                if b not in ref_band:
                    X = np.asarray(data[f"band__{b}"], np.float64)
                    ref_band[b] = bq.metrics(BR.wcov(X, w if b == "Flux" else np.ones(X.shape[0])), x, F)
                ref, src = ref_band[b][k], "g2r band__%s (wcov)" % b
            else:
                ref, src = rv.extract(bud_r, p), "partc-r2 budget_Q (not rebuilt by G2R)"
            ra, rr = rv.render(rv.extract(bud_a, p), r["transform"], r["fmt"]), rv.render(ref, r["transform"], r["fmt"])
            c_rows.append({"id": r["id"], "path": p, "fmt": r["fmt"], "printed_purity": r["printed"], "reference": src,
                           "route_a_budget": ra, "reference_rendered": rr, "pass": ra == rr})
    rec["b_q_printed"] = {"rows": b_rows, "pass": bool(b_rows) and all(r["pass"] for r in b_rows)}
    rec["c_band_printed"] = {"rows": c_rows, "pass": bool(c_rows) and all(r["pass"] for r in c_rows)}
    dU = np.asarray(s5a["universe"], np.float64) - np.asarray(s5r["universe"], np.float64)
    dE = np.asarray(data["C_univ_new"], np.float64) - np.asarray(data["C_univ_old"], np.float64)
    rec["universe_delta_scaled_rel"] = float(np.abs(dU - dE).max() / np.abs(dE).max())
    ok = (rec["a_entries"]["pass"] and rec["b_q_printed"]["pass"] and rec["c_band_printed"]["pass"]
          and rec["d_x_equal_partc_r2"] and rec["d_F_equal_partc_r2"])
    rec["verdict"] = "PASS" if ok else "FAIL"
    return finish(a, rec)


def finish(a, rec):
    with open(a.out, "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    e, r = rec.get("a_entries", {}), rec.get("i_per_entry_rel", {})
    bad_b = [x["id"] for x in rec.get("b_q_printed", {}).get("rows", []) if not x["pass"]]
    bad_c = [x["id"] for x in rec.get("c_band_printed", {}).get("rows", []) if not x["pass"]]
    print(f"C1 {rec['verdict']}: (a) max_scaled={e.get('max_scaled')} n_above={e.get('n_above')} worst={e.get('worst')}; "
          f"(i) per-entry max_rel={r.get('max')} n_above_1e-15={r.get('n_above_1e-15')} worst={r.get('worst')}; "
          f"(ii) {rec.get('ii_scaled_by_max')}; (iv) bitwise={rec.get('iv_bitwise_equal')}; "
          f"(b) rows={len(rec.get('b_q_printed', {}).get('rows', []))} failing={bad_b}; "
          f"(c) rows={len(rec.get('c_band_printed', {}).get('rows', []))} failing={bad_c}; "
          f"(d) x={rec.get('d_x_equal_partc_r2')} F={rec.get('d_F_equal_partc_r2')}; "
          f"universe_delta_scaled_rel={rec.get('universe_delta_scaled_rel')}")
    return 0 if rec["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
