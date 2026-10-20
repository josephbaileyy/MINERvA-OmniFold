#!/usr/bin/env python3
"""MP-5(a) step 2, the check of the proxy (GENIE CV only): rebuild the frozen GENIE 2.12.10 CV 5D prediction with the
muon angle measured from a fixed beam axis, by MP3-A's chain (gen_to_xsec5d.extract_genie's event arrays,
gen5d_flux_reweight.build_genie for the < 50 GeV sample, the gen5d_flux_supplement formula for 50-100 GeV).

Each gst event's lepton is rotated from GENIE's frame (nu along +z) into the MAT beam frame by a nu direction drawn
from the analysis MC (mp5_tune.py's pool), conditional on E_nu, with the declared seed (mp5_declaration.json). Only
pT, p_par, W (through theta) and the phase-space decision change; E_avail, q3, weights and normalization are frozen.

CONTROL G1 (before any rotated build is read): the same code path with n = z for every event reproduces
extract_genie's event arrays and the frozen < 50 GeV and full products bitwise (xsec and sumw2).
Usage: python3 mp5_genie.py OUTDIR POOLDIR DECLARATION S5C_CONTRACT
"""
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import gen5d_flux_reweight as gfr  # noqa: E402
import gen5d_flux_supplement as sup  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402

GEN = "genie_cv"
RAW = ["cc", "mec", "Ev", "pxv", "pyv", "pzv", "El", "pxl", "pyl", "pzl", "Q2", "hitnuc", "eav5d"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def rotate(px, py, pz, n):
    """R p with R the rotation by alpha = angle(z, n) about u = z x n / |z x n| (Rodrigues); R z = n.
    Where |z x n| = 0 the input is returned unchanged (bitwise)."""
    nx, ny, nz = n[:, 0], n[:, 1], n[:, 2]
    s = np.hypot(nx, ny)
    rot = s > 0
    s1_ = np.where(rot, s, 1.0)
    ux, uy = -ny / s1_, nx / s1_
    al = np.arctan2(s, nz)
    c, sn = np.cos(al), np.sin(al)
    udp = ux * px + uy * py
    qx = px * c + (uy * pz) * sn + ux * udp * (1.0 - c)
    qy = py * c - (ux * pz) * sn + uy * udp * (1.0 - c)
    qz = pz * c + (ux * py - uy * px) * sn
    return np.where(rot, qx, px), np.where(rot, qy, py), np.where(rot, qz, pz)


def events(ROOT, g5, path, n):
    """extract_genie's in-phase-space event arrays (gen_to_xsec5d.py:136-176) with the lepton taken as R(n) p for
    pT, p_par, W and the phase-space decision; E_avail and q3 from the unrotated vectors."""
    d = ROOT.RDataFrame("gst", path).Define("eav5d", g5.EAVAIL_CPP).AsNumpy(RAW)
    cc = d["cc"].astype(bool)
    mec = d["mec"].astype(bool)
    if n is None:
        n = np.tile([0.0, 0.0, 1.0], (cc.size, 1))
    qx, qy, qz = rotate(d["pxl"], d["pyl"], d["pzl"], n)
    pt = np.hypot(qx, qy)
    pz = qz
    in_ps = g5.u3d.u2d.in_truth_phase_space
    lo_t, hi_t, lo_z, hi_z = g5.PT[0], g5.PT[-1], g5.PZ[0], g5.PZ[-1]
    inps = np.fromiter((c and in_ps(float(a), float(b), lo_t, hi_t, lo_z, hi_z)
                        for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())), dtype=bool, count=cc.size)
    sel = np.where(inps)[0]
    Ev, pxv, pyv, pzv = (d[k][sel] for k in ("Ev", "pxv", "pyv", "pzv"))
    El = d["El"][sel]
    rx, ry, rz = qx[sel], qy[sel], qz[sel]
    W = np.fromiter((g5.gew.w_true((a, b, c, e), (f, g, h, i)) for a, b, c, e, f, g, h, i in
                     zip(Ev.tolist(), pxv.tolist(), pyv.tolist(), pzv.tolist(),
                         El.tolist(), rx.tolist(), ry.tolist(), rz.tolist())), dtype=float, count=sel.size)
    _, q3 = g5.q3_true(Ev, pxv, pyv, pzv, El, d["pxl"][sel], d["pyl"][sel], d["pzl"][sel])
    ev = {"pt": pt[sel], "pz": pz[sel], "eavail": d["eav5d"][sel], "q3": q3, "W": W, "is_mec": mec[sel]}
    info = {"n_entries": int(cc.size), "n_cc": int(cc.sum()), "n_in_ps": int(sel.size),
            "nu_along_z": bool(np.all(d["pxv"] == 0) and np.all(d["pyv"] == 0)),
            "Ev": d["Ev"], "cc": cc, "sel": sel}
    return ev, info


