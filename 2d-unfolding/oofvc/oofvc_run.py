#!/usr/bin/env python3
"""OOFVC units (OOFVC-DECLARATION.md section 2.1): E_R's driver through REF-C2C1's runner, unchanged, in the deploy
tree built by make_tree.sh (the paper's pT edges and the OOFVC option). Four units, each through ref_c2c1.run_unit
with E_R's argv:
  off/er, off/c2_central   production (C-BASE against Tier 1's E units, scored on the laptop)
  R/er,   R/c2_central     --signal-convention minerva --oofvc-rows ROWS
Each c2 unit also yields N (the IBU-only secondary) from the same run: the signal loader's sim_pass per row is
recorded (record_selected), O_j is formed from the selected rows whose reco is outside the grid (plus, under R, the
moved rows reconstructed outside it), and u^N_K = u_K * sum_i M_ij / (sum_i M_ij + O_j) is re-extracted by the driver's
own recorded extraction. ref_c2c1.py, its C-SIM, C-ROO and C-FILL run as they are.

  python3 oofvc_run.py --tree DEPLOY --rows ROWS.npz --rows-sha256 SHA --out OUT [--unit off/er ...]
Exit 0 only if every unit's controls pass; a refused precondition is 4, a failed control 6.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import oofvc_lib as L  # noqa: E402

UNITS = ("off/er", "off/c2_central", "R/er", "R/c2_central")
RC_GATE, RC_CONTROL = 4, 6
MINERVA_ARGV = ["--signal-convention", "minerva", "--oofvc-rows"]


def sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def import_runner(tree: Path):
    sys.path.insert(0, str(tree / "2d-unfolding" / "ref_c2c1"))
    import ref_c2c1 as C
    if Path(C.__file__).resolve().parent != (tree / "2d-unfolding" / "ref_c2c1").resolve():
        raise RuntimeError(f"ref_c2c1 resolved outside the deploy tree: {C.__file__}")
    return C


def moved_outside_direct(rows: dict, pot_scale: float, pt_e, pz_e) -> np.ndarray:
    """N's moved part straight from the join's rows file: rows with a true cell and no reco cell, the background
    loader's weight rule (0 <= w < 1e6), reco weight x POT scale at the true cell (C-NMOVED's reference)."""
    t_ok = L.in_bins(rows["true_pt"], rows["true_pz"], pt_e, pz_e)
    r_ok = L.in_bins(rows["reco_pt"], rows["reco_pz"], pt_e, pz_e)
    w = np.asarray(rows["w_reco"], float)
    m = t_ok & ~r_ok & (w >= 0) & (w < 1e6)
    return L.o_vector(rows["true_pt"][m], rows["true_pz"][m], w[m] * pot_scale, pt_e, pz_e)


def n_record(C, driver, cap: dict, sig: dict, outside, ks, rows=None, pot_scale=None) -> dict:
    """N from one c2 run: O_j, the factor, u^N_K at every K, and its cross section by the recorded extraction."""
    pt_e, pz_e = driver.PT_EDGES, driver.PZ_EDGES
    t = L.global_index(sig["truth_pt"], sig["truth_pz"], pt_e, pz_e)
    r = L.global_index(sig["reco_pt"], sig["reco_pz"], pt_e, pz_e)
    pt_ok, sel = np.asarray(sig["pass_truth"], bool), np.asarray(sig["selected"], bool)
    w_reco = np.asarray(sig["w_reco"], float)
    # O's signal part: selected rows with a true cell and no reco cell (reco outside the grid, or on its upper edge,
    # where ROOT and M put it in the overflow)
    o_rows = sel & pt_ok & (t >= 0) & (r < 0)
    O = np.bincount(t[o_rows], weights=w_reco[o_rows], minlength=cap["T"].size)
    o_moved = np.zeros_like(O)
    if outside is not None:  # R: the moved rows reconstructed outside the grid (not appended)
        o_moved = L.o_vector(outside["truth_pt"], outside["truth_pz"], outside["w_reco"], pt_e, pz_e)
    O_all = O + o_moved
    sum_m = cap["M"].sum(axis=0)
    fac = L.n_factor(sum_m, O_all)
    traj_n = {K: cap["traj"][K] * fac for K in ks}
    nid = {K: cap["traj"][K] * L.n_factor(sum_m, np.zeros_like(O_all)) for K in ks}
    controls = {"C-NID": {"pass": bool(all(np.array_equal(nid[K], cap["traj"][K]) for K in ks))}}
    # C-NSUM: sum_j (sum_i M_ij + O_j) against the selected, truth-in-grid weight counted from the loader's rows,
    # plus the moved part recomputed from the rows file (not the driver's)
    direct_moved = np.zeros_like(O) if rows is None else moved_outside_direct(rows, pot_scale, pt_e, pz_e)
    direct = float(w_reco[sel & pt_ok & (t >= 0)].sum()) + float(direct_moved.sum())
    total = float(sum_m.sum() + O_all.sum())
    controls["C-NSUM"] = {"total": total, "direct": direct,
                          "pass": bool(abs(total / direct - 1) <= 1e-12 if direct > 0 else total == 0)}
    # C-NMOVED: the driver's moved part equals the rows file's, cell by cell
    dev = float(np.max(np.abs(o_moved - direct_moved))) if o_moved.size else 0.0
    controls["C-NMOVED"] = {"max_abs": dev, "sum": float(direct_moved.sum()),
                            "pass": bool(dev <= 1e-12 * max(1.0, float(np.abs(direct_moved).max(initial=0.0))))}
    xs_n = C.xsec_at_every_k(driver, {"traj": traj_n, "extract": cap["extract"],
                                      "real_extract": cap["real_extract"]}, ks)
    return {"O_signal": O, "O_moved": o_moved, "sum_M": sum_m, "factor": fac,
            "unfolded_N": np.array([traj_n[K] for K in ks]), "xsec_N": np.array([xs_n[K] for K in ks]),
            "controls": controls}


def run(a) -> int:
    C = import_runner(a.tree)
    cfg = json.loads(C.CONFIG.read_text())
    try:
        C.check_code(cfg)
        verified = C.check_inputs(cfg)
        driver, ohf = C.load_driver()
    except (C.GateFailure, OSError) as e:
        print(f"refusing: {e}", file=sys.stderr)
        return RC_GATE
    if sha256(a.rows) != a.rows_sha256:
        print("refusing: the rows file is not the join's", file=sys.stderr)
        return RC_GATE
    if not C.under(a.rows, C.staging_root(cfg)):
        print("refusing: the rows file is not under the staging root", file=sys.stderr)
        return RC_GATE
    lib = Path(cfg["inputs"]["roounfold_lib"])

    def lib_sha():
        return "numpy unfolder" if a.numpy_unfolder else (sha256(lib) if lib.is_file() else "missing")
    if not a.numpy_unfolder and lib_sha() != cfg["inputs"]["roounfold_lib_sha256"]:
        print("refusing: libRooUnfold.so is not its pin", file=sys.stderr)
        return RC_GATE
    rows = {k: v for k, v in np.load(a.rows).items()}
    pins_before = {"driver": sha256(C.RE2), "runner": sha256(Path(C.__file__)), "oofvc_run": sha256(Path(__file__)),
                   "oofvc_lib": sha256(HERE / "oofvc_lib.py"), "rows": sha256(a.rows), "inputs": verified,
                   "roounfold_lib": lib_sha(), "join_record": sha256(a.join_record)}
    rc = 0
    outputs = {}  # every file each unit wrote, by digest (codex-school r2 #1: n.npz and the records are covered)
    for unit in a.unit:
        conv, kind = unit.split("/")
        out = a.out / conv
        cfg_u = copy.deepcopy(cfg)
        if conv == "R":
            cfg_u["e_r"]["argv"] = list(cfg["e_r"]["argv"]) + MINERVA_ARGV + [str(a.rows)]
        seen: dict = {}
        real_run_driver, real_loader = C.run_driver, driver.collect_signal_arrays_2d

        def run_driver(*args, **kw):
            cap = real_run_driver(*args, **kw)
            seen["cap"] = cap
            return cap

        def loader(*args, **kw):
            sig = real_loader(*args, record_selected=True, **kw)
            seen["sig"] = sig
            return sig
        with mock.patch.object(C, "run_driver", run_driver), \
                mock.patch.object(driver, "collect_signal_arrays_2d", loader):
            urc = C.run_unit(driver, ohf, cfg_u, (kind, None), out, inputs_verified=verified,
                             unfolder=C.dagostini if a.numpy_unfolder else None)
        rec = {"unit": unit, "rc": urc, "argv": C.resolve_argv(cfg_u, None), "numpy_unfolder": a.numpy_unfolder,
               "n_signal_rows": int(seen["sig"]["truth_pt"].size) if "sig" in seen else None}
        outside = seen["sig"].get("oofvc_outside") if "sig" in seen else None
        rec["oofvc_counts"] = outside["counts"] if outside is not None else None
        if kind == "c2_central" and urc == 0:
            ks = list(cfg["c2"]["iterations"]["scan"])
            import ROOT
            f = ROOT.TFile.Open(str(out / f"{kind}.root"))
            pot = float(f.Get("potScale").GetVal())
            f.Close()
            nr = n_record(C, driver, seen["cap"], seen["sig"], outside, ks,
                          rows=rows if conv == "R" else None, pot_scale=pot)
            np.savez_compressed(out / "n.npz", ks=np.array(ks), **{k: v for k, v in nr.items() if k != "controls"})
            rec["n_controls"] = nr["controls"]
            if not all(c["pass"] for c in nr["controls"].values()):
                urc = RC_CONTROL
        (out / f"{kind}.oofvc.json").write_text(json.dumps(rec, indent=1, default=str) + "\n")
        names = [f"{kind}.done", f"{kind}.npz", f"{kind}.root", f"{kind}.oofvc.json"] + (
            ["n.npz"] if kind == "c2_central" and (out / "n.npz").exists() else [])
        outputs[unit] = {n: sha256(out / n) for n in names if (out / n).exists()}
        rc = rc or urc
    pins_after = {"driver": sha256(C.RE2), "runner": sha256(Path(C.__file__)), "oofvc_run": sha256(Path(__file__)),
                  "oofvc_lib": sha256(HERE / "oofvc_lib.py"), "rows": sha256(a.rows), "inputs": C.check_inputs(cfg),
                  "roounfold_lib": lib_sha(), "join_record": sha256(a.join_record)}
    c_pins = pins_before == pins_after
    tag = "_".join(u.replace("/", "-") for u in a.unit)  # one pins file per process (the job runs four at once)
    (a.out / f"pins_{tag}.json").write_text(json.dumps({"units": a.unit, "before": pins_before, "after": pins_after,
                                                        "outputs": outputs, "pass": c_pins}, indent=1) + "\n")
    return rc or (0 if c_pins else RC_CONTROL)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--rows-sha256", required=True)
    ap.add_argument("--join-record", type=Path, required=True,
                    help="the join's join.json; its digest is pinned with the rows, so the scorer reads the record the "
                         "units ran beside (codex-school r3 #3)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--unit", action="append", choices=UNITS)
    ap.add_argument("--numpy-unfolder", action="store_true",
                    help="tests only, where no libRooUnfold exists: ref_c2c1's numpy update replaces RooUnfoldBayes, so "
                         "C-ROO does not run. The cluster script never passes it, and the scorer refuses a c2 unit "
                         "without C-ROO")
    a = ap.parse_args(argv)
    a.unit = a.unit or list(UNITS)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
