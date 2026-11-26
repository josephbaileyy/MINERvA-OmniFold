#!/usr/bin/env python3
"""OOFVC scorer (OOFVC-DECLARATION.md sections 2.2-2.4), on the laptop: the fetched units against the publication, Tier
1's committed E units and regenA3's ladder. Controls first; the readings are printed only if every control passes.

  python3 oofvc_score.py --units FETCHED/units --join FETCHED/join/join.json --rows FETCHED/join/oofvc_rows.npz \
      --tree LOCAL_DEPLOY_TREE --repo REPO > score.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import oofvc_lib as L  # noqa: E402

PUB_REL = "docs/orchestration/state/precharge-20261125/inputs/replay/release.root"
PUB_SHA = "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3"
TIER1_E = "docs/orchestration/state/ibu-chi2-20261123/tier1/units/e"
LADDER = "docs/orchestration/state/ibu-chi2-20261123/regenA3/out/ladder.json"
LADDER_SHA = "565d1f99a3bd702bb1bd7279e97a571eaa6786941b48310fba290c17ec85422a"
D_ER_TIER1 = 2.121436  # tier1/score.out, to the printed precision; C-BASE compares at 1e-6 relative
PRIMARY_K = 10
COLUMN_40_60 = 15
FIXED = ("hOFTruthDenom2D", "hDataReco2D", "hFlux_pt")
FIXED_PARAMS = ("dataPOT", "mcPOT", "potScale", "fluxIntegral_m2_per_POT", "nNucleons")


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def th2(f, name) -> np.ndarray:
    h = f.Get(name)
    return np.array([h.GetBinContent(ix, iy) for ix in range(1, h.GetNbinsX() + 1) for iy in range(1, h.GetNbinsY() + 1)])


def hist_bits(f, name) -> bytes:
    h = f.Get(name)
    return np.array([h.GetBinContent(i) for i in range(h.GetNcells())], np.float64).tobytes()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=Path, required=True)
    ap.add_argument("--join", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    a = ap.parse_args(argv)
    import ROOT
    sys.path.insert(0, str(a.tree / "2d-unfolding"))
    import compare_to_paper_fullcov as cpf
    pub_path = a.repo / PUB_REL
    out = {"schema": "oofvc-score/1", "controls": {}, "inputs": {"publication_sha256": sha256(pub_path),
                                                              "ladder_sha256": sha256(a.repo / LADDER),
                                                              "rows_sha256": sha256(a.rows),
                                                              "join_sha256": sha256(a.join)}}
    ctl = out["controls"]
    ctl["C-IN"] = {"pass": out["inputs"]["publication_sha256"] == PUB_SHA and out["inputs"]["ladder_sha256"] == LADDER_SHA}
    fp = ROOT.TFile.Open(str(pub_path))
    import contextlib
    with contextlib.redirect_stdout(sys.stderr):  # flatten_th2d prints its axis titles; stdout carries the record
        pub = cpf.flatten_th2d(fp.Get("pt_pl_cross_section"))
    cov = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
    fp.Close()
    join = json.loads(a.join.read_text())
    ctl["C-JOIN-RECORD"] = {"pass": join.get("verdict") == "PASS" and join.get("rows_sha256") == out["inputs"]["rows_sha256"]}

    # unit verdicts: ref_c2c1's done-markers (C-SIM, C-ROO, C-FILL), N's controls, the pins
    verdicts = {}
    for conv in ("off", "R"):
        for kind in ("er", "c2_central"):
            verdicts[f"{conv}/{kind}"] = json.loads((a.units / conv / f"{kind}.done").read_text())["verdict"]
        n = json.loads((a.units / conv / "c2_central.oofvc.json").read_text())["n_controls"]
        verdicts[f"{conv}/N"] = "PASS" if all(c["pass"] for c in n.values()) else "FAIL"
        meta = json.loads(str(np.load(a.units / conv / "c2_central.npz", allow_pickle=True)["meta"]))
        verdicts[f"{conv}/c2_C-ROO_ran"] = "PASS" if "C-ROO" in meta["controls"] else "FAIL"  # RooUnfold, not numpy
    pins_files = sorted(a.units.glob("pins_*.json"))
    pins = [json.loads(p.read_text()) for p in pins_files]
    covered = sorted(u for p in pins for u in p["units"])
    ctl["C-UNITS"] = {"verdicts": verdicts, "pass": all(v == "PASS" for v in verdicts.values())}
    ctl["C-PINS"] = {"files": [p.name for p in pins_files], "units": covered,
                     "pass": bool(pins) and all(p["pass"] for p in pins)
                     and covered == sorted(["off/er", "off/c2_central", "R/er", "R/c2_central"])}

    f = {c: ROOT.TFile.Open(str(a.units / c / "er.root")) for c in ("off", "R")}
    z = {c: np.load(a.units / c / "c2_central.npz", allow_pickle=True) for c in ("off", "R")}
    nz = {c: np.load(a.units / c / "n.npz", allow_pickle=True) for c in ("off", "R")}
    ks = [int(k) for k in z["off"]["ks"]]
    ax, ay = f["off"].Get("hXSec2D").GetXaxis(), f["off"].Get("hXSec2D").GetYaxis()
    pt_edges = [ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)]  # pT on X (re2_driver.make_th2d)
    pz_edges = [ay.GetBinLowEdge(i) for i in range(1, ay.GetNbins() + 2)]

    def D(x):
        return L.distance(x, pub, cov)[0]

    # C-BASE: off reproduces Tier 1's E units and regenA3's set e
    t1 = ROOT.TFile.Open(str(a.repo / TIER1_E / "er.root"))
    ref = th2(t1, "hXSec2D")
    t1.Close()
    er_off = th2(f["off"], "hXSec2D")
    m = ref != 0
    base_rel = float(np.max(np.abs(er_off[m] / ref[m] - 1))) if m.any() else 0.0
    t1c = np.load(a.repo / TIER1_E / "c2_central.npz", allow_pickle=True)
    xm = t1c["xsec"] != 0
    c2_rel = float(np.max(np.abs(z["off"]["xsec"][xm] / t1c["xsec"][xm] - 1)))
    lad = json.loads((a.repo / LADDER).read_text())["sets"]["e"]["D_IBU_every_K"]
    d_off = {K: D(z["off"]["xsec"][ks.index(K)]) for K in ks}
    lad_rel = max(abs(d_off[K] / lad[str(K)] - 1) for K in ks)
    der_off = D(er_off)
    ctl["C-BASE"] = {"er_hXSec2D_max_rel": base_rel, "c2_xsec_max_rel": c2_rel, "D_IBU_vs_regenA3_max_rel": lad_rel,
                     "D_ER": der_off, "D_ER_vs_tier1_rel": abs(der_off / D_ER_TIER1 - 1),
                     "pass": bool(base_rel <= 1e-8 and c2_rel <= 1e-8 and lad_rel <= 1e-6
                                  and np.all(er_off[~m] == 0) and abs(der_off / D_ER_TIER1 - 1) <= 1e-6)}

    # C-FIX: under R the denominator, the data, the flux and the exposures are bit for bit those of off
    fix = {k: hist_bits(f["off"], k) == hist_bits(f["R"], k) for k in FIXED}
    fix.update({k: f["off"].Get(k).GetVal() == f["R"].Get(k).GetVal() for k in FIXED_PARAMS})
    ctl["C-FIX"] = {"equal": fix, "pass": all(fix.values())}

    # C-MOVE: the background removed per reco cell equals the moved rows reconstructed in the grid, to 1e-12 of the
    # cell's production background; R's signal grows by exactly those rows
    rows = dict(np.load(a.rows))
    pot = float(join["pot_scale"])
    g = L.global_index(rows["reco_pt"], rows["reco_pz"], pt_edges, pz_edges)
    inside = L.in_rectangle(rows["reco_pt"], rows["reco_pz"], pt_edges, pz_edges)
    moved_cell = np.bincount(g[g >= 0], weights=rows["w_reco"][g >= 0] * pot, minlength=224)
    b_off, b_r = th2(f["off"], "hBkgReco2D"), th2(f["R"], "hBkgReco2D")
    dev = np.abs((b_off - b_r) - moved_cell)
    scale = np.maximum(np.abs(b_off), 1e-300)
    n_off = json.loads((a.units / "off" / "er.oofvc.json").read_text())["n_signal_rows"]
    n_r = json.loads((a.units / "R" / "er.oofvc.json").read_text())["n_signal_rows"]
    ctl["C-MOVE"] = {"max_dev_over_cell": float(np.max(dev / scale)), "appended": n_r - n_off,
                     "moved_reco_in_grid": int(inside.sum()),
                     "pass": bool(np.all(dev <= 1e-12 * scale) and n_r - n_off == int(inside.sum()))}

    out["controls_pass"] = all(c["pass"] for c in ctl.values())
    if not out["controls_pass"]:
        out["reading"] = "STOP"
        print(json.dumps(out, indent=1, default=float))
        return 8

    # operands (section 2.3) and readings (section 2.4)
    iK = ks.index(PRIMARY_K)
    ops = {"D_IBU_0": d_off[PRIMARY_K], "D_IBU_R": D(z["R"]["xsec"][iK]), "D_ER_0": der_off,
           "D_ER_R": D(th2(f["R"], "hXSec2D")), "D_IBU_N": D(nz["off"]["xsec_N"][iK]),
           "D_IBU_RN": D(nz["R"]["xsec_N"][iK])}
    r = {"r_IBU": ops["D_IBU_R"] / ops["D_IBU_0"], "r_ER": ops["D_ER_R"] / ops["D_ER_0"],
         "r_N": ops["D_IBU_N"] / ops["D_IBU_0"], "r_RN": ops["D_IBU_RN"] / ops["D_IBU_0"]}
    b = {k: L.band(v) for k, v in r.items()}
    out["operands"], out["ratios"], out["bands"] = ops, r, b
    out["statements"] = {"primary": L.primary_statement(b["r_IBU"], b["r_ER"]), "N": L.n_statement(b["r_N"]),
                         "RN_band": b["r_RN"], "E_R_under_N": "not applicable"}
    pt_full, pz_full = pt_edges, pz_edges
    out["descriptive"] = {
        "D_IBU_every_K": {c: {K: D(z[c]["xsec"][ks.index(K)]) for K in ks} for c in ("off", "R")},
        "D_IBU_N_every_K": {c: {K: D(nz[c]["xsec_N"][ks.index(K)]) for K in ks} for c in ("off", "R")},
        "column_40_60_ratio": {
            "IBU_0": L.column_ratio(z["off"]["xsec"][iK], pub, pt_full, pz_full, COLUMN_40_60),
            "IBU_R": L.column_ratio(z["R"]["xsec"][iK], pub, pt_full, pz_full, COLUMN_40_60),
            "IBU_N": L.column_ratio(nz["off"]["xsec_N"][iK], pub, pt_full, pz_full, COLUMN_40_60),
            "IBU_RN": L.column_ratio(nz["R"]["xsec_N"][iK], pub, pt_full, pz_full, COLUMN_40_60),
            "ER_0": L.column_ratio(er_off, pub, pt_full, pz_full, COLUMN_40_60),
            "ER_R": L.column_ratio(th2(f["R"], "hXSec2D"), pub, pt_full, pz_full, COLUMN_40_60)},
        "completeness_above_1": {c: {"n_cells": int((th2(f[c], "hOFCompleteness2D") > 1 + 1e-12).sum()),
                                     "max": float(th2(f[c], "hOFCompleteness2D").max())} for c in ("off", "R")},
        "classes": join["classes"]}
    out["reading"] = "READ"
    print(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
