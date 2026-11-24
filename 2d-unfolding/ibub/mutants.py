#!/usr/bin/env python3
"""IBUB's hand mutants. Each one is a single-site change to ``ibub_unit.py`` or ``ibub_readout.py``, applied in place
and run against the tests that should kill it. The file is then restored and its sha256 re-checked; a restore that
does not reproduce the original bytes stops the run.

Before any mutant, every named test set must pass unmutated (the baseline), and every mutant's site must occur exactly
once. A mutant must still compile (``ast.parse`` for Python, ``bash -n`` for the job). It is KILLED only when a named
test fails or errors, and SURVIVES when they all pass. A suite that cannot load (an import failure, a missing test) is
a harness failure, which stops the run rather than counting as a kill. Every mutant must be killed.

    python -B mutants.py PYTHON [--only N]

PYTHON is an interpreter with PyROOT, numpy, scipy, LightGBM and scikit-learn. The results are printed as one TSV line
per mutant (index, verdict, file, tests, what it breaks), then a total line.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
U, R, L, O, J = "ibub_unit.py", "ibub_readout.py", "ibub_lanes.py", "ibub_overlap.py", "jobs/ibub_job.sbatch"
TU, TR, TJ, TO = "test_ibub_unit", "test_ibub_readout", "test_ibub_job", "test_ibub_overlap"

# (file, old, new, tests, what the mutant breaks)
MUTANTS = [
    (U, 'bad = sorted({a.split("=", 1)[0] for a in argv} & set(cfg["g2r_forbidden_options"]))', "bad = []",
     [f"{TU}.Pure", f"{TU}.Driver"], "C-G2R refuses nothing"),
    (U, '{a.split("=", 1)[0] for a in argv}', "set(argv)", [f"{TU}.Pure"], "C-G2R misses --miss-map=v"),
    (U, '        argv += ["--data-file", str(data_copy)]', "        pass", [f"{TU}.Driver"],
     "a data unit runs without its data file"),
    (U, "    if threads != cfg[\"e_r\"][\"thread_env\"]:", "    if False:", [f"{TU}.Driver"],
     "the thread gate is gone"),
    (U, "    if cpus != int(cfg[\"e_r\"][\"cpus\"]):", "    if False:", [f"{TU}.Driver"], "the CPU gate is gone"),
    (U, "    if got != want:\n        dest.unlink()\n        raise GateFailure(f\"C-DATA:",
     "    if False:\n        dest.unlink()\n        raise GateFailure(f\"C-DATA:", [f"{TU}.Driver"],
     "a data file off its pin is used"),
    (U, "        if data_copy is not None and Path(data_copy).exists():\n            Path(data_copy).unlink()",
     "        pass", [f"{TU}.Driver"], "the data copy is kept"),
    (U, 'data["pass"] = bool(data["argv_equal"] and prov.get("dataFileSha256") == data_sha)',
     'data["pass"] = bool(data["argv_equal"])', [f"{TU}.Driver"], "C-DATA ignores the recorded digest"),
    (U, 'xs = max([max_rel(np.asarray(a["xsec"])[i][rep], np.asarray(b["xsec"])[i][rep])',
     'xs = max([max_rel(np.asarray(a["xsec"])[i][~rep], np.asarray(b["xsec"])[i][~rep])', [f"{TU}.Pure"],
     "C-REP compares the unreported cells"),
    (U, 'out["pass"] = bool(max(out["xsec_max_rel"], out["T_max_rel"], out["y_max_rel"]) <= rtol)',
     'out["pass"] = bool(max(out["xsec_max_rel"], out["y_max_rel"]) <= rtol)', [f"{TU}.Pure"], "C-REP ignores T"),
    (U, "            os.chmod(dest, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)", "            pass", [f"{TU}.Pure"],
     "staged copies stay writable"),
    (U, "        ok = ok and not missing", "        pass", [f"{TU}.Pure"], "the preflight ignores a missing toy file"),
    (U, '    if hashlib.sha256(raw).hexdigest() != t["pseudo_b_sha256"]:', "    if False:", [f"{TU}.Pure"],
     "pseudo_b.json is read off its pin"),
    (R, "            cols.append(np.where(m, area, 0.0)[:, None])", "            cols.append(m.astype(float)[:, None])",
     [f"{TR}.Pure"], "bands are bare sums, not area-weighted"),
    (R, "    return NormalDist().inv_cdf(1 - alpha / 2 / tests)", "    return NormalDist().inv_cdf(1 - alpha / 2 / 205)",
     [f"{TR}.Pure"], "z* uses 205 tests, not the family"),
    (R, '    d = per_test(Y["IBU"] - Y["OF"], counts, zs, xt, sigma)',
     '    d = per_test(Y["IBU"] - Y["OF"][::-1], counts, zs, xt, sigma)', [f"{TR}.Pure"],
     "the difference is not paired toy by toy"),
    (R, '    flagged = [i for i in range(tests) if abs(d["z"][i]) > zs]',
     '    flagged = [i for i in range(tests) if abs(m["IBU"]["z"][i]) > zs]', [f"{TR}.Pure"],
     "the rule reads IBU's own bias, not the difference"),
    (R, '    for k in ("bias", "pull_mean", "pull_sd", "p_hat"):', '    for k in ("bias", "pull_mean"):', [f"{TR}.Pure"],
     "C-OF checks only the means (blind to a mispairing)"),
    (R, '        if prov.get("dataFileSha256") != shas[s]:', "        if False:", [f"{TR}.EndToEnd"],
     "the product's recorded data digest is not checked"),
    (R, "        k10.append(iu.max_rel(row10, h))", "        k10.append(0.0)", [f"{TR}.EndToEnd"], "C-K10 is gone"),
    (R, '                              "pass": ibu["nonfinite"] == {"K10": 0, "K5": 0}}',
     '                              "pass": ibu["nonfinite"]["K10"] == 0}', [f"{TR}.EndToEnd"], "C-CELLS skips K = 5"),
    (R, "            E_of = x_of - x_true", "            E_of = E_post", [f"{TR}.EndToEnd"],
     "OmniFold's errors are taken after the surrogates"),
    (R, '            if ibu["missing"]:\n                if not rec["controls_failed"]:',
     '            if False:\n                if not rec["controls_failed"]:', [f"{TR}.EndToEnd"],
     "a missing unit does not stop the reading"),
    (R, "            if nseeds != [n[\"seed\"] for n in natures]:", "            if False:", [f"{TR}.EndToEnd"],
     "the truth rows are not checked against the natures"),
    (R, '    guard_off_tree(out, "--out")', "    pass", [f"{TR}.EndToEnd"], "--out under a guarded tree is allowed"),
    (R, '            if not rec["C-OF"]["pass"]:\n                rec["controls_failed"].append("C-OF")',
     '            if False:\n                rec["controls_failed"].append("C-OF")', [f"{TR}.EndToEnd"],
     "a failed C-OF does not invalidate the tune"),
    (U, "        if dest.exists():            # a partial or unverified copy never stays behind to block a rerun\n            dest.unlink()",
     "        if False:\n            dest.unlink()", [f"{TU}.Refusals"], "a partial data copy stays behind"),
    (U, '        if set(controls) != CONTROLS[unit["kind"]]:', "        if False:", [f"{TU}.Driver"],
     "a unit with an undeclared control set writes a marker"),
    (R, "            if str(meta.get(k)) != str(bound[k]):", "            if False:", [f"{TR}.EndToEnd"],
     "a unit from another job, runner or config is read"),
    (R, '        if set(ctl) != iu.CONTROLS["toy"]:', "        if False:", [f"{TR}.EndToEnd"],
     "a unit lacking a declared control is read"),
    (R, "        if list(z[\"ks\"]) != ks_want:\n            missing.append(s)",
     "        if list(z[\"ks\"]) != ks_want:\n            pass", [f"{TR}.EndToEnd"],
     "a unit of another K scan is not missing"),
    (R, '        if meta.get("data_sha256") != shas[s] or marker.get("data_sha256") != shas[s]:',
     '        if meta.get("data_sha256") != shas[s]:', [f"{TR}.EndToEnd"], "the marker's data digest is not checked"),
    (R, '        if (meta.get("kind"), meta.get("tune"), meta.get("seed")) != ("toy", truth, s):',
     '        if meta.get("seed") != s:', [f"{TR}.EndToEnd"], "a unit of another tune or kind is read"),
    (R, '        if not isinstance(marker, dict) or (marker.get("unit"), marker.get("seed")) != (name, s):',
     "        if not isinstance(marker, dict):", [f"{TR}.EndToEnd"], "a marker naming another unit is read"),
    (U, '        controls["C-ROO"] = {"max_rel": roo, "pass": bool(roo <= c2["c_roo_rtol"])}',
     '        controls["C-ROO"] = {"max_rel": roo, "pass": True}', [f"{TU}.Driver"], "C-ROO always passes"),
    (U, '        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit and t["exit_status"] == 0',
     "        fast = True", [f"{TU}.Pure"], "the re-price trigger is gone"),
    (U, '        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit and t["exit_status"] == 0',
     '        fast = isinstance(t["wall_s"], float) and t["wall_s"] <= limit', [f"{TU}.Pure"],
     "a failed reference step passes the barrier"),
    (U, '        ok = ok and rec["central_df_vs_central"]["pass"]', "        pass", [f"{TU}.Pure"],
     "the barrier ignores central_df against central"),
    (U, ' and rc.sha256(npz) == m.get("sha256") and rc.sha256(root) == m.get("root_sha256"))\n        mine',
     ' and rc.sha256(npz) == m.get("sha256"))\n        mine', [f"{TU}.Pure"],
     "the barrier ignores the reference root's digest"),
    (U, "        ok = ok and good and mine and fast", "        ok = ok and good and fast", [f"{TU}.Pure"],
     "the barrier accepts another job's references"),
    (U, '    if p != n and not p.startswith(n + os.sep):', "    if False:", [f"{TU}.Hardening"],
     "a destination outside the namespace is accepted"),
    (U, "    if os.path.realpath(n) != os.path.abspath(n):", "    if False:", [f"{TU}.Hardening"],
     "a symlinked namespace is accepted"),
    (U, "    if r.returncode != 0 or head != want:", "    if r.returncode != 0:", [f"{TU}.Hardening"],
     "a unit runs at another deploy"),
    (U, '        if m.get("verdict") == "PASS" and (m.get("job"), m.get("deploy_head")) == (bound["job"], bound["deploy_head"]):',
     '        if m.get("verdict") == "PASS":', [f"{TU}.Driver"], "another job's PASS marker is accepted as done"),
    (U, "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and not extra and barrier) else \"FAIL\"",
     "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and barrier) else \"FAIL\"", [f"{TU}.Hardening"],
     "the completion check ignores undeclared markers"),
    (U, "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and not extra and barrier) else \"FAIL\"",
     "    rec[\"verdict\"] = \"PASS\" if (passed == len(expected) and not extra) else \"FAIL\"", [f"{TU}.Hardening"],
     "the completion check ignores the barrier receipt"),
    (U, "    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):\n        return float(\"inf\")\n    nz",
     "    if a.shape != b.shape:\n        return float(\"inf\")\n    nz", [f"{TU}.Hardening"], "a NaN can pass max_rel"),
    (U, "        for u in units:                              # C-G2R, before the driver is imported (section 5)\n            resolve_argv(",
     "        for u in []:                              # C-G2R, before the driver is imported (section 5)\n            resolve_argv(",
     [f"{TU}.Refusals"], "C-G2R runs only after the driver import"),
    (R, '            if not rec["C-BARRIER"]["pass"]:', "            if False:", [f"{TR}.EndToEnd"],
     "the barrier receipt is not checked"),
    (R, '    problems += [f"{name}: a marker for an undeclared unit" for name in sorted(present - expected)]',
     "    pass", [f"{TR}.EndToEnd"], "an undeclared marker is not noticed"),
    (R, '        for k in ("slurm_job", "runner_sha256", "config_sha256", "deploy_head"):',
     '        for k in ("slurm_job", "runner_sha256", "config_sha256"):', [f"{TR}.EndToEnd"],
     "a meta from another deploy is read"),
    (R, "        if final[\"verdict\"] == \"PASS\":", "        if True:", [f"{TR}.EndToEnd"],
     "a STOP record still carries the readings"),
    (R, '        nonfinite["K5"] += int((~np.isfinite(row5)).sum())\n        if marker.get("verdict") != "PASS":',
     '        if marker.get("verdict") != "PASS":', [f"{TR}.EndToEnd"], "C-CELLS skips K = 5"),
    (R, "                run.watch(tpath)                                  # the truth file joins the atime ledger",
     "                pass", [f"{TR}.EndToEnd"], "the truth file is not in the atime ledger"),
    (L, "    rows += [(\"toys\", k % LANES, u) for k, u in enumerate(toys)]",
     "    rows += [(\"toys\", k % 3, u) for k, u in enumerate(toys)]", [f"{TJ}.Lanes"], "the toys are dealt to 3 lanes"),
    (L, "        if n != len(want) // LANES:", "        if False:", [f"{TJ}.Job"], "verify ignores the lane counts"),
    (O, '               or (o[0] == "read (cov2d-acked)" and t[0].startswith("cov2d"))]',
     '               or (o[0] == "read (cov2d-acked)")]', [f"{TO}"], "an acked read on another lane's path is allowed"),
    (O, "    out += IBUCHI + LR_P0", "    out += IBUCHI", [f"{TO}"], "LR's P0 paths are not protected"),
    (O, "    out += IBUCHI + LR_P0", "    out += LR_P0", [f"{TO}"], "the ibuchi root is not protected"),
    (J, 'if [ "$brc" -ne 0 ] || [ "$(echo $REF_RCS | tr -d \' 0\')" != "" ]; then', "if false; then", [f"{TJ}.Job"],
     "the toys start without the barrier"),
    (J, '[ "$(key QOS)" = regular ] || refuse', '[ -n "$(key QOS)" ] || refuse', [f"{TJ}.Job"],
     "another QOS is accepted"),
    (J, '[ "$(key NumNodes)" = 1 ] || refuse', '[ -n "$(key NumNodes)" ] || refuse', [f"{TJ}.Job"],
     "another node count is accepted"),
    (J, '[ "$(key OverSubscribe)" = NO ] || refuse', 'true || refuse', [f"{TJ}.Job"], "a shared node is accepted"),
    (J, '[ "$(key TimeLimit)" = "$LIMIT" ] || refuse', 'true || refuse', [f"{TJ}.Job"], "another time limit is accepted"),
    (J, '[ -n "$rso" ] && under "$rso" "$RN" || refuse', 'true || refuse', [f"{TJ}.Job"], "StdOut outside $N is accepted"),
    (J, '[ -z "$(ls -A "$U")" ] || refuse', 'true || refuse', [f"{TJ}.Job"], "a used units directory is accepted"),
    (J, 'r=$(realpath "$d") && under "$r" "$RN" && [ ! -L "$d" ] || refuse', 'true || refuse', [f"{TJ}.Job"],
     "a symlinked logs directory is accepted"),
    (J, '[ "$crc" -eq 0 ] || ok=0', 'true || ok=0', [f"{TJ}.Job"], "a failed completion check ends PASS"),
    (J, 'info=$("$SCONTROL" show job "$SLURM_JOB_ID") || refuse', 'info=$("$SCONTROL" show job "$SLURM_JOB_ID") || true',
     [f"{TJ}.Job"], "a failed scontrol query is not refused"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# Run in a fresh interpreter: rc 0 when every test passed, 1 when a test failed or errored, 2 when the suite itself
# could not load (an import or syntax failure, or a named test that does not exist), which is a harness failure.
RUNNER = """
import sys, unittest
sys.argv = sys.argv[:1]
loader = unittest.TestLoader()
suite = loader.loadTestsFromNames(NAMES)
def walk(t):
    if isinstance(t, unittest.TestSuite):
        for x in t:
            yield from walk(x)
    else:
        yield t
