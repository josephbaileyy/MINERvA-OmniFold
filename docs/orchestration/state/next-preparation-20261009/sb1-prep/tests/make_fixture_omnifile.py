"""Write a small synthetic omnifile in the universe file's schema, for the SB1 equality tests.

The schema follows the real ``runEventLoopOmniFold_MEFHC_universes_full.root`` as listed on a
Perlmutter login node on 2026-10-10 (``operands/universe_branches.json``): the same four trees,
the same branch names and types, CV branches, decoys the 2D loaders must not read (``*_eavail``,
``*_q3``, ``*_W``, ``Int_t`` truth counters, background identity columns, the data tree's extra
observables), and three universes:

* ``Flux_0`` and ``GEANT_Neutron_0`` -- VERTICAL: weight branches only;
* ``Muon_Energy_MINOS_0`` -- LATERAL: weights plus shifted kinematics on every MC tree, named as
  the real file names them (``pT_truth_``/``pz_truth_`` on ``mc_truth_denom``, ``MC_``/``MC_pz_``
  and ``sim_``/``sim_pz_`` on ``mc_signal_reco``, ``sim_background_``/``sim_background_pz_`` on
  ``mc_background``), with ``q3``/``W`` shifted decoys.

Unlike the real file, where the lateral TRUTH kinematics equal CV (``operands/lateral_probe.json``),
every lateral branch here differs from its CV counterpart, so reading the wrong one changes bytes.
About 1 % of rows sit on every boundary a loader tests: non-finite values, ``-0.0``, weights at and
beyond ``[0, 1e4)`` (``[0, 1e6)`` for the background), negative weights, the analysis rectangle's
edges, +-4 ulps around the 20-degree truth cut, ``|x| > 1e3`` for the data guard, and ``UChar_t``
pass flags 0, 1 and 2. Nothing is trained or fitted.

    python3.13 make_fixture_omnifile.py OUT.root [--rows N] [--extra K] [--seed S]
"""

import argparse
import json
import math
import os
import sys

import numpy as np

PT_LO, PT_HI, PZ_LO, PZ_HI = 0.0, 4.5, 1.5, 60.0
TAN20 = math.tan(math.radians(20.0))
VERTICAL = ("Flux_0", "GEANT_Neutron_0")
LATERAL = ("Muon_Energy_MINOS_0",)
SPECIAL = [np.nan, np.inf, -np.inf, -0.0, 0.0, 1e4, np.nextafter(1e4, 0), np.nextafter(1e4, 2e4),
           1e6, np.nextafter(1e6, 0), -1e-300, -1.0, PT_LO, PT_HI, PZ_LO, PZ_HI,
           np.nextafter(PT_HI, 10), np.nextafter(PZ_LO, 0), 1e3, np.nextafter(1e3, 2e3), -1e3]


def _boundary(rng, cols, names, every):
    n = next(iter(cols.values())).size
    for j, name in enumerate(names):
        idx = np.arange(j, n, every)
        cols[name][idx] = np.resize(np.array(SPECIAL), idx.size)


