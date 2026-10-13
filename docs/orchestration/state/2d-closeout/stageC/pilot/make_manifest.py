#!/usr/bin/env python3
"""Write manifest.json: the sha256 of every file of the pilot package and the external pins it executes or reads.

  python make_manifest.py            (from anywhere; writes manifest.json next to this script)
  python make_manifest.py --check    (exit 1 if manifest.json is stale)

The binding addendum quotes sha256(manifest.json). Package files are every tracked-or-staged file under this
directory except manifest.json itself; the production driver and the XR instrument are hashed from the same
checkout. Large data inputs are listed with the digests the jobs check (sbatch_pilot.sh, analyze_*.py), not
re-hashed here.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           check=True).stdout.strip())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def package_files():
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard",
                        str(HERE.relative_to(ROOT))], capture_output=True, text=True, check=True)
    files = sorted(f for f in r.stdout.split() if not f.endswith("/manifest.json") and "__pycache__" not in f)
    return {f: sha(ROOT / f) for f in files}


def build():
    code = {f: sha(ROOT / f) for f in ("2d-unfolding/unfold_2d_omnifold_unbinned.py",
                                       "docs/orchestration/state/next-preparation-20261009/xr-linux/xr/xr_compare.py",
                                       "docs/orchestration/state/next-preparation-20261009/xr-linux/xr/manifest/references.json")}
    P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
    ext = {   # role -> {path, sha256}; full paths, never bare file names
        "helper": {"path": f"{P}/unbinned_unfolding/python/omnifold.py",
                   "sha256": "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"},
        "cv_omnifile": {"path": "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/"
                                "runEventLoopOmniFold_MEFHC.root",
                        "sha256": "43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df"},
        "flux_mc_file": {"path": f"{P}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root",
                         "sha256": "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"},
        "flux_universe_file": {"path": f"{P}/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root",
                               "sha256": "5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb"},
        "universe_omnifile": {"path": f"{P}/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root",
                              "sha256": "220c479e (prefix; the full digest is recorded by preflight_uomni.sh)"},
        "L0_reference": {"path": "/pscratch/sd/j/josephrb/xr-linux-20261011/L0/a1/XR-L0.root",
                         "sha256": "751380245dbb27f67616ade8321d73274e0a5c0bb1344275fc3b67db2595aecc"},
        "E_U": {"path": f"{P}/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
                "sha256": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"},
        "ml_covariance": {"path": f"{P}/2d-unfolding/uq/seedscan_lgbm_ml/uq_covariance_ml.root",
                          "sha256": "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"},
        "active_files": {"path": "/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/"
                                 "active_universe_5d_standard_merged/SHA256SUMS",
                         "sha256": "per file in that list (= stageB/diagnostics/copy/SHA256SUMS.active.src)"},
        "july_products": {"path": f"{P}/2d-unfolding/uq/purity_newomni/",
                          "sha256": "per file in analyze_pilot.py PIN and p2g2/select_flux.json"},
    }
    return {"schema": "stagec-pilot-manifest/1", "package": package_files(), "code_outside_package": code,
            "external_pins": ext}


def main():
    m = build()
    text = json.dumps(m, indent=1, sort_keys=True) + "\n"
    out = HERE / "manifest.json"
    if "--check" in sys.argv:
        ok = out.is_file() and out.read_text() == text
        print("manifest.json", "OK" if ok else "STALE")
        return 0 if ok else 1
    out.write_text(text)
    print(f"wrote {out} sha256 {sha(out)} ({len(m['package'])} package files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
