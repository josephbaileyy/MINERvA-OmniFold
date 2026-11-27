#!/usr/bin/env python3
"""OOFVC join (OOFVC-DECLARATION.md sections 1.2 and 2.2, route A): the production omnifile's mc_background and
mc_signal_reco against the 12 playlists' oofvc_dump outputs, on exact values. Writes the driver's --oofvc-rows file
and a record; any refused control is a STOP (exit 8) and writes no rows.

  python3 oofvc_join.py --omnifile CV.root --dump-dir DIR --split split.json --out OUTDIR

Controls (each a STOP):
  C-ROUTE  every dump row is routed to exactly one tree: to_bkg == not to_sig (reco-mode and truth-mode routings agree)
  C-JOIN   mc_background (every entry) one-to-one with the dump's to_bkg rows on (reco pT, reco p||, w): the
           director's tie rule (exact_join) and bound (0.1% of the moved weight)
  C-SIGW   mc_signal_reco's selected rows (sim_pass) one-to-one with the dump's to_sig rows that the signal loop keeps
           (not dup_sig) on (sim, sim_pz, w_reco), the same rule and bound (0.1% of the joined weight); then on every
           pair MC, MC_pz and w_truth bit-for-bit equal to the dump's true_pt, true_pz and w_truth
  C-LAB    the joined background's oflow categories (FAKE_PS, FAKE_VTX, OTHER) on the OLD 14 x 16 reco grid, POT-scaled,
           equal oflow/split.json cell by cell (relative 1e-9; absolute 1e-9 where split.json has 0)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oofvc_lib as L  # noqa: E402

RC_STOP = 8
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
# the grid's outer edges (both p_T sets share them) and the OLD edges that oflow binned on
PT_OLD = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]
DUMP_FLOAT = ("reco_pt", "reco_pz", "w_reco", "true_pt", "true_pz", "w_truth", "theta_true", "vtx_x", "vtx_y", "vtx_z")
DUMP_INT = ("entry", "mc_run", "mc_subrun", "mc_nthEvtInFile", "nu_pdg", "current", "to_bkg", "to_sig", "dup_sig",
            "fid")
DUMP_FLAGS = ("to_bkg", "to_sig", "dup_sig", "fid")   # UChar_t in oofvc_dump.cpp
BKG_FLAGS = ("sim_background_pass",)                  # UChar_t in the event loop's mc_background
SIG_FLAGS = ("sim_pass",)                             # UChar_t in mc_signal_reco
LAB_RTOL = 1e-9


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_tree(path: Path, tree: str, cols, flags=()) -> dict:
    """The columns as numbers (oofvc_lib.normalize: ROOT 6.28 returns UChar_t as one-character strings), the named
    flags refused unless 0 or 1."""
    import ROOT
    return L.normalize({k: np.asarray(v) for k, v in ROOT.RDataFrame(tree, str(path)).AsNumpy(list(cols)).items()},
                       flags)


def read_dumps(dump_dir: Path) -> tuple[dict, dict]:
    parts, shas = [], {}
    for pl in PLAYLISTS:
        p = dump_dir / f"{pl}.root"
        shas[pl] = sha256(p)
        d = read_tree(p, "rows", DUMP_FLOAT + DUMP_INT, DUMP_FLAGS)
        d["playlist"] = np.full(d["entry"].size, PLAYLISTS.index(pl), np.int64)
        parts.append(d)
    return {k: np.concatenate([d[k] for d in parts]) for k in parts[0]}, shas


def oflow_fid(x, y, z) -> np.ndarray:
    """oflow's fiducial test, as remote3.sh computes it (the same numpy operations), so C-LAB compares like with like.
    The descriptive class split uses the dump's own flag (MAT's truth ZRange and Apothem)."""
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    ap = 850.0; side = ap * 2 / np.sqrt(3)
    return (np.abs(x) <= ap) & ((np.abs(y) < side / 2) | (np.abs(y) < side - np.abs(x) * (side / 2) / ap)) & (z >= 5980) & (z <= 8422)


def categories(d: dict, rows: np.ndarray, pot_scale: float) -> dict:
    """oflow's categories (oflow/remote3.sh) of the given dump rows, on the OLD reco grid, POT-scaled."""
    pt, pz, w = d["reco_pt"][rows], d["reco_pz"][rows], d["w_reco"][rows]
    ok = np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w) & (w >= 0) & (w < 1e6)
    ip = np.searchsorted(PT_OLD, pt, side="right") - 1
    iz = np.searchsorted(PZ, pz, side="right") - 1
    g = np.where((ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16), ip * 16 + iz, -1)
    cc = L.is_numu_cc(d["nu_pdg"][rows], d["current"][rows])
    fid = oflow_fid(d["vtx_x"][rows], d["vtx_y"][rows], d["vtx_z"][rows])
    out = {}
    for name, sel in (("FAKE_PS", cc & fid), ("FAKE_VTX", cc & ~fid), ("OTHER", ~cc)):
        m = ok & sel & (g >= 0)
        out[name] = np.bincount(g[m], weights=w[m] * pot_scale, minlength=224)
        out[name + "_n"] = int(m.sum())
    return out


