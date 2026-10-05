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
              "Partition", "NodeList", "TimeLimit", "NumCPUs", "TresPerJob",
              "SubmitTime", "StartTime", "Command", "WorkDir", "StdOut")

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
        val = [float(v) for v in history.get("val_loss", [])]
        best = min(range(len(val)), key=val.__getitem__) if val else None
        ckpt = pkl.with_name(pkl.name[: -len(".pkl")] + ".weights.h5")
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
            # ModelCheckpoint(save_best_only) rewrites the .weights.h5 only when val_loss
            # improves; the .pkl is written after fit returns. Their mtimes bracket when
            # the best epoch was saved. The pushed weights come from the in-memory model,
            # not from this file.
            "val_loss_argmin_epoch": best,
            "best_is_last_epoch": (best == len(val) - 1) if val else None,
            "checkpoint_mtime": ckpt.stat().st_mtime if ckpt.is_file() else None,
            "history_mtime": pkl.stat().st_mtime,
            "checkpoint_sha256": sha256_of(ckpt) if ckpt.is_file() else None,
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
            # INFERRED FROM SOURCE, not logged: `RunModel` passes
            # steps_per_epoch=int(train_frac*NTRAIN//BATCH_SIZE) with
            # NTRAIN=num_steps*BATCH_SIZE, which floors to train_frac*num_steps. The
            # runtime audit measures the same quantity at small scale.
            "updates_per_epoch_reco_source_formula": int(0.8 * int(log["num_steps_reco"])),
            "updates_per_epoch_gen_source_formula": int(0.8 * int(log["num_steps_gen"])),
            "train_frac_assumed": 0.8,
            "train_frac_source": "MultiFold.__init__ default; the driver passes no train_frac",
        }
    rows = receipt.get("closure", {}) if receipt.get("present") else {}
    if log.get("num_steps_gen") and rows.get("prior_rows"):
        # Batch size as the ENGINE LOG implies it for each step, independently of the
        # receipt's declared batch: num_steps = rows // batch.
        n1 = int(rows.get("pdata_rows") or 0) + int(rows["prior_rows"])
        n2 = 2 * int(rows["prior_rows"])
        record["engine_log_implied"] = {
            "step1_rows": n1, "step2_rows": n2,
            "step1_batch_range": [n1 // (int(log["num_steps_reco"]) + 1) + 1,
                                  n1 // int(log["num_steps_reco"])],
            "step2_batch_range": [n2 // (int(log["num_steps_gen"]) + 1) + 1,
                                  n2 // int(log["num_steps_gen"])],
        }
    return record


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Per (stage, arm): the executed quantities, as sets, so a single outlier shows."""
    groups: dict[str, dict[str, Any]] = {}
    for rec in records:
        receipt = rec["receipt"]
        if not receipt.get("present"):
            continue
        key = f"{receipt['stage']}/{receipt['arm']}"
        g = groups.setdefault(key, {
            "runs": 0, "batch_size": set(), "num_steps_reco": set(), "num_steps_gen": set(),
            "epochs_run": set(), "history_keys": set(), "realized_lr_by_fit": set(),
            "learning_rate_argument": set(), "val_argmin_is_last_epoch": [],
            "val_argmin_epoch": [], "pretrained_exact": set(), "seconds": []})
        g["runs"] += 1
        g["batch_size"].add(receipt["estimator"]["batch_size"])
        g["num_steps_reco"].add(rec["engine_log"].get("num_steps_reco"))
        g["num_steps_gen"].add(rec["engine_log"].get("num_steps_gen"))
        g["learning_rate_argument"].add(receipt.get("learning_rate"))
        lrs = receipt["estimator"].get("realized_learning_rates") or []
        g["realized_lr_by_fit"].add(tuple((d["iteration"], round(d["learning_rate"], 12))
                                          for d in lrs))
        pre = receipt.get("pretrained") or {}
        g["pretrained_exact"].add(pre.get("exact") if isinstance(pre, dict) else None)
        g["seconds"].append(receipt.get("seconds"))
        for h in rec["histories"]:
            g["epochs_run"].add(h["epochs_run"])
            g["history_keys"].add(tuple(h["history_keys"]))
            g["val_argmin_is_last_epoch"].append(h["best_is_last_epoch"])
            g["val_argmin_epoch"].append((h["iteration"], h["step"], h["val_loss_argmin_epoch"]))
    out = {}
    for key, g in sorted(groups.items()):
        flags = [f for f in g["val_argmin_is_last_epoch"] if f is not None]
        out[key] = {
            "runs": g["runs"],
            "batch_size": sorted(g["batch_size"]),
            "num_steps_reco": sorted(x for x in g["num_steps_reco"] if x is not None),
            "num_steps_gen": sorted(x for x in g["num_steps_gen"] if x is not None),
            "epochs_run": sorted(g["epochs_run"]),
            "history_keys": sorted(list(k) for k in g["history_keys"]),
            "learning_rate_argument": sorted(g["learning_rate_argument"]),
            "realized_lr_by_fit": sorted(list(map(list, t)) for t in g["realized_lr_by_fit"]),
            "pretrained_exact": sorted(g["pretrained_exact"], key=repr),
            "fits": len(flags),
            "fits_whose_val_loss_argmin_is_last_epoch": sum(flags),
            "val_argmin_epoch_by_step": {
                f"step{s}": sorted(e for (_i, st, e) in g["val_argmin_epoch"] if st == s)
                for s in (1, 2)},
            "seconds_mean": (sum(g["seconds"]) / len(g["seconds"])) if g["seconds"] else None,
        }
    return out


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
    selection = root / "tuning" / "selected_learning_rate.json"
    payload = {
        "tuning_selection": ({"path": str(selection), "sha256": sha256_of(selection),
                              "content": json.loads(selection.read_text())}
                             if selection.is_file() else {"present": False}),
        "summary": summarize(records),
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
