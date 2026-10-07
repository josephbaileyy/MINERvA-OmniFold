"""Controls that must pass before any final-bank GBDT number is used.

    pgc_controls.py pet-rescore --pet-source SRC --run RUN_DIR --k 5 --row-features rf.npz \
        --committed scored_fb/<run>.design_scores.json --out control_pet_rescore.json
    pgc_controls.py matched-repro --pet-source SRC --run RUN_DIR --selection selection_F0.npz \
        --reco-scalars reco_scalars.npy --row-features rf.npz --committed-rows rows.jsonl.gz \
        --out control_matched_repro.json --ledger cpu_ledger.jsonl --threads 2

* `pet-rescore` re-scores a committed PET final-bank run from its own iteration file with the
  local copies of the scorer and `row_features.npz`, and requires every histogram value of the
  committed score file to be reproduced (|diff| <= 1e-12). It proves the scoring harness and the
  row-feature copy, not the estimator. No fitting.
* `matched-repro` builds a problem with `pgc_fb.build_problem` from a predecessor run directory
  whose `replicate_arrays.npz` is the source of a matched-study selection, requires every
  estimator input to equal `selection_data.build_problem` on the matched study's extracted
  selection, then refits one committed matched-study task (OmniFold, efficiency-corrected,
  truth4_species, h1, seed 1, 10 iterations) and compares its R at every k with the committed task
  row. It proves the data assembly, the estimator and this environment. One GBDT fit, charged to
  the same CPU ledger as the fill-in.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import resource
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pgc_source  # noqa: E402

TOL = 1e-12


def _walk_numbers(a: Any, b: Any, path: str, out: list[tuple[str, float]]) -> None:
    if isinstance(a, dict):
        for k in a:
            if k in b:
                _walk_numbers(a[k], b[k], f"{path}.{k}", out)
            else:
                out.append((f"{path}.{k} missing", float("inf")))
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((f"{path} length", float("inf")))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _walk_numbers(x, y, f"{path}[{i}]", out)
    elif isinstance(a, bool) or a is None:
        if a != b:
            out.append((path, float("inf")))
    elif isinstance(a, (int, float)):
        out.append((path, abs(float(a) - float(b))))


def pet_rescore(a: argparse.Namespace) -> int:
    src = pgc_source.activate(a.pet_source)
    import score_design as sdz
    committed = json.loads(Path(a.committed).read_text())
    scorer = sdz.DesignScorer(a.run, sdz.RowFeatures(a.row_features))
    ours = scorer.score([a.k])
    it_c = [r for r in committed["iterations"] if r["k"] == a.k][0]
    it_o = [r for r in ours["iterations"] if r["k"] == a.k][0]
    diffs: list[tuple[str, float]] = []
    _walk_numbers(it_c["histograms"], it_o["histograms"], "histograms", diffs)
    _walk_numbers(it_c["stability"], it_o["stability"], "stability", diffs)
    worst = max(diffs, key=lambda d: d[1])
    same_digest = it_c["iteration_file_sha256"] == it_o["iteration_file_sha256"]
    ok = worst[1] <= TOL and same_digest
    rec = {"control": "pet-rescore", "run": Path(a.run).name, "k": a.k,
           "iteration_file_sha256": it_o["iteration_file_sha256"],
           "iteration_file_matches_committed": same_digest,
           "n_values_compared": len(diffs), "max_abs_diff": worst[1], "worst_path": worst[0],
           "tolerance": TOL, "pass": ok, "pet_source": src["commit"],
           "pet_files_loaded": pgc_source.loaded_files(a.pet_source)}
    Path(a.out).write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps(rec))
    return 0 if ok else 1


def matched_repro(a: argparse.Namespace) -> int:
    os.environ["OMP_NUM_THREADS"] = str(a.threads)
    for v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[v] = "1"
    t_wall = time.perf_counter()
    r0 = resource.getrusage(resource.RUSAGE_SELF)
    src = pgc_source.activate(a.pet_source)
    import numpy as np
    import matched_design as md
    import scalar_estimators as se
    import scalar_scoring as ss
    import selection_data as sd
    import pgc_fb

    sel_name = a.selection_name
    case = "dev" if sel_name.startswith("F") else a.case
    ref = sd.build_problem(sd.load_selection(a.selection), sel_name, case)
    cols = pgc_fb.InventoryColumns(a.reco_scalars, a.row_features)
    ours = pgc_fb.build_problem(a.run, cols, sd)
    checks: dict[str, bool] = {}
    for side in ("prior", "pseudo"):
        Xr, _ = ref.reco_matrix(side)
        Xo, _ = ours.reco_matrix(side)
        checks[f"{side}_reco_matrix"] = bool(np.array_equal(Xr, Xo, equal_nan=True))
        for key in ("rows", "w_truth", "w_reco", "pass_reco", "pass_truth", "region"):
            checks[f"{side}_{key}"] = bool(np.array_equal(getattr(ref, side)[key],
                                                          getattr(ours, side)[key]))
    for ts in md.TRUTH_SETS:
        checks[f"truth_matrix_{ts}"] = bool(np.array_equal(ref.truth_matrix(ts)[0],
                                                           ours.truth_matrix(ts)[0],
                                                           equal_nan=True))
    checks["distortion"] = bool(np.array_equal(ref.distortion, ours.distortion))
    checks["oracle"] = bool(np.array_equal(ref.oracle, ours.oracle))
    checks["w_data"] = bool(np.array_equal(ref.w_data, ours.w_data))
    inputs_ok = all(checks.values())

    rows = [json.loads(line) for line in gzip.open(a.committed_rows, "rt")]
    want = {r["k"]: r["R"] for r in rows
            if r["selection"] == sel_name and r["case"] == case and r["method"] == "omnifold"
            and r["miss"] == "efficiency_corrected" and r["truth_set"] == "truth4_species"
            and r["seed"] == a.seed}
    got: dict[int, float] = {}
    scorer = ss.Scorer(ours)
    fit_info: dict[int, Any] = {}

    def on_it(k: int, push: np.ndarray, info: dict[str, Any]) -> None:
        got[k] = scorer.score(push)["eavail"]["recovery"]
        fit_info[k] = info

    if inputs_ok:
        se.run_omnifold(ours, truth_set="truth4_species", miss_rule="efficiency_corrected",
                        params=md.HGB_GRID["h1"], seed=a.seed,
                        iterations=md.OMNIFOLD_ITERATIONS, on_iteration=on_it)
    diffs = {k: abs(got[k] - want[k]) for k in sorted(got) if k in want}
    r1 = resource.getrusage(resource.RUSAGE_SELF)
    wall = time.perf_counter() - t_wall
    cpu = (r1.ru_utime - r0.ru_utime) + (r1.ru_stime - r0.ru_stime)
    ok = inputs_ok and len(diffs) == 10 and max(diffs.values()) <= a.r_tolerance
    import sklearn
    rec = {"control": "matched-repro", "run": Path(a.run).name, "selection": sel_name,
           "case": case, "seed": a.seed, "input_checks": checks, "inputs_identical": inputs_ok,
           "R_committed": want, "R_refit": got, "abs_diff": diffs,
           "max_abs_diff": max(diffs.values()) if diffs else None,
           "r_tolerance": a.r_tolerance, "pass": ok, "fit": fit_info,
           "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "sklearn": sklearn.__version__},
           "wall_seconds": wall, "cpu_seconds": cpu, "threads": a.threads,
           "pet_source": src["commit"], "pet_files_loaded": pgc_source.loaded_files(a.pet_source)}
    Path(a.out).write_text(json.dumps(rec, indent=1) + "\n")
    entry = {"task": f"control-matched-repro-{sel_name}-{case}-s{a.seed}", "run": Path(a.run).name,
             "ok": ok, "error": None, "wall_seconds": wall, "cpu_seconds": cpu,
             "threads": a.threads, "charge_core_hours": wall * a.threads / 3600.0,
             "cpu_core_hours": cpu / 3600.0,
             "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(a.ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps({k: rec[k] for k in ("inputs_identical", "max_abs_diff", "pass",
                                          "wall_seconds", "cpu_seconds")}))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pet-rescore")
    p.add_argument("--pet-source", type=Path, required=True)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--k", type=int, required=True)
    p.add_argument("--row-features", type=Path, required=True)
    p.add_argument("--committed", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    m = sub.add_parser("matched-repro")
    m.add_argument("--pet-source", type=Path, required=True)
    m.add_argument("--run", type=Path, required=True)
    m.add_argument("--selection", type=Path, required=True)
    m.add_argument("--selection-name", default="F0")
    m.add_argument("--case", default="dev")
    m.add_argument("--seed", type=int, default=1)
    m.add_argument("--reco-scalars", type=Path, required=True)
    m.add_argument("--row-features", type=Path, required=True)
    m.add_argument("--committed-rows", type=Path, required=True)
    m.add_argument("--r-tolerance", type=float, default=1e-6)
    m.add_argument("--threads", type=int, default=2)
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--ledger", type=Path, required=True)
    a = ap.parse_args(argv)
    return pet_rescore(a) if a.cmd == "pet-rescore" else matched_repro(a)


if __name__ == "__main__":
    sys.exit(main())
