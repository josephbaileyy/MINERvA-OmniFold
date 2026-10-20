#!/usr/bin/env python3
"""MP-2 S0 step 1: per-event feature tables for the descriptive probe (mp2_s0_declaration.json).

Tune v1: a seeded 2M-row subsample of the S1 dump's eligible rows (pass_truth, inside the fine 5D grid, 0.5 <= E_nu
<= 50 GeV, hydrogen EXCLUDED: mc_targetZ != 1). The 5 scalars are of_inputs_5d's MCgen columns and the weight its
w_truth. NuWro: every cc event of work_nuwro_p1..p8 in extract_nuwro's phase-space mask and inside the grid, with the
frozen chain's weight e.weight x r(E_nu) (gen5d_flux_reweight.flux_weights / r_of).

Control N0 (exit 3 on failure): the NuWro weight chain rebuilt here reproduces the frozen flux-fixed product
gen5d_fluxfix/nuwro_cv_xsec5d.npz (xsec_flat, sumw2_flat) bitwise, over extract_nuwro's own row set.
Control N1: the NuWro scalars read with the particles (flat tree) are the frozen flat files' rows, and the flat pz
equals the last muon's post pz / 1000 for every event (row alignment of treeout and nuwro_obs).

Usage (omnifold_py310): python3 mp2_s0_features.py S1DIR DECLARATION OUTDIR
"""
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

NS = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
G = f"{NS}/3d-unfolding/genie"
OFIN = f"{NS}/nd-unfolding/of_inputs_5d.npz"
OFIN_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
FLAT = [f"{S5P}/gen5d/nuwro_flat5d/nuwro_flat5d_p{i}.root" for i in range(1, 9)]
RAW = [f"{G}/work_nuwro_p{i}/nuwro_p{i}.root" for i in range(1, 9)]
FLUX = f"{G}/flux_mefhc_numu_nuwro.root"
PHI_T = f"{S5P}/gen5d_fluxfix"
PRODUCT = f"{S5P}/gen5d_fluxfix/nuwro_cv_xsec5d.npz"
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
A_BEAM = -0.05887
MAX_THETA = math.radians(20.0)
EDGES5 = [np.asarray(e, float) for e in (
    [0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5],
    [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60],
    [0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100], [0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100], [0, 1.1, 1.4, 1.8, 2.2, 3.0, 100])]
