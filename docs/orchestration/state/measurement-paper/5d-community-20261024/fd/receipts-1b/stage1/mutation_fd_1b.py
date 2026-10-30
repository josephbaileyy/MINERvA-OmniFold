#!/usr/bin/env python3
"""1B stage 1's mutation receipt (FD-1B-DECLARATION.md section 8.4): revert or bend one declared rule at a time in the
toy mode, the scorer and the submit line, run ``nd-unfolding/tests/test_fd_1b.py`` against the mutant, and record
which tests die. A mutant that no test kills is printed UNKILLED and is a finding.

The mutant never exists inside the repository. Each run builds a throwaway tree OUTSIDE it: real COPIES of every
top-level ``nd-unfolding/*.py`` (a symlinked module would resolve its ``_ND`` back into the repository, put that
directory first on ``sys.path``, and let a later import load the UNMUTATED module), the test file and its conftest, and
symlinks to ``docs/`` and ``2d-unfolding/`` for the committed records the code reads. Every replacement must match
exactly once, the mutant must differ from the original and compile; any of those failing is a hard error, not a row.
An unmutated control run must pass every test first.

    python3 mutation_fd_1b.py [--only M01,S03] [--list]

MEASURES: which tests detect each mutation. CANNOT AUTHORIZE: anything.
"""
from __future__ import annotations

import argparse
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
ND = REPO / "nd-unfolding"
TEST = ND / "tests/test_fd_1b.py"

