#!/usr/bin/env python3
"""COV2D-G2R §3-§5, the readout, on a login node (root_6_28 with the pinned MAT environment, as COV2D's readout):

* ``data``: part (a). The 175 corrected universe products at the data give C_univ,new by the rollup's own band_cov;
  C_new = Q_R - C_univ,old + C_univ,new, with C_univ,old the 38 weight bands of part B's S5_R (production_cov.npz's
  band_<b>). The record gives §3's readings of C_new against Q_R, the noise floor of the two override-off reruns, and
  the controls G6 (band_cov on part B's own 175 products reproduces each band_<b> to 1e-12 relative, as COV2D's
  section 9.5) and G10 (re2c_build_q.metrics on Q_R reproduces budget_Q.json's median and integral sigma).
* ``tune``: part (+), at one tune. The 175 corrected universe products on d̃_T give the corrected universe bands; C_T'
  keeps every other block of the committed blocks_<T>.npz (g2r.c_t_prime). The null is recomputed at C_T' (COV2D's
  cov2d_null.null_at_T, unchanged) and written before the committed errors are read against it. The 300 committed
  errors (E_<T>.npz) are graded by cov2d_score.score and the leave-out-MEC readout, with section 6's readouts. Controls
  G6 (c_t_prime on the OLD bands reproduces blocks_<T>.npz's C_univ, C_T and C_T_minus bitwise) and G7 (the committed
  errors against the committed C_T and null reproduce score_<T>.json's grade) run first.

  python g2r_readout.py data --products TSV --map-sha SHA --out DIR
  python g2r_readout.py tune --truth T --products TSV --map-sha SHA --out DIR

The products TSV: label, path, sha256, role (g2r | off), universe (BAND:IDX). Each product is read through O_NOATIME
at its digest, and its provenance must record g2rMissMap with the map's sha256 and its own universe (role g2r), or no
g2rMissMap (role off), and at a tune the realization's dataFileSha256.

Exit 0 when the record is written with every control passing; 5 INVALID; 8 if an atime moved.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
COV2D = HERE.parent
REPO = COV2D.parents[1]
sys.path[:0] = [str(HERE), str(COV2D), str(REPO / "nd-unfolding"), str(REPO / "2d-unfolding" / "re2" / "partc")]
import g2r  # noqa: E402

REC = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d"
T2A = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier2-20261110/t2a"
OUTA = REPO / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/outA"
# The committed inputs of the regrade, at their digests (OUTCOME-20261108; T2A's receipt and its PINS).
COMMITTED = {
    "AR23": {"blocks": (REC / "readout/AR23/blocks_AR23.npz",
                        "abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee"),
             "null": (REC / "readout/AR23/null_AR23.json",
                      "80274e52c23365e5c6f84fad977576e54507bf186e1d04a8da8d596a75b0ac76"),
             "score": (REC / "readout/AR23/score_AR23.json",
                       "fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1"),
             "E": (T2A / "AR23/E_AR23.npz", "ccda9c50c6bb1cbbdd2206c8954652f4f77c6cf2b4451e8488601e9896b0a85e")},
    "G18": {"blocks": (REC / "readout/G18/blocks_G18.npz",
                       "7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d"),
            "null": (REC / "readout/G18/null_G18.json",
                     "6bd5259d61b062af7b3a8b09af78fc544e3eba48e35a062a28fdcd923b90f6e0"),
            "score": (REC / "readout/G18/score_G18.json",
                      "849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec"),
            "E": (T2A / "G18/E_G18.npz", "846b9d852218b531d605bd955ca9a9037d187e74723077bdfff4557efafc3ba6")},
}
# Part (a)'s inputs on pscratch (RE2-PARTC-REPORT.md §2, chain of custody) and the committed budget record.
PARTC = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2"
S5_NPZ = (f"{PARTC}/s5/production_cov.npz", "631cf255fff43b5cb35acd9cefdcee99e5ee95b85dc2f30d8e0aca513095eea1")
Q205_NPZ = (f"{PARTC}/outA/cov2d_Q_205.npz", "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2")
BUDGET_Q = "bbe13622656e9f43978d9cb022ac74ca4ba059b1cf56fed9e082bfb3b1be03aa"   # outA/budget_Q.json (committed .gz)
GRADE_EXACT = ("ndf", "counts", "k_cell", "cell_flag", "joint_count", "k_joint", "flagged_cells", "verdict")
RC_INVALID, RC_ATIME = 5, 8


# ------------------------------------------------------------------------------------------------ the pure cores
def grade_reproduces(g_new: dict, g_old: dict, chi2_tol: float) -> dict:
    """G7: the regrade code's grade of the committed errors against the committed C_T and null equals the committed
    grade: every integer field exactly, mean chi2/ndf to COV2D A5's tolerance."""
    diff = [k for k in GRADE_EXACT if g_new.get(k) != g_old.get(k)]
    rel = abs(g_new["chi2_mean_over_ndf"] - g_old["chi2_mean_over_ndf"]) / abs(g_old["chi2_mean_over_ndf"])
    return {"fields_differing": diff, "chi2_rel_diff": rel, "chi2_tol": chi2_tol,
            "pass": not diff and rel <= chi2_tol}


