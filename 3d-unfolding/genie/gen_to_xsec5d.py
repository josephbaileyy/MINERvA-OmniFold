#!/usr/bin/env python3
"""Truth-level 5D generator prediction d^5 sigma/(dpT dp|| dEavail dq3 dW) per nucleon.

Four fixed generators, each on the scalar-5D analysis grid (C order pt, pz,
eavail, q3, W; 14*16*7*7*6 = 65856 cells):

  genie_cv   GENIE 2.12.10 CV (no MEC)   genie_mefhc_cv_ALL.gst.root
  genie_mec  GENIE 2.12.10 + Valencia    genie_mefhc_mec_ALL.gst.root
  nuwro      NuWro 21.09                 nuwro_flat5d_p*.root (nuwro_to_flat_5d.C)
  gibuu      GiBUU 2019                  work_gibuu_arr/task*/FinalEvents.dat

The event selection, pT/p||/E_avail/W arithmetic and normalisation of each
generator are those of that generator's existing 3D and (E_avail,W) converters,
imported where they are functions and restated statement-for-statement where they
are inline:

  genie_cv   genie_to_xsec3d.py + gen_to_xsec_eavailW.py  (sigma_CC/13 x N_bin/N_cc)
  genie_mec  genie_mec_to_xsec3d.py                        (sigma_CC/13 x N_bin/N_nonMEC)
  nuwro      nuwro_to_xsec3d.py                            (sum w_bin / N_total)
  gibuu      gibuu_to_xsec3d.py + gibuu_to_xsec_eavailW.py (sum perweight_bin / M x 1e-38)

GENIE+MEC: the two existing converters DISAGREE on normalisation -- the (E_avail,W)
band ran gen_to_xsec_eavailW.py, which divides by all CC, the 3D converter by the
non-MEC CC count. xsec_flat carries the 3D (genie_mec_to_xsec3d.py) convention;
meta.normalisation.factor_to_eavailW_band_convention = N_nonMEC/N_cc converts.

q3 is PlotUtils Getq3True: calcq3(mc_Q2, E_nu, E_mu) = sqrt(Q2 + (E_nu-E_mu)^2),
with Q2 the lab-frame -(k-k')^2 (what the MINERvA tuple branch mc_Q2 holds).

Run in the analysis env (root_6_28), from a checkout whose 3d-unfolding/ and
2d-unfolding/ hold the converters imported below:
  python gen_to_xsec5d.py --generator genie_cv --genie-dir <.../3d-unfolding/genie> \
      --out genie_cv_xsec5d.npz
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

# OI-136: import root derived from this file, never a hardcoded cluster root.
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for _p in (str(_REPO / "3d-unfolding"), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ROOT  # noqa: E402

import unfold_3d_omnifold_unbinned as u3d  # noqa: E402
import genie_to_xsec3d as g3d  # noqa: E402
import gen_to_xsec_eavailW as gew  # noqa: E402
import gibuu_to_xsec_eavailW as gibew  # noqa: E402
import gibuu_to_xsec3d as gib3d  # noqa: E402
from gst_reader import read_gst  # noqa: E402

EDGES = {
    "pt": np.asarray([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0,
                      1.25, 1.5, 2.5, 4.5], float),
    "pz": np.asarray([1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60],
                     float),
    "eavail": np.asarray([0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100], float),
    "q3": np.asarray([0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100], float),
    "W": np.asarray([0, 1.1, 1.4, 1.8, 2.2, 3.0, 100], float),
}
AXES = ("pt", "pz", "eavail", "q3", "W")
SHAPE = tuple(len(EDGES[a]) - 1 for a in AXES)
PT, PZ, EA, WE = EDGES["pt"], EDGES["pz"], EDGES["eavail"], EDGES["W"]

# the grid must be the one the existing converters bin on
assert np.array_equal(PT, np.asarray(u3d.PT_EDGES, float))
assert np.array_equal(PZ, np.asarray(u3d.PZ_EDGES, float))
assert np.array_equal(EA, np.asarray(u3d.EAVAIL_EDGES, float))
assert np.array_equal(EA, gew.EAVAIL_EDGES) and np.array_equal(WE, gew.W_EDGES)
assert np.array_equal(EA, gibew.EAVAIL_EDGES) and np.array_equal(WE, gibew.W_EDGES)

# CVUniverse.h:39-41 (diagnostic struck-nucleon W only; production W uses M_n, as
# every existing converter does)
CVU_M_N, CVU_M_P = 0.93956536, 0.938272013
CVU_M_NUCLEON = (1.5 * CVU_M_N + CVU_M_P) / 2.5

EAVAIL_CPP = """
double r = 0.0;
for (int j = 0; j < nf; ++j) {
  const int pdg = pdgf[j]; const double E = Ef[j]; const int a = std::abs(pdg);
  if (pdg == 22) r += E;
  else if (a == 211) r += E - %r;
  else if (pdg == 111) r += E;
  else if (pdg == 2212) r += E - %r;
}
return r;
""" % (g3d.MASS_PI_PM, g3d.MASS_P)


def sha256(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def file_record(path, role):
    p = os.path.abspath(path)
    return {"path": p, "role": role, "bytes": os.path.getsize(p), "sha256": sha256(p)}


def q3_true(enu, kx, ky, kz, emu, mx, my, mz):
    """PlotUtils Getq3True: calcq3(Q2, Enu, Elep) = sqrt(Q2 + (Enu-Elep)^2), with
    Q2 = -(k-k')^2 from the lab-frame neutrino k and muon k' (== tuple mc_Q2)."""
    q0 = enu - emu
    q2 = (kx - mx) ** 2 + (ky - my) ** 2 + (kz - mz) ** 2 - q0 * q0
    with np.errstate(invalid="ignore"):
        return q2, np.sqrt(q2 + q0 * q0)


def w_struck(enu, emu, pz, pmu, hitnuc):
    """CVUniverse::GetTrueExperimentersW with the struck-nucleon mass
    (CVUniverse.h:396-410); NaN where W^2 < 0. DIAGNOSTIC ONLY."""
    m = np.where(hitnuc == 2112, CVU_M_N, np.where(hitnuc == 2212, CVU_M_P, CVU_M_NUCLEON))
    costh = np.clip(pz / pmu, -1.0, 1.0)
    q2 = 4.0 * enu * emu * np.sin(np.arccos(costh) / 2.0) ** 2
    with np.errstate(invalid="ignore"):
        return np.sqrt(m * m + 2.0 * (enu - emu) * m - q2)


# ---------------------------------------------------------------------------
# per-generator event extraction -> dict of per-event arrays (in-PS events only)
# ---------------------------------------------------------------------------
def extract_genie(gst, mec_mode, graphs, flux, flux_hist, parity_n):
    ROOT.gErrorIgnoreLevel = ROOT.kError
    cols = ["cc", "mec", "Ev", "pxv", "pyv", "pzv", "El", "pxl", "pyl", "pzl", "Q2",
            "hitnuc", "eav5d"]
    d = (ROOT.RDataFrame("gst", gst).Define("eav5d", EAVAIL_CPP).AsNumpy(cols))
    cc = d["cc"].astype(bool)
    mec = d["mec"].astype(bool)
    n_all = cc.size
    n_cc = int(cc.sum())
    n_nonmec = int((cc & ~mec).sum())
    pt = np.hypot(d["pxl"], d["pyl"])
    pz = d["pzl"]
    in_ps = u3d.u2d.in_truth_phase_space
    lo_t, hi_t, lo_z, hi_z = PT[0], PT[-1], PZ[0], PZ[-1]
    inps = np.fromiter((c and in_ps(float(a), float(b), lo_t, hi_t, lo_z, hi_z)
                        for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())),
                       dtype=bool, count=n_all)
    sel = np.where(inps)[0]
    Ev, pxv, pyv, pzv = (d[k][sel] for k in ("Ev", "pxv", "pyv", "pzv"))
    El, pxl, pyl, pzl = (d[k][sel] for k in ("El", "pxl", "pyl", "pzl"))
    W = np.fromiter((gew.w_true((a, b, c, e), (f, g, h, i)) for a, b, c, e, f, g, h, i in
                     zip(Ev.tolist(), pxv.tolist(), pyv.tolist(), pzv.tolist(),
                         El.tolist(), pxl.tolist(), pyl.tolist(), pzl.tolist())),
                    dtype=float, count=sel.size)
    Q2lab, q3 = q3_true(Ev, pxv, pyv, pzv, El, pxl, pyl, pzl)
    gstQ2 = d["Q2"][sel]
    pmu = np.sqrt(pxl * pxl + pyl * pyl + pzl * pzl)
    Wcvu = w_struck(Ev, El, pzl, pmu, d["hitnuc"][sel])

    # reader parity: the first parity_n events through the EXISTING reader +
    # functions must give bitwise-identical pt, pz, E_avail, W and PS decision
    par = {"n_checked": 0, "n_mismatch": 0}
    pos = {int(i): k for k, i in enumerate(sel[sel < parity_n])}
    for i, ev in enumerate(read_gst(gst)):
        if i >= parity_n:
            break
        par["n_checked"] += 1
        ok_cc = bool(ev["cc"]) == bool(cc[i])
        _, a, b, c = ev["lep"]
        p_t = float(np.hypot(a, b))
        ps = ev["cc"] and in_ps(p_t, float(c), lo_t, hi_t, lo_z, hi_z)
        good = ok_cc and (ps == (i in pos))
        if good and ps:
            k = pos[i]
            good = (p_t == pt[i] and float(c) == pz[i]
                    and g3d.eavail_true(ev["fs"]) == d["eav5d"][i]
                    and gew.w_true(ev["nu"], ev["lep"]) == W[k])
        par["n_mismatch"] += (not good)

    sigma_nuc, info = g3d.flux_avg_sigma_cc_per_nucleon(graphs, flux, flux_hist)
    if mec_mode:
        per_evt = sigma_nuc / n_nonmec          # genie_mec_to_xsec3d.py:102
        conv = "genie_mec_to_xsec3d.py: sigma_totcc/13 / N_nonMEC per event (3D convention)"
    else:
        per_evt = sigma_nuc / n_cc              # genie_to_xsec3d.py:145, gen_to_xsec_eavailW.py:110
        conv = "genie_to_xsec3d.py / gen_to_xsec_eavailW.py: sigma_totcc/13 x N_bin/N_cc"
    ev = {"pt": pt[sel], "pz": pz[sel], "eavail": d["eav5d"][sel], "q3": q3, "W": W,
          "is_mec": mec[sel]}
    norm = {"convention": conv, "sigma_totcc_flux_avg_per_nucleon_cm2": sigma_nuc,
            "sigma_info": info, "N_events_in_file": n_all, "N_cc": n_cc,
            "N_nonMEC_cc": n_nonmec, "f_MEC": (n_cc - n_nonmec) / n_cc,
            "per_event_xsec_cm2": per_evt,
            "graphs": graphs, "flux": flux, "flux_hist": flux_hist}
    if mec_mode:
        norm["factor_to_eavailW_band_convention"] = n_nonmec / n_cc
    diag = {"reader_parity": par,
            "gst_Q2_vs_lab_Q2_max_absdiff_GeV2": float(np.max(np.abs(gstQ2 - Q2lab))),
            "gst_Q2_vs_lab_Q2_max_reldiff": float(np.max(np.abs(gstQ2 - Q2lab)
                                                         / np.maximum(np.abs(gstQ2), 1e-12))),
            "W_struck_nucleon_mass": w_migration(W, Wcvu)}
    return ev, norm, diag


def extract_nuwro(new_files, old_files):
    ROOT.gErrorIgnoreLevel = ROOT.kError
    parity = []
    cols_old = ["cc", "pt", "pz", "eavail", "W", "weight"]
    cols = cols_old + ["Enu", "Q2", "q0", "q3", "hitnuc", "dyn"]
    acc = {k: [] for k in cols}
    n_total = 0
    for fn, fo in zip(new_files, old_files):
        f = ROOT.TFile.Open(fn)
        nt = int(f.Get("nTotal").GetVal())
        f.Close()
        f = ROOT.TFile.Open(fo)
        nt_old = int(f.Get("nTotal").GetVal())
        f.Close()
        n_total += nt
        d = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(cols)
        o = ROOT.RDataFrame("nuwro_obs", fo).AsNumpy(cols_old)
        same = {k: bool(np.array_equal(d[k], o[k], equal_nan=True)) for k in cols_old}
        parity.append({"new": fn, "old": fo, "nTotal_equal": nt == nt_old,
                       "branches_bitwise_equal": same})
        for k in cols:
            acc[k].append(d[k])
    d = {k: np.concatenate(v) for k, v in acc.items()}
    sel = d["cc"].astype(bool)
    d = {k: v[sel] for k, v in d.items()}
    pt, pz = d["pt"], d["pz"]
    # nuwro_to_xsec3d.py:59-61 (nuwro_to_xsec_eavailW.py:55-58 adds W finite, in [0,1e4))
    m = (np.isfinite(pt) & np.isfinite(pz)
         & (pt >= PT[0]) & (pt <= PT[-1]) & (pz >= PZ[0]) & (pz <= PZ[-1])
         & (np.arctan2(pt, pz) < u3d.u2d.MAX_MUON_THETA_RAD))
    W = d["W"]
    wok = np.isfinite(W) & (W >= 0) & (W < 1e4)
    d = {k: v[m] for k, v in d.items()}
    pmu = np.sqrt(d["pt"] ** 2 + d["pz"] ** 2)
    Emu = d["Enu"] - d["q0"]
    Wcvu = w_struck(d["Enu"], Emu, d["pz"], pmu, d["hitnuc"])
    ev = {"pt": d["pt"], "pz": d["pz"], "eavail": d["eavail"], "q3": d["q3"], "W": W[m],
          "weight_raw": d["weight"], "divisor": float(n_total), "scale": 1.0}
    norm = {"convention": "nuwro_to_xsec3d.py / nuwro_to_xsec_eavailW.py: "
                          "sum(weight in bin)/N_total; weight = NuWro flux-avg sigma_CC/nucleon",
            "N_total": n_total, "N_cc": int(sel.sum()),
            "weight_mean_cm2": float(d["weight"].mean()),
            "weight_unique": int(np.unique(d["weight"]).size)}
    diag = {"flat_parity_vs_existing_nuwro_flat": parity,
            "in_PS_failing_eavailW_W_mask": int((~wok[m]).sum()),
            "in_PS_q3_sentinel": int((d["q3"] == -9999).sum()),
            "W_struck_nucleon_mass": w_migration(W[m], Wcvu)}
    return ev, norm, diag


def extract_gibuu(files):
    """gibuu_to_xsec3d.py:91-133 + gibuu_to_xsec_eavailW.py:56-106, per file."""
    MASS_PI, MASS_P = gib3d.MASS_PI, gib3d.MASS_P
    M_N, M_MU, MUON_IDS = gibew.M_NUCLEON, gibew.M_MU, gibew.MUON_IDS
    out = {k: [] for k in ("pt", "pz", "eavail", "q3", "W", "w", "enu_ok")}
    n_events = 0
    for fn in files:
        d = np.loadtxt(fn, comments="#")
        if d.ndim == 1:
            d = d[None, :]
        run = d[:, 0].astype(np.int64); ev = d[:, 1].astype(np.int64)
        pid = d[:, 2].astype(int); ch = d[:, 3].astype(int)
        pw = d[:, 4]; E = d[:, 8]; px = d[:, 9]; py = d[:, 10]; pz = d[:, 11]
        enu = d[:, 14]
        key = run * 10_000_000 + ev
        ukey, inv = np.unique(key, return_inverse=True)
        nev = ukey.size
        n_events += nev
        lep = np.isin(pid, MUON_IDS)
        pt_e = np.full(nev, np.nan); pz_e = np.full(nev, np.nan); w_e = np.zeros(nev)
        emu_e = np.full(nev, np.nan); enu_e = np.full(nev, np.nan)
        px_e = np.full(nev, np.nan); py_e = np.full(nev, np.nan)
        li = inv[lep]
        pt_e[li] = np.hypot(px[lep], py[lep]); pz_e[li] = pz[lep]; w_e[li] = pw[lep]
        emu_e[li] = E[lep]; enu_e[li] = enu[lep]
        px_e[li] = px[lep]; py_e[li] = py[lep]
        had = (pw != 0) & (~lep)
        econ = np.zeros(d.shape[0])
        m = had & (pid == 1) & (ch == 1);           econ[m] = E[m] - MASS_P
        m = had & (pid == 101) & (np.abs(ch) == 1); econ[m] = E[m] - MASS_PI
        m = had & (pid == 101) & (ch == 0);         econ[m] = E[m]
        m = had & (pid == 999);                     econ[m] = E[m]
        ea_e = np.zeros(nev); np.add.at(ea_e, inv, econ)
        pmu = np.sqrt(np.clip(emu_e**2 - M_MU**2, 0, None))
        with np.errstate(invalid="ignore", divide="ignore"):
            costh = np.clip(pz_e / pmu, -1.0, 1.0)
            theta = np.arccos(costh)
            q2 = 4.0 * enu_e * emu_e * np.sin(theta / 2.0) ** 2
            w2 = M_N**2 + 2.0 * (enu_e - emu_e) * M_N - q2
            W_e = np.where(w2 > 0, np.sqrt(np.clip(w2, 0, None)), 0.0)
        _, q3_e = q3_true(enu_e, 0.0, 0.0, enu_e, emu_e, px_e, py_e, pz_e)
        ok = np.isfinite(pt_e) & (w_e > 0)            # gibuu_to_xsec3d.py:118
        for k, v in (("pt", pt_e), ("pz", pz_e), ("eavail", ea_e), ("q3", q3_e),
                     ("W", W_e), ("w", w_e), ("enu_ok", np.isfinite(enu_e))):
            out[k].append(v[ok])
    a = {k: np.concatenate(v) for k, v in out.items()}
    m = (np.isfinite(a["pt"]) & np.isfinite(a["pz"])
         & (a["pt"] >= PT[0]) & (a["pt"] <= PT[-1]) & (a["pz"] >= PZ[0]) & (a["pz"] <= PZ[-1])
         & (np.arctan2(a["pt"], a["pz"]) < u3d.u2d.MAX_MUON_THETA_RAD))
    a = {k: v[m] for k, v in a.items()}
    M = float(len(files))
    ev = {"pt": a["pt"], "pz": a["pz"], "eavail": a["eavail"], "q3": a["q3"], "W": a["W"],
          "weight_raw": a["w"], "divisor": M, "scale": 1.0e-38}
    norm = {"convention": "gibuu_to_xsec3d.py / gibuu_to_xsec_eavailW.py: "
                          "sum(perweight in bin)/M x 1e-38, M = number of FinalEvents files",
            "M_files": int(M), "N_events": n_events}
    diag = {"in_PS_enu_not_finite": int((~a["enu_ok"]).sum())}
    return ev, norm, diag


def w_migration(W, Wcvu):
    b0 = np.digitize(W, WE); b1 = np.digitize(Wcvu, WE)
    return {"n": int(W.size), "n_W2_negative_nan_in_CVUniverse": int(np.isnan(Wcvu).sum()),
            "n_W_bin_changes": int((b0 != b1).sum()),
            "max_abs_dW_GeV": float(np.nanmax(np.abs(W - Wcvu)))}


# ---------------------------------------------------------------------------
def hist(cols, w, edges):
    c, _ = np.histogramdd(np.column_stack(cols), bins=edges, weights=w)
    return c


def widths(*names):
    ws = [np.diff(EDGES[a]) for a in names]
    out = ws[0]
    for w in ws[1:]:
        out = np.multiply.outer(out, w)
    return out


def build(gen, ev, norm):
    """Returns xsec5, sumw2_5, nevt5 and the exact existing-converter 3D and
    (E_avail,W) arrays from the same events."""
    cols5 = [ev[a] for a in AXES]
    e5 = [EDGES[a] for a in AXES]
    dV5 = widths(*AXES)
    dV3 = widths("pt", "pz", "eavail")
    dVew = widths("eavail", "W")
    nevt5 = hist(cols5, None, e5)
    if gen in ("genie_cv", "genie_mec"):
        s, n = norm["sigma_totcc_flux_avg_per_nucleon_cm2"], None
        c3 = hist([ev["pt"], ev["pz"], ev["eavail"]], None, [PT, PZ, EA])
        cew = hist([ev["eavail"], ev["W"]], None, [EA, WE])
        if gen == "genie_cv":
            n = norm["N_cc"]
            x5 = s * (nevt5 / n) / dV5
            x3 = s * (c3 / n) / dV3                    # genie_to_xsec3d.py:145
            xew = s * (cew / n) / dVew                 # gen_to_xsec_eavailW.py:110
            xew_alt = None
        else:
            pe = s / norm["N_nonMEC_cc"]
            x5 = nevt5 * pe / dV5
            x3 = c3 * pe / dV3                          # genie_mec_to_xsec3d.py:105-107
            xew = s * (cew / norm["N_cc"]) / dVew       # band ran gen_to_xsec_eavailW.py
            xew_alt = cew * pe / dVew                   # the 3D convention, same events
        v5 = nevt5 * (norm["per_event_xsec_cm2"] ** 2) / dV5 ** 2
    else:
        # nuwro: wsum/N_total/dV (nuwro_to_xsec3d.py:71, nuwro_to_xsec_eavailW.py:70);
        # gibuu: wsum/M/dV*1e-38 (gibuu_to_xsec3d.py:139, gibuu_to_xsec_eavailW.py:112)
        wr, div, sc = ev["weight_raw"], ev["divisor"], ev["scale"]
        x5 = hist(cols5, wr, e5) / div / dV5 * sc
        v5 = hist(cols5, wr * wr, e5) / div ** 2 / dV5 ** 2 * sc ** 2
        x3 = hist([ev["pt"], ev["pz"], ev["eavail"]], wr, [PT, PZ, EA]) / div / dV3 * sc
        xew = hist([ev["eavail"], ev["W"]], wr, [EA, WE]) / div / dVew * sc
        xew_alt = None
    return x5, v5, nevt5, x3, xew, xew_alt


def read_th(path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if h.InheritsFrom("TH3"):
        a = np.array([[[h.GetBinContent(i, j, k) for k in range(1, h.GetNbinsZ() + 1)]
                       for j in range(1, h.GetNbinsY() + 1)]
                      for i in range(1, h.GetNbinsX() + 1)])
    else:
        a = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)]
                      for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return a


def compare(a, ref, var=None):
    nz = ref != 0
    r = {"max_rel_diff_nonzero_bins": float(np.max(np.abs(a[nz] - ref[nz]) / np.abs(ref[nz])))
         if nz.any() else None,
         "n_bins": int(ref.size), "n_ref_zero": int((~nz).sum()),
         "n_zero_mismatch": int(((a == 0) != (ref == 0)).sum()),
         "bitwise_equal": bool(np.array_equal(a, ref))}
    if var is not None:
        # different-sample comparison: pull with (approximately) equal-size samples
        m = var > 0
        pull2 = (a[m] - ref[m]) ** 2 / (2.0 * var[m])
        r["chi2_equal_stats_approx"] = float(pull2.sum())
        r["ndf"] = int(m.sum())
    return r


def git_head(root):
    """HEAD of the code root; a git-archive export records it in SOURCE_COMMIT."""
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel", "HEAD"],
                             capture_output=True, text=True, timeout=30).stdout.split()
        if len(out) == 2 and Path(out[0]).resolve() == Path(root).resolve():
            return out[1]
    except Exception:  # noqa: BLE001 -- provenance only
        pass
    sc = Path(root) / "SOURCE_COMMIT"
    return ("export-of:" + sc.read_text().strip()) if sc.exists() else None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generator", required=True,
                    choices=["genie_cv", "genie_mec", "nuwro", "gibuu"])
    ap.add_argument("--genie-dir", required=True,
                    help="directory holding the generator event files and existing ROOT outputs")
    ap.add_argument("--nuwro-flat5d-glob", default=None,
                    help="glob for nuwro_to_flat_5d.C outputs (nuwro only)")
    ap.add_argument("--nuwro-raw-glob", default=None,
                    help="glob for the raw NuWro files the flat5d were made from (sha256 only)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--parity-n", type=int, default=20000)
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError
    G = os.path.abspath(args.genie_dir)
    gen = args.generator
    inputs = []
    ref3d = {"genie_cv": "genie_cv_xsec3d.root", "genie_mec": "genie_mec_cv_xsec3d.root",
             "nuwro": "nuwro_cv_xsec3d.root", "gibuu": "gibuu_cv_xsec3d.root"}[gen]
    refew = {"genie_cv": "genie_cv_xsec_eavailW.root", "genie_mec": "genie_mec_xsec_eavailW.root",
             "nuwro": "nuwro_cv_xsec_eavailW.root", "gibuu": "gibuu_cv_xsec_eavailW.root"}[gen]

    if gen in ("genie_cv", "genie_mec"):
        gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv"
                           else "genie_mefhc_mec_ALL.gst.root")
        graphs = os.path.join(G, "xsec_graphs.root")
        flux = os.path.join(G, "flux_mefhc_numu.root")
        ev, norm, diag = extract_genie(gst, gen == "genie_mec", graphs, flux, "flux_numu",
                                       args.parity_n)
        inputs += [file_record(gst, "events"), file_record(graphs, "normalisation"),
                   file_record(flux, "normalisation")]
    elif gen == "nuwro":
        new = sorted(glob.glob(args.nuwro_flat5d_glob))
        old = sorted(glob.glob(os.path.join(G, "work_nuwro_p*/nuwro_flat.root")))
        if not new or len(new) != len(old):
            raise SystemExit(f"flat5d/flat file sets differ: {len(new)} vs {len(old)}")
        ev, norm, diag = extract_nuwro(new, old)
        inputs += [file_record(p, "events (nuwro_to_flat_5d.C output)") for p in new]
        inputs += [file_record(p, "parity reference (existing nuwro_flat.root)") for p in old]
        if args.nuwro_raw_glob:
            inputs += [file_record(p, "raw NuWro input to nuwro_to_flat_5d.C")
                       for p in sorted(glob.glob(args.nuwro_raw_glob))]
    else:
        files = sorted(glob.glob(os.path.join(G, "work_gibuu_arr/task*/FinalEvents.dat")))
        ev, norm, diag = extract_gibuu(files)
        inputs += [file_record(p, "events") for p in files]

    # range accounting: every in-PS event must land in the 5D grid
    rng = {}
    for a in AXES:
        v = ev[a]
        rng[a] = {"n_nonfinite": int((~np.isfinite(v)).sum()),
                  "n_below": int((v < EDGES[a][0]).sum()),
                  "n_above": int((v > EDGES[a][-1]).sum()),
                  "min": float(np.nanmin(v)), "max": float(np.nanmax(v))}
    x5, v5, nevt5, x3, xew, xew_alt = build(gen, ev, norm)
    n_in_ps = int(ev["pt"].size)
    n_in_grid = int(nevt5.sum())

    dq3W = widths("q3", "W")
    m3 = (x5 * dq3W[None, None, None]).sum(axis=(3, 4))
    mew = (x5 * widths("pt", "pz")[:, :, None, None, None]
           * np.diff(EDGES["q3"])[None, None, None, :, None]).sum(axis=(0, 1, 3))
    v3 = (v5 * (dq3W ** 2)[None, None, None]).sum(axis=(3, 4))
    ref3 = read_th(os.path.join(G, ref3d), "hXSec3D")
    refe = read_th(os.path.join(G, refew), "hXSec_eavailW")
    inputs += [file_record(os.path.join(G, ref3d), "validation reference (3D)"),
               file_record(os.path.join(G, refew), "validation reference (E_avail,W)")]
    val = {
        "recomputed_3d_vs_committed_3d": compare(x3, ref3),
        "recomputed_eavailW_vs_committed_eavailW": compare(xew, refe),
        "5d_marginal_vs_committed_3d": compare(m3, ref3, var=v3 if gen == "genie_cv" else None),
        "5d_marginal_vs_committed_eavailW": compare(mew, refe),
        "5d_marginal_vs_recomputed_3d": compare(m3, x3),
        "5d_marginal_vs_recomputed_eavailW": compare(mew, xew),
    }
    if xew_alt is not None:
        val["5d_marginal_vs_committed_eavailW_x_Nnonmec_over_Ncc"] = compare(
            mew * norm["factor_to_eavailW_band_convention"], refe)
    total5 = float((x5 * widths(*AXES)).sum())
    dV3 = widths("pt", "pz", "eavail")
    val["integrated_sigma_cm2"] = {
        "5d_grid": total5, "committed_3d": float((ref3 * dV3).sum()),
        "committed_eavailW": float((refe * widths("eavail", "W")).sum())}
    val["integrated_sigma_cm2"]["5d_stat_rel_err"] = float(
        np.sqrt((v5 * widths(*AXES) ** 2).sum()) / total5)

    code_files = [Path(__file__).resolve()] + [Path(m.__file__).resolve() for m in
                                               (u3d, u3d.u2d, g3d, gew, gibew, gib3d)]
    code_files.append(Path(sys.modules["gst_reader"].__file__).resolve())
    code_files.append(Path(sys.modules["xsec_3d"].__file__).resolve())
    macro = _HERE / "nuwro_to_flat_5d.C"
    if gen == "nuwro" and macro.exists():
        code_files.append(macro)
    meta = {
        "schema": "gen5d/v1",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generator": gen,
        "generator_label": {"genie_cv": "GENIE 2.12.10 CV (no MEC)",
                            "genie_mec": "GENIE 2.12.10 + Valencia MEC (Default+CCMEC)",
                            "nuwro": "NuWro 21.09", "gibuu": "GiBUU 2019"}[gen],
        "quantity": "d5sigma/(dpT dp|| dEavail dq3 dW), cm^2/nucleon/(GeV/c)^2/GeV^3",
        "axes": list(AXES), "shape": list(SHAPE), "order": "C",
        "edges": {a: EDGES[a].tolist() for a in AXES},
        "phase_space": "truth muon pT in [0,4.5], p|| in [1.5,60] GeV/c (inclusive), "
                       "theta_mu < 20 deg (atan2(pT,p||)); CC only; no vertex cut "
                       "(unfold_2d_omnifold_unbinned.py:51-64)",
        "definitions": {
            "eavail": "CVUniverse::GetEAvailableTrue (CVUniverse.h:361-374): gamma +E, "
                      "pi+- +E-0.135, pi0 +E, p +E-0.93827 GeV over final-state particles",
            "q3": "PlotUtils Getq3True = calcq3(mc_Q2, Enu, Elep) = sqrt(Q2 + (Enu-Elep)^2) "
                  "(TruthFunctions.h:45-47, BaseUniverse.cxx:81-83); Q2 = -(k-k')^2 in the lab",
            "W": "existing-converter W (gen_to_xsec_eavailW.py:49-61): "
                 "sqrt(M_n^2 + 2(Enu-Emu)M_n - 4 Enu Emu sin^2(theta/2)), M_n=0.939565, "
                 "0 if W^2<=0; CVUniverse.h:396-410 uses the struck-nucleon mass instead "
                 "(see diagnostics.W_struck_nucleon_mass)",
        },
        "normalisation": norm,
        "range_accounting": rng,
        "n_in_phase_space": n_in_ps, "n_events_in_grid": n_in_grid,
        "diagnostics": diag,
        "validation": val,
        "inputs": inputs,
        "code": {"git_head_of_code_root": git_head(_REPO), "code_root": str(_REPO),
                 "files": [{"path": str(p), "sha256": sha256(p)} for p in code_files]},
        "argv": sys.argv,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    np.savez(args.out, xsec_flat=x5.reshape(-1), sumw2_flat=v5.reshape(-1),
             nevt_flat=nevt5.reshape(-1), n_events=np.int64(n_in_grid),
             **{f"edges_{a}": EDGES[a] for a in AXES},
             shape=np.asarray(SHAPE), meta_json=np.asarray(json.dumps(meta)))
    with open(os.path.splitext(args.out)[0] + ".meta.json", "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps({"generator": gen, "n_in_ps": n_in_ps, "n_in_grid": n_in_grid,
                      "range": rng, "validation": val, "normalisation": norm,
                      "diagnostics": diag}, indent=1, default=str))


if __name__ == "__main__":
    main()