FULL = ["pt", "pz", "eavail", "q3", "W", "enu", "n_p", "n_n", "n_pipm", "n_pi0", "n_gamma", "n_other",
        "p1_KE", "p1_cos", "n1_KE", "pipm1_KE", "pipm1_cos", "pi01_E", "sum_p_KE", "sum_n_KE"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def in_grid(cols):
    ok = np.ones(cols[0].size, bool)
    for c, e in zip(cols, EDGES5):
        with np.errstate(invalid="ignore"):
            ok &= np.isfinite(c) & (c >= e[0]) & (c <= e[-1])
    return ok


def particle_features(pdg, E, px, py, pz, off, rotate):
    """Per-event features from ragged particles (MeV). rotate: MAT RotateX(A_BEAM) of the momenta first."""
    n_ev = off.size - 1
    cnt = np.diff(off)
    row = np.repeat(np.arange(n_ev), cnt)
    if rotate:
        s, c = math.sin(A_BEAM), math.cos(A_BEAM)
        py, pz = c * py - s * pz, s * py + c * pz
    p2 = px * px + py * py + pz * pz
    KE = E - np.sqrt(np.maximum(E * E - p2, 0.0))
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = pz / np.sqrt(p2)
    a = np.abs(pdg)
    excl = np.isin(a, [11, 12, 13, 14, 16]) | (a >= 1000000000)
    sp = {"p": (pdg == 2212) & (KE > 100.0), "n": (pdg == 2112) & (KE > 50.0), "pipm": (a == 211) & (KE > 50.0),
          "pi0": pdg == 111, "gamma": (pdg == 22) & (E > 10.0)}
    known = (pdg == 2212) | (pdg == 2112) | (a == 211) | (pdg == 111) | (pdg == 22)
    sp["other"] = ~excl & ~known
    f = {}
    for k, m in sp.items():
        f[f"n_{k}"] = np.bincount(row[m], minlength=n_ev).astype(np.float32)

    def leading(m, val, extra=None):
        out = np.full(n_ev, np.nan)
        out_x = np.full(n_ev, np.nan)
        idx = np.nonzero(m)[0]
        if idx.size:
            o = np.lexsort((val[idx], row[idx]))       # by row, then ascending val: the last per row is the max
            idx = idx[o]
            last = np.ones(idx.size, bool)
            last[:-1] = row[idx][1:] != row[idx][:-1]
            sel = idx[last]
            out[row[sel]] = val[sel]
            if extra is not None:
                out_x[row[sel]] = extra[sel]
        return out, out_x
    f["p1_KE"], f["p1_cos"] = leading(sp["p"], KE, cos)
    f["n1_KE"], _ = leading(sp["n"], KE)
    f["pipm1_KE"], f["pipm1_cos"] = leading(sp["pipm"], KE, cos)
    f["pi01_E"], _ = leading(sp["pi0"], E)
    f["sum_p_KE"] = np.bincount(row[sp["p"]], KE[sp["p"]], minlength=n_ev)
    f["sum_n_KE"] = np.bincount(row[sp["n"]], KE[sp["n"]], minlength=n_ev)
    return f


def nuwro(decl, res):
    import awkward as ak
    import uproot
    import gen5d_flux_reweight as gfr
    acc = {k: [] for k in ("cc", "pt", "pz", "eavail", "q3", "W", "Enu", "weight")}
    feats, n_total, n1 = [], 0, {"pz_last_muon_equal_rows": 0, "rows": 0}
    for fr, ff in zip(RAW, FLAT):
        ft = uproot.open(ff)
        n_total += int(ft["nTotal"].member("fVal"))
        d = ft["nuwro_obs"].arrays(list(acc), library="np")
        t = uproot.open(fr)["treeout"]
        if t.num_entries != d["cc"].size:
            raise SystemExit(f"{fr}: treeout {t.num_entries} != flat {d['cc'].size}")
        a = t.arrays(["e/post/post.pdg", "e/post/post.t", "e/post/post.x", "e/post/post.y", "e/post/post.z"],
                     library="ak")
        pdg = a["e/post/post.pdg"]
        mz = a["e/post/post.z"][np.abs(pdg) == 13]
        lastpz = ak.to_numpy(ak.fill_none(ak.firsts(mz[:, ::-1]), -9999.0 * 1000.0)) / 1000.0
        n1["pz_last_muon_equal_rows"] += int(np.sum(lastpz == d["pz"]))
        n1["rows"] += int(d["pz"].size)
        off = np.zeros(len(pdg) + 1, np.int64)
        np.cumsum(ak.to_numpy(ak.num(pdg)), out=off[1:])
        flat = [ak.to_numpy(ak.flatten(a[k])) for k in ("e/post/post.pdg", "e/post/post.t", "e/post/post.x",
                                                         "e/post/post.y", "e/post/post.z")]
        feats.append(particle_features(*flat, off, rotate=False))
        for k in acc:
            acc[k].append(d[k])
        res["inputs"][fr] = {"sha256": sha256(fr)}
        res["inputs"][ff] = {"sha256": sha256(ff)}
    d = {k: np.concatenate(v) for k, v in acc.items()}
    fe = {k: np.concatenate([f[k] for f in feats]) for k in feats[0]}
    n1["pass"] = n1["pz_last_muon_equal_rows"] == n1["rows"]
    res["controls"]["N1_nuwro_alignment"] = n1
    # frozen flux-fix weights (gen5d_flux_reweight.cmd_reweight, nuwro branch)
    z, meta, _ = gfr.load_phi_t(PHI_T)
    h = uproot.open(FLUX)["flux_numu"]
    e_s, c_s = np.asarray(h.axis().edges(), float), np.asarray(h.values(), float)
    lo, hi = gfr.GEN_RANGE["nuwro"]
    phi_s, rbin, rng = gfr.flux_weights(e_s, c_s, z["phi_t_density"], float(z["Phi_t"]), lo, hi)
    r_all = gfr.r_of(d["Enu"], e_s, rbin, rng)
    ccm = d["cc"].astype(bool)
    pt, pz = d["pt"], d["pz"]
    m = ccm & np.isfinite(pt) & np.isfinite(pz) & (pt >= EDGES5[0][0]) & (pt <= EDGES5[0][-1]) \
        & (pz >= EDGES5[1][0]) & (pz <= EDGES5[1][-1])
    with np.errstate(invalid="ignore"):
        m &= np.arctan2(pt, pz) < MAX_THETA
    # N0: the frozen product from extract_nuwro's row set (cc, then the PS mask; same row order)
    cols = [d[k][m] for k in ("pt", "pz", "eavail", "q3", "W")]
    wr = d["weight"][m] * r_all[m]
    dV5 = np.diff(EDGES5[0])
    for e in EDGES5[1:]:
        dV5 = np.multiply.outer(dV5, np.diff(e))
    x5 = np.histogramdd(np.column_stack(cols), bins=EDGES5, weights=wr)[0] / float(n_total) / dV5 * 1.0
    v5 = np.histogramdd(np.column_stack(cols), bins=EDGES5, weights=wr * wr)[0] / float(n_total) ** 2 / dV5 ** 2 * 1.0
    P = np.load(PRODUCT, allow_pickle=True)
    n0 = {"N_total": n_total, "n_cc": int(ccm.sum()), "n_ps": int(m.sum()),
          "xsec_bitwise": bool(np.array_equal(x5.reshape(-1), np.asarray(P["xsec_flat"]))),
          "sumw2_bitwise": bool(np.array_equal(v5.reshape(-1), np.asarray(P["sumw2_flat"]))),
          "product_sha256": sha256(PRODUCT), "phi_t_npz_sha256": meta["npz_sha256"], "flux_sha256": sha256(FLUX)}
    nz = np.asarray(P["xsec_flat"]) != 0
    n0["xsec_max_rel"] = float(np.max(np.abs(x5.reshape(-1)[nz] - np.asarray(P["xsec_flat"])[nz])
                                      / np.abs(np.asarray(P["xsec_flat"])[nz])))
    n0["pass"] = n0["xsec_bitwise"] and n0["sumw2_bitwise"]
    res["controls"]["N0_nuwro_weight_chain"] = n0
    ok = m & in_grid([d[k] for k in ("pt", "pz", "eavail", "q3", "W")]) & (d["Enu"] >= 0.5) & (d["Enu"] <= 50.0)
    X = {"pt": pt, "pz": pz, "eavail": d["eavail"], "q3": d["q3"], "W": d["W"], "enu": d["Enu"]}
    X.update(fe)
    out = {k: np.asarray(X[k], float)[ok] for k in FULL}
    out["w"] = (d["weight"] * r_all)[ok]
    res["nuwro"] = {"n_selected": int(ok.sum()), "n_ps_not_in_grid": int((m & ~ok).sum()),
                    "sum_w": float(out["w"].sum()), "n_w_zero": int((out["w"] == 0).sum())}
    return out


def tune(s1dir, decl, res):
    sub = decl["population"]["tune_v1_subsample"]
    z = np.load(OFIN, allow_pickle=True)
    MCgen = np.asarray(z["MCgen"])
    WT = np.asarray(z["w_truth"], float)
    PT = np.asarray(z["pass_truth"], bool)
    elig_parts, meta = [], {}
    for p in PLAYLISTS:
        s = np.load(f"{s1dir}/s1_{p}.npz")
        r0, n = int(s["mcgen_row0"]), int(s["n_rows"])
        g = MCgen[r0:r0 + n].astype(float)
        enu = np.asarray(s["mc_incomingE"]) / 1000.0
        ok = PT[r0:r0 + n] & in_grid([g[:, i] for i in range(5)]) & (enu >= 0.5) & (enu <= 50.0) \
            & (np.asarray(s["mc_targetZ"]) != 1) & np.isfinite(WT[r0:r0 + n])
        meta[p] = {"r0": r0, "n": n, "n_eligible": int(ok.sum()),
                   "n_H_excluded": int((PT[r0:r0 + n] & (np.asarray(s["mc_targetZ"]) == 1)).sum())}
        elig_parts.append(r0 + np.nonzero(ok)[0])
    elig = np.concatenate(elig_parts)
    rng = np.random.default_rng(sub["seed"])
    pick = np.sort(rng.choice(elig, size=min(sub["n"], elig.size), replace=False))
    out = {k: [] for k in FULL + ["w", "mcgen_row", "targetZ"]}
    for p in PLAYLISTS:
        r0, n = meta[p]["r0"], meta[p]["n"]
        rows = pick[(pick >= r0) & (pick < r0 + n)] - r0
        s = np.load(f"{s1dir}/s1_{p}.npz")
        off = np.asarray(s["fs_offsets"])
        st, cnt = off[rows], np.diff(off)[rows]
        o2 = np.zeros(rows.size + 1, np.int64)
        np.cumsum(cnt, out=o2[1:])
        gi = np.repeat(st - o2[:-1], cnt) + np.arange(o2[-1], dtype=np.int64)
        fe = particle_features(*(np.asarray(s[k])[gi] for k in ("fs_pdg", "fs_E", "fs_px", "fs_py", "fs_pz")), o2,
                               rotate=True)
        g = MCgen[r0 + rows].astype(float)
        X = {"pt": g[:, 0], "pz": g[:, 1], "eavail": g[:, 2], "q3": g[:, 3], "W": g[:, 4],
             "enu": np.asarray(s["mc_incomingE"])[rows] / 1000.0}
        X.update(fe)
        for k in FULL:
            out[k].append(np.asarray(X[k], float))
        out["w"].append(WT[r0 + rows])
        out["mcgen_row"].append(r0 + rows)
        out["targetZ"].append(np.asarray(s["mc_targetZ"])[rows])
    out = {k: np.concatenate(v) for k, v in out.items()}
    res["tune_v1"] = {"n_eligible": int(elig.size), "n_selected": int(pick.size), "per_playlist": meta,
                      "n_H_excluded_total": int(sum(v["n_H_excluded"] for v in meta.values())),
                      "selected_targetZ_counts": {str(int(a)): int(b) for a, b in
                                                  zip(*np.unique(out["targetZ"], return_counts=True))},
                      "sum_w": float(out["w"].sum())}
    return out


def main():
    s1dir, declp, outd = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    outd.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    decl = json.loads(declp.read_text())
    import gen5d_flux_reweight as gfr
    res = {"schema": "mp2-s0-features/1", "argv": sys.argv, "slurm_job": os.environ.get("SLURM_JOB_ID"),
           "declaration_sha256": sha256(declp), "code": {}, "inputs": {}, "controls": {}}
    for m in (sys.modules[__name__], gfr):
        p = Path(m.__file__).resolve()
        res["code"][m.__name__] = {"file": str(p), "sha256": sha256(p)}
    z = np.load(OFIN, allow_pickle=True)
    if not all(np.array_equal(np.asarray(z[f"edges_{i}"], float), EDGES5[i]) for i in range(5)):
        raise SystemExit("of_inputs_5d edges differ from the declared grid")
    nw = nuwro(decl, res)
    print("N0", json.dumps(res["controls"]["N0_nuwro_weight_chain"]), flush=True)
    print("N1", json.dumps(res["controls"]["N1_nuwro_alignment"]), flush=True)
    if not (res["controls"]["N0_nuwro_weight_chain"]["pass"] and res["controls"]["N1_nuwro_alignment"]["pass"]):
        res["exit"] = 3
        (outd / "s0_features.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        return 3
    tv = tune(s1dir, decl, res)
    np.savez(outd / "s0_nuwro.npz", **nw)
    np.savez(outd / "s0_tune.npz", **tv)
    for k in ("s0_nuwro.npz", "s0_tune.npz"):
        res[k] = sha256(outd / k)
    res["wall_s"], res["exit"] = round(time.time() - t0, 1), 0
    (outd / "s0_features.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("FEATURES", json.dumps({"nuwro": res["nuwro"], "tune_n": res["tune_v1"]["n_selected"],
                                  "tune_H_excluded": res["tune_v1"]["n_H_excluded_total"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