def old_bands(B: dict, order) -> dict:
    return {b: np.asarray(B[f"band__{b}"], np.float64) for b in order}


G6_TOL = 1e-12            # the declaration §8: "to 10^-12 relative" (bitwise depends on the BLAS: see the receipts)


def g6_tune(B: dict, rebuilt: dict) -> dict:
    """G6 at a tune: c_t_prime on the OLD bands reproduces the committed blocks to 1e-12 relative (max |diff| / max
    |committed|), as the declaration's §8 states; whether it is also bitwise is recorded."""
    keys = ["C_univ", "C_T"] + (["C_T_minus"] if "C_T_minus" in B else [])
    rel = {k: float(np.max(np.abs(np.asarray(rebuilt[k]) - np.asarray(B[k]))) / float(np.max(np.abs(np.asarray(B[k])))))
           for k in keys}
    bitwise = {k: bool(np.array_equal(np.asarray(rebuilt[k]), np.asarray(B[k]))) for k in keys}
    differ = [k for k in keys if not rel[k] <= G6_TOL]
    return {"compared": keys, "rel_diff": rel, "bitwise": bitwise, "tol": G6_TOL, "differing": differ,
            "pass": not differ}


def data_core(s5: dict, Q: np.ndarray, new_bands: dict, w_flux, band_cov, order, flux: str) -> dict:
    """Part (a): C_univ,old from S5_R's band_<b>, C_univ,new from the corrected bands by band_cov, and C_new."""
    missing = [b for b in order if f"band_{b}" not in s5]
    if missing or set(new_bands) != set(order):
        raise g2r.Refusal(f"data: bands missing from S5_R {missing} or from the products "
                          f"{sorted(set(order) ^ set(new_bands))}")
    old = sum(np.asarray(s5[f"band_{b}"], np.float64) for b in sorted(order))
    new = sum(band_cov(np.asarray(new_bands[b], np.float64), w_flux if b == flux else None) for b in sorted(order))
    return {"C_univ_old": old, "C_univ_new": new, "C_new": np.asarray(Q, np.float64) - old + new}


def floor_core(Q: np.ndarray, bands_old: dict, offs: dict, w_flux, band_cov, flux: str) -> dict:
    """The noise floor (§3): Q_R with each override-off rerun's row put in place of part B's row of the same universe.
    ``offs``: {(band, idx): vector}. Bitwise-equal reruns give a floor of exactly zero."""
    Qf = np.asarray(Q, np.float64).copy()
    equal = {}
    for (b, i), v in offs.items():
        X_old = np.asarray(bands_old[b], np.float64)
        X_new = X_old.copy()
        X_new[i] = np.asarray(v, np.float64)
        equal[f"{b}:{i}"] = bool(np.array_equal(X_new[i], X_old[i]))
        w = w_flux if b == flux else None
        Qf += band_cov(X_new, w) - band_cov(X_old, w)
    return {"bitwise_equal": equal, "Q_floor": Qf}


