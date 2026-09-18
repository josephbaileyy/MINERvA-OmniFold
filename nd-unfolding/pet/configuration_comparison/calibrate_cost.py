"""Measure per-evaluation cost for both arms on one GPU, at their real configurations.

The feasibility of the complete comparison turns on one ratio ``r``: what an evaluation
costs with Gregor's backbone against ours. Every estimate so far has been unusable ---
the parameter ratio (58.7x) is a bad proxy, and the CPU timing was overhead-dominated,
which its own control demonstrated. This measures it on the device the campaign runs on.

WHAT IT IS AND IS NOT. Both models are timed **on the same GPU at their own real
configurations**: ours is the production PET in TensorFlow at batch 512, his is
OmniLearned PET2-small in PyTorch at batch 2048 and, for a per-step comparison at fixed
work, also at 512. They are therefore **device-matched and framework-unmatched**. That
confound is real and is named in the receipt: a same-framework number needs the Keras
port, and this measurement exists so the port is not built before anyone knows whether
the campaign it enables is affordable.

The reported quantity is **cost per example presented**, not per step. Per-step time
would flatter whichever arm uses the larger batch, and example presentations are the
fairness axis the proposal freezes.

**One arm per invocation.** Our arm needs TensorFlow and his needs PyTorch, and nothing
establishes that a single Perlmutter interpreter has both. So each arm is timed by its
own interpreter into its own file and a third `--reduce` invocation combines them, which
also makes the reducer refuse a half-finished pair instead of quietly reporting one arm.

Nothing is trained to convergence, no closure statistic is produced, and no learning
claim is possible from the output.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

TOKENS = 12
OUR_BATCH = 512          # NOMINAL_SEED_POLICY["batch_size"]
THEIR_BATCH = 2048       # submit_train_jobs.generate_cmd(bs=2048)
WARMUP = 5
REPEATS = 20

# The production training budget, from train_fullevent_nominal.NOMINAL_SEED_POLICY.
NITER = 3
EPOCHS = 8
TRAIN_EVENTS = 2_000_000
STEPS_PER_FIT = TRAIN_EVENTS // OUR_BATCH
# MultiFold runs two fits (step 1 and step 2) per iteration.
FITS_PER_EVALUATION = 2 * NITER
EXAMPLES_PER_EVALUATION = FITS_PER_EVALUATION * EPOCHS * TRAIN_EVENTS


def _stats(times: list[float], batch: int) -> dict[str, Any]:
    median = statistics.median(times)
    return {
        "repeats": len(times),
        "step_seconds_median": median,
        "step_seconds_min": min(times),
        "step_seconds_max": max(times),
        "coefficient_of_variation": statistics.stdev(times) / statistics.mean(times)
        if len(times) > 1 else 0.0,
        "batch": batch,
        "seconds_per_example": median / batch,
    }


def time_ours(repo: Path) -> dict[str, Any]:
    """Time one forward+backward of the production PET at the nominal configuration."""
    root = repo / "omnifold_nn"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import numpy as np
    import tensorflow as tf
    from omnifold.net import PET

    gpus = [d.name for d in tf.config.list_logical_devices("GPU")]
    if not gpus:
        raise SystemExit("[calibrate] no GPU visible to TensorFlow (fail closed)")

    model = PET(num_feat=5, num_evt=13, num_part=TOKENS,
                num_heads=2, num_transformer=2, projection_dim=32, local=True, K=3)
    rng = np.random.RandomState(0)
    part = tf.constant(rng.randn(OUR_BATCH, TOKENS, 5), tf.float32)
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
        "framework": "tensorflow (legacy keras)", "device": gpus[0],
        "trainable_parameters": int(sum(int(np.prod(w.shape)) for w in model.trainable_weights)),
        **_stats(times, OUR_BATCH),
    }


def time_theirs(checkout: Path, batch: int, size: str = "small") -> dict[str, Any]:
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
    feats = torch.randn(batch, TOKENS, 4, device=device)
    pid = torch.randint(0, 8, (batch, TOKENS), device=device)
    add = torch.randn(batch, TOKENS, 5, device=device)
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
        torch.cuda.synchronize()   # without this the clock measures queueing, not work
        times.append(time.perf_counter() - start)
    return {
        "framework": "pytorch", "device": torch.cuda.get_device_name(0),
        "preset": preset, "size": size,
        "trainable_parameters": int(sum(p.numel() for p in model.parameters())),
        **_stats(times, batch),
    }


def reduce_halves(ours_path: Path, theirs_path: Path) -> dict[str, Any]:
    """Combine the two arms' halves, refusing a partial pair."""
    for path, label in ((ours_path, "ours"), (theirs_path, "theirs")):
        if not path.is_file():
            raise SystemExit(
                f"[calibrate] the {label} half is missing at {path}. A ratio needs both "
                "arms; refusing to report one."
            )
    ours = json.loads(ours_path.read_text())
    theirs = json.loads(theirs_path.read_text())
    if ours.get("device") != theirs.get("device"):
        raise SystemExit(
            f"[calibrate] the halves ran on different devices "
            f"({ours.get('device')!r} vs {theirs.get('device')!r}); the ratio would "
            "confound device with configuration."
        )
    return ours, theirs["native_batch"], theirs["matched_batch"]


