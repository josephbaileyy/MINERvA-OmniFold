#!/usr/bin/env python3
"""Export the small arrays behind the article's Figs. 1-3 (and the numbers they quote) to one npz + manifest.

Run on a Perlmutter login node from a clean clone, in the analysis ROOT environment (root_6_28). It imports the
committed producers' own loaders -- never retypes them -- and refuses if any of them resolves outside the clone
(OI-136). Every source file is hashed into the manifest.

  Fig. 1  2d-unfolding/compare_to_models.py + compare_to_paper_fullcov.py (+ agreement_windows_receipt.bin_areas)
          ours hXSec2D, the published TH2D and its Total/StatOnly covariances, the MINERvA Tune v1 ancillary.
  Fig. 2  nd-unfolding/excess_eavail_W.py output excess_eavail_W.root: hData2D (unfolded, d2sigma/dEavail dW),
          hGenCV2D (the comparator: mc_truth_denom x w_truth, i.e. MINERvA Tune v1 -- the OmniFold prior),
          hExcess2D (cell-integrated data - comparator).
  Fig. 3  3d-unfolding/genie/overlay_eavailW_band.py inputs: hData2D above and the four flux-repaired generator
          hXSec_eavailW files (Stage-7 generator-context receipt sidecars).

Report-only cross-checks (do not gate the export): hData2D re-projected from the 5D product with the producer's
own load_data_xsec/project_marginal; the Fig. 2 comparator against the s5p MnvTune 5D prediction where the grids
allow.

MEASURES: nothing new. CANNOT AUTHORIZE: any uncertainty (the 2D band is being rebuilt as VL170; not exported).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--code-root", type=Path, required=True, help="clean clone whose producers are imported")
    ap.add_argument("--analysis-root", type=Path, default=Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold"))
    ap.add_argument("--genfig", type=Path,
                    default=Path("/pscratch/sd/j/josephrb/s5p-20260926/stage7/genfig/3d-unfolding/genie"))
    ap.add_argument("--mnvtune5d", type=Path, default=Path("/pscratch/sd/j/josephrb/s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz"))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    for p in (a.out, Path(str(a.out) + ".manifest.json")):
        if p.exists():
            raise SystemExit(f"refusing to overwrite {p}")
    cr = a.code_root.resolve()
    for sub in ("2d-unfolding", "nd-unfolding", "3d-unfolding/genie"):
        sys.path.insert(0, str(cr / sub))
    import ROOT  # noqa: E402
    ROOT.gROOT.SetBatch(True)
    import compare_to_paper_fullcov as cpf  # noqa: E402
    import compare_to_models as ctm  # noqa: E402
    import agreement_windows_receipt as awr  # noqa: E402
    import overlay_eavailW_band as oeb  # noqa: E402
    import excess_eavail_W as eew  # noqa: E402
    import xsec_nd  # noqa: E402
    mods = {m.__name__: m for m in (cpf, ctm, awr, oeb, eew, xsec_nd)}
    for name, m in mods.items():
        if not Path(m.__file__).resolve().is_relative_to(cr):
            raise SystemExit(f"{name} imported from {m.__file__}, outside the clone {cr} (OI-136)")

    A = a.analysis_root
    src = {
        "ours_2d": A / "2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root",
        "paper_cov": A / "2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root",
        "tune_v1_txt": A / "2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt",
        "excess_eavail_W": A / "nd-unfolding/products/5d/excess_eavail_W.root",
        "xsec_5d": A / "nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root",
        "gen_GENIE-CV": a.genfig / "genie_cv_xsec_eavailW.root",
        "gen_GENIE+MEC": a.genfig / "genie_mec_xsec_eavailW.root",
        "gen_NuWro": a.genfig / "nuwro_cv_xsec_eavailW.root",
        "gen_GiBUU": a.genfig / "gibuu_cv_xsec_eavailW.root",
        "mnvtune_5d": a.mnvtune5d,
    }
    out = {}
    # ---- Fig. 1 -------------------------------------------------------------------------------------------
    fp = ROOT.TFile.Open(str(src["paper_cov"]))
    h_paper = fp.Get("pt_pl_cross_section")
    out["paper_v"] = cpf.flatten_th2d(h_paper)
    out["cov_total"] = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
    out["cov_stat"] = cpf.tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    out["area_paper"] = awr.bin_areas(h_paper)
    fo = ROOT.TFile.Open(str(src["ours_2d"]))
    h_ours = fo.Get("hXSec2D")
    out["ours_v"] = cpf.flatten_ours(h_ours)
    out["area_ours"] = awr.bin_areas(h_ours)
    out["tune_v1_v"] = ctm.load_model_csv(str(src["tune_v1_txt"]))
    out["mask_reported"] = np.diag(out["cov_stat"]) > 0
    out["pt_edges"], out["pz_edges"] = ctm.PT_EDGES, ctm.PZ_EDGES
    # ---- Figs. 2-3 ----------------------------------------------------------------------------------------
    fe = ROOT.TFile.Open(str(src["excess_eavail_W"]))
    for k in ("hData2D", "hGenCV2D", "hExcess2D"):
        out[k] = oeb.th2_to_np(fe.Get(k))
    out["eavail_edges"], out["W_edges"] = oeb.EAVAIL_EDGES, oeb.W_EDGES
    gens = []
    for key in [k for k in src if k.startswith("gen_")]:
        f = ROOT.TFile.Open(str(src[key]))
        out[f"{key}"] = oeb.th2_to_np(f.Get("hXSec_eavailW"))
        gens.append(key[4:])
    # ---- report-only cross-checks -------------------------------------------------------------------------
    checks = {}
    und, u2d = eew.und, eew.u2d
    axis_names = ["eavail", "q3", "W"]
    extras = [dict(und.EXTRA_AXES[x], name=x) for x in axis_names]
    edges = [u2d.PT_EDGES, u2d.PZ_EDGES] + [ax["edges"] for ax in extras]
    shape = tuple(len(e) - 1 for e in edges)
    d5 = eew.load_data_xsec(str(src["xsec_5d"]), shape)
    md = xsec_nd.project_marginal(d5, edges, drop_axes=[0, 1, 3])
    rel = float(np.max(np.abs(md - out["hData2D"]) / np.maximum(np.abs(out["hData2D"]), 1e-300)))
    checks["hData2D_vs_5d_product_projection"] = {"max_rel_diff": rel, "shape": list(md.shape)}
    try:
        z = np.load(src["mnvtune_5d"], allow_pickle=True)
        flat = np.asarray(z["xsec_flat"], float)
        if flat.size == int(np.prod(shape)):
            mt = xsec_nd.project_marginal(flat.reshape(shape), edges, drop_axes=[0, 1, 3])
            r = mt / np.where(out["hGenCV2D"] > 0, out["hGenCV2D"], np.nan)
            checks["comparator_vs_s5p_mnvtune5d"] = {"ratio_median": float(np.nanmedian(r)),
                                                     "ratio_min": float(np.nanmin(r)), "ratio_max": float(np.nanmax(r))}
        else:
            checks["comparator_vs_s5p_mnvtune5d"] = {"skipped": f"grid size {flat.size} != {int(np.prod(shape))}"}
    except Exception as e:  # report-only
        checks["comparator_vs_s5p_mnvtune5d"] = {"skipped": f"{type(e).__name__}: {e}"}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **out)
    head = subprocess.run(["git", "-C", str(cr), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    man = {"schema": "article-figs-arrays/1", "code_root": str(cr), "code_commit": head,
           "producer_modules": {n: {"path": str(Path(m.__file__).resolve().relative_to(cr)), "sha256": sha256(m.__file__)}
                                for n, m in mods.items()},
           "sources": {k: {"path": str(v), "sha256": sha256(v), "bytes": Path(v).stat().st_size} for k, v in src.items()},
           "generators": gens,
           "units": {"ours_v/paper_v/tune_v1_v": "d2sigma/(dpT dppar), cm^2/(GeV/c)^2/nucleon, 224 global bins gid=(ptbin-1)*16+(pzbin-1)",
                     "cov_*": "paper covariance on the 224 grid (cm^2/(GeV/c)^2/nucleon)^2",
                     "area_*": "bin area dpT*dppar (GeV/c)^2",
                     "hData2D/hGenCV2D/gen_*": "d2sigma/(dEavail dW), cm^2/GeV^2/nucleon, (7 Eavail x 6 W)",
                     "hExcess2D": "cell-integrated (data - comparator), cm^2/nucleon"},
           "comparator_note": "hGenCV2D is mc_truth_denom x w_truth = MINERvA Tune v1 (the OmniFold prior), labelled 'GENIE CV' in the producer",
           "not_exported": "any 2D uncertainty band or rollup (VL162 superseded; VL170 rebuild pending)",
           "cross_checks_report_only": checks}
    man["npz_sha256"] = sha256(a.out)
    Path(str(a.out) + ".manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    print(json.dumps({"out": str(a.out), "npz_sha256": man["npz_sha256"], "checks": checks}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
