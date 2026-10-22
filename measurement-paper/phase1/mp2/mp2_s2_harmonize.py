#!/usr/bin/env python3
"""MP-2 S2 step 2 (root_6_28): controls, then the harmonized generator events, features and CH products, the Tune
v1 C+H feature table, and the reference hybrid H_CH,an, under the frozen feature contract
(feature_contract_draft.json sha256 98141c2f..., binding addenda 8 and 9; IMPLEMENTATION.md for the readings).

Order. Each control runs before anything harmonized is formed; a failed control stops the job (exit 3).
  H0  A7's fine-null construction: s5p_truths.fine_ratio on each generator's frozen product and the frozen MnvTune
      truth reproduces A7's rho-<G>-F.npz bitwise (so H_CH,an below is A7's construction on another numerator).
  N   weight chain and normalization, per generator: per-event weights c_e from the frozen chain (GENIE r A / B and
      the supplement's S/N_pop; NuWro w r / N_total x 12/13 or 1/13; GiBUU perweight r / M x 1e-38 x 12/13 or
      1/13), histogrammed with the frozen readers' own native-convention scalars, reproduce the frozen CH product:
      nevt exactly, xsec_flat and sumw2_flat to <= 1e-10 relative (bitwise is not available: the frozen builds
      multiply after summing).
  A   alignment of this study's particle readers with the frozen readers, bitwise where both read one stored value:
      GENIE dump vs RDataFrame (Ev, El, pxl, pyl, pzl, pxv, pyv, cc); NuWro treeout vs the flat trees (weight, the
      muon pz / 1000, cc; E_nu = in[0].t / 1000 to 1e-12 rel); GiBUU parser vs extract_gibuu (pt, pz, perweight,
      E_nu of every native in-PS event).
  Z   nu along +z: GENIE pxv = pyv = 0 and NuWro in[0].x = in[0].y = 0 for every entry; GiBUU non-DIS H events whose energy
      balances (|sum E_final - E_struck - E_nu| <= 1 MeV) balance pT to <= 1 MeV (C12 cannot be checked, the remnant
      is not written). H events missing energy (DIS; a final nucleon not written) are counted, not tested: a missing
      particle unbalances pT without any tilt of the nu (S2-IMPLEMENTATION.md, Z).
Then, per generator: the nu direction draw (default_rng(seed_G), one uniform per entry in the declared order), the
whole-event rotation R(n), the analysis-convention scalars, the features, the harmonized CH product, and the
events inside the phase space and the fine grid; and H_CH,an = fine_ratio(harmonized CH product, MnvTune truth)
with A7's coarse edges and only-cells. Tune v1: the C+H rows inside the fine grid (all supports), MCgen scalars,
w_truth, E_nu, the features from the rotated S1 particle lists.

Usage: python3 mp2_s2_harmonize.py --dump DUMPDIR --s1 S1DIR --pool POOLDIR --out OUT --nproc N
Exit 0 done; 3 a control failed.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import multiprocessing as mp
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
import mp2_s1_dump as s1d  # noqa: E402
import mp2_s2_charm as chm  # noqa: E402
import mp3c_build as b3c  # noqa: E402
import mp5_genie as m5  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402
import s5p_truths as st  # noqa: E402

CONTRACT_SHA = "98141c2f22f4fc3f2a7f5b30a0c509d6a29a37d145a72ea802623a2a2d6630cd"
S5P = gfr.S5P
G = gfr.DEFAULTS["genie_dir"]
P1 = "/pscratch/sd/j/josephrb/measurement-paper/phase1"
OFIN = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
OFIN_SHA = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
MNVTUNE = f"{S5P}/gen5d/mnvtune_v1_xsec5d.npz"
A7_NULLS = {"genie_cv": "genie_cv", "genie_mec": "genie_mec", "nuwro_ch": "nuwro_cv", "gibuu_ch": "gibuu_cv"}
A7_NULL_DIR = f"{S5P}/ratios/nullsF"
FROZEN_CH = {"genie_cv": f"{sup.OUT}/genie_cv_xsec5d_full.npz", "genie_mec": f"{sup.OUT}/genie_mec_xsec5d_full.npz",
             "nuwro_ch": f"{P1}/mp3b/runA/out_r2/build_k1/nuwro_CH_xsec5d_full.npz",
             "gibuu_ch": f"{P1}/mp3c/out_b/bcheck/mp3c_fine_gibuu_frozen.npz"}
SEED_G = {"genie_cv": 2026102131, "genie_mec": 2026102132, "nuwro_ch": 2026102133, "gibuu_ch": 2026102134}
SUPPORT = {"genie_cv": (0.0, 100.0), "genie_mec": (0.0, 100.0), "nuwro_ch": (0.5, 100.0), "gibuu_ch": (0.0, 20.0)}
ENU_BINS = [0.0, 3.0, 5.0, 8.0, 15.0, 30.0, math.inf]
F_C, F_H = 12.0 / 13.0, 1.0 / 13.0
A_BEAM = s1d.A_BEAM
AX = ("pt", "pz", "eavail", "q3", "W")
REL_TOL = 1e-10
PT_BALANCE_MAX_GEV = 1e-3
# GiBUU (ID, charge) -> PDG: the contract's map with addendum 9's amendments (902 -> 13; (1, -1) -> -2212)
GIBUU_MAP = {(1, 1): 2212, (1, 0): 2112, (1, -1): -2212, (101, 1): 211, (101, 0): 111, (101, -1): -211,
             (102, 0): 221, (110, 1): 321, (110, 0): 311, (111, 0): -311, (111, -1): -321, (32, 0): 3122,
             (33, 1): 3222, (33, 0): 3212, (33, -1): 3112, (902, -1): 13}
OTHER_BASE = 900_000_000          # an unmapped GiBUU (ID, charge): code < 1e9, so 'other' (not excluded)
F_PRIMARY = ["pt", "pz", "eavail", "q3", "W", "enu", "sum_p_KE", "sum_pipm_KE", "sum_em_E", "sum_n_KE", "E_other",
             "n_p", "n_pipm", "p1_KE", "p1_cos", "pipm1_KE", "pipm1_cos", "n1_KE"]
V3_KEYS = ["v3_n_mult_KE10", "v3_p_mult_KE20", "v3_pi0_count"]


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def rel_close(a, b):
    a, b = np.asarray(a, float).ravel(), np.asarray(b, float).ravel()
    nz = b != 0
    zero_ok = bool(np.all(a[~nz] == 0))
    mx = float(np.max(np.abs(a[nz] - b[nz]) / np.abs(b[nz]))) if nz.any() else 0.0
    return {"max_rel": mx, "zero_cells_equal": zero_ok, "bitwise": bool(np.array_equal(a, b)),
            "pass": bool(zero_ok and mx <= REL_TOL)}


def product(cols, c, dV5):
    """x = sum c / dV, sumw2 = sum c^2 / dV^2, nevt = count, on the frozen grid (g5.hist semantics)."""
    e5 = [G5.EDGES[a] for a in AX]
    x = G5.hist(cols, c, e5) / dV5
    v = G5.hist(cols, c * c, e5) / dV5 ** 2
    n = G5.hist(cols, None, e5)
    return x.reshape(-1), v.reshape(-1), n.reshape(-1)


# ---------------------------------------------------------------- particles and features
def features(pdg, E, px, py, pz, off):
    """Per-event features from ragged, already beam-frame particles (MeV); the contract's species, thresholds and
    leading-particle rules. pdg >= 1e9, |pdg| in {11..14, 16} are excluded; 'other' is anything else that is
    not p, n, pi+-, pi0, gamma."""
    n_ev = off.size - 1
    row = np.repeat(np.arange(n_ev), np.diff(off))
    p2 = px * px + py * py + pz * pz
    KE = E - np.sqrt(np.maximum(E * E - p2, 0.0))
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = pz / np.sqrt(p2)
    a = np.abs(pdg)
    excl = np.isin(a, [11, 12, 13, 14, 16]) | (a >= 1_000_000_000)
    is_p, is_n, is_pi, is_pi0, is_g = pdg == 2212, pdg == 2112, a == 211, pdg == 111, pdg == 22
    other = ~excl & ~(is_p | is_n | is_pi | is_pi0 | is_g)
    sp_p, sp_n, sp_pi = is_p & (KE > 100.0), is_n & (KE > 50.0), is_pi & (KE > 50.0)
    em = is_pi0 | (is_g & (E > 10.0))
    bc = lambda m, w=None: np.bincount(row[m], None if w is None else w[m], minlength=n_ev)  # noqa: E731

    def leading(m, extra=None):
        out, out_x = np.full(n_ev, np.nan), np.full(n_ev, np.nan)
        idx = np.nonzero(m)[0]
        if idx.size:
            o = np.lexsort((KE[idx], row[idx]))
            idx = idx[o]
            last = np.ones(idx.size, bool)
            last[:-1] = row[idx][1:] != row[idx][:-1]
            sel = idx[last]
            out[row[sel]] = KE[sel]
            if extra is not None:
                out_x[row[sel]] = extra[sel]
        return out, out_x
    f = {"sum_p_KE": bc(sp_p, KE), "sum_pipm_KE": bc(sp_pi, KE), "sum_em_E": bc(em, E), "sum_n_KE": bc(sp_n, KE),
         "E_other": bc(other, E), "n_p": bc(sp_p).astype(float), "n_pipm": bc(sp_pi).astype(float)}
    f["p1_KE"], f["p1_cos"] = leading(sp_p, cos)
    f["pipm1_KE"], f["pipm1_cos"] = leading(sp_pi, cos)
    f["n1_KE"], _ = leading(sp_n)
    f["v3_n_mult_KE10"] = bc(is_n & (KE > 10.0)).astype(float)
    f["v3_p_mult_KE20"] = bc(is_p & (KE > 20.0)).astype(float)
    f["v3_pi0_count"] = bc(is_pi0).astype(float)
    # the per-neutron KE spectrum (all neutrons), kept ragged: KE and the event row
    f["_neutron_KE"], f["_neutron_row"] = KE[is_n], row[is_n]
    return f


def rotate_particles(px, py, pz, off, n_ev_dir):
    """R(n_e) applied to every particle of event e (the contract's whole-event rotation)."""
    rep = np.repeat(n_ev_dir, np.diff(off), axis=0)
    return m5.rotate(px, py, pz, rep)


def harmonize(name, ent, rng_seed, pools, dV5, res):
    """ent: per-entry dict (enu GeV, lepton E/px/py/pz GeV in the generator frame with nu along +z, cc, hit code,
    target 'C'/'H' as 6/1, weight c, sample index) and ragged FS (pdg, E, px, py, pz MeV, offsets)."""
    n = ent["enu"].size
    u = np.random.default_rng(rng_seed).random(n)
    ndir = m5.draw_directions(u, ent["enu"], pools, ENU_BINS)
    qx, qy, qz = m5.rotate(ent["lpx"], ent["lpy"], ent["lpz"], ndir)
    pt, pzl = np.hypot(qx, qy), qz
    in_ps_f = G5.u3d.u2d.in_truth_phase_space
    PT, PZ = G5.EDGES["pt"], G5.EDGES["pz"]
    ps = np.fromiter((c and in_ps_f(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                      for c, a, b in zip(ent["cc"].tolist(), pt.tolist(), pzl.tolist())), dtype=bool, count=n)
    pmu = np.sqrt(ent["lpx"] ** 2 + ent["lpy"] ** 2 + ent["lpz"] ** 2)
    W = G5.w_struck(ent["enu"], ent["lE"], pzl, pmu, ent["hit"])
    _, q3 = G5.q3_true(ent["enu"], 0.0, 0.0, ent["enu"], ent["lE"], ent["lpx"], ent["lpy"], ent["lpz"])
    ea = s1d.eavail_mat(ent["fs_pdg"], ent["fs_E"], ent["fs_offsets"]) / 1000.0
    rx, ry, rz = rotate_particles(ent["fs_px"], ent["fs_py"], ent["fs_pz"], ent["fs_offsets"], ndir)
    fe = features(ent["fs_pdg"], ent["fs_E"], rx, ry, rz, ent["fs_offsets"])
    X = {"pt": pt, "pz": pzl, "eavail": ea, "q3": q3, "W": W, "enu": ent["enu"]}
    fi = s1.fine_index(np.column_stack([X[a] for a in AX]))
    grid = ps & (fi >= 0) & (ent["c"] > 0)
    lo, hi = SUPPORT[name]
    supp_ok = (ent["enu"] >= lo) & (ent["enu"] <= hi)
    xh, vh, nh = product([X[a][ps] for a in AX], ent["c"][ps], dV5)
    r12 = None
    if "fs0_pdg" in ent:                      # R12 decayed: the same events with the lists as GiBUU wrote them
        ea0 = s1d.eavail_mat(ent["fs0_pdg"], ent["fs0_E"], ent["fs0_offsets"]) / 1000.0
        X0 = dict(X, eavail=ea0)
        fi0 = s1.fine_index(np.column_stack([X0[a] for a in AX]))
        x0, v0, n0 = product([X0[a][ps] for a in AX], ent["c"][ps], dV5)
        r0x, r0y, r0z = rotate_particles(ent["fs0_px"], ent["fs0_py"], ent["fs0_pz"], ent["fs0_offsets"], ndir)
        fe0 = features(ent["fs0_pdg"], ent["fs0_E"], r0x, r0y, r0z, ent["fs0_offsets"])
        gid0, _ = gibuu_codes(ent["fs0_pdg"])
        changed = np.bincount(np.repeat(np.arange(n), np.diff(ent["fs0_offsets"])),
                              np.isin(gid0, list(chm.GIBUU_CHARM_IDS)), n) > 0          # the events that carried charm
        g0 = ps & (fi0 >= 0) & (ent["c"] > 0)
        cg = changed & (grid | g0)
        w_ = ent["c"]
        r12 = {"product_undecayed": (x0, v0, n0),
               "report": {"n_events_changed": int(changed.sum()), "n_changed_in_grid_either": int(cg.sum()),
                          "n_in_grid_decayed_not_undecayed": int(np.sum(changed & grid & ~g0)),
                          "n_in_grid_undecayed_not_decayed": int(np.sum(changed & g0 & ~grid)),
                          "in_grid_rate_share_changed_decayed": float(w_[changed & grid].sum() / w_[grid].sum()),
                          "eavail_shift_GeV_changed_in_grid_either": {
                              "mean_c_weighted": float(np.sum(w_[cg] * (ea - ea0)[cg]) / w_[cg].sum()) if cg.any() else None,
                              "quantiles_0.1_0.5_0.9": [float(q) for q in np.quantile((ea - ea0)[cg], [0.1, 0.5, 0.9])] if cg.any() else []},
                          "species_sum_shift_MeV_mean_c_weighted": {
                              k: float(np.sum(w_[cg] * (fe[k] - fe0[k])[cg]) / w_[cg].sum()) if cg.any() else None
                              for k in ("sum_p_KE", "sum_pipm_KE", "sum_em_E", "sum_n_KE", "E_other")},
                          "in_grid_rate_decayed_over_undecayed": float((xh @ dV5.reshape(-1)) / (x0 @ dV5.reshape(-1)))}}
    excl = ent.get("charm_excl")
    al = np.arctan2(np.hypot(ndir[:, 0], ndir[:, 1]), ndir[:, 2])
    res["harmonized"][name] = {
        "n_entries": int(n), "n_cc": int(ent["cc"].sum()), "n_in_ps": int(ps.sum()), "n_in_grid": int(grid.sum()),
        "n_in_grid_outside_support": int((grid & ~supp_ok).sum()),
        "n_W_nan_in_ps": int(np.sum(ps & np.isnan(W))), "n_default_mass_cc": int(np.sum(ent["cc"] & ~np.isin(ent["hit"], [2112, 2212]))),
        "drawn_alpha_mrad_median": float(np.median(1e3 * al)),
        "in_grid_rate_per_nucleon_cm2": float(xh @ dV5.reshape(-1)),
        "in_grid_rate_H_share": float((xh_h := product([X[a][ps & (ent["tgt"] == 1)] for a in AX],
                                                        ent["c"][ps & (ent["tgt"] == 1)], dV5)[0]) @ dV5.reshape(-1)
                                      / (xh @ dV5.reshape(-1))),
    }
    keep = grid & supp_ok
    if excl is not None:                      # R12 fallback: out of the training, V1 and V3 samples (as R13)
        res["harmonized"][name]["R12_excluded"] = {"n_events": int(np.sum(keep & excl)),
                                                   "in_grid_rate_share": float(ent["c"][keep & excl].sum() / ent["c"][keep].sum())}
        keep = keep & ~excl
    if r12 is not None:
        res["harmonized"][name]["R12"] = r12["report"]
    ev = {k: np.asarray(X[k], float)[keep] for k in X}
    for k in F_PRIMARY[6:] + V3_KEYS:
        ev[k] = np.asarray(fe[k], float)[keep]
    ev["c"], ev["tgt"], ev["j"] = ent["c"][keep], ent["tgt"][keep], np.nonzero(keep)[0]
    ev["fine"] = fi[keep]
    nk = np.isin(fe["_neutron_row"], np.nonzero(keep)[0])
    ev["nKE_val"], ev["nKE_ev"] = fe["_neutron_KE"][nk], np.searchsorted(np.nonzero(keep)[0], fe["_neutron_row"][nk])
    return ev, (xh, vh, nh), xh_h, (r12["product_undecayed"] if r12 is not None else None)


# ---------------------------------------------------------------- GENIE
def genie(ROOT, gen, dump, pools, dV5, res):
    """Native chain (cmd_reweight / cmd_supplement statements) for weights; harmonization from the dump."""
    main_p, full_p = os.path.join(sup.OUT, f"{gen}_xsec5d.npz"), os.path.join(sup.OUT, f"{gen}_xsec5d_full.npz")
    shape = tuple(G5.SHAPE)
    _, meta = sup.load5(main_p, shape)
    full_np, fmeta = sup.load5(full_p, shape)
    nm = meta["normalisation"]
    A, B = nm["sigma_CC_t_lt50_per_nucleon_cm2"], nm["sum_r_normalising_population"]
    sn = fmeta["supplement"]["normalisation"]
    S_50_100, N_pop = sn["S_50_100_cm2"], sn["N_normalising_population"]
    gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv" else "genie_mefhc_mec_ALL.gst.root")
    supp_file = sup.SUPP_FILES[gen]
    graphs, flux = os.path.join(G, "xsec_graphs.root"), os.path.join(G, "flux_mefhc_numu.root")
    z, _, _ = gfr.load_phi_t(sup.OUT)
    e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
    lo, hi = gfr.GEN_RANGE[gen]
    _, rbin, rng_e = gfr.flux_weights(e_s, c_s, z["phi_t_density"], float(z["Phi_t"]), lo, hi)
    cols = ["cc", "mec", "Ev", "El", "pxl", "pyl", "pzl", "pxv", "pyv", "tgt", "hitnuc"]
    parts, ctrl = [], {"inputs": {gst: sha256(gst), supp_file: sha256(supp_file), main_p: sha256(main_p),
                                  full_p: sha256(full_p)}}
    nat_cols, nat_c = [], []
    for which, path, gfile in (("main", gst, graphs), ("supp", supp_file, sup.GRAPHS_100)):
        d = ROOT.RDataFrame("gst", path).AsNumpy(cols)
        dd = np.load(dump / f"{gen}_{which}.npz")
        a_ok = {k: bool(np.array_equal(np.asarray(d[k]), dd[k])) for k in ("cc", "Ev", "El", "pxl", "pyl", "pzl", "pxv", "pyv", "tgt", "hitnuc")}
        cc = np.asarray(d["cc"]).astype(bool)
        ctrl[f"A_{which}"] = a_ok
        ctrl[f"Z_{which}"] = {"n_pxv_or_pyv_nonzero": int(np.sum((d["pxv"] != 0) | (d["pyv"] != 0)))}
        if which == "main":
            r_all = gfr.r_of(np.asarray(d["Ev"]), e_s, rbin, rng_e)
            c = np.where(cc, A * r_all / B, 0.0)
        else:
            c = np.where(cc, S_50_100 / N_pop, 0.0)
        # native in-PS events, as cmd_reweight / cmd_supplement select them, aligned with extract_genie
        ev, _, _ = G5.extract_genie(path, gen == "genie_mec", gfile, flux if which == "main" else sup.FLUX_SUPP,
                                    "flux_numu", 0)
        pt0, pz0 = np.hypot(d["pxl"], d["pyl"]), np.asarray(d["pzl"])
        in_ps = G5.u3d.u2d.in_truth_phase_space
        PT, PZ = G5.EDGES["pt"], G5.EDGES["pz"]
        sel = np.where(np.fromiter((c_ and in_ps(float(x), float(y), PT[0], PT[-1], PZ[0], PZ[-1])
                                    for c_, x, y in zip(cc.tolist(), pt0.tolist(), pz0.tolist())), dtype=bool, count=cc.size))[0]
        ctrl[f"A_{which}"]["native_sel_aligned_with_extract_genie"] = bool(
            np.array_equal(pt0[sel], ev["pt"]) and np.array_equal(pz0[sel], ev["pz"]))
        nat_cols.append([ev[k] for k in AX])
        nat_c.append(c[sel])
        tg = np.asarray(d["tgt"])
        if not np.all(np.isin(tg, [1000060120, 2212, 11])):
            raise SystemExit(f"{path}: a target other than C12, H and the atomic electron")
        ctrl[f"targets_{which}"] = {str(k): int(v) for k, v in zip(*np.unique(tg[cc], return_counts=True))}
        parts.append({"enu": np.asarray(d["Ev"], float), "lE": np.asarray(d["El"], float),
                      "lpx": np.asarray(d["pxl"], float), "lpy": np.asarray(d["pyl"], float), "lpz": np.asarray(d["pzl"], float),
                      "cc": cc, "hit": np.asarray(d["hitnuc"]), "tgt": np.where(tg == 2212, 1, np.where(tg == 11, 0, 6)), "c": c,
                      "fs_pdg": dd["fs_pdgf"], "fs_E": 1000.0 * dd["fs_Ef"], "fs_px": 1000.0 * dd["fs_pxf"],
                      "fs_py": 1000.0 * dd["fs_pyf"], "fs_pz": 1000.0 * dd["fs_pzf"], "fs_offsets": dd["fs_offsets"]})
    x, v, nn = product([np.concatenate([p[i] for p in nat_cols]) for i in range(5)], np.concatenate(nat_c), dV5)
    ctrl["N"] = {"xsec": rel_close(x, full_np["xsec_flat"]), "sumw2": rel_close(v, full_np["sumw2_flat"]),
                 "nevt_equal": bool(np.array_equal(nn, full_np["nevt_flat"])), "frozen": full_p}
    ctrl["N"]["pass"] = ctrl["N"]["xsec"]["pass"] and ctrl["N"]["sumw2"]["pass"] and ctrl["N"]["nevt_equal"]
    ctrl["pass"] = bool(ctrl["N"]["pass"] and all(all(ctrl[f"A_{w}"].values()) for w in ("main", "supp"))
                        and all(ctrl[f"Z_{w}"]["n_pxv_or_pyv_nonzero"] == 0 for w in ("main", "supp")))
    return ctrl, concat_entries(parts)


def concat_entries(parts):
    out = {}
    for k in ("enu", "lE", "lpx", "lpy", "lpz", "cc", "hit", "tgt", "c"):
        out[k] = np.concatenate([p[k] for p in parts])
    offs, base = [], 0
    for p in parts:
        offs.append(p["fs_offsets"][:-1] + base)
        base += int(p["fs_offsets"][-1])
    out["fs_offsets"] = np.concatenate(offs + [np.array([base], np.int64)])
    for k in ("fs_pdg", "fs_E", "fs_px", "fs_py", "fs_pz"):
        out[k] = np.concatenate([np.asarray(p[k], np.int64 if k == "fs_pdg" else float) for p in parts])
    out["sample"] = np.concatenate([np.full(p["enu"].size, i, np.int8) for i, p in enumerate(parts)])
    return out


# ---------------------------------------------------------------- NuWro
def nuwro(ROOT, dump, pools, dV5, res):
    import mp3b_build as b3
    z, _, _ = gfr.load_phi_t(sup.OUT)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    flux = os.path.join(G, "flux_mefhc_numu_nuwro.root")
    e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
    _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, b3.LO_MAIN, b3.HI_MAIN)
    e2, c2 = gfr.read_th1(ROOT, sup.FLUX_SUPP, "flux_numu")
    _, rbin2, rng2 = gfr.flux_weights(e2, c2, phi_t, Phi_t, sup.LO, sup.HI)
    r_const = float(np.sum((phi_t * np.diff(edges))[rng2]) / Phi_t)
    rec = json.loads((dump / "s2_dump.json").read_text())["samples"]
    ctrl, parts, nat_cols, nat_c = {}, [], [], []
    for which, frac, target in (("c12_main", F_C, 6), ("c12_supp", F_C, 6), ("h_main", F_H, 1), ("h_supp", F_H, 1)):
        flats = [f["path"] for f in rec[f"nuwro_{which}"]["flats"]]
        old = sorted(glob.glob(os.path.join(G, "work_nuwro_p*/nuwro_flat.root"))) if which == "c12_main" else flats
        ev, _, _ = G5.extract_nuwro(flats, old)
        d = b3.nuwro_events(ROOT, flats)
        ccm, m = b3.ps_mask(G5, d)
        dd = np.load(dump / f"nuwro_{which}.npz")
        N_total = float(ev["divisor"])
        if which.endswith("main"):
            r_all = gfr.r_of(d["Enu"], e_s, rbin, rng)
        else:
            r_all = np.full(d["Enu"].size, r_const)
        c = np.where(d["cc"].astype(bool), d["weight"] * r_all / N_total * frac, 0.0)
        idx_ps = np.nonzero(ccm)[0][m]
        nat_cols.append([ev[k] for k in AX])
        nat_c.append(c[idx_ps])
        # alignment: treeout (dump) vs flat rows
        cc = dd["cc"].astype(bool)
        fo = dd["fs_offsets"]
        row = np.repeat(np.arange(cc.size), np.diff(fo))
        mu = np.abs(dd["fs_pdg"]) == 13
        nmu = np.bincount(row[mu], minlength=cc.size)
        lastmu = np.full(cc.size, -1)
        lastmu[row[mu]] = np.nonzero(mu)[0]                      # the last muon of each event (ascending order)
        io = dd["in_offsets"]
        nin = np.diff(io)
        enu = dd["in_t"][io[:-1]] / 1000.0
        a_ok = {"n_rows_equal": int(cc.size) == int(d["cc"].size),
                "cc_bitwise": bool(np.array_equal(cc, d["cc"].astype(bool))),
                "weight_bitwise": bool(np.array_equal(dd["weight"], d["weight"])),
                "at_least_one_muon_per_cc_event": bool(np.all(nmu[cc] >= 1)),
                "n_cc_events_by_muon_count": {str(k_): int(v_) for k_, v_ in zip(*np.unique(nmu[cc], return_counts=True))},
                "muon_pz_over_1000_bitwise_cc": bool(np.array_equal(dd["fs_z"][lastmu[cc]] / 1000.0, d["pz"][cc])),
                "enu_max_rel": float(np.max(np.abs(enu - d["Enu"]) / np.abs(d["Enu"])))}
        a_ok["enu_ok"] = a_ok["enu_max_rel"] <= 1e-12
        ctrl[f"A_{which}"] = a_ok
        ctrl[f"Z_{which}"] = {"n_in0_x_or_y_nonzero": int(np.sum((dd["in_x"][io[:-1]] != 0) | (dd["in_y"][io[:-1]] != 0)))}
        l = np.where(cc, lastmu, 0)
        in1 = np.where(nin >= 2, dd["in_pdg"][np.minimum(io[:-1] + 1, io[-1] - 1)], 0)
        hit = np.where(nin == 2, in1, 0)                     # n_in = 3 (two struck nucleons) and n_in = 1: default
        keep = np.ones(dd["fs_pdg"].size, bool)
        parts.append({"enu": enu, "lE": dd["fs_t"][l] / 1000.0, "lpx": dd["fs_x"][l] / 1000.0,
                      "lpy": dd["fs_y"][l] / 1000.0, "lpz": dd["fs_z"][l] / 1000.0, "cc": cc, "hit": hit,
                      "tgt": np.full(cc.size, target), "c": c, "fs_pdg": dd["fs_pdg"][keep], "fs_E": dd["fs_t"],
                      "fs_px": dd["fs_x"], "fs_py": dd["fs_y"], "fs_pz": dd["fs_z"], "fs_offsets": fo})
        ctrl[f"struck_{which}"] = {str(k): int(v) for k, v in zip(*np.unique(nin[cc], return_counts=True))}
    fz = np.load(FROZEN_CH["nuwro_ch"], allow_pickle=True)
    x, v, nn = product([np.concatenate([p[i] for p in nat_cols]) for i in range(5)], np.concatenate(nat_c), dV5)
    ctrl["N"] = {"xsec": rel_close(x, fz["xsec_flat"]), "sumw2": rel_close(v, fz["sumw2_flat"]),
                 "nevt_equal": bool(np.array_equal(nn, fz["nevt_flat"])), "frozen": FROZEN_CH["nuwro_ch"]}
    ctrl["N"]["pass"] = ctrl["N"]["xsec"]["pass"] and ctrl["N"]["sumw2"]["pass"] and ctrl["N"]["nevt_equal"]
    ctrl["pass"] = bool(ctrl["N"]["pass"] and all(
        all(vv for kk, vv in ctrl[f"A_{w}"].items() if kk not in ("enu_max_rel", "n_cc_events_by_muon_count")) and ctrl[f"Z_{w}"]["n_in0_x_or_y_nonzero"] == 0
        for w in ("c12_main", "c12_supp", "h_main", "h_supp")))
    return ctrl, concat_entries(parts)


# ---------------------------------------------------------------- GiBUU
def gibuu_file(fn):
    """One FinalEvents.dat: events in extract_gibuu's order (np.unique of run x 1e7 + event), the muon, the
    final-state list mapped to PDG, the struck nucleon, production_ID, E_nu, the H pT balance."""
    d = np.loadtxt(fn, comments="#")
    if d.ndim == 1:
        d = d[None, :]
    run, evn = d[:, 0].astype(np.int64), d[:, 1].astype(np.int64)
    pid, ch, pw = d[:, 2].astype(int), d[:, 3].astype(int), d[:, 4]
    E, px, py, pz, prod, enu_r = d[:, 8], d[:, 9], d[:, 10], d[:, 11], d[:, 13].astype(int), d[:, 14]
    key = run * 10_000_000 + evn
    ukey, inv = np.unique(key, return_inverse=True)
    nev = ukey.size
    order = np.argsort(inv, kind="stable")
    inv_o = inv[order]
    lep = (pid == 902) & (pw != 0)
    fin = pw != 0
    init = (pw == 0) & (pid == 1)
    out = {"n_events": nev}
    li = inv[lep]
    if np.unique(li).size != li.size:
        raise SystemExit(f"{fn}: an event with two muons")
    for k, arr in (("lE", E), ("lpx", px), ("lpy", py), ("lpz", pz), ("w", pw), ("enu", enu_r)):
        v = np.full(nev, np.nan)
        v[li] = arr[lep]
        out[k] = v
    out["prod"] = np.full(nev, -1)
    out["prod"][inv] = prod
    n_init = np.bincount(inv[init], minlength=nev)
    q_init = np.full(nev, -9)
    q_init[inv[init]] = ch[init]
    out["hit"] = np.where((n_init == 1) & ~np.isin(out["prod"], [35, 36]),
                          np.where(q_init == 1, 2212, np.where(q_init == 0, 2112, 0)), 0)
    # final-state list (pw != 0), event order, mapped
    fo = order[fin[order]]
    codes = np.array([GIBUU_MAP.get((i, q), OTHER_BASE + 10 * i + (q + 2)) for i, q in zip(pid[fo].tolist(), ch[fo].tolist())],
                     np.int64)
    if np.any(pid[fo] < 0) or np.any(np.isin(pid, [901, 903])):
        raise SystemExit(f"{fn}: a negative GiBUU ID or a lepton ID 901/903 (not seen in the preflight; no declared map)")
    out["fs_pdg"], out["fs_E"] = codes, 1000.0 * E[fo]
    out["fs_px"], out["fs_py"], out["fs_pz"] = 1000.0 * px[fo], 1000.0 * py[fo], 1000.0 * pz[fo]
    out["fs_offsets"] = np.concatenate([[0], np.cumsum(np.bincount(inv[fo], minlength=nev))]).astype(np.int64)
    dpx = np.bincount(inv[fin], px[fin], nev) - np.bincount(inv[init], px[init], nev)
    dpy = np.bincount(inv[fin], py[fin], nev) - np.bincount(inv[init], py[init], nev)
    out["pt_balance"] = np.hypot(dpx, dpy)
    out["e_balance"] = np.bincount(inv[fin], E[fin], nev) - np.bincount(inv[init], E[init], nev) - out["enu"]
    out["unmapped"] = {f"{i},{q}": int(c) for (i, q), c in zip(*np.unique(np.column_stack([pid[fo], ch[fo]])[codes >= OTHER_BASE],
                                                                          axis=0, return_counts=True))} if np.any(codes >= OTHER_BASE) else {}
    return fn, out


def gibuu_codes(codes):
    """Back from the unmapped code OTHER_BASE + 10 ID + (charge + 2) to GiBUU (ID, charge); mapped codes -> (-1, 0)."""
    x = np.asarray(codes, np.int64) - OTHER_BASE
    um = (x >= 0) & (x < 100_000_000)
    return np.where(um, x // 10, -1), np.where(um, x % 10 - 2, 0)


def tune_species_playlist(arg):
    """The PDG species in one playlist's Tune C+H in-grid lists (tune_playlist's rows)."""
    s1dir, p, r0, n = arg
    z = np.load(OFIN, allow_pickle=True)
    fi = s1.fine_index(np.asarray(z["MCgen"][r0:r0 + n], float))
    wt = np.asarray(z["w_truth"][r0:r0 + n], float)
    s = np.load(f"{s1dir}/s1_{p}.npz")
    keep = np.isin(np.asarray(s["mc_targetZ"]), [1, 6]) & (fi >= 0) & np.isfinite(wt)
    off = np.asarray(s["fs_offsets"])
    row = np.repeat(np.arange(off.size - 1), np.diff(off))
    return np.unique(np.asarray(s["fs_pdg"])[keep[row]].astype(np.int64))


def tune_species(s1dir, nproc):
    args, r0 = [], 0
    for p in s1d.PLAYLISTS:
        s = np.load(f"{s1dir}/s1_{p}.npz")
        n = int(s["n_rows"])
        args.append((s1dir, p, r0, n))
        r0 += n
    with mp.get_context("fork").Pool(min(nproc, len(args))) as pool:
        got = pool.map(tune_species_playlist, args)
    return {int(v) for v in np.unique(np.concatenate(got))}


def r12_charm(ent, s1dir, nproc, workdir):
    """R12 (addendum 14 §4): decay GiBUU's charmed hadrons before any feature. If any fail-closed check fails, the
    branch is the fallback: the lists stay undecayed and the charm events are marked for exclusion from the training,
    V1 and V3 samples (as R13). The branch follows from the checks alone."""
    gid, gq = gibuu_codes(ent["fs_pdg"])
    ts = tune_species(s1dir, nproc)
    new, rec = chm.decay_entries(ent, (gid, gq), ts, workdir)
    rec["tune_species"] = sorted(ts)
    off = ent["fs_offsets"]
    row = np.repeat(np.arange(off.size - 1), np.diff(off))
    is_c = np.isin(gid, list(chm.GIBUU_CHARM_IDS))
    charm_ev = np.zeros(off.size - 1, bool)
    charm_ev[row[is_c]] = True
    if new is not None and rec["pass"]:
        rec["branch"] = "decayed (PYTHIA6 tables, every check passed)"
        return new, rec
    rec["branch"] = "fallback: a check failed; charm events excluded from training, V1 and V3 (as R13)"
    out = dict(ent)
    out["charm_excl"] = charm_ev
    return out, rec


def gibuu(ROOT, pools, dV5, res, nproc, s1dir=None, workdir=None):
    c12 = [os.path.join(G, f"work_gibuu_arr/task{i}/FinalEvents.dat") for i in range(1, 81)]
    hf = [f"{P1}/mp3c/prod/task{i}/FinalEvents.dat" for i in range(1001, 1081)]
    jobcard = gfr.DEFAULTS["gibuu_jobcard"]                     # the frozen build's (as mp3c_bcheck.py)
    g_edges, fcut, phi_g, _, _ = b3c.gibuu_density(jobcard)
    z, _, _ = gfr.load_phi_t(sup.OUT)
    ctrl, parts, nat_cols, nat_c = {"jobcard": jobcard, "jobcard_sha256": sha256(jobcard)}, [], [], []
    b3c.G5 = G5
    for which, files, frac, target in (("c12", c12, F_C, 6), ("h", hf, F_H, 1)):
        a, M, _, _, aligned = b3c.events(files, nproc)          # the frozen readers (native, in-PS)
        r, zero = b3c.weights(a, g_edges, phi_g, z["edges"], z["phi_t_density"], float(z["Phi_t"]))
        nat_cols.append([a[k] for k in AX])
        nat_c.append(a["w"] * r / M * 1.0e-38 * frac)
        with mp.get_context("fork").Pool(min(nproc, len(files))) as pool:
            got = dict(pool.map(gibuu_file, files))
        per = [got[f] for f in files]
        enu = np.concatenate([p["enu"] for p in per])
        ok = np.isfinite(np.concatenate([p["lpz"] for p in per])) & (np.concatenate([p["w"] for p in per]) > 0)
        ev = {k: np.concatenate([p[k] for p in per]) for k in ("lE", "lpx", "lpy", "lpz", "w", "hit", "prod", "pt_balance",
                                                                 "e_balance")}
        rr, _ = b3c.weights({"enu": np.where(ok, enu, 0.0)}, g_edges, phi_g, z["edges"], z["phi_t_density"], float(z["Phi_t"]))
        c = np.where(ok, np.nan_to_num(ev["w"]) * rr / M * 1.0e-38 * frac, 0.0)
        # alignment with extract_gibuu: the native PS events of this parser equal the frozen reader's
        pt0 = np.hypot(ev["lpx"], ev["lpy"])
        m = ok & (pt0 >= G5.EDGES["pt"][0]) & (pt0 <= G5.EDGES["pt"][-1]) & (ev["lpz"] >= G5.EDGES["pz"][0]) \
            & (ev["lpz"] <= G5.EDGES["pz"][-1]) & (np.arctan2(pt0, ev["lpz"]) < G5.u3d.u2d.MAX_MUON_THETA_RAD)
        ctrl[f"A_{which}"] = {"frozen_reader_self_aligned": bool(aligned), "n_native_ps": int(m.sum()), "n_frozen": int(a["pt"].size),
                              "pt_bitwise": bool(np.array_equal(pt0[m], a["pt"])), "pz_bitwise": bool(np.array_equal(ev["lpz"][m], a["pz"])),
                              "w_bitwise": bool(np.array_equal(ev["w"][m], a["w"])), "enu_bitwise": bool(np.array_equal(enu[m], a["enu"])),
                              "zero_flux_bin": bool(zero)}
        unm = {}
        for p in per:
            for k, v in p["unmapped"].items():
                unm[k] = unm.get(k, 0) + v
        ctrl[f"unmapped_{which}"] = unm
        if which == "h":
            ebal = ok & (np.abs(ev["e_balance"]) <= PT_BALANCE_MAX_GEV)
            full = ebal & (ev["prod"] != 34)
            miss = ok & ~ebal
            dis_bal = ebal & (ev["prod"] == 34)
            ctrl["Z_h"] = {"rule": "non-DIS H events whose energy balances to 1 MeV balance pT to 1 MeV (S2-IMPLEMENTATION.md, Z)",
                           "n_DIS_energy_balanced": int(dis_bal.sum()),
                           "n_DIS_energy_balanced_pt_above_1MeV": int(np.sum(ev["pt_balance"][dis_bal] > PT_BALANCE_MAX_GEV)),
                           "n_energy_balanced": int(full.sum()), "pt_balance_max_GeV": float(ev["pt_balance"][full].max()),
                           "n_above_1MeV": int(np.sum(ev["pt_balance"][full] > PT_BALANCE_MAX_GEV)),
                           "n_missing_energy_by_production_ID": {str(k): int(v) for k, v in zip(*np.unique(ev["prod"][miss], return_counts=True))},
                           "missing_energy_GeV_quantiles_0.1_0.5_0.9_nonDIS": [float(x) for x in np.quantile(ev["e_balance"][miss & (ev["prod"] != 34)], [0.1, 0.5, 0.9])]
                           if np.any(miss & (ev["prod"] != 34)) else []}
        offs, base = [], 0
        for p in per:
            offs.append(p["fs_offsets"][:-1] + base)
            base += int(p["fs_offsets"][-1])
        parts.append({"enu": np.where(ok, enu, 0.0), "lE": np.nan_to_num(ev["lE"]), "lpx": np.nan_to_num(ev["lpx"]),
                      "lpy": np.nan_to_num(ev["lpy"]), "lpz": np.nan_to_num(ev["lpz"]), "cc": ok, "hit": ev["hit"],
                      "tgt": np.full(enu.size, target), "c": c,
                      "fs_pdg": np.concatenate([p["fs_pdg"] for p in per]), "fs_E": np.concatenate([p["fs_E"] for p in per]),
                      "fs_px": np.concatenate([p["fs_px"] for p in per]), "fs_py": np.concatenate([p["fs_py"] for p in per]),
                      "fs_pz": np.concatenate([p["fs_pz"] for p in per]),
                      "fs_offsets": np.concatenate(offs + [np.array([base], np.int64)])})
    fz = np.load(FROZEN_CH["gibuu_ch"], allow_pickle=True)
    x, v, nn = product([np.concatenate([p[i] for p in nat_cols]) for i in range(5)], np.concatenate(nat_c), dV5)
    ctrl["N"] = {"xsec": rel_close(x, fz["xsec_CH"]), "sumw2": rel_close(v, fz["sumw2_CH"]),
                 "nevt_equal": bool(np.array_equal(nn, fz["nevt_CH"])), "frozen": FROZEN_CH["gibuu_ch"]}
    ctrl["N"]["pass"] = ctrl["N"]["xsec"]["pass"] and ctrl["N"]["sumw2"]["pass"] and ctrl["N"]["nevt_equal"]
    ctrl["pass"] = bool(ctrl["N"]["pass"] and ctrl["Z_h"]["n_above_1MeV"] == 0 and ctrl["Z_h"]["n_energy_balanced"] > 0
                        and all(all(v_ for k_, v_ in ctrl[f"A_{w}"].items() if k_ not in ("n_native_ps", "n_frozen", "zero_flux_bin"))
                                and not ctrl[f"A_{w}"]["zero_flux_bin"] for w in ("c12", "h")))
    ent = concat_entries(parts)
    if s1dir is None:
        raise SystemExit("STOP: GiBUU needs --s1 for R12's Tune species")
    ent, ctrl["R12"] = r12_charm(ent, s1dir, nproc, workdir)
    return ctrl, ent


# ---------------------------------------------------------------- Tune v1
def tune_playlist(arg):
    s1dir, p, r0, n = arg
    z = np.load(OFIN, allow_pickle=True)
    g = np.asarray(z["MCgen"][r0:r0 + n], float)
    wt = np.asarray(z["w_truth"][r0:r0 + n], float)
    s = np.load(f"{s1dir}/s1_{p}.npz")
    tz = np.asarray(s["mc_targetZ"])
    fi = s1.fine_index(g)
    keep = np.isin(tz, [1, 6]) & (fi >= 0) & np.isfinite(wt)
    rows = np.nonzero(keep)[0]
    off = np.asarray(s["fs_offsets"])
    st_, cnt = off[rows], np.diff(off)[rows]
    o2 = np.zeros(rows.size + 1, np.int64)
    np.cumsum(cnt, out=o2[1:])
    gi = np.repeat(st_ - o2[:-1], cnt) + np.arange(o2[-1], dtype=np.int64)
    pdg = np.asarray(s["fs_pdg"])[gi].astype(np.int64)
    E, px, py, pz = (np.asarray(s[k])[gi].astype(float) for k in ("fs_E", "fs_px", "fs_py", "fs_pz"))
    sn, cs = math.sin(A_BEAM), math.cos(A_BEAM)
    py, pz = cs * py - sn * pz, sn * py + cs * pz              # MAT RotateX(A_BEAM): the beam frame
    fe = features(pdg, E, px, py, pz, o2)
    out = {"pt": g[rows, 0], "pz": g[rows, 1], "eavail": g[rows, 2], "q3": g[rows, 3], "W": g[rows, 4],
           "enu": np.asarray(s["mc_incomingE"])[rows] / 1000.0}
    for k in F_PRIMARY[6:] + V3_KEYS:
        out[k] = fe[k]
    out["w_truth"], out["tgt"], out["i"], out["fine"] = wt[rows], tz[rows], r0 + rows, fi[rows]
    out["nKE_val"], out["nKE_ev"] = fe["_neutron_KE"], fe["_neutron_row"]
    return p, out, {"n": int(n), "n_CH_in_grid": int(rows.size),
                    "n_other_nuclei_in_grid": int(np.sum(~np.isin(tz, [1, 6]) & (fi >= 0)))}


def tune(s1dir, nproc, res):
    z = np.load(OFIN, allow_pickle=True)
    if sha256(OFIN) != OFIN_SHA:
        raise SystemExit("of_inputs_5d digest differs")
    args, r0 = [], 0
    for p in s1d.PLAYLISTS:
        s = np.load(f"{s1dir}/s1_{p}.npz")
        if int(s["mcgen_row0"]) != r0:
            raise SystemExit(f"{p}: mcgen_row0 {int(s['mcgen_row0'])} != {r0}")
        n = int(s["n_rows"])
        args.append((s1dir, p, r0, n))
        r0 += n
    if r0 != z["MCgen"].shape[0]:
        raise SystemExit("S1 rows do not cover MCgen")
    with mp.get_context("fork").Pool(min(nproc, len(args))) as pool:
        got = pool.map(tune_playlist, args)
    out, base = {}, 0
    for k in got[0][1]:
        if k == "nKE_ev":
            continue
        out[k] = np.concatenate([g[1][k] for g in got])
    evs = []
    for g in got:
        evs.append(g[1]["nKE_ev"] + base)
        base += g[1]["i"].size
    out["nKE_ev"] = np.concatenate(evs)
    res["tune"] = {"per_playlist": {g[0]: g[2] for g in got}, "n_CH_in_grid": int(out["i"].size),
                   "n_H_in_grid": int(np.sum(out["tgt"] == 1))}
    return out


# ---------------------------------------------------------------- H0 and H_CH,an
def ratio_args(gname):
    jp = os.path.join(A7_NULL_DIR, f"null-{A7_NULLS[gname]}-F.json")
    return jp, json.loads(Path(jp).read_text())


def h0_and_hybrid(gname, xh, nh, res, out):
    jp, R = ratio_args(gname)
    cedges = [np.asarray(c, float) for c in R["coarse_edges"]]
    edges = [np.asarray(G5.EDGES[a], float) for a in AX]
    only = np.zeros(int(np.prod([len(c) - 1 for c in cedges])), bool)
    only[np.asarray(R["only_cells"], int)] = True
    den, cnt_den = np.load(MNVTUNE, allow_pickle=True), st.load_counts(Path(MNVTUNE))
    num_f = np.load(R["numerator"]["path"], allow_pickle=True)
    rho0, _ = st.fine_ratio(np.asarray(num_f["xsec_flat"], float), np.asarray(den["xsec_flat"], float),
                            st.load_counts(Path(R["numerator"]["path"])), cnt_den, edges, cedges, only)
    frozen_rho = np.load(R["rho_npz"]["path"])["rho"]
    h0 = {"null_json": jp, "null_json_sha256": sha256(jp), "rho_npz_sha256": sha256(R["rho_npz"]["path"]),
          "rho_npz_sha256_matches_json": sha256(R["rho_npz"]["path"]) == R["rho_npz"]["sha256"],
          "numerator_sha256_matches_json": sha256(R["numerator"]["path"]) == R["numerator"]["sha256"],
          "denominator_sha256_matches_json": sha256(MNVTUNE) == R["denominator"]["sha256"],
          "rho_bitwise": bool(np.array_equal(rho0, frozen_rho))}
    h0["pass"] = all(v for k, v in h0.items() if isinstance(v, bool))
    res["controls"][f"H0_{gname}"] = h0
    if not h0["pass"]:
        return None
    rho, acc = st.fine_ratio(xh, np.asarray(den["xsec_flat"], float), nh, cnt_den, edges, cedges, only)
    rp = out / f"rho_an_{gname}.npz"
    np.savez_compressed(rp, rho=rho)
    rj = {"schema": "s5p-fine-ratio/1", "label": f"H_CH,an: fine null {gname} (harmonized CH, MP-2 S2) / MnvTune v1, A7's "
                                                 "construction (coarse edges, only-cells, n_min, clips)",
          "numerator": {"path": str(out / f"harmonized_{gname}.npz"), "sha256": None},
          "denominator": {"path": MNVTUNE, "sha256": sha256(MNVTUNE)}, "code_sha256": sha256(Path(st.__file__).resolve()),
          "fine_edges": [e.tolist() for e in edges], "coarse_edges": [c.tolist() for c in cedges],
          "only_cells": R["only_cells"], "rho_npz": {"path": str(rp), "sha256": sha256(rp)}, "stats": acc,
          "a7_null": jp}
    return rj


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    global G5
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", type=Path, required=True)
    ap.add_argument("--s1", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--nproc", type=int, default=32)
    ap.add_argument("--only", default="genie_cv,genie_mec,nuwro_ch,gibuu_ch,tune")
    a = ap.parse_args(argv)
    t0 = time.time()
    if sha256(a.contract) != CONTRACT_SHA:
        print("STOP: the contract's sha256 is not the frozen one", flush=True)
        return 4
    a.out.mkdir(parents=True, exist_ok=False)
    ROOT = gfr.import_root()
    G5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    for mm in (gfr, sup, s1d, chm, b3c, m5, s1, st):
        if Path(mm.__file__).resolve().parent != HERE:
            raise SystemExit(f"{mm.__name__} imported from {mm.__file__}, not {HERE}")
    res = {"schema": "mp2-s2-harmonize/1", "argv": sys.argv, "slurm_job": os.environ.get("SLURM_JOB_ID"),
           "contract_sha256": CONTRACT_SHA, "environment": gfr.environment(), "code": {}, "controls": {},
           "harmonized": {}, "inputs": {}}
    for mm in [sys.modules[__name__], gfr, sup, s1d, chm, b3c, m5, s1, st, G5, G5.u3d, G5.u3d.u2d]:
        p = Path(mm.__file__).resolve()
        res["code"][mm.__name__] = {"file": str(p), "sha256": sha256(p)}
    res["inputs"]["dump"] = {"s2_dump.json": sha256(a.dump / "s2_dump.json")}
    pools = [np.load(a.pool / f"pool_b{b}.npy") for b in range(len(ENU_BINS) - 1)]
    res["inputs"]["pool_sha256"] = {f"pool_b{b}.npy": sha256(a.pool / f"pool_b{b}.npy") for b in range(len(ENU_BINS) - 1)}
    dV5 = G5.widths(*AX)
    only = a.only.split(",")

    def finish(rc, msg):
        ru = resource.getrusage(resource.RUSAGE_SELF)
        res.update(verdict=msg, exit=rc, cpu_s=ru.ru_utime + ru.ru_stime, maxrss_kb=ru.ru_maxrss, wall_s=time.time() - t0)
        (a.out / "s2_harmonize.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
        print(msg, flush=True)
        return rc

    for gname in ("genie_cv", "genie_mec", "nuwro_ch", "gibuu_ch"):
        if gname not in only:
            continue
        t1 = time.time()
        if gname.startswith("genie"):
            ctrl, ent = genie(ROOT, gname, a.dump, pools, dV5, res)
        elif gname == "nuwro_ch":
            ctrl, ent = nuwro(ROOT, a.dump, pools, dV5, res)
        else:
            ctrl, ent = gibuu(ROOT, pools, dV5, res, a.nproc, a.s1, Path(os.environ.get("TMPDIR", str(a.out))))
        res["controls"][gname] = ctrl
        print("CONTROLS", gname, json.dumps({"N": ctrl["N"], "pass": ctrl["pass"]}, default=float), flush=True)
        if not ctrl["pass"]:
            return finish(3, f"STOP: a control failed for {gname}; nothing harmonized")
        ev, (xh, vh, nh), xhh, undec = harmonize(gname, ent, SEED_G[gname], pools, dV5, res)
        if undec is not None:                 # R12: the same harmonization without the charm decays (descriptive)
            np.savez(a.out / f"harmonized_{gname}_undecayed.npz", xsec_flat=undec[0], sumw2_flat=undec[1], nevt_flat=undec[2],
                     shape=np.asarray(G5.SHAPE), meta_json=np.asarray(json.dumps({"generator": gname, "quantity":
                     "as harmonized_<G>.npz, with GiBUU's charmed hadrons left undecayed (R12 descriptive only)"})))
        rj = h0_and_hybrid(gname, xh, nh, res, a.out)
        if rj is None:
            return finish(3, f"STOP: H0 failed for {gname}")
        hp = a.out / f"harmonized_{gname}.npz"
        np.savez(hp, xsec_flat=xh, sumw2_flat=vh, nevt_flat=nh, xsec_H_part=xhh, shape=np.asarray(G5.SHAPE),
                 meta_json=np.asarray(json.dumps({"generator": gname, "quantity": "dsigma per CH nucleon, harmonized "
                                                  "(analysis convention, MP-2 S2)", "support_GeV": SUPPORT[gname]})))
        rj["numerator"]["sha256"] = sha256(hp)
        (a.out / f"hybrid_an_{gname}.json").write_text(json.dumps(rj, indent=1) + "\n")
        np.savez(a.out / f"events_{gname}.npz", **ev)
        res["harmonized"][gname]["wall_s"] = round(time.time() - t1, 1)
        res["harmonized"][gname]["hybrid_an_stats"] = rj["stats"]
        print("HARMONIZED", gname, json.dumps(res["harmonized"][gname], default=float), flush=True)
    if "tune" in only:
        tv = tune(a.s1, a.nproc, res)
        np.savez(a.out / "tune_CH.npz", **tv)
        print("TUNE", json.dumps(res["tune"]), flush=True)
    res["outputs"] = {p.name: sha256(p) for p in sorted(a.out.glob("*.npz")) if p.is_file()}
    return finish(0, "S2 harmonization done")


if __name__ == "__main__":
    raise SystemExit(main())