# (id, file, old, new, the rule it breaks)
MUTATIONS = [
    ("M01", "fd_1b_toys.py", "    return w / w.sum()", "    return np.full(w.size, 1.0 / w.size)",
     "flux drawn uniformly, not with probability w_u / sum w"),
    ("M02", "fd_1b_toys.py", "    groups.pop(s1_assemble.DROPPED, None)", "    pass",
     "Rvp1pi kept as a drawn band"),
    ("M03", "fd_1b_toys.py", '"detector": {b: int(rng.integers(0, 2))', '"detector": {b: int(rng.integers(0, 1))',
     "detector bands always at endpoint 0"),
    ("M04", "fd_1b_toys.py", "int(2 * rng.integers(0, 2) - 1)", "1", "lateral sign always +1"),
    ("M05", "fd_1b_toys.py", "        fs *= k_wr * ne.truth_preserving(k_wt, inputs, source)", "        fs *= k_wr",
     "interaction universe applied without the truth-preserving g_f"),
    ("M06", "fd_1b_toys.py", '        if not (det_dir / f"{tag}_wr.npy").exists():', "        if False:",
     "a detector band may come from somewhere other than the dump"),
    ("M07", "fd_1b_toys.py", '    rep["obs_counts"] = exp["obs_counts"]\n', "",
     "the streams also resample the pseudo-data (data statistics counted twice)"),
    ("M08", "fd_1b_toys.py", "_MeanRNG() if expectation else", "_MeanRNG() if False else",
     "the derivation runs are not noise-free"),
    ("M09", "fd_1b_toys.py", "np.ones(inputs[\"MCgen\"].shape[0], bool), r)", "np.ones(inputs[\"MCgen\"].shape[0], bool), r * fs)",
     "the truth moves with the draw"),
    # (A first M10 doubled the truth weight; it is an EQUIVALENT mutant: true_xsec divides the reweighted truth by a
    # completeness built from the same weights, so the factor cancels exactly. Run 1 recorded it UNKILLED.)
    ("M10", "fd_1b_toys.py", 'x_true = s5n_pseudo.true_xsec(half_w, np.ones(inputs["MCgen"].shape[0], bool), r)',
     'x_true = s5n_pseudo.true_xsec(half_w, s5c_pseudo.half_mask(inputs["MCgen"].shape[0], 1), r)',
     "the full-MC truth taken over half of the MC"),
    ("M11", "fd_1b_toys.py", "    if not (lo <= first <= last <= hi):", "    if False:",
     "seeds outside the arm's declared range accepted"),
    ("M12", "fd_1b_toys.py", '    if a.arm.startswith("repro") != a.no_draws:', "    if False:",
     "draws switched off outside the reproduction arms"),
    ("M13", "fd_1b_toys.py", '        if (st.st_size, st.st_mtime_ns) != (rec["size"], rec["mtime_ns"]):', "        if False:",
     "a pinned weight file changed after pinning is accepted"),
    ("M14", "fd_1b_toys.py", "    if want != got:", "    if False:",
     "a truth ratio without the committed F1 digest is accepted"),
    ("M15", "fd_1b_toys.py", 'ui = dict(inputs, w_reco=np.where(is_b,', 'ui = dict(inputs, w_reco=np.where(True,',
     "half mode applies the draw to the unfolding half too"),
    ("M16", "fd_1b_toys.py", 'CONFIG, ESTIMATOR_SEED, ITERS = "R", 42, 5', 'CONFIG, ESTIMATOR_SEED, ITERS = "R", 43, 5',
     "the estimator seed is not production's 42"),
    ("M17", "fd_1b_toys.py", "        exp = mc_template_streams(exp, seed)\n", "",
     "production toys without set A's MC and template streams"),
    ("M18", "fd_1b_toys.py", "        raise Refusal(f\"input digests {npz_sha} / {bkg_sha} are not the declared ones\")",
     "        pass", "inputs with the wrong digest accepted"),
    ("S01", "fd_1b_score.py", "N_BOOT, BOOT_SEED = 20_000, 20_261_030", "N_BOOT, BOOT_SEED = 20_000, 20_261_005",
     "the bootstrap generator seed is VL169's, not this study's"),
    ("S02", "fd_1b_score.py", 'intervals[f"C{k}"][1] < NOMINAL[k]', 'intervals[f"C{k}"][0] < NOMINAL[k]',
     "the one-sided rule reads the interval's lower bound"),
    ("S03", "fd_1b_score.py", '    if v == "PASS" and not pc["passes"]:', "    if False:",
     "a PASS stands when the positive control fails"),
    ("S04", "fd_1b_score.py", "* deltas[b] * g / 2.0", "* deltas[b] / 2.0",
     "the lateral surrogate is not carried to the truth"),
    ("S05", "fd_1b_score.py", 'if k != "seed")', "if True)", "M_d includes the undrawn seed block"),
    ("S06", "fd_1b_score.py", "        if got != want:", "        if False:",
     "a toy whose draw departs from its seed's declared draw is scored"),
    ("S07", "fd_1b_score.py", "        elif not np.array_equal(xt, truth):\n            raise Invalid(",
     "        elif False:\n            raise Invalid(",
     "toys with differing truths are scored together"),
    ("S08", "fd_1b_score.py", "WILSON_LEVEL, FLAG_LEVEL = 0.95, 0.995", "WILSON_LEVEL, FLAG_LEVEL = 0.95, 0.95",
     "cells flagged at the 95 % Wilson bound, not 99.5 %"),
    ("S09", "fd_1b_score.py", "chi2_values(X, X.mean(axis=0), Md_t) * n / (n - 1)", "chi2_values(X, X.mean(axis=0), Md_t)",
     "the mean-subtracted chi-square without N / (N - 1)"),
    ("S10", "fd_1b_score.py", "        L = np.linalg.cholesky(M)", "        L = np.linalg.cholesky(M + 1e-3 * np.trace(M) * np.eye(M.shape[0]))",
     "4A with a ridge, so a singular matrix is not refused"),
    ("S11", "fd_1b_score.py", "GATE_D_WINDOW = SCALE_TOLERANCE", "GATE_D_WINDOW = (0.5, 2.0)",
     "gate D's window wider than the control's"),
    ("S12", "fd_1b_score.py", "sa.mat_cov(X, w if b == sa.FLUX else None) * np.outer(g, g)", "sa.mat_cov(X, None) * np.outer(g, g)",
     "gate D's flux block without the constraint weights"),
    ("S13", "fd_1b_score.py", 'LEVEL = {"interim": 0.995, "final": 0.95}', 'LEVEL = {"interim": 0.95, "final": 0.95}',
     "the interim look at 95 %, not 99.5 %"),
    ("S14", "fd_1b_score.py", '    verdict = v if (v == "FAIL" or pc_ok) else "INCONCLUSIVE"', "    verdict = v",
     "a test arm's PASS stands when its x0.7 control does not fail"),
    ("S15", "fd_1b_score.py", '    if look == "interim" and not v.startswith("FAIL"):', '    if look == "interim" and False:',
     "the interim look returns a final verdict"),
    ("S16", "fd_1b_score.py", "    g = f / (U @ truth)\n", "    g = np.ones_like(f)\n",
     "gate D compares toy-space blocks with f-space blocks"),
    # after the independent review (FD-1B-STAGE1-REPORT.md section 6)
    ('S17', 'fd_1b_score.py', '    g = f / (U @ truth)\n', '    g = f / x["CV"]\n',
     'gate D carried to f by the noise-free unfold instead of the truth (review finding 1)'),
    ('S18', 'fd_1b_score.py', '        return {"gates": "nothing", "refused": str(e)}', '        raise',
     'a 4A refusal overrides the coverage verdict (review finding 2)'),
    ('S19', 'fd_1b_score.py', '        centred["verdict"] = None\n', '',
     '4A carries a verdict at a test arm (binding ruling 4; review finding 3)'),
    ('S20', 'fd_1b_score.py', '        if m.get("numpy_version") != np.__version__:', '        if False:',
     'a scorer under another numpy grades instead of refusing (review finding 5)'),
    ('S21', 'fd_1b_score.py', 'expect = {"arm": arm, "mode": mode, "no_draws": False, "truth": truth_name,', 'expect = {"arm": arm, "mode": mode, "no_draws": False,',
     "the toys' truth name is not checked (review finding 4)"),
    ('S22', 'fd_1b_score.py', '        if not np.all(np.isfinite(xt)):', '        if False:',
     'a non-finite truth is scored (review finding 4)'),
    ('T07', 'fd_1b_tasks.py', '    if not deploy.startswith(P + "/"):', '    if False:',
     'a deploy off pscratch accepted (review finding 8)'),
    ("T01", "fd_1b_tasks.py", 'ACCOUNT, QOS, CONSTRAINT_FLAG = "m3246", "regular", "cpu"',
     'ACCOUNT, QOS, CONSTRAINT_FLAG = "m3246", "premium", "cpu"', "the submit line on premium QOS"),
    ("T02", "fd_1b_tasks.py", '    if not 0 < hours(spec["limit"]) < MAX_LIMIT_H:', "    if False:",
     "a limit of 12 h or more accepted"),
    ("T03", "fd_1b_tasks.py", '    if most != spec["most_per_lane"]:', "    if False:",
     "a packing whose fullest lane is not the declared one accepted"),
    ("T04", "fd_1b_tasks.py", 'PACKER_REL = "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh"',
     'PACKER_REL = "nd-unfolding/s5c_array.sh"', "a submit line through another script than the committed packer"),
    ("T05", "fd_1b_tasks.py", '("g18", "toy", 2_620_100, 2_620_299)', '("g18", "toy", 2_620_100, 2_620_298)',
     "a declared G18 toy is never run"),
    ("T06", "fd_1b_tasks.py", '    if abs(cap(job) - DECLARED_CAPS[job]) > 1e-9:', "    if False:",
     "a job whose enforced cap is not the declared one accepted"),
]


