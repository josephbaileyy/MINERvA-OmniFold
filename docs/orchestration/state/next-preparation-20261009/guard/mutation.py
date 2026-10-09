#!/usr/bin/env python3
"""Negative controls: each mutant must turn the named tests red, each in a fresh scratch clone.

    python3 mutation.py <repo> <scratch-dir> <out.json> [--root-python PY] [--only NAME ...]

A clone (``git clone --shared``) of ``<repo>``'s HEAD is made per mutant, the mutation is applied by
an exact, once-only text replacement (or by adding a file), and the named tests are run there. The
mutant is CAUGHT when the run exits non-zero and every expected test is reported FAIL or ERROR. The
unmutated clone is run first with the same commands, and must pass, so a red result cannot come
from the environment. Nothing here touches ``<repo>``.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOTED = "nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py"
FAILOPEN = "nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py"
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
TOY = "2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py"
KI85 = "2d-unfolding/uq/coverage_fixed_truth/ki85_compare.py"
CANON = "/" + "/".join(("pscratch", "sd", "j", "josephrb", "MINERvA-OmniFold"))

R_FWD = "nd-unfolding.tests.test_oi136_rooted_insert_ratchet.TheCanonicalRootMustNotReachPositionZero.test_no_file_outside_the_named_set_feeds_a_rooted_insert"
F_INV = "nd-unfolding.tests.test_oi136_failopen_inventory_ratchet.TheInventoryIsARatchet.test_the_fail_open_set_is_EXACTLY_the_recorded_one"
P = "test_producer_provenance"
H = "test_n2_harness"

RATCHETS = ("plain", ["-m", "unittest", R_FWD, F_INV])


def n2_tests(*names, root=False):
    return ("root" if root else "plain",
            ["-m", "unittest", *names], N2)


MUTANTS = [
    # name, edits [(path, old, new)] or [(path, None, content)], (interpreter, argv[, cwd]), expected
    ("new-tracked-live-site",
     [("2d-unfolding/uq/new_live_site.py", None,
       f'import sys\n_ROOT = "{CANON}"\nsys.path.insert(0, _ROOT + "/2d-unfolding/uq")\n')],
     RATCHETS, [R_FWD.rsplit(".", 1)[1], F_INV.rsplit(".", 1)[1]], True),
    ("new-untracked-live-site",
     [("2d-unfolding/uq/new_live_site.py", None,
       f'import sys\n_ROOT = "{CANON}"\nsys.path.insert(0, _ROOT + "/2d-unfolding/uq")\n')],
     RATCHETS, [F_INV.rsplit(".", 1)[1]], False),
    # The defect's original spelling: a string literal (both instruments see it).
    ("toy-literal-replanted",
     [(TOY, 'OMNIFOLD_PY = REPO / "unbinned_unfolding" / "python"',
       f'OMNIFOLD_PY = "{CANON}/unbinned_unfolding/python"')],
     RATCHETS, [R_FWD.rsplit(".", 1)[1], F_INV.rsplit(".", 1)[1]], True),
    ("ki85-literal-replanted",
     [(KI85, "UQ = HERE.parent ", f'UQ = "{CANON}/2d-unfolding/uq" ')],
     RATCHETS, [R_FWD.rsplit(".", 1)[1], F_INV.rsplit(".", 1)[1]], True),
    # A pathlib spelling: the AST ratchet sees it, the probe's regex does not (the known
    # gate2_target_runtime.py shape). Expected red is the AST arm only; the record shows the probe.
    ("toy-literal-replanted-as-path",
     [(TOY, 'OMNIFOLD_PY = REPO / "unbinned_unfolding" / "python"',
       f'OMNIFOLD_PY = Path("{CANON}/unbinned_unfolding/python")')],
     RATCHETS, [R_FWD.rsplit(".", 1)[1]], True),
    ("loader-accepts-pre-imported",
     [(f"{N2}/execution.py", "    existing = sys.modules.get(name)\n",
       "    existing = None\n")],
     n2_tests(f"{P}.TheLoader", f"{P}.TheKi85Producer", f"{P}.TheToyProducer", root=True),
     ["test_refuses_a_module_imported_by_anything_else",
      "test_a_pre_imported_analyzer_from_another_checkout_refuses",
      "test_a_pre_imported_helper_from_another_checkout_refuses_before_output"], True),
    ("loader-skips-digest",
     [(f"{N2}/execution.py", "    if expect_sha256 is not None and record[\"sha256\"] != expect_sha256:",
       "    if False:")],
     n2_tests(f"{P}.TheLoader", f"{P}.TheKi85Producer", f"{P}.TheToyProducer", root=True),
     ["test_refuses_a_digest_mismatch_without_executing",
      "test_a_changed_analyzer_refuses_before_its_body_runs",
      "test_changed_helper_bytes_refuse_before_the_helper_runs"], True),
    ("strict-skips-guard",
     [(f"{N2}/execution.py", "        require_guard(root, guard)\n", "        pass\n")],
     n2_tests(f"{P}.TheKi85Producer", f"{P}.TheToyProducer", root=True),
     ["test_strict_mode_refuses_unguarded", "test_strict_mode_refuses_missing_provenance"], True),
    ("strict-ignores-head-drift",
     [(f"{N2}/execution.py", "        if ident[\"mismatched\"]:", "        if False:")],
     n2_tests(f"{P}.TheToyProducer", root=True),
     ["test_strict_mode_refuses_a_committed_helper_edited_since_head"], True),
    ("output-overwrite-allowed",
     [(f"{N2}/execution.py", "    if os.path.lexists(path):", "    if False:")],
     n2_tests(f"{P}.TheToyProducer", root=True),
     ["test_strict_mode_refuses_to_overwrite_and_leaves_the_file_untouched"], True),
    ("ids-allow-duplicates",
     [(f"{N2}/identity.py", "    if len(set(out)) != len(out):", "    if False:")],
     n2_tests(f"{H}.Identity"), ["test_a_repeated_identity_is_a_stop_condition"], True),
    ("ids-allow-missing",
     [(f"{N2}/identity.py", "    missing = [c for c in KEY if c not in table]\n",
       "    missing = []\n"),
      (f"{N2}/identity.py", "    for i, row in enumerate(zip(*(table[c] for c in KEY))):",
       "    for i, row in enumerate(zip(*(table[c] for c in KEY if c in table))):"),
      (f"{N2}/identity.py", "        if source is None or str(source) == \"\" or any(",
       "        if False and any(")],
     n2_tests(f"{H}.Identity"), ["test_missing_ids_are_refused"], True),
    ("c1-disabled",
     [(f"{N2}/identity.py", "            if both:\n                raise IdentityError(f\"C1",
       "            if False:\n                raise IdentityError(f\"C1")],
     n2_tests(f"{H}.Identity"), ["test_c1_fires_when_a_reservoir_key_is_moved_into_training"],
     True),
    ("c6-disabled",
     [(f"{N2}/identity.py", "        if stray:", "        if False:")],
     n2_tests(f"{H}.Identity.test_c6_fires_on_a_reservoir_row_in_the_bank",
              f"{H}.Harness.test_failed_contaminated_and_missing_members_are_reported_not_dropped"),
     ["test_c6_fires_on_a_reservoir_row_in_the_bank",
      "test_failed_contaminated_and_missing_members_are_reported_not_dropped"], True),
    ("ledger-drops-missing",
     [(f"{N2}/members.py", "            out.append((m, \"missing\", None))\n", "")],
     n2_tests(f"{H}.Members",
              f"{H}.Harness.test_failed_contaminated_and_missing_members_are_reported_not_dropped"),
     ["test_the_ledger_keeps_every_declared_member",
      "test_failed_contaminated_and_missing_members_are_reported_not_dropped"], True),
    ("write-new-overwrites",
     [(f"{N2}/members.py", "            os.link(tmp, path)", "            os.replace(tmp, path); open(tmp, 'w').close()")],
     n2_tests(f"{H}.Members"), ["test_write_new_never_overwrites"], True),
    ("mc-stream-resampled",
     [(f"{N2}/design.py",
       '"B": {"data_stream": "bootstrap: data-only Poisson(1) per row of the base pseudo-data",\n'
       '                 "mc_stream": "held"}',
       '"B": {"data_stream": "bootstrap: data-only Poisson(1) per row of the base pseudo-data",\n'
       '                 "mc_stream": "bootstrap"}')],
     n2_tests(f"{H}.Design"), ["test_the_plan_streams_seeds_and_estimator"], True),
    ("real-admission-without-authorization",
     [(f"{N2}/harness.py", "    if adm.get(\"synthetic\") is False:\n        need.append(\"authorization\")\n", ""),
      (f"{N2}/harness.py", "    if not adm[\"synthetic\"]:\n        auth = Path(root)",
       "    if False:\n        auth = Path(root)")],
     n2_tests(f"{H}.Harness.test_no_or_incomplete_admission_refuses_a_launch"),
     ["test_no_or_incomplete_admission_refuses_a_launch"], True),
]


def clone(repo, dest):
    if dest.exists():
        shutil.rmtree(dest)
    subprocess.run(["git", "clone", "-q", "--shared", str(repo), str(dest)], check=True)
    return dest


def apply(root, edits, track):
    for path, old, new in edits:
        f = root / path
        if old is None:
            f.write_text(new)
            if track:
                subprocess.run(["git", "-C", str(root), "add", path], check=True)
            continue
        text = f.read_text()
        if text.count(old) != 1:
            raise SystemExit(f"mutation anchor not found exactly once in {path}: {old[:60]!r}")
        f.write_text(text.replace(old, new))


def run(root, spec, pythons):
    kind, argv = spec[0], spec[1]
    cwd = root / spec[2] if len(spec) > 2 else root
    env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    if kind == "root":
        env["PYTHONPATH"] = pythons["root_libdir"]
    t0 = time.time()
    cp = subprocess.run([pythons[kind], *argv], cwd=cwd, capture_output=True, text=True, env=env)
    text = cp.stdout + cp.stderr
    red = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\w+)", text, re.M)))
    ran = re.search(r"^Ran (\d+) tests?", text, re.M)
    skipped = re.search(r"skipped=(\d+)", text)
    return {"exit": cp.returncode, "red": red, "ran": int(ran.group(1)) if ran else None,
            "skipped": int(skipped.group(1)) if skipped else 0, "wall_s": round(time.time() - t0, 1),
            "tail": text[-1500:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("scratch")
    ap.add_argument("out")
    ap.add_argument("--root-python", default="python3.13")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    libdir = subprocess.run(["root-config", "--libdir"], capture_output=True, text=True).stdout.strip()
    pythons = {"plain": sys.executable, "root": a.root_python, "root_libdir": libdir}
    repo, scratch = Path(a.repo).resolve(), Path(a.scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    results = {"repo_head": head, "mutants": []}
    chosen = [m for m in MUTANTS if not a.only or m[0] in a.only]
    specs = {json.dumps(m[2]): m[2] for m in chosen}
    base = clone(repo, scratch / "unmutated")
    results["unmutated"] = {k: run(base, s, pythons) for k, s in specs.items()}
    for k, r in results["unmutated"].items():
        print(f"[unmutated] {k[:70]} exit={r['exit']} ran={r['ran']} skipped={r['skipped']}")
    shutil.rmtree(base)
    for name, edits, spec, expected, track in chosen:
        root = clone(repo, scratch / name)
        apply(root, edits, track)
        r = run(root, spec, pythons)
        caught = r["exit"] != 0 and all(e in r["red"] for e in expected)
        results["mutants"].append({"name": name, "expected_red": expected, "caught": caught, **r})
        print(f"[{'CAUGHT' if caught else 'MISSED'}] {name}: exit={r['exit']} red={r['red']} "
              f"ran={r['ran']} {r['wall_s']}s")
        shutil.rmtree(root)
    results["all_caught"] = all(m["caught"] for m in results["mutants"])
    results["unmutated_all_green"] = all(r["exit"] == 0 for r in results["unmutated"].values())
    Path(a.out).write_text(json.dumps(results, indent=1) + "\n")
    print(f"unmutated all green: {results['unmutated_all_green']}; "
          f"all mutants caught: {results['all_caught']}")
    return 0 if results["all_caught"] and results["unmutated_all_green"] else 1


if __name__ == "__main__":
    sys.exit(main())
