"""Bound how much more a training step costs with Gregor's paper backbone.

The whole feasibility of a complete head-to-head turns on one number: what one
OmniFold training step costs with a 2.76 M-parameter PET2 backbone instead of our
47 k-parameter PET. A parameter ratio does not answer that -- compute scales with
FLOPs, not weights -- so this measures forward+backward wall time for both models
at the SAME token count and batch size.

WHAT THIS IS NOT. It times a PyTorch model and a TensorFlow model on CPU, so it is
**cross-framework and cross-device** and cannot be quoted as the GPU ratio. It is
here to distinguish "about the same" from "one to two orders of magnitude", which is
the only distinction the go/no-go needs at proposal time. A same-framework GPU
measurement replaces it once the port exists; that is stage 2's job and this script
must not be cited in its place.

Two guards against the obvious ways such a comparison misleads:

* both models see the same token count (12) and the same batch, so the ratio is not
  a token-budget artifact;
* the per-model spread over repeats is reported, because a ratio of medians whose
  inputs overlap is not a ratio at all.
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
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

TOKENS = 12
BATCHES = (64, 512)   # two batches: if the ratio moves, the small one was overhead
WARMUP = 3
REPEATS = 10


def _summarize(times: list[float]) -> dict[str, float]:
    return {
        "median_ms": statistics.median(times) * 1e3,
        "min_ms": min(times) * 1e3,
        "max_ms": max(times) * 1e3,
        "repeats": len(times),
    }


def time_our_pet(repo: Path, BATCH: int) -> dict[str, Any]:
    """Time one forward+backward of the production PET at its own configuration."""
    root = repo / "omnifold_nn"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import numpy as np
    import tensorflow as tf
    from omnifold.net import PET

    model = PET(num_feat=5, num_evt=13, num_part=TOKENS,
                num_heads=2, num_transformer=2, projection_dim=32, local=True, K=3)
    part = tf.constant(np.random.RandomState(0).randn(BATCH, TOKENS, 5), tf.float32)
    evt = tf.constant(np.random.RandomState(1).randn(BATCH, 13), tf.float32)
    target = tf.constant(np.random.RandomState(2).randint(0, 2, (BATCH, 1)), tf.float32)
    opt = tf.keras.optimizers.Adam(1e-4)

    def step():
        with tf.GradientTape() as tape:
            out = model([part, evt], training=True)
            loss = tf.reduce_mean(tf.square(tf.cast(out, tf.float32) - target))
        grads = tape.gradient(loss, model.trainable_weights)
        opt.apply_gradients(zip(grads, model.trainable_weights))

    for _ in range(WARMUP):
        step()
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        step()
        times.append(time.perf_counter() - start)
    return {
        "framework": "tensorflow (legacy keras)",
        "trainable_parameters": int(sum(int(np.prod(w.shape)) for w in model.trainable_weights)),
        **_summarize(times),
    }


def time_gregor_pet2(checkout: Path, size: str, BATCH: int) -> dict[str, Any]:
    """Time one forward+backward of the paper's PET2 backbone at a named preset."""
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    import torch
    from src.models.omnilearned.network import PET2
    from src.models.omnilearned.utils import get_model_parameters

    torch.manual_seed(0)
    torch.set_num_threads(os.cpu_count() or 1)
    preset = get_model_parameters(size)
    model = PET2(input_dim=4, add_dim=5, pid=True, pid_dim=8, cond_dim=16,
                 num_coord=2, K=10, add_info=True, conditional=True,
                 mode="classifier", num_classes=1, **preset)
    model.train()
    feats = torch.randn(BATCH, TOKENS, 4)
    pid = torch.randint(0, 8, (BATCH, TOKENS))
    add = torch.randn(BATCH, TOKENS, 5)
    cond = torch.randn(BATCH, 16)
    target = torch.randint(0, 2, (BATCH, 1)).float()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)

    def step() -> None:
        # Exactly the call `forward_model` makes at train.py:1665-1672, so this times
        # the code path his training actually runs rather than a guess at it.
        opt.zero_grad(set_to_none=True)
        outputs = model(feats, target, cond=cond, pid=pid, add_info=add)
        loss = torch.nn.functional.mse_loss(
            outputs["y_pred"].reshape(BATCH, -1)[:, :1], target
        )
        loss.backward()
        opt.step()

    for _ in range(WARMUP):
        step()
    times = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        step()
        times.append(time.perf_counter() - start)
    return {
        "framework": "pytorch",
        "preset": preset,
        "trainable_parameters": int(sum(p.numel() for p in model.parameters())),
        **_summarize(times),
    }


def main() -> None:
    """Bound the step-cost ratio and write a receipt that states its own limits."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--gregor-checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    by_batch: dict[str, Any] = {}
    for batch in BATCHES:
        ours = time_our_pet(args.repo, batch)
        theirs = {s: time_gregor_pet2(args.gregor_checkout, s, batch) for s in ("small", "medium")}
        by_batch[str(batch)] = {
            "ours": ours,
            "gregors_paper_backbone": theirs,
            "step_cost_ratio_to_ours": {
                s: theirs[s]["median_ms"] / ours["median_ms"] for s in theirs
            },
        }
    # If the ratio is stable across an 8x batch change, FLOPs dominate and the number
    # means something. If it moves, the smaller batch was measuring framework overhead
    # and NEITHER number is a scaling estimate.
    ratio_small = [by_batch[str(b)]["step_cost_ratio_to_ours"]["small"] for b in BATCHES]
    overhead_dominated = (max(ratio_small) / min(ratio_small)) > 1.5

    receipt: dict[str, Any] = {
        "scope": (
            "CPU, cross-framework, indicative ONLY: distinguishes 'about the same' from "
            "'orders of magnitude'. NOT the GPU ratio and not a substitute for a "
            "same-framework measurement."
        ),
        "tokens": TOKENS,
        "batches": list(BATCHES),
        "warmup": WARMUP,
        "repeats": REPEATS,
        "by_batch": by_batch,
        "ratio_moves_with_batch": overhead_dominated,
        "verdict": (
            "OVERHEAD-DOMINATED: the ratio moves with batch size, so neither number is "
            "a scaling estimate and the cost question is UNRESOLVED until stage 2 "
            "measures it on GPU in one framework."
            if overhead_dominated else
            "STABLE across an 8x batch change, so the ratio is FLOP-driven and usable "
            "as an order-of-magnitude bound -- still cross-framework, still CPU."
        ),
        "non_claim": (
            "A framework difference is folded into every ratio here. Use it to decide "
            "whether the complete comparison is plausibly affordable, never to quote a "
            "cost. Stage 2 of the proposal replaces it with one measured GPU evaluation "
            "per arm in a single framework."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    for batch in BATCHES:
        block = by_batch[str(batch)]
        print(f"batch {batch}: ours {block['ours']['median_ms']:.1f} ms; " + "; ".join(
            f"PET2-{s} {block['gregors_paper_backbone'][s]['median_ms']:.1f} ms "
            f"({block['step_cost_ratio_to_ours'][s]:.1f}x)"
            for s in ("small", "medium")))
    print(receipt["verdict"])


if __name__ == "__main__":
    main()
