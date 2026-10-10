#!/usr/bin/env python3
"""Mutation controls for the SB1 package: each guard must turn its targeted test red.

    PYTHONPATH=$(root-config --libdir) python3.13 checks/mutation.py COMMIT OUT.json

Clones COMMIT with ``git clone --shared`` into a temporary directory, runs every targeted test on
the unmutated clone first (all must pass, no skips), then applies one source substitution at a
time (each must occur exactly once), runs its targeted tests, records the outcome and restores the
file. A mutant counts as caught when a targeted test fails, errors or crashes the interpreter.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PKG = "docs/orchestration/state/next-preparation-20261009/sb1-prep"
BS, RUN, VER, ADM = (f"{PKG}/branch_select.py", f"{PKG}/sb1_run.py", f"{PKG}/sb1_verify.py",
                     f"{PKG}/sb1_admit.py")
T_BS = "test_branch_select"
T_G = "test_sb1_guarded"
T_C = "test_launch_chain"
MUTANTS = [
    ("restore-addresses-dropped", BS, "        restore_addresses(tree, addresses)\n", "",
     T_BS, "test_a_reused_tree_is_restored_and_reads_identically_afterwards"),
    ("inactive-address-allowed", BS, "        if not self._tree.GetBranchStatus(name):\n",
     "        if False:\n", T_BS, "test_every_omitted_activation_is_refused_before_the_first_read"),
    ("active-set-unchecked", BS, "        if sorted(active_names(tree)) != want:\n",
     "        if False:\n", T_BS, "test_an_extra_activation_is_refused_before_the_first_read"),
    ("rule-unchecked", BS, "    if names != want:\n", "    if False:\n",
     T_BS, "test_a_loader_that_reads_another_branch_is_refused_by_the_rule"),
    ("discovery-forwards-addresses", BS,
     "        self.addressed.append(str(name))\n        return 0\n",
     "        self.addressed.append(str(name))\n        return self._tree.SetBranchAddress(name, buf)\n",
     T_BS, "test_discovery_reads_no_entry_and_leaves_no_address"),
    ("all-arm-entry-unchecked", BS, "    if not all(s for _, s in snap):\n        raise",
     "    if False:\n        raise", T_BS, "test_a_partial_entry_state_is_restored_exactly"),
    ("histogram-not-digested", BS, "    if hist is not None:\n        out[\"histogram\"]",
     "    if False:\n        out[\"histogram\"]", T_BS,
     "test_selective_is_byte_identical_to_the_pinned_loaders"),
    ("reference-not-compared", RUN, "            if reference is not None:\n",
     "            if False:\n", T_G, "test_a_reference_with_different_bytes_stops_before_training"),
    ("input-stat-unchecked", RUN, "            if not all(same.values()):\n",
     "            if False:\n", T_G, "test_an_input_changed_after_hashing_is_refused"),
    ("driver-pin-unchecked", RUN, "    if by_rel.get(DRIVER_REL) != DRIVER_SHA256:\n",
     "    if False:\n", T_G, "test_a_changed_driver_is_refused_even_when_committed_and_stated"),
    ("mib-read-as-1000", VER, '"M": 1024 ** 2', '"M": 1000 ** 2', T_C,
     "test_a_mib_value_is_not_read_as_kib"),
    ("s2-bound-loosened", VER, "sl[\"maxdiskread_bytes\"] <= 10 * GB",
     "sl[\"maxdiskread_bytes\"] <= 12 * GB", T_C, "test_too_many_bytes_read_fails_s2"),
    ("s4-bound-loosened", VER, "sl[\"elapsed_s\"] <= 0.5 * ul[\"elapsed_s\"]",
     "sl[\"elapsed_s\"] <= 0.51 * ul[\"elapsed_s\"]", T_C, "test_slow_selective_arm_fails_s4"),
    ("guard-inventory-unchecked", VER, "    if inv:\n", "    if False:\n", T_C,
     "test_a_guard_record_from_another_root_is_not_a_pass"),
    ("checkout-unchecked", ADM, '    if Path(adm["checkout"]).resolve() != REPO.resolve():\n',
     "    if False:\n", T_C, "test_each_admission_guard_refuses"),
    ("dirty-tree-allowed", ADM, '    if git("status", "--porcelain", "--untracked-files=no").strip():\n',
     "    if False:\n", T_C, "test_a_dirty_tree_is_refused"),
    ("package-binding-unchecked", ADM, "    if changed:\n", "    if False:\n", T_C,
     "test_a_package_changed_after_its_commit_is_refused"),
    ("authorization-text-unchecked", ADM,
     "    if pkg not in auth_text or manifest_sha not in auth_text:\n", "    if False:\n", T_C,
     "test_an_authorization_that_does_not_name_the_package_is_refused"),
    ("input-stat-now-unchecked", ADM,
     '        if stat_of(path) != {k: want[k] for k in ("size", "mtime_ns", "ino")}:\n',
     "        if False:\n", T_C, "test_each_admission_guard_refuses"),
    ("unadmitted-module-allowed", VER, "    if extra:\n", "    if False:\n", T_C,
     "test_an_unadmitted_executed_module_is_not_a_pass"),
    ("partial-receipt-is-difference", VER,
     '            whole = a.get("status") == "complete" and b.get("status") == "complete"\n',
     "            whole = True\n", T_C, "test_a_killed_selective_arm_is_inconclusive_not_fail"),
    ("env-setup-unchecked", VER, "    if len(setups) != 1 or None in setups:\n",
     "    if False:\n", T_C, "test_receipts_from_different_environments_are_not_a_pass"),
    ("nc-ignores-loaders", VER, '              and c.get("loaders") == [])', "              )",
     T_C, "test_a_control_that_returned_a_loader_fails_nc"),
    ("submit-ignores-failed-sbatch", f"{PKG}/launch/sb1_submit.sh",
     '  id="$("${S[@]}" "$@")" || return 1\n  id="${id%%;*}"                       # --parsable prints "id[;cluster]"\n  [[ "${id}" =~ ^[0-9]+$ ]] || return 1\n',
     '  id="$("${S[@]}" "$@")"\n  id="${id%%;*}"\n', T_C,
     "test_a_failed_sbatch_cancels_what_was_queued_and_fails"),
    ("authorization-needs-only-one-value", ADM,
     "    if pkg not in auth_text or manifest_sha not in auth_text:\n",
     "    if pkg not in auth_text and manifest_sha not in auth_text:\n", T_C,
     "test_an_authorization_that_does_not_name_the_package_is_refused"),
    ("proposal-admitted", ADM, '    if adm["status"] != "ADMITTED":\n', "    if False:\n", T_C,
     "test_a_proposal_cannot_be_submitted"),
    ("symlinked-authorization", ADM,
     ' or (top / norm).resolve() != top / norm:\n', ':\n', T_C,
     "test_hostile_authorization_paths_are_refused"),
]


def run_tests(clone, module, names):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1")
    args = [sys.executable, "-m", "unittest", "-v"]
    for n in names:
        args += ["-k", n]
    args.append(module)
    t0 = time.time()
    r = subprocess.run(args, cwd=clone / PKG / "tests", capture_output=True, text=True, env=env)
    tail = [line for line in r.stderr.splitlines() if not line.startswith("[/")][-6:]
    return {"returncode": r.returncode, "seconds": round(time.time() - t0, 1),
            "ran": next((line for line in r.stderr.splitlines() if line.startswith("Ran ")), None),
            "skipped": "skipped" in r.stderr.split("Ran ")[-1] if "Ran " in r.stderr else None,
            "tail": tail}


def main():
    commit, out = sys.argv[1], Path(sys.argv[2])
    repo = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                               text=True, check=True).stdout.strip())
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "clone"
        subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(repo), str(clone)],
                       check=True)
        subprocess.run(["git", "-C", str(clone), "-c", "core.hooksPath=/dev/null", "checkout",
                        "-q", commit], check=True)
        by_module = {}
        for _, _, _, _, module, test in MUTANTS:
            by_module.setdefault(module, []).append(test)
        baseline = {m: run_tests(clone, m, sorted(set(t))) for m, t in by_module.items()}
        results = {"commit": commit, "baseline": baseline, "mutants": []}
        if any(b["returncode"] != 0 or b["skipped"] for b in baseline.values()):
            results["verdict"] = "BASELINE NOT GREEN"
        else:
            for name, rel, old, new, module, test in MUTANTS:
                path = clone / rel
                src = path.read_text()
                n = src.count(old)
                if n != 1:
                    results["mutants"].append({"name": name, "error": f"site occurs {n} times"})
                    continue
                path.write_text(src.replace(old, new))
                try:
                    res = run_tests(clone, module, [test])
                finally:
                    path.write_text(src)
                results["mutants"].append({"name": name, "file": rel, "test": test,
                                           "caught": res["returncode"] != 0, **res})
            caught = sum(m.get("caught", False) for m in results["mutants"])
            results["verdict"] = f"{caught} of {len(MUTANTS)} caught"
    out.write_text(json.dumps(results, indent=1) + "\n")
    print(results["verdict"])
    return 0 if results["verdict"] == f"{len(MUTANTS)} of {len(MUTANTS)} caught" else 1


if __name__ == "__main__":
    sys.exit(main())
