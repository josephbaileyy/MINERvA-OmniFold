#!/usr/bin/env python3
"""MP3-A step 1: GENIE CH fine-grid 5D predictions split by target code (frozen spec PLAN.md §4.2-4.3).

For G in {genie_cv, genie_mec} this rebuilds the frozen s5p GENIE prediction ``<G>_xsec5d_full.npz``
through the code path that built it (gen5d_flux_reweight.build_genie for the < 50 GeV sample, the
gen5d_flux_supplement formula for the 50-100 GeV supplement, then their sum), checks it against the
frozen product bit for bit (CONTROL), and builds the same sums restricted to the events of one target
code (gst ``tgt``): carbon 1000060120, hydrogen 2212, and any other code (reported, not merged).
The per-event weights and normalization constants are the frozen product's own, so the target parts add
up to the CH prediction (per CH nucleon). The carbon-only per-C12-nucleon prediction is
(13/12) x the carbon part, as r5_genie_events.py:140-141 normalizes it.

Runs in the root_6_28 env (ROOT RDataFrame, as the product build did). Reads only frozen inputs; writes
only to OUTDIR. Usage: python3 mp3a_build.py OUTDIR
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

C12, H1 = 1000060120, 2212
N_C_OVER_CH = 12.0 / 13.0


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def find_input(meta, role_substr, path_substr=None):
    for rec in meta.get("inputs", []):
        if role_substr in rec.get("role", "") and (path_substr is None or path_substr in rec["path"]):
            return rec
    return None


def sel_in_ps(g5, d):
    """The phase-space selection of gen_to_xsec5d.extract_genie / gen5d_flux_reweight.cmd_reweight."""
    cc = d["cc"].astype(bool)
    pt = np.hypot(d["pxl"], d["pyl"])
    pz = d["pzl"]
    in_ps = g5.u3d.u2d.in_truth_phase_space
    PT, PZ = g5.EDGES["pt"], g5.EDGES["pz"]
    inps = np.fromiter((c and in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                        for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())), dtype=bool, count=cc.size)
    return np.where(inps)[0], pt, pz


def subset(ev, m):
    return {k: v[m] for k, v in ev.items()}


def one(ROOT, g5, gen, out):
    AX, E5 = g5.AXES, g5.EDGES
    shape = tuple(g5.SHAPE)
    dV5 = g5.widths(*AX)
    G = gfr.DEFAULTS["genie_dir"]
    rec = {"generator": gen}
    main_p = os.path.join(sup.OUT, f"{gen}_xsec5d.npz")
    full_p = os.path.join(sup.OUT, f"{gen}_xsec5d_full.npz")
    main_np, meta = sup.load5(main_p, shape)
    full_np, fmeta = sup.load5(full_p, shape)
    rec["frozen_products"] = {"main": {"path": main_p, "sha256": sha256(main_p)},
                              "full": {"path": full_p, "sha256": sha256(full_p)}}
    nm = meta["normalisation"]
    A, B = nm["sigma_CC_t_lt50_per_nucleon_cm2"], nm["sum_r_normalising_population"]

    # ---- < 50 GeV sample, exactly as cmd_reweight
    gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv" else "genie_mefhc_mec_ALL.gst.root")
    graphs = os.path.join(G, "xsec_graphs.root")
    flux = os.path.join(G, "flux_mefhc_numu.root")
    t0 = time.time()
    gst_sha = sha256(gst)
    want = find_input(meta, "events")
    rec["gst"] = {"path": gst, "sha256": gst_sha, "product_meta_sha256": want and want.get("sha256"),
                  "matches_product_meta": bool(want and want.get("sha256") == gst_sha)}
    ev, norm, _ = g5.extract_genie(gst, gen == "genie_mec", graphs, flux, "flux_numu", 0)
    d = ROOT.RDataFrame("gst", gst).AsNumpy(["cc", "mec", "Ev", "pxl", "pyl", "pzl", "tgt", "hitnuc"])
    sel, pt, pz = sel_in_ps(g5, d)
    aligned = bool(np.array_equal(pt[sel], ev["pt"]) and np.array_equal(pz[sel], ev["pz"]))
    if not aligned:
        raise SystemExit(f"{gen}: event alignment with extract_genie failed")
    z, _, _ = gfr.load_phi_t(sup.OUT)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
    lo, hi = gfr.GEN_RANGE[gen]
    _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, lo, hi)
    cc = d["cc"].astype(bool)
    mec = d["mec"].astype(bool)
    r_all = gfr.r_of(d["Ev"], e_s, rbin, rng)
    r_ps = r_all[sel]
    # recompute the normalization constants (cmd_reweight's statements) and compare with the product's
    sig = gfr.SigmaCC(ROOT, graphs, "CH")
    I = sig.bin_integrals(e_s)
    sigma_t50 = float(np.sum(np.where(rng, phi_t / Phi_t, 0.0) * I))
    pop_B = cc if gen == "genie_cv" else (cc & ~mec)
    Bsum = float(np.sum(r_all[pop_B]))
    rec["normalisation_recomputed"] = {"A_product": A, "A_recomputed": sigma_t50, "A_bitwise": sigma_t50 == A,
                                       "B_product": B, "B_recomputed": Bsum, "B_bitwise": Bsum == B}
    tgt = d["tgt"].astype(np.int64)[sel]
    hitnuc = d["hitnuc"].astype(np.int64)[sel]
    x_m, v_m = gfr.build_genie(g5, gen, ev, r_ps, A, B, dV5)
    rec["control_main"] = gfr.compare_arrays(x_m.reshape(-1), main_np["xsec_flat"])
    rec["control_main"]["sumw2_bitwise"] = bool(np.array_equal(v_m.reshape(-1), main_np["sumw2_flat"]))

    # ---- 50-100 GeV supplement, exactly as cmd_supplement
    sn = fmeta["supplement"]["normalisation"]
    supp_file = sup.SUPP_FILES[gen]
    s_sha = sha256(supp_file)
    rec["supplement_file"] = {"path": supp_file, "sha256": s_sha,
                              "product_meta_sha256": fmeta["supplement"]["events"].get("sha256"),
                              "matches_product_meta": fmeta["supplement"]["events"].get("sha256") == s_sha}
    ev_s, _, _ = g5.extract_genie(supp_file, gen == "genie_mec", sup.GRAPHS_100, sup.FLUX_SUPP, "flux_numu", 0)
    ds = ROOT.RDataFrame("gst", supp_file).AsNumpy(["cc", "mec", "Ev", "pxl", "pyl", "pzl", "tgt", "hitnuc"])
    sel_s, pt_s, pz_s = sel_in_ps(g5, ds)
    if not (np.array_equal(pt_s[sel_s], ev_s["pt"]) and np.array_equal(pz_s[sel_s], ev_s["pz"])):
        raise SystemExit(f"{gen}: supplement alignment with extract_genie failed")
    tgt_s = ds["tgt"].astype(np.int64)[sel_s]
    hit_s = ds["hitnuc"].astype(np.int64)[sel_s]
    S_50_100, N_pop, pe = sn["S_50_100_cm2"], sn["N_normalising_population"], sn["per_event_xsec_cm2"]

    def supp_part(m):
        nevt = g5.hist([ev_s[a][m] for a in AX], None, [E5[a] for a in AX])
        x_s = S_50_100 * (nevt / N_pop) / dV5 if gen == "genie_cv" else nevt * pe / dV5
        v_s = nevt * (pe ** 2) / dV5 ** 2
        return x_s, v_s, nevt

    x_s, v_s, n_s = supp_part(np.ones(sel_s.size, bool))
    x_f = main_np["xsec_flat"].reshape(shape) + x_s
    v_f = main_np["sumw2_flat"].reshape(shape) + v_s
    rec["control_full"] = gfr.compare_arrays(x_f.reshape(-1), full_np["xsec_flat"])
    rec["control_full"]["sumw2_bitwise"] = bool(np.array_equal(v_f.reshape(-1), full_np["sumw2_flat"]))
    x_f2 = x_m + x_s
    rec["control_full_from_rebuilt_main"] = gfr.compare_arrays(x_f2.reshape(-1), full_np["xsec_flat"])

    # ---- the target split
    parts = {}
    codes = sorted(set(np.unique(tgt).tolist()) | set(np.unique(tgt_s).tolist()))
    groups = {"C12": (tgt == C12, tgt_s == C12), "H1": (tgt == H1, tgt_s == H1),
              "other": (~np.isin(tgt, [C12, H1]), ~np.isin(tgt_s, [C12, H1]))}
    for name, (mm, ms) in groups.items():
        xm, vm = gfr.build_genie(g5, gen, subset(ev, mm), r_ps[mm], A, B, dV5)
        xs_, vs_, ns_ = supp_part(ms)
        nm_ = g5.hist([ev[a][mm] for a in AX], None, [E5[a] for a in AX])
        parts[name] = {"x": (xm + xs_).reshape(-1), "v": (vm + vs_).reshape(-1), "n": (nm_ + ns_).reshape(-1),
                       "n_main": int(mm.sum()), "n_supp": int(ms.sum()),
                       "sigma_in_grid_cm2": float(((xm + xs_) * dV5).sum())}
    xsum = sum(parts[k]["x"] for k in parts)
    rec["split_closure_vs_full_product"] = gfr.compare_arrays(xsum, full_np["xsec_flat"])
    rec["tgt_codes"] = {"main_ps": {str(c): int((tgt == c).sum()) for c in codes},
                        "supp_ps": {str(c): int((tgt_s == c).sum()) for c in codes}}
    hh = np.concatenate([hitnuc[tgt == H1], hit_s[tgt_s == H1]])
    rec["hydrogen_hitnuc_values"] = {str(k): int(v) for k, v in zip(*np.unique(hh, return_counts=True))}
    oth = np.concatenate([tgt[~np.isin(tgt, [C12, H1])], tgt_s[~np.isin(tgt_s, [C12, H1])]])
    rec["other_code_events"] = {str(k): int(v) for k, v in zip(*np.unique(oth, return_counts=True))}
    mec_ps = np.asarray(ev["is_mec"], bool)
    rec["mec_events_by_target_main_ps"] = {str(c): int((mec_ps & (tgt == c)).sum()) for c in codes}
    for k in parts:
        rec.setdefault("parts", {})[k] = {kk: parts[k][kk] for kk in ("n_main", "n_supp", "sigma_in_grid_cm2")}
    rec["sigma_in_grid_full_product_cm2"] = float((full_np["xsec_flat"].reshape(shape) * dV5).sum())

    # ---- cross-check against r5 (per fine W bin, all fine cells): C-only/CH per nucleon and H share
    iW = np.arange(int(np.prod(shape))) % shape[4]
    vol = dV5.reshape(-1)
    r5x = {}
    for j in range(shape[4]):
        m = iW == j
        tot = float((full_np["xsec_flat"][m] * vol[m]).sum())
        c = float((parts["C12"]["x"][m] * vol[m]).sum())
        h = float((parts["H1"]["x"][m] * vol[m]).sum())
        o = float((parts["other"]["x"][m] * vol[m]).sum())
        r5x[f"W{j}"] = {"Conly_over_CH_per_nucleon": c / N_C_OVER_CH / tot, "H_frac": h / tot,
                        "H_plus_other_frac": (h + o) / tot}
    rec["r5_crosscheck_fine_W"] = r5x

    np.savez_compressed(os.path.join(out, f"mp3a_fine_{gen}.npz"),
                        xsec_CH_frozen=full_np["xsec_flat"], sumw2_CH_frozen=full_np["sumw2_flat"],
                        xsec_CH_rebuilt=x_f2.reshape(-1), sumw2_CH_rebuilt=(v_m + v_s).reshape(-1),
                        **{f"xsec_{k}": parts[k]["x"] for k in parts}, **{f"sumw2_{k}": parts[k]["v"] for k in parts},
                        **{f"nevt_{k}": parts[k]["n"] for k in parts})
    rec["wall_s"] = time.time() - t0
    return rec


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    res = {"schema": "mp3a-build/1", "argv": sys.argv, "code": {}, "environment": gfr.environment(), "generators": {}}
    for m in [sys.modules[__name__], gfr, sup] + [g5, g5.u3d, g5.u3d.u2d, g5.g3d, g5.gew, g5.gibew, g5.gib3d,
                                                   sys.modules["gst_reader"], sys.modules["xsec_3d"]]:
        p = Path(m.__file__).resolve()
        res["code"][m.__name__] = {"file": str(p), "sha256": sha256(p)}
    for gen in ("genie_cv", "genie_mec"):
        res["generators"][gen] = one(ROOT, g5, gen, out)
        r = res["generators"][gen]
        print(gen, json.dumps({k: r[k] for k in ("control_main", "control_full", "control_full_from_rebuilt_main",
                                                 "split_closure_vs_full_product", "normalisation_recomputed",
                                                 "tgt_codes", "other_code_events")}), flush=True)
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["cpu_s"] = ru.ru_utime + ru.ru_stime
    res["maxrss_kb"] = ru.ru_maxrss
    with open(os.path.join(out, "mp3a_build.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    ok = all(r["control_full"]["bitwise_equal"] and r["control_main"]["bitwise_equal"]
             for r in res["generators"].values())
    print("CONTROL_BITWISE", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
