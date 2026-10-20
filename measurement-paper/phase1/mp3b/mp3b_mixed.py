#!/usr/bin/env python3
"""MP3-B variant (C), ruled by the director after the 60022605 abort:
"mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH".

  x_mixed = (12/13) x_NuWro,C12 (the frozen nuwro_cv_xsec5d_full.npz arrays, rebuilt bitwise as B2 first)
          + (1/13) x_GENIE,H     (per H nucleon = 13 x the tgt == 2212 part of the frozen GENIE CV CH prediction,
                                  as MP3-A split it: mp3a_fine_genie_cv.npz, whose split adds up to the frozen
                                  product and whose carbon part x 13/12 is per C12 nucleon)
  sumw2_mixed = (12/13)^2 sumw2_NuWro,C12 + (1/13)^2 13^2 sumw2_GENIE,H1

The same formula as (A); only the hydrogen source differs. Writes mp3b_fine_mixed.npz with the keys mp3b_eval.py
reads, plus the product in gen5d npz format. Usage (root_6_28): python3 mp3b_mixed.py --out OUT
Exit codes: 0 written; 3 a control (B2, or the MP3-A input's integrity) failed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import mp3b_build as b  # noqa: E402

LABEL = "mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH"
MP3A_FINE = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3a/out/build/mp3a_fine_genie_cv.npz"
MP3A_FINE_SHA256 = "f2599b71d90d34242379834edca2ef83f310d1a88a82445339bf4bb04fdafe2d"   # mp3a/out_sha256.txt
GENIE_CV_FULL = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=False)
    ROOT = b.gfr.import_root()
    g5 = b.gfr.load_g5(b.gfr.DEFAULTS["gen5d_tree"])
    res = {"schema": "mp3b-mixed/1", "label": LABEL, "argv": sys.argv, "environment": b.gfr.environment(),
           "code": {m.__name__: {"file": str(Path(m.__file__).resolve()), "sha256": b.sha256(Path(m.__file__).resolve())}
                    for m in (sys.modules[__name__], b, b.gfr, b.sup, g5)}}

    def finish(code, msg):
        res.update(verdict=msg, exit_code=code)
        (a.out / "mp3b_mixed.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
        print(msg, flush=True)
        return code

    z, _, _ = b.gfr.load_phi_t(b.FLUXFIX)
    b2, c12, _, full_meta = b.rebuild_c12(ROOT, g5, z)
    res["B2_C12_rebuild"] = {k: b2[k] for k in ("main", "full", "full_from_rebuilt_main", "pass")}
    print("B2", json.dumps({"pass": b2["pass"]}), flush=True)
    if not b2["pass"]:
        return finish(3, "STOP: the NuWro C12 rebuild is not bitwise; no mixed prediction")
    sha = b.sha256(MP3A_FINE)
    zg = np.load(MP3A_FINE)
    gfull = np.load(GENIE_CV_FULL, allow_pickle=True)
    split = zg["xsec_C12"] + zg["xsec_H1"] + zg["xsec_other"]
    nz = gfull["xsec_flat"] != 0
    ctrl = {"mp3a_fine_sha256": sha, "matches_mp3a_receipt": sha == MP3A_FINE_SHA256,
            "mp3a_frozen_CH_equals_genie_cv_full": bool(np.array_equal(zg["xsec_CH_frozen"], gfull["xsec_flat"])),
            "split_closure_max_rel": float(np.max(np.abs(split[nz] - gfull["xsec_flat"][nz]) / gfull["xsec_flat"][nz])),
            "genie_cv_full_sha256": b.sha256(GENIE_CV_FULL)}
    res["controls"] = ctrl
    print("CONTROLS", json.dumps(ctrl), flush=True)
    if not (ctrl["matches_mp3a_receipt"] and ctrl["mp3a_frozen_CH_equals_genie_cv_full"] and ctrl["split_closure_max_rel"] < 1e-12):
        return finish(3, "STOP: the MP3-A GENIE split does not match its receipt or the frozen product")
    x_h = 13.0 * zg["xsec_H1"]
    v_h = 169.0 * zg["sumw2_H1"]
    n_h = zg["nevt_H1"]
    x_ch = b.F_C * c12["xsec_C12_frozen"] + b.F_H * x_h
    v_ch = b.F_C ** 2 * c12["sumw2_C12_frozen"] + b.F_H ** 2 * v_h
    n_ch = c12["nevt_C12_frozen"] + n_h
    np.savez_compressed(a.out / "mp3b_fine_mixed.npz", **c12, xsec_H=x_h, sumw2_H=v_h, nevt_H=n_h,
                        xsec_CH=x_ch, sumw2_CH=v_ch, nevt_CH=n_ch, label=np.asarray(LABEL))
    meta = {"generator": "mixed_NuWroC12_GENIEH", "label": LABEL,
            "quantity": "dsigma per CH nucleon = (12/13) NuWro C12 (frozen) + (1/13) GENIE 2.12.10 CV H (per H nucleon)",
            "composition": f"(12/13) x {b.FROZEN_FULL} + (1/13) x 13 x xsec_H1 of {MP3A_FINE}",
            "axes": list(g5.AXES), "shape": list(g5.SHAPE), "edges": {ax: g5.EDGES[ax].tolist() for ax in g5.AXES},
            "phase_space": full_meta["phase_space"], "definitions": full_meta["definitions"], "code": res["code"]}
    np.savez(a.out / "mixed_NuWroC12_GENIEH_xsec5d_full.npz", xsec_flat=x_ch, sumw2_flat=v_ch, nevt_flat=n_ch,
             n_events=np.int64(n_ch.sum()), **{f"edges_{ax}": g5.EDGES[ax] for ax in g5.AXES},
             shape=np.asarray(g5.SHAPE), meta_json=np.asarray(json.dumps(meta)))
    vol = g5.widths(*g5.AXES).reshape(-1)
    res["integrated"] = {"sigma_in_grid_GENIE_H_per_H_nucleon_cm2": float(x_h @ vol),
                         "sigma_in_grid_NuWro_C12_per_nucleon_cm2": float(c12["xsec_C12_frozen"] @ vol),
                         "f_H_in_grid": float(b.F_H * (x_h @ vol) / (x_ch @ vol))}
    res["products"] = {p: b.sha256(a.out / p) for p in ("mp3b_fine_mixed.npz", "mixed_NuWroC12_GENIEH_xsec5d_full.npz")}
    return finish(0, "MIXED written: " + LABEL)


if __name__ == "__main__":
    raise SystemExit(main())