def build_tree(root: Path, mutation=None) -> None:
    (root / "nd-unfolding/tests").mkdir(parents=True)
    for p in ND.glob("*.py"):
        shutil.copy2(p, root / "nd-unfolding" / p.name)
    for name in ("test_fd_1b.py", "conftest.py"):
        shutil.copy2(ND / "tests" / name, root / "nd-unfolding/tests" / name)
    for d in ("docs", "2d-unfolding"):
        (root / d).symlink_to(REPO / d)
    if mutation is None:
        return
    mid, fn, old, new, _ = mutation
    target = root / "nd-unfolding" / fn
    src = target.read_text()
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"[harness] {mid}: the replacement matches {n} times in {fn}, not once")
    out = src.replace(old, new)
    if out == src:
        raise SystemExit(f"[harness] {mid}: the mutant equals the original")
    target.write_text(out)
    py_compile.compile(str(target), doraise=True)


def run_suite(root: Path) -> tuple[int, list[str], str]:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rf", "-p", "no:cacheprovider",
                        str(root / "nd-unfolding/tests/test_fd_1b.py")], cwd=root, capture_output=True, text=True)
    failed = sorted(set(re.findall(r"^FAILED \S+::(\S+::\S+)", r.stdout, re.M)))
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-200:]
    return r.returncode, failed, tail


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--only", default=None)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for m in MUTATIONS:
            print(f"{m[0]}  {m[1]:16s} {m[4]}")
        return 0
    chosen = [m for m in MUTATIONS if a.only is None or m[0] in a.only.split(",")]
    stale = [(m[0], (ND / m[1]).read_text().count(m[2])) for m in chosen if (ND / m[1]).read_text().count(m[2]) != 1]
    if stale:  # checked before any run, so a table is never cut short by a replacement that no longer matches
        raise SystemExit(f"[harness] replacements that do not match exactly once: {stale}")
    scratch = Path(tempfile.mkdtemp(prefix="fd1b-mutants-"))
    if REPO in scratch.resolve().parents:
        raise SystemExit("[harness] refusing: the mutant tree would be inside the repository")
    try:
        root = scratch / "control"
        build_tree(root)
        rc, failed, tail = run_suite(root)
        print(f"CONTROL  rc={rc}  {tail}")
        if rc != 0:
            raise SystemExit(f"[harness] the unmutated suite fails: {failed}")
        unkilled = []
        for m in chosen:
            root = scratch / m[0]
            build_tree(root, m)
            rc, failed, tail = run_suite(root)
            status = "KILLED" if rc != 0 else "UNKILLED"
            if rc == 0:
                unkilled.append(m[0])
            print(f"{m[0]}  {status:8s} {m[1]:16s} {m[4]}")
            print(f"     {tail}")
            for t in failed:
                print(f"     dies: {t}")
        print(f"SUMMARY  {len(chosen) - len(unkilled)} of {len(chosen)} killed; unkilled: {unkilled or 'none'}")
        return 1 if unkilled else 0
    finally:
        shutil.rmtree(scratch)


if __name__ == "__main__":
    sys.exit(main())
