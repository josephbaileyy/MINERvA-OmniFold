#!/usr/bin/env python3
"""MP3-B step 1: controls, gates B1-B3, and the NuWro free-proton (H) and NuWro-on-CH fine-grid 5D products
(frozen spec PLAN.md §4.3; BINDING-PHASE1-20261019 §2 and D6).

Order (each stage runs only if every earlier one passed; nothing cell-level about H is computed before B3):

  C0  card control: the .par files NuWro wrote for the two H samples differ from the frozen C12 production
      (work_nuwro_p1) and supplement (supp/nuwro) .par files in exactly {random_seed, number_of_events,
      nucleus_p, nucleus_n, nucleus_target}, with the SEEDS.txt values and the proton.txt target (1, 0, 0).
  C1  converter control: nuwro_to_flat_5d.C (the frozen gen5d copy), re-run in this job on the frozen C12 p1 and
      supplement NuWro files, reproduces the frozen flat trees branch for branch, bitwise, and nTotal.
  B1  H channel content: among CC events of both H samples no QEL/COH/MEC (dyn 0, 6, 8), and the struck nucleon
      (hitnuc) is a proton (2212) for every CC event; NuWro's own channel tables agree (events 0, sigma 0).
  B2  the frozen NuWro product rebuilt through its own code path (gen5d_flux_reweight.cmd_reweight's NuWro
      statements, then gen5d_flux_supplement.cmd_supplement's) equals gen5d_fluxfix/nuwro_cv_xsec5d.npz and
      nuwro_cv_xsec5d_full.npz bitwise (xsec_flat and sumw2_flat; nevt_flat reported).
      Also reproduced: the frozen build's sampling-model statistics for the C12 main and supplement samples
      (the statistic B3 applies), compared field by field with the frozen meta.
  B3  the flux-fix weight closure of the H supplement, i.e. the closure the frozen build recorded for the C12
      supplement (gen5d_flux_supplement.cmd_supplement): the supplement flux file equals phi_t x width on
      [50,100] bitwise, r is constant, and the sampling-model test (gen5d_flux_reweight.sampling_test, proxy
      mode, frozen pass rule p >= 1e-3 across and within bins, no event outside the generation bins) passes for
      every non-empty population. sigma proxy: PRIMARY GENIE's own H1 tot_cc graph (the target-matched
      analogue of the frozen C12 proxy); the literal C12 proxy is computed and reported, not gating.
      The same test on the H main sample is the frozen chain's own STOP rule (cmd_reweight raises on it); it is
      applied identically and also stops this study.
  BUILD  H main: sum_bin w_e r_e / N_total (r = the NuWro flux-fix weight on [0.5, 50] GeV); H supplement:
      sum_bin w_e r / N_total (r constant); full H = main + supplement (sumw2 and nevt add). NuWro's event weight
      is its flux-averaged sigma per target nucleon, so for the free-proton target the H product is per H
      nucleon (= per proton), as the C12 product is per C12 nucleon. CH per nucleon:
      x_CH = (12/13) x_C12 + (1/13) x_H, sumw2_CH = (12/13)^2 sumw2_C12 + (1/13)^2 sumw2_H, with x_C12 the frozen
      full product's own arrays.

Usage (root_6_28 env): python3 mp3b_build.py --out OUT --gen GENDIR --seeds SEEDS.txt
Exit codes: 0 all passed and products written; 2 a control (C0/C1) failed; 3 a gate (B1-B3) failed.
"""
from __future__ import annotations

import argparse
import glob
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

S5P = gfr.S5P
G = gfr.DEFAULTS["genie_dir"]
GEN5D = gfr.DEFAULTS["gen5d_dir"]
FLUXFIX = sup.OUT
FROZEN_MAIN = os.path.join(FLUXFIX, "nuwro_cv_xsec5d.npz")
FROZEN_FULL = os.path.join(FLUXFIX, "nuwro_cv_xsec5d_full.npz")
FROZEN_MAIN_PAR = os.path.join(G, "work_nuwro_p1", "nuwro_p1.root.par")
FROZEN_SUPP_PAR = os.path.join(sup.SUPP, "nuwro", "nuwro_supp.root.par")
FROZEN_P1_ROOT_FLAT = os.path.join(GEN5D, "nuwro_flat5d", "nuwro_flat5d_p1.root")
FROZEN_SUPP_FLAT = sup.SUPP_FILES["nuwro"]
FLAT_BRANCHES = ["cc", "pt", "pz", "eavail", "W", "weight", "Enu", "Q2", "q0", "q3", "dyn", "hitnuc"]
CARD_DIFF_KEYS = {"random_seed", "number_of_events", "nucleus_p", "nucleus_n", "nucleus_target"}
H_TARGET = {"nucleus_p": "1", "nucleus_n": "0", "nucleus_target": "0"}
# card variants of the director's kaskada_on check: k1 = the H card (NuWro's default kaskada_on = 1, which must
# then EQUAL the reference); k0 = the same card plus kaskada_on = 0 (C0 allows that one extra key for k0 only)
CARD_EXTRA = {"k1": (set(), {}), "k0": ({"kaskada_on"}, {"kaskada_on": "0"})}
LO_MAIN, HI_MAIN = gfr.GEN_RANGE["nuwro"]
F_C, F_H = 12.0 / 13.0, 1.0 / 13.0
QEL_COH_MEC = (0, 6, 8)            # NuWro CC dyn codes: 0 QEL, 2 RES, 4 DIS, 6 COH, 8 MEC (12 = nu-e, not CC)


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def read_seeds(path) -> dict:
    out = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = int(v.strip())
    for k in ("H_MAIN_SEED", "H_MAIN_N", "H_SUPP_SEED", "H_SUPP_N"):
        if k not in out:
            raise SystemExit(f"{path}: {k} not declared")
    return out