def regrade_core(B: dict, new: dict, E: np.ndarray, truth: str, flat: list, weak: np.ndarray, controls_failed: list,
                 M: str, write_null=None, n_mc: int | None = None) -> dict:
    """At one tune: the null at C_T' from the corrected bands (cov2d_null.null_at_T), handed to ``write_null`` before
    any error is read against it; then the committed errors graded against C_T' (cov2d_score.score, with COV2D A5's
    Cholesky tolerance from C_T' alone), the leave-out-MEC readout against C_T'- and its null, section 6's readouts
    that need only the blocks, and the tune-level eps of C_T' against the committed C_T."""
    import cov2d_null as cn
    import cov2d_readout as crd
    import cov2d_readouts as cr
    import cov2d_score as cs
    kw = {} if n_mc is None else {"n_mc": n_mc}
    res = cn.null_at_T(new, new["bands"], B["minos_x"], B["w_flux"], **kw)
    nrec = crd.jsonable({"schema": g2r.SCHEMA, "truth": truth, "null": res["null"], "thresholds": res["thresholds"],
                         "size": res["size"], "null_minus": res.get("null_minus"), "M": M})
    if write_null is not None:
        write_null(nrec)
    null, null_minus = crd.null_from_json(nrec["null"]), crd.null_from_json(nrec["null_minus"])
    chol, chol_minus = crd.cholesky_tol(new["C_T"]), crd.cholesky_tol(new["C_T_minus"])
    g = cs.score(E, new["C_T"], null, truth, flat, weak, list(controls_failed), chol_tol=chol["tol"])
    lom = cr.leave_out_mec(E, {"C_T_minus": new["C_T_minus"]}, null_minus, g, flat, chol_tol=chol_minus["tol"])
    sigma = np.sqrt(np.diag(new["C_T"]))
    readouts = {"spread_alone": cr.spread_alone(E, new["C_T"], new["C_model_abs"]), "bias": cr.bias(E, sigma),
                "predicted_offset": cr.predicted_offset(new["bands"], B["w_flux"], B["x_T"]), "leave_out_mec": lom}
    return {"null_record": nrec, "grade": g, "cholesky_check": chol, "cholesky_check_minus": chol_minus,
            "readouts": readouts, "tune_eps": g2r.readings(B["C_T"], new["C_T"])}


# ---------------------------------------------------------------------------------------------------- the I/O
def read_products(tsv: Path, map_sha: str, role_want: str, data_sha: str | None, tmp: Path, read_pinned,
                  read_provenance) -> dict:
    """{(band, idx): path of a private copy} for the rows of role ``role_want``, each read at its digest through
    O_NOATIME and its provenance checked."""
    out = {}
    with open(tsv, newline="") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if not row or row[0].startswith("#"):
                continue
            label, path, digest, role, uni = row
            if role != role_want:
                continue
            band, idx = uni.split(":")
            dst = tmp / f"{label}.root"
            dst.write_bytes(read_pinned(path, digest))
            prov = read_provenance(dst)
            mm = json.loads(prov["g2rMissMap"]) if "g2rMissMap" in prov else None
            if role == "g2r" and (mm is None or mm.get("sha256") != map_sha or mm.get("universe") != uni):
                raise g2r.Refusal(f"{label}: g2rMissMap {mm} does not name map {map_sha} and universe {uni}")
            if role == "off" and mm is not None:
                raise g2r.Refusal(f"{label}: an override-off rerun records g2rMissMap")
            if data_sha is not None and prov.get("dataFileSha256") != data_sha:
                raise g2r.Refusal(f"{label}: dataFileSha256 {prov.get('dataFileSha256')} is not the realization's")
            if (band, int(idx)) in out:
                raise g2r.Refusal(f"{label}: universe {uni} twice")
            out[(band, int(idx))] = dst
    return out


def tsv_paths(tsv: Path) -> list[str]:
    """Every product path the TSV names, for the atime ledger (G9)."""
    with open(tsv, newline="") as fh:
        return [row[1] for row in csv.reader(fh, delimiter="\t") if row and not row[0].startswith("#")]


def stack_bands(products: dict, vec, order, bands_n) -> dict:
    want = {(b, i) for b in order for i in range(bands_n[b])}
    if set(products) != want:
        raise g2r.Refusal(f"products: {len(set(products) ^ want)} universes missing or extra")
    return {b: np.stack([vec(products[(b, i)]) for i in range(bands_n[b])]) for b in order}


