#!/usr/bin/env python3
"""Mutation receipt for rpl_scale_fit.py: each mutant must fail tests/test_rpl_scale_fit.py.

usage: rpl_scale_fit_mutation.py OUT.json [--only NAME ...]

Each mutant replaces exactly one source fragment (which must occur exactly once) in a copy of the module, placed in a
fresh temporary directory beside unmodified copies of the RPD-RECO modules it imports, so the working tree is never
mutated. The suite runs serially (-x) with every thread cap at 1 against the copy (RPL_SCALE_FIT_MODULE). A mutant is
killed when the suite fails. The receipt records each mutant, its outcome and the suite's last line.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_DIR = HERE.parent
MODULE = MODULE_DIR / "rpl_scale_fit.py"
SIBLINGS = ("fd_rpd_reco.py", "fd_rpd_inputs.py", "fd_rpd_reco_custody.py")
SUITE = HERE / "test_rpl_scale_fit.py"

MUTANTS = [
    ("lattice-index-side", 'side="right").astype(np.int64)', 'side="left").astype(np.int64)'),
    ("lattice-overflow", "overflow = cumulative[..., -1:] - interior", "overflow = cumulative[..., -2:-1] - interior"),
    ("chi2-no-profile", "    k = sx / sxx\n", "    k = 1.0\n"),
    ("parabola-convexity", "    if not a > 0:\n", "    if not a < 0:\n"),
    ("coarse-stride", "COARSE_STRIDE = 50", "COARSE_STRIDE = 100"),
    ("fine-window", "FINE_HALF = 50", "FINE_HALF = 5"),
    ("scan-edge-strict", "return bool(abs(result[\"coarse_min_alpha\"]) >= edge or", "return bool(abs(result[\"coarse_min_alpha\"]) > edge or"),
    ("not-a-scale-inclusive", 'if fit["p_alpha_hat"] < P_FIT_MIN:', 'if fit["p_alpha_hat"] <= P_FIT_MIN:'),
    ("beyond-inclusive", "if size - error > sigma_band:", "if size - error >= sigma_band:"),
    ("within-strict", "if size + error <= sigma_band:", "if size + error < sigma_band:"),
    ("band-sigmas", "BAND_SIGMAS = 2.0", "BAND_SIGMAS = 1.0"),
    ("no-step-reading", 'if d1_pb_reading != "SEEN":', 'if d1_pb_reading == "NOT-SEEN":'),
    ("used-bins-or", "self.used = (p_group[0] >= R.MIN_PREDICTION) & (p_ref[0]", "self.used = (p_group[0] >= R.MIN_PREDICTION) | (p_ref[0]"),
    ("ndf-minus-one", "self.ndf = int(self.used.sum()) - 2", "self.ndf = int(self.used.sum()) - 1"),
    ("refit-subset", "for r in range(1, R.BOOTSTRAPS + 1)])", "for r in range(1, 30)])"),
    ("seed-word", "np.random.SeedSequence([20261104, 11, replica + 1])", "np.random.SeedSequence([20261104, 12, replica + 1])"),
    ("histogram-equality-skipped", "alpha0_n.shape == c0_n.shape and bool(np.array_equal(alpha0_n, c0_n))", "alpha0_n.shape == c0_n.shape"),
    ("reproduction-tolerance", "REPRODUCTION_RTOL = 1e-12", "REPRODUCTION_RTOL = 1.0"),
    ("plant-tolerance", "pull <= PLANT_TOLERANCE and not at_scan_edge(fit)", "pull <= PLANT_TOLERANCE + 1e9 and not at_scan_edge(fit)"),
    ("plant-direction", "lattice.index(pz * (1.0 + alpha)) for alpha in PLANTS", "lattice.index(pz / (1.0 + alpha)) for alpha in PLANTS"),
    ("direct-direction", "R.bin_indices(pz / (1.0 + alpha), R.PZ_EDGES)", "R.bin_indices(pz * (1.0 + alpha), R.PZ_EDGES)"),
    ("unit-test-c0-accepted", 'require("unit_test_predecessor_only" not in records["c0"]["result"], "P_RPD", "c0 is a unit-test stand-in")', "pass"),
    ("chain-digest-skipped", 'require(self_digest(rpd_run / f"{step}.json") == digests[step], "P_RPD", f"{step} is not d1\'s chain")', "pass"),
    ("environment-skipped", 'require(p0["result"]["environment"] == environment, "ENVIRONMENT"', 'require(True, "ENVIRONMENT"'),
    ("wall-skipped", "        check()\n        count = len(sample.values)", "        count = len(sample.values)"),
    ("fits-on-no-step", 'if outcome != "NO-STEP":  # NO-STEP: no fit is read', "if True:"),
    ("step-regions", "STEP_REGIONS = ((0, 6), (6, 8))", "STEP_REGIONS = ((0, 6), (6, 9))"),
    ("threads-skipped", 'require(os.environ.get(key) == "1", "THREADS"', 'require(True, "THREADS"'),
    ("nice-skipped", 'require(os.getpriority(os.PRIO_PROCESS, 0) == 19, "NICE"', 'require(True, "NICE"'),
    ("output-exists-skipped", 'require(not out.exists() or not any(out.iterdir()), "OUTPUT_EXISTS"', 'require(True, "OUTPUT_EXISTS"'),
]


def run_one(name: str, old: str, new: str, source: str) -> dict:
    require_once = source.count(old)
    if require_once != 1:
        return {"name": name, "outcome": "INVALID", "detail": f"fragment occurs {require_once} times"}
    with tempfile.TemporaryDirectory(prefix=f"rpl-mut-{name}-") as tmp:
        directory = Path(tmp)
        for sibling in SIBLINGS:
            shutil.copy2(MODULE_DIR / sibling, directory / sibling)
        mutated = directory / "rpl_scale_fit.py"
        mutated.write_text(source.replace(old, new))
        environment = dict(os.environ, RPL_SCALE_FIT_MODULE=str(mutated), PYTHONDONTWRITEBYTECODE="1")
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            environment[key] = "1"
        started = time.monotonic()
        completed = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", str(SUITE)],
            capture_output=True,
            text=True,
            env=environment,
            cwd=tmp,
        )
        tail = [line for line in completed.stdout.splitlines() if line.strip()][-1:] or [""]
        return {
            "name": name,
            "outcome": "KILLED" if completed.returncode != 0 else "SURVIVED",
            "returncode": completed.returncode,
            "seconds": round(time.monotonic() - started, 1),
            "suite_last_line": tail[0],
            "mutated_sha256": hashlib.sha256(mutated.read_bytes()).hexdigest(),
        }


def main(argv: list[str]) -> int:
    out = Path(argv[0])
    only = set(argv[argv.index("--only") + 1 :]) if "--only" in argv else None
    source = MODULE.read_text()
    results = []
    for name, old, new in MUTANTS:
        if only is not None and name not in only:
            continue
        result = run_one(name, old, new, source)
        print(f"{result['outcome']:9s} {name} {result.get('seconds', '')}", flush=True)
        results.append(result)
    killed = sum(r["outcome"] == "KILLED" for r in results)
    receipt = {
        "schema": "rpl-scale-fit-mutation/1",
        "module_sha256": hashlib.sha256(MODULE.read_bytes()).hexdigest(),
        "suite_sha256": hashlib.sha256(SUITE.read_bytes()).hexdigest(),
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "required": len(results),
        "killed": killed,
        "all_killed": killed == len(results),
        "results": results,
    }
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"MUTATION :: {killed}/{len(results)} killed")
    return 0 if killed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