tests = list(walk(suite))
if loader.errors or not tests or any(type(t).__name__ == "_FailedTest" for t in tests):
    sys.exit(2)
r = unittest.TextTestRunner(verbosity=0).run(suite)
sys.exit(0 if r.wasSuccessful() else 1)
"""


def run_tests(py: str, tests: list) -> int:
    code = RUNNER.replace("NAMES", repr(list(tests)))
    r = subprocess.run([py, "-B", "-c", code], cwd=HERE, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="2"))
    return r.returncode


def compiles(py: str, path: Path) -> bool:
    if path.suffix == ".py":
        return subprocess.run([py, "-B", "-c", f"import ast; ast.parse(open({str(path)!r}).read())"],
                              capture_output=True).returncode == 0
    return subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0


def main(argv: list) -> int:
    py = argv[0]
    only = int(argv[argv.index("--only") + 1]) if "--only" in argv else None
    chosen = [(i, m) for i, m in enumerate(MUTANTS, 1) if only is None or i == only]
    for i, (f, old, new, tests, what) in chosen:     # every site exists exactly once before anything runs
        n = (HERE / f).read_text().count(old)
        if n != 1:
            print(f"{i}\tNOT-APPLIED\t{f}\t{what} (the site occurs {n} times)")
            return 2
    sets = sorted({tuple(m[3]) for _, m in chosen})
    for t in sets:                                   # the baseline: unmutated, every named test set must pass
        b = run_tests(py, list(t))
        print(f"BASELINE\t{'PASS' if b == 0 else 'FAIL rc ' + str(b)}\t{','.join(t)}", flush=True)
        if b != 0:
            return 2
    killed = total = 0
    for i, (f, old, new, tests, what) in chosen:
        path = HERE / f
        orig = path.read_bytes()
        try:
            path.write_text(orig.decode().replace(old, new))
            if not compiles(py, path):
                print(f"{i}\tHARNESS\t{f}\t{','.join(tests)}\t{what} (the mutant does not compile)")
                return 2
            rc = run_tests(py, tests)
        finally:
            path.write_bytes(orig)
        if sha(path.read_bytes()) != sha(orig):
            print(f"{i}\tRESTORE-FAILED\t{f}")
            return 3
        if rc == 2:
            print(f"{i}\tHARNESS\t{f}\t{','.join(tests)}\t{what} (the suite did not load)")
            return 2
        total += 1
        verdict = "KILLED" if rc == 1 else "SURVIVED"
        killed += verdict == "KILLED"
        print(f"{i}\t{verdict}\t{f}\t{','.join(tests)}\t{what}", flush=True)
    print(f"TOTAL\t{killed}/{total} killed")
    return 0 if killed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
