"""Mutation controls for the XR package: each mutant must turn its targeted test red.

Each mutant edits one package file in place, runs the named tests, and restores the file, whose
sha256 is verified after every mutant. Run from this directory with the same interpreter and
PYTHONPATH as the suite:

    PYTHONPATH=$(root-config --libdir) python3.13 mutation.py --out mutation-results.json
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent

MUTANTS = [
    ("overwrite-allowed", "xr_run.py", "        gx.reserve_output(str(out))\n", "        pass\n",
     ["test_xr.XR.test_an_existing_output_is_never_overwritten"]),
    ("symlink-allowed", "xr_run.py", "    if str(real) != os.path.normpath(str(p)):\n",
     "    if False:\n", ["test_xr.XR.test_a_symlinked_attempt_directory_is_refused"]),
    ("frozen-path-allowed", "xr_run.py", "    if str(real) in frozen_paths(refs):\n", "    if False:\n",
     ["test_xr.XR.test_an_output_that_is_a_frozen_reference_path_is_refused"]),
    ("checkout-outroot-allowed", "xr_run.py", "    for root in (Path(repo).resolve(), Path(CANONICAL), *map(Path, extra_forbidden)):\n",
     "    for root in ():\n", ["test_xr.XR.test_an_outroot_inside_the_checkout_is_refused"]),
    ("seed-unchecked", "xr_run.py", "                if seed != want:\n", "                if False:\n",
     ["test_xr.XR.test_a_wrong_seed_stops_before_training"]),
    ("class-unchecked", "xr_run.py", "                if _name not in self.want:\n", "                if False:\n",
     ["test_xr.XR.test_a_backend_other_than_the_frozen_one_stops_before_training"]),
    ("normalization-unchecked", "xr_run.py", "    if bad:\n        raise BackendRefusal(f\"normalization", "    if False:\n        raise BackendRefusal(f\"normalization",
     ["test_xr.XR.test_a_normalization_differing_from_the_reference_is_refused"]),
    ("driver-pin-unchecked", "xr_run.py", "    if rec[\"sha256\"] != run[\"driver_digest\"]:\n", "    if False:\n",
     ["test_xr.XR.test_a_changed_driver_or_helper_is_refused"]),
    ("input-digest-unchecked", "xr_run.py", "            if digest != spec[\"sha256\"] or st[\"size\"] != spec[\"size\"]:\n",
     "            if False:\n", ["test_xr.XR.test_an_input_with_other_bytes_is_refused"]),
    ("cwd-unchecked", "xr_run.py", "        if Path.cwd().resolve() != REPO / \"2d-unfolding\":\n", "        if False:\n",
     ["test_xr.XR.test_the_wrong_working_directory_is_refused"]),
    ("no-loky-seed", "xr_run.py", "        receipt[\"cpu_count\"] = seed_loky_cache()\n", "        pass\n",
     ["test_xr.XR.test_lightgbm_ran_with_a_child_free_core_count"]),
    ("abbreviated-commit-accepted", "xr_admit.py", "    if not re.fullmatch(r\"[0-9a-f]{40}\", package_commit or \"\"):\n",
     "    if False:\n", ["test_xr.XR.test_the_authorization_binding"]),
    ("package-drift-accepted", "xr_admit.py", "    if changed:\n        raise Refusal(f\"the package changed after", "    if False:\n        raise Refusal(f\"the package changed after",
     ["test_xr.XR.test_a_package_change_after_the_package_commit_is_refused"]),
    ("attempt-cap-off-by-one", "xr_admit.py", "    if used + 1 > runs[\"kinds\"][kind_name][\"max_attempts_total\"]:\n",
     "    if used + 1 > runs[\"kinds\"][kind_name][\"max_attempts_total\"] + 1:\n",
     ["test_xr.XR.test_submit_counts_attempts_per_kind_and_cancels_on_a_failed_sbatch"]),
    ("billing-unchecked", "xr_admit.py", "              \"billing\": billing is not None and billing <= kind[\"billing_max\"],\n",
     "              \"billing\": True,\n", ["test_xr.XR.test_jobcheck_refuses_an_allocation_outside_the_caps"]),
    ("ledger-billing-unflagged", "xr_admit.py", "    return OVER if over or any(\"billing\" in r and \">\" in r for r in report) else 0\n",
     "    return OVER if over else 0\n", ["test_xr.XR.test_ledger_charges_and_flags"]),
    ("loose-tolerance", "xr_compare.py", "TOL = 1e-8\n", "TOL = 1e-7\n",
     ["test_xr.Comparator.test_tolerance_cells_and_digests"]),
    ("cell-identity-unchecked", "xr_compare.py", "    if gid(xn) != cells or gid(xr) != cells:\n", "    if False:\n",
     ["test_xr.Comparator.test_tolerance_cells_and_digests"]),
    ("submit-no-cancel", "launch/xr_submit.sh", "on_error() { for j in \"${QUEUED[@]}\"; do scancel \"$j\" || true; done;",
     "on_error() { for j in; do scancel \"$j\" || true; done;",
     ["test_xr.XR.test_submit_counts_attempts_per_kind_and_cancels_on_a_failed_sbatch"]),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*", help="run only these mutants")
    a = ap.parse_args()
    results = []
    for name, rel, old, new, tests in MUTANTS:
        if a.only and name not in a.only:
            continue
        path = PKG / rel
        before = path.read_bytes()
        digest = sha(path)
        text = before.decode()
        if text.count(old) != 1:
            results.append({"mutant": name, "status": "ANCHOR-NOT-UNIQUE", "count": text.count(old)})
            continue
        try:
            path.write_text(text.replace(old, new))
            r = subprocess.run([sys.executable, "-m", "unittest", *tests], cwd=HERE, capture_output=True, text=True,
                               env=dict(os.environ, OMP_NUM_THREADS="1"))
            caught = r.returncode != 0
            results.append({"mutant": name, "file": rel, "tests": tests, "caught": caught,
                            "tail": r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""})
        finally:
            path.write_bytes(before)
            assert sha(path) == digest, f"restore failed for {rel}"
        print(f"{name}: {'caught' if caught else 'NOT CAUGHT'}", flush=True)
    out = {"n": len(results), "caught": sum(1 for r in results if r.get("caught")), "results": results}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['caught']} of {out['n']} caught")
    return 0 if out["caught"] == out["n"] else 1


if __name__ == "__main__":
    sys.exit(main())
