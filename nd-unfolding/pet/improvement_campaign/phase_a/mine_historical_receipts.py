"""Level-2 evidence: what the FULL-SCALE historical campaign runs left behind.

Task A1 Part 1 asks for runtime capture first and logs/receipts second. This module
is the second: it reads only what the executed campaign wrote to
`/pscratch/sd/j/josephrb/campaign-20260920`, and it is strictly read-only -- no path
under the historical output directory is ever opened for writing.

Four independent artifact families are mined per run directory:

`receipt.json`
    The driver's own record. `estimator.batch_size`, `estimator.epochs`,
    `estimator.realized_learning_rates` (the annealed estimator's fit-time
    interception, see `nd-unfolding/pet/annealed_estimator.py`) and
    `pretrained` are the fields Part 1 needs.

`weights/log_<name>.txt`
    The engine's own log. Its first line is emitted from
    `omnifold_nn/omnifold/omnifold.py` `MultiFold.__init__` and reports
    `num_steps_reco` and `num_steps_gen`, each of which is an event count divided
    by ONE batch size. That line is the load-bearing measurement for hypothesis B:
    a per-step batch size would make the two numbers independent of each other,
    and a single shared one makes their ratio exactly the ratio of the arms'
    batch sizes.

`weights/OmniFold_*_iter<i>_step<s>.pkl`
    `hist.history` pickled by `RunModel`. `len(history["loss"])` is the number of
    epochs the fit ACTUALLY ran, which is the only way to see whether the
    early-stopping rule ever fired at full scale. Keys are reported verbatim so a
    reader can see which quantities the engine did and did not record (a learning
    rate among them or not).

`allocation.txt`
    `scontrol show job` at launch. It carries the job id, the account and QOS, and
    -- decisively for provenance -- the `COMMIT=` the launcher exported, which is
    the commit the training path actually ran from.

Nothing here is a verdict. Every emitted field is a transcription of one file plus
that file's sha256, so a later lane can re-open the exact object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import re
from pathlib import Path
from typing import Any

# The historical output root. Read-only: this module refuses to write under it.
HISTORICAL_ROOT = Path("/pscratch/sd/j/josephrb/campaign-20260920")

STAGES = ("tuning", "pilot", "final")

# `MultiFold.__init__` logs this line before any training happens.
STEPS_LINE = re.compile(
    r"^(\d+) training steps at reco and (\d+) steps at gen\s*$", re.MULTILINE)

# The per-fit pickle name encodes the iteration and the OmniFold step.
PKL_NAME = re.compile(r"_iter(\d+)_step(\d+)\.pkl$")

# `scontrol` output is space-separated `Key=Value`; these are the keys we keep.
ALLOC_KEYS = ("JobId", "ArrayJobId", "ArrayTaskId", "Account", "QOS",
              "Partition", "NodeList", "TimeLimit", "NumCPUs", "TresPerJob")

# The launcher exports the pinned checkout commit inside `SubmitLine=`.
SUBMIT_COMMIT = re.compile(r"COMMIT=([0-9a-f]{40})")


def sha256_of(path: Path) -> str:
    """Hex digest of a file, read in chunks so a weights blob does not land in RAM."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_engine_log(weights_dir: Path) -> dict[str, Any]:
    """The engine's `log_<name>.txt`: declared training steps and the iteration trace."""
    logs = sorted(weights_dir.glob("log_*.txt"))
    if not logs:
        return {"present": False}
    log = logs[0]
    text = log.read_text()
    match = STEPS_LINE.search(text)
    return {
        "present": True,
        "path": str(log),
        "sha256": sha256_of(log),
        # None rather than 0: absent is not zero, and a later reader must be able
        # to tell "the engine did not log it" from "the engine logged zero".
        "num_steps_reco": int(match.group(1)) if match else None,
        "num_steps_gen": int(match.group(2)) if match else None,
        "iterations_logged": text.count("ITERATION:"),
        "step1_runs_logged": text.count("RUNNING STEP 1"),
        "step2_runs_logged": text.count("RUNNING STEP 2"),
        "dual_leg_weights_active": "B-4 dual-leg MC weights ACTIVE" in text,
    }


def read_histories(weights_dir: Path) -> list[dict[str, Any]]:
    """One record per pickled `hist.history`, keyed by (iteration, step)."""
    out: list[dict[str, Any]] = []
    for pkl in sorted(weights_dir.glob("OmniFold_*_iter*_step*.pkl")):
        match = PKL_NAME.search(pkl.name)
        if match is None:
            continue
        with pkl.open("rb") as handle:
            history = pickle.load(handle)
        # Every Keras history value is a per-epoch list, so any key's length is
        # the epoch count; `loss` is the one guaranteed to be present.
        epochs_run = len(history.get("loss", []))
        out.append({
            "iteration": int(match.group(1)),
            "step": int(match.group(2)),
            "path": str(pkl),
            "sha256": sha256_of(pkl),
            "history_keys": sorted(history.keys()),
            "epochs_run": epochs_run,
            "loss": [float(v) for v in history.get("loss", [])],
            "val_loss": [float(v) for v in history.get("val_loss", [])],
            # Present only if some callback wrote it; recorded so its ABSENCE is
            # itself evidence about what the executed path tracked.
            "lr": [float(v) for v in history.get("lr", [])],
        })
    return sorted(out, key=lambda rec: (rec["iteration"], rec["step"]))