def _kin(rng, n):
    pz = rng.gamma(3.0, 2.0, n) + 1.0
    pt = rng.exponential(0.45, n)
    k = max(1, n // 50)                                  # rows within 4 ulps of the 20-degree cut
    edge = pz[:k] * TAN20
    pt[:k] = edge + (np.arange(k) % 9 - 4) * np.spacing(edge)
    return pt, pz


def _pass(rng, n, p=0.62):
    flag = (rng.uniform(size=n) < p).astype(np.uint8)
    flag[::97] = 2                                       # the driver tests != 0
    return flag


def _shift(rng, x, scale):
    return x * (1.0 + scale * rng.standard_normal(x.size))


def signal_columns(rng, n, extra):
    pt, pz = _kin(rng, n)
    passed = _pass(rng, n)
    sim = np.where(passed > 0, _shift(rng, pt, 0.05), -9999.0)
    sim_pz = np.where(passed > 0, _shift(rng, pz, 0.05), -9999.0)
    c = {"sim": sim, "sim_pz": sim_pz, "sim_eavail": rng.uniform(0, 2, n),
         "sim_q3": rng.uniform(0, 2, n), "sim_W": rng.uniform(0.9, 3, n), "sim_pass": passed,
         "w_reco": rng.lognormal(0, 0.3, n), "MC": pt, "MC_pz": pz,
         "MC_eavail": rng.uniform(0, 2, n), "MC_q3": rng.uniform(0, 2, n),
         "MC_W": rng.uniform(0.9, 3, n), "MC_nproton": rng.integers(0, 5, n).astype(np.int32),
         "MC_npip": rng.integers(0, 3, n).astype(np.int32), "MC_hadangle": rng.uniform(0, 3, n),
         "w_truth": rng.lognormal(0, 0.3, n)}
    _boundary(rng, c, ("MC", "MC_pz", "sim", "sim_pz", "w_truth", "w_reco"), 89)
    for u in VERTICAL + LATERAL:
        c[f"w_truth_{u}"] = _shift(rng, c["w_truth"], 0.05)
        c[f"w_reco_{u}"] = _shift(rng, c["w_reco"], 0.05)
    for u in LATERAL:
        for src in ("MC", "MC_pz", "sim", "sim_pz"):
            c[f"{src}_{u}"] = _shift(rng, c[src], 0.01)
        for src in ("MC_q3", "MC_W", "sim_q3", "sim_W"):
            c[f"{src}_{u}"] = _shift(rng, c[src], 0.01)
        _boundary(rng, c, (f"MC_{u}", f"sim_pz_{u}", f"w_reco_{u}"), 101)
    for k in range(extra):
        c[f"w_truth_Pad_{k}"] = 1.0 + 0.05 * rng.standard_normal(n)
    return c


def truth_columns(rng, n, extra):
    pt, pz = _kin(rng, n)
    c = {"MC": pt, "MC_pz": pz, "MC_eavail": rng.uniform(0, 2, n), "MC_q3": rng.uniform(0, 2, n),
         "MC_W": rng.uniform(0.9, 3, n), "MC_nproton": rng.integers(0, 5, n).astype(np.int32),
         "MC_npip": rng.integers(0, 3, n).astype(np.int32), "MC_hadangle": rng.uniform(0, 3, n),
         "w_truth": rng.lognormal(0, 0.3, n)}
    _boundary(rng, c, ("MC", "MC_pz", "w_truth"), 83)
    for u in VERTICAL + LATERAL:
        c[f"w_truth_{u}"] = _shift(rng, c["w_truth"], 0.05)
    for u in LATERAL:
        c[f"pT_truth_{u}"] = _shift(rng, c["MC"], 0.01)
        c[f"pz_truth_{u}"] = _shift(rng, c["MC_pz"], 0.01)
        c[f"q3_truth_{u}"] = _shift(rng, c["MC_q3"], 0.01)
        c[f"W_truth_{u}"] = _shift(rng, c["MC_W"], 0.01)
        _boundary(rng, c, (f"pT_truth_{u}", f"w_truth_{u}"), 103)
    for k in range(extra):
        c[f"w_truth_Pad_{k}"] = 1.0 + 0.05 * rng.standard_normal(n)
    return c


def background_columns(rng, n, extra):
    pt, pz = _kin(rng, n)
    c = {"sim_background": pt, "sim_background_pz": pz, "sim_background_eavail": rng.uniform(0, 2, n),
         "sim_background_q3": rng.uniform(0, 2, n), "sim_background_W": rng.uniform(0.9, 3, n),
         "sim_background_pass": _pass(rng, n, 0.9), "w_bkg": rng.lognormal(-1.5, 0.3, n),
         "bkg_nuPDG": np.full(n, 14, np.int32), "bkg_current": rng.integers(1, 3, n).astype(np.int32),
         "bkg_inttype": rng.integers(1, 10, n).astype(np.int32), "bkg_vtx_x": rng.normal(0, 400, n),
         "bkg_vtx_y": rng.normal(0, 400, n), "bkg_vtx_z": rng.uniform(5980, 8422, n)}
    _boundary(rng, c, ("sim_background", "sim_background_pz", "w_bkg"), 31)
    for u in VERTICAL + LATERAL:
        c[f"w_bkg_{u}"] = _shift(rng, c["w_bkg"], 0.05)
    for u in LATERAL:
        for src in ("sim_background", "sim_background_pz", "sim_background_q3", "sim_background_W"):
            c[f"{src}_{u}"] = _shift(rng, c[src], 0.01)
        _boundary(rng, c, (f"sim_background_{u}", f"w_bkg_{u}"), 37)
    for k in range(extra):
        c[f"w_bkg_Pad_{k}"] = 1.0 + 0.05 * rng.standard_normal(n)
    return c


def data_columns(rng, n):
    pt, pz = _kin(rng, n)
    c = {"measured": pt, "measured_pz": pz, "measured_eavail": rng.uniform(0, 2, n),
         "measured_q3": rng.uniform(0, 2, n), "measured_W": rng.uniform(0.9, 3, n),
         "measured_pass": _pass(rng, n, 0.95)}
    _boundary(rng, c, ("measured", "measured_pz"), 29)
    return c


def _snapshot(ROOT, path, tree, cols, mode):
    # FromNumpy has no uint8 column type: UChar_t columns travel as int32 and are narrowed.
    names = list(cols)
    data = {}
    defines = []
    for k, v in cols.items():
        if v.dtype == np.uint8:
            data[f"{k}__i32"] = v.astype(np.int32)
            defines.append(k)
        else:
            data[k] = np.ascontiguousarray(v)
    df = ROOT.RDF.FromNumpy(data)
    for k in defines:
        df = df.Define(k, f"(UChar_t){k}__i32")
    opts = ROOT.RDF.RSnapshotOptions()
    opts.fMode = mode
    opts.fCompressionAlgorithm = ROOT.RCompressionSetting.EAlgorithm.kZLIB
    opts.fCompressionLevel = 1
    df.Snapshot(tree, path, names, opts)


def write_fixture(path, rows=20000, extra=24, seed=20261010):
    import ROOT
    rng = np.random.default_rng(seed)
    if os.path.exists(path):
        os.remove(path)
    _snapshot(ROOT, path, "mc_truth_denom", truth_columns(rng, rows, extra), "RECREATE")
    _snapshot(ROOT, path, "mc_signal_reco", signal_columns(rng, rows, extra), "UPDATE")
    _snapshot(ROOT, path, "mc_background", background_columns(rng, max(500, rows // 40), extra),
              "UPDATE")
    _snapshot(ROOT, path, "data", data_columns(rng, max(1000, rows // 8)), "UPDATE")
    f = ROOT.TFile(path, "UPDATE")
    for name, val in (("dataPOTUsed", 1.0e20), ("mcPOTUsed", 4.708e20),
                      ("hasTruthOnlyMisses", 1.0), ("nTruthOnlyMisses", 0.0)):
        ROOT.TParameter("double")(name, val).Write()
    f.Close()
    return {"path": path, "rows": rows, "extra_per_tree": extra, "seed": seed,
            "bytes": os.path.getsize(path), "root": ROOT.gROOT.GetVersion()}


def write_flux(path, n_bins=14):
    import ROOT
    from array import array
    edges = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
    f = ROOT.TFile(path, "RECREATE")
    h = ROOT.TH1D("pTmu_reweightedflux_integrated", "", n_bins, array("d", edges))
    for i in range(1, n_bins + 1):
        h.SetBinContent(i, 1.0e-8 * i)
    h.Write()
    f.Close()
    return path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--rows", type=int, default=20000)
    ap.add_argument("--extra", type=int, default=24)
    ap.add_argument("--seed", type=int, default=20261010)
    a = ap.parse_args(argv)
    json.dump(write_fixture(a.out, a.rows, a.extra, a.seed), sys.stdout)
    print()


if __name__ == "__main__":
    main()