def phase_tune(truth: str, tsv: Path, map_sha: str, out: Path) -> dict:
    import cov2d as c
    import cov2d_blocks as cb
    import cov2d_readout as crd
    import cov2d_score as cs
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        run = crd.Run(truth, crd.RUN_DIR, Path(td))
        rec, ro = run.rec, run.ro
        rec.update(schema=g2r.SCHEMA, step="tune", map_sha256=map_sha)
        pins = {k: crd.read_pinned(*COMMITTED[truth][k]) for k in ("blocks", "null", "score", "E")}
        B = dict(np.load(io.BytesIO(pins["blocks"]), allow_pickle=False))
        old_null, old_score = json.loads(pins["null"]), json.loads(pins["score"])
        with np.load(io.BytesIO(pins["E"]), allow_pickle=False) as z:
            E, seeds = np.asarray(z["E"], np.float64), [int(s) for s in z["seeds"]]
        if seeds != list(c.TOY_SEEDS[truth]) or E.shape != (300, 205):
            raise c.Refusal("E is not the declared 300 toys in seed order on 205 cells")
        flat = [int(i) for i in np.flatnonzero(B["rep"])]
        ratio_rec = json.loads(crd.read_pinned(*crd.C2_RECORD))
        weak = np.asarray(ratio_rec["b"][truth]["variance_ratio"]["option_1_clipped"], np.float64)
        _, C_minus, rec["c_model"] = cb.c_model()
        cells = cb.CellsT(B["rep"], B["x_T"])
        # G7, first: the committed grade from the committed errors, C_T and null
        tol_old = crd.cholesky_tol(B["C_T"])
        g_old = cs.score(E, B["C_T"], crd.null_from_json(old_null["null"]), truth, flat, weak,
                         chol_tol=tol_old["tol"])
        rec["G7"] = grade_reproduces(g_old, old_score["grade"], tol_old["tol"])
        # G6: the rebuild on the OLD bands reproduces the committed blocks
        re_old = g2r.c_t_prime(B, old_bands(B, c.ORDER), ro.universe_block, cells, c.ORDER, c.LATERAL_BANDS,
                               cb.NORM_KEY, C_minus)
        rec["G6"] = g6_tune(B, re_old)
        for k in ("G7", "G6"):
            if not rec[k]["pass"]:
                rec["controls_failed"].append(f"{k} failed")
        if rec["controls_failed"]:
            rec["verdict"] = "INVALID"
            return run.finish(out, f"score_g2r_{truth}.invalid.json")
        # the corrected products
        er = run.er_cells()
        if not np.array_equal(np.asarray(er.rep, bool), B["rep"].astype(bool)):
            raise c.Refusal("E_R's cells differ from blocks_<T>.npz's")
        real_sha = crd.data_shas(truth)[c.REALIZATION_SEED[truth]]
        for p in tsv_paths(tsv):
            run.watch(p)
        prods = read_products(tsv, map_sha, "g2r", real_sha, Path(td), crd.read_pinned, crd.read_provenance)
        new_bands = stack_bands(prods, er.vec, c.ORDER, c.BANDS)
        new = g2r.c_t_prime(B, new_bands, ro.universe_block, cells, c.ORDER, c.LATERAL_BANDS, cb.NORM_KEY, C_minus)
        rec["section_9_8"] = cb.psd_checks(new["C_T"])
        if not rec["section_9_8"]["pass"]:
            rec["controls_failed"].append("section 9.8: C_T' is not symmetric PSD at 1e-12")
        # the null at C_T' (written before the errors are read against it), then the regrade
        core = regrade_core(B, new, E, truth, flat, weak, rec["controls_failed"], rec["M"],
                            write_null=lambda nrec: (out / f"null_g2r_{truth}.json").write_text(
                                json.dumps(crd.jsonable(nrec), indent=1, sort_keys=True)))
        np.savez(out / f"blocks_g2r_{truth}.npz", **g2r.blocks_npz_arrays(B, new))
        rec["null_digest"] = crd.sha((out / f"null_g2r_{truth}.json").read_bytes())
        rec["blocks_npz_sha256"] = crd.sha((out / f"blocks_g2r_{truth}.npz").read_bytes())
        g = core["grade"]
        rec.update(cholesky_check=core["cholesky_check"], cholesky_check_minus=core["cholesky_check_minus"], grade=g,
                   readouts=core["readouts"], tune_eps=core["tune_eps"])
        rec["verdict"] = g["verdict"]
        return run.finish(out, f"score_g2r_{truth}.json")