def read_par(path) -> dict:
    """NuWro's dump of every parameter it ran with ('key = value' per line)."""
    out = {}
    for line in Path(path).read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def card_control(par_h: str, par_ref: str, seed: int, n: int, card: str = "k1") -> dict:
    h, ref = read_par(par_h), read_par(par_ref)
    keys = set(h) | set(ref)
    diff = sorted(k for k in keys if h.get(k) != ref.get(k))
    extra_allowed, extra_want = CARD_EXTRA[card]
    allowed = CARD_DIFF_KEYS | extra_allowed
    want = {"random_seed": str(seed), "number_of_events": str(n), **H_TARGET, **extra_want}
    ok = set(diff) <= allowed and all(h.get(k) == v for k, v in want.items())
    return {"par": par_h, "par_sha256": sha256(par_h), "reference_par": par_ref, "reference_sha256": sha256(par_ref),
            "differing_keys": diff, "values_H": {k: h.get(k) for k in diff}, "values_reference": {k: ref.get(k) for k in diff},
            "card_variant": card, "allowed_differing_keys": sorted(allowed), "required_values": want,
            "rule": "every differing key is in the allowed set and the H card carries the required values",
            "pass": bool(ok)}


def flat_arrays(ROOT, path, cols=FLAT_BRANCHES):
    d = ROOT.RDataFrame("nuwro_obs", path).AsNumpy(cols)
    f = ROOT.TFile.Open(path)
    nt = float(f.Get("nTotal").GetVal())
    f.Close()
    return {k: np.asarray(v) for k, v in d.items()}, nt


def converter_control(ROOT, mine: str, frozen: str) -> dict:
    a, na = flat_arrays(ROOT, mine)
    b, nb = flat_arrays(ROOT, frozen)
    br = {k: bool(a[k].dtype == b[k].dtype and np.array_equal(a[k], b[k], equal_nan=True)) for k in FLAT_BRANCHES}
    return {"reconverted": mine, "frozen": frozen, "frozen_sha256": sha256(frozen), "n_entries": int(a["cc"].size),
            "nTotal_equal": na == nb, "branches_bitwise_equal": br, "pass": bool(na == nb and all(br.values()))}


def channel_table(path) -> dict:
    """NuWro's <output>.root.txt: dyn events ratio sigma[cm2]."""
    rows = {}
    for line in Path(path).read_text().splitlines():
        p = line.split()
        if len(p) == 4 and p[0].isdigit():
            rows[int(p[0])] = {"events": int(p[1]), "ratio": float(p[2]), "sigma_cm2": float(p[3])}
    return rows


def gate_b1(ROOT, flat: str, table: str) -> dict:
    d, nt = flat_arrays(ROOT, flat, ["cc", "dyn", "hitnuc"])
    cc = d["cc"].astype(bool)
    dyn_cc = {str(int(k)): int(v) for k, v in zip(*np.unique(d["dyn"][cc], return_counts=True))}
    dyn_all = {str(int(k)): int(v) for k, v in zip(*np.unique(d["dyn"], return_counts=True))}
    hit_cc = {str(int(k)): int(v) for k, v in zip(*np.unique(d["hitnuc"][cc], return_counts=True))}
    hit_noncc = {str(int(k)): int(v) for k, v in zip(*np.unique(d["hitnuc"][~cc], return_counts=True))}
    tab = channel_table(table)
    n_forbidden = int(np.isin(d["dyn"][cc], QEL_COH_MEC).sum())
    tab_ok = all(tab.get(c, {"events": 0, "sigma_cm2": 0.0})["events"] == 0
                 and tab.get(c, {"events": 0, "sigma_cm2": 0.0})["sigma_cm2"] == 0.0 for c in QEL_COH_MEC)
    proton_only = bool(cc.sum() > 0 and np.all(d["hitnuc"][cc] == 2212))
    return {"flat": flat, "flat_sha256": sha256(flat), "n_entries": int(cc.size), "nTotal": nt, "n_cc": int(cc.sum()),
            "dyn_counts_cc": dyn_cc, "dyn_counts_all": dyn_all, "hitnuc_counts_cc": hit_cc, "hitnuc_counts_noncc": hit_noncc,
            "n_cc_QEL_COH_MEC": n_forbidden, "nuwro_channel_table": tab, "table_QEL_COH_MEC_zero": tab_ok,
            "struck_nucleon_proton_only_cc": proton_only,
            "pass": bool(n_forbidden == 0 and tab_ok and proton_only)}


class SigmaH1(gfr.SigmaCC):
    """gfr.SigmaCC restricted to the GENIE nu_mu H1 tot_cc graph (per H nucleon): the target-matched sigma-shape
    proxy for the H sampling-model test. Only __init__ differs; integration is SigmaCC's."""

    def __init__(self, ROOT, graphs_file):  # noqa: D107  (deliberately does not call SigmaCC.__init__)
        self.f = ROOT.TFile.Open(graphs_file)
        g = None
        for k in self.f.GetListOfKeys():
            nm = k.GetName()
            if "H1" in nm and nm.startswith("nu_mu"):
                g = self.f.Get(nm).Get("tot_cc")
                break
        if not g:
            raise SystemExit(f"tot_cc for H1 not in {graphs_file}")
        self.graphs = [g]
        self.norm = 1.0
        self.knots = np.array([g.GetX()[i] for i in range(g.GetN())], float)
        self.x_max = float(self.knots.max())


