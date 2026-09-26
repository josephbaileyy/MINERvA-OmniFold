#!/usr/bin/env python3
"""s5p Stage 4 inputs: weight-only detector universes and selection-complete lateral endpoints, dumped
into the ROOT-free forms the negweight-refined npz path reads.

``detector``: one pass over an omnifile that carries the weight-only detector bands (default
MinosEfficiency and GEANT_Neutron/Pion/Proton, +-1 sigma each). With the driver's own collectors
(``unfold_nd_omnifold_unbinned.collect_signal_nd`` / ``collect_truth_denom_nd`` / ``collect_bkg_nd`` with
``extra_wbranches``) it writes, per universe, ``{tag}_wt.npy`` / ``{tag}_wr.npy`` (signal truth/reco
weights, POT-scaled, row-aligned with the CV npz), ``{tag}_bkgw.npy`` (background event weights, row-aligned
with the s5c background dump) and ``{tag}_denom_nd.npy`` (the universe's truth-denominator histogram). It
REFUSES to write unless the same pass's CV arrays reproduce the npz (MC coordinates, pass flags, weights,
measured events, denominator) and the background dump (coordinates, weights) exactly: that is what makes
the universe weights belong to those rows.

``lateral``: one selection-complete lateral endpoint omnifile (``active_universe_5d/standard/merged/``: the
CV branches carry that endpoint's shifted kinematics) dumped exactly as ``nn_dump_inputs.py`` dumps the CV
omnifile (axes eavail, q3, W), plus its background dump in the ``s5c_dump_bkg.py`` form (``bkg_reco``,
``bkg_w``, ``bkg_nd``, ``meta.npz_sha256``). The observed events must equal the CV npz's.

MEASURES: nothing scientific; it re-expresses committed event-loop outputs. CANNOT AUTHORIZE: any
uncertainty, construction or adoption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
for p in (str(_ND.parent / "2d-unfolding"), str(_ND)):
    if p not in sys.path:
        sys.path.insert(0, p)

DETECTOR_BANDS = ("MinosEfficiency:0", "MinosEfficiency:1", "GEANT_Neutron:0", "GEANT_Neutron:1",
                  "GEANT_Pion:0", "GEANT_Pion:1", "GEANT_Proton:0", "GEANT_Proton:1")
AXES = ("eavail", "q3", "W")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def setup():
    import ROOT  # noqa: F401
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und
    extras = [dict(und.EXTRA_AXES[a], name=a) for a in AXES]
    edges = [u2d.PT_EDGES, u2d.PZ_EDGES] + [ax["edges"] for ax in extras]
    return u2d, und, extras, edges


def same(name: str, a, b, tol=0.0) -> None:
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        raise RuntimeError(f"{name}: shape {a.shape} != {b.shape}")
    if tol == 0.0:
        ok = np.array_equal(a, b, equal_nan=np.issubdtype(a.dtype, np.floating))
    else:
        ok = np.allclose(a, b, rtol=tol, atol=0.0, equal_nan=True)
    if not ok:
        raise RuntimeError(f"{name}: differs from the reference")


def detector(a) -> int:
    import ROOT
    u2d, und, extras, edges = setup()
    san = u2d._sanitize_band_for_branch
    unis = [(b, int(i)) for b, _, i in (u.partition(":") for u in a.universes.split(","))]
    pt_lo, pt_hi, pz_lo, pz_hi = edges[0][0], edges[0][-1], edges[1][0], edges[1][-1]
    f = ROOT.TFile.Open(str(a.omnifile), "READ")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    t0 = time.time()
    sig = und.collect_signal_nd(f.Get("mc_signal_reco"), extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale, use_weights=True,
                                extra_wbranches=[(f"w_truth_{san(b)}_{i}", f"w_reco_{san(b)}_{i}") for b, i in unis])
    td = und.collect_truth_denom_nd(f.Get("mc_truth_denom"), extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale, use_weights=True,
                                    extra_wbranches=[f"w_truth_{san(b)}_{i}" for b, i in unis])
    bkg_pt, bkg_pz, bkg_ex, bkg_w, bkg_uw = und.collect_bkg_nd(f.Get("mc_background"), extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi,
                                                              extra_wbranches=[f"w_bkg_{san(b)}_{i}" for b, i in unis])
    meas_pt, meas_pz, meas_ex = und.collect_data_nd(f.Get("data"), extras, pt_lo, pt_hi, pz_lo, pz_hi)
    f.Close()
    z = np.load(a.npz, allow_pickle=True)
    bz = np.load(a.bkg, allow_pickle=True)
    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"], *sig["truth_extras"]]).astype(np.float32)
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"], *sig["reco_extras"]]).astype(np.float32)
    same("MCgen", MCgen, z["MCgen"])
    same("MCreco", MCreco, z["MCreco"])
    same("pass_reco", sig["pass_reco"], z["pass_reco"])
    same("pass_truth", sig["pass_truth"], z["pass_truth"])
    same("w_truth", sig["w_truth"], z["w_truth"])
    same("w_reco", sig["w_reco"], z["w_reco"])
    same("measured", np.column_stack([meas_pt, meas_pz, *meas_ex]).astype(np.float32), z["measured"])
    denom_cv, _ = und.histnd([td["pt"], td["pz"]] + td["extras"], td["w"], edges)
    same("denom_nd", denom_cv, z["denom_nd"])
    same("bkg_reco", np.column_stack([bkg_pt, bkg_pz] + bkg_ex), bz["bkg_reco"])
    same("bkg_w", bkg_w, bz["bkg_w"])
    a.out.mkdir(parents=True, exist_ok=True)
    written = {}
    for k, (b, i) in enumerate(unis):
        tag = f"{b}_{i}"
        dn, _ = und.histnd([td["pt"], td["pz"]] + td["extras"], td["extra_w"][k], edges)
        arrays = {"wt": np.asarray(sig["extra_wt"][k], np.float32), "wr": np.asarray(sig["extra_wr"][k], np.float32),
                  "bkgw": np.asarray(bkg_uw[k], np.float32), "denom_nd": np.asarray(dn, np.float64)}
        for key, arr in arrays.items():
            path = a.out / f"{tag}_{key}.npy"
            if path.exists():
                raise RuntimeError(f"refusing to overwrite {path}")
            np.save(path, arr)
            written[f"{tag}_{key}.npy"] = sha256(path)
    receipt = {"schema": "s5p-detector-dump/1", "omnifile": str(a.omnifile), "npz": str(a.npz), "npz_sha256": sha256(a.npz),
               "bkg_dump": str(a.bkg), "bkg_sha256": sha256(a.bkg), "universes": [f"{b}:{i}" for b, i in unis],
               "cv_reproduced": ["MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco", "measured", "denom_nd",
                                 "bkg_reco", "bkg_w"], "files_sha256": written, "seconds": round(time.time() - t0, 1),
               "code_sha256": sha256(Path(__file__).resolve())}
    (a.out / "detector-dump.json").write_text(json.dumps(receipt, indent=1) + "\n")
    print(json.dumps({"written": len(written), "seconds": receipt["seconds"]}))
    return 0


def lateral(a) -> int:
    import ROOT
    u2d, und, extras, edges = setup()
    pt_lo, pt_hi, pz_lo, pz_hi = edges[0][0], edges[0][-1], edges[1][0], edges[1][-1]
    for path in (a.out, a.out_bkg):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    f = ROOT.TFile.Open(str(a.omnifile), "READ")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    flux_bins, _ = u2d.load_flux_bins(str(a.mcfile), a.flux_hist, edges[0])
    meas_pt, meas_pz, meas_ex = und.collect_data_nd(f.Get("data"), extras, pt_lo, pt_hi, pz_lo, pz_hi)
    bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(f.Get("mc_background"), extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi)
    sig = und.collect_signal_nd(f.Get("mc_signal_reco"), extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale, use_weights=True)
    td = und.collect_truth_denom_nd(f.Get("mc_truth_denom"), extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale, use_weights=True)
    f.Close()
    measured = np.column_stack([meas_pt, meas_pz, *meas_ex]).astype(np.float32)
    z = np.load(a.cv_npz, allow_pickle=True)
    same("measured (data are not shifted by a lateral MC band)", measured, z["measured"])
    same("flux", flux_bins, z["flux"], tol=1e-12)
    data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
    bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
    meas_w = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)
    denom_nd, _ = und.histnd([td["pt"], td["pz"]] + td["extras"], td["w"], edges)
    np.savez_compressed(a.out, axes=np.array(list(AXES), dtype=object),
                        MCgen=np.column_stack([sig["truth_pt"], sig["truth_pz"], *sig["truth_extras"]]).astype(np.float32),
                        MCreco=np.column_stack([sig["reco_pt"], sig["reco_pz"], *sig["reco_extras"]]).astype(np.float32),
                        measured=measured, pass_reco=sig["pass_reco"], pass_truth=sig["pass_truth"],
                        w_truth=sig["w_truth"], w_reco=sig["w_reco"], measured_weights=meas_w, denom_nd=denom_nd,
                        flux=np.asarray(flux_bins, float), data_pot=data_pot, n_nucleons=u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
                        **{f"edges_{i}": np.asarray(e, float) for i, e in enumerate(edges)}, nedges=len(edges))
    npz_sha = sha256(a.out)
    meta = {"schema": "s5p-lateral-bkg-dump/1", "omnifile": str(a.omnifile), "npz": str(a.out), "npz_sha256": npz_sha,
            "axes": list(AXES), "code_sha256": sha256(Path(__file__).resolve()), "cv_npz": str(a.cv_npz),
            "check": "measured equals the CV npz's; background collected by collect_bkg_nd from this endpoint's own trees",
            "seconds": round(time.time() - t0, 1)}
    np.savez_compressed(a.out_bkg, bkg_reco=np.column_stack([bkg_pt, bkg_pz] + bkg_ex), bkg_w=np.asarray(bkg_w, float),
                        bkg_nd=bkg_nd, meta=json.dumps(meta))
    print(json.dumps({"npz": str(a.out), "npz_sha256": npz_sha, "bkg_sha256": sha256(a.out_bkg), "mc_rows": int(sig["pass_truth"].size),
                      "bkg_rows": int(bkg_w.size), "seconds": meta["seconds"]}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detector")
    d.add_argument("--omnifile", type=Path, required=True)
    d.add_argument("--npz", type=Path, required=True)
    d.add_argument("--bkg", type=Path, required=True)
    d.add_argument("--universes", default=",".join(DETECTOR_BANDS))
    d.add_argument("--out", type=Path, required=True, help="bank directory for the weight files")
    l = sub.add_parser("lateral")
    l.add_argument("--omnifile", type=Path, required=True)
    l.add_argument("--cv-npz", type=Path, required=True)
    l.add_argument("--mcfile", type=Path, default=Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"))
    l.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    l.add_argument("--out", type=Path, required=True)
    l.add_argument("--out-bkg", type=Path, required=True)
    a = ap.parse_args(argv)
    return detector(a) if a.cmd == "detector" else lateral(a)


if __name__ == "__main__":
    raise SystemExit(main())
