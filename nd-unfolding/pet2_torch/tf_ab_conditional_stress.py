#!/usr/bin/env python3
"""Self-locating experimental TensorFlow A/B conditional-closure runner.

This executes the existing vendored TensorFlow ``PET``/``MultiFold`` engine on
the portable aligned analytic fixture: recoil-cloud-only A versus the current
full-event B footing (the same cloud plus reconstructed muon globals).  It
writes JSON and makes no TF/PyTorch layer-equivalence claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import time

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PACKAGE_PARENT = REPO / "nd-unfolding"
for location in (PACKAGE_PARENT, REPO / "omnifold_nn"):
    if str(location) not in sys.path:
        sys.path.insert(0, str(location))

from pet2_torch.artifacts import write_json
from pet2_torch.evaluation import conditional_closure_metrics
from pet2_torch.fixtures import make_known_ratio_closure_dataset
from pet2_torch.utils import environment_receipt


def _muon_globals(batch):
    return batch.globals[
        :,
        [
            batch.global_names.index("mu_pt"),
            batch.global_names.index("mu_pparallel"),
        ],
    ].astype(np.float32)


def _run_arm(tf, PET, MultiFold, DataLoader, fixture, full_event, args, work_root):
    dataset = fixture.dataset
    signal = dataset.signal
    target = dataset.measured.literal_target()
    tf.keras.utils.set_random_seed(args.estimator_seed)
    data_evt = _muon_globals(target) if full_event else None
    reco_evt = _muon_globals(signal.reco) if full_event else None
    gen_evt = _muon_globals(signal.truth) if full_event else None
    data = DataLoader(
        reco=target.continuous.astype(np.float32),
        weight=dataset.measured.refined_weights.astype(np.float32),
        normalize=True,
        reco_evt=data_evt,
    )
    # This deliberately uses the current TF single-MC-weight convention.  The
    # JSON records that it cannot exercise the PyTorch w_reco/w_truth split.
    mc = DataLoader(
        reco=signal.reco.continuous.astype(np.float32),
        gen=signal.truth.continuous.astype(np.float32),
        pass_reco=signal.pass_reco,
        pass_gen=signal.pass_truth,
        weight=signal.w_truth.astype(np.float32),
        normalize=True,
        reco_evt=reco_evt,
        gen_evt=gen_evt,
    )
    p = signal.reco.continuous.shape[1]
    event_dim = 2 if full_event else 0
    model1 = PET(
        signal.reco.continuous.shape[2],
        num_evt=event_dim,
        num_part=p,
        num_transformer=2,
        num_heads=2,
        projection_dim=32,
        local=True,
        K=3,
        coord_idx=(1, 2),
    )
    model2 = PET(
        signal.truth.continuous.shape[2],
        num_evt=event_dim,
        num_part=p,
        num_transformer=2,
        num_heads=2,
        projection_dim=32,
        local=True,
        K=3,
        coord_idx=(1, 2),
    )

    class PreregisteredMultiFold(MultiFold):
        def get_optimizer(self, _num_steps, fixed=False, min_learning_rate=1e-5):
            learning_rate = min_learning_rate if fixed else args.learning_rate
            return tf.keras.optimizers.AdamW(
                learning_rate=learning_rate,
                weight_decay=args.weight_decay,
            )

    name = "B_full_event" if full_event else "A_recoil_only"
    arm_work = Path(work_root) / name
    arm_work.mkdir()
    try:
        tf.config.experimental.reset_memory_stats("GPU:0")
    except (RuntimeError, ValueError):
        pass
    started = time.perf_counter()
    unfolding = PreregisteredMultiFold(
        name,
        model1,
        model2,
        data,
        mc,
        niter=args.iterations,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.learning_rate,
        train_frac=0.7,
        early_stop=args.epochs,
        weights_folder=str(arm_work / "weights"),
        log_folder=str(arm_work),
        verbose=False,
    )
    np.random.seed(args.split_seed)
    unfolding.Unfold()
    push = np.asarray(unfolding.weights_push, dtype=np.float64)
    runtime_seconds = time.perf_counter() - started
    try:
        peak_gpu_memory = int(
            tf.config.experimental.get_memory_info("GPU:0")["peak"]
        )
    except (KeyError, RuntimeError, ValueError):
        peak_gpu_memory = None
    metrics = conditional_closure_metrics(
        dataset,
        push,
        fixture.expected_truth_ratio,
        fixture.declared_tail_mask,
    )
    return {
        "arm": "B" if full_event else "A",
        "feature_footing": (
            "current full-event PET cloud plus reconstructed muon globals"
            if full_event
            else "current recoil-only PET cloud"
        ),
        "runtime_seconds": runtime_seconds,
        "signal_rows_per_wall_second": signal.truth.n_rows / runtime_seconds,
        "peak_gpu_memory_bytes": peak_gpu_memory,
        "push_quantiles": np.quantile(push, [0, 0.01, 0.5, 0.99, 1]).tolist(),
        "conditional_closure": metrics,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--contract-only", action="store_true")
    parser.add_argument("--events", type=int, default=2048)
    parser.add_argument("--background-events", type=int, default=40)
    parser.add_argument("--max-tokens", type=int, default=7)
    parser.add_argument("--fixture-seed", type=int, default=424242)
    parser.add_argument("--estimator-seed", type=int, default=101)
    parser.add_argument("--split-seed", type=int, default=424242)
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.out).expanduser().resolve()
    fixture = make_known_ratio_closure_dataset(
        n_signal=args.events,
        n_background=args.background_events,
        max_tokens=args.max_tokens,
        seed=args.fixture_seed,
    )
    matched_budget = (
        args.events == 100000
        and args.background_events == 10000
        and args.max_tokens == 12
        and args.fixture_seed == 424242
        and args.estimator_seed in (101, 202, 303)
        and args.split_seed == 424242
        and args.iterations == 2
        and args.epochs == 8
        and args.batch_size == 512
        and args.learning_rate == 1e-4
        and args.weight_decay == 1e-2
    )
    result = {
        "status": "contract_only" if args.contract_only else "running",
        "evidence_class": "portable_synthetic_tf_current_engine_ab",
        "comparison": {
            "A": "existing TensorFlow/Keras PET recoil-only footing",
            "B": "existing TensorFlow/Keras PET full-event muon-global footing",
        },
        "fixture": fixture.specification,
        "recipe": {
            "estimator_seed": args.estimator_seed,
            "split_seed": args.split_seed,
            "split_mechanism": (
                "existing MultiFold seeded shuffle, train_frac=0.7; no claim of "
                "row-identical split with the PyTorch stable partition"
            ),
            "iterations": args.iterations,
            "epochs_per_step": args.epochs,
            "batch_size": args.batch_size,
            "signal_events": args.events,
            "background_events": args.background_events,
            "max_tokens": args.max_tokens,
            "optimizer": "AdamW",
            "learning_rate": args.learning_rate,
            "weight_decay": args.weight_decay,
            "classification": (
                "matched_budget_tf_a_vs_b"
                if matched_budget
                else "smoke_or_custom_downgrade"
            ),
            "tf_a_vs_b_comparison_claim_permitted": matched_budget,
            "same_rows_between_tf_arms": True,
            "tf_single_mc_weight": "w_truth for both steps (existing baseline limitation)",
            "executes_full_omnifold_loop": True,
            "publication_claim": False,
            "layer_equivalence_claim": False,
            "horovod_policy": (
                "disabled in this single-GPU runner before importing the "
                "vendored baseline; distributed baseline code is unchanged"
            ),
        },
        "environment": environment_receipt(),
        "g2_validation_claim": False,
    }
    if not args.contract_only:
        try:
            import tensorflow as tf
            # The archived single-GPU TensorFlow container also happens to
            # contain Horovod.  The vendored MultiFold module auto-initializes
            # Horovod merely when importable, which makes a direct one-task
            # Slurm run abort in MPI_Init before training.  This runner is
            # explicitly single-GPU, so make the optional package unavailable
            # without modifying the baseline implementation.
            sys.modules["horovod"] = None
            sys.modules["horovod.tensorflow"] = None
            sys.modules["horovod.tensorflow.keras"] = None
            from omnifold import MultiFold, PET
            from omnifold.dataloader import DataLoader
        except ImportError as exc:
            result.update(status="unavailable", reason=f"TensorFlow PET unavailable: {exc}")
            write_json(output, result)
            print(json.dumps(result, sort_keys=True))
            return 3
        with tempfile.TemporaryDirectory(prefix="pet2_tf_ab_") as work:
            result["arms"] = {
                "A": _run_arm(
                    tf, PET, MultiFold, DataLoader, fixture, False, args, work
                ),
                "B": _run_arm(
                    tf, PET, MultiFold, DataLoader, fixture, True, args, work
                ),
            }
        result["status"] = "complete_experimental_tf_current_engine_ab"
    write_json(output, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