def nuwro_events(ROOT, files):
    """The per-event columns cmd_reweight / cmd_supplement read, concatenated in file order."""
    cols = ["cc", "pt", "pz", "Enu", "weight", "dyn"]
    acc = {k: [] for k in cols}
    for fn in files:
        dd = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(cols)
        for k in cols:
            acc[k].append(dd[k])
    return {k: np.concatenate(v) for k, v in acc.items()}


def ps_mask(g5, d):
    """cmd_reweight's alignment selection (extract_nuwro's in-phase-space CC events)."""
    E5 = g5.EDGES
    ccm = d["cc"].astype(bool)
    PT, PZ = E5["pt"], E5["pz"]
    ptc, pzc = d["pt"][ccm], d["pz"][ccm]
    m = (np.isfinite(ptc) & np.isfinite(pzc) & (ptc >= PT[0]) & (ptc <= PT[-1])
         & (pzc >= PZ[0]) & (pzc <= PZ[-1]) & (np.arctan2(ptc, pzc) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
    return ccm, m


def aligned(ev, d, ccm, m) -> bool:
    return bool(np.array_equal(d["pt"][ccm][m], ev["pt"]) and np.array_equal(d["pz"][ccm][m], ev["pz"])
                and np.array_equal(d["weight"][ccm][m], ev["weight_raw"]))


LABELS = {"main": ("all CC events", "CC RES/DIS (dyn 2-5; E-weighted proposal + bias)",
                    "CC QEL/COH/MEC (dyn 0,1,6-9; plain proposal)"),          # cmd_reweight's labels
          "supp": ("all CC events", "CC RES/DIS (dyn 2-5)", "CC QEL/COH/MEC")}  # cmd_supplement's labels


def sampling_set(d, e_s, c_s, lo, hi, sig, label_sig, which):
    """The frozen populations (cmd_reweight / cmd_supplement); an empty population is recorded, not tested."""
    ccm = d["cc"].astype(bool)
    Ev = d["Enu"]
    dism = (d["dyn"] > 1) & (d["dyn"] < 6)
    out = []
    for lab, sel in zip(LABELS[which], (ccm, ccm & dism, ccm & ~dism)):
        if int(sel.sum()) == 0:
            out.append({"population": lab, "n_events": 0, "empty": True, "pass": True,
                        "note": "empty population (no event to test; for H this is B1's content)"})
            continue
        s = gfr.sampling_test(Ev[sel], e_s, c_s, lo, hi, sig, False, lab)
        s["sigma_proxy"] = label_sig
        s.pop("flux_bin_E_lo", None)
        s["across_bins_content_proportional"].pop("pull_per_bin", None)
        out.append(s)
    return out


def brief(s) -> dict:
    if s.get("empty"):
        return {"population": s["population"], "n_events": 0, "empty": True}
    a, w = s["across_bins_content_proportional"], s["within_bin_uniform_x_sigma"]
    return {"population": s["population"], "n_events": s["n_events"], "n_outside": s["n_outside_generation_bins"],
            "across_chi2": a["chi2"], "across_ndf": a["ndf"], "across_p": a["p"],
            "within_chi2": w["chi2"], "within_ndf": w["ndf"], "within_p": w["p"], "pass": s["pass"]}


def compare_sampling(mine: list, frozen: list) -> dict:
    rows, ok = [], len(mine) == len(frozen)
    for a, b in zip(mine, frozen):
        ba, bb = brief(a), brief(b)
        same = all(ba.get(k) == bb.get(k) for k in ("population", "n_events", "n_outside", "across_chi2", "across_ndf",
                                                      "across_p", "within_chi2", "within_ndf", "within_p", "pass"))
        rows.append({"mine": ba, "frozen": bb, "identical": bool(same)})
        ok = ok and same
    return {"rows": rows, "identical": bool(ok)}


def rebuild_c12(ROOT, g5, z):
    """The frozen NuWro product through its own statements (cmd_reweight NuWro branch, cmd_supplement NuWro
    branch, then the merge)."""
    AX, E5 = g5.AXES, g5.EDGES
    shape = tuple(g5.SHAPE)
    dV5 = g5.widths(*AX)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    rec = {}
    # ---- < 50 GeV
    new = sorted(glob.glob(os.path.join(GEN5D, "nuwro_flat5d", "nuwro_flat5d_p*.root")))
    oldf = sorted(glob.glob(os.path.join(G, "work_nuwro_p*/nuwro_flat.root")))
    flux = os.path.join(G, "flux_mefhc_numu_nuwro.root")
    e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
    ev, norm, diag = g5.extract_nuwro(new, oldf)
    d = nuwro_events(ROOT, new)
    ccm, m = ps_mask(g5, d)
    if not aligned(ev, d, ccm, m):
        raise SystemExit("C12 main: event alignment with extract_nuwro failed")
    phi_s, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, LO_MAIN, HI_MAIN)
    r_all = gfr.r_of(d["Enu"], e_s, rbin, rng)
    r_ps = r_all[ccm][m]
    N_total = float(ev["divisor"])
    x_m, v_m = gfr.build_weighted_nuwro(g5, ev, r_ps, N_total, dV5)
    n_m = g5.hist([ev[a] for a in AX], None, [E5[a] for a in AX])
    main_np, main_meta = sup.load5(FROZEN_MAIN, shape)
    full_np, full_meta = sup.load5(FROZEN_FULL, shape)
    rec["inputs"] = {"main_flats": [{"path": p, "sha256": sha256(p)} for p in new],
                     "main_flats_match_frozen_meta": [sha256(p) == i["sha256"] for p, i in
                                                      zip(new, [i for i in main_meta["inputs"] if "nuwro_flat5d_p" in i["path"]])],
                     "flux": {"path": flux, "sha256": sha256(flux)},
                     "frozen_main": {"path": FROZEN_MAIN, "sha256": sha256(FROZEN_MAIN)},
                     "frozen_full": {"path": FROZEN_FULL, "sha256": sha256(FROZEN_FULL)}}
    rec["main"] = {"xsec": gfr.compare_arrays(x_m.reshape(-1), main_np["xsec_flat"]),
                   "sumw2": gfr.compare_arrays(v_m.reshape(-1), main_np["sumw2_flat"]),
                   "nevt": gfr.compare_arrays(n_m.reshape(-1), main_np["nevt_flat"]),
                   "N_total": N_total, "N_total_frozen": main_meta["normalisation"]["N_total"],
                   "extract_parity_vs_old_flats": [all(p["branches_bitwise_equal"].values()) and p["nTotal_equal"]
                                                   for p in diag["flat_parity_vs_existing_nuwro_flat"]]}
    sigC_main = gfr.SigmaCC(ROOT, os.path.join(G, "xsec_graphs.root"), "C12")
    samp_main = sampling_set(d, e_s, c_s, LO_MAIN, HI_MAIN, sigC_main, "GENIE C12 tot_cc/12 (frozen)", "main")
    rec["sampling_main_reproduced"] = compare_sampling(samp_main, main_meta["checks"]["sampling_model"])
    # ---- 50-100 GeV supplement
    flux_rec = sup.check_flux_file(ROOT)
    e2, c2 = gfr.read_th1(ROOT, sup.FLUX_SUPP, "flux_numu")
    _, rbin2, rng2 = gfr.flux_weights(e2, c2, phi_t, Phi_t, sup.LO, sup.HI)
    r_const = float(np.sum((phi_t * np.diff(edges))[rng2]) / Phi_t)
    if not np.allclose(rbin2[rng2], r_const, rtol=1e-12, atol=0):
        raise SystemExit("supplement r is not constant")
    evs, norms, diags = g5.extract_nuwro([FROZEN_SUPP_FLAT], [FROZEN_SUPP_FLAT])
    ds = nuwro_events(ROOT, [FROZEN_SUPP_FLAT])
    fn = ROOT.TFile.Open(FROZEN_SUPP_FLAT)
    Ns = int(fn.Get("nTotal").GetVal())
    fn.Close()
    x_s, v_s = gfr.build_weighted_nuwro(g5, evs, np.full(evs["pt"].size, r_const), float(Ns), dV5)
    n_s = g5.hist([evs[a] for a in AX], None, [E5[a] for a in AX])
    x_f = main_np["xsec_flat"].reshape(shape) + x_s
    v_f = main_np["sumw2_flat"].reshape(shape) + v_s
    n_f = main_np["nevt_flat"].reshape(shape) + n_s
    rec["supplement"] = {"file": {"path": FROZEN_SUPP_FLAT, "sha256": sha256(FROZEN_SUPP_FLAT),
                                  "matches_frozen_meta": sha256(FROZEN_SUPP_FLAT) == full_meta["supplement"]["events"]["sha256"]},
                         "r_constant": r_const, "r_constant_frozen": full_meta["supplement"]["normalisation"]["r_constant"],
                         "N_total": Ns, "flux_file": flux_rec}
    rec["full"] = {"xsec": gfr.compare_arrays(x_f.reshape(-1), full_np["xsec_flat"]),
                   "sumw2": gfr.compare_arrays(v_f.reshape(-1), full_np["sumw2_flat"]),
                   "nevt": gfr.compare_arrays(n_f.reshape(-1), full_np["nevt_flat"])}
    rec["full_from_rebuilt_main"] = {"xsec": gfr.compare_arrays((x_m + x_s).reshape(-1), full_np["xsec_flat"]),
                                     "sumw2": gfr.compare_arrays((v_m + v_s).reshape(-1), full_np["sumw2_flat"])}
    sigC_supp = sup.sigma100(ROOT, "C12")
    samp_supp = sampling_set(ds, e2, c2, sup.LO, sup.HI, sigC_supp, "GENIE C12 tot_cc/12 to 100 GeV (frozen)", "supp")
    rec["sampling_supp_reproduced"] = compare_sampling(samp_supp, full_meta["supplement"]["sampling_model"])
    bw = lambda c: bool(c["bitwise_equal"])  # noqa: E731
    rec["pass"] = bool(bw(rec["main"]["xsec"]) and bw(rec["main"]["sumw2"]) and bw(rec["full"]["xsec"])
                       and bw(rec["full"]["sumw2"]) and bw(rec["full_from_rebuilt_main"]["xsec"])
                       and bw(rec["full_from_rebuilt_main"]["sumw2"]))
    rec["pass_rule"] = ("B2 PASS iff the rebuilt <50 GeV product and the full product (frozen merge operands, and "
                        "rebuilt main + rebuilt supplement) equal the frozen xsec_flat and sumw2_flat bitwise")
    arrays = {"xsec_C12_frozen": full_np["xsec_flat"], "sumw2_C12_frozen": full_np["sumw2_flat"],
              "nevt_C12_frozen": full_np["nevt_flat"], "xsec_C12_rebuilt": (x_m + x_s).reshape(-1),
              "sumw2_C12_rebuilt": (v_m + v_s).reshape(-1)}
    integ = {"weight_mean_main_cm2": float(np.mean(d["weight"])), "weight_mean_supp_cm2": float(np.mean(ds["weight"])),
             "N_total_main": N_total, "N_total_supp": Ns}
    return rec, arrays, integ, full_meta


def h_sample(ROOT, g5, z, flats, which):
    """The H sample (the completed chunks of one energy range) through the same statements as the C12 sample of
    that range: extract_nuwro over the file list sums nTotal and concatenates events, exactly as p1..p8."""
    AX, E5 = g5.AXES, g5.EDGES
    dV5 = g5.widths(*AX)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    ev, norm, diag = g5.extract_nuwro(flats, flats)
    d = nuwro_events(ROOT, flats)
    ccm, m = ps_mask(g5, d)
    if not aligned(ev, d, ccm, m):
        raise SystemExit(f"H {which}: event alignment with extract_nuwro failed")
    N_total = float(ev["divisor"])
    if which == "main":
        flux = os.path.join(G, "flux_mefhc_numu_nuwro.root")
        e_s, c_s = gfr.read_th1(ROOT, flux, "flux_numu")
        _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, LO_MAIN, HI_MAIN)
        r_all = gfr.r_of(d["Enu"], e_s, rbin, rng)
        r_ps = r_all[ccm][m]
        lo, hi = LO_MAIN, HI_MAIN
        graphs = os.path.join(G, "xsec_graphs.root")
        sig_h, sig_c = SigmaH1(ROOT, graphs), gfr.SigmaCC(ROOT, graphs, "C12")
        extra = {"n_events_E_outside_generation_range": int(np.sum((d["Enu"] < lo) | (d["Enu"] > hi))),
                 "flux": {"path": flux, "sha256": sha256(flux)}}
    else:
        flux_rec = sup.check_flux_file(ROOT)
        e_s, c_s = gfr.read_th1(ROOT, sup.FLUX_SUPP, "flux_numu")
        _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, sup.LO, sup.HI)
        r_const = float(np.sum((phi_t * np.diff(edges))[rng]) / Phi_t)
        r_is_const = bool(np.allclose(rbin[rng], r_const, rtol=1e-12, atol=0))
        r_all = np.full(d["Enu"].size, r_const)
        r_ps = np.full(ev["pt"].size, r_const)
        lo, hi = sup.LO, sup.HI
        sig_h, sig_c = SigmaH1(ROOT, sup.GRAPHS_100), sup.sigma100(ROOT, "C12")
        extra = {"flux_file": flux_rec, "r_constant": r_const, "r_is_constant": r_is_const}
    samp_h = sampling_set(d, e_s, c_s, lo, hi, sig_h, "GENIE H1 tot_cc (PRIMARY, target-matched)", which)
    samp_c = sampling_set(d, e_s, c_s, lo, hi, sig_c, "GENIE C12 tot_cc/12 (the frozen C12 proxy, literal; report only)",
                            which)
    passed = all(s["pass"] for s in samp_h) and (which == "main" or (extra["r_is_constant"]
                                                                       and extra["flux_file"]["contents_equal_phi_t_x_width_bitwise"]))
    x, v = gfr.build_weighted_nuwro(g5, ev, r_ps, N_total, dV5)
    n = g5.hist([ev[a] for a in AX], None, [E5[a] for a in AX])
    check = {"sample": which, "flats": [{"path": f, "sha256": sha256(f)} for f in flats], "N_total": N_total,
             "n_in_ps": int(ev["pt"].size),
             "energy_range_GeV": [lo, hi], "sampling_model_H1_proxy_PRIMARY": samp_h,
             "sampling_model_C12_proxy_literal": samp_c, **extra,
             "extract_diagnostics": {k: v_ for k, v_ in diag.items() if k != "flat_parity_vs_existing_nuwro_flat"},
             "weight_unique": int(np.unique(d["weight"]).size), "weight_mean_cm2": float(np.mean(d["weight"])),
             "pass": bool(passed)}
    return check, (x, v, n)