def main() -> None:
    """Time one arm, or reduce two halves into the receipt that re-costs the campaign."""
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
        args.output.write_text(json.dumps(time_ours(args.repo), indent=2) + "\n")
        print(f"wrote our half to {args.output}")
        return
    if args.arm == "theirs":
        if args.gregor_checkout is None:
            raise SystemExit("[calibrate] --gregor-checkout is required for --arm theirs")
        half = {
            "native_batch": time_theirs(args.gregor_checkout, THEIR_BATCH),
            "matched_batch": time_theirs(args.gregor_checkout, OUR_BATCH),
        }
        half["device"] = half["native_batch"]["device"]
        args.output.write_text(json.dumps(half, indent=2) + "\n")
        print(f"wrote their half to {args.output}")
        return

    if args.ours_half is None or args.theirs_half is None:
        raise SystemExit("[calibrate] --ours-half and --theirs-half are required to reduce")
    ours, theirs_native, theirs_matched = reduce_halves(args.ours_half, args.theirs_half)

    # Cost per example is the fairness-relevant unit; per-step would flatter the larger
    # batch. r is quoted on the native-batch figure because that is his real setting.
    r_native = theirs_native["seconds_per_example"] / ours["seconds_per_example"]
    r_matched = theirs_matched["seconds_per_example"] / ours["seconds_per_example"]
    our_eval_hours = ours["seconds_per_example"] * EXAMPLES_PER_EVALUATION / 3600.0

    receipt: dict[str, Any] = {
        "scope": (
            "per-evaluation training cost for both arms on ONE GPU at their real "
            "configurations. No convergence, no closure statistic, no learning claim."
        ),
        "confound_named": (
            "DEVICE-MATCHED, FRAMEWORK-UNMATCHED: ours is TensorFlow and his is PyTorch, "
            "because the Keras port does not exist yet. A same-framework r requires the "
            "port; this measurement exists so the port is not built before anyone knows "
            "whether the campaign it enables is affordable."
        ),
        "budget_model": {
            "niter": NITER, "epochs": EPOCHS, "train_events": TRAIN_EVENTS,
            "fits_per_evaluation": FITS_PER_EVALUATION,
            "examples_per_evaluation": EXAMPLES_PER_EVALUATION,
            "fairness_axis": "example presentations, not optimizer steps",
        },
        "halves": {"ours": str(args.ours_half), "theirs": str(args.theirs_half)},
        "ours": ours,
        "theirs_native_batch": theirs_native,
        "theirs_matched_batch": theirs_matched,
        "r_per_example_native_batch": r_native,
        "r_per_example_matched_batch": r_matched,
        "our_evaluation_gpu_hours": our_eval_hours,
        "fit_only_caveat": (
            "These are FIT-time projections. The feature contract's ~1.1-1.3 GPU-h for a "
            "nominal train also covers the fixture build, normalization, reweight-all "
            "inference and serialization, which this driver does not time and which do "
            "not scale with the backbone. So the projected totals below UNDERSTATE "
            "absolute cost and are the right basis only for the RATIO."
        ),
        "their_evaluation_gpu_hours": our_eval_hours * r_native,
        "projected_final_comparison_gpu_hours": {
            str(n): n * our_eval_hours * (1.0 + r_native) for n in (4, 8, 12, 16)
        },
        "non_claim": (
            "Cost is cost. A cheaper arm is not a better one, and nothing here bears on "
            "recovery, closure or representation quality."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"ours   {ours['step_seconds_median']*1e3:8.2f} ms/step @ {OUR_BATCH} "
          f"= {ours['seconds_per_example']*1e6:.3f} us/example")
    print(f"theirs {theirs_native['step_seconds_median']*1e3:8.2f} ms/step @ {THEIR_BATCH} "
          f"= {theirs_native['seconds_per_example']*1e6:.3f} us/example")
    print(f"r (per example, native batches) = {r_native:.2f}")
    print(f"one evaluation: ours {our_eval_hours:.2f} GPU-h, "
          f"his {our_eval_hours * r_native:.2f} GPU-h")


if __name__ == "__main__":
    main()
