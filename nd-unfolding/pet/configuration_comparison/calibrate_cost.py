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
EXAMPLES_PER_EVALUATION = FITS_PER_EVALUATION * EPOCHS * TRAIN_EVENTS

CROSS_FRAMEWORK_QUALIFICATION = (
    "DEVICE-MATCHED, FRAMEWORK-UNMATCHED. Ours is TensorFlow and his is PyTorch because "
    "the Keras port does not exist yet, so every ratio here folds in a framework "
    "difference. It distinguishes 'comparable' from 'orders of magnitude apart'; it is "
    "not the same-framework ratio the final costing needs."
)
FIT_ONLY_CAVEAT = (
    "Projections are FIT-time only. The feature contract's ~1.1-1.3 GPU-h for a nominal "
    "train also covers the fixture build, normalization, reweight-all inference and "
    "serialization, none of which scale with the backbone. Absolute projections therefore "
    "UNDERSTATE cost; the ratio is the reliable part."
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


def time_theirs(checkout: Path, tokens: int, batch: int, size: str = "small") -> dict[str, Any]:
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
                 mode="classifier", num_classes=1, **preset).to(device)
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

    for _ in range(WARMUP):
        step()
    torch.cuda.synchronize()
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        step()
        torch.cuda.synchronize()   # otherwise the clock measures queueing, not work
        times.append(time.perf_counter() - start)
    return {
        "framework": "pytorch",
        "tokens": tokens,
        "preset": preset, "size": size,
        "trainable_parameters": int(sum(p.numel() for p in model.parameters())),
        **_throughput(times, batch),
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
        our_hours = our_row["seconds_per_example"] * EXAMPLES_PER_EVALUATION / 3600.0
        # Projections use the MATCHED-batch ratio, so a missing native cell degrades the
        # reporting and not the costing.
        projected[key] = {
            "our_evaluation_gpu_hours": our_hours,
            "their_evaluation_gpu_hours": our_hours * r_matched,
            "arm_pair_evaluation_gpu_hours": our_hours * (1.0 + r_matched),
            "ratio_source": "matched_batch (same batch and tokens for both arms)",
            "final_comparison_gpu_hours_by_seeds": {
                str(n): n * our_hours * (1.0 + r_matched) for n in (4, 8, 12, 16)
            },
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
        "projected_evaluation_cost": {
            "budget_model": {
                "niter": NITER, "epochs": EPOCHS, "train_events": TRAIN_EVENTS,
                "fits_per_evaluation": FITS_PER_EVALUATION,
                "examples_per_evaluation": EXAMPLES_PER_EVALUATION,
                "fairness_axis": "example presentations, not optimizer steps",
            },
            "fit_only_caveat": FIT_ONLY_CAVEAT,
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
    parser.add_argument("--arm", choices=("ours", "theirs", "reduce"), required=True)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--gregor-checkout", type=Path)
    parser.add_argument("--ours-half", type=Path)
    parser.add_argument("--theirs-half", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.arm == "ours":
        if args.repo is None:
            raise SystemExit("[calibrate] --repo is required for --arm ours")
        half = {
            "gpu_identity": physical_gpu_identity(),
            "by_tokens": {str(t): time_ours(args.repo, t) for t in TOKEN_COUNTS},
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
        half = {"gpu_identity": physical_gpu_identity(), "by_tokens": by_tokens}
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
        print(f"tokens={tokens:>2}  projected arm-pair evaluation = "
              f"{row['arm_pair_evaluation_gpu_hours']:.2f} GPU-h (model-derived)")


if __name__ == "__main__":
    main()