def read_chunks(path) -> list:
    """SEEDS-chunked.txt: CHUNK <sample> <i> <N> <primary> <alt1> <alt2>."""
    out = []
    for line in Path(path).read_text().splitlines():
        p = line.split()
        if p and p[0] == "CHUNK":
            out.append({"sample": p[1], "i": p[2], "N": int(p[3]), "seeds": [int(x) for x in p[4:7]]})
    if not out:
        raise SystemExit(f"{path}: no CHUNK declaration")
    return out


def abort_info(attempt_dir: Path) -> dict:
    """An aborted attempt: NuWro's last progress line, its assertion and print, and its planned channel counts."""
    txt = (attempt_dir / "stderr_time.txt").read_text(errors="replace").replace("\r", "\n").splitlines()
    prog = [ln.strip() for ln in txt if "events ready" in ln and "test events" not in ln]
    last = prog[-1] if prog else None
    phase_dyn, pct = None, None
    if last:
        import re
        mm = re.search(r"([0-9.]+) % of dyn\[(\d+)\]", last)
        if mm:
            pct, phase_dyn = float(mm.group(1)), int(mm.group(2))
    planned = channel_table(attempt_dir / "nuwro.root.txt") if (attempt_dir / "nuwro.root.txt").exists() else {}
    dis_planned = planned.get(4, {}).get("events", 0)
    if phase_dyn is None:
        dis_done = 0.0
    elif phase_dyn < 4:
        dis_done = 0.0
    elif phase_dyn == 4:
        dis_done = pct / 100.0 * dis_planned
    else:
        dis_done = float(dis_planned)
    return {"last_progress": last, "phase_dyn": phase_dyn, "phase_percent": pct, "planned_channel_events": planned,
            "dis_events_processed_approx": dis_done,
            "messages": [ln.strip() for ln in txt if ("Assertion" in ln or ln.startswith("E=") or "signal" in ln
                                                      or "rror" in ln)][:10]}


