"""B2 driver: the A1 recipe driver (`improvement_campaign/run_unfold.py`) plus what task B2 needs.

Nothing in `run_unfold.py`, the engine or the loader is edited; this module subclasses the A1
`RecipeMultiFold` and reuses its optimizer build/verification, split, recorder and factories.
It adds:

* **per-iteration state** -- after every OmniFold iteration the pull (step-1 weights carried to
  truth) and the push (step-2 output), both over ALL of half B in `dump_rows_b` order, as float32
  in `iterations/iterNN.npz`; the two models' weights in `iterations/modelsNN.npz`; the fit records
  in `fits.jsonl`; `state.json` (last completed iteration, config hash);
* **resume** -- a rerun with the same config continues after the last completed iteration: the
  push is restored and both models are rebuilt from their factories and loaded with the saved
  weights (warm start is then exactly the continuous run's; every fit's seeds depend only on
  (step seed, step, iteration), `run_unfold.derive_seed`);
* **a deadline** -- an iteration is not started if its projected duration would cross
  `--deadline-unix`; the run then exits 0 with `INCOMPLETE` in `status.txt`;
* **B2 input arms** (`b2_arms.py`, named and hashed; `RunConfig.feature_arm` names one);
* **truth-only mode** (`--mode truth_only`, experiment 2): step 2 ALONE, trained on half A to
  separate prior truth x (the true tilt) from prior truth -- the engine's own `RunStep2` with the
  pull set to the injected tilt -- then evaluated on half B's truth at EVERY epoch. A learnability
  diagnostic of the step-2 input set, NOT a detector-level bound or an unfolding recovery.

CLI: `b2_driver.py --config <json> --repo <checkout> --out <dir> --inputs-npz ... --identity-sidecar
... [--mode unfold|truth_only] [--populations <B1 populations.npz>] [--deadline-unix T]`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[1]
SCALAR = CAMPAIGN / "phase_b" / "scalar"
for _p in (CAMPAIGN, HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import b2_arms  # noqa: E402
import recorder as rec  # noqa: E402
import run_unfold as ru  # noqa: E402
from recipe import RunConfig  # noqa: E402

LOGIT_CAP = rec.REWEIGHT_LOGIT_CAP
STEP2_MISS_MODES = ("carry", "efficiency_corrected")


def sha256_file(path: Path) -> str:
    return ru.sha256_of(Path(path))


def write_json_atomic(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=repr) + "\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------------------------- #
# Inputs
# ---------------------------------------------------------------------------------------------- #
def scalar_reader(np: Any, ffd: Any, inputs_npz: Path) -> Callable[[str, str, Any], Any]:
    """`closure_data.read_scalar_column`, with each npz member read once (they are 0.8 GB)."""
    import numpy.lib.format as npf
    cache: dict[str, Any] = {}

    def read(which: str, column: str, rows: Any) -> Any:
        if which not in cache:
            member = {"reco": "reco_scalars.npy", "truth": "truth_scalars.npy"}[which]
            with zipfile.ZipFile(str(inputs_npz)) as archive:
                with archive.open(member) as handle:
                    cache[which] = npf.read_array(handle, allow_pickle=False)
        return cache[which][np.asarray(rows), ffd.SCALAR_COLS[column]].astype(np.float64)

    return read


def build_inputs(cd: Any, mods: dict[str, Any], np: Any, config: RunConfig, args: Any,
                 need_half_a: bool) -> tuple[Any, dict[str, Any] | None]:
    """`closure_data.build_closure_inputs`, capturing the loader it builds so half A's truth
    arrays (needed only in truth-only mode) come from the SAME loader and normalization."""
    ffd = mods["ffd"]
    original = ffd.build_fullevent_loaders
    captured: dict[str, Any] = {}

    def recording(*a: Any, **k: Any) -> Any:
        out = original(*a, **k)
        captured["out"] = out
        return out

    ffd.build_fullevent_loaders = recording
    try:
        inputs = cd.build_closure_inputs(
            mods, np, arm=config.arm, events=config.events, endpoint=config.endpoint,
            inputs_npz=args.inputs_npz, identity_sidecar=args.identity_sidecar,
            theirs_index=None, theirs_cache=None)
    finally:
        ffd.build_fullevent_loaders = original
    if not need_half_a:
        return inputs, None
    _data, mc_all, imc, _cr, _cg, _meta = captured["out"]
    imc = np.asarray(imc).astype(np.int64)
    rows_a = np.asarray(inputs.meta["dump_rows_a"]).astype(np.int64)
    order = np.argsort(imc, kind="stable")
    pos = order[np.searchsorted(imc[order], rows_a)]
    if not np.array_equal(imc[pos], rows_a):
        raise SystemExit("[b2] half-A rows are not in the loader's subsample")
    half_a = {"rows": rows_a,
              "reco": np.asarray(mc_all.reco)[pos], "reco_evt": np.asarray(mc_all.reco_evt)[pos],
              "gen": np.asarray(mc_all.gen)[pos], "gen_evt": np.asarray(mc_all.gen_evt)[pos],
              "pass_reco": np.asarray(mc_all.pass_reco)[pos].astype(bool),
              "pass_gen": np.asarray(mc_all.pass_gen)[pos].astype(bool),
              "weight": np.asarray(mc_all.weight, dtype=np.float64)[pos],
              "weight_reco": np.asarray(mc_all.weight_reco, dtype=np.float64)[pos]}
    if not np.array_equal(half_a["pass_gen"], np.asarray(inputs.meta["pass_gen_a"], bool)):
        raise SystemExit("[b2] half-A pass_gen differs from the closure's")
    return inputs, half_a


def column_stats(np: Any, cloud: Any, max_rows: int = 200_000) -> list[dict[str, float]]:
    """Per-column statistics over REAL tokens (energy column != 0): is anything standardized?"""
    sub = np.asarray(cloud[:max_rows], dtype=np.float64)
    real = sub[..., 0] != 0
    out = []
    for c in range(sub.shape[-1]):
        v = sub[..., c][real]
        q = np.quantile(v, [0.01, 0.5, 0.99]) if v.size else [float("nan")] * 3
        out.append({"column": c, "mean": float(v.mean()), "std": float(v.std()),
                    "min": float(v.min()), "max": float(v.max()), "p01": float(q[0]),
                    "p50": float(q[1]), "p99": float(q[2])})
    return out


def event_stats(np: Any, evt: Any) -> list[dict[str, float]]:
    e = np.asarray(evt, dtype=np.float64)
    return [{"column": c, "mean": float(e[:, c].mean()), "std": float(e[:, c].std()),
             "min": float(e[:, c].min()), "max": float(e[:, c].max())}
            for c in range(e.shape[1])]


def apply_arm(np: Any, arm: Any, inputs: Any, read: Callable, half_a: dict | None) -> dict:
    blocks = {
        "pdata_reco": inputs.pdata["reco"], "pdata_reco_evt": inputs.pdata["reco_evt"],
        "mc_reco": inputs.mc["reco"], "mc_reco_evt": inputs.mc["reco_evt"],
        "mc_gen": inputs.mc["gen"], "mc_gen_evt": inputs.mc["gen_evt"],
        "coord_gen": inputs.meta["coord_gen"],
        "pdata_rows": inputs.pdata["rows"], "mc_rows": inputs.mc["rows"],
        "pdata_pass_reco": np.ones(len(inputs.pdata["rows"]), bool),
        "mc_pass_reco": inputs.mc["pass_reco"], "mc_pass_gen": inputs.mc["pass_gen"],
        "extra_gen": ({"half_a": (half_a["gen"], half_a["gen_evt"], half_a["rows"],
                                  half_a["pass_gen"])} if half_a is not None else {}),
    }
    out = b2_arms.apply(arm, blocks, lambda col, rows: read("reco", col, rows),
                        lambda col, rows: read("truth", col, rows), np)
    inputs.pdata["reco_evt"] = out["pdata_reco_evt"]
    inputs.mc["reco_evt"] = out["mc_reco_evt"]
    inputs.mc["gen"] = out["mc_gen"]
    inputs.mc["gen_evt"] = out["mc_gen_evt"]
    inputs.meta["coord_gen"] = tuple(int(c) for c in out["coord_gen"])
    if half_a is not None:
        g, ge, _rows, _pg = out["extra_gen"]["half_a"]
        half_a["gen"], half_a["gen_evt"] = g, ge
    return out["record"]


# ---------------------------------------------------------------------------------------------- #
# The engine subclass
# ---------------------------------------------------------------------------------------------- #
def make_b2_multifold(MultiFold: type, tf: Any, np: Any) -> type:
    Recipe = ru.make_recipe_multifold(MultiFold, tf, np)

    class B2MultiFold(Recipe):
        def __init__(self, *a: Any, deadline_unix: float | None = None,
                     first_iteration_estimate_s: float = 1200.0,
                     stop_after_iteration: int | None = None,
                     step2_miss_mode: str = "carry", **k: Any) -> None:
            super().__init__(*a, **k)
            if step2_miss_mode not in STEP2_MISS_MODES:
                raise SystemExit(f"[b2] unknown step-2 miss mode {step2_miss_mode!r}")
            self.step2_miss_mode = step2_miss_mode
            self.deadline_unix = deadline_unix
            self.stop_after_iteration = stop_after_iteration
            self.first_iteration_estimate_s = float(first_iteration_estimate_s)
            self.state_dir = self.out_dir / "iterations"
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.fits_sink = self.out_dir / "fits.jsonl"
            self.segments: list[dict[str, Any]] = []
            self._fits_written = 0

        # ---- step 2: the engine's rule, or the efficiency-corrected one ---------------- #
        def RunStep2(self, i: int) -> None:
            """`carry` is the engine's own `RunStep2` (misses carry the previous push into the
            class-1 weights). `efficiency_corrected` trains the truth classifier on the
            RECO-PASSING events alone -- where the step-1 correction lives -- and applies the
            learned truth-level ratio to ALL truth events, misses included (Huang et al.
            arXiv:2504.06857 sec. V.A). It assumes the selection efficiency depends only on the
            truth variables the classifier sees."""
            if self.step2_miss_mode == "carry":
                super().RunStep2(i)
                return
            self.log_string("RUNNING STEP 2 (efficiency-corrected: trained on accepted events)")
            accepted = np.asarray(self.mc.pass_reco, dtype=np.float32)
            self.RunModel(
                np.concatenate((self.labels_mc, self.labels_gen)),
                np.concatenate((self.mc.weight * accepted,
                                self.mc.weight * self.weights_pull * accepted)),
                i, self.model2, stepn=2,
                NTRAIN=self.num_steps_gen * self.config.step2.batch_size, cached=i > self.start)
            new_weights = np.ones_like(self.weights_push)
            new_weights[self.mc.pass_gen] = self.reweight(
                self._pack_gen(self.mc.gen), self.model2)[self.mc.pass_gen]
            self.weights_push = new_weights

        # ---- persistence -------------------------------------------------------------- #
        def _save_iteration(self, i: int, seconds: float) -> None:
            np.savez(self.state_dir / f"iter{i:02d}.npz",
                     pull=np.asarray(self.weights_pull, np.float32),
                     push=np.asarray(self.weights_push, np.float32))
            blobs = {}
            for stepn, models in ((1, self.step1_models), (2, self.step2_models)):
                for j, w in enumerate(models[0].get_weights()):
                    blobs[f"s{stepn}_{j:04d}"] = w
            np.savez(self.state_dir / f"models{i:02d}.npz", **blobs)
            with self.fits_sink.open("a") as handle:
                for record in self.fit_records[self._fits_written:]:
                    handle.write(json.dumps(record, default=repr) + "\n")
            self._fits_written = len(self.fit_records)
            self.iteration_records[-1]["seconds"] = seconds
            write_json_atomic(self.out_dir / "state.json", {
                "completed_iteration": i, "config_hash": self.config.content_hash(),
                "iteration_records": self.iteration_records, "segments": self.segments})

        def _restore(self) -> int:
            state_path = self.out_dir / "state.json"
            if not state_path.exists():
                return 0
            state = json.loads(state_path.read_text())
            if state["config_hash"] != self.config.content_hash():
                raise SystemExit("[b2] state.json belongs to another config; refusing to resume")
            k = int(state["completed_iteration"])
            with np.load(self.state_dir / f"iter{k:02d}.npz") as blob:
                self.weights_push = np.asarray(blob["push"], np.float32)
                self.weights_pull = np.asarray(blob["pull"], np.float32)
            with np.load(self.state_dir / f"models{k:02d}.npz") as blob:
                for stepn, models in ((1, self.step1_models), (2, self.step2_models)):
                    step = self.step_recipe(stepn)
                    tf.keras.utils.set_random_seed(ru.derive_seed(step.seed, stepn, "init", 0))
                    model = self.factories[stepn]()
                    names = sorted(n for n in blob.files if n.startswith(f"s{stepn}_"))
                    model.set_weights([blob[n] for n in names])
                    models[:] = [model]
            self.iteration_records = list(state["iteration_records"])
            self.segments = list(state.get("segments", []))
            if self.fits_sink.exists():
                self.fit_records = [json.loads(line) for line in
                                    self.fits_sink.read_text().splitlines() if line.strip()]
                self._fits_written = len(self.fit_records)
            self.log_string(f"[b2] resumed after iteration {k}")
            return k + 1

        # ---- the loop ----------------------------------------------------------------- #
        def Unfold(self) -> bool:
            self.step1_models, self.step2_models = [], []
            self.mc_weight_reco = getattr(self.mc, "weight_reco", None)
            if self.mc_weight_reco is None:
                self.mc_weight_reco = self.mc.weight
            self.weights_pull = np.ones(self.mc.weight.shape[0], dtype=np.float32)
            self.weights_push = np.ones(self.mc.weight.shape[0], dtype=np.float32)
            self.iteration_records = []
            start = self._restore()
            segment = {"job": os.environ.get("SLURM_JOB_ID"), "first_iteration": start,
                       "started_unix": time.time()}
            self.segments.append(segment)
            last = self.first_iteration_estimate_s
            for i in range(start, self.niter):
                if self.deadline_unix is not None and time.time() + 1.1 * last > \
                        self.deadline_unix:
                    segment["stopped_before_iteration"] = i
                    self.log_string(f"[b2] deadline: not starting iteration {i}")
                    return False
                self.log_string(f"ITERATION: {i + 1}")
                t0 = time.perf_counter()
                self.RunStep1(i)
                self.RunStep2(i)
                last = time.perf_counter() - t0
                self.iteration_records.append({
                    "iteration": i, "pull": rec.weight_stats(np, self.weights_pull),
                    "push": rec.weight_stats(np, self.weights_push)})
                segment["last_iteration"] = i
                self._save_iteration(i, last)
                if self.stop_after_iteration is not None and i >= self.stop_after_iteration \
                        and i + 1 < self.niter:
                    segment["stopped_before_iteration"] = i + 1
                    self._save_iteration(i, last)
                    return False
            return True

    return B2MultiFold


# ---------------------------------------------------------------------------------------------- #
# Truth-only evaluation (experiment 2)
# ---------------------------------------------------------------------------------------------- #
class TruthOnlyEvaluator:
    """Scores a step-2 classifier's learned ratio on half B's truth at every epoch.

    Two scores, both from B1's historical-code scorers (`phase_b/scalar`):
    * `learnability`: B x ratio against B x (the half-A tilt FUNCTION evaluated on B) -- how well
      the ratio was learned, without the half-A / half-B sampling difference (B1's convention);
    * `endpoint`: the historical score of the push over half B (`scalar_common.score_push`),
      whose sampling ceiling is 0.984 (B1 anchors, the injected function itself).
    """

    def __init__(self, np: Any, *, gen_b: Any, gen_evt_b: Any, pass_gen_b: Any, rows_b: Any,
                 tilt_spec: dict[str, Any], populations: Path | None, batch_size: int) -> None:
        self.np = np
        self.gen_b, self.gen_evt_b = gen_b, gen_evt_b
        self.pg = np.asarray(pass_gen_b, bool)
        self.batch_size = int(batch_size)
        self.records: list[dict[str, Any]] = []
        self.endpoint = None
        self.tilt_spec = tilt_spec
        if str(SCALAR) not in sys.path:
            sys.path.append(str(SCALAR))
        import run_ibu
        import run_truth_learnability as rtl
        import scalar_common as scm
        self.scm, self.rtl, self.run_ibu = scm, rtl, run_ibu
        self.sources = scm.verify_historical_sources()
        self.alignment = {"populations": None}
        if populations is not None:
            pop = scm.load_populations(populations)
            self.alignment = {"populations": str(populations),
                              "populations_sha256": scm.sha256_file(populations),
                              "b_rows_equal": bool(np.array_equal(pop["b_rows"], rows_b)),
                              "b_pass_truth_equal": bool(np.array_equal(
                                  pop["b_pass_truth"].astype(bool), self.pg))}
            if self.alignment["b_rows_equal"] and self.alignment["b_pass_truth_equal"]:
                self.endpoint = scm.endpoint_from_populations(pop)
                self.eav_b = pop["b_truth"][self.pg, 2]
                if not np.array_equal(self.eav_b, pop["ep_eavail_b"]):
                    raise SystemExit("[b2] half-B truth rows do not align with the Endpoint")
                self.w_b = pop["b_w_truth"][self.pg]
                self.region_b = pop["ep_region_b"].astype("<U32")
                self.edges = pop["endpoint_edges"]
                self.tilt_fn_b = self.tilt_function(self.eav_b)
                pga = pop["a_pass_truth"].astype(bool)
                self.pga = pga
                self.a_rows = pop["a_rows"]
                self.eav_a = pop["a_truth"][pga, 2]
                if not np.array_equal(self.eav_a, pop["ep_eavail_a"]):
                    raise SystemExit("[b2] half-A truth rows do not align with the Endpoint")
                self.w_a = pop["a_w_truth"][pga]
                self.tilt_a = pop["a_tilt"][pga]
                self.region_a = pop["ep_region_a"].astype("<U32")
                self.alignment["tilt_function_reproduces_half_a_tilt_max_abs_dev"] = float(
                    np.max(np.abs(self.tilt_function(self.eav_a) - self.tilt_a)))

    def tilt_function(self, eavail: Any) -> Any:
        """The half-A tilt, as a FUNCTION of true E_avail (its recorded spec), on other rows."""
        np, s = self.np, self.tilt_spec
        z = np.clip((np.asarray(eavail, np.float64) - s["pt_p50"]) / s["pt_iqr"],
                    -s["clip_z"], s["clip_z"])
        return np.exp(s["amplitude"] * z) / s["pre_normalization_mean"]

    def ratio(self, model: Any) -> Any:
        np = self.np
        logit = np.asarray(model.predict((self.gen_b[self.pg], self.gen_evt_b[self.pg]),
                                         batch_size=self.batch_size, verbose=0))[:, 0]
        if not np.all(np.isfinite(logit)):
            raise ValueError("non-finite logits on half B")
        return np.exp(np.clip(logit, -LOGIT_CAP, LOGIT_CAP)), int((np.abs(logit) >= LOGIT_CAP)
                                                                   .sum())

    def score(self, ratio: Any) -> dict[str, Any]:
        np = self.np
        out: dict[str, Any] = {"ratio_summary": self.scm.weight_summary(ratio)}
        if self.endpoint is None:
            return out
        push = np.ones(self.pg.size)
        push[self.pg] = ratio
        full = self.scm.score_push(self.endpoint, push, self.run_ibu.SCOREABLE,
                                   self.run_ibu.INFORMATIONAL)
        out["endpoint"] = full
        rows = np.arange(self.eav_b.size)
        out["learnability"] = self.rtl.score_on(rows, self.eav_b, self.w_b, self.tilt_fn_b,
                                                ratio, self.region_b, self.edges)
        out["mean_abs_log_ratio_error"] = float(np.average(
            np.abs(np.log(ratio) - np.log(self.tilt_fn_b)), weights=self.w_b))
        return out

    def score_in_sample(self, rows_a: Any, push_a: Any) -> dict[str, Any] | None:
        """B1-convention recovery on half A itself (train + validation events)."""
        np = self.np
        if self.endpoint is None or not np.array_equal(self.a_rows, rows_a):
            return None
        ratio = np.asarray(push_a, np.float64)[self.pga]
        return self.rtl.score_on(np.arange(self.eav_a.size), self.eav_a, self.w_a, self.tilt_a,
                                 ratio, self.region_a, self.edges)

    def callback(self, tf: Any) -> Any:
        evaluator = self

        class EpochEval(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch: int, logs: Any = None) -> None:
                t0 = time.perf_counter()
                ratio, saturated = evaluator.ratio(self.model)
                record = {"epoch": int(epoch), "saturated": saturated,
                          "val_loss": float((logs or {}).get("val_loss", float("nan"))),
                          "loss": float((logs or {}).get("loss", float("nan"))),
                          **evaluator.score(ratio)}
                record["seconds"] = time.perf_counter() - t0
                evaluator.records.append(record)
                brief = record.get("learnability", {}).get("aggregate", {}).get("recovery")
                print(f"[b2 truth-only] epoch {epoch} learnability R={brief} val_loss="
                      f"{record['val_loss']:.5f}", flush=True)

        return EpochEval()


def evaluating_factory(PET: type, base: Callable[[], Any], callbacks: list) -> Callable[[], Any]:
    """A step-2 factory whose models add `callbacks` to every `fit` (the model code is unchanged:
    the instance's class is a thin subclass that only extends the callback list)."""

    class EvaluatedPET(PET):
        def fit(self, *a: Any, callbacks: Any = None, **k: Any) -> Any:  # noqa: D102
            return super().fit(*a, callbacks=list(callbacks or []) + list(extra), **k)

    extra = callbacks

    def factory() -> Any:
        model = base()
        model.__class__ = EvaluatedPET
        return model

    return factory


# ---------------------------------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inputs-npz", type=Path, required=True)
    parser.add_argument("--identity-sidecar", type=Path, required=True)
    parser.add_argument("--mode", choices=("unfold", "truth_only"), default="unfold")
    parser.add_argument("--populations", type=Path, default=None,
                        help="B1's populations.npz (truth-only scoring on the endpoint)")
    parser.add_argument("--probe-rows", type=int, default=50_000)
    parser.add_argument("--deadline-unix", type=float, default=None)
    parser.add_argument("--first-iteration-estimate-s", type=float, default=1200.0)
    parser.add_argument("--stop-after-iteration", type=int, default=None,
                        help="testing: exit INCOMPLETE after this iteration (resume check)")
    parser.add_argument("--step2-miss-mode", choices=STEP2_MISS_MODES, default="carry",
                        help="'carry' is the engine's rule (the default path, byte-identical); "
                             "'efficiency_corrected' trains step 2 on reco-passing events only "
                             "and applies the ratio to all truth events")
    args = parser.parse_args()

    out = scope.refuse_historical_output(args.out)
    out.mkdir(parents=True, exist_ok=True)
    config = RunConfig.from_json(args.config.read_text())
    if config.arm != "ours":
        raise SystemExit("[b2] B2 runs the ours arm only")
    arm = b2_arms.get(config.feature_arm)
    scope.refuse_real_data_inputs(
        bkg_mode="mc-only", measured_leg_is_real=False,
        npz_keys_read=[f"{w}_scalars" for w in ("reco", "truth")],
        input_paths=[args.inputs_npz])
    started = time.perf_counter()
    probe_record = ru._load_numpy_probe()

    import numpy as np
    import closure_data as cd
    mods = cd.import_historical(args.repo)
    import tensorflow as tf
    import training_recipe
    import torch_adamw
    gpus = [d.name for d in tf.config.list_physical_devices("GPU")]
    if not gpus:
        raise SystemExit("[b2] no GPU visible to TensorFlow; refusing to train on CPU")
    if mods["omnifold"].REWEIGHT_LOGIT_CAP != rec.REWEIGHT_LOGIT_CAP:
        raise SystemExit("[b2] the recorder's logit cap differs from the engine's")
    rec.install_counters(tf, next(k for k in tf.keras.optimizers.Adam.__mro__
                                  if "_clip_gradients" in vars(k)))

    truth_only = args.mode == "truth_only"
    inputs, half_a = build_inputs(cd, mods, np, config, args, need_half_a=truth_only)
    digests_before_arm = inputs.digests(np)
    stats_before = {"gen_cloud": column_stats(np, inputs.mc["gen"]),
                    "gen_evt": event_stats(np, inputs.mc["gen_evt"]),
                    "reco_evt": event_stats(np, inputs.mc["reco_evt"])}
    read = scalar_reader(np, mods["ffd"], args.inputs_npz)
    arm_record = apply_arm(np, arm, inputs, read, half_a)
    stats_after = {"gen_cloud": column_stats(np, inputs.mc["gen"]),
                   "gen_evt": event_stats(np, inputs.mc["gen_evt"]),
                   "reco_evt": event_stats(np, inputs.mc["reco_evt"])}
    pdata, mcb = cd.make_loaders(mods, np, inputs)
    factories, _check = ru.model_factories(config, mods, inputs)
    B2 = make_b2_multifold(mods["omnifold"].MultiFold, tf, np)
    common = dict(config=config, out_dir=out, pretrained_check=None,
                  training_recipe=training_recipe, torch_adamw=torch_adamw,
                  probe_rows=args.probe_rows, deadline_unix=args.deadline_unix,
                  first_iteration_estimate_s=args.first_iteration_estimate_s,
                  stop_after_iteration=args.stop_after_iteration,
                  step2_miss_mode=args.step2_miss_mode)
    receipt: dict[str, Any] = {
        "schema": "pet-improvement-b2-run-receipt-v1", "mode": args.mode,
        "config": config.to_dict(), "config_hash": config.content_hash(),
        "b2_arm": arm.name, "b2_arm_hash": arm.content_hash(), "b2_arm_record": arm_record,
        "step2_miss_mode": args.step2_miss_mode,
        "run_identity": hashlib.sha256(
            f"{config.content_hash()}|{arm.content_hash()}|{args.step2_miss_mode}|{args.mode}"
            .encode()).hexdigest(),
        "code_commit": subprocess.run(["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                                      capture_output=True, text=True).stdout.strip(),
        "inputs_npz": str(args.inputs_npz), "input_digests_before_arm": digests_before_arm,
        "input_column_stats_before_arm": stats_before,
        "input_column_stats_after_arm": stats_after,
        "numpy_sve_probe": probe_record, "precision_policy": mods["precision_policy"],
        "sys_path_entries_removed": mods["sys_path_entries_removed"],
        "closure": {k: v for k, v in inputs.meta.items()
                    if k not in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a",
                                 "mc_indices")},
        "measured_leg_is_real_data": False, "gpus": gpus,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    }

    if not truth_only:
        unfolder = B2(config.name, factories=factories, data=pdata, mc=mcb, **common)
        complete = unfolder.Unfold()
        receipt.update({"fits": unfolder.fit_records, "iterations": unfolder.iteration_records,
                        "segments": unfolder.segments, "complete": bool(complete)})
        np.savez_compressed(out / "halves.npz", dump_rows_a=inputs.meta["dump_rows_a"],
                            dump_rows_b=inputs.meta["dump_rows_b"],
                            tilt_a=inputs.meta["tilt_a"], pass_gen_a=inputs.meta["pass_gen_a"],
                            pass_gen_b=inputs.mc["pass_gen"], pass_reco_b=inputs.mc["pass_reco"])
        receipt["iteration_files"] = {
            p.name: sha256_file(p) for p in sorted((out / "iterations").glob("iter*.npz"))}
    else:
        spec = inputs.meta["tilt_spec"]
        evaluator = TruthOnlyEvaluator(
            np, gen_b=inputs.mc["gen"], gen_evt_b=inputs.mc["gen_evt"],
            pass_gen_b=inputs.mc["pass_gen"], rows_b=inputs.meta["dump_rows_b"],
            tilt_spec=spec, populations=args.populations,
            batch_size=config.step2.predict_batch_size)
        factories = dict(factories)
        factories[2] = evaluating_factory(mods["net"].PET, factories[2],
                                          [evaluator.callback(tf)])
        # Step 2 alone on half A, the pull set to the injected tilt: the engine's RunStep2.
        DataLoader, ffd = mods["DataLoader"], mods["ffd"]
        mca = DataLoader(reco=half_a["reco"], gen=half_a["gen"], pass_reco=half_a["pass_reco"],
                         pass_gen=half_a["pass_gen"],
                         weight=half_a["weight"].astype(np.float32),
                         weight_reco=half_a["weight_reco"].astype(np.float32), normalize=True,
                         normalization_factor=ffd.STEP1_MC_NORMALIZATION,
                         reco_evt=half_a["reco_evt"], gen_evt=half_a["gen_evt"])
        unfolder = B2(config.name, factories=factories, data=pdata, mc=mca, **common)
        unfolder.step1_models, unfolder.step2_models = [], []
        tilt_a = np.asarray(inputs.meta["tilt_a"], np.float32)
        unfolder.weights_pull = tilt_a
        unfolder.weights_push = np.ones_like(tilt_a)
        unfolder.RunStep2(0)
        final_ratio, saturated = evaluator.ratio(unfolder.step2_models[0])
        final = {"saturated": saturated, **evaluator.score(final_ratio)}
        in_sample = evaluator.score_in_sample(half_a["rows"], unfolder.weights_push)
        np.savez_compressed(out / "truth_only_ratio_b.npz",
                            ratio_b=np.asarray(final_ratio, np.float32),
                            dump_rows_b=inputs.meta["dump_rows_b"],
                            pass_gen_b=inputs.mc["pass_gen"])
        receipt.update({"fits": unfolder.fit_records, "epochs_on_half_b": evaluator.records,
                        "final_after_restore": final, "in_sample_half_a": in_sample,
                        "tilt_spec_half_a": spec, "scoring_alignment": evaluator.alignment,
                        "historical_sources": evaluator.sources, "complete": True,
                        "label": ("LEARNABILITY DIAGNOSTIC of the step-2 input set (true tilt "
                                  "supplied as the class-1 weight); NOT a detector-level bound "
                                  "and NOT an unfolding recovery")})
        complete = True
    receipt["seconds"] = time.perf_counter() - started
    write_json_atomic(out / "receipt.json", receipt)
    (out / "status.txt").write_text("COMPLETE\n" if complete else "INCOMPLETE\n")
    print(json.dumps({"receipt": str(out / "receipt.json"), "complete": bool(complete),
                      "seconds": receipt["seconds"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
