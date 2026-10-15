#!/usr/bin/env python3
"""Write manifest.json: the sha256 of every file of the production package, of the code outside it that the package
executes or imports, and the external pins it reads. Adapted from the pilot's make_manifest.py.

  python make_manifest.py            (from anywhere; writes manifest.json next to this script)
  python make_manifest.py --check    (exit 1 if manifest.json is stale)

The binding addendum names sha256(manifest.json). Package files are every tracked-or-staged file under this
directory except manifest.json itself. Large data inputs are listed with the digests the jobs and analyses check
(sbatch_prod.sh, analyze_prod.py, s5_rollup.py), not re-hashed here.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           check=True).stdout.strip())
ST = "docs/orchestration/state/2d-closeout"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def package_files():
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard",
                        str(HERE.relative_to(ROOT))], capture_output=True, text=True, check=True)
    files = sorted(f for f in r.stdout.split() if not f.endswith("/manifest.json") and "__pycache__" not in f)
    return {f: sha(ROOT / f) for f in files}


def build():
    code = {f: sha(ROOT / f) for f in (
        "2d-unfolding/unfold_2d_omnifold_unbinned.py",                       # production driver (jobs)
        f"{ST}/stageC/pilot/p1/driver_p1.py",                                 # three-stream copy (jobs)
        f"{ST}/stageC/pilot/analyze_pilot.py",                                # imported by analyze_prod.py
        f"{ST}/stageC/pilot/p1/analyze_p1.py",                                # imported by analyze_prod.py
        f"{ST}/stageC/pilot/evidence/SHA256SUMS.pscratch",                    # pilot reproduction references
        f"{ST}/c04-repair/scripts/build_repair.py",                           # imported by s5_rollup.py
        f"{ST}/stageB/evidence/b-genie-truth/sweeps.json",                    # July and May per-file digests
        "docs/orchestration/state/next-preparation-20261009/xr-linux/xr/xr_compare.py",
        "docs/orchestration/state/next-preparation-20261009/xr-linux/xr/manifest/references.json")}
    P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
    C04 = "/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build"
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
                              "sha256": "220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418"},
        "active_files_sums": {"path": "/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/"
                                      "active_universe_5d_standard_merged/SHA256SUMS",
                              "sha256": "73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6"},
        "L0_reference": {"path": "/pscratch/sd/j/josephrb/xr-linux-20261011/L0/a1/XR-L0.root",
                         "sha256": "751380245dbb27f67616ade8321d73274e0a5c0bb1344275fc3b67db2595aecc"},
        "E_U": {"path": f"{P}/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
                "sha256": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"},
        "ml_covariance": {"path": f"{P}/2d-unfolding/uq/seedscan_lgbm_ml/uq_covariance_ml.root",
                          "sha256": "3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9"},
        "vl175_rollup": {"path": f"{C04}/uq_universe_covariance_c04x01.root",
                         "sha256": "da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948"},
        "vl175_build_json": {"path": f"{C04}/build.json",
                             "sha256": "dcc1331e8e510cc21a2abd95675cfc69acf92bae7ae3dfa43a3a94b9fdbe34dd"},
        "vl175_minos_npz": {"path": f"{C04}/minos_rescaled.npz",
                            "sha256": "8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d"},
        "vl175_budget": {"path": f"{C04}/budget.json",
                         "sha256": "aab8a24ebd61df54e7277999d49300c3bdaa045710835bfa05adf3bfc71dd8fa"},
        "constraint": {"path": f"{P}/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/"
                               "sorted_NuEConstraint_FHC_RHC_IMD.txt",
                       "sha256": "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"},
        "july_products": {"path": f"{P}/2d-unfolding/uq/purity_newomni/",
                          "sha256": "per file in stageB/evidence/b-genie-truth/sweeps.json ('pn/')"},
        "may_products": {"path": f"{P}/2d-unfolding/uq/universe_sweep_fluxfix/",
                         "sha256": "per file in stageB/evidence/b-genie-truth/sweeps.json ('may/'); S5 control only"},
        "pilot_outputs": {"path": "/pscratch/sd/j/josephrb/2d-closeout-stageC-pilot-20261013/out/",
                          "sha256": "per file in stageC/pilot/evidence/SHA256SUMS.pscratch"},
    }
    return {"schema": "stagec-production-manifest/1", "package": package_files(), "code_outside_package": code,
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