def chunk_accounting(ROOT, gen: Path, chunks: list) -> dict:
    """Per chunk: attempts (seed, rc), the attempt kept, events, DIS fraction; per sample: the estimated excluded
    fraction = aborts / (DIS events in completed chunks + DIS events processed before each abort), a stated
    approximation (one event per abort; the progress line gives the processed count to 0.1 %)."""
    rows, per = [], {}
    for c in chunks:
        C = gen / c["sample"] / f"c{c['i']}"
        att = []
        for line in (C / "attempts.tsv").read_text().splitlines() if (C / "attempts.tsv").exists() else []:
            k, seed, rc = line.split("\t")
            att.append({"attempt": int(k), "seed": int(seed), "nuwro_rc": int(rc)})
        result = (C / "RESULT").read_text().split() if (C / "RESULT").exists() else ["missing"]
        row = {"sample": c["sample"], "chunk": c["i"], "N_declared": c["N"], "declared_seeds": c["seeds"],
               "attempts": att, "result": result[0], "aborts": []}
        for a in att:
            if a["nuwro_rc"] != 0:
                row["aborts"].append({"attempt": a["attempt"], "seed": a["seed"], "rc": a["nuwro_rc"],
                                      **abort_info(C / f"a{a['attempt']}")})
            if a["seed"] != c["seeds"][a["attempt"]]:
                raise SystemExit(f"{C}: attempt {a['attempt']} ran seed {a['seed']}, declared {c['seeds'][a['attempt']]}")
        if result[0] == "ok":
            k = int(result[1])
            W = C / f"a{k}"
            flat = str(W / "flat5d.root")
            d, nt = flat_arrays(ROOT, flat, ["cc", "dyn"])
            row.update(kept_attempt=k, kept_seed=int(result[2]), alternate_used=k > 0, flat=flat, nTotal=nt,
                       n_cc=int(d["cc"].sum()), n_dis=int(np.sum(d["dyn"] == 4)),
                       dis_fraction=float(np.mean(d["dyn"] == 4)), attempt_dir=str(W))
        rows.append(row)
    for smp in sorted({c["sample"] for c in chunks}):
        rs = [r for r in rows if r["sample"] == smp]
        n_ab = sum(len(r["aborts"]) for r in rs)
        dis_ok = sum(r.get("n_dis", 0) for r in rs)
        dis_ab = sum(x["dis_events_processed_approx"] for r in rs for x in r["aborts"])
        exc = n_ab / (dis_ok + dis_ab) if (dis_ok + dis_ab) > 0 else None
        per[smp] = {"chunks_declared": len(rs), "chunks_completed": sum(r["result"] == "ok" for r in rs),
                    "chunks_dropped": [r["chunk"] for r in rs if r["result"] == "dropped"],
                    "chunks_other": [(r["chunk"], r["result"]) for r in rs if r["result"] not in ("ok", "dropped")],
                    "alternates_used": [(r["chunk"], r.get("kept_seed")) for r in rs if r.get("alternate_used")],
                    "aborts": n_ab, "events_in_completed_chunks": sum(r.get("nTotal", 0) for r in rs),
                    "dis_events_completed": dis_ok, "dis_events_processed_in_aborted_attempts_approx": dis_ab,
                    "excluded_fraction_aborts_per_dis_event_approx": exc,
                    "excluded_fraction_above_1e-4": (exc is not None and exc > 1e-4),
                    "note": "approximation: each abort removes one DIS event configuration; the denominator counts DIS "
                            "events generated in completed chunks plus those processed before each abort (progress %)"}
    return {"chunks": rows, "per_sample": per}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--gen", type=Path, required=True)
    ap.add_argument("--seeds", type=Path, required=True)
    ap.add_argument("--card", choices=sorted(CARD_EXTRA), default="k1")
    ap.add_argument("--parity-dir", type=Path, default=None, help="C1 re-converted flats (default GEN/parity)")
    a = ap.parse_args(argv)
    parity = a.parity_dir if a.parity_dir is not None else a.gen / "parity"
    t0 = time.time()
    a.out.mkdir(parents=True, exist_ok=False)
    ROOT = gfr.import_root()
    g5 = gfr.load_g5(gfr.DEFAULTS["gen5d_tree"])
    for mod in (gfr, sup):
        if Path(mod.__file__).resolve().parent != HERE:
            raise SystemExit(f"{mod.__name__} imported from {mod.__file__}, not from {HERE}")
    res = {"schema": "mp3b-build/2 (chunked)", "argv": sys.argv, "environment": gfr.environment(), "code": {}, "stages": {}}
    for mm in [sys.modules[__name__], gfr, sup, g5, g5.u3d, g5.u3d.u2d, sys.modules["gst_reader"], sys.modules["xsec_3d"]]:
        p = Path(mm.__file__).resolve()
        res["code"][mm.__name__] = {"file": str(p), "sha256": sha256(p)}
    chunks = read_chunks(a.seeds)
    res["seeds"] = {"file": str(a.seeds), "sha256": sha256(a.seeds), "chunks": chunks}
    res["card_variant"] = a.card
    out_json = a.out / "mp3b_build.json"

    def finish(code: int, msg: str) -> int:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        res.update(verdict=msg, exit_code=code, cpu_s=ru.ru_utime + ru.ru_stime, maxrss_kb=ru.ru_maxrss,
                   wall_s=time.time() - t0)
        out_json.write_text(json.dumps(res, indent=1, default=float) + "\n")
        print(msg, flush=True)
        return code

    # ---- chunk accounting (generation outcome; no physics read)
    acc = chunk_accounting(ROOT, a.gen, chunks)
    res["chunk_accounting"] = acc
    print("CHUNKS", json.dumps(acc["per_sample"], default=float), flush=True)
    done = {smp: [r for r in acc["chunks"] if r["sample"] == smp and r["result"] == "ok"] for smp in ("H_main", "H_supp")}
    if acc["per_sample"].get("H_main", {}).get("chunks_other") or acc["per_sample"].get("H_supp", {}).get("chunks_other"):
        return finish(2, "STOP: a chunk ended neither completed nor dropped")
    if not done["H_main"] or not done["H_supp"]:
        return finish(2, "STOP: a sample has no completed chunk")
    flats_m = [r["flat"] for r in done["H_main"]]
    flats_s = [r["flat"] for r in done["H_supp"]]

    # ---- C0 on EVERY attempt's .par dump (completed and aborted), then C1
    refs = {"H_main": FROZEN_MAIN_PAR, "H_supp": FROZEN_SUPP_PAR}
    c0 = {}
    for r in acc["chunks"]:
        for at in r["attempts"]:
            par = a.gen / r["sample"] / f"c{r['chunk']}" / f"a{at['attempt']}" / "nuwro.root.par"
            c0[f"{r['sample']}/c{r['chunk']}/a{at['attempt']}"] = card_control(str(par), refs[r["sample"]], at["seed"],
                                                                                r["N_declared"], a.card)
    c0_pass = all(v["pass"] for v in c0.values())
    c0 = {"per_attempt": c0, "n_cards": len(c0), "pass": c0_pass,
          "differing_key_sets": sorted({tuple(v["differing_keys"]) for v in c0.values()})}
    res["stages"]["C0_card"] = c0
    print("C0", json.dumps({"n_cards": c0["n_cards"], "differing_key_sets": c0["differing_key_sets"], "pass": c0_pass}), flush=True)
    c1 = {"C12_p1": converter_control(ROOT, str(parity / "flat5d_C12_p1.root"), FROZEN_P1_ROOT_FLAT),
          "C12_supp": converter_control(ROOT, str(parity / "flat5d_C12_supp.root"), FROZEN_SUPP_FLAT)}
    c1["pass"] = all(v["pass"] for v in c1.values())
    res["stages"]["C1_converter"] = c1
    print("C1", json.dumps({k: v["pass"] for k, v in c1.items() if k != "pass"}), flush=True)
    if not (c0["pass"] and c1["pass"]):
        return finish(2, "STOP: control C0/C1 failed; no gate evaluated")

    # ---- B1 over every completed chunk
    b1 = {}
    for smp in ("H_main", "H_supp"):
        per = {r["chunk"]: gate_b1(ROOT, r["flat"], str(Path(r["attempt_dir"]) / "nuwro.root.txt")) for r in done[smp]}
        agg = {}
        for key in ("dyn_counts_cc", "hitnuc_counts_cc"):
            tot = {}
            for v in per.values():
                for kk, nn in v[key].items():
                    tot[kk] = tot.get(kk, 0) + nn
            agg[key] = tot
        b1[smp] = {"per_chunk": per, **agg, "n_cc_QEL_COH_MEC": sum(v["n_cc_QEL_COH_MEC"] for v in per.values()),
                   "pass": all(v["pass"] for v in per.values())}
    b1["pass"] = all(v["pass"] for k, v in b1.items() if k != "pass")
    res["stages"]["B1"] = b1
    print("B1", json.dumps({k: (v["dyn_counts_cc"], v["hitnuc_counts_cc"], v["pass"]) for k, v in b1.items() if k != "pass"}), flush=True)
    if not b1["pass"]:
        return finish(3, "STOP: gate B1 failed; no CH prediction")

    # ---- B2
    z, _, _ = gfr.load_phi_t(FLUXFIX)
    b2, c12, integ_c, full_meta = rebuild_c12(ROOT, g5, z)
    res["stages"]["B2"] = b2
    print("B2", json.dumps({"main": b2["main"]["xsec"], "full": b2["full"]["xsec"], "pass": b2["pass"],
                            "sampling_reproduced": [b2["sampling_main_reproduced"]["identical"],
                                                    b2["sampling_supp_reproduced"]["identical"]]}), flush=True)
    if not b2["pass"]:
        return finish(3, "STOP: gate B2 failed; no CH prediction")

    # ---- B3 (and the main sample's chain STOP rule); the H arrays are built here but not read before the verdict
    chk_s, arr_s = h_sample(ROOT, g5, z, flats_s, "supp")
    chk_m, arr_m = h_sample(ROOT, g5, z, flats_m, "main")
    frozen_supp = [brief(s) for s in full_meta["supplement"]["sampling_model"]]
    b3 = {"supplement": chk_s, "main_chain_stop_rule": chk_m,
          "frozen_C12_supplement_closure": {"sampling_model": frozen_supp,
                                            "r_constant": full_meta["supplement"]["normalisation"]["r_constant"],
                                            "flux_file_bitwise": full_meta["supplement"]["flux"]["contents_equal_phi_t_x_width_bitwise"]},
          "frozen_C12_statistic_reproduced_in_this_job": b2["sampling_supp_reproduced"]["identical"],
          "pass_rule": ("B3 PASS iff the H supplement meets the closure the frozen C12 supplement met: flux file = phi_t x "
                        "width bitwise, r constant, and every non-empty sampling-model population passes p >= 1e-3 "
                        "(across and within) with no event outside the generation bins (sigma proxy: GENIE H1 graph, "
                        "PRIMARY). The H main sample's same test is the chain's own STOP rule and also stops the study.")}
    b3["pass"] = bool(chk_s["pass"] and chk_m["pass"])
    res["stages"]["B3"] = b3
    print("B3", json.dumps({"supp": [brief(s) for s in chk_s["sampling_model_H1_proxy_PRIMARY"]],
                            "main": [brief(s) for s in chk_m["sampling_model_H1_proxy_PRIMARY"]],
                            "pass": b3["pass"]}, default=float), flush=True)
    if not b3["pass"]:
        return finish(3, "STOP: gate B3 failed; no CH prediction")

    # ---- the H and CH fine products
    x_h = (arr_m[0] + arr_s[0]).reshape(-1)
    v_h = (arr_m[1] + arr_s[1]).reshape(-1)
    n_h = (arr_m[2] + arr_s[2]).reshape(-1)
    x_ch = F_C * c12["xsec_C12_frozen"] + F_H * x_h
    v_ch = F_C ** 2 * c12["sumw2_C12_frozen"] + F_H ** 2 * v_h
    n_ch = c12["nevt_C12_frozen"] + n_h
    shape = tuple(g5.SHAPE)
    vol = g5.widths(*g5.AXES).reshape(-1)
    np.savez_compressed(a.out / "mp3b_fine_nuwro.npz", **c12, xsec_H=x_h, sumw2_H=v_h, nevt_H=n_h,
                        xsec_H_main=arr_m[0].reshape(-1), sumw2_H_main=arr_m[1].reshape(-1),
                        xsec_H_supp=arr_s[0].reshape(-1), sumw2_H_supp=arr_s[1].reshape(-1),
                        xsec_CH=x_ch, sumw2_CH=v_ch, nevt_CH=n_ch)
    common = {"axes": list(g5.AXES), "shape": list(shape), "order": "C", "edges": {ax: g5.EDGES[ax].tolist() for ax in g5.AXES},
              "phase_space": full_meta["phase_space"], "definitions": full_meta["definitions"],
              "code": res["code"], "seeds": res["seeds"], "created_by": "measurement-paper/phase1/mp3b/mp3b_build.py"}
    for name, x, v, n, extra in (
            ("nuwro_H_xsec5d_full", x_h, v_h, n_h,
             {"generator": "nuwro_H", "card_variant": a.card, "quantity": "dsigma per H nucleon (free proton), NuWro 21.09.1 e20:debug",
              "composition": "H main (0.5-50 GeV, flux-fix r(E)) + H 50-100 GeV supplement (constant r); sumw2, nevt add",
              "normalisation": {"convention": "sum_bin w_e r_e / N_total per sample (gen5d_flux_reweight / "
                                              "gen5d_flux_supplement NuWro convention); w_e = NuWro flux-averaged sigma "
                                              "per target nucleon = per proton for nucleus_p=1, nucleus_n=0",
                                "main": {"N_total": chk_m["N_total"], "weight_mean_cm2": chk_m["weight_mean_cm2"]},
                                "supp": {"N_total": chk_s["N_total"], "weight_mean_cm2": chk_s["weight_mean_cm2"],
                                         "r_constant": chk_s["r_constant"]}}}),
            ("nuwro_CH_xsec5d_full", x_ch, v_ch, n_ch,
             {"generator": "nuwro_CH", "quantity": "dsigma per CH nucleon = (12/13) C12 + (1/13) H",
              "composition": f"(12/13) x {FROZEN_FULL} (frozen arrays) + (1/13) x nuwro_H_xsec5d_full; "
                             "sumw2 = (12/13)^2 sumw2_C12 + (1/13)^2 sumw2_H; nevt = raw counts added"})):
        meta = {**common, **extra}
        np.savez(a.out / f"{name}.npz", xsec_flat=x, sumw2_flat=v, nevt_flat=n, n_events=np.int64(n.sum()),
                 **{f"edges_{ax}": g5.EDGES[ax] for ax in g5.AXES}, shape=np.asarray(shape), meta_json=np.asarray(json.dumps(meta)))
    sig_h, sig_c = float(x_h @ vol), float(c12["xsec_C12_frozen"] @ vol)
    res["integrated_after_gates"] = {
        "sigma_in_grid_H_per_nucleon_cm2": sig_h, "sigma_in_grid_C12_per_nucleon_cm2": sig_c,
        "sigma_in_grid_CH_per_nucleon_cm2": float(x_ch @ vol), "f_H_in_grid": F_H * sig_h / float(x_ch @ vol),
        "H_over_C12_per_nucleon_in_grid": sig_h / sig_c,
        "weight_mean_H_main_cm2": chk_m["weight_mean_cm2"], "weight_mean_C12_main_cm2": integ_c["weight_mean_main_cm2"],
        "flux_avg_sigma_ratio_H_over_C12_main_sampled_spectrum": chk_m["weight_mean_cm2"] / integ_c["weight_mean_main_cm2"],
        "weight_mean_H_supp_cm2": chk_s["weight_mean_cm2"], "weight_mean_C12_supp_cm2": integ_c["weight_mean_supp_cm2"],
        "n_in_grid": {"H_main": int(arr_m[2].sum()), "H_supp": int(arr_s[2].sum()), "C12_full": int(c12["nevt_C12_frozen"].sum())}}
    res["products"] = {p: {"path": str(a.out / p), "sha256": sha256(a.out / p)} for p in
                       ("mp3b_fine_nuwro.npz", "nuwro_H_xsec5d_full.npz", "nuwro_CH_xsec5d_full.npz")}
    return finish(0, "GATES_B1_B3_PASS; H and CH fine products written")


if __name__ == "__main__":
    raise SystemExit(main())
