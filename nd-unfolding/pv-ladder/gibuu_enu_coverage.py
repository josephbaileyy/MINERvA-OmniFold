#!/usr/bin/env python3
"""GiBUU's E_nu coverage against the analysis flux, per p_parallel range (H2-DEFINITION-DECLARATION addendum A1).

GiBUU 2019's sample stops at E_nu = 20 GeV (KNOWN_ISSUES 82). For two generators that cover E_nu up to 50 GeV, this
gives the share of the flux-averaged in-phase-space CC cross section that comes from E_nu > 20 GeV, per truth p_parallel
range: that share is what GiBUU cannot contain there. The events and weights are the flux repair's own
(s5p gen5d_fluxfix/code/gen5d_flux_reweight.py, KNOWN_ISSUES 83): per-event r(E) = (phi_t / Phi_t) / phi_s, times
NuWro's event weight; in phase space by the analysis rectangle and theta_mu < 20 degrees, as gen_to_xsec5d selects.

Run on Perlmutter after `source setup_salloc_env.sh` (ROOT reads the samples). Simulation only.

MEASURES: generator samples. CANNOT AUTHORIZE: any GiBUU domain or comparison.
"""
import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PZ_RANGES = ((1.5, 4.5), (4.5, 6.0), (6.0, 10.0), (10.0, 20.0), (20.0, 60.0))
E_CUT = 20.0


def shares(pz, E, w):
    out = []
    for lo, hi in PZ_RANGES:
        m = (pz >= lo) & ((pz < hi) | ((hi == 60.0) & (pz <= hi)))
        tot = float(w[m].sum())
        out.append({"pz": [lo, hi], "share_E_gt_20": float(w[m & (E > E_CUT)].sum()) / tot if tot > 0 else None,
                    "share_of_in_ps": tot / float(w.sum()), "n_events": int(m.sum())})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fluxfix-code", default=f"{S5P}/gen5d_fluxfix/code")
    ap.add_argument("--fluxfix-dir", default=f"{S5P}/gen5d_fluxfix")
    ap.add_argument("--gen5d-dir", default=f"{S5P}/gen5d")
    ap.add_argument("--genie-dir", default=f"{REPO}/3d-unfolding/genie")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    sys.path.insert(0, a.fluxfix_code)
    import gen5d_flux_reweight as F

    ROOT = F.import_root()
    g5 = F.load_g5(os.path.join(a.gen5d_dir, "code", "tree"))
    E5 = g5.EDGES
    PT, PZ = E5["pt"], E5["pz"]
    z, _, phit_path = F.load_phi_t(a.fluxfix_dir)
    edges_t, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    out = {"schema": "gibuu-enu-coverage/1", "e_cut_gev": E_CUT, "inputs": [F.file_record(phit_path, "phi_t")],
           "code": {"gibuu_enu_coverage.py": F.sha256(__file__), "gen5d_flux_reweight.py": F.sha256(F.__file__)},
           "generators": {}}
    for gen in ("genie_cv", "nuwro"):
        lo, hi = F.GEN_RANGE[gen]
        if gen == "genie_cv":
            gst = os.path.join(a.genie_dir, "genie_mefhc_cv_ALL.gst.root")
            flux = os.path.join(a.genie_dir, "flux_mefhc_numu.root")
            d = ROOT.RDataFrame("gst", gst).AsNumpy(["cc", "Ev", "pxl", "pyl", "pzl"])
            cc = d["cc"].astype(bool)
            pt, pz, E, w0 = np.hypot(d["pxl"], d["pyl"]), d["pzl"], d["Ev"], np.ones(cc.size)
            out["inputs"] += [F.file_record(gst, "GENIE CV events"), F.file_record(flux, "generation flux")]
        else:
            files = sorted(glob.glob(os.path.join(a.gen5d_dir, "nuwro_flat5d", "nuwro_flat5d_p*.root")))
            flux = os.path.join(a.genie_dir, "flux_mefhc_numu_nuwro.root")
            acc = {k: [] for k in ("cc", "pt", "pz", "Enu", "weight")}
            for fn in files:
                dd = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(list(acc))
                for k in acc:
                    acc[k].append(dd[k])
            d = {k: np.concatenate(v) for k, v in acc.items()}
            cc = d["cc"].astype(bool)
            pt, pz, E, w0 = d["pt"], d["pz"], d["Enu"], d["weight"].astype(float)
            out["inputs"] += [F.file_record(p, "NuWro events") for p in files] + [F.file_record(flux, "generation flux")]
        e_s, c_s = F.read_th1(ROOT, flux, "flux_numu")
        if not np.allclose(e_s, edges_t):
            raise SystemExit(f"[FAIL] {gen}: generation-flux edges differ from phi_t's")
        _, rbin, rng = F.flux_weights(e_s, c_s, phi_t, Phi_t, lo, hi)
        r = F.r_of(E, e_s, rbin, rng)
        with np.errstate(invalid="ignore"):
            inps = (cc & np.isfinite(pt) & np.isfinite(pz) & (pt >= PT[0]) & (pt <= PT[-1]) & (pz >= PZ[0])
                    & (pz <= PZ[-1]) & (np.arctan2(pt, pz) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
        w = (w0 * r)[inps]
        rec = {"n_in_ps": int(inps.sum()), "generation_range_gev": [lo, hi],
               "share_E_gt_20_all_in_ps": float(w[E[inps] > E_CUT].sum() / w.sum()),
               "by_pz": shares(np.asarray(pz[inps], float), np.asarray(E[inps], float), w)}
        out["generators"][gen] = rec
        print(f"[cov] {gen}: {rec['n_in_ps']} in-PS events; E>20 share overall {100 * rec['share_E_gt_20_all_in_ps']:.2f} %")
        for b in rec["by_pz"]:
            print(f"[cov]   p_par {b['pz'][0]:g}-{b['pz'][1]:g}: E>20 share {100 * b['share_E_gt_20']:.2f} % "
                  f"({100 * b['share_of_in_ps']:.1f} % of in-PS sigma, {b['n_events']} events)")
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