def read_allocation(run_dir: Path) -> dict[str, Any]:
    """`scontrol show job` as captured at launch, plus the exported pinned commit."""
    alloc = run_dir / "allocation.txt"
    if not alloc.is_file():
        return {"present": False}
    text = alloc.read_text()
    fields: dict[str, Any] = {}
    for token in text.split():
        key, _, value = token.partition("=")
        if key in ALLOC_KEYS and key not in fields:
            fields[key] = value
    commit = SUBMIT_COMMIT.search(text)
    fields.update({
        "present": True,
        "path": str(alloc),
        "sha256": sha256_of(alloc),
        "exported_commit": commit.group(1) if commit else None,
    })
    return fields


def read_receipt(run_dir: Path) -> dict[str, Any]:
    """The driver's own receipt, narrowed to the fields Part 1 audits."""
    receipt = run_dir / "receipt.json"
    if not receipt.is_file():
        return {"present": False}
    payload = json.loads(receipt.read_text())
    estimator = payload.get("estimator", {})
    closure = payload.get("closure", {})
    return {
        "present": True,
        "path": str(receipt),
        "sha256": sha256_of(receipt),
        "arm": payload.get("arm"),
        "seed": payload.get("seed"),
        "stage": payload.get("stage"),
        "learning_rate": payload.get("learning_rate"),
        "niter": payload.get("niter"),
        "pretrained": payload.get("pretrained"),
        "seconds": payload.get("seconds"),
        "estimator": {
            "annealed": estimator.get("annealed"),
            "epochs": estimator.get("epochs"),
            "batch_size": estimator.get("batch_size"),
            "estimator_seed": estimator.get("estimator_seed"),
            "subsample_seed": estimator.get("subsample_seed"),
            "fits_recorded": estimator.get("fits_recorded"),
            "realized_learning_rates": estimator.get("realized_learning_rates"),
        },
        "closure": {
            "measured_leg_is_real_data": closure.get("measured_leg_is_real_data"),
            "bkg_mode": closure.get("bkg_mode"),
            "half_size": closure.get("half_size"),
            "pdata_rows": closure.get("pdata_rows"),
            "prior_rows": closure.get("prior_rows"),
            "split_seed": closure.get("split_seed"),
        },
        "substitution": payload.get("substitution"),
    }


def mine_run(run_dir: Path) -> dict[str, Any]:
    """Every artifact family for one `<stage>/<arm>-seed<n>[-lr<x>]` directory."""
    weights_dir = run_dir / "weights"
    record: dict[str, Any] = {
        "run_dir": str(run_dir),
        "name": run_dir.name,
        "receipt": read_receipt(run_dir),
        "allocation": read_allocation(run_dir),
        "engine_log": (read_engine_log(weights_dir) if weights_dir.is_dir()
                       else {"present": False}),
        "histories": read_histories(weights_dir) if weights_dir.is_dir() else [],
    }
    log = record["engine_log"]
    receipt = record["receipt"]
    batch = receipt.get("estimator", {}).get("batch_size") if receipt.get("present") else None
    if log.get("num_steps_gen") and batch:
        # The engine derives both counts from ONE `self.BATCH_SIZE`, so multiplying
        # back recovers the event population each step was told it had. Two arms
        # whose truth side is declared identical must agree on `examples_gen`.
        record["derived"] = {
            "batch_size": int(batch),
            "examples_reco": int(log["num_steps_reco"]) * int(batch),
            "examples_gen": int(log["num_steps_gen"]) * int(batch),
            # `RunModel` passes steps_per_epoch=int(train_frac*NTRAIN//BATCH_SIZE)
            # with NTRAIN=num_steps*BATCH_SIZE, which floors to train_frac*num_steps.
            "updates_per_epoch_reco": int(0.8 * int(log["num_steps_reco"])),
            "updates_per_epoch_gen": int(0.8 * int(log["num_steps_gen"])),
            "train_frac_assumed": 0.8,
            "train_frac_source": "MultiFold.__init__ default; the driver passes no train_frac",
        }
    return record


def discover_runs(root: Path) -> list[Path]:
    """Every run directory under the three frozen stages, in a stable order."""
    runs: list[Path] = []
    for stage in STAGES:
        stage_dir = root / stage
        if not stage_dir.is_dir():
            continue
        runs.extend(sorted(child for child in stage_dir.iterdir() if child.is_dir()))
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HISTORICAL_ROOT,
                        help="historical campaign output root (read-only)")
    parser.add_argument("--out", type=Path, required=True,
                        help="where to write the mined JSON; must be OUTSIDE --root")
    args = parser.parse_args()

    out = args.out.resolve()
    root = args.root.resolve()
    if root == out or root in out.parents:
        raise SystemExit(
            f"[mine] refusing to write {out} under the historical output root {root}; "
            "the historical campaign's outputs are preserved unmodified")

    runs = discover_runs(root)
    if not runs:
        raise SystemExit(f"[mine] no run directories under {root}")

    records = [mine_run(run) for run in runs]
    payload = {
        "mined_from": str(root),
        "task": "A1 Part 1 evidence level 2 (logs and receipts of the executed campaign)",
        "run_count": len(records),
        "runs": records,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"[mine] {len(records)} runs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