def draw_directions(u, Ev, pools, bins):
    """The declared draw: per E bin, the w_truth-weighted empirical pool, k = searchsorted(cdf, u, 'right')."""
    b = np.digitize(Ev, bins) - 1
    if np.any((b < 0) | (b >= len(pools))):
        raise SystemExit("an event outside the declared E_nu bins")
    n = np.empty((Ev.size, 3))
    for j, P in enumerate(pools):
        m = b == j
        cdf = np.cumsum(P[:, 3])
        cdf = cdf / cdf[-1]
        k = np.minimum(np.searchsorted(cdf, u[m], side="right"), len(P) - 1)
        n[m] = P[k, :3]
    return n


def main():
    out, pooldir, decl_p, contract_p = (Path(x) for x in sys.argv[1:5])
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    decl = json.loads(decl_p.read_text())
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    res = {"schema": "mp5-genie/1", "argv": sys.argv, "declaration_sha256": sha256(decl_p), "environment": gfr.environment(),
           "code": {}, "controls": {}}
    for m in [sys.modules[__name__], gfr, sup, s1, g5, g5.u3d, g5.u3d.u2d, g5.gew]:
        p = Path(m.__file__).resolve()
        res["code"][m.__name__] = {"file": str(p), "sha256": sha256(p)}
        print("module", m.__name__, p, flush=True)
    AX, E5 = g5.AXES, g5.EDGES
    shape = tuple(g5.SHAPE)
    dV5 = g5.widths(*AX)
    G = gfr.DEFAULTS["genie_dir"]
    main_p, full_p = os.path.join(sup.OUT, f"{GEN}_xsec5d.npz"), os.path.join(sup.OUT, f"{GEN}_xsec5d_full.npz")
    main_np, meta = sup.load5(main_p, shape)
    full_np, fmeta = sup.load5(full_p, shape)
    res["frozen_products"] = {"main": {"path": main_p, "sha256": sha256(main_p)}, "full": {"path": full_p, "sha256": sha256(full_p)}}
    nm = meta["normalisation"]
    A, B = nm["sigma_CC_t_lt50_per_nucleon_cm2"], nm["sum_r_normalising_population"]
    gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root")
    graphs, flux = os.path.join(G, "xsec_graphs.root"), os.path.join(G, "flux_mefhc_numu.root")
    res["gst"] = {"path": gst, "sha256": sha256(gst)}
    supp_file = sup.SUPP_FILES[GEN]
    res["supplement_file"] = {"path": supp_file, "sha256": sha256(supp_file),
                              "product_meta_sha256": fmeta["supplement"]["events"].get("sha256")}
    res["gst"]["product_meta_sha256"] = next((r.get("sha256") for r in meta.get("inputs", []) if "events" in r.get("role", "")), None)

    z, _, _ = gfr.load_phi_t(sup.OUT)
    phi_t, Phi_t = z["phi_t_density"], float(z["Phi_t"])
    e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
    lo, hi = gfr.GEN_RANGE[GEN]
    _, rbin, rng_e = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, lo, hi)
    sn = fmeta["supplement"]["normalisation"]
    S_50_100, N_pop, pe_s = sn["S_50_100_cm2"], sn["N_normalising_population"], sn["per_event_xsec_cm2"]

    def build(nmain, nsupp):
        ev, im = events(ROOT, g5, gst, nmain)
        r_all = gfr.r_of(im["Ev"], e_s, rbin, rng_e)
        x_m, v_m = gfr.build_genie(g5, GEN, ev, r_all[im["sel"]], A, B, dV5)
        ev_s, is_ = events(ROOT, g5, supp_file, nsupp)
        nevt = g5.hist([ev_s[a] for a in AX], None, [E5[a] for a in AX])
        x_s = S_50_100 * (nevt / N_pop) / dV5
        v_s = nevt * (pe_s ** 2) / dV5 ** 2
        # per-event J-cell contributions (U x sums vol * x): A r / B (main), S_50_100 / N_pop (supplement)
        c_main = np.zeros(im["n_entries"])
        c_main[im["sel"]] = A * r_all[im["sel"]] / B
        c_supp = np.zeros(is_["n_entries"])
        c_supp[is_["sel"]] = S_50_100 / N_pop
        return {"ev": ev, "im": im, "ev_s": ev_s, "is": is_, "x_m": x_m, "v_m": v_m, "x_s": x_s, "v_s": v_s,
                "c": np.concatenate([c_main, c_supp])}

    # ---- G1: the unrotated path (n = z) against extract_genie and the frozen products
    ref_ev, ref_norm, _ = g5.extract_genie(gst, False, graphs, flux, "flux_numu", 0)
    ref_s, _, _ = g5.extract_genie(supp_file, False, sup.GRAPHS_100, sup.FLUX_SUPP, "flux_numu", 0)
    U0 = build(None, None)
    g1 = {"events_main_bitwise": {k: bool(np.array_equal(U0["ev"][k], ref_ev[k])) for k in ref_ev},
          "events_supp_bitwise": {k: bool(np.array_equal(U0["ev_s"][k], ref_s[k])) for k in ref_s},
          "nu_along_z": [U0["im"]["nu_along_z"], U0["is"]["nu_along_z"]],
          "main_xsec_bitwise": bool(np.array_equal(U0["x_m"].reshape(-1), main_np["xsec_flat"])),
          "main_sumw2_bitwise": bool(np.array_equal(U0["v_m"].reshape(-1), main_np["sumw2_flat"])),
          "full_xsec_bitwise": bool(np.array_equal((U0["x_m"] + U0["x_s"]).reshape(-1), full_np["xsec_flat"])),
          "full_sumw2_bitwise": bool(np.array_equal((U0["v_m"] + U0["v_s"]).reshape(-1), full_np["sumw2_flat"])),
          "N_cc_vs_product": [U0["im"]["n_cc"], ref_norm["N_cc"]]}
    g1["pass"] = (all(g1["events_main_bitwise"].values()) and all(g1["events_supp_bitwise"].values())
                  and all(g1["nu_along_z"]) and g1["main_xsec_bitwise"] and g1["main_sumw2_bitwise"]
                  and g1["full_xsec_bitwise"] and g1["full_sumw2_bitwise"])
    res["controls"]["G1_unrotated_rebuild"] = g1
    print("G1", json.dumps(g1), flush=True)
    if not g1["pass"]:
        return finish(res, out, t0, 3)

    # ---- the rotated build (declared seed, bins, pool)
    bins = [float(x) for x in decl["enu_bins_GeV"]]
    pools = [np.load(pooldir / f"pool_b{b}.npy") for b in range(len(bins) - 1)]
    res["pool_sha256"] = {f"pool_b{b}.npy": sha256(pooldir / f"pool_b{b}.npy") for b in range(len(bins) - 1)}
    rng = np.random.default_rng(int(decl["rng"]["seed"]))
    u_main = rng.random(U0["im"]["n_entries"])
    u_supp = rng.random(U0["is"]["n_entries"])
    n_main = draw_directions(u_main, U0["im"]["Ev"], pools, bins)
    n_supp = draw_directions(u_supp, U0["is"]["Ev"], pools, bins)
    del pools
    R = build(n_main, n_supp)
    al = np.arctan2(np.hypot(n_main[:, 0], n_main[:, 1]), n_main[:, 2])
    eb = np.digitize(U0["im"]["Ev"], bins) - 1
    res["drawn_alpha_mrad_main"] = {f"bin{b}": {"n": int((eb == b).sum()),
                                                "median": float(np.median(1e3 * al[eb == b])) if (eb == b).any() else None}
                                    for b in range(len(bins) - 1)}

    # per-event J cells, unrotated vs rotated, for the migration MC error and census
    supported = json.loads(contract_p.read_text())["measurement"]["partition_J"]["supported_cells"]
    cmap, ncell = s1.coarse_map(s1.J_EDGES, supported)

    def jcells(B_):
        out_ = []
        for ev, inf in ((B_["ev"], B_["im"]), (B_["ev_s"], B_["is"])):
            j = np.full(inf["n_entries"], -1)
            fi = s1.fine_index(np.column_stack([ev[a] for a in AX]))
            j[inf["sel"]] = np.where(fi >= 0, cmap[np.maximum(fi, 0)], -1)
            out_.append(j)
        return np.concatenate(out_)
    j0, j1 = jcells(U0), jcells(R)
    c = U0["c"]
    mv = j0 != j1
    res["migration"] = {"n_events_change_J_cell": int(mv.sum()),
                        "n_ps_decision_changes_main": int(np.setxor1d(U0["im"]["sel"], R["im"]["sel"]).size),
                        "n_ps_decision_changes_supp": int(np.setxor1d(U0["is"]["sel"], R["is"]["sel"]).size),
                        "n_W_zero_unrot_rot": [int((U0["ev"]["W"] == 0).sum()), int((R["ev"]["W"] == 0).sum())]}
    c_rot = R["c"]
    np.savez_compressed(out / "mp5_genie.npz",
                        xsec_unrot_full=(U0["x_m"] + U0["x_s"]).reshape(-1), sumw2_unrot_full=(U0["v_m"] + U0["v_s"]).reshape(-1),
                        xsec_beam_full=(R["x_m"] + R["x_s"]).reshape(-1), sumw2_beam_full=(R["v_m"] + R["v_s"]).reshape(-1),
                        J_var_out=np.bincount(j0[mv & (j0 >= 0)], (c ** 2)[mv & (j0 >= 0)], ncell),
                        J_var_in=np.bincount(j1[mv & (j1 >= 0)], (c_rot ** 2)[mv & (j1 >= 0)], ncell),
                        J_n_out=np.bincount(j0[mv & (j0 >= 0)], None, ncell), J_n_in=np.bincount(j1[mv & (j1 >= 0)], None, ncell))
    return finish(res, out, t0, 0)


def finish(res, out, t0, rc):
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s"], res["maxrss_kb"], res["wall_s"], res["exit"] = ru.ru_utime + ru.ru_stime, ru.ru_maxrss, time.time() - t0, rc
    (out / "mp5_genie.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print("GENIE_CONTROLS", {k: v.get("pass") for k, v in res["controls"].items()}, "exit", rc, flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