def run(a) -> int:
    rec: dict = {"schema": "oofvc-join/1", "inputs": {}, "controls": {}}
    rec["inputs"]["omnifile_sha256"] = sha256(a.omnifile)
    rec["inputs"]["split_sha256"] = sha256(a.split)
    def stop(name, why):
        rec["controls"].setdefault(name, {}).update({"pass": False, "why": str(why)})  # keep the measured fields
        rec["verdict"] = "STOP"
        (a.out / "join.json").write_text(json.dumps(rec, indent=1, default=float) + "\n")
        print(f"STOP {name}: {why}", flush=True)
        return RC_STOP

    try:
        d, rec["inputs"]["dump_sha256"] = read_dumps(a.dump_dir)
    except L.ReadRefusal as e:
        return stop("C-READ", e)
    import ROOT
    f = ROOT.TFile.Open(str(a.omnifile))
    pot_scale = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal()
    f.Close()
    rec["pot_scale"] = pot_scale
    try:
        bkg = read_tree(a.omnifile, "mc_background", ("sim_background", "sim_background_pz", "sim_background_pass",
                                                      "w_bkg"), BKG_FLAGS)
        sig = read_tree(a.omnifile, "mc_signal_reco", ("sim", "sim_pz", "sim_pass", "w_reco", "MC", "MC_pz", "w_truth"),
                        SIG_FLAGS)
    except L.ReadRefusal as e:
        return stop("C-READ", e)
    rec["controls"]["C-READ"] = {"pass": True, "note": "object one-character columns read as uint8; flags in {0, 1}"}

    to_bkg, to_sig, dup = d["to_bkg"] != 0, d["to_sig"] != 0, d["dup_sig"] != 0
    n_dis = L.route_disagree(to_bkg, to_sig)
    rec["controls"]["C-ROUTE"] = {"n_rows": int(to_bkg.size), "n_disagree": n_dis, "pass": n_dis == 0}
    if n_dis:
        return stop("C-ROUTE", f"{n_dis} rows routed to both or neither tree")

    # C-JOIN: every mc_background entry against the dump's to_bkg rows
    rb = np.flatnonzero(to_bkg)
    if np.any(bkg["sim_background_pass"] == 0):
        return stop("C-JOIN", "mc_background holds rows with sim_background_pass 0; the background loop writes only "
                              "selected entries")
    ev = np.column_stack([d["playlist"], d["mc_run"], d["mc_subrun"], d["mc_nthEvtInFile"]])
    vals = np.column_stack([d[k] for k in DUMP_FLOAT] + [d[k] for k in ("nu_pdg", "current", "fid")])
    try:
        j = L.exact_join((bkg["sim_background"], bkg["sim_background_pz"], bkg["w_bkg"]),
                         (d["reco_pt"][rb], d["reco_pz"][rb], d["w_reco"][rb]), ev[rb], vals[rb], bkg["w_bkg"])
    except L.JoinStop as e:
        return stop("C-JOIN", e)
    m = rb[j["right_of_left"]]  # the dump row of each mc_background entry
    moved = L.moved_mask(d["nu_pdg"][m], d["current"][m], d["true_pt"][m], d["true_pz"][m], PT_OLD, PZ)
    moved_w = float(bkg["w_bkg"][moved].sum())
    tied_moved_w = float(bkg["w_bkg"][j["tied_left"] & moved].sum())
    try:
        L.check_tie_bound(j["tied_weight"], moved_w)
    except L.JoinStop as e:
        return stop("C-JOIN", e)
    rec["controls"]["C-JOIN"] = {"n_background": int(bkg["w_bkg"].size), "n_dump_to_bkg": int(rb.size),
                                 "n_tied_groups": j["n_tied_groups"], "n_tied_rows": j["n_tied_rows"],
                                 "tied_weight": j["tied_weight"], "tied_weight_moved": tied_moved_w,
                                 "moved_weight": moved_w, "pass": True}

    # C-SIGW: the selected signal rows against the dump's kept to_sig rows, then the truth side bit for bit
    sel = sig["sim_pass"] != 0
    rs = np.flatnonzero(to_sig & ~dup)
    try:
        js = L.exact_join((sig["sim"][sel], sig["sim_pz"][sel], sig["w_reco"][sel]),
                          (d["reco_pt"][rs], d["reco_pz"][rs], d["w_reco"][rs]), ev[rs], vals[rs], sig["w_reco"][sel])
        L.check_tie_bound(js["tied_weight"], float(sig["w_reco"][sel].sum()))
    except L.JoinStop as e:
        return stop("C-SIGW", e)
    ms = rs[js["right_of_left"]]
    truth_equal = {k: bool(np.array_equal(sig[s][sel].astype(np.float64).view(np.uint64),
                                          d[t][ms].astype(np.float64).view(np.uint64)))
                   for s, t, k in (("MC", "true_pt", "MC"), ("MC_pz", "true_pz", "MC_pz"), ("w_truth", "w_truth", "w_truth"))}
    rec["controls"]["C-SIGW"] = {"n_signal_selected": int(sel.sum()), "n_dump_to_sig_kept": int(rs.size),
                                 "n_dump_dup_sig": int((to_sig & dup).sum()), "n_tied_groups": js["n_tied_groups"],
                                 "tied_weight": js["tied_weight"], "truth_bit_equal": truth_equal,
                                 "pass": all(truth_equal.values())}
    if not all(truth_equal.values()):
        return stop("C-SIGW", f"truth side differs: {truth_equal}")

    # C-LAB: oflow's categories from the joined rows against oflow/split.json
    ref = json.loads(a.split.read_text())
    got = categories(d, m, pot_scale)
    worst, cnt_ok, finite = 0.0, True, True
    for k in ("FAKE_PS", "FAKE_VTX", "OTHER"):
        r = np.asarray(ref[k], float)
        finite &= bool(r.size == got[k].size == 224 and np.all(np.isfinite(r)) and np.all(np.isfinite(got[k])))
        if not finite:
            break
        nz = r != 0
        dev = np.concatenate([np.abs(got[k][nz] / r[nz] - 1), np.abs(got[k][~nz])])
        worst = max(worst, float(dev.max(initial=0.0)))
        cnt_ok &= got[k + "_n"] == ref[k + "_n"]
    rec["controls"]["C-LAB"] = {"max_rel": worst, "counts_equal": bool(cnt_ok), "finite": finite,
                                "n": {k: got[k + "_n"] for k in ("FAKE_PS", "FAKE_VTX", "OTHER")},
                                "pass": bool(finite and worst <= LAB_RTOL and cnt_ok)}
    if not rec["controls"]["C-LAB"]["pass"]:
        return stop("C-LAB", f"max relative {worst:.3g}, counts equal {cnt_ok}")

    # the moved rows (section 1.3), and the class sizes the record reports (ruling 3)
    e = np.flatnonzero(moved)
    rows = {"entry": e.astype(np.int64), "reco_pt": bkg["sim_background"][e].astype(np.float64),
            "reco_pz": bkg["sim_background_pz"][e].astype(np.float64),
            "true_pt": d["true_pt"][m[e]].astype(np.float64), "true_pz": d["true_pz"][m[e]].astype(np.float64),
            "w_reco": bkg["w_bkg"][e].astype(np.float64), "w_truth": d["w_truth"][m[e]].astype(np.float64)}
    cc = L.is_numu_cc(d["nu_pdg"][m], d["current"][m])
    fid = d["fid"][m] != 0
    reco_in = L.in_bins(bkg["sim_background"], bkg["sim_background_pz"], PT_OLD, PZ)
    w = bkg["w_bkg"] * pot_scale

    def size(mask):
        return {"rows": int(mask.sum()), "weight_pot": float(w[mask].sum()),
                "weight_pot_reco_in_grid": float(w[mask & reco_in].sum())}
    rec["classes"] = {"moved_out_of_fiducial": size(moved & ~fid), "moved_fiducial": size(moved & fid),
                      "moved_reco_outside_grid": size(moved & ~reco_in),
                      "kept_true_muon_outside_grid_out_of_fiducial": size(cc & ~moved & ~fid),
                      "kept_true_muon_outside_grid_fiducial": size(cc & ~moved & fid),
                      "other": size(~cc)}
    a.out.mkdir(parents=True, exist_ok=True)
    np.savez(a.out / "oofvc_rows.npz", **rows)
    rec["rows_sha256"] = sha256(a.out / "oofvc_rows.npz")
    rec["verdict"] = "PASS"
    (a.out / "join.json").write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(json.dumps({"verdict": "PASS", "moved": int(e.size), "rows_sha256": rec["rows_sha256"]}), flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--omnifile", type=Path, required=True)
    ap.add_argument("--dump-dir", type=Path, required=True)
    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if (a.out / "join.json").exists() or (a.out / "oofvc_rows.npz").exists():
        print("refusing: the output exists", file=sys.stderr)
        return 2
    a.out.mkdir(parents=True, exist_ok=True)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
