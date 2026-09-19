"""Measure training throughput for both arms on one GPU, at their real configurations.

The feasibility of the complete comparison turns on one ratio ``r``: what an evaluation
costs with Gregor's backbone against ours. Every earlier estimate was unusable -- the
parameter ratio (58.7x) is a bad proxy, and the CPU timing was overhead-dominated, which
its own two-batch control demonstrated.

**Measured and projected are kept apart.** ``measured_throughput`` holds only what a clock
read: seconds per step and per example presented. ``projected_evaluation_cost`` holds
GPU-hours, which are *derived* from a training-budget model (niter, epochs, subsample) and
are therefore only as good as that model. Conflating the two is how a timing becomes a
budget nobody can audit.

**Two token counts, both promised by the cost plan and both delivered here.** The current
input caps clouds at **12** tokens; Gregor's configuration caps at **33**. Attention is
quadratic in token count and the MLP terms linear, so the ratio at 12 does not price a
comparison run at 33. Timing both is what makes the completion cost estimable rather than
assumed.

**Cross-framework qualification, which does not go away.** Ours is TensorFlow and his is
PyTorch, because the Keras port does not exist yet. The arms are therefore
**device-matched and framework-unmatched**, and every ratio here carries that confound. A
same-framework ``r`` needs the port; this job exists so the port is not built before
anyone knows whether the campaign it enables is affordable.

**One arm per invocation.** Our arm needs TensorFlow and his needs PyTorch, and nothing
establishes that a single Perlmutter interpreter has both. Each arm is timed by its own
interpreter into its own file and a third ``--arm reduce`` invocation combines them.

**Device identity is verified on a physical identifier**, not a framework string: TF says
``/device:GPU:0`` and PyTorch says ``NVIDIA A100-SXM4-40GB``, which never compare equal,
so an earlier version's reducer would have rejected every genuine pair. Both halves record
the GPU **UUID** and PCI bus id from ``nvidia-smi``, which is the same string whichever
framework asks.

Nothing is trained to convergence, no closure statistic is produced, and no learning
claim is possible from the output.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")


def _select_keras_backend() -> dict[str, Any]:
    """Set TF_USE_LEGACY_KERAS only where it is the right answer.

    The vendored PET is Keras-2 code. Two environments satisfy it and they need OPPOSITE
    settings, which an unconditional `setdefault` gets wrong in one of them:

    * TF 2.16 with Keras 3 plus the `tf_keras` shim (this Mac) -- the variable is
      REQUIRED, or `tf.keras` resolves to Keras 3 and the model cannot build;
    * TF 2.15 with Keras 2 bundled and no `tf_keras` (Perlmutter's tensorflow/2.15.0) --
      the variable is HARMFUL: TF then looks for a `tf_keras` package that is not there
      and `tensorflow.keras` disappears entirely.

    Measured 2026-09-18: hardcoding it failed job 58526592 in 18 s with
    `ModuleNotFoundError: No module named 'tensorflow.keras'`, having passed on the Mac.
    So the choice is made from what is installed, and recorded in the receipt so the
    environment is attributable rather than assumed.
    """
    import importlib.util

    shim = importlib.util.find_spec("tf_keras") is not None
    if shim:
        os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
    return {
        "tf_keras_shim_available": shim,
        "tf_use_legacy_keras": os.environ.get("TF_USE_LEGACY_KERAS"),
        "reason": (
            "Keras-3 TensorFlow with the tf_keras shim: the shim is selected."
            if shim else
            "no tf_keras shim: assuming TensorFlow bundles Keras 2, which the vendored "
            "PET needs. If tf.keras turns out to be Keras 3 the model will fail to build "
            "and that is the documented, loud failure."
        ),
    }

# CORRECTION, 2026-09-19. The first calibration built his backbone from PET2's CLASS
# defaults, which are use_int=True and local_int=True. That is not the paper
# configuration. `plot_configs/V1Paper.json` names OmniLearned-small, -small-rw and
# -medium as the V1 lineup, and the matching `OLS`, `OLS_RW` and `OLM_FB` branches of
# `src/jobs/submit_train_jobs.py:155-169` pass NEITHER `--ol-interaction` NOR
# `--ol-local-interaction`; both are `store_true` with `default=False`. A fourth
# branch, `OLS_int`, turns them on and is not in the paper lineup.
#
# Capacity barely moves (2,762,550 -> 2,758,702, 0.14 %), so the capacity comparison
# is unaffected. COST is a different matter: the interaction block builds an
# (B, N, N, 3) pairwise tensor and pushes it through a 3 -> 256 -> num_heads MLP,
# which is quadratic in tokens, so the measured ratio r was taken on a model doing
# work the paper configuration does not do. That is why r is re-measured here.
PAPER_INTERACTION_FLAGS = {"use_int": False, "local_int": False}

TOKEN_COUNTS = (12, 33)   # ours today; Gregor's max_particles
OUR_BATCH = 512           # NOMINAL_SEED_POLICY["batch_size"]
THEIR_BATCH = 2048        # submit_train_jobs.generate_cmd(bs=2048)
WARMUP = 5
REPEATS = 20

# The production training budget, from train_fullevent_nominal.NOMINAL_SEED_POLICY.
# Used ONLY for the projection block, never for the measured block.
NITER = 3
EPOCHS = 8
TRAIN_EVENTS = 2_000_000
FITS_PER_EVALUATION = 2 * NITER          # MultiFold runs step 1 and step 2 per iteration

# CORRECTED 2026-09-19, by the realized-policy check rather than by reading.
# `MultiFold` concatenates BOTH classes before training, so one fit presents
# `epochs * train_frac * NTRAIN` examples with `NTRAIN = mc.nmax + data.nmax` at
# step 1 and `2 * mc.nmax` at step 2 (`omnifold.py:131-132`, `:297`). The previous
# model used `epochs * train_events`, which is the MC leg alone -- a 1.6x
# understatement. `--max-events` subsamples `imc`, which indexes the MC arrays
# only; the measured leg keeps its full inventory.
N_DATA_ASSUMED = TRAIN_EVENTS            # CONDITIONAL: see BUDGET_TENSION
ROWS_PER_FIT_STEP1 = TRAIN_EVENTS + N_DATA_ASSUMED
ROWS_PER_FIT_STEP2 = 2 * TRAIN_EVENTS
EXAMPLES_PER_EVALUATION = int(
    NITER * EPOCHS * TRAIN_FRAC_PLACEHOLDER * (ROWS_PER_FIT_STEP1 + ROWS_PER_FIT_STEP2)
) if False else None                     # replaced below, once TRAIN_FRAC is defined

# Evaluation is not only fits. Two forward-only populations were previously outside
# the model entirely, and together they are a third as large again as the training
# budget, so a fit-only projection is not a small underestimate:
#
#  * REWEIGHTING. `RunStep1` and `RunStep2` each call `reweight` over the whole MC
#    array once per iteration (`omnifold.py:199` and `:219`), so an evaluation makes
#    2 * NITER full inference passes over the subsample.
#  * VALIDATION. `MultiFold` splits `train_frac = 0.8`, and the held-out fifth is a
#    forward pass on every epoch of every fit -- 0.25 times the training examples.
#
# Both are timed against the measured INFERENCE throughput, not the training step
# time, because a backward pass is roughly twice the work of a forward one and
# charging inference at the training rate would overstate it.
TRAIN_FRAC = 0.8
VALIDATION_MULTIPLIER = (1.0 - TRAIN_FRAC) / TRAIN_FRAC
REWEIGHT_PASSES_PER_EVALUATION = 2 * NITER
EXAMPLES_PER_EVALUATION = int(
    NITER * EPOCHS * TRAIN_FRAC * (ROWS_PER_FIT_STEP1 + ROWS_PER_FIT_STEP2)
)
INFERENCE_EXAMPLES_PER_EVALUATION = int(
    REWEIGHT_PASSES_PER_EVALUATION * TRAIN_EVENTS
    + VALIDATION_MULTIPLIER * EXAMPLES_PER_EVALUATION
)

BUDGET_TENSION = (
    "n_data is ASSUMED equal to train_events and that assumption is not safe. The "
    "measured leg is not subsampled by --max-events, so its size is whatever the "
    "production input holds. At n_data = train_events the model puts our arm's "
    "evaluation at roughly 1.9 GPU-h, ABOVE the feature contract's independently "
    "measured 1.1-1.3 GPU-h for a nominal train. Both cannot be right. Resolving it "
    "needs mc.nmax and data.nmax read off a production run's loader meta; until "
    "then every absolute GPU-hour here is conditional and the RATIO is the reliable "
    "part."
)

CROSS_FRAMEWORK_QUALIFICATION = (
    "DEVICE-MATCHED, FRAMEWORK-UNMATCHED. Ours is TensorFlow and his is PyTorch because "
    "the Keras port does not exist yet, so every ratio here folds in a framework "
    "difference. It distinguishes 'comparable' from 'orders of magnitude apart'; it is "
    "not the same-framework ratio the final costing needs."
)
RESIDUAL_OVERHEAD_CAVEAT = (
    "Projections now cover fits, reweighting and validation, all from measured "
    "throughput. They still exclude the fixture build, normalization and serialization, "
    "which the feature contract folds into its ~1.1-1.3 GPU-h for a nominal train and "
    "which do not scale with the backbone. Absolute projections therefore still "
    "UNDERSTATE cost slightly; the ratio is the reliable part."
)


def physical_gpu_identity() -> dict[str, Any]:
    """Identify the visible GPU by UUID and PCI bus id, independent of framework.

    Framework device strings cannot be compared across frameworks, so the halves are
    matched on what `nvidia-smi` reports. `CUDA_VISIBLE_DEVICES` is recorded because it
    selects which physical device index 0 refers to.
    """
    query = "uuid,pci.bus_id,name"
    try:
        raw = subprocess.run(
            ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader"],
            capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"[calibrate] cannot read GPU identity from nvidia-smi: {exc}")
    devices = []
    for line in raw.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 3:
            devices.append({"uuid": parts[0], "pci_bus_id": parts[1], "name": parts[2]})
    if not devices:
        raise SystemExit("[calibrate] nvidia-smi reported no GPUs (fail closed)")
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    return {
        "cuda_visible_devices": visible,
        "devices": devices,
        "primary_uuid": devices[0]["uuid"],
        "primary_pci_bus_id": devices[0]["pci_bus_id"],
    }


def _throughput(times: list[float], batch: int) -> dict[str, Any]:
    """Only clock readings. No budget model, no extrapolation."""
    median = statistics.median(times)
    return {
        "repeats": len(times),
        "step_seconds_median": median,
        "step_seconds_min": min(times),
        "step_seconds_max": max(times),
        "coefficient_of_variation": (
            statistics.stdev(times) / statistics.mean(times) if len(times) > 1 else 0.0
        ),
        "batch": batch,
        "seconds_per_example": median / batch,
        "examples_per_second": batch / median,
    }


def time_ours(repo: Path, tokens: int) -> dict[str, Any]:
    """Time one forward+backward of the production PET at the nominal configuration."""
    root = repo / "omnifold_nn"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    backend = _select_keras_backend()
    import numpy as np
    import tensorflow as tf
    import keras
    from omnifold.net import PET

    if not tf.config.list_logical_devices("GPU"):
        raise SystemExit("[calibrate] no GPU visible to TensorFlow (fail closed)")

    model = PET(num_feat=5, num_evt=13, num_part=tokens,
                num_heads=2, num_transformer=2, projection_dim=32, local=True, K=3)
    rng = np.random.RandomState(0)
    part = tf.constant(rng.randn(OUR_BATCH, tokens, 5), tf.float32)
    evt = tf.constant(rng.randn(OUR_BATCH, 13), tf.float32)
    target = tf.constant(rng.randint(0, 2, (OUR_BATCH, 1)), tf.float32)
    opt = tf.keras.optimizers.Adam(1e-4)

    @tf.function
    def step():
        with tf.GradientTape() as tape:
            out = model([part, evt], training=True)
            loss = tf.reduce_mean(tf.square(tf.cast(out, tf.float32) - target))
        grads = tape.gradient(loss, model.trainable_weights)
        opt.apply_gradients(zip(grads, model.trainable_weights))
        return loss

    for _ in range(WARMUP):
        step()
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        float(step())      # force completion before stopping the clock
        times.append(time.perf_counter() - start)
    return {
        "framework": f"tensorflow {tf.__version__} / keras {keras.__version__}",
        "keras_backend_selection": backend,
        "tokens": tokens,
        "trainable_parameters": int(sum(int(np.prod(w.shape)) for w in model.trainable_weights)),
        **_throughput(times, OUR_BATCH),
    }


def time_theirs(checkout: Path, tokens: int, batch: int, size: str = "small",
                warmup: int | None = None, repeats: int | None = None) -> dict[str, Any]:
    """Time one forward+backward of OmniLearned PET2 at the paper preset."""
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    import torch
    from src.models.omnilearned.network import PET2
    from src.models.omnilearned.utils import get_model_parameters

    if not torch.cuda.is_available():
        raise SystemExit("[calibrate] no GPU visible to PyTorch (fail closed)")
    device = torch.device("cuda")
    torch.manual_seed(0)
    preset = get_model_parameters(size)
    model = PET2(input_dim=4, add_dim=5, pid=True, pid_dim=8, cond_dim=16,
                 num_coord=2, K=10, add_info=True, conditional=True,
                 mode="classifier", num_classes=1, **PAPER_INTERACTION_FLAGS,
                 **preset).to(device)
    model.train()
    feats = torch.randn(batch, tokens, 4, device=device)
    pid = torch.randint(0, 8, (batch, tokens), device=device)
    add = torch.randn(batch, tokens, 5, device=device)
    cond = torch.randn(batch, 16, device=device)
    target = torch.randint(0, 2, (batch, 1), device=device).float()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)

    def step() -> None:
        # The call `forward_model` makes at train.py:1665-1672.
        opt.zero_grad(set_to_none=True)
        outputs = model(feats, target, cond=cond, pid=pid, add_info=add)
        loss = torch.nn.functional.mse_loss(
            outputs["y_pred"].reshape(batch, -1)[:, :1], target)
        loss.backward()
        opt.step()

    for _ in range(WARMUP if warmup is None else warmup):
        step()
    torch.cuda.synchronize()
    times = []
    for _ in range(REPEATS if repeats is None else repeats):
        start = time.perf_counter()
        step()
        torch.cuda.synchronize()   # otherwise the clock measures queueing, not work
        times.append(time.perf_counter() - start)
    return {
        "framework": "pytorch",
        "tokens": tokens,
        "preset": preset, "size": size,
        "interaction_flags": dict(PAPER_INTERACTION_FLAGS),
        "trainable_parameters": int(sum(p.numel() for p in model.parameters())),
        **_throughput(times, batch),
    }


def time_theirs_inference(checkout: Path, tokens: int, batch: int,
                          size: str = "small") -> dict[str, Any]:
    """Forward-only cost for his arm, which is what evaluation actually pays.

    The training projection prices fits. An OmniFold evaluation also reweights
    every event at every iteration, and that is inference, not training, so
    quoting a fit-time total as the evaluation cost understates it. Measured
    separately rather than assumed to be a fixed fraction of the step time.
    """
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    import torch
    from src.models.omnilearned.network import PET2
    from src.models.omnilearned.utils import get_model_parameters

    device = torch.device("cuda")
    torch.manual_seed(0)
    preset = get_model_parameters(size)
    model = PET2(input_dim=4, add_dim=5, pid=True, pid_dim=8, cond_dim=16,
                 num_coord=2, K=10, add_info=True, conditional=True,
                 mode="classifier", num_classes=1, **PAPER_INTERACTION_FLAGS,
                 **preset).to(device)
    model.eval()
    feats = torch.randn(batch, tokens, 4, device=device)
    pid = torch.randint(0, 8, (batch, tokens), device=device)
    add = torch.randn(batch, tokens, 5, device=device)
    cond = torch.randn(batch, 16, device=device)
    target = torch.randint(0, 2, (batch, 1), device=device).float()

    def step() -> None:
        with torch.no_grad():
            model(feats, target, cond=cond, pid=pid, add_info=add)

    for _ in range(WARMUP):
        step()
    torch.cuda.synchronize()
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        step()
        torch.cuda.synchronize()
        times.append(time.perf_counter() - start)
    return {"framework": "pytorch", "mode": "inference", "tokens": tokens,
            "interaction_flags": dict(PAPER_INTERACTION_FLAGS), **_throughput(times, batch)}


def time_ours_inference(repo: Path, tokens: int) -> dict[str, Any]:
    """Forward-only cost for our arm, at the production PET."""
    backend = _select_keras_backend()
    import numpy as np
    import tensorflow as tf

    root = repo / "omnifold_nn"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from omnifold.net import PET

    model = PET(num_feat=5, num_evt=13, num_part=tokens, num_heads=2,
                num_transformer=2, projection_dim=32, local=True, K=3)
    rng = np.random.RandomState(0)
    part = tf.constant(rng.randn(OUR_BATCH, tokens, 5), tf.float32)
    evt = tf.constant(rng.randn(OUR_BATCH, 13), tf.float32)

    @tf.function
    def step():
        return model.model([part, evt], training=False)

    for _ in range(WARMUP):
        step()
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        float(tf.reduce_sum(step()))
        times.append(time.perf_counter() - start)
    return {"framework": f"tensorflow {tf.__version__}", "mode": "inference",
            "tokens": tokens, "keras_backend_selection": backend,
            **_throughput(times, OUR_BATCH)}


def time_ported_complete(repo: Path, tokens: int, batch: int,
                         mode: str = "train") -> dict[str, Any]:
    """Time his arm at the configuration we INTEND to run, not the degraded one.

    `time_ported` builds what is runnable today: our clouds, our event blocks, no
    PID, no auxiliary channel. That arm is legitimate for plumbing and for a
    framework-matched ratio, but costing the campaign from it prices the wrong
    model -- his complete arm carries a PID embedding, five auxiliary columns and
    sixteen globals, which is 35,200 more parameters and two more embedding paths
    over every token.

    The DATA does not exist yet (R-1/R-2), so the inputs here are synthetic at his
    widths. That is exactly the right scope for a cost measurement and exactly the
    wrong scope for anything else, which is why this function times and returns.
    """
    backend = _select_keras_backend()
    import numpy as np
    import tensorflow as tf

    root = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import pet2_keras_port as port
    import training_recipe as recipe

    if not tf.config.list_logical_devices("GPU"):
        raise SystemExit("[calibrate] no GPU visible to TensorFlow (fail closed)")
    settings = {"input_dim": 4, "pid": True, "pid_dim": 8, "add_info": True,
                "add_dim": 5, "conditional": True, "cond_dim": 16, "num_coord": 2,
                "K": 10, "num_classes": 1}
    model = port.PET2Port(**settings, **port.preset("small"))
    rng = np.random.RandomState(0)
    x = tf.constant(rng.randn(batch, tokens, 4), tf.float32)
    pid = tf.constant(rng.randint(0, 8, (batch, tokens)), tf.int32)
    add = tf.constant(rng.randn(batch, tokens, 5), tf.float32)
    cond = tf.constant(rng.randn(batch, 16), tf.float32)
    labels = tf.constant(rng.randint(0, 2, (batch, 1)).astype("float32"))
    variables = None

    if mode == "train":
        optimizer = recipe.build_optimizer(
            "theirs", schedule=recipe.derive_schedule(batch, examples=batch * 1000))

        @tf.function
        def step_fn():
            with tf.GradientTape() as tape:
                logits = model(x, cond, pid, add, training=True)
                loss = tf.reduce_mean(
                    tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=logits))
            optimizer.apply_gradients(
                zip(tape.gradient(loss, model.trainable_variables),
                    model.trainable_variables))
            return loss
    else:
        @tf.function
        def step_fn():
            return tf.reduce_sum(model(x, cond, pid, add, training=False))

    for _ in range(WARMUP):
        step_fn()
    times, values = [], []
    for _ in range(REPEATS):
        start = time.perf_counter()
        values.append(float(step_fn()))
        times.append(time.perf_counter() - start)
    return {
        "framework": f"tensorflow {tf.__version__}",
        "arm": "theirs_complete", "step": "his_own_schema", "mode": mode,
        "tokens": tokens, "precision": "float32",
        "configuration": settings,
        "keras_backend_selection": backend,
        "trainable_parameters": int(sum(int(np.prod(w.shape))
                                        for w in model.trainable_variables)),
        "values_finite": bool(np.isfinite(values).all()),
        "first_value": values[0], "last_value": values[-1],
        "value_changed_over_the_run": bool(values[0] != values[-1]),
        "inputs_are_synthetic_at_his_widths": True,
        **_throughput(times, batch),
    }


def time_ported(repo: Path, step: str, tokens: int, batch: int,
                mode: str = "train") -> dict[str, Any]:
    """Time the KERAS PORT of his backbone, at one OmniFold step schema.

    This is the measurement that removes the cross-framework qualification. Every
    earlier ratio compared our TensorFlow PET against his PyTorch PET2, so it
    folded in a framework difference that no amount of care could separate from an
    architecture difference. Both arms now run in the same engine on the same
    device, so the ratio is the architecture and the recipe and nothing else.

    Production precision: float32, which is what both arms train in. The float64
    paths exist only for the port checks.
    """
    backend = _select_keras_backend()
    import numpy as np
    import tensorflow as tf

    root = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import pet2_omnifold_adapter as adapter
    import training_recipe as recipe

    if not tf.config.list_logical_devices("GPU"):
        raise SystemExit("[calibrate] no GPU visible to TensorFlow (fail closed)")
    schema = adapter.STEP_SCHEMAS[step]
    model = adapter.build_step_model(step, num_part=tokens)
    rng = np.random.RandomState(0)
    part = np.abs(rng.rand(batch, tokens, schema["num_feat"])).astype(np.float32)
    evt = rng.randn(batch, schema["num_evt"]).astype(np.float32)
    labels = np.concatenate(
        [rng.randint(0, 2, (batch, 1)), np.ones((batch, 1))], axis=1).astype(np.float32)
    part_t, evt_t, y_t = tf.constant(part), tf.constant(evt), tf.constant(labels)

    if mode == "train":
        optimizer = recipe.build_optimizer(
            "theirs", schedule=recipe.derive_schedule(batch, examples=batch * 1000))
        variables = model.trainable_variables or None

        @tf.function
        def step_fn():
            with tf.GradientTape() as tape:
                loss = adapter.weighted_binary_crossentropy(
                    y_t, model([part_t, evt_t], training=True))
            optimizer.apply_gradients(
                zip(tape.gradient(loss, model.trainable_variables),
                    model.trainable_variables))
            return loss
    else:
        @tf.function
        def step_fn():
            return tf.reduce_sum(model([part_t, evt_t], training=False))

    # A timing loop that only reads the clock cannot tell a number from a NaN, and
    # a cell that trained to NaN would be reported as a throughput. The value is
    # captured and checked, so this VALIDATES the path as well as timing it.
    for _ in range(WARMUP):
        step_fn()
    times, values = [], []
    for _ in range(REPEATS):
        start = time.perf_counter()
        values.append(float(step_fn()))
        times.append(time.perf_counter() - start)
    finite = bool(np.isfinite(values).all())
    return {
        "framework": f"tensorflow {tf.__version__}",
        "arm": "ported_pet2", "step": step, "mode": mode, "tokens": tokens,
        "precision": "float32",
        "keras_backend_selection": backend,
        "trainable_parameters": int(sum(int(np.prod(w.shape))
                                        for w in model.trainable_variables)),
        "values_finite": finite,
        "first_value": values[0], "last_value": values[-1],
        "value_changed_over_the_run": bool(values[0] != values[-1]),
        **_throughput(times, batch),
    }


def time_ours_step(repo: Path, step: str, tokens: int, batch: int,
                   mode: str = "train") -> dict[str, Any]:
    """Our incumbent PET at the SAME step schema, batch and precision.

    Named `ours_incumbent` in the receipt: this is the promoted production
    configuration, not a candidate improvement on it.
    """
    backend = _select_keras_backend()
    import numpy as np
    import tensorflow as tf

    root = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import pet2_omnifold_adapter as adapter

    omnifold_root = repo / "omnifold_nn"
    if str(omnifold_root) not in sys.path:
        sys.path.insert(0, str(omnifold_root))
    from omnifold.net import PET, weighted_binary_crossentropy

    schema = adapter.STEP_SCHEMAS[step]
    model = PET(num_feat=schema["num_feat"], num_evt=schema["num_evt"],
                num_part=tokens, num_heads=2, num_transformer=2,
                projection_dim=32, local=True, K=3,
                coord_idx=schema["coord_idx"])
    rng = np.random.RandomState(0)
    part = tf.constant(np.abs(rng.rand(batch, tokens, schema["num_feat"])), tf.float32)
    evt = tf.constant(rng.randn(batch, schema["num_evt"]), tf.float32)
    y = tf.constant(np.concatenate(
        [rng.randint(0, 2, (batch, 1)), np.ones((batch, 1))], axis=1), tf.float32)
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)

    if mode == "train":
        @tf.function
        def step_fn():
            with tf.GradientTape() as tape:
                loss = weighted_binary_crossentropy(y, model.model([part, evt]))
            optimizer.apply_gradients(
                zip(tape.gradient(loss, model.model.trainable_variables),
                    model.model.trainable_variables))
            return loss
    else:
        @tf.function
        def step_fn():
            return tf.reduce_sum(model.model([part, evt], training=False))

    for _ in range(WARMUP):
        step_fn()
    times, values = [], []
    for _ in range(REPEATS):
        start = time.perf_counter()
        values.append(float(step_fn()))
        times.append(time.perf_counter() - start)
    return {
        "framework": f"tensorflow {tf.__version__}",
        "arm": "ours_incumbent", "step": step, "mode": mode, "tokens": tokens,
        "precision": "float32",
        "keras_backend_selection": backend,
        "trainable_parameters": int(sum(int(np.prod(w.shape))
                                        for w in model.model.trainable_weights)),
        "values_finite": bool(np.isfinite(values).all()),
        "first_value": values[0], "last_value": values[-1],
        "value_changed_over_the_run": bool(values[0] != values[-1]),
        **_throughput(times, batch),
    }


def diagnose_native_batch(checkout: Path, tokens: int, size: str = "small") -> dict[str, Any]:
    """Find out WHY batch 2048 fails at 33 tokens, and what would fix it.

    The distinction the answer has to support is between two different actions:

    * a BACKEND REPAIR, which leaves the recipe alone -- his batch stays 2048 and
      only the attention kernel selection changes;
    * a BATCH-SIZE CHANGE, which alters his configuration and therefore has to be
      declared as an adaptation and reflected in the fairness budget.

    So this records the exact exception and the innermost frame that raised it,
    tries each SDPA backend in turn, and bisects the largest batch that runs under
    the default backend. Every cell is attempted independently.
    """
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    import traceback

    import torch

    def attempt(batch: int, backend: Any = None) -> dict[str, Any]:
        # ONE step, not a timing run: the question here is whether the cell runs at
        # all, and twenty-five repetitions of an answer already known costs GPU time
        # against a budget that is being reported.
        probe = {"warmup": 0, "repeats": 1}
        try:
            if backend is None:
                time_theirs(checkout, tokens, batch, size, **probe)
            else:
                from torch.nn.attention import sdpa_kernel

                with sdpa_kernel(backend):
                    time_theirs(checkout, tokens, batch, size, **probe)
            return {"ran": True}
        except Exception as exc:                      # noqa: BLE001 - recorded
            frames = traceback.extract_tb(exc.__traceback__)
            innermost = frames[-1] if frames else None
            return {
                "ran": False,
                "error": f"{type(exc).__name__}: {exc}".split("\n")[0][:400],
                "raised_at": (f"{Path(innermost.filename).name}:{innermost.lineno} "
                              f"in {innermost.name}") if innermost else None,
            }
        finally:
            torch.cuda.empty_cache()

    backends: dict[str, Any] = {"default": attempt(THEIR_BATCH)}
    try:
        from torch.nn.attention import SDPBackend

        candidates = [("math", SDPBackend.MATH),
                      ("efficient_attention", SDPBackend.EFFICIENT_ATTENTION),
                      ("flash_attention", SDPBackend.FLASH_ATTENTION)]
    except Exception:                                  # noqa: BLE001
        candidates = []
        backends["sdpa_kernel_unavailable"] = {"ran": False,
                                               "error": "torch.nn.attention absent"}
    for name, backend in candidates:
        backends[name] = attempt(THEIR_BATCH, backend)

    # Largest working batch under the default backend, by bisection on powers of two
    # down from his native size. Bisection rather than a sweep so the probe stays
    # bounded; the point is to identify the action, not to profile the device.
    ladder = [b for b in (2048, 1024, 512, 256) if b <= THEIR_BATCH]
    largest_working = None
    ladder_results = {}
    for batch in ladder:
        outcome = backends["default"] if batch == THEIR_BATCH else attempt(batch)
        ladder_results[str(batch)] = outcome
        if outcome["ran"] and largest_working is None:
            largest_working = batch
    repair_backends = [n for n, r in backends.items() if n != "default" and r.get("ran")]

    # If a repair exists, TIME it. His intended configuration is batch 2048, so a
    # repair whose throughput is unknown leaves the completion cost unknown too --
    # the math backend materialises the full attention matrix and is not free.
    repaired: dict[str, Any] = {}
    if not backends["default"]["ran"] and repair_backends:
        from torch.nn.attention import SDPBackend, sdpa_kernel

        lookup = {"math": SDPBackend.MATH,
                  "efficient_attention": SDPBackend.EFFICIENT_ATTENTION,
                  "flash_attention": SDPBackend.FLASH_ATTENTION}
        name = repair_backends[0]
        try:
            with sdpa_kernel(lookup[name]):
                repaired = {"backend": name,
                            **time_theirs(checkout, tokens, THEIR_BATCH, size)}
        except Exception as exc:                      # noqa: BLE001 - recorded
            repaired = {"backend": name, "error": f"{type(exc).__name__}: {exc}"[:400]}
        finally:
            torch.cuda.empty_cache()
    elif backends["default"]["ran"]:
        repaired = {"backend": "default", "note": "no repair needed"}

    return {
        "repaired_native_throughput": repaired,
        "tokens": tokens,
        "native_batch": THEIR_BATCH,
        "native_batch_runs": backends["default"]["ran"],
        "by_sdpa_backend": backends,
        "batch_ladder": ladder_results,
        "largest_working_batch_default_backend": largest_working,
        "backend_repair_available": bool(repair_backends),
        "backend_repair_backends": repair_backends,
        "required_action": (
            "none: the native batch already runs" if backends["default"]["ran"]
            else ("backend repair, recipe preserved: "
                  f"{repair_backends} run at batch {THEIR_BATCH}")
            if repair_backends
            else ("batch-size change, recipe altered: no attention backend runs at "
                  f"batch {THEIR_BATCH}; the largest that does is "
                  f"{largest_working}")
        ),
    }


def reduce_halves(ours_path: Path, theirs_path: Path) -> dict[str, Any]:
    """Combine the two arms' halves, refusing a partial or mismatched pair.

    Identity is checked on the GPU **UUID**, which both halves obtain from nvidia-smi.
    Framework device strings differ by construction and cannot serve.
    """
    for path, label in ((ours_path, "ours"), (theirs_path, "theirs")):
        if not path.is_file():
            raise SystemExit(
                f"[calibrate] the {label} half is missing at {path}. A ratio needs both "
                "arms; refusing to report one."
            )
    ours = json.loads(ours_path.read_text())
    theirs = json.loads(theirs_path.read_text())

    our_id = ours.get("gpu_identity", {})
    their_id = theirs.get("gpu_identity", {})
    if not our_id.get("primary_uuid") or not their_id.get("primary_uuid"):
        raise SystemExit(
            "[calibrate] a half is missing its GPU identity; the ratio would confound "
            "device with configuration."
        )
    if our_id["primary_uuid"] != their_id["primary_uuid"]:
        raise SystemExit(
            f"[calibrate] the halves ran on different physical GPUs: "
            f"{our_id['primary_uuid']} vs {their_id['primary_uuid']}."
        )

    measured: dict[str, Any] = {}
    projected: dict[str, Any] = {}
    for tokens in TOKEN_COUNTS:
        key = str(tokens)
        if key not in ours.get("by_tokens", {}) or key not in theirs.get("by_tokens", {}):
            raise SystemExit(
                f"[calibrate] token count {tokens} is missing from a half; the cost plan "
                "promises both 12 and 33 and a partial answer prices nothing."
            )
        our_row = ours["by_tokens"][key]
        their_native = theirs["by_tokens"][key]["native_batch"]
        their_matched = theirs["by_tokens"][key]["matched_batch"]

        # The MATCHED-batch cell is the like-for-like comparison and is required: same
        # batch, same tokens, so the ratio is not a batch artifact. The native-batch cell
        # is his real setting and is reported when it ran, but it cannot be required --
        # some (batch, device, stack) combinations do not run at all.
        if "error" in their_matched:
            raise SystemExit(
                f"[calibrate] the matched-batch cell at {tokens} tokens failed "
                f"({their_matched['error']}). That is the like-for-like comparison; "
                "without it there is no ratio to report at this token count."
            )
        r_matched = their_matched["seconds_per_example"] / our_row["seconds_per_example"]
        native_ok = "error" not in their_native
        r_native = (their_native["seconds_per_example"] / our_row["seconds_per_example"]
                    if native_ok else None)
        measured[key] = {
            "ours": our_row,
            "theirs_native_batch": their_native,
            "theirs_matched_batch": their_matched,
            "ratio_per_example_native_batch": r_native,
            "ratio_per_example_matched_batch": r_matched,
            "ratio_used_for_projection": "matched_batch",
            "native_batch_available": native_ok,
        }
        our_fit_hours = our_row["seconds_per_example"] * EXAMPLES_PER_EVALUATION / 3600.0
        their_fit_hours = our_fit_hours * r_matched

        our_infer = (ours.get("inference") or {}).get(key)
        their_infer = (theirs.get("inference") or {}).get(key)
        inference_measured = bool(
            our_infer and their_infer and "error" not in their_infer
        )
        if inference_measured:
            our_inference_hours = (our_infer["seconds_per_example"]
                                   * INFERENCE_EXAMPLES_PER_EVALUATION / 3600.0)
            their_inference_hours = (their_infer["seconds_per_example"]
                                     * INFERENCE_EXAMPLES_PER_EVALUATION / 3600.0)
        else:
            our_inference_hours = their_inference_hours = None

        our_total = (our_fit_hours + our_inference_hours
                     if inference_measured else None)
        their_total = (their_fit_hours + their_inference_hours
                       if inference_measured else None)
        pair_total = (our_total + their_total) if inference_measured else None

        # Projections use the MATCHED-batch ratio, so a missing native cell degrades the
        # reporting and not the costing.
        projected[key] = {
            "our_fit_gpu_hours": our_fit_hours,
            "their_fit_gpu_hours": their_fit_hours,
            "arm_pair_fit_gpu_hours": our_fit_hours + their_fit_hours,
            "inference_measured": inference_measured,
            "our_inference_gpu_hours": our_inference_hours,
            "their_inference_gpu_hours": their_inference_hours,
            "our_evaluation_gpu_hours": our_total,
            "their_evaluation_gpu_hours": their_total,
            "arm_pair_evaluation_gpu_hours": pair_total,
            "inference_ratio_per_example": (
                their_infer["seconds_per_example"] / our_infer["seconds_per_example"]
                if inference_measured else None
            ),
            "ratio_source": "matched_batch (same batch and tokens for both arms)",
            "final_comparison_gpu_hours_by_seeds": (
                {str(n): n * pair_total for n in (4, 8, 12, 16)}
                if inference_measured else None
            ),
        }

    return {
        "scope": (
            "training throughput for both arms on ONE GPU at their real configurations, "
            "and evaluation costs PROJECTED from it. No convergence, no closure "
            "statistic, no learning claim."
        ),
        "cross_framework_qualification": CROSS_FRAMEWORK_QUALIFICATION,
        "gpu_identity": {"ours": our_id, "theirs": their_id,
                         "matched_on": "primary_uuid from nvidia-smi"},
        "halves": {"ours": str(ours_path), "theirs": str(theirs_path)},
        "measured_throughput": measured,
        "native_batch_diagnosis": theirs.get("native_batch_diagnosis"),
        "interaction_flags": dict(PAPER_INTERACTION_FLAGS),
        "interaction_flag_correction": (
            "his arm is built with use_int=False and local_int=False, the V1-paper "
            "setting. The 2026-09-18 calibration used PET2's class defaults of "
            "True/True, which is the non-paper OLS_int variant, and therefore timed a "
            "model doing quadratic pairwise work the paper configuration does not do."
        ),
        "projected_evaluation_cost": {
            "budget_model": {
                "niter": NITER, "epochs": EPOCHS, "train_events": TRAIN_EVENTS,
                "fits_per_evaluation": FITS_PER_EVALUATION,
                "examples_per_evaluation": EXAMPLES_PER_EVALUATION,
                "train_frac": TRAIN_FRAC,
                "reweight_passes_per_evaluation": REWEIGHT_PASSES_PER_EVALUATION,
                "inference_examples_per_evaluation": INFERENCE_EXAMPLES_PER_EVALUATION,
                "fairness_axis": "example presentations, not optimizer steps",
            },
            "residual_overhead_caveat": RESIDUAL_OVERHEAD_CAVEAT,
            "derived_not_measured": (
                "Everything in this block is a model applied to the measured throughput "
                "above. Quote the measured block for throughput and this block only with "
                "its budget model attached."
            ),
            "by_tokens": projected,
        },
        "non_claim": (
            "Cost is cost. A cheaper arm is not a better one, and nothing here bears on "
            "recovery, closure or representation quality."
        ),
    }


def main() -> None:
    """Time one arm across both token counts, or reduce two halves."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=("ours", "theirs", "reduce", "matched"),
                        required=True)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--gregor-checkout", type=Path)
    parser.add_argument("--ours-half", type=Path)
    parser.add_argument("--theirs-half", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.arm == "matched":
        # Both arms in ONE framework, at both step schemas, at both intended
        # batches, in production precision. Cells are independent; a cell that the
        # stack cannot run records its error and the rest proceed.
        if args.repo is None:
            raise SystemExit("[calibrate] --repo is required for --arm matched")
        cells: dict[str, Any] = {}
        for step in ("step1_reco", "step2_gen"):
            for tokens in TOKEN_COUNTS:
                for batch in (OUR_BATCH, THEIR_BATCH):
                    for mode in ("train", "inference"):
                        for arm, fn in (("ours_incumbent", time_ours_step),
                                        ("ported_pet2", time_ported)):
                            key = f"{arm}|{step}|{tokens}|{batch}|{mode}"
                            try:
                                cells[key] = fn(args.repo, step, tokens, batch, mode)
                            except Exception as exc:      # noqa: BLE001 - recorded
                                cells[key] = {"error": f"{type(exc).__name__}: {exc}"[:300],
                                              "arm": arm, "step": step, "tokens": tokens,
                                              "batch": batch, "mode": mode}
                                print(f"{key}: FAILED {type(exc).__name__}", file=sys.stderr)
        ran = {k: v for k, v in cells.items() if "error" not in v}
        non_finite = sorted(k for k, v in ran.items() if not v["values_finite"])
        static = sorted(k for k, v in ran.items()
                        if v["mode"] == "train" and not v["value_changed_over_the_run"])
        # His COMPLETE arm: his own schema, which does not vary by OmniFold step
        # because the data is mapped into it rather than the model into the data.
        for tokens in TOKEN_COUNTS:
            for batch in (OUR_BATCH, THEIR_BATCH):
                for mode in ("train", "inference"):
                    key = f"theirs_complete|his_own_schema|{tokens}|{batch}|{mode}"
                    try:
                        cells[key] = time_ported_complete(args.repo, tokens, batch, mode)
                    except Exception as exc:          # noqa: BLE001 - recorded
                        cells[key] = {"error": f"{type(exc).__name__}: {exc}"[:300],
                                      "arm": "theirs_complete", "tokens": tokens,
                                      "batch": batch, "mode": mode}
                        print(f"{key}: FAILED {type(exc).__name__}", file=sys.stderr)

        half = {"gpu_identity": physical_gpu_identity(), "framework_matched": True,
                "cells": cells,
                "validation": {
                    "cells_attempted": len(cells), "cells_ran": len(ran),
                    "cells_failed": sorted(k for k in cells if k not in ran),
                    "non_finite_cells": non_finite,
                    "training_cells_whose_loss_never_moved": static,
                    "held": bool(not non_finite and not static and ran),
                    "criterion": ("every cell that ran must produce finite values, and "
                                  "every TRAINING cell's loss must move -- a loss frozen "
                                  "across 20 steps means the optimizer is not connected, "
                                  "which a throughput number would hide"),
                },
                "note": ("both arms in TensorFlow on one GPU: the cross-framework "
                         "qualification does not apply to these ratios")}
        args.output.write_text(json.dumps(half, indent=2) + "\n")
        for key, cell in sorted(cells.items()):
            if "error" in cell:
                print(f"{key:56s} FAILED")
            else:
                print(f"{key:56s} {cell['step_seconds_median']*1e3:8.2f} ms/step "
                      f"= {cell['seconds_per_example']*1e6:8.3f} us/example"
                      + ("" if cell["values_finite"] else "  NON-FINITE"))
        validation = half["validation"]
        print(f"validation: {'PASS' if validation['held'] else 'FAIL'} "
              f"({validation['cells_ran']}/{validation['cells_attempted']} ran, "
              f"{len(validation['non_finite_cells'])} non-finite, "
              f"{len(validation['training_cells_whose_loss_never_moved'])} frozen)")
        return

    if args.arm == "ours":
        if args.repo is None:
            raise SystemExit("[calibrate] --repo is required for --arm ours")
        half = {
            "gpu_identity": physical_gpu_identity(),
            "by_tokens": {str(t): time_ours(args.repo, t) for t in TOKEN_COUNTS},
            "inference": {str(t): time_ours_inference(args.repo, t) for t in TOKEN_COUNTS},
        }
        args.output.write_text(json.dumps(half, indent=2) + "\n")
        for tokens, row in half["by_tokens"].items():
            print(f"ours   tokens={tokens:>2} {row['step_seconds_median']*1e3:8.2f} ms/step "
                  f"@ {OUR_BATCH} = {row['seconds_per_example']*1e6:.3f} us/example")
        return

    if args.arm == "theirs":
        if args.gregor_checkout is None:
            raise SystemExit("[calibrate] --gregor-checkout is required for --arm theirs")
        # Each (tokens, batch) cell is attempted independently. A cell that the device or
        # the stack cannot run records its error and the rest proceed: measured 2026-09-18,
        # batch 2048 raised `CUDA error: invalid configuration argument` inside PyTorch's
        # scaled_dot_product_attention on an A100 under pytorch/2.6.0, which previously
        # destroyed the whole arm including the cells that DO run. A partial, honestly
        # labelled matrix is worth more than nothing, and the reducer decides separately
        # whether what survived is enough.
        by_tokens: dict[str, Any] = {}
        for tokens in TOKEN_COUNTS:
            cells: dict[str, Any] = {}
            for label, batch in (("native_batch", THEIR_BATCH), ("matched_batch", OUR_BATCH)):
                try:
                    cells[label] = time_theirs(args.gregor_checkout, tokens, batch)
                except Exception as exc:                      # noqa: BLE001 - recorded, not swallowed
                    cells[label] = {"error": f"{type(exc).__name__}: {exc}",
                                    "tokens": tokens, "batch": batch}
                    print(f"theirs tokens={tokens:>2} batch={batch}: FAILED "
                          f"{type(exc).__name__}", file=sys.stderr)
            by_tokens[str(tokens)] = cells
        inference: dict[str, Any] = {}
        for tokens in TOKEN_COUNTS:
            try:
                inference[str(tokens)] = time_theirs_inference(
                    args.gregor_checkout, tokens, OUR_BATCH)
            except Exception as exc:                  # noqa: BLE001 - recorded
                inference[str(tokens)] = {"error": f"{type(exc).__name__}: {exc}"[:400],
                                          "tokens": tokens}
        diagnosis = {}
        for tokens in TOKEN_COUNTS:
            try:
                diagnosis[str(tokens)] = diagnose_native_batch(args.gregor_checkout, tokens)
            except Exception as exc:                  # noqa: BLE001 - recorded
                diagnosis[str(tokens)] = {"error": f"{type(exc).__name__}: {exc}"[:400]}
        half = {"gpu_identity": physical_gpu_identity(), "by_tokens": by_tokens,
                "inference": inference, "native_batch_diagnosis": diagnosis}
        args.output.write_text(json.dumps(half, indent=2) + "\n")
        for tokens, row in by_tokens.items():
            for label in ("native_batch", "matched_batch"):
                cell = row[label]
                if "error" in cell:
                    print(f"theirs tokens={tokens:>2} {label}: FAILED")
                else:
                    print(f"theirs tokens={tokens:>2} {label}: "
                          f"{cell['step_seconds_median']*1e3:8.2f} ms/step @ {cell['batch']} "
                          f"= {cell['seconds_per_example']*1e6:.3f} us/example")
        return

    if args.ours_half is None or args.theirs_half is None:
        raise SystemExit("[calibrate] --ours-half and --theirs-half are required to reduce")
    receipt = reduce_halves(args.ours_half, args.theirs_half)
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    for tokens, row in receipt["measured_throughput"].items():
        native = row["ratio_per_example_native_batch"]
        print(f"tokens={tokens:>2}  r matched-batch = "
              f"{row['ratio_per_example_matched_batch']:.2f}"
              + (f", native-batch = {native:.2f}" if native is not None
                 else ", native-batch = UNAVAILABLE"))
    for tokens, row in receipt["projected_evaluation_cost"]["by_tokens"].items():
        if row["inference_measured"]:
            print(f"tokens={tokens:>2}  projected arm-pair evaluation = "
                  f"{row['arm_pair_evaluation_gpu_hours']:.2f} GPU-h "
                  f"(fit {row['arm_pair_fit_gpu_hours']:.2f} + inference "
                  f"{row['our_inference_gpu_hours'] + row['their_inference_gpu_hours']:.2f}, "
                  "model-derived)")
        else:
            print(f"tokens={tokens:>2}  arm-pair FIT ONLY = "
                  f"{row['arm_pair_fit_gpu_hours']:.2f} GPU-h; inference NOT measured")
    diagnosis = receipt.get("native_batch_diagnosis") or {}
    for tokens, row in diagnosis.items():
        print(f"tokens={tokens:>2}  native batch: {row.get('required_action', row)}")


if __name__ == "__main__":
    main()