def phase_data(tsv: Path, map_sha: str, out: Path) -> dict:
    import cov2d as c
    import cov2d_blocks as cb
    import cov2d_readout as crd
    import re2c_build_q as bq
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        run = crd.Run("data", crd.RUN_DIR, Path(td))
        rec, ro = run.rec, run.ro
        rec.update(schema=g2r.SCHEMA, step="data", map_sha256=map_sha)
        for k in crd.ROLLUP_PINS:
            run.watch(ro.PIN[k][0])
        rec["inputs"] = cb.noatime_inputs(ro, Path(td) / "rollup", {k: ro.PIN[k] for k in crd.ROLLUP_PINS})
        w_flux, _ = ro.flux_weights()
        for p in (S5_NPZ[0], Q205_NPZ[0]):
            run.watch(p)
        s5 = dict(np.load(io.BytesIO(crd.read_pinned(*S5_NPZ)), allow_pickle=False))
        q205 = dict(np.load(io.BytesIO(crd.read_pinned(*Q205_NPZ)), allow_pickle=False))
        Q, x = np.asarray(q205["Q"], np.float64), np.asarray(q205["x"], np.float64)
        F = np.asarray(s5["functionals"], np.float64)
        er = run.er_cells()
        if not np.array_equal(np.asarray(er.x, np.float64), x):
            rec["controls_failed"].append("E_R's cells are not cov2d_Q_205.npz's x")
        # G10: metrics on Q_R reproduce the committed budget
        import gzip
        budget_raw = gzip.decompress((OUTA / "budget_Q.json.gz").read_bytes())
        if crd.sha(budget_raw) != BUDGET_Q:
            raise c.Refusal("budget_Q.json is not at its digest")
        bud = json.loads(budget_raw)["Q"]
        m = bq.metrics(Q, x, F)
        g10 = {k: [m[k], bud[k]] for k in ("median_pct", "integral_sigma_pct")}
        rec["G10"] = {"values": g10, "pass": all(abs(a - b) <= 1e-12 * abs(b) for a, b in g10.values())}
        # G6: band_cov on part B's own 175 products reproduces S5_R's bands
        sums = ro.partb_sums()
        old_paths = {(b, i): run.copy(f"{ro.NS_R}/out/U_{b}_{i}/xsec.root", sums[f"U_{b}_{i}/xsec.root"],
                                      f"U_{b}_{i}.root") for b in c.ORDER for i in range(c.BANDS[b])}
        bands_old = stack_bands(old_paths, er.vec, c.ORDER, c.BANDS)
        g6 = {b: float(np.max(np.abs(ro.band_cov(bands_old[b], w_flux if b == c.FLUX else None) - s5[f"band_{b}"]))
                       / np.max(np.abs(s5[f"band_{b}"]))) for b in c.ORDER}
        rec["G6"] = {"worst_rel": max(g6.values()), "per_band": g6, "tol": cb.TOL, "pass": max(g6.values()) <= cb.TOL}
        for k in ("G10", "G6"):
            if not rec[k]["pass"]:
                rec["controls_failed"].append(f"{k} failed")
        if rec["controls_failed"]:
            rec["verdict"] = "INVALID"
            return run.finish(out, "data_g2r.invalid.json")
        for p in tsv_paths(tsv):
            run.watch(p)
        prods = read_products(tsv, map_sha, "g2r", None, Path(td), crd.read_pinned, crd.read_provenance)
        new_bands = stack_bands(prods, er.vec, c.ORDER, c.BANDS)
        core = data_core(s5, Q, new_bands, w_flux, ro.band_cov, c.ORDER, c.FLUX)
        rec["readings"] = g2r.readings(Q, core["C_new"], bq.metrics, x, F)
        offs = read_products(tsv, map_sha, "off", None, Path(td), crd.read_pinned, crd.read_provenance)
        fl = floor_core(Q, bands_old, {k: er.vec(p) for k, p in offs.items()}, w_flux, ro.band_cov, c.FLUX)
        rec["floor"] = {"bitwise_equal": fl["bitwise_equal"], "readings": g2r.readings(Q, fl["Q_floor"])}
        np.savez(out / "data_g2r.npz", C_new=core["C_new"], C_univ_old=core["C_univ_old"],
                 C_univ_new=core["C_univ_new"], **{f"band__{b}": v for b, v in new_bands.items()})
        rec["npz_sha256"] = crd.sha((out / "data_g2r.npz").read_bytes())
        rec["verdict"] = "PASS"
        return run.finish(out, "data_g2r.json")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="phase", required=True)
    for name in ("data", "tune"):
        p = sub.add_parser(name)
        if name == "tune":
            p.add_argument("--truth", required=True, choices=sorted(COMMITTED))
        p.add_argument("--products", required=True, type=Path)
        p.add_argument("--map-sha", required=True)
        p.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    rec = phase_tune(a.truth, a.products, a.map_sha, a.out) if a.phase == "tune" else \
        phase_data(a.products, a.map_sha, a.out)
    print(f"G2R-{a.phase.upper()} verdict={rec['verdict']} controls_failed={rec['controls_failed']} stop={rec['stop']}")
    if rec.get("atime_moved"):
        return RC_ATIME
    return 0 if rec["verdict"] not in ("INVALID", "STOP") else RC_INVALID


if __name__ == "__main__":
    sys.exit(main())
